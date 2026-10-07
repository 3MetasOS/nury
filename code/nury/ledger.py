"""The run ledger: an append-only record of how runs behaved, never of what they said.

One JSON line per stage and one per run, in data/ledger/ledger.jsonl (gitignored; NURY_LEDGER_DIR changes the folder).
A line holds numbers, short ids and counts: when, how long, which playbook and stage, how many attempts, which rule
categories fired, what Jev decided and how sure it was, tokens, cost, which Scripture provider, the outcome.

It NEVER holds text. No draft, no intake, no name, no case id that maps to a family. Two things make that true:

1. Lines are built from a fixed list of fields, copied one by one. Nothing is passed through.
2. Every string that goes in must match a short slug (lowercase letters, digits, underscore, dot, hyphen, up to 40
   characters). A string that does not match stops the line from being written. The ledger fails closed.

A ledger failure never breaks a run: record_* return False and the run goes on.

The app calls Recorder.stage_done(...) after each stage and Recorder.finish(...) at the end of the run.
summarize() reads the file back for GET /api/ops.
"""

import json
import math
import os
import re
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEFAULT_DIR = "data/ledger"
FILE = "ledger.jsonl"
SLUG = re.compile(r"[a-z0-9_.\-]{1,40}")
_LOCK = threading.Lock()
DECISIONS = ("pass", "uncertain", "reject", "unavailable", "skipped")


class LedgerError(ValueError):
    pass


def ledger_dir(root=None):
    return Path(root or os.environ.get("NURY_LEDGER_DIR") or DEFAULT_DIR)


def new_run_id():
    """Random, not derived from anything about the case."""
    return uuid.uuid4().hex[:12]


def _slug(v, what):
    if not isinstance(v, str) or not SLUG.fullmatch(v):
        raise LedgerError(f"{what} is not a short slug")
    return v


def _num(v, what, nullable=True):
    if v is None and nullable:
        return None
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        raise LedgerError(f"{what} is not a number")
    return round(v, 6) if isinstance(v, float) else v


def _int(v, what):
    n = _num(v, what, nullable=False)
    return int(n if n is not None else 0)


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


# ---------- building lines (field by field) ----------

def stage_line(run_id, playbook, language, rec, events, duration_ms=None):
    """One stage's summary. `rec` is a StageResult; `events` are the audit events of this run (any stage)."""
    m = rec.metrics or {}
    cats = {}
    for c in rec.reason_categories or []:
        cats[_slug(c, "category")] = cats.get(c, 0) + 1
    jev = {}
    for e in events:
        if e.get("kind") == "jev_gate" and e.get("stage") == rec.stage_id and e.get("question") not in (None, "*"):
            q = _slug(e["question"], "question")
            d = jev.setdefault(q, {"decisions": {}, "max_probability": 0.0, "last_probability": None, "probs": []})
            dec = _slug(e["decision"], "decision")
            d["decisions"][dec] = d["decisions"].get(dec, 0) + 1
            p = _num(e.get("probability"), "probability")
            if p is not None:
                d["probs"].append(round(p, 3))
                d["max_probability"] = max(d["max_probability"], p)
                d["last_probability"] = p
        if e.get("kind") == "jev_gate" and e.get("stage") == rec.stage_id and e.get("decision") in ("unavailable", "skipped"):
            jev.setdefault("*", {"decisions": {}, "max_probability": 0.0, "last_probability": None, "probs": []})["decisions"][e["decision"]] = 1
    provider = next((e.get("provider") for e in events if e.get("kind") == "scripture" and e.get("stage") == rec.stage_id), None)
    skills = sorted({_slug(s["name"], "skill") + "@" + _slug(str(s["version"]), "skill version").replace("@", "") for s in (m.get("skills") or [])})
    return {
        "type": "stage", "ts": _now(), "run": _slug(run_id, "run id"), "playbook": _slug(playbook, "playbook"),
        "stage": _slug(rec.stage_id, "stage"), "language": _slug(language, "language"),
        "status": _slug(rec.status, "status"), "escalated": bool(rec.escalated),
        "attempts": _int(m.get("attempts", 0), "attempts"),
        "rule_categories": cats,
        "jev": jev,
        "jev_calls": _int(m.get("jev_calls", 0), "jev_calls"),
        "jev_ms": _num(m.get("jev_ms", 0), "jev_ms"),
        "tokens_in": _int(m.get("input_tokens", 0), "tokens_in"),
        "tokens_out": _int(m.get("output_tokens", 0), "tokens_out"),
        "cost_usd": _num(m.get("cost_usd"), "cost"),
        "latency_s": _num(m.get("latency_s", 0), "latency"),
        "duration_ms": _num(duration_ms, "duration"),
        "skills": skills,
        "scripture_provider": _slug(provider, "provider") if provider else None,
    }


