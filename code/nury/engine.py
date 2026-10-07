"""Nury engine: run_stage, correction loop, approval gates, chaining.

There is no send path here. Output goes to the pastor's gate and nowhere else.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional

from . import guardrails as g
from .audit import AuditLog
from .gloo_client import GlooClient, GuardrailBlock
from .stages import REGISTRY, SOURCE_FILES, STAGES, load_source

MAX_TRIES = 3
STOP_MESSAGE = "I'll handle this manually."


@dataclass
class CaseState:
    """Everything that flows between stages."""
    intake: str
    language: str = "es"                          # family language
    approved: dict = field(default_factory=dict)  # stage_id -> approved OR edited text
    results: dict = field(default_factory=dict)   # stage_id -> StageResult

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
    final: Optional[str]        # text that later stages use (None if not approved/edited)
    disclaimer: str
    metrics: dict
    message: str = ""           # for stopped / escalated / error


def approve_all(result):
    return GateDecision("approve")


def _new_metrics():
    return {"attempts": 0, "retries": 0, "self_corrections": 0, "latency_s": 0.0,
            "input_tokens": 0, "output_tokens": 0}


def _correction_note(reasons):
    return ("\n\nYour previous draft was rejected by the safety check for these reasons:\n"
            + "\n".join(f"- {r}" for r in reasons)
            + "\nWrite a new draft that fixes every reason. Do not mention the rejection. Output only the draft.")


def run_stage(stage_id, state: CaseState, gate: Callable = approve_all, client: Optional[GlooClient] = None,
              audit: Optional[AuditLog] = None, provoke: Optional[dict] = None) -> StageResult:
    """Draft one stage, check it, correct it (max 3 tries), then ask the gate.

    gate(result) -> GateDecision. The gate only sees safe drafts.
    provoke: {stage_id: extra instruction} added on the FIRST try only.
             For demos and tests that must show a rejected-and-regenerated draft.
    """
    stage = REGISTRY[stage_id]
    client = client or GlooClient()
    audit = audit or AuditLog()
    data = {k: load_source(SOURCE_FILES[k]) for k in stage.sources}
    lang = "en" if stage.audience == "pastor" else state.language
    disclaimer = g.DISCLAIMER[lang]
    m = _new_metrics()
    base_ins, user_input = stage.build(state, data)
    audit.log("stage_start", stage=stage_id, deps_used=[d for d in stage.deps if d in state.approved])

    reasons, draft = [], None
    for attempt in range(1, MAX_TRIES + 1):
        ins = base_ins
        if attempt == 1 and provoke and stage_id in provoke:
            ins += "\n\n" + provoke[stage_id]
        if reasons:
            ins += _correction_note(reasons)
        m["attempts"] = attempt
        audit.log("gloo_call", stage=stage_id, attempt=attempt)
        try:
            text, meta = client.ask(user_input, instructions=ins)
        except GuardrailBlock as e:
            audit.log("gloo_block", stage=stage_id, attempt=attempt, detail=e.detail)
            reasons, text = ["Gloo guardrails blocked the request"], None
            m["self_corrections"] += 1
            continue
        except Exception as e:  # network or HTTP error: not a safety failure
            audit.log("error", stage=stage_id, attempt=attempt, error=type(e).__name__)
            return StageResult(stage_id, stage.title, "error", None, None, disclaimer, m,
                               f"Gloo call failed ({type(e).__name__}). {STOP_MESSAGE}")
        m["latency_s"] = round(m["latency_s"] + meta["latency_s"], 3)
        m["input_tokens"] += meta["input_tokens"]
        m["output_tokens"] += meta["output_tokens"]
        reasons = g.unsafe_reasons(text) + stage.checks(text, state, data)
        audit.log("check", stage=stage_id, attempt=attempt, passed=not reasons, reasons=reasons,
                  tokens_in=meta["input_tokens"], tokens_out=meta["output_tokens"],
                  latency_s=meta["latency_s"])
        if not reasons:
            draft = text
            break
        audit.log("draft_rejected", stage=stage_id, attempt=attempt, visible_to_pastor=False, draft=text)
        m["self_corrections"] += 1

    m["retries"] = m["attempts"] - 1
    if draft is None:
        audit.log("escalated", stage=stage_id, attempts=m["attempts"], reasons=reasons)
        return StageResult(stage_id, stage.title, "escalated", None, None, disclaimer, m,
                           f"Nury could not produce a safe draft after {MAX_TRIES} tries. {STOP_MESSAGE}")

    result = StageResult(stage_id, stage.title, "approved", draft, None, disclaimer, m)
    decision = gate(result)
    audit.log("gate", stage=stage_id, action=decision.action)
    if decision.action == "stop":
        result.status, result.message = "stopped", STOP_MESSAGE
    elif decision.action == "edit":
        if not decision.text or not decision.text.strip():
            raise ValueError("edit needs text")
        result.status, result.final = "edited", decision.text.strip()
        # The pastor owns edits. We flag, we do not block.
        warn = g.unsafe_reasons(result.final) + stage.checks(result.final, state, data)
        audit.log("edit_check", stage=stage_id, warnings=warn)
    elif decision.action == "approve":
        result.final = draft
    else:
        raise ValueError(f"unknown gate action {decision.action!r}")

    if result.final is not None:
        state.approved[stage_id] = result.final
    state.results[stage_id] = result
    return result


def run_pipeline(state: CaseState, gate: Callable = approve_all, client: Optional[GlooClient] = None,
                 audit: Optional[AuditLog] = None, provoke: Optional[dict] = None, stages=None):
    """Run stages in order. Stop at the first stop, escalation, or error."""
    client = client or GlooClient()
    audit = audit or AuditLog()
    out = []
    for s in (stages or [s.id for s in STAGES]):
        r = run_stage(s, state, gate, client, audit, provoke)
        out.append(r)
        if r.status not in ("approved", "edited"):
            break
    return out


# For demos and tests only: make the FIRST try violate a check so the loop shows
# a rejected-and-regenerated draft. Pass as run_stage(..., provoke=DEMO_PROVOKE).
DEMO_PROVOKE = {
    "pastoral": "For this first draft only, write about 200 words and tell the family their case will be won.",
}
