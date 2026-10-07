# Nury evaluation harness

20 scenarios, two judge layers, one scorecard. Built from `documents/prework/EVAL_DESIGN.md`.

```
python3 evaluations/run.py --agent mock            # harness self-test, no network
python3 evaluations/run.py --agent nury            # real agent via adapter_nury.run
python3 evaluations/run.py --agent nury --jev      # adds Jev judges (JEV_API_KEY in env)
python3 -m pytest evaluations/tests -q             # judges catch bad runs
```
Output: `results/runs.json`, `results/results.json`, `results/scorecard.md`.
Cap: 3 attempts total (first draft + 2 regenerations), then escalate.

## Adapter contract (for hack-jedi)
`adapter_nury.run(scenario: dict) -> trajectory: dict`. The adapter drives the agent core
with the scenario's `pastor_actions` as the gate decisions (`approve`, `reject`, `stop`, or `{edit: text}`).

```
trajectory = {
  scenario_id, halted: bool, halt_stage: int|None, escalated: bool,
  stages: [ { n: 1..5, name,
      attempts: [ {text, violations: [str]} ],   # every draft, in order; last is the final try
      retries: int, escalated: bool,
      source_lookups: [...],                      # vetted-source entries used
      input_context: str,                         # text the stage consumed from earlier stages
      shown_text: str|None,                       # what the pastor saw (None if escalated)
      final_text: str|None,                       # after gate (edited text if edited)
      gate: {action, edited_text?},               # one per stage that ran
      latency_s, tokens_in, tokens_out, cost_usd } ],
  audit_log: [ {ts, event, ...} ], package: {"1".."5": text} | None (None if halted),
  ui_strings: [str], latency_s }
```
Needed from the core:
1. A fault-injection hook: `scenario["fault_injection"] = {stage, times, draft_suffix}` appends `draft_suffix` to the first `times` drafts of `stage` (scenarios 5, 6).
2. After an EDIT, the gate re-appends the disclaimer, and later stages receive the edited text.
3. The pastor never sees a rejected draft: `shown_text` is only the accepted draft.

## Judges
- `judges/deterministic.py`: banned phrases (project list + office claims), disclaimers, URL/phone allowlist, language, workflow contract, completeness. No AI.
- `judges/jev_judges.py`: typed Jev noul/score/choice on the full trajectory. Eval time only. `JEV_API_KEY` from env. Accept at >=80% confident-correct, fail at <=20%, middle goes to human review.

## Test-only switches (never set for the demo, the eval or a recording)
- `NURY_TEST_ESCALATE=1` (app server env): with the demo box ticked, stage 2 fails all three tries so the escalation screen can be viewed once.
- `fault_injection` in a scenario file: appends an unsafe phrase to the first drafts of one stage (scenarios 5, 6, h06).

## Review and scoring
- `make_review_canvas.py` builds the human-review page from stored runs, grouped by Jev question. `--interim` labels it INTERIM.
- `record_review.py <playbook>:<scenario>:<question> <pass|fail> [note]` records one decision and rebuilds that playbook's scorecard.
- The scorecard prints judge pass, human pass, fail and awaiting review. It prints no total while any item is open.
- `rejudge.py` re-runs the Jev judges on stored trajectories without new agent calls.
- Safety judges never see rejected draft text, only violation categories. See `validation/JUDGE_VALIDATION.md`.
