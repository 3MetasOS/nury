"""Nury pastor app server. Stdlib only. Run from code/:  python3 -m app.server  (http://127.0.0.1:8080)

One session per intake. The engine runs in a worker thread; its approval gate blocks
until the pastor posts a decision. The API never returns rejected drafts.
There is no send path: nothing here contacts the family.
"""
import json
import os
import subprocess
import re
import threading
import uuid
import urllib.parse
import difflib
import textwrap
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from nury.audit import AuditLog
from nury import casefile as cf
from nury.engine import UNSAFE_SUFFIX, CaseState, GateDecision, compute_outcome, get_playbook, run_stage
from nury.privacy import PrivacyClient, make_client, privacy_enabled, propose_terms
from nury.playbook import PLAYBOOKS_DIR, PlaybookError, list_playbooks
from nury import log
from nury import replay

STATIC = Path(__file__).parent / "static"
# 'Our network' screen: hack-jedi's app/network_api.py. Mounted as its docstring says: every /api/network request goes to
# handle(method, path, body_bytes) -> (status, content_type, bytes), and /network serves static/network.html.
try:
    from app import network_api  # type: ignore
except Exception:
    network_api = None
STATIC_OK = re.compile(r"^/(fonts/)?[A-Za-z0-9_-]+\.(html|css|js|svg|woff2)$")
MIME = {"woff2": "font/woff2", "html": "text/html; charset=utf-8", "css": "text/css; charset=utf-8", "js": "text/javascript; charset=utf-8", "svg": "image/svg+xml"}
CASES_ROOT = str(Path(__file__).resolve().parents[1] / "cases")   # saved by the app on the server's disk, gitignored
CASE_ID = re.compile(r"^[A-Za-z0-9._-]{1,80}$")
SESSIONS = {}

# Hardening limits (documents/product/CODE_REVIEW.md). Each can be raised with an environment variable.
MAX_BODY = 1_000_000          # bytes of any request body
MAX_INTAKE = 20_000           # characters of an intake, a revision note or a pastor's edit
MAX_PROTECTED, MAX_TERM = 50, 80
MAX_BUSY = int(os.environ.get("NURY_MAX_BUSY", "3"))            # runs writing at the same time (a run waiting at a gate costs nothing)
MAX_SESSIONS = int(os.environ.get("NURY_MAX_SESSIONS", "50"))
SESSION_TTL_S = int(os.environ.get("NURY_SESSION_TTL_S", str(4 * 3600)))
RUN_CALL_BUDGET = int(os.environ.get("NURY_RUN_CALL_BUDGET", "60"))   # Gloo HTTP calls one run may make (a normal run makes 5 to 12)
SEC_HEADERS = (("X-Content-Type-Options", "nosniff"), ("X-Frame-Options", "DENY"), ("Referrer-Policy", "no-referrer"),
               ("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: blob:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; "
                "form-action 'self'; frame-ancestors 'none'"))


class BadRequest(Exception):
    def __init__(self, message, code=400):
        super().__init__(message)
        self.message, self.code = message, code


def busy_count():
    """Sessions that are writing a draft now. A session waiting at a gate or finished is not busy."""
    return sum(1 for x in list(SESSIONS.values()) if not x.done and x.waiting is None)


def purge_sessions(now=None):
    """Drop sessions older than the TTL (a run left at a gate is stopped first) and, over the cap, the oldest finished ones."""
    now = time.time() if now is None else now
    for sid, x in list(SESSIONS.items()):
        if now - getattr(x, "created", now) > SESSION_TTL_S:
            if not x.done and hasattr(x, "abandon"):
                x.abandon()
            SESSIONS.pop(sid, None)
    over = len(SESSIONS) - MAX_SESSIONS
    if over > 0:
        for sid in sorted((k for k, x in SESSIONS.items() if x.done), key=lambda k: SESSIONS[k].created)[:over]:
            SESSIONS.pop(sid, None)
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
        t = re.sub(r"^# .*\n+", "", t)                                       # heading
        t = re.sub(r"^What the pastor typed, exactly\.[^\n]*\n+", "", t)       # save_case's note line
        t = re.sub(r"\n*\[Index\]\(index\.md\)\s*$", "", t)                  # page footer
        return t.strip()
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
            "This is an updated draft of the case. It sits beside the first draft, which is unchanged.\n\n"
            "## What the pastor reported\n\n"
            f"- Step: {rv.get('step') or 'not named'}\n- Result: {RESULT_LABEL.get(rv.get('result'), 'unknown')}\n"
            f"- What happened: {rv.get('note', '').strip()}\n\n"
            "## Stages drafted again\n\n" + ", ".join(stage_ids) + "\n\n"
            "## Compared with the earlier version\n\n" + "\n".join(rows) + "\n\n"
            "Nury records what the pastor reported and drafts again. It does not predict what will happen next.\n")
    (d / "changes.md").write_text(text, encoding="utf-8")
    (d / "revision.json").write_text(json.dumps({"revises": rv["case_id"], "step": rv.get("step"), "result": rv.get("result")}), encoding="utf-8")


