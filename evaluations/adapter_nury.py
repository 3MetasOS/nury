"""Adapter: drives the real Nury core with run_scripted and returns a trajectory.

Needs GLOO_API_KEY in the environment or repo-root .env. Never prints or stores it.
Cost shows only if NURY_PRICE_IN / NURY_PRICE_OUT (USD per 1M tokens) are set; else None.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from nury.engine import run_scripted  # noqa: E402

STAGE_IDS = ["triage", "rights", "attorney", "checklist", "pastoral"]


def _viol(v):
    return [x if isinstance(x, str) else f"{x.get('category')}: {x.get('reason')}" for x in (v or [])]


def _decisions(actions):
    out = {}
    for k, act in actions.items():
        sid = STAGE_IDS[int(k) - 1]
        if isinstance(act, dict) and "edit" in act:
            out[sid] = ("edit", act["edit"])
        elif act in ("reject", "stop"):
            out[sid] = "stop"  # the core has one halt action
        else:
            out[sid] = "approve"
    return out


def run(sc):
    t0 = time.time()
    fi = sc.get("fault_injection")
    if fi:
        fi = dict(fi, stage=STAGE_IDS[fi["stage"] - 1])
    kw = {"playbook": sc["playbook"]} if sc.get("playbook") else {}
    state, results, audit = run_scripted(sc["intake"], sc["output_language"], _decisions(sc["pastor_actions"]),
                                         fault_injection=fi, **kw)
    stages, halted, halt_stage, escalated = [], False, None, False
    for r in results:
        n = STAGE_IDS.index(r.stage_id) + 1 if r.stage_id in STAGE_IDS else len(stages) + 1
        m = r.metrics
        ctx = r.input_context
        stages.append({
            "n": n, "name": r.stage_id, "status": r.status,
            "attempts": [{"text": a.get("text"), "violations": _viol(a.get("violations"))} for a in r.attempts],
            "retries": m.get("retries", 0), "escalated": r.escalated,
            "input_context": "\n".join(ctx.values()) if isinstance(ctx, dict) else (ctx or ""),
            "source_lookups": [e["kind"] for e in audit.events if e.get("stage") == r.stage_id and e["kind"] == "source"],
            "shown_text": r.shown_text, "final_text": r.final, "gate": r.gate,
            "latency_s": m.get("latency_s", 0), "tokens_in": m.get("input_tokens", 0),
            "tokens_out": m.get("output_tokens", 0), "cost_usd": m.get("cost_usd"),
        })
        if r.status == "error":
            raise RuntimeError(r.message or "stage error")
        if r.status in ("stopped", "escalated"):
            halted, halt_stage, escalated = True, n, r.status == "escalated"
            break
    pkg = None if halted else {str(s["n"]): s["final_text"] for s in stages}
    return {"scenario_id": sc["id"], "stages": stages, "halted": halted, "halt_stage": halt_stage,
            "escalated": escalated, "audit_log": audit.events, "package": pkg,
            "ui_strings": ["Approve", "Edit", "Stop"], "latency_s": round(time.time() - t0, 2)}
