"""Observability extras for the /observability page: the evaluation summary, a guarded smoke run, and a stub for /api/ops when the ledger is empty.
Numbers and short labels only: never draft text, never a name.
/api/ops itself is hack-jedi's ops_api + nury.ledger. When the ledger holds no packages yet, the page shows a summary built from the stored
evaluation runs and says so in its 'source' line, so a stub is never mistaken for use.
The smoke evaluation is off unless NURY_ALLOW_EVAL_RUN=1, runs one at a time in a background thread, and never beside another live job."""
import json
import os
import re
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from nury import log

ROOT = Path(__file__).resolve().parents[2]
EVAL = ROOT / "evaluations"
SMOKE_IDS = "01,09,12"          # detention: happy path, Spanish output, pastoral-office probe
SMOKE_N = 3
LOCK = threading.Lock()
STATE = {"running": False, "started": None, "progress": "", "result": None, "error": None}


def _pct(vals, q):
    v = sorted(x for x in vals if x is not None)
    if not v:
        return None
    k = (len(v) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(v) - 1)
    return round(v[lo] + (v[hi] - v[lo]) * (k - lo), 4)


def _iso(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(timespec="seconds")


def _stub():
    """Summary from stored evaluation runs. Real runs, real numbers, but test runs, not use by a pastor."""
    runs = []
    for f in (EVAL / "results" / "runs.json", EVAL / "results" / "hospital" / "runs.json"):
        if f.is_file():
            for r in json.loads(f.read_text(encoding="utf-8")).get("runs", []):
                runs.append((f.stat().st_mtime, r))
    runs.sort(key=lambda x: x[0])
    rows, stage_lat, rej, jev, prov = [], {}, {}, {}, {}
    drafts = rejected = escalated = 0
    for i, (mt, r) in enumerate(runs):
        tj = r.get("trajectory") or {}
        sts = tj.get("stages", [])
        cost = sum((s.get("cost_usd") or 0) for s in sts)
        esc = bool(tj.get("escalated"))
        outcome = "escalated" if esc else ("stopped" if tj.get("halted") else ("error" if r.get("error") else "complete"))
        rows.append({"t": _iso(mt + i), "crisis": tj.get("playbook", "detention"), "stages": len(sts), "attempts": sum(len(s.get("attempts", [])) for s in sts),
                     "cost": round(cost, 5), "latency_s": round(tj.get("latency_s") or 0, 1), "outcome": outcome})
        escalated += esc
        for s in sts:
            stage_lat.setdefault(s["name"], []).append(s.get("latency_s") or 0)
            for a in s.get("attempts", []):
                drafts += 1
                cats = {str(v).split(":")[0] for v in a.get("violations", [])}
                rejected += bool(cats)
                for c in cats:
                    rej[c] = rej.get(c, 0) + 1
            for g in s.get("jev_gate", []):
                q = g.get("question")
                if not q or q == "*":
                    continue
                e = jev.setdefault(q, {"pass": 0, "uncertain": 0, "reject": 0, "unavailable": 0, "probs": []})
                e[g.get("decision") if g.get("decision") in e else "unavailable"] += 1
                if isinstance(g.get("probability"), (int, float)):
                    e["probs"].append(round(g["probability"], 3))
        for e in tj.get("scripture", []):
            p = "bank" if e.get("provider") in ("bank", "none") else e.get("provider")
            prov[p] = prov.get(p, 0) + 1
    n = len(rows)
    costs, lats = [r["cost"] for r in rows], [r["latency_s"] for r in rows]
    return {"source": "evaluation runs (stub: no real use is in the ledger yet)", "generated": _iso(time.time()),
            "headline": {"packages": n, "cost_avg": round(sum(costs) / n, 5) if n else None, "cost_p95": _pct(costs, .95),
                         "latency_p50_s": _pct(lats, .5), "latency_p95_s": _pct(lats, .95),
                         "escalation_rate": round(escalated / n, 4) if n else None, "rejection_rate": round(rejected / drafts, 4) if drafts else None},
            "latency_by_stage": [{"stage": k, "p50": _pct(v, .5), "p95": _pct(v, .95), "n": len(v)} for k, v in stage_lat.items()],
            "cost_series": [{"t": r["t"], "cost": r["cost"]} for r in rows],
            "rejections_by_category": rej, "jev_by_question": jev, "provider_mix": prov, "runs": list(reversed(rows))[:50]}


def ops():
    """The ledger's view (hack-jedi). If it holds no packages yet, the labelled stub."""
    try:
        from app import ops_api
        status, _ctype, body = ops_api.handle("GET", "/api/ops")
        d = json.loads(body)
        if status == 200 and (d.get("headline") or {}).get("packages"):
            return d
    except Exception as e:
        log.note("evals_api.ops_view", e)
    return _stub()


_NUM = re.compile(r"Scenarios run: (\d+)\. Passed by the judges: (\d+)\. Passed after human review: (\d+)\. Failed: (\d+) .*?Sent to human review and still waiting: (\d+)")
_COST = re.compile(r"Cost: \$([\d.]+) total, \$([\d.]+) per run")
_CORE = re.compile(r"last commit `([0-9a-f]{7,})")


def _score(path, label):
    if not path.is_file():
        return None
    t = path.read_text(encoding="utf-8")
    m, c, k = _NUM.search(t), _COST.search(t), _CORE.search(t)
    if not m:
        return None
    return {"set": label, "scenarios": int(m[1]), "judge_pass": int(m[2]), "human_pass": int(m[3]), "failed": int(m[4]), "awaiting_review": int(m[5]),
            "cost_total": float(c[1]) if c else None, "cost_per_run": float(c[2]) if c else None, "core_commit": k[1] if k else None,
            "updated": _iso(path.stat().st_mtime)}


def evals():
    sets = [x for x in (_score(EVAL / "results" / "scorecard.md", "Detention (20 scenarios)"),
                        _score(EVAL / "results" / "hospital" / "scorecard.md", "Hospital (8 scenarios)"),
                        _score(EVAL / "results" / "attacker" / "scorecard.md", "Attacker intakes")) if x]
    est = round(SMOKE_N * 0.075, 2)
    return {"sets": sets, "smoke": {"enabled": os.environ.get("NURY_ALLOW_EVAL_RUN") == "1", "scenarios": SMOKE_N, "estimate_usd": est,
                                    "note": f"{SMOKE_N} detention scenarios with privacy, the Jev gate and the Jev judges on. About ${est} of Gloo credit; Jev is billed on its own key."},
            "state": {k: STATE[k] for k in ("running", "started", "progress", "result", "error")}}


def _other_live_job():
    try:
        out = subprocess.run(["pgrep", "-f", r"run\.py --agent"], capture_output=True, text=True).stdout.split()
        return any(int(p) != os.getpid() for p in out)
    except Exception:
        return False


def _worker():
    out = EVAL / "results" / "smoke"
    try:
        STATE["progress"] = "Running 3 scenarios. This takes a few minutes."
        p = subprocess.run([sys.executable, "run.py", "--agent", "nury", "--jev", "--only", SMOKE_IDS, "--out", str(out)], cwd=str(EVAL),
                           capture_output=True, text=True, timeout=1500)
        if p.returncode != 0:
            STATE["error"] = f"The run stopped with exit code {p.returncode}."
        else:
            STATE["result"] = _score(out / "scorecard.md", "Smoke evaluation (3 scenarios)")
    except Exception as e:
        STATE["error"] = type(e).__name__
    finally:
        STATE["running"] = False
        STATE["progress"] = "" if STATE["error"] else "Done."


def start_smoke(body):
    """Returns (status, payload). Needs the server flag and an explicit confirmation of the shown estimate."""
    if os.environ.get("NURY_ALLOW_EVAL_RUN") != "1":
        return 403, {"error": "Evaluation runs are switched off on this server."}
    est = evals()["smoke"]["estimate_usd"]
    if body.get("confirm") is not True or body.get("estimate_usd") != est:
        return 400, {"error": "Confirm the cost estimate first.", "estimate_usd": est}
    with LOCK:
        if STATE["running"]:
            return 409, {"error": "A smoke evaluation is already running."}
        if _other_live_job():
            return 409, {"error": "Another live job is running. Try again when it ends."}
        STATE.update({"running": True, "started": _iso(time.time()), "progress": "Starting.", "result": None, "error": None})
        threading.Thread(target=_worker, daemon=True).start()
    return 202, {"started": True}
