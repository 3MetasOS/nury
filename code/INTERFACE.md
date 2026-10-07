# Nury core interface (hack-jedi)

Python 3.12. Needs `requests`. `GLOO_API_KEY` comes from the environment or the repo-root `.env`. `GLOO_MODEL` is optional (default `gloo-anthropic-claude-sonnet-4.6`). Run from `code/`.

```python
from nury.engine import (CaseState, GateDecision, StageResult, run_stage, run_pipeline,
                         approve_all, DEMO_PROVOKE, STOP_MESSAGE)
from nury.audit import AuditLog
from nury.stages import STAGES, REGISTRY      # ids: triage, rights, attorney, checklist, pastoral
from nury.gloo_client import GlooClient, GuardrailBlock
```

## Signatures

```python
CaseState(intake: str, language: str = "es")   # .approved {stage_id: approved-or-edited text}
                                               # .results  {stage_id: StageResult}
                                               # .set_manual(stage_id, text)  # pastor wrote it by hand

GateDecision(action: "approve" | "edit" | "stop", text: str | None)   # text required for "edit"

run_stage(stage_id, state, gate=approve_all, client=None, audit=None, provoke=None, fault_injection=None) -> StageResult
run_pipeline(state, gate=approve_all, client=None, audit=None, provoke=None, stages=None, fault_injection=None) -> list[StageResult]
run_scripted(intake, language="es", decisions=None, fault_injection=None, client=None, audit=None, stages=None) -> (state, results, audit)
                                  # decisions: {stage_id: "approve" | "stop" | ("edit", text)}; default approve
scripted_gate(decisions) -> gate
```

`gate(result: StageResult) -> GateDecision` runs after each stage. The gate only ever sees a safe draft.

```python
StageResult(stage_id, title,
  status,      # "approved" | "edited" | "stopped" | "escalated" | "error"
  draft,       # safe draft shown at the gate (None if escalated or error)
  final,       # text later stages use: the draft if approved, the pastor's text if edited
  disclaimer,  # show with every output (English for triage, family language otherwise)
  metrics,     # attempts, retries, self_corrections, latency_s, input_tokens, output_tokens, cost_usd
  message,     # "I'll handle this manually." for stopped / escalated / error
  # eval-only fields (the gate callback never receives `attempts`):
  attempts,           # [{n, text, violations: [{category, reason}]}]  (text None on a Gloo 403)
  reason_categories,  # categories of rejected attempts, e.g. ["banned_phrase"]
  escalated,          # bool
  shown_text,         # draft + disclaimer, what the pastor saw (None if escalated)
  gate,               # {action, edited_text}
  input_context)      # {dep_stage_id: approved/edited text this stage consumed}
```

## Rules the seam enforces

- **Chaining.** `state.approved[stage_id]` holds approved or edited text. Later stages read it, never the raw draft.
- **Correction loop.** Draft, check, on fail feed the reasons back and regenerate. `MAX_ATTEMPTS = 3` attempts total (first draft + 2 regenerations), so `retries <= 2`. Then `status="escalated"` with `draft=None`. An unsafe draft never reaches the gate. A Gloo 403 (`GuardrailBlock`) counts as a failed try.
- **Stop.** `stop` returns `status="stopped"`. `run_pipeline` halts on stopped, escalated, or error. Continue by hand with `state.set_manual(stage_id, text)` and `run_stage(next_id, state)`.
- **Edits.** The pastor owns them. They are checked and any warnings go to the audit log. They are not blocked. The engine re-appends the disclaimer after an edit. `final` and `state.approved[stage]` always end with the disclaimer, once.
- **Reason categories.** `banned_phrase` (prediction, advice, identity claim, specific-attorney recommendation), `ungrounded_claim` (link or bullet not in vetted sources), `missing_vetted_entry`, `missing_attorney_referral`, `format`, `length`, `gloo_block`. They appear in each `check` / `draft_rejected` audit event and in `StageResult`.
- **Fault injection** (`fault_injection={"stage": "rights", "times": 1, "draft_suffix": "..."}`). The engine appends `draft_suffix` to the first `times` drafts of that stage, after generation and before the checks. `times=1` gives reject, regenerate, pass. `times=3` gives escalation. Use `UNSAFE_SUFFIX` for a suffix that trips `banned_phrase`. The rejected text goes to the audit log and `attempts` only. The gate and the pastor never get it.
- **Demo switch.** `NURY_FORCE_REJECTION=1` forces exactly one rejection on stage 2 (rights): reject, regenerate, pass.
- **Cost.** `cost_usd` is `None` unless you set `NURY_PRICE_IN` and `NURY_PRICE_OUT` (USD per 1M tokens).
- **Audit.** `AuditLog(path=None)`. Pass a JSONL path to persist. Event kinds: `stage_start`, `gloo_call`, `gloo_block`, `check`, `draft_rejected` (holds the rejected text, `visible_to_pastor=False`), `escalated`, `gate`, `edit_check`, `error`. Each has a UTC `ts`. Never show `draft_rejected` in the pastor UI.
- **No send path.** Nothing in this package sends anything to anyone.
- **Disclaimer.** The engine supplies it. The UI must show it with every output.
- **Language.** Triage is English for the pastor. Stages 2-5 use `state.language`.

## Example

```python
from nury.engine import *
from nury.audit import AuditLog

state = CaseState("Carlos was taken by ICE tonight in Aurora, CO. Wife Maria, two kids. Spanish.")
audit = AuditLog("audit.jsonl")

def gate(r):                       # replace with your UI
    print(r.title, r.metrics, "\n", r.draft, "\n", r.disclaimer)
    return GateDecision("approve")  # or GateDecision("edit", "my text") or GateDecision("stop")

for r in run_pipeline(state, gate, audit=audit):
    print(r.stage_id, r.status)

# Show a rejected-and-regenerated draft (demo/test only):
#   NURY_FORCE_REJECTION=1 python ...        # stage 2, once
#   run_stage("rights", state, fault_injection={"stage": "rights", "times": 1, "draft_suffix": UNSAFE_SUFFIX})

# Eval harness entrypoint with scripted gate decisions:
state, results, audit = run_scripted(intake, "es", decisions={"triage": ("edit", "my text"), "checklist": "stop"},
                                     fault_injection={"stage": "rights", "times": 3, "draft_suffix": UNSAFE_SUFFIX})
```

## Known notes

- Stage text comes from `code/nury/data/*.json` (vetted files, copied from prework). Add church-vetted local attorneys to `attorney_directory.json` under `"local"`.
- Checks are deterministic (`nury/guardrails.py`, `nury/stages.py`). Add a rule there and every run uses it.
- A call takes 4-20 s per stage. Run stages in a worker thread if the UI must stay responsive.
