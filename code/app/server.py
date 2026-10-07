"""Nury pastor app server. Stdlib only. Run from code/:  python3 -m app.server  (http://127.0.0.1:8080)

One session per intake. The engine runs in a worker thread; its approval gate blocks
until the pastor posts a decision. The API never returns rejected drafts.
There is no send path: nothing here contacts the family.
"""
import json
import os
import threading
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from nury.audit import AuditLog
from nury.engine import UNSAFE_SUFFIX, CaseState, GateDecision, get_playbook, run_stage
from nury.gloo_client import GlooClient
from nury.playbook import PLAYBOOKS_DIR, PlaybookError, list_playbooks

STATIC = Path(__file__).parent / "static"
SESSIONS = {}
GENERIC_PLACEHOLDER = "Who called, who is affected, where, when, and what the family asks."


def playbooks():
    """Selector data: id, title, description, status, plus intake placeholder and demo text if the playbook has them."""
    out = []
    for p in list_playbooks():
        p = dict(p)
        p.setdefault("status", "live")
        intake = {}
        f = PLAYBOOKS_DIR / p["id"] / "playbook.json"
        if f.is_file():
            intake = json.loads(f.read_text(encoding="utf-8")).get("intake", {})
        p["placeholder"] = intake.get("placeholder", GENERIC_PLACEHOLDER)
        demo = intake.get("demo")
        if demo:
            p["demo_intake"] = demo
        out.append(p)
    return out


def safe_event(e):
    """Audit event for the pastor's screen: no draft text, no error detail, no quoted matches. Categories only."""
    out = {k: v for k, v in e.items() if k not in ("draft", "detail", "reasons", "text")}
    if "violations" in out:
        out["violations"] = [v.get("category", "violation") if isinstance(v, dict) else "violation" for v in out["violations"]]
    return out


