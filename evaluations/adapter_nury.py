"""Adapter: drives the real Nury core (code/nury) for one scenario and returns a trajectory.

Needs GLOO_API_KEY in the environment or repo-root .env. Never prints or stores it.
Cost: set NURY_PRICE_IN and NURY_PRICE_OUT (USD per 1M tokens) to report cost; otherwise cost is None.
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from nury.audit import AuditLog  # noqa: E402
from nury.engine import CaseState, GateDecision, run_stage  # noqa: E402
from nury.gloo_client import GlooClient  # noqa: E402
from nury.stages import REGISTRY, STAGES  # noqa: E402

STAGE_IDS = [s.id for s in STAGES]
PRICE_IN = os.environ.get("NURY_PRICE_IN")
PRICE_OUT = os.environ.get("NURY_PRICE_OUT")


class FaultClient:
    """Wraps GlooClient. Appends draft_suffix to the first `times` replies of one stage.
    The core sees an ordinary unsafe draft. Test hook only; the product never uses it."""

    def __init__(self, inner, fi):
        self.inner, self.fi, self.stage, self.n = inner, fi, None, 0

    def ask(self, user_input, instructions=None, **kw):
        text, meta = self.inner.ask(user_input, instructions=instructions, **kw)
        fi = self.fi
        if fi and self.stage == STAGE_IDS[fi["stage"] - 1]:
            self.n += 1
            if self.n <= fi["times"]:
                text += fi["draft_suffix"]
        return text, meta

    def __getattr__(self, k):
        return getattr(self.inner, k)


def _cost(tin, tout):
    if PRICE_IN is None or PRICE_OUT is None:
        return None
    return round(tin * float(PRICE_IN) / 1e6 + tout * float(PRICE_OUT) / 1e6, 6)


def run(sc):
    t0 = time.time()
    audit = AuditLog()
    state = CaseState(sc["intake"], sc["output_language"])
    client = FaultClient(GlooClient(), sc.get("fault_injection"))
    actions = sc["pastor_actions"]
    stages, halted, halt_stage, escalated, err = [], False, None, False, None
    for n, sid in enumerate(STAGE_IDS, 1):
        act = actions.get(n, actions.get(str(n), "approve"))

        def gate(_r, act=act):
            if isinstance(act, dict) and "edit" in act:
                return GateDecision("edit", act["edit"])
            if act in ("reject", "stop"):
                return GateDecision("stop")  # the core has one halt action
            return GateDecision("approve")

        client.stage, client.n = sid, 0
        ctx = "\n".join(state.approved[d] for d in REGISTRY[sid].deps if d in state.approved)
        r = run_stage(sid, state, gate, client, audit)
        ev = [e for e in audit.events if e.get("stage") == sid]
        rejected = {e["attempt"]: e["draft"] for e in ev if e["kind"] == "draft_rejected"}
        checks = {e["attempt"]: e for e in ev if e["kind"] == "check"}
        blocks = {e["attempt"] for e in ev if e["kind"] == "gloo_block"}
        attempts = []
        for i in range(1, r.metrics["attempts"] + 1):
            if i in blocks:
                attempts.append({"text": None, "violations": ["gloo guardrail block"]})
            elif i in rejected:
                attempts.append({"text": rejected[i], "violations": checks[i]["reasons"]})
            else:
                attempts.append({"text": r.draft, "violations": []})
        m = r.metrics
        shown = None
        if r.status in ("approved", "edited", "stopped") and r.draft is not None:
            shown = (r.final if r.status == "edited" else r.draft) + "\n\n" + r.disclaimer
        stages.append({
            "n": n, "name": sid, "attempts": attempts, "retries": m["retries"],
            "escalated": r.status == "escalated", "status": r.status, "input_context": ctx,
            "source_lookups": [k for k in REGISTRY[sid].sources],
            "shown_text": shown, "final_text": r.final,
            "gate": None if r.status in ("escalated", "error") else
                    {"action": {"approved": "approve", "edited": "edit", "stopped": "stop"}[r.status],
                     "edited_text": r.final if r.status == "edited" else None},
            "latency_s": m["latency_s"], "tokens_in": m["input_tokens"], "tokens_out": m["output_tokens"],
            "cost_usd": _cost(m["input_tokens"], m["output_tokens"]),
        })
        if r.status == "error":
            err = r.message
            break
        if r.status in ("stopped", "escalated"):
            halted, halt_stage, escalated = True, n, r.status == "escalated"
            break
    if err:
        raise RuntimeError(err)
    pkg = None if halted else {str(s["n"]): s["final_text"] for s in stages}
    return {"scenario_id": sc["id"], "stages": stages, "halted": halted, "halt_stage": halt_stage,
            "escalated": escalated, "audit_log": audit.events, "package": pkg,
            "ui_strings": ["Approve", "Edit", "Stop"], "latency_s": round(time.time() - t0, 2)}
