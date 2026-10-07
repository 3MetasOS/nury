# Nury architecture: a crisis-management system driven by playbooks

Decided by Juan and hack-sensei, 2026-10-06. Owner: hack-sensei. Built by hack-jedi.

## Idea
Nury is one engine that runs crisis playbooks. A **crisis** is data, not code. Adding a new crisis and how to solve it means adding a playbook folder. The engine does not change.

Detention is playbook #1 and the flagship demo. The engine, safety floor, gates, audit and eval harness are shared by every playbook.

## Layers
1. **Engine** (`code/nury/`): runs stages, chains approved or edited text, runs the correction loop (3 attempts total, then escalate), runs the approval gate (Approve / Edit / Stop), writes the audit log. Knows nothing about immigration.
2. **Safety floor** (in the engine, not in data): no legal advice, prediction or strategy; no claim to be a pastor, counselor or lawyer; disclaimer on every output; URL and phone allowlist from the playbook's vetted sources; no send path. A playbook can add checks. It cannot remove these.
3. **Playbook** (`code/playbooks/<crisis_id>/`): everything that is specific to one crisis.
4. **App** (`code/app/`): the pastor picks a crisis from the playbook list, then Intake, Pipeline, Package.
5. **Evals** (`evaluations/`): each scenario names its `playbook`. The harness runs any playbook. Scenarios per playbook, scored per playbook.

## Playbook contract
```
code/playbooks/detention/
  playbook.json     id, title, one-line description, languages, disclaimer text (EN, ES)
  stages.json       ordered stages; each has: id, title, prompt file, sources used,
                    extra checks (by name), output language rule (pastor | family),
                    optional "when" condition on triage fields (a path)
  prompts/          one prompt file per stage (verbatim prompts are judged evidence)
  sources/          vetted JSON files; the only facts the stages may use
  outcomes.json     terminal outcomes and what the package contains for each
```
- **Paths:** a stage can run, or change its prompt or sources, depending on triage fields. Example: where the person was detained (workplace, traffic stop, home, check-in) selects a different checklist block. Conditions are plain field matches, no code.
- **Outcomes:** `package_complete`, `stopped_by_pastor`, `escalated`, `blocked`. A playbook says what each outcome hands the pastor (for example, on `escalated` at stage 2: the sources list plus "handle this manually").
- **Triage is stage 1 of every playbook.** Its output fields feed the paths.

## What changes from the current code
hack-jedi's core already has the stage registry, chaining, loop and gates. The change is small: move the detention stages, prompts and sources out of Python into `code/playbooks/detention/`, add a playbook loader, and make `run_pipeline(playbook, state, ...)` take the loaded playbook. Behavior for detention stays the same. Keep `INTERFACE.md` current.

## Milestones (MDT)
| # | When | Milestone | Owner |
|---|---|---|---|
| M1 | Oct 6 done | Gloo client live; core engine with correction loop and gates | jedi |
| M2 | Oct 6 night | Playbook refactor: detention runs from `code/playbooks/detention/`, same tests pass | jedi |
| M3 | Oct 7 09:00 | Pastor app on the engine: crisis picker, Intake, Pipeline, Package, audit view | artisans |
| M4 | Oct 7 11:00 | Real eval run, 20 scenarios, first scorecard; failures fixed and logged | artisans |
| M5 | Oct 7 12:00 | Description draft; deck with real numbers | ninja |
| M6 | Oct 7 15:00 | End-to-end demo, one rejected-and-regenerated draft; harness scores final | all |
| M7 | Oct 7 18:00 | Description and deck final; Juan reads | ninja |
| M8 | Oct 7 20:30 | Deck, script, video in Juan's hands | ninja, video |
| M9 | Oct 7 21:00 | SUBMITTED. Hard stop. | sensei |
| M10 | Oct 8 09:00 | Finalist video, only if top 25 | video |

## Stretch: second playbook
Only after M4. It proves the architecture: a second crisis added with **zero engine changes**. Juan picks the crisis and supplies or approves its vetted sources. Hospital emergency or sudden death in a family are candidates. Nothing is claimed in the pitch until it runs and has at least 5 scenarios scored.

## Rules that stay
Vetted sources only. No open web. No send path. Nury is not a pastor. Humanitarian, never political. Keys from the environment only.