STAGE_LINE = {   # used only when a playbook's stage has no `summary` of its own
    "pastor": "For you. Nury drafts it from what the family told you. You read it and decide.",
    "family": "For the family, in their language, drafted from approved sources. You approve or edit it.",
}


def crisis_detail():
    """UI content for the crisis detail page (app-owned display data, keyed by playbook id). Not core, not a prompt."""
    f = Path(__file__).parent / "crisis_detail.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {"common_never": [], "playbooks": {}}


def stage_lines(pid):
    """[{id, title, line}] for the crisis detail page, from the playbook itself. Nothing here names a crisis."""
    try:
        pb = get_playbook(pid)
    except PlaybookError:
        return []
    out = []
    for st in pb.stages:
        extra = getattr(st, "summary", "") or ""
        out.append({"id": st.id, "title": re.sub(r"^\d+\.\s*", "", st.title),
                    "line": extra or STAGE_LINE.get(st.audience, STAGE_LINE["family"])})
    return out


def _case_title(case):
    """The CURRENT playbook title for a saved case (the stored title is the one at save time)."""
    pid = (case.get("meta") or {}).get("playbook")
    for p in list_playbooks():
        if p.get("id") == pid:
            return p.get("title") or (case.get("meta") or {}).get("title") or pid
    return (case.get("meta") or {}).get("title") or pid or "Case"


def _iso(created):
    """case.json 'created' is '2026-10-07 03:20 UTC'; the page wants ISO."""
    return (created or "").replace(" UTC", "Z").replace(" ", "T") if created else ""


