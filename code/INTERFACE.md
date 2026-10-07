# Nury core interface (hack-jedi)

Python 3.12. Needs `requests`. `GLOO_API_KEY` comes from the environment or the repo-root `.env`. `GLOO_MODEL` is optional (default `gloo-anthropic-claude-sonnet-4.6`). Run from `code/`.

```python
from nury.engine import (CaseState, GateDecision, StageResult, run_stage, run_pipeline,
                         approve_all, DEMO_PROVOKE, STOP_MESSAGE)
from nury.audit import AuditLog
from nury.engine import get_playbook, compute_outcome   # get_playbook("detention") -> Playbook
from nury.playbook import list_playbooks, load_playbook   # list_playbooks() -> [{id, title, description}] for the crisis picker
from nury.stages import STAGES, REGISTRY      # shim: the detention playbook's stages (ids: triage, rights, attorney, checklist, pastoral)
from nury.gloo_client import GlooClient, GuardrailBlock
```

## Signatures

```python
CaseState(intake: str, language: str = "es")   # .approved {stage_id: approved-or-edited text}
                                               # .results  {stage_id: StageResult}
                                               # .set_manual(stage_id, text)  # pastor wrote it by hand

GateDecision(action: "approve" | "edit" | "stop", text: str | None)   # text required for "edit"

run_stage(stage_id, state, gate=approve_all, client=None, audit=None, provoke=None, fault_injection=None, playbook=None) -> StageResult
run_pipeline(playbook, state, gate=approve_all, client=None, audit=None, provoke=None, stages=None, fault_injection=None) -> list[StageResult]
                                  # playbook = id string or Playbook. The old run_pipeline(state, gate, ...) still works (detention).
run_scripted(intake, language="es", decisions=None, fault_injection=None, client=None, audit=None, stages=None, playbook=None) -> (state, results, audit)
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

## Playbooks (a crisis is a folder)

`code/playbooks/<id>/` holds `playbook.json`, `stages.json`, `prompts/`, `sources/`, `outcomes.json`. The engine never names a crisis. Detention is `playbooks/detention/`. To add a crisis, add a folder. See `documents/ARCHITECTURE.md`.

- `playbook.json` carries the domain wording the engine's rules template fills in: `boundary: {who, domain, professional, professional_kind}`, the `disclaimer` (en, es), `draft_label`, and optional `extra_banned: [{pattern, why}]`. The rules stay in the engine (`nury/guardrails.py`). The engine holds no immigration words.
- `stages.json` per stage: `id, title, audience ("pastor"|"family"), prompt, input, deps, sources, checks, when, variants`.
- `sources[]`: `{name, file, var, groups:[{list, line, empty?}]}`. The engine renders the vetted JSON into the prompt variable `{{var}}`. `{{lang_name}}` is also available.
- `checks[]`: named checks from `nury/checks.py`: `required_labels, numbered_after, cited_bullets, ends_with_referral, vetted_links_present, required_headings, max_words`. They add to the safety floor.
- **Paths.** `when` is a plain field match on triage output (`"LABEL: value"` lines become fields, e.g. `urgency`). `{"field": "triage.urgency", "in": ["high"]}`, or `equals`, `matches` (regex), `all`, `any`. A stage whose `when` fails gets `status="skipped"` and the run goes on. `variants: [{when, prompt}]` swaps the prompt for the first match. The detention playbook ships no variants yet, because a variant needs its own vetted source facts.
- **Outcomes.** After `run_pipeline`, `state.outcome = {outcome, message, package, failed_stage}`. `outcome` is `package_complete`, `stopped_by_pastor`, `escalated`, or `blocked` (Gloo blocked every attempt, or the call failed). `outcomes.json` says what each hands the pastor. `by_stage` overrides one failing stage (rights escalation hands over `sources_list`).
- **Safety floor (engine, not data).** Boundary prompt, banned-pattern checks, language check, link and phone allowlist from the stage's sources and approved earlier text, disclaimer on every output, 3-attempt cap, no send path. The loader refuses a playbook whose disclaimer drops "AI assistant / pastor / not a <professional> / advice" (EN and ES), or that has no `boundary` fields, and refuses a playbook whose stage 1 is not `triage`.
- Prompt history: `playbooks/detention/PROMPT_NOTES.md`. Tests: `cd code && python3 -m unittest discover -s tests`.

## Crisis list and live tracks

`nury.playbook.list_playbooks()` returns the data for `GET /api/playbooks`, in display order:

```json
{"playbooks": [
  {"id": "detention",     "title": "Immigration detention or raid", "description": "...", "status": "live"},
  {"id": "hospital",      "title": "Hospital emergency",            "description": "...", "status": "live"},
  {"id": "sudden-death",  "title": "Sudden death in a family",      "description": "Coming soon. Not available yet.", "status": "soon"},
  {"id": "house-fire",    "title": "House fire or displacement",    "description": "Coming soon. Not available yet.", "status": "soon"}
]}
```

- `status` is `live` or `soon`. A `soon` entry has no stages. `load_playbook`, `run_stage` and `run_pipeline` raise `PlaybookError` for it. The UI must not make it clickable.
- **Source approval.** A playbook with `sources/approvals.json` (hospital) runs only when every source it uses is `approved`. A `rejected` source is removed from the playbook. While any is `pending`, the playbook lists as `soon` and refuses to run. For UI work only, set `NURY_ALLOW_PENDING=1` in your dev shell: it lists and runs as `live`. Never set it for the demo or the eval.
- **Stage ids differ per playbook.** Take them from `get_playbook(id).stages`. Hospital: `triage, info, resources, checklist, pastoral`. Detention: `triage, rights, attorney, checklist, pastoral`. For the forced rejection use stage index 1 of the playbook: `fault_injection={"stage": pb.stages[1].id, "times": 1, "draft_suffix": UNSAFE_SUFFIX}`. The env switch `NURY_FORCE_REJECTION` still targets `rights` only.
- Pass the id through: `run_stage(stage_id, state, gate, client, audit, fault_injection=..., playbook="hospital")`, `run_pipeline("hospital", state, ...)`, `run_scripted(..., playbook="hospital")`.
- `playbook.json` may carry `intake: {placeholder, demo}`. The app reads it for the intake box and the "Use demo intake" button. The detention demo text is the locked text from `presentation/SHARED_DEMO.md`, byte for byte.
- Hospital extra banned patterns (medical outcome, diagnosis guesses, medical advice, promises of healing) live in `playbooks/hospital/playbook.json` under `extra_banned`, not in the engine.

## Rules the seam enforces

- **Chaining.** `state.approved[stage_id]` holds approved or edited text. Later stages read it, never the raw draft.
- **Correction loop.** Draft, check, on fail feed the reasons back and regenerate. `MAX_ATTEMPTS = 3` attempts total (first draft + 2 regenerations), so `retries <= 2`. Then `status="escalated"` with `draft=None`. An unsafe draft never reaches the gate. A Gloo 403 (`GuardrailBlock`) counts as a failed try.
- **Stop.** `stop` returns `status="stopped"`. `run_pipeline` halts on stopped, escalated, or error. Continue by hand with `state.set_manual(stage_id, text)` and `run_stage(next_id, state)`.
- **Edits.** The pastor owns them. They are checked and any warnings go to the audit log. They are not blocked. The engine re-appends the disclaimer after an edit. `final` and `state.approved[stage]` always end with the disclaimer, once.
- **Reason categories.** `banned_phrase` (prediction, advice, identity claim, specific-attorney recommendation), `ungrounded_claim` (link or bullet not in vetted sources), `missing_vetted_entry`, `missing_referral`, `format`, `length`, `language`, `gloo_block`. They appear in each `check` / `draft_rejected` audit event and in `StageResult`.
- **Fault injection** (`fault_injection={"stage": "rights", "times": 1, "draft_suffix": "..."}`). The engine appends `draft_suffix` to the first `times` drafts of that stage, after generation and before the checks. `times=1` gives reject, regenerate, pass. `times=3` gives escalation. Use `UNSAFE_SUFFIX` (Spanish) for a suffix that trips `banned_phrase` only. The rejected text goes to the audit log and `attempts` only. The gate and the pastor never get it.
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

- Stage text comes from `code/playbooks/detention/sources/*.json` (vetted). Add church-vetted local attorneys to `attorney_directory.json` under `"local"`.
- Floor checks: `nury/guardrails.py`. Named playbook checks: `nury/checks.py`.
- `draft` shown at the gate: `shown_text` starts with a label line ("Borrador de Nury para revisión del pastor") from `playbook.json`. `final` does not carry it.
- A call takes 4-20 s per stage. Run stages in a worker thread if the UI must stay responsive.
