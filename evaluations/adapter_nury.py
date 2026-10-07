"""Adapter: drives the real Nury core with run_scripted and returns a trajectory.

Needs GLOO_API_KEY in the environment or repo-root .env. Never prints or stores it.
Cost shows only if NURY_PRICE_IN / NURY_PRICE_OUT (USD per 1M tokens) are set; else None.
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

# Confirmed by hack-sensei from Gloo GET /platform/v2/models: gloo-anthropic-claude-sonnet-4.6,
# input $3.00 and output $15.00 per 1M tokens. Cache pricing not used.
MODEL = os.environ.get("GLOO_MODEL", "gloo-anthropic-claude-sonnet-4.6")
if MODEL == "gloo-anthropic-claude-sonnet-4.6":
    os.environ.setdefault("NURY_PRICE_IN", "3.00")
    os.environ.setdefault("NURY_PRICE_OUT", "15.00")
PRICES = {"model": MODEL, "usd_per_1m_in": os.environ.get("NURY_PRICE_IN"), "usd_per_1m_out": os.environ.get("NURY_PRICE_OUT")}

from nury.engine import get_playbook, run_scripted  # noqa: E402  (after price defaults)



def _viol(v):
    return [x if isinstance(x, str) else f"{x.get('category')}: {x.get('reason')}" for x in (v or [])]


def _decisions(actions, ids):
    out = {}
    for k, act in actions.items():
        sid = ids[int(k) - 1]
        if isinstance(act, dict) and "edit" in act:
            out[sid] = ("edit", act["edit"])
        elif act in ("reject", "stop"):
            out[sid] = "stop"  # the core has one halt action
        else:
            out[sid] = "approve"
    return out


def run(sc):
    t0 = time.time()
    pbid = sc.get("playbook", "detention")
    ids = [st.id for st in get_playbook(pbid).stages]
    fi = sc.get("fault_injection")
    if fi:
        fi = dict(fi, stage=ids[fi["stage"] - 1])
    kw = {"playbook": pbid}
    state, results, audit = run_scripted(sc["intake"], sc["output_language"], _decisions(sc["pastor_actions"], ids),
                                         fault_injection=fi, **kw)
    stages, halted, halt_stage, escalated = [], False, None, False
    for r in results:
        n = ids.index(r.stage_id) + 1 if r.stage_id in ids else len(stages) + 1
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
            "ui_strings": ["Approve", "Edit", "Stop"], "n_stages": len(ids), "playbook": pbid, "latency_s": round(time.time() - t0, 2)}