def cases_overview():
    """Every saved case with what the home and cases pages need: family id, version, follow-up flag, a one-line summary."""
    out = []
    for c in cf.list_cases(CASES_ROOT):
        try:
            loaded = cf.load_case(c["id"], CASES_ROOT)
        except Exception as e:
            log.note("server.cases_overview", e)
            continue
        meta = loaded["meta"]
        m = re.search(r"^Situation:\s*(.+)$", loaded["pages"].get("index.md", ""), re.M)
        fam = base_id(c["id"])
        ver = 1 if c["id"] == fam else int(c["id"].rsplit("-v", 1)[1])
        out.append({"id": c["id"], "family_id": fam, "playbook": c["playbook"], "title": c.get("title") or meta.get("title") or c["id"],
                    "created": c.get("created"), "iso": _iso(c.get("created")), "version": ver, "status": "saved",
                    "followup": bool(meta.get("needs_follow_up")), "summary": (textwrap.shorten(m.group(1).strip(), width=110, placeholder="\u2026") if m else "")})
    counts = {}
    for c in out:
        counts[c["family_id"]] = max(counts.get(c["family_id"], 1), c["version"])
    for c in out:
        c["version_count"] = counts[c["family_id"]]
    return out


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
        p["stages"] = stage_lines(p["id"]) if p["status"] == "live" else []
        det = crisis_detail()
        p["detail"] = dict(det["playbooks"].get(p["id"], {}), common_never=det.get("common_never", [])) if p["id"] in det["playbooks"] else None
        pj_file = PLAYBOOKS_DIR / p["id"] / "playbook.json"
        pj = json.loads(pj_file.read_text(encoding="utf-8")) if pj_file.is_file() else {}
        langs = pj.get("languages", [])
        dflt = pj.get("default_family_language")
        p["languages"] = sorted(langs, key=lambda l: (l != dflt, l))   # the family's default language first
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
        self.created = time.time()
        self.abandoned = False
        self.pb = get_playbook(playbook_id)
        self.language = language
        self.intake = intake
        self.rec = None            # run ledger recorder (numbers only); None when the ledger is unavailable
        self.revision = revision      # {case_id, step, result, note} when this run revises a saved case
        # One privacy client per session: its token map lives here. The pastor's confirmed list is the list that counts.
        self.client = make_client(protected=protected) if protected is not None else make_client(intake=intake)
        try:   # every vetted phone, link and email of this run stays intact; the family's own numbers are still tokenized
            if hasattr(self.client, "allow_playbook"):
                self.client.allow_playbook(self.pb)
        except Exception as e:
            log.note("server.allow_playbook", e)
        try:   # church contacts keep their phones and links readable in the model context (INTERFACE.md, Church network)
            from nury import network as net
            if hasattr(self.client, "allow_network"):
                self.client.allow_network(net.load_network(root=str(Path(CASES_ROOT).parent / "network")).list())
        except Exception as e:
            log.note("server.allow_network", e)
        inner = getattr(self.client, "inner", self.client)
        self.replay = bool(getattr(inner, "replay", False))          # recorded model words, live checks (nury/replay.py)
        self.replay_edited = False
        if self.replay:
            inner.use_playbook(playbook_id, language)
        if hasattr(inner, "max_calls"):           # the most Gloo HTTP calls this one run may make
            inner.max_calls = RUN_CALL_BUDGET
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
        try:
            from nury import ledger
            self.rec = ledger.Recorder(self.pb.id, language)
        except Exception:
            self.rec = None
        self.thread = threading.Thread(target=self.work, daemon=True)
        self.thread.start()

    def gate(self, result):
        with self.cv:
            if self.abandoned:                      # the session expired while this draft was being written
                return GateDecision("stop", None)
            self.waiting, self.decision = result, None
            self.cv.wait_for(lambda: self.decision is not None)
            d, self.waiting = self.decision, None
            if self.replay and d.action == "edit":
                self.replay_edited = True
        self._feedback(result, d)
        return d

    def _feedback(self, result, d):
        """One structured, name-free record of the pastor's decision, only when NURY_FEEDBACK is on. Never blocks the pastor."""
        try:
            from nury import feedback
            if feedback.mode() == "off":
                return
            final = None if d.action == "stop" else (d.text if d.action == "edit" else result.shown_text)
            label = (self.revision or {}).get("result")
            feedback.record_gate(result.stage_id, d.action, result.shown_text, final, self.client, self.audit.events, outcome_label=label,
                                 playbook=self.pb.id, language=self.language, run_id=getattr(self.rec, "run_id", None))
        except Exception as e:
            log.note("server.feedback_gate", e)

    def work(self):
        try:
            client = self.client
            gate = client.wrap_gate(self.gate) if hasattr(client, "wrap_gate") else self.gate   # protects names added in an Edit
            for s in self.pb.stages:
                self.current = s.id
                r = run_stage(s.id, self.state, gate, client, self.audit,
                              fault_injection=self.fault, playbook=self.pb.id)
                self.results.append(r)
                if self.rec:
                    self.rec.stage_done(r, self.audit.events)
                if self.replay:                       # the Jev scores of the recorded run, shown as recorded
                    self.audit.log("jev_recorded", stage=s.id, label="recorded", scores=getattr(getattr(self.client, "inner", self.client), "jev_scores", lambda _s: [])(s.id))
                if r.status not in ("approved", "edited"):
                    try:
                        self.sources_list = compute_outcome(self.pb.id, self.state, self.results)["package"].get("sources_list", [])
                    except Exception:
                        self.sources_list = []
                    self.halted = r.message
                    break
        except Exception as e:
            self.error = type(e).__name__
        try:
            if self.rec:
                self.rec.finish(compute_outcome(self.pb.id, self.state, self.results))
        except Exception as e:
            log.note("server.ledger_finish", e)
        self.current, self.done = None, True

    def save(self):
        """Save the approved package to a local case folder. Raises cf.CaseError unless every stage is approved or edited."""
        new_id = next_version_id(self.revision["case_id"]) if self.revision else None
        r = cf.save_case(self.state, self.audit, playbook=self.pb.id, root=CASES_ROOT, case_id=new_id,
                         privacy=self.client if isinstance(self.client, PrivacyClient) else None)
        self.case_id = r["id"]
        d = Path(r["path"])
        if not (d / "intake.md").exists():   # save_case writes it now; this only covers an older core
            (d / "intake.md").write_text("# Intake\n\n" + self.intake.strip() + "\n", encoding="utf-8")
        if self.revision:
            self._write_changes(d, r["id"])
        return {"id": r["id"], "version": r["id"], "path": os.path.relpath(r["path"], Path(CASES_ROOT).parent.parent)}

    def _write_changes(self, d, new_id):
        write_changes(d, new_id, self.revision, [s.id for s in self.pb.stages])

    def map_svg(self):
        try:
            return cf.nextsteps_svg(self.pb, self.state, "Next steps")
        except Exception:
            return None

    def decide(self, action, text=None, stage=None):
        """Record the pastor's decision for the draft that is waiting. When stage is given it must be that draft's stage:
        a double click, a second tab or a late click can never approve a draft the pastor has not seen."""
        with self.cv:
            if self.waiting is None:
                return False
            if stage is not None and stage != self.waiting.stage_id:
                return False
            self.decision = GateDecision(action, text)
            self.cv.notify_all()
            return True

    def abandon(self):
        """Stop a run nobody is watching any more (called when its session expires)."""
        with self.cv:
            self.abandoned = True
            if self.waiting is not None and self.decision is None:
                self.decision = GateDecision("stop", None)
                self.cv.notify_all()

    def progress(self, ev):
        """What the engine is doing right now, read from real audit events. No timers, no guesses.
        phase: writing | checking | checking_jev | regenerating | ready | escalated | idle. Carries categories and counts only."""
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
        elif last and last["kind"] == "jev_gate_start":
            phase = "checking_jev"          # Jev is classifying the draft; real event, ends when the jev_gate events arrive
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
        return {"id": self.id, "replay": self.replay, "replay_banner": replay.BANNER if self.replay else None,
                "replay_note": replay.EDIT_NOTE if self.replay and self.replay_edited else None,
                "playbook": {"id": self.pb.id, "title": self.pb.title}, "stages": stages, "gate": gate, "strip": strip, "progress": progress, "halted": self.halted,
                "error": self.error, "sources_list": self.sources_list, "done": self.done, "log": log, "language": self.state.language,
                "package": {s["id"]: s["final"] for s in stages if s["final"]} if self.done and not self.halted else None,
                "map_svg": self.map_svg() if self.done and not self.halted else None,
                "case_id": getattr(self, "case_id", None)}


