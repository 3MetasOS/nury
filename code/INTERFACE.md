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

run_stage(stage_id, state, gate=approve_all, client=None, audit=None, provoke=None) -> StageResult
run_pipeline(state, gate=approve_all, client=None, audit=None, provoke=None, stages=None) -> list[StageResult]
```

`gate(result: StageResult) -> GateDecision` runs after each stage. The gate only ever sees a safe draft.

```python
StageResult(stage_id, title,
  status,      # "approved" | "edited" | "stopped" | "escalated" | "error"
  draft,       # safe draft shown at the gate (None if escalated or error)
  final,       # text later stages use: the draft if approved, the pastor's text if edited
  disclaimer,  # show with every output (English for triage, family language otherwise)
  metrics,     # attempts, retries, self_corrections, latency_s, input_tokens, output_tokens
  message)     # "I'll handle this manually." for stopped / escalated / error
```

## Rules the seam enforces

- **Chaining.** `state.approved[stage_id]` holds approved or edited text. Later stages read it, never the raw draft.
- **Correction loop.** Draft, check, on fail feed the reasons back and regenerate. Max 3 tries (`MAX_TRIES`), then `status="escalated"` with `draft=None`. An unsafe draft never reaches the gate. A Gloo 403 (`GuardrailBlock`) counts as a failed try.
- **Stop.** `stop` returns `status="stopped"`. `run_pipeline` halts on stopped, escalated, or error. Continue by hand with `state.set_manual(stage_id, text)` and `run_stage(next_id, state)`.
- **Edits.** The pastor owns them. They are checked and any warnings go to the audit log. They are not blocked.
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
run_stage("pastoral", state, provoke=DEMO_PROVOKE, audit=audit)
```

## Known notes

- Stage text comes from `code/nury/data/*.json` (vetted files, copied from prework). Add church-vetted local attorneys to `attorney_directory.json` under `"local"`.
- Checks are deterministic (`nury/guardrails.py`, `nury/stages.py`). Add a rule there and every run uses it.
- A call takes 4-20 s per stage. Run stages in a worker thread if the UI must stay responsive.