class Session:
    def __init__(self, playbook_id, intake, language, demo_guardrail):
        self.id = uuid.uuid4().hex[:12]
        self.pb = get_playbook(playbook_id)
        self.state = CaseState(intake, language)
        self.audit = AuditLog()
        # Per-session fault, never the process-wide env var: it would hit every concurrent session.
        self.fault = {"stage": self.pb.stages[1].id, "times": 1, "draft_suffix": UNSAFE_SUFFIX} if demo_guardrail else None
        # TEST ONLY: NURY_TEST_ESCALATE=1 (server env, never set for the demo) makes stage 2 fail all 3 tries
        # when the demo box is ticked, so the escalation path can be viewed once in a browser.
        if demo_guardrail and os.environ.get("NURY_TEST_ESCALATE") == "1":
            self.fault["times"] = 3
        self.current = None        # stage id being worked
        self.waiting = None        # StageResult at the gate
        self.decision = None
        self.cv = threading.Condition()
        self.done = False
        self.error = None
        self.halted = None         # message when stopped / escalated / error
        self.thread = threading.Thread(target=self.work, daemon=True)
        self.thread.start()

    def gate(self, result):
        with self.cv:
            self.waiting, self.decision = result, None
            self.cv.wait_for(lambda: self.decision is not None)
            d, self.waiting = self.decision, None
            return d

    def work(self):
        try:
            client = GlooClient()
            for s in self.pb.stages:
                self.current = s.id
                r = run_stage(s.id, self.state, self.gate, client, self.audit,
                              fault_injection=self.fault, playbook=self.pb.id)
                if r.status not in ("approved", "edited"):
                    self.halted = r.message
                    break
        except Exception as e:
            self.error = type(e).__name__
        self.current, self.done = None, True

    def decide(self, action, text=None):
        with self.cv:
            if self.waiting is None:
                return False
            self.decision = GateDecision(action, text)
            self.cv.notify_all()
            return True

    def progress(self, ev):
        """What the engine is doing right now, read from real audit events. No timers, no guesses.
        phase: writing | checking | regenerating | ready | escalated | idle. Carries categories and counts only."""
        sid = self.current or (self.waiting.stage_id if self.waiting else None)
        if not sid:
            return {"phase": "idle", "stage": None, "attempt": 0, "elapsed_s": 0}
        mine = [e for e in ev if e.get("stage") == sid]
        start = next((e for e in reversed(mine) if e["kind"] == "stage_start"), None)
        mine = mine[mine.index(start):] if start else mine
        last = mine[-1] if mine else None
        calls = [e for e in mine if e["kind"] == "gloo_call"]
        fails = [e for e in mine if e["kind"] in ("draft_rejected", "gloo_block")]
        if self.waiting:
            phase = "ready"
        elif last and last["kind"] == "escalated":
            phase = "escalated"
        elif last and last["kind"] == "check":
            phase = "checking"
        elif fails and last and last["kind"] in ("draft_rejected", "gloo_block", "gloo_call"):
            phase = "regenerating"
        else:
            phase = "writing"
        elapsed = 0.0
        if start:
            t0 = datetime.fromisoformat(start["ts"])
            t1 = datetime.fromisoformat(last["ts"]) if phase in ("ready", "escalated") and last else datetime.now(timezone.utc)
            elapsed = max(0.0, (t1 - t0).total_seconds())
        return {"phase": phase, "stage": sid, "attempt": min(len(fails) + 1, 3), "calls": len(calls),
                "elapsed_s": int(elapsed)}

    def view(self):
        ev = list(self.audit.events)
        stages = []
        for s in self.pb.stages:
            res = self.state.results.get(s.id)
            stages.append({"id": s.id, "title": s.title,
                           "status": res.status if res else ("working" if s.id == self.current else "pending"),
                           "final": res.final if res else None,
                           "disclaimer": res.disclaimer if res else None,
                           "metrics": res.metrics if res else None})
        gate = None
        if self.waiting:
            w = self.waiting
            gate = {"id": w.stage_id, "title": w.title, "draft": w.draft, "disclaimer": w.disclaimer, "metrics": w.metrics}
        # Guardrail status strip for the stage in progress. Never carries rejected text.
        strip = None
        if self.current:
            mine = [e for e in ev if e.get("stage") == self.current]
            fails = [e for e in mine if e["kind"] in ("draft_rejected", "gloo_block")]
            if fails:
                last_check = [e for e in mine if e["kind"] == "check"]
                strip = ("passed" if (self.waiting or (last_check and last_check[-1]["passed"]))
                         else f"Draft rejected by guardrail. Regenerating ({min(len(fails) + 1, 3)} of 3).")
        progress = self.progress(ev)
        log = [safe_event(e) for e in ev]
        return {"id": self.id, "playbook": {"id": self.pb.id, "title": self.pb.title}, "stages": stages, "gate": gate, "strip": strip, "progress": progress, "halted": self.halted,
                "error": self.error, "done": self.done, "log": log, "language": self.state.language,
                "package": {s["id"]: s["final"] for s in stages if s["final"]} if self.done and not self.halted else None}


class H(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        p = self.path.split("?")[0]
        if p == "/":
            b = (STATIC / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
        elif p == "/api/playbooks":
            self._json({"playbooks": playbooks()})
        elif p.startswith("/api/session/"):
            s = SESSIONS.get(p.split("/")[3])
            self._json(s.view() if s else {"error": "no such session"}, 200 if s else 404)
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        p, b = self.path, self._body()
        if p == "/api/run":
            intake = (b.get("intake") or "").strip()
            if not intake:
                return self._json({"error": "Type what the family told you."}, 400)
            pid = b.get("playbook") or "detention"
            chosen = next((p for p in playbooks() if p["id"] == pid), None)
            if not chosen or chosen["status"] != "live":
                return self._json({"error": "That crisis is not available yet."}, 400)
            try:
                s = Session(pid, intake, b.get("language", "es"), bool(b.get("demo_guardrail")))
            except PlaybookError:
                return self._json({"error": "That crisis is not available yet."}, 400)
            SESSIONS[s.id] = s
            self._json({"id": s.id})
        elif p.startswith("/api/session/") and p.endswith("/decision"):
            s = SESSIONS.get(p.split("/")[3])
            act = b.get("action")
            if not s or act not in ("approve", "edit", "stop") or (act == "edit" and not (b.get("text") or "").strip()):
                return self._json({"error": "bad request"}, 400)
            self._json({"ok": s.decide(act, b.get("text"))})
        else:
            self._json({"error": "not found"}, 404)

    def log_message(self, *a):  # no request logging: keeps intake text out of logs
        pass


def main():
    port = int(os.environ.get("PORT", "8080"))
    print(f"Nury on http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()


if __name__ == "__main__":
    main()