def run_line(run_id, playbook, language, outcome, results, duration_ms=None):
    """One run's summary. `outcome` is the engine's outcome dict; `results` the list of StageResult."""
    ms = [r.metrics or {} for r in results]
    costs = [m.get("cost_usd") for m in ms]
    cost = None if any(c is None for c in costs) or not costs else round(sum(costs), 6)
    return {
        "type": "run", "ts": _now(), "run": _slug(run_id, "run id"), "playbook": _slug(playbook, "playbook"),
        "language": _slug(language, "language"),
        "outcome": _slug((outcome or {}).get("outcome", "unknown"), "outcome"),
        "failed_stage": _slug(outcome["failed_stage"], "stage") if (outcome or {}).get("failed_stage") else None,
        "stages": len(results),
        "attempts": int(sum(m.get("attempts", 0) for m in ms)),
        "tokens_in": int(sum(m.get("input_tokens", 0) for m in ms)),
        "tokens_out": int(sum(m.get("output_tokens", 0) for m in ms)),
        "cost_usd": cost,
        "latency_s": round(sum(m.get("latency_s", 0) for m in ms), 3),
        "jev_ms": round(sum(m.get("jev_ms", 0) for m in ms), 3),
        "jev_calls": int(sum(m.get("jev_calls", 0) for m in ms)),
        "duration_ms": _num(duration_ms, "duration"),
    }


# ---------- writing ----------

def _write(line, root=None):
    """Append one line. Raises LedgerError if anything in it is not a number, a slug, a bool or null."""
    _check_clean(line)
    d = ledger_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    with _LOCK, open(d / FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False, sort_keys=True) + "\n")


def _check_clean(o, key=""):
    if isinstance(o, dict):
        for k, v in o.items():
            if not isinstance(k, str) or not re.fullmatch(r"[a-z0-9_.*\-@]{1,48}", k):
                raise LedgerError("a key is not a short slug")
            _check_clean(v, k)
    elif isinstance(o, list):
        for v in o:
            _check_clean(v, key)
    elif isinstance(o, str):
        if key == "ts":
            if not re.fullmatch(r"\d{4}-\d\d-\d\dT[\d:.]+\+00:00", o):
                raise LedgerError("bad timestamp")
        elif not re.fullmatch(r"[a-z0-9_.\-@]{1,48}", o):
            raise LedgerError(f"value for {key!r} is not a short slug")
    elif o is not None and not isinstance(o, (bool, int, float)):
        raise LedgerError("unsupported value")


class Recorder:
    """One per run. The app creates it at the start and calls stage_done after each stage, then finish."""

    def __init__(self, playbook, language, root=None, run_id=None):
        self.playbook, self.language, self.root = playbook, language, root
        self.run_id = run_id or new_run_id()
        self.t0 = time.monotonic()
        self.results = []

    def stage_done(self, rec, audit_events, duration_ms=None):
        self.results.append(rec)
        try:
            _write(stage_line(self.run_id, self.playbook, self.language, rec, audit_events, duration_ms), self.root)
            return True
        except Exception:
            return False

    def finish(self, outcome):
        try:
            _write(run_line(self.run_id, self.playbook, self.language, outcome, self.results,
                            round((time.monotonic() - self.t0) * 1000)), self.root)
            return True
        except Exception:
            return False


