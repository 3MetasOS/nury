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
| M2 | Oct 6 done | Playbook refactor: detention runs from `code/playbooks/detention/`, same tests pass | jedi |
| M2b | Oct 6 23:00 | Hospital source list drafted for Juan's approval (canvas) | jedi |
| M2c | Oct 7 08:00 | Hospital playbook runs end to end; detention unchanged | jedi |
| M3 | Oct 7 09:00 | Pastor app: crisis selector (2 live, 2 soon), Intake, Pipeline, Package, audit view | artisans |
| M4 | Oct 7 11:00 | Real eval run, 20 scenarios, first scorecard; failures fixed and logged | artisans |
| M5 | Oct 7 12:00 | Description draft; deck with real numbers | ninja |
| M6 | Oct 7 15:00 | End-to-end demo, one rejected-and-regenerated draft; harness scores final | all |
| M7 | Oct 7 18:00 | Description and deck final; Juan reads | ninja |
| M8 | Oct 7 20:30 | Deck, script, video in Juan's hands | ninja, video |
| M9 | Oct 7 21:00 | SUBMITTED. Hard stop. | sensei |
| M10 | Oct 8 09:00 | Finalist video, only if top 25 | video |

## Crisis selector and live tracks (decided by Juan, 2026-10-06 ~21:00 MDT)
The app opens on a **crisis selector**, not on intake. Each card is a playbook.
- **Live (2):** `detention` (flagship, the demo) and `hospital` (hospital emergency: a family member in the ER or ICU). Both run on the same engine with no engine change. Each has its own vetted sources, at least 5 scored scenarios (detention has 20), and its own scorecard section.
- **Coming soon (labeled, not clickable):** sudden death in a family; house fire or displacement. They are cards only. Nothing is claimed about them.
- The pitch and description claim only what runs and is scored. The demo stays the detention family.
- Hospital playbook rules: information only, no medical advice, no diagnosis or prognosis, no claim to be clergy or a clinician, vetted sources only, same approval gates and correction loop. Sources are drafted by hack-jedi from official public pages (build-time reading only; the runtime has no open web) and **approved by Juan** before they ship.
- API: `GET /api/playbooks` returns id, title, one-line description and status (`live` or `soon`). The selector reads it. The UI never hardcodes a crisis.

## Nury skills (our own light skill system, decided by Juan 2026-10-06)
A **skill** is a small, versioned instruction module that a playbook stage can include by name. It is not a Claude Code skill; it is plain text that the engine adds to the stage prompt. A new crisis picks skills up by name.
```
code/skills/<name>/SKILL.md     the instructions (EN and ES sections), version in the header
code/skills/<name>/checks.json  optional named checks that go with the skill
stages.json                     "skills": ["voice", "grounding"] on a stage
```
- **Safety floor wins.** A skill can add rules and checks. It can never remove or override the floor, the disclaimer or a playbook's banned patterns. The loader refuses a skill that tries.
- **Evidence.** The audit log records a `skill_applied` event (name, version, stage) every time. The scorecard shows which skills ran.
- **First two skills.** `voice` (distilled from the humanizer ideas: plain words, no stock phrases, no inflated language, natural Spanish for the family) on the pastoral and checklist stages. `grounding` (every line comes from the vetted points, or is a plain question for the professional) on checklist and resources stages.
- **Proof.** Deterministic check for stock AI phrases, a tone score from the Jev decision API (TypeSafe, a third-party service used at eval time only), and a before/after comparison for the judges.
- No extra model call. Skills change the prompt, not the number of calls.

