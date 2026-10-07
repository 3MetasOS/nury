"""Adapter: drives the real Nury core with run_scripted and returns a trajectory.

Needs GLOO_API_KEY in the environment or repo-root .env. Never prints or stores it.
Cost shows only if NURY_PRICE_IN / NURY_PRICE_OUT (USD per 1M tokens) are set; else None.
"""
import json
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



class _Capture:
    """Sits BELOW the privacy layer. Records the exact strings that would be sent to the model, so a run can be
    checked for protected names at the boundary. Only counts leave this class; the strings stay in memory."""

    def __init__(self, inner):
        self.inner, self.bodies, self.parts = inner, [], []

    def ask(self, user_input, instructions=None, **kw):
        self.bodies.append(f"{user_input or ''}\n{instructions or ''}")
        self.parts.append((user_input or "", instructions or ""))
        return self.inner.ask(user_input, instructions=instructions, **kw)

    def respond(self, user_input, instructions=None, **kw):
        self.bodies.append(f"{user_input or ''}\n{instructions or ''}")
        self.parts.append((user_input or "", instructions or ""))
        return self.inner.respond(user_input, instructions=instructions, **kw)

    def __getattr__(self, name):
        return getattr(self.inner, name)


def _static_text(pbid):
    from nury import guardrails
    pb = get_playbook(pbid)
    parts = [guardrails.boundary(pb.boundary), json.dumps(pb.disclaimer, ensure_ascii=False)] + [s.prompt for s in pb.stages]
    parts += [json.dumps(v, ensure_ascii=False) for v in pb.sources.values()]
    return "\n".join(parts)


def _own(text):
    """Nury's own sentences. The verse block is the vetted source, not Nury's words, so judges read the text without it."""
    try:
        from nury import scripture
        return scripture.strip_block(text) if text else text
    except Exception:
        return text


def _contains(text, term):
    import re
    t = term.strip()
    if not t:
        return False
    pat = rf"(?<!\w){re.escape(t)}(?!\w)" if t[0].isalnum() and t[-1].isalnum() else re.escape(t)
    return re.search(pat, text, re.I) is not None


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
    from nury.gloo_client import GlooClient
    cap = _Capture(GlooClient())
    client = make_client(inner=cap, intake=sc["intake"])
    try:   # keep every vetted phone, link and email of the run intact (the family's own numbers are still tokenized)
        if hasattr(client, "allow_playbook"):
            client.allow_playbook(get_playbook(pbid))
    except Exception:
        pass
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
            "own_text": _own(r.shown_text),   # Nury's own words: the verse block removed (it is Scripture, judged separately)
            "jev_calls": m.get("jev_calls", 0), "jev_ms": m.get("jev_ms", 0),
            "jev_gate": [{k: e.get(k) for k in ("attempt", "question", "probability", "decision")} for e in audit.events
                         if e.get("kind") == "jev_gate" and e.get("stage") == r.stage_id],
        })
        if r.status == "error":
            raise RuntimeError(r.message or "stage error")
        if r.status in ("stopped", "escalated"):
            halted, halt_stage, escalated = True, n, r.status == "escalated"
            break
    # Boundary check: no protected value (names the pastor confirmed or added, phones, emails...) in any string sent to the model.
    pmap = client.map() if hasattr(client, "map") else {}
    values = [v for v in pmap.values() if isinstance(v, str) and v.strip()]
    # The family's content travels in the user input: every protected value must be absent there. The instructions are the
    # playbook's own prompts: a value that already occurs in that static text (a junk "name" such as "Write" that the
    # privacy layer proposed from a sentence-initial word) cannot identify anyone, so it is not counted there.
    static = _static_text(pbid)
    leaks = sum(1 for u, ins in cap.parts for v in values if _contains(u, v) or (_contains(ins, v) and not _contains(static, v)))
    expect = (sc.get("flags") or {}).get("expect_protected", [])
    protected_present = {t: any(_contains(v, t) for v in values) for t in expect}
    pkg = None if halted else {str(s["n"]): s["final_text"] for s in stages}
    return {"scenario_id": sc["id"], "stages": stages, "halted": halted, "halt_stage": halt_stage,
            "escalated": escalated, "audit_log": audit.events, "package": pkg,
            "ui_strings": ["Approve", "Edit", "Stop"], "n_stages": len(ids), "playbook": pbid, "privacy": PRIVACY,
            "scripture": [{k: e.get(k) for k in ("stage", "verse", "provider")} for e in audit.events if e.get("kind") == "scripture"],
            "scripture_fallbacks": [{k: e.get(k) for k in ("stage", "verse", "provider", "reasons")} for e in audit.events if e.get("kind") == "scripture_fallback"],
            "privacy_checked_values": len(values), "privacy_bodies": len(cap.bodies), "privacy_leaks": leaks, "protected_present": protected_present, "latency_s": round(time.time() - t0, 2)}
