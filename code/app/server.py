"""Nury pastor app server. Stdlib only. Run from code/:  python3 -m app.server  (http://127.0.0.1:8080)

One session per intake. The engine runs in a worker thread; its approval gate blocks
until the pastor posts a decision. The API never returns rejected drafts.
There is no send path: nothing here contacts the family.
"""
import json
import os
import re
import threading
import uuid
import urllib.parse
import difflib
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from nury.audit import AuditLog
from nury import casefile as cf
from nury.engine import UNSAFE_SUFFIX, CaseState, GateDecision, compute_outcome, get_playbook, run_stage
from nury.gloo_client import GlooClient
from nury.privacy import PrivacyClient, make_client, privacy_enabled, propose_terms
from nury.playbook import PLAYBOOKS_DIR, PlaybookError, list_playbooks

STATIC = Path(__file__).parent / "static"
CASES_ROOT = str(Path(__file__).resolve().parents[1] / "cases")   # local only, gitignored
CASE_ID = re.compile(r"^[A-Za-z0-9._-]{1,80}$")
SESSIONS = {}
GENERIC_PLACEHOLDER = "Who called, who is affected, where, when, and what the family asks."


RESULT_LABEL = {"hoped": "went as hoped", "not_hoped": "did not go as hoped", "unknown": "unknown"}


def base_id(cid):
    return re.sub(r"-v\d+$", "", cid)


def versions_of(cid):
    """All saved versions of one case, v1 first. v1 has the base id; later ones end in -vN."""
    b = base_id(cid)
    ids = [c["id"] for c in cf.list_cases(CASES_ROOT) if base_id(c["id"]) == b]
    return sorted(ids, key=lambda i: (0, 0) if i == b else (1, int(i.rsplit("-v", 1)[1])))


def next_version_id(cid):
    b = base_id(cid)
    nums = [1 if i == b else int(i.rsplit("-v", 1)[1]) for i in versions_of(cid)]
    return f"{b}-v{max(nums or [1]) + 1}"


def original_intake(pages):
    t = pages.get("intake.md")
    if t:
        return re.sub(r"^# .*\n+", "", t).strip()
    # Cases saved before intake.md existed: the approved triage is the structured intake.
    t = next((v for k, v in sorted(pages.items()) if k.startswith("01-")), "")
    return re.sub(r"^# .*\n+", "", t.split("\n---\n")[0]).strip()   # drop the page footer (links, disclaimer)


def revision_intake(case_id, step, result, note):
    """Original intake plus a dated update in the pastor's words. A record, never a prediction."""
    c = cf.load_case(case_id, CASES_ROOT)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    update = (f"UPDATE FROM THE PASTOR ({day}). Step: {step or 'not named'}. "
              f"Result: {RESULT_LABEL.get(result, 'unknown')}. What happened, in the pastor's words: {note.strip()}")
    return original_intake(c["pages"]) + "\n\n" + update, c["meta"]


def diff_pages(a_text, b_text):
    out = []
    for line in difflib.ndiff(a_text.splitlines(), b_text.splitlines()):
        tag = line[:2]
        if tag in ("+ ", "- ", "  "):
            out.append({"t": {"+ ": "add", "- ": "del", "  ": "same"}[tag], "x": line[2:]})
    return out