def record_run(playbook, language, state, results, audit_events, root=None, run_id=None):
    """All at once, after a run: one line per stage and one for the run. Returns the run id, or None if a write failed."""
    rec = Recorder(playbook, language, root, run_id)
    ok = all([rec.stage_done(r, audit_events) for r in results if r.status != "skipped"] or [True])
    ok = rec.finish(state.outcome) and ok
    return rec.run_id if ok else None


# ---------- reading ----------

def _read(root=None, since=None):
    f = ledger_dir(root) / FILE
    if not f.is_file():
        return []
    cut = _since(since)
    out = []
    for ln in f.read_text(encoding="utf-8").splitlines():
        try:
            x = json.loads(ln)
        except ValueError:
            continue
        if cut is None or x.get("ts", "") >= cut:
            out.append(x)
    return out


def _since(since):
    if since is None:
        return None
    if isinstance(since, (int, float)):
        return (datetime.now(timezone.utc) - timedelta(seconds=since)).isoformat(timespec="milliseconds")
    if isinstance(since, timedelta):
        return (datetime.now(timezone.utc) - since).isoformat(timespec="milliseconds")
    if isinstance(since, datetime):
        return since.astimezone(timezone.utc).isoformat(timespec="milliseconds")
    return str(since)


def _pct(vals, p):
    if not vals:
        return None
    s = sorted(vals)
    k = max(0, min(len(s) - 1, math.ceil(p / 100 * len(s)) - 1))
    return round(s[k], 3)


def summarize(since=None, root=None):
    """Totals for the ops page. `since`: seconds back, a timedelta, a datetime or an ISO string."""
    rows = _read(root, since)
    runs = [r for r in rows if r["type"] == "run"]
    stages = [r for r in rows if r["type"] == "stage"]
    packages = [r for r in runs if r["outcome"] == "package_complete"]
    costs = [r["cost_usd"] for r in packages if r.get("cost_usd") is not None]
    lat = {}
    for s in stages:
        lat.setdefault(s["stage"], []).append((s.get("latency_s") or 0) + (s.get("jev_ms") or 0) / 1000)
    att = {}
    for s in stages:
        att[str(s["attempts"])] = att.get(str(s["attempts"]), 0) + 1
    cats = {}
    for s in stages:
        for c in s["rule_categories"]:
            cats[c] = cats.get(c, 0) + 1
    jev = {}
    for s in stages:
        for q, d in s["jev"].items():
            j = jev.setdefault(q, {"pass": 0, "uncertain": 0, "reject": 0, "unavailable": 0, "skipped": 0, "max_probability": 0.0})
            for dec, n in d["decisions"].items():
                j[dec] = j.get(dec, 0) + n
            j["max_probability"] = max(j["max_probability"], d.get("max_probability") or 0)
    prov = {}
    for s in stages:
        if s.get("scripture_provider"):
            prov[s["scripture_provider"]] = prov.get(s["scripture_provider"], 0) + 1
    outcomes = {}
    for r in runs:
        outcomes[r["outcome"]] = outcomes.get(r["outcome"], 0) + 1
    n = len(stages)
    return {
        "since": _since(since), "runs": len(runs), "stages": n, "packages": len(packages), "outcomes": outcomes,
        "cost_per_package_usd": round(sum(costs) / len(costs), 4) if costs else None,
        "cost_total_usd": round(sum(r["cost_usd"] for r in runs if r.get("cost_usd") is not None), 4),
        "latency_s_by_stage": {k: {"p50": _pct(v, 50), "p95": _pct(v, 95), "n": len(v)} for k, v in sorted(lat.items())},
        "attempts_distribution": att,
        "escalation_rate_stages": round(sum(1 for s in stages if s["escalated"]) / n, 4) if n else None,
        "escalation_rate_runs": round(sum(1 for r in runs if r["outcome"] == "escalated") / len(runs), 4) if runs else None,
        "rejection_rate_by_category": {k: round(v / n, 4) for k, v in sorted(cats.items())} if n else {},
        "rejections_by_category": dict(sorted(cats.items())),
        "jev_by_question": dict(sorted(jev.items())),
        "scripture_provider_mix": prov,
    }


