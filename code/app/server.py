"""Nury pastor app server. Stdlib only. Run from code/:  python3 -m app.server  (http://127.0.0.1:8080)

One session per intake. The engine runs in a worker thread; its approval gate blocks
until the pastor posts a decision. The API never returns rejected drafts.
There is no send path: nothing here contacts the family.
"""
import json
import os
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from nury.audit import AuditLog
from nury.engine import DEMO_PROVOKE, CaseState, GateDecision, run_stage
from nury.gloo_client import GlooClient
from nury.stages import STAGES

STATIC = Path(__file__).parent / "static"
SESSIONS = {}
DEMO_INTAKE = ("Maria called at 2:07 AM, very upset, speaking Spanish. Her husband Jose was detained by immigration "
               "officers outside his workplace in Aurora around 6 PM yesterday. She does not know if the officers "
               "showed a warrant. Jose has lived here 14 years. They have two children, 8 and 11, both US citizens. "
               "Maria is afraid to leave the house tomorrow. She wants to know what to do tonight.")


class Session:
    def __init__(self, intake, language, demo_guardrail):
        self.id = uuid.uuid4().hex[:12]
        self.state = CaseState(intake, language)
        self.audit = AuditLog()
        self.provoke = DEMO_PROVOKE if demo_guardrail else None
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
            for s in STAGES:
                self.current = s.id
                r = run_stage(s.id, self.state, self.gate, client, self.audit, self.provoke)
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

    def view(self):
        ev = list(self.audit.events)
        stages = []
        for s in STAGES:
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
            calls = [e for e in mine if e["kind"] == "gloo_call"]
            fails = [e for e in mine if e["kind"] in ("draft_rejected", "gloo_block")]
            if fails:
                n = len(calls)
                last_check = [e for e in mine if e["kind"] == "check"]
                strip = ("passed" if (self.waiting or (last_check and last_check[-1]["passed"]))
                         else f"Draft rejected by guardrail. Regenerating ({min(n + 1, 3)} of 3).")
        log = [{k: v for k, v in e.items() if k not in ("draft", "detail")} for e in ev]
        return {"id": self.id, "stages": stages, "gate": gate, "strip": strip, "halted": self.halted,
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
        elif p == "/api/demo-intake":
            self._json({"intake": DEMO_INTAKE})
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
            s = Session(intake, b.get("language", "es"), bool(b.get("demo_guardrail")))
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