## Case file and next-steps map (decided by Juan 2026-10-06)
After the pastor approves a package, Nury can save it as a **case file**: a folder of linked markdown pages (index, one page per stage, people, documents, timeline, log) the pastor can reopen, read, print and export. Style: a small personal wiki, compiled once from approved text.
- **Saved by the app, not uploaded.** The app saves case files in `cases/` on the server that runs it (gitignored). Nothing is uploaded to anyone; the only thing that leaves is the model request, which carries tokens, not names. There is no sign-in, no per-church separation and no encryption at rest yet (see FEATURES.md). Demo and evals use synthetic families only.
- **Approved content only.** Pages hold what the pastor approved or edited. A rejected draft never enters a case file. `log.md` records each gate with a timestamp.
- **Built without a model call.** Pages and the map are produced deterministically from the approved stage outputs and the audit log.
- **Next-steps map.** One SVG per case: lanes for tonight, this week, questions still open, and who to call. It shows steps and questions, never outcomes. No future-tense claims about the case.
- **Later (not before submission):** a possible-paths map from vetted process sources (`pathways.json` per playbook), and a case update loop where Nury proposes page edits and the pastor approves each one.

## Privacy layer: pseudonymize before anything goes to a model (decided by Juan 2026-10-07)
Nury sends no direct identifiers to any model. A **PrivacyClient** wraps the Gloo client (the engine already takes `client=`, so the core does not change).
- **Outbound:** names, phone numbers, emails, street addresses, dates of birth, A-numbers and case numbers are replaced with tokens (`[PERSON_1]`, `[PHONE_1]`, `[PLACE_1]`...) before the request is sent. Places are generalized to the city or state level when a token would break the meaning.
- **The mapping is never sent to the model.** The token map lives in memory for the run and in the saved case file (`privacy-map.json`) on the server that runs the app.
- **Inbound:** the response is detokenized by the app, so the pastor sees real names. The family-facing message reads naturally.
- **Detection:** deterministic rules for phones, emails, IDs, dates and addresses; for names, the pastor confirms a **protected terms** list on the intake screen (Nury proposes capitalized words it found; the pastor adds or removes). The pastor stays in charge of what counts as protected.
- **Honest limit:** this removes direct identifiers. Context ("14 years", "his workplace") can still hint at who a person is. We say that plainly.
- **Proof:** a leak test sends a synthetic intake full of canary names and numbers and checks the captured outbound request: none of them may appear. The same wrapper covers the eval harness's calls to Gloo; Jev only ever sees synthetic families.
- On by default in the app and in the eval adapter.

## Case revision: reload a case and run a second path (decided by Juan 2026-10-07)
A pastor reopens a saved case, records **what happened** (a step, and whether it went as hoped, did not, or is unknown, in the pastor's words), and Nury re-runs the affected stages with the new facts. Never a prediction; it is a record plus a new draft.
- Built on existing pieces: the case file holds the approved text; a revision builds a new `CaseState` with the earlier approved stages kept, the update appended to the intake, and runs the stages from triage on (new facts always re-run triage), through the same correction loop and approval gates.
- The case keeps **versions**: `v1` stays untouched; `v2` is saved beside it with a change log (what the pastor reported, which stages were re-run, what changed). The pastor can compare v1 and v2.
- Revision runs go through the PrivacyClient like every other run.

## Church network and official lists (decided by Juan 2026-10-07)
Rule change (Juan): "Nury never recommends a specific attorney" becomes "Nury lists only contacts the pastor has vetted, labeled as the church's own, plus official vetted lists. It never endorses anyone."
- **Church network:** a directory the app saves for the pastor (`network/`, gitignored, like `cases/`): name, kind (pro bono immigration lawyer, Medicare/Medicaid helper...), languages, city and state, phone or link, the pastor's note, last-used date. The attorney and resources stages match the case (place, language, need) and list these first under "People our church has worked with". The vetted link and phone allowlist includes them. A small "Our network" screen adds, edits and tags entries.
- **Official list:** the U.S. Department of Justice list of recognized free legal service providers by state, ingested at build time as a vetted source (Juan approves it on a canvas first). Same pattern for other crises where an official list exists.
- **No open web at runtime.** A later pastor-triggered "find more" panel (unverified candidates, never in a family message, one-click "add to our network" after the pastor checks them) is after submission. Reason: fake "notario" services target these families; search results can include them.

## Rules that stay
Vetted sources only. No open web. No send path. Nury is not a pastor. Humanitarian, never political. Keys from the environment only.
