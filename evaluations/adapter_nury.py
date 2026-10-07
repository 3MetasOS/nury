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

from nury.audit import AuditLog  # noqa: E402
from nury.engine import CaseState, get_playbook, run_pipeline, scripted_gate  # noqa: E402  (after price defaults)
from nury.privacy import make_client, privacy_enabled  # noqa: E402

PRIVACY = privacy_enabled()   # on by default; NURY_PRIVACY=off for an A/B. The scorecard records it.



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
    saved_env = {k: os.environ.get(k) for k in (sc.get("env") or {})}
    os.environ.update({k: str(v) for k, v in (sc.get("env") or {}).items()})   # e.g. NURY_DEMO_NETWORK=1 for network scenarios
    try:
        return _run(sc, t0, pbid, ids, fi, kw)
    finally:
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def _run(sc, t0, pbid, ids, fi, kw):
    # Same path as run_scripted, plus the privacy client (protects every suggested person in the intake)
    # and the gate wrapper that protects a name the pastor adds in an edit.
    state, audit = CaseState(sc["intake"], sc["output_language"]), AuditLog()
    client = make_client(intake=sc["intake"])
    try:   # keep the church contacts' phones and links readable in the model context, as INTERFACE.md says
        from nury import network as net
        if hasattr(client, "allow_network"):
            client.allow_network(net.load_network(root=str(Path(__file__).resolve().parents[1] / "code" / "network")).list())
    except Exception:
        pass
    gate = scripted_gate(_decisions(sc["pastor_actions"], ids))
    if hasattr(client, "wrap_gate"):
        gate = client.wrap_gate(gate)
    results = run_pipeline(pbid, state, gate, client, audit, fault_injection=fi)
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
            "ui_strings": ["Approve", "Edit", "Stop"], "n_stages": len(ids), "playbook": pbid, "privacy": PRIVACY, "latency_s": round(time.time() - t0, 2)}
