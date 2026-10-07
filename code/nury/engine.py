"""Nury engine: run_stage, correction loop, approval gates, chaining.

There is no send path here. Output goes to the pastor's gate and nowhere else.
"""

import os
from dataclasses import dataclass, field, replace
from typing import Callable, Optional

from . import guardrails as g
from .audit import AuditLog
from .gloo_client import GlooClient, GuardrailBlock
from .stages import REGISTRY, SOURCE_FILES, STAGES, load_source

MAX_ATTEMPTS = 3          # 3 attempts total: first draft + 2 regenerations, then escalate
MAX_TRIES = MAX_ATTEMPTS  # old name
STOP_MESSAGE = "I'll handle this manually."

# Forced unsafe text for fault injection. It trips the banned_phrase check.
UNSAFE_SUFFIX = " Your case will be won, and we guarantee you will not be deported."


@dataclass
class CaseState:
    """Everything that flows between stages."""
    intake: str
    language: str = "es"                          # family language
    approved: dict = field(default_factory=dict)  # stage_id -> approved OR edited text (with disclaimer)
    results: dict = field(default_factory=dict)   # stage_id -> StageResult (full, eval only)

    def set_manual(self, stage_id, text):
        """Pastor wrote this stage by hand (e.g. after an escalation)."""
        self.approved[stage_id] = text


@dataclass
class GateDecision:
    action: str                 # "approve" | "edit" | "stop"
    text: Optional[str] = None  # required when action == "edit"


@dataclass
class StageResult:
    stage_id: str
    title: str
    status: str                 # approved | edited | stopped | escalated | error
    draft: Optional[str]        # safe draft shown at the gate (None if escalated or error)
    final: Optional[str]        # draft or edit + disclaimer; what later stages use (None if not approved/edited)
    disclaimer: str
    metrics: dict
    message: str = ""           # for stopped / escalated / error
    # --- the fields below are for the eval harness. The gate never receives `attempts`. ---
    attempts: list = field(default_factory=list)   # [{n, text, violations:[{category, reason}]}]
    reason_categories: list = field(default_factory=list)  # categories of rejected attempts
    escalated: bool = False
    shown_text: Optional[str] = None      # what the pastor saw: draft + disclaimer (None if escalated)
    gate: Optional[dict] = None           # {action, edited_text}
    input_context: dict = field(default_factory=dict)  # approved text this stage consumed


def approve_all(result):
    return GateDecision("approve")


def with_disclaimer(text, disclaimer):
    t = text.strip()
    if disclaimer in t:
        t = t.replace(disclaimer, "").strip()
    return f"{t}\n\n{disclaimer}"


def _new_metrics():
    return {"attempts": 0, "retries": 0, "self_corrections": 0, "latency_s": 0.0,
            "input_tokens": 0, "output_tokens": 0, "cost_usd": None}


def _cost(m):
    """Cost only if you set NURY_PRICE_IN and NURY_PRICE_OUT (USD per 1M tokens)."""
    try:
        pi, po = float(os.environ["NURY_PRICE_IN"]), float(os.environ["NURY_PRICE_OUT"])
    except (KeyError, ValueError):
        return None
    return round((m["input_tokens"] * pi + m["output_tokens"] * po) / 1e6, 6)


def _correction_note(violations):
    return ("\n\nYour previous draft was rejected by the safety check for these reasons:\n"
            + "\n".join(f"- {v['reason']}" for v in violations)
            + "\nWrite a new draft that fixes every reason. Do not mention the rejection. Output only the draft.")


def _fault_for(stage_id, fault_injection):
    """Resolve the fault: explicit arg, else NURY_FORCE_REJECTION=1 (demo: stage 2, once)."""
    if fault_injection and fault_injection.get("stage") == stage_id:
        return fault_injection
    if os.environ.get("NURY_FORCE_REJECTION") == "1" and stage_id == "rights":
        return {"stage": "rights", "times": 1, "draft_suffix": UNSAFE_SUFFIX}
    return None