def _build_info():
    """Read once at server start: the commit and its date from git, and the test counts from the last recorded run (a small JSON; missing means show nothing)."""
    out = {}
    root = Path(__file__).resolve().parent.parent.parent
    try:
        r = subprocess.run(["git", "-C", str(root), "log", "-1", "--format=%h|%cd", "--date=format:%Y-%m-%d %H:%M"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and "|" in r.stdout:
            out["commit"], out["date"] = r.stdout.strip().split("|", 1)
    except Exception:
        pass
    try:
        t = json.loads((Path(__file__).resolve().parent / "test_counts.json").read_text())
        if isinstance(t.get("product"), int) and isinstance(t.get("evaluation"), int):
            out["tests"] = {"product": t["product"], "evaluation": t["evaluation"], "recorded": str(t.get("recorded", ""))}
    except Exception:
        pass
    return out


BUILD = _build_info()


class H(BaseHTTPRequestHandler):
    timeout = 30      # seconds a connection may stall before the server drops it

    def end_headers(self):
        for k, v in SEC_HEADERS:
            self.send_header(k, v)
        super().end_headers()

    def _hosts(self):
        port = self.server.server_address[1]
        hosts = {f"127.0.0.1:{port}", f"localhost:{port}", f"[::1]:{port}"}
        hosts |= {h.strip().lower() for h in os.environ.get("NURY_ALLOWED_HOSTS", "").split(",") if h.strip()}
        return hosts

    def _guard(self, write):
        """False (and a 403 or 415 is sent) unless the request is for this server: a Host we serve, an Origin that is us
        (or absent), and, for a change, a JSON body. This stops a web page the pastor opens from driving the app."""
        hosts = self._hosts()
        if (self.headers.get("Host") or "").lower() not in hosts:
            self._json({"error": "This address is not allowed."}, 403)
            return False
        origin = self.headers.get("Origin")
        if origin is not None and origin.lower() not in {"http://" + h for h in hosts}:
            self._json({"error": "This request came from another site."}, 403)
            return False
        if write and (self.headers.get("Content-Type") or "").split(";")[0].strip().lower() != "application/json":
            self._json({"error": "Send JSON."}, 415)
            return False
        return True

    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def _raw(self):
        if not hasattr(self, "_rawcache"):
            try:
                n = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                raise BadRequest("The request length was not a number.")
            if n < 0:
                raise BadRequest("The request length was not valid.")
            if n > MAX_BODY:
                raise BadRequest("The request is too large.", 413)
            try:
                self._rawcache = self.rfile.read(n)
            except OSError:                                   # a stalled client: the socket timeout fired
                raise BadRequest("The request took too long.", 408)
        return self._rawcache

    def _body(self):
        return json.loads(self._raw() or b"{}")

    def _network(self, method, path):
        """True when the request belongs to the network screen and was answered."""
        if not (network_api and path.split("?")[0].startswith("/api/network")):
            return False
        status, ctype, body = network_api.handle(method, self.path, self._raw())
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
        return True

    def do_PUT(self):
        if not self._guard(True):
            return
        try:
            self._network("PUT", self.path) or self._json({"error": "not found"}, 404)
        except BadRequest as e:
            self._json({"error": e.message}, e.code)

    def do_DELETE(self):
        if not self._guard(True):
            return
        try:
            self._network("DELETE", self.path) or self._json({"error": "not found"}, 404)
        except BadRequest as e:
            self._json({"error": e.message}, e.code)

    def _print_page(self, kind, ident, copy, screen_note):
        """The print page for a saved case or a finished run: (html, title) or (None, None)."""
        from app import pdf_export
        fonts = "/fonts" if screen_note else pdf_export.STATIC.as_uri() + "/fonts"
        if kind == "case":
            if not CASE_ID.match(ident):
                return None, None
            try:
                c = cf.load_case(ident, CASES_ROOT)
            except Exception:
                return None, None
            title = _case_title(c)
            data = pdf_export.case_payload(c, title)
            return pdf_export.print_html("case", data, copy, title, _iso(c["meta"].get("created")), fonts_base=fonts, screen_note=screen_note, extras=pdf_export.playbook_extras(c["meta"].get("playbook", ""), PLAYBOOKS_DIR)), title
        s_ = SESSIONS.get(ident)
        if not s_:
            return None, None
        v = s_.view()
        title = (v.get("playbook") or {}).get("title") or "Case"
        iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return pdf_export.print_html("session", v, copy, title, iso, fonts_base=fonts, screen_note=screen_note, extras=pdf_export.playbook_extras((v.get("playbook") or {}).get("id", ""), PLAYBOOKS_DIR)), title

    def do_GET(self):
        if not self._guard(False):
            return
        try:
            self._get()
        except BadRequest as e:
            self._json({"error": e.message}, e.code)

    def _get(self):
        p = self.path.split("?")[0]
        if self._network("GET", p):
            return
        if p == "/network" and (STATIC / "network.html").is_file():
            p = "/network.html"
        elif p in ("/how-it-was-built", "/how-it-was-built/"):
            p = "/how-it-was-built.html"
        elif p in ("/observability", "/observability/"):
            p = "/observability.html"
        elif p.rstrip("/") in ("/standards", "/what-did-not-work", "/economics", "/pattern", "/run-your-own", "/about"):
            p = p.rstrip("/") + ".html"
        elif p in ("/build-log", "/build-log/"):
            p = "/build-log.html"
        elif p in ("/improvement", "/improvement/", "/self-improvement", "/self-improvement/"):
            p = "/improvement.html"      # the page is called Self-improvement; the old path keeps working
        if p == "/memorial/nury.jpg" and (STATIC / "memorial" / "nury.jpg").is_file():      # the photo slot on About: only when Juan provides the file
            b = (STATIC / "memorial" / "nury.jpg").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
            return
        if STATIC_OK.match(p) and (STATIC / p[1:]).is_file() and p != "/index.html":
            b = (STATIC / p[1:]).read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", MIME[p.rsplit(".", 1)[1]])
            if p.endswith(".woff2"):
                self.send_header("Cache-Control", "public, max-age=604800")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
        elif p == "/api/ops":
            from app import evals_api
            self._json(evals_api.ops())
        elif p == "/api/improvement":
            from app import improvement_api
            self._json(improvement_api.view())
        elif p == "/api/evals":
            from app import evals_api
            self._json(evals_api.evals())
        elif p == "/api/rules":
            from app import rules_info
            self._json(rules_info.rules())
        elif p.startswith("/api/playbook/"):
            from app import rules_info
            d = rules_info.playbook_detail(p.split("/")[3])
            self._json(d if d else {"error": "unknown playbook"}, 200 if d else 404)
        elif p == "/api/build":
            self._json(BUILD)
        elif p == "/api/features":
            fb = False
            sentence = ""
            try:
                from nury import feedback
                fb, sentence = feedback.mode() != "off", feedback.CONSENT_SENTENCE
            except Exception as e:
                log.note("server.features_feedback", e)
            chips = []
            try:
                from nury import feedback as _f
                chips = [{"slug": c, "label": _f.CHIP_LABELS[c]} for c in _f.CHIPS] if fb else []
            except Exception as e:
                log.note("server.features_chips", e)
            try:
                from nury import checks as _checks
                n_checks = len(_checks.REGISTRY)
            except Exception:
                n_checks = None
            self._json({"replay": replay.active(), "replay_banner": replay.BANNER if replay.active() else "",
                        "network": (STATIC / "network.html").is_file(), "followup": hasattr(cf, "set_follow_up"), "named_checks": n_checks,
                        "feedback": fb, "consent_sentence": sentence if fb else "", "chips": chips})
        elif p == "/":
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
            self._json({"cases": cases_overview()})
        elif p.startswith("/api/case/") and p.endswith("/export"):
            cid = urllib.parse.unquote(p.split("/")[3])
            if not CASE_ID.match(cid):
                return self._json({"error": "bad id"}, 400)
            try:
                c = cf.load_case(cid, CASES_ROOT)
            except Exception:
                return self._json({"error": "case not found"}, 404)
            from app import pdf_export
            z, _pdf = pdf_export.export_zip_bytes(cid, c, _case_title(c), _iso(c["meta"].get("created")), extras=pdf_export.playbook_extras(c["meta"].get("playbook", ""), PLAYBOOKS_DIR))   # PDFs and records/case.json; never the token map
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", f'attachment; filename="{cid}.zip"')
            self.send_header("Content-Length", str(len(z)))
            self.end_headers()
            self.wfile.write(z)
        elif (m := re.match(r"^/api/session/([A-Za-z0-9._%-]+)/export$", p)):
            from app import pdf_export
            s_ = SESSIONS.get(urllib.parse.unquote(m.group(1)))
            if not s_:
                return self._json({"error": "no such session"}, 404)
            vw = s_.view()
            z, _ok = pdf_export.session_zip_bytes(vw, (vw.get("playbook") or {}).get("title") or "Case", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                                  extras=pdf_export.playbook_extras((vw.get("playbook") or {}).get("id", ""), PLAYBOOKS_DIR))
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", 'attachment; filename="nury-copies.zip"')
            self.send_header("Content-Length", str(len(z)))
            self.end_headers()
            self.wfile.write(z)
        elif (m := re.match(r"^/api/(case|session)/([A-Za-z0-9._%-]+)/pdf/(family|pastor)$", p)):
            from app import pdf_export
            html_, title = self._print_page(m.group(1), urllib.parse.unquote(m.group(2)), m.group(3), pdf_export.find_chrome() is None)
            if html_ is None:
                return self._json({"error": "not found"}, 404)
            pdf = pdf_export.render_pdf(html_) if pdf_export.find_chrome() else None
            if not pdf:
                return self._json({"error": pdf_export.NO_BROWSER, "print_url": f"/{m.group(1)}-print/{m.group(2)}/{m.group(3)}"}, 501)
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", f'attachment; filename="{pdf_export.slug(title)}-{m.group(3)}-copy.pdf"')
            self.send_header("Content-Length", str(len(pdf)))
            self.end_headers()
            self.wfile.write(pdf)
        elif (m := re.match(r"^/(case|session)-print/([A-Za-z0-9._%-]+)/(family|pastor)$", p)):
            from app import pdf_export
            html_, _t = self._print_page(m.group(1), urllib.parse.unquote(m.group(2)), m.group(3), True)
            if html_ is None:
                return self._json({"error": "not found"}, 404)
            b = html_.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
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
        if not self._guard(True):
            return
        try:
            self._post()
        except BadRequest as e:
            self._json({"error": e.message}, e.code)

    def _post(self):
        p = self.path
        if self._network("POST", p):
            return
        try:
            b = self._body()
        except (ValueError, UnicodeDecodeError):      # json.JSONDecodeError is a ValueError
            return self._json({"error": "The request was not valid JSON."}, 400)
        if not isinstance(b, dict):
            return self._json({"error": "The request must be a JSON object."}, 400)
        if p == "/api/propose-terms":
            if len(str(b.get("intake") or "")) > MAX_INTAKE:
                return self._json({"error": f"That is too long. Keep it under {MAX_INTAKE:,} characters."}, 400)
            self._json({"on": privacy_enabled(), "terms": propose_terms(b.get("intake") or "") if privacy_enabled() else []})
        elif p == "/api/revision-preview":
            try:
                intake, meta = revision_intake(b.get("case_id", ""), b.get("step", ""), b.get("result", ""), b.get("note", ""))
            except Exception:
                return self._json({"error": "case not found"}, 404)
            # Names are proposed from the family's words and the pastor's note only, never from the structured
            # "Step:" and "Result:" labels or the checklist sentence the pastor picked (they are not names).
            terms_text = original_intake(cf.load_case(b.get("case_id", ""), CASES_ROOT)["pages"]) + "\n\n" + str(b.get("note", "")).strip()
            self._json({"intake": intake, "terms_text": terms_text, "playbook": meta["playbook"], "language": meta.get("language", "es")})
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
            if len(intake) > MAX_INTAKE or (rev and len(str(rev.get("note", ""))) > MAX_INTAKE):
                return self._json({"error": f"That is too long. Keep it under {MAX_INTAKE:,} characters."}, 400)
            pid = b.get("playbook") or "detention"
            chosen = next((p for p in playbooks() if p["id"] == pid), None)
            if not chosen or chosen["status"] != "live":
                return self._json({"error": "That crisis is not available yet."}, 400)
            if replay.active() and not replay.is_sample(pid, intake, b.get("language", "es")):
                return self._json({"error": replay.REFUSAL, "replay": True}, 400)
            if b.get("language", "es") not in chosen.get("languages", ["es"]):
                return self._json({"error": "That language is not available for this crisis."}, 400)
            if isinstance(b.get("protected"), list) and (len(b["protected"]) > MAX_PROTECTED or any(len(str(t.get("term", "") if isinstance(t, dict) else t)) > MAX_TERM for t in b["protected"])):
                return self._json({"error": "Too many protected names, or a name is too long."}, 400)
            purge_sessions()
            if busy_count() >= MAX_BUSY:
                return self._json({"error": "Nury is busy with other drafts. Try again in a minute."}, 429)
            try:
                prot = b.get("protected")
                prot = [{"term": str(t.get("term", "")).strip(), "kind": t.get("kind", "person")} for t in prot if str(t.get("term", "")).strip()] if isinstance(prot, list) else None
                s = Session(pid, intake, b.get("language", "es"), bool(b.get("demo_guardrail")), prot,
                            {"case_id": rev["case_id"], "step": rev.get("step", ""), "result": rev.get("result", ""), "note": rev["note"]} if rev else None)
            except PlaybookError:
                return self._json({"error": "That crisis is not available yet."}, 400)
            except Exception:                           # for example a missing key: say so in plain words, never drop the connection
                return self._json({"error": "Nury could not start. Check that the server has its keys, then try again."}, 500)
            SESSIONS[s.id] = s
            if rev and str(rev.get("result", "")).strip():
                try:   # the 'Something changed' outcome, counted without the pastor's note
                    from nury import feedback
                    feedback.record_outcome(pid, str(rev.get("result")), language=b.get("language", "es"))
                except Exception as e:
                    log.note("server.record_outcome", e)
            self._json({"id": s.id})
        elif p == "/api/feedback":
            try:
                from nury import feedback
                s_ = SESSIONS.get(str(b.get("session", "")))
                ok = False
                if s_ and feedback.mode() != "off" and str(b.get("chip", "")) in feedback.CHIPS:
                    ok = bool(feedback.record_chip(str(b.get("stage", "")), str(b["chip"]), playbook=s_.pb.id, language=s_.language,
                                                   run_id=getattr(s_.rec, "run_id", None)))
                self._json({"ok": ok})
            except Exception:
                self._json({"ok": False})
        elif p == "/api/evals/smoke":
            from app import evals_api
            code, payload = evals_api.start_smoke(b if isinstance(b, dict) else {})
            self._json(payload, code)
        elif p.startswith("/api/case/") and p.endswith("/followup"):
            cid = urllib.parse.unquote(p.split("/")[3])
            if not CASE_ID.match(cid):
                return self._json({"error": "bad id"}, 400)
            if not hasattr(cf, "set_follow_up"):
                return self._json({"error": "Follow-up flags are not available in this build."}, 501)
            if not isinstance(b.get("value"), bool):
                return self._json({"error": "value must be true or false"}, 400)
            try:
                cf.set_follow_up(cid, b["value"], CASES_ROOT)
            except FileNotFoundError:
                return self._json({"error": "case not found"}, 404)
            except cf.CaseError as e:
                return self._json({"error": str(e)}, 404 if str(e).startswith("no case") else 400)
            entry = next((c for c in cases_overview() if c["id"] == cid), None)
            self._json({"ok": True, "followup": b["value"], "case": entry})
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
            if not isinstance(b.get("stage"), str) or len(str(b.get("text") or "")) > MAX_INTAKE:
                return self._json({"error": "bad request"}, 400)
            ok = s.decide(act, b.get("text"), stage=b["stage"])
            self._json({"ok": ok}, 200 if ok else 409)
        else:
            self._json({"error": "not found"}, 404)

    def log_message(self, *a):  # no request logging: keeps intake text out of logs
        pass


def rebuild_static_pages():
    """Regenerate the document pages (How this was built, Build log, Standards, ...) from their Markdown when python-markdown is installed.
    The server itself needs no extra package: without it, the committed pages are served as they are. Never stops the server."""
    try:
        from app import build_docs
        build_docs.build(); build_docs.build_log(); build_docs.build_standards(); build_docs.build_about(); build_docs.build_wdnw(); build_docs.build_pattern()
        for a, b, c, d in build_docs.SIMPLE_DOCS:
            build_docs.build_simple(a, b, c, d)
        return True
    except Exception:
        return False


def refresh_build_log_if_stale():
    """At start: if BUILD_LOG.md is newer than the built Build log page, regenerate the page (same sanitizer and secret scan), so it is never
    more than one restart behind. A failed scan keeps the old page and prints a warning. Never stops the server."""
    try:
        from app import build_docs
        src, out = build_docs.LOG_SRC, build_docs.LOG_OUT
        if not Path(src).is_file():
            return "no-source"
        if Path(out).is_file() and Path(out).stat().st_mtime >= Path(src).stat().st_mtime:
            return "current"
        try:
            build_docs.build_log()
            return "rebuilt"
        except SystemExit as e:
            print("WARNING: the Build log page was not refreshed:", e)
            return "scan-failed"
    except Exception as e:
        print("WARNING: the Build log page was not refreshed:", e)
        return "error"


def main():
    refresh_build_log_if_stale()
    if os.environ.get("NURY_REBUILD_PAGES") == "1":      # off by default: a hosted copy serves the committed pages
        print("pages rebuilt" if rebuild_static_pages() else "pages not rebuilt (python-markdown missing or a source file changed shape)")
    port = int(os.environ.get("PORT", "8080"))
    print(f"Nury on http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()


if __name__ == "__main__":
    main()