def write_changes(d, new_id, rv, stage_ids):
    """changes.md and revision.json for a revised case. Written next to the new version; v1 is never touched."""
    d = Path(d)
    old = cf.load_case(rv["case_id"], CASES_ROOT)["pages"]
    new = {p.name: p.read_text(encoding="utf-8") for p in d.glob("0*-*.md")}
    rows = []
    for name in sorted(new):
        title = re.sub(r"\.md$", "", re.sub(r"^\d+-", "", name))
        n = sum(1 for x in difflib.ndiff(old.get(name, "").splitlines(), new[name].splitlines()) if x[:2] in ("+ ", "- "))
        rows.append(f"- {title}: {'unchanged' if n == 0 else str(n) + ' lines differ'}")
    text = ("# What changed\n\n"
            f"This is version {new_id.rsplit('-v', 1)[1]} of the case. It sits beside the earlier version, which is unchanged.\n\n"
            "## What the pastor reported\n\n"
            f"- Step: {rv.get('step') or 'not named'}\n- Result: {RESULT_LABEL.get(rv.get('result'), 'unknown')}\n"
            f"- What happened: {rv.get('note', '').strip()}\n\n"
            "## Stages drafted again\n\n" + ", ".join(stage_ids) + "\n\n"
            "## Compared with the earlier version\n\n" + "\n".join(rows) + "\n\n"
            "Nury records what the pastor reported and drafts again. It does not predict what will happen next.\n")
    (d / "changes.md").write_text(text, encoding="utf-8")
    (d / "revision.json").write_text(json.dumps({"revises": rv["case_id"], "step": rv.get("step"), "result": rv.get("result")}), encoding="utf-8")


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
    def __init__(self, playbook_id, intake, language, demo_guardrail, protected=None, revision=None):
        self.id = uuid.uuid4().hex[:12]
        self.pb = get_playbook(playbook_id)
        self.intake = intake
        self.revision = revision      # {case_id, step, result, note} when this run revises a saved case
        # One privacy client per session: its token map lives here. The pastor's confirmed list is the list that counts.
        self.client = make_client(protected=protected) if protected is not None else make_client(intake=intake)
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
        self.results = []
        self.sources_list = []     # vetted names and links handed to the pastor on escalation
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
            client = self.client
            gate = client.wrap_gate(self.gate) if hasattr(client, "wrap_gate") else self.gate   # protects names added in an Edit
            for s in self.pb.stages:
                self.current = s.id
                r = run_stage(s.id, self.state, gate, client, self.audit,
                              fault_injection=self.fault, playbook=self.pb.id)
                self.results.append(r)
                if r.status not in ("approved", "edited"):
                    try:
                        self.sources_list = compute_outcome(self.pb.id, self.state, self.results)["package"].get("sources_list", [])
                    except Exception:
                        self.sources_list = []
                    self.halted = r.message
                    break
        except Exception as e:
            self.error = type(e).__name__
        self.current, self.done = None, True

    def save(self):
        """Save the approved package to a local case folder. Raises cf.CaseError unless every stage is approved or edited."""
        new_id = next_version_id(self.revision["case_id"]) if self.revision else None
        r = cf.save_case(self.state, self.audit, playbook=self.pb.id, root=CASES_ROOT, case_id=new_id,
                         privacy=self.client if isinstance(self.client, PrivacyClient) else None)
        self.case_id = r["id"]
        d = Path(r["path"])
        (d / "intake.md").write_text("# Intake\n\n" + self.intake.strip() + "\n", encoding="utf-8")   # the pastor's own words, local only
        if self.revision:
            self._write_changes(d, r["id"])
        return {"id": r["id"], "version": r["id"] if not self.revision else r["id"], "path": os.path.relpath(r["path"], Path(CASES_ROOT).parent.parent)}

    def _write_changes(self, d, new_id):
        write_changes(d, new_id, self.revision, [s.id for s in self.pb.stages])

    def map_svg(self):
        try:
            return cf.nextsteps_svg(self.pb, self.state, "Next steps")
        except Exception:
            return None

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
                "error": self.error, "sources_list": self.sources_list, "done": self.done, "log": log, "language": self.state.language,
                "package": {s["id"]: s["final"] for s in stages if s["final"]} if self.done and not self.halted else None,
                "map_svg": self.map_svg() if self.done and not self.halted else None,
                "case_id": getattr(self, "case_id", None)}


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
        elif p.startswith("/api/case/") and "/compare/" in p:
            parts = p.split("/")   # ['', 'api', 'case', A, 'compare', B]
            a, b = urllib.parse.unquote(parts[3]), urllib.parse.unquote(parts[5])
            if not (CASE_ID.match(a) and CASE_ID.match(b)):
                return self._json({"error": "bad id"}, 400)
            try:
                ca, cb = cf.load_case(a, CASES_ROOT)["pages"], cf.load_case(b, CASES_ROOT)["pages"]
            except Exception:
                return self._json({"error": "case not found"}, 404)
            names = sorted(n for n in set(ca) | set(cb) if re.match(r"0\d-", n))
            self._json({"a": a, "b": b, "pages": {n: diff_pages(ca.get(n, ""), cb.get(n, "")) for n in names}})
        elif p == "/api/cases":
            self._json({"cases": cf.list_cases(CASES_ROOT)})
        elif p.startswith("/api/case/") and p.endswith("/export"):
            cid = urllib.parse.unquote(p.split("/")[3])
            if not CASE_ID.match(cid):
                return self._json({"error": "bad id"}, 400)
            try:
                z = Path(cf.export_zip(cid, CASES_ROOT)).read_bytes()
            except Exception:
                return self._json({"error": "case not found"}, 404)
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", f'attachment; filename="{cid}.zip"')
            self.send_header("Content-Length", str(len(z)))
            self.end_headers()
            self.wfile.write(z)
        elif p.startswith("/api/case/"):
            cid = urllib.parse.unquote(p.split("/")[3])
            if not CASE_ID.match(cid):
                return self._json({"error": "bad id"}, 400)
            try:
                c = cf.load_case(cid, CASES_ROOT)
                c["versions"] = versions_of(cid)
                self._json(c)
            except Exception:
                self._json({"error": "case not found"}, 404)
        elif p == "/api/privacy":
            self._json({"on": privacy_enabled()})
        elif p == "/api/playbooks":
            self._json({"playbooks": playbooks()})
        elif p.startswith("/api/session/"):
            s = SESSIONS.get(p.split("/")[3])
            self._json(s.view() if s else {"error": "no such session"}, 200 if s else 404)
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        p, b = self.path, self._body()
        if p == "/api/propose-terms":
            self._json({"on": privacy_enabled(), "terms": propose_terms(b.get("intake") or "") if privacy_enabled() else []})
        elif p == "/api/revision-preview":
            try:
                intake, meta = revision_intake(b.get("case_id", ""), b.get("step", ""), b.get("result", ""), b.get("note", ""))
            except Exception:
                return self._json({"error": "case not found"}, 404)
            self._json({"intake": intake, "playbook": meta["playbook"], "language": meta.get("language", "es")})
        elif p == "/api/run":
            intake = (b.get("intake") or "").strip()
            rev = b.get("revise") if isinstance(b.get("revise"), dict) else None
            if rev:
                if not CASE_ID.match(str(rev.get("case_id", ""))) or not str(rev.get("note", "")).strip():
                    return self._json({"error": "Say what happened, then start."}, 400)
                try:
                    intake, meta = revision_intake(rev["case_id"], rev.get("step", ""), rev.get("result", ""), rev["note"])
                except Exception:
                    return self._json({"error": "case not found"}, 404)
                b["playbook"], b["language"] = meta["playbook"], meta.get("language", "es")
            if not intake:
                return self._json({"error": "Type what the family told you."}, 400)
            pid = b.get("playbook") or "detention"
            chosen = next((p for p in playbooks() if p["id"] == pid), None)
            if not chosen or chosen["status"] != "live":
                return self._json({"error": "That crisis is not available yet."}, 400)
            try:
                prot = b.get("protected")
                prot = [{"term": str(t.get("term", "")).strip(), "kind": t.get("kind", "person")} for t in prot if str(t.get("term", "")).strip()] if isinstance(prot, list) else None
                s = Session(pid, intake, b.get("language", "es"), bool(b.get("demo_guardrail")), prot,
                            {"case_id": rev["case_id"], "step": rev.get("step", ""), "result": rev.get("result", ""), "note": rev["note"]} if rev else None)
            except PlaybookError:
                return self._json({"error": "That crisis is not available yet."}, 400)
            SESSIONS[s.id] = s
            self._json({"id": s.id})
        elif p.startswith("/api/session/") and p.endswith("/save"):
            s = SESSIONS.get(p.split("/")[3])
            if not s:
                return self._json({"error": "no such session"}, 404)
            try:
                self._json(s.save())
            except cf.CaseError:
                self._json({"error": "Nothing was saved. Every stage must be approved or edited first."}, 400)
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