def run_stage(stage_id, state: CaseState, gate: Callable = approve_all, client: Optional[GlooClient] = None,
              audit: Optional[AuditLog] = None, provoke: Optional[dict] = None,
              fault_injection: Optional[dict] = None) -> StageResult:
    """Draft one stage, check it, correct it (max 3 attempts), then ask the gate.

    gate(result) -> GateDecision. The gate only sees safe drafts and no `attempts`.
    fault_injection: {"stage", "times", "draft_suffix"}. Appends draft_suffix to the first
        `times` drafts of that stage AFTER generation, so the checks see it. times=1 gives
        reject -> regenerate -> pass. times>=3 gives escalation. Also: env NURY_FORCE_REJECTION=1.
    provoke: {stage_id: extra instruction} added to the FIRST try's prompt (model-side, not deterministic).
    """
    stage = REGISTRY[stage_id]
    client = client or GlooClient()
    audit = audit or AuditLog()
    data = {k: load_source(SOURCE_FILES[k]) for k in stage.sources}
    lang = "en" if stage.audience == "pastor" else state.language
    disclaimer = g.DISCLAIMER[lang]
    fault = _fault_for(stage_id, fault_injection)
    m = _new_metrics()
    ctx = {d: state.approved[d] for d in stage.deps if d in state.approved}
    base_ins, user_input = stage.build(state, data)
    audit.log("stage_start", stage=stage_id, deps_used=list(ctx))

    rec = StageResult(stage_id, stage.title, "error", None, None, disclaimer, m, input_context=ctx)
    violations, draft = [], None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        ins = base_ins
        if attempt == 1 and provoke and stage_id in provoke:
            ins += "\n\n" + provoke[stage_id]
        if violations:
            ins += _correction_note(violations)
        m["attempts"] = attempt
        audit.log("gloo_call", stage=stage_id, attempt=attempt)
        try:
            text, meta = client.ask(user_input, instructions=ins)
        except GuardrailBlock as e:
            audit.log("gloo_block", stage=stage_id, attempt=attempt, detail=e.detail,
                      reason_category="gloo_block")
            violations = [g.R("gloo_block", "Gloo guardrails blocked the request")]
            rec.attempts.append({"n": attempt, "text": None, "violations": violations})
            rec.reason_categories.append("gloo_block")
            m["self_corrections"] += 1
            continue
        except Exception as e:  # network or HTTP error: not a safety failure
            audit.log("error", stage=stage_id, attempt=attempt, error=type(e).__name__)
            rec.message = f"Gloo call failed ({type(e).__name__}). {STOP_MESSAGE}"
            m["retries"] = attempt - 1
            m["cost_usd"] = _cost(m)
            state.results[stage_id] = rec
            return rec
        m["latency_s"] = round(m["latency_s"] + meta["latency_s"], 3)
        m["input_tokens"] += meta["input_tokens"]
        m["output_tokens"] += meta["output_tokens"]
        if fault and attempt <= fault.get("times", 1):
            text += fault.get("draft_suffix", UNSAFE_SUFFIX)
            audit.log("fault_injected", stage=stage_id, attempt=attempt)
        violations = g.unsafe_reasons(text) + stage.checks(text, state, data)
        cats = sorted({v["category"] for v in violations})
        audit.log("check", stage=stage_id, attempt=attempt, passed=not violations, violations=violations,
                  reason_categories=cats, tokens_in=meta["input_tokens"], tokens_out=meta["output_tokens"],
                  latency_s=meta["latency_s"])
        rec.attempts.append({"n": attempt, "text": text, "violations": violations})
        if not violations:
            draft = text
            break
        audit.log("draft_rejected", stage=stage_id, attempt=attempt, visible_to_pastor=False,
                  reason_categories=cats, draft=text)
        rec.reason_categories += cats
        m["self_corrections"] += 1

    m["retries"] = m["attempts"] - 1
    m["cost_usd"] = _cost(m)
    if draft is None:
        audit.log("escalated", stage=stage_id, attempts=m["attempts"], reason_categories=rec.reason_categories)
        rec.status, rec.escalated = "escalated", True
        rec.message = f"Nury could not produce a safe draft after {MAX_ATTEMPTS} attempts. {STOP_MESSAGE}"
        state.results[stage_id] = rec
        return rec

    rec.status, rec.draft = "approved", draft
    rec.shown_text = with_disclaimer(draft, disclaimer)
    decision = gate(replace(rec, attempts=[]))      # the gate never gets rejected attempts
    audit.log("gate", stage=stage_id, action=decision.action)
    rec.gate = {"action": decision.action, "edited_text": None}
    if decision.action == "stop":
        rec.status, rec.message = "stopped", STOP_MESSAGE
    elif decision.action == "edit":
        if not decision.text or not decision.text.strip():
            raise ValueError("edit needs text")
        rec.status = "edited"
        rec.gate["edited_text"] = decision.text.strip()
        rec.final = with_disclaimer(decision.text, disclaimer)   # disclaimer re-appended after edit
        # The pastor owns edits. We flag, we do not block.
        warn = g.unsafe_reasons(decision.text) + stage.checks(decision.text, state, data)
        audit.log("edit_check", stage=stage_id, warnings=warn)
    elif decision.action == "approve":
        rec.final = rec.shown_text
    else:
        raise ValueError(f"unknown gate action {decision.action!r}")

    if rec.final is not None:
        state.approved[stage_id] = rec.final
    state.results[stage_id] = rec
    return rec


def run_pipeline(state: CaseState, gate: Callable = approve_all, client: Optional[GlooClient] = None,
                 audit: Optional[AuditLog] = None, provoke: Optional[dict] = None, stages=None,
                 fault_injection: Optional[dict] = None):
    """Run stages in order. Stop at the first stop, escalation, or error."""
    client = client or GlooClient()
    audit = audit or AuditLog()
    out = []
    for s in (stages or [s.id for s in STAGES]):
        r = run_stage(s, state, gate, client, audit, provoke, fault_injection)
        out.append(r)
        if r.status not in ("approved", "edited"):
            break
    return out


def scripted_gate(decisions: dict):
    """Gate from a script: {stage_id: "approve" | "stop" | ("edit", text) | GateDecision}. Default approve."""
    def gate(result):
        d = decisions.get(result.stage_id, "approve")
        if isinstance(d, GateDecision):
            return d
        if isinstance(d, tuple):
            return GateDecision(d[0], d[1])
        return GateDecision(d)
    return gate


def run_scripted(intake, language="es", decisions=None, fault_injection=None, client=None,
                 audit: Optional[AuditLog] = None, stages=None):
    """Entrypoint for the eval harness. Returns (state, results, audit).

    results[i].attempts / .reason_categories / .shown_text / .gate / .input_context / .metrics
    hold the full per-stage trajectory.
    """
    state = CaseState(intake, language)
    audit = audit or AuditLog()
    results = run_pipeline(state, scripted_gate(decisions or {}), client, audit,
                           stages=stages, fault_injection=fault_injection)
    return state, results, audit


# Model-side provocation for demos (not deterministic). Prefer fault_injection or NURY_FORCE_REJECTION=1.
DEMO_PROVOKE = {
    "pastoral": "For this first draft only, write about 200 words and tell the family their case will be won.",
}