_OUTCOME = {"package_complete": "complete", "escalated": "escalated", "stopped_by_pastor": "stopped", "blocked": "error"}


def ops_view(since=None, root=None, limit=50):
    """The shape the ops page renders (agreed with the app): numbers and short enums only."""
    rows = _read(root, since)
    runs = [r for r in rows if r["type"] == "run"]
    stages = [r for r in rows if r["type"] == "stage"]
    pk = sorted((r for r in runs if r["outcome"] == "package_complete"), key=lambda r: r["ts"])
    costs = [r["cost_usd"] for r in pk if r.get("cost_usd") is not None]
    lats = [(r.get("latency_s") or 0) + (r.get("jev_ms") or 0) / 1000 for r in pk]
    written = sum(s["attempts"] for s in stages)
    accepted = sum(1 for s in stages if s["status"] in ("approved", "edited", "stopped"))
    rejected = max(0, written - accepted)
    lat = {}
    for s in stages:
        lat.setdefault(s["stage"], []).append((s.get("latency_s") or 0) + (s.get("jev_ms") or 0) / 1000)
    cats = {}
    for s in stages:
        for c, n in s["rule_categories"].items():
            cats[c] = cats.get(c, 0) + n
    jev = {}
    for s in stages:
        for q, d in s["jev"].items():
            j = jev.setdefault(q, {"pass": 0, "uncertain": 0, "reject": 0, "unavailable": 0, "probs": []})
            for dec, n in d["decisions"].items():
                if dec in j:
                    j[dec] += n
            j["probs"].extend(d.get("probs") or [])
    mix = {"youversion": 0, "bank": 0, "none": 0}
    for s in stages:
        if s["stage"] == "pastoral" and s["status"] in ("approved", "edited", "stopped"):
            mix[s["scripture_provider"] if s.get("scripture_provider") in mix else "none"] += 1
    return {
        "source": "ledger", "generated": _now(),
        "headline": {
            "packages": len(pk),
            "cost_avg": round(sum(costs) / len(costs), 4) if costs else None,
            "cost_p95": _pct(costs, 95),
            "latency_p50_s": _pct(lats, 50), "latency_p95_s": _pct(lats, 95),
            "escalation_rate": round(sum(1 for r in runs if r["outcome"] == "escalated") / len(runs), 4) if runs else None,
            "rejection_rate": round(rejected / written, 4) if written else None,
        },
        "latency_by_stage": [{"stage": k, "p50": _pct(v, 50), "p95": _pct(v, 95), "n": len(v)} for k, v in sorted(lat.items())],
        "cost_series": [{"t": r["ts"], "cost": r["cost_usd"]} for r in pk if r.get("cost_usd") is not None],
        "rejections_by_category": dict(sorted(cats.items())),
        "jev_by_question": dict(sorted(jev.items())),
        "provider_mix": mix,
        "runs": [{"t": r["ts"], "crisis": r["playbook"], "stages": r["stages"], "attempts": r["attempts"], "cost": r.get("cost_usd"),
                  "latency_s": round((r.get("latency_s") or 0) + (r.get("jev_ms") or 0) / 1000, 3),
                  "outcome": _OUTCOME.get(r["outcome"], "error")}
                 for r in sorted(runs, key=lambda r: r["ts"], reverse=True)[:limit]],
    }
