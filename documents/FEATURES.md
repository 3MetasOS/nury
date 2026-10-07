# Nury features: what is built and what is not

Written 2026-10-07 by hack-jedi from the repo, the test suites and BUILD_LOG. Strict rule: a feature is listed as built only if you can open the file or the result named in the evidence column. Film and deck claim only rows marked BUILT.

Status words:
- **BUILT, live verified**: it ran against the real Gloo endpoint (a live run, or a real browser on a live run), and the result is in a file or in BUILD_LOG.
- **BUILT, offline tested**: it is built and a test or a browser check without a model call proves it. It has not been part of a live run, or it does not need one.
- **BUILT, not yet checked live**: the code or script exists and was never run against the real endpoint.
- **PLANNED**: written in the architecture notes, no code.
- **NOT BUILT** (or **NOT BUILT, next**): nothing exists, or we deliberately left it out. "Next" marks what must exist before real churches use Nury on a server.

"Live verified" means it ran, not that it scored well. Pass rates and the effect of the skills are not claimed here; see `documents/TECH_CLAIMS.md`.

Count: 47 live verified, 37 offline tested, 4 built but not yet checked live, 7 planned, 21 not built.

## 1. Pastor experience

| Feature | What it does | Status | Evidence | For |
|---|---|---|---|---|
| Crisis selector | The app opens on cards. Detention and hospital run. Sudden death and house fire say "coming soon" and cannot be opened. | BUILT, live verified | `code/app/static/index.html` (#picks); `GET /api/playbooks` in `code/app/server.py`; BUILD_LOG 20, 56 | pastor, judge |
| Intake screen | The pastor types what the family said, picks Spanish or English for the family, and can load a demo intake. | BUILT, live verified | `index.html` (#v-intake); `intake` in `playbooks/*/playbook.json`; BUILD_LOG 20, 56 | pastor |
| Protected names step | Nury proposes names to hide from the AI service. The pastor ticks, adds a person or a place, and unticks wrong ones. Phones, emails, addresses, dates and ID numbers are always protected. | BUILT, live verified | `index.html` (#v-protect); `nury/privacy.propose_terms`; `code/tests/test_privacy.py`; BUILD_LOG 47, 56 | pastor |
| Five stages per crisis | Triage, a rights or information brief, contacts, a family checklist, and a pastoral message, drafted in order. | BUILT, live verified | `code/playbooks/*/stages.json`; `evaluations/results/scorecard.md`; BUILD_LOG 66 | pastor, judge |
| Approval gate: Approve, Edit, Stop | After every stage the pastor approves, edits or stops. Later stages read the edited text. | BUILT, live verified | `nury/engine.run_stage`; scenarios 15, 16, 17; BUILD_LOG 51, 56 | pastor, judge |
| Names added in an edit stay protected | A name the pastor types while editing is hidden from the AI service before the next stage runs. | BUILT, live verified | `PrivacyClient.wrap_gate`; scenario 16 live in slot A (BUILD_LOG 51); `tests/test_privacy.py` | pastor, judge |
| Stop | Stop ends the run with "I'll handle this manually." Nothing is sent. | BUILT, live verified | scenario 17 in the scored run; `StageResult` status `stopped` | pastor |
| Progress and status line | A five-step tracker, a live line ("Nury is working on triage…", the rejection wording, "Passed"), seconds per stage, buttons disabled while a stage runs. | BUILT, live verified | `index.html` (#steps, #strip); BUILD_LOG 22 | pastor |
| Halt card | If a stage escalates or the pastor stops, a card says "Nury stopped. Nothing was sent." and offers the vetted sources. | BUILT, live verified | `index.html` (#halt); escalation viewed in a browser through the test-only switch (BUILD_LOG 22); scenario 06 | pastor |
| Day and Night | An optional toggle. Night is the default, and the choice is remembered. | BUILT, offline tested | `index.html` (#theme); commit 52c7346; toggle flips dark to light in a browser check on 2026-10-07; not part of a live run | pastor |
| Case view | A case is one full run of the five stages (older text says 'package'). The finished case shows every stage with Copy all and Download, and the line "Nury never sends anything. You do." | BUILT, live verified | `index.html` (#v-pkg); BUILD_LOG 56 | pastor |
| Audit view | A collapsible log of each call, check and gate, with reason categories only, never a rejected draft. | BUILT, live verified | `server.safe_event`; `index.html` (#log2); BUILD_LOG 22 | pastor, judge |
| Rejection strip | When a draft is rejected the screen reads "Draft rejected by guardrail. Regenerating (2 of 3)." and then "Passed". The rejected text is never shown. | BUILT, live verified | `index.html` (#strip); slot B check f; BUILD_LOG 22 | pastor, judge |
| Save as a case | One tap saves the approved case as a case folder of linked pages, kept by the app. | BUILT, live verified | `nury/casefile.save_case`; `index.html` (#b-save); BUILD_LOG 56 (case file 5 of 5) | pastor |
| Open cases and read them | Saved cases list on the first screen. The pastor reads the pages, sees the map, and exports a zip. | BUILT, live verified | `index.html` (#v-case); `list_cases`, `load_case`, `export_zip`; BUILD_LOG 56 | pastor |
| Revision, v1 to v2, and Compare | "Something changed": the pastor records what happened, Nury drafts again from triage with the same gates, v2 is saved beside v1, and a red and green view compares them. | BUILT, live verified | `code/app/server.py` (revision); `evaluations/casefile_check.py`; BUILD_LOG 56 (v1 files byte-identical after v2) | pastor, judge |
| Next-steps map | One picture with four lanes: tonight, this week, questions still open, who to call. Steps and questions only, no outcomes. | BUILT, live verified | `nury/casefile.nextsteps_svg`; `tests/test_casefile.py`; BUILD_LOG 34, 56 | pastor, judge |
| Our network screen | The pastor adds, edits, tags and deletes contacts, sets the church's place, imports and exports. A banner says "Fictional demo contacts" in demo mode. | BUILT, offline tested | `code/app/static/network.html`, `code/app/network_api.py`; `tests/test_network_api.py`; browser checks at 390 and 1280 px; mounted in the app (BUILD_LOG 47) | pastor |
| Scripture in the pastoral message | The model picks a verse id from the approved list for this case and writes at most two short why-lines. The app inserts the exact verse text, reference and translation name. If no verse fits, no verse is added. | BUILT, live verified | `nury/scripture.py`; `checks.verse_block_verbatim`; `tests/test_scripture.py`; live verified (8 runs, 2026-10-07) | pastor, judge |
| Three Scripture checks | `no_providence_claims` (no claim about what God will do, why this happened, or what God knows, sees, feels, wants or intends beyond the verse, EN and ES), `no_model_scripture` (the model writes no reference and no verse), `verse_block_verbatim` (the block equals the source word for word). The registry now holds 20 named checks; the 14 above are the ones the scored runs used. | BUILT, offline tested | `nury/checks.py`; `tests/test_scripture.py` | judge, developer |
| Three panel-driven checks | No 'call <Name>' in the pastor's voice, no unsupported signing or care-decision directive in a DO NOT list, no advice or 'critical' claim in triage. The registry holds 20 named checks, the same 20 at the scored build c317050. | BUILT, offline tested | `nury/checks.py`; `tests/test_panel_fixes.py` | judge, developer |
| Needs follow-up flag | The pastor marks a saved case as needing follow-up, or clears the mark. A flag only: no reminder, no date. Saved in `case.json`; no other file changes. The route and the button are the app's, not built yet. | PLANNED | `casefile.set_follow_up`; `tests/test_casefile.py` | pastor |
| Jev checks every draft at run time | After the deterministic checks pass, one batched call to Jev asks the stage's yes/no questions about the draft. 0.50 or more rejects and regenerates (0.60 for `assumes_facts`, a per-question line set after seeing validation data), 0.30 up to the line passes and is logged, below 0.30 passes. Not applied to pastor edits. | BUILT, live verified | `nury/jev_gate.py`; `tests/test_jev_gate.py`; `evaluations/validation/JEV_GATE_VALIDATION.md`; live runs 2026-10-07 (it rejected safe text in detention 14 before a fix) | pastor, judge |
| Jev sees only tokens | The draft, the intake, earlier text and the sources go to Jev through the same Pseudonymizer as the Gloo path. The token map never goes. | BUILT, offline tested | `tests/test_privacy.py` (Jev leak test, 15 canaries) | pastor, judge |
| The gate fails open | No key, timeout (8 s), error or a bad answer: the draft goes on under the deterministic floor, the audit logs `unavailable`, later stages skip the gate. The pastor sees nothing. | BUILT, offline tested | `tests/test_jev_gate.py` | pastor |
| Jev audit and progress | Each question logs stage, attempt, question, probability and decision (`reject`, `uncertain`, `pass`, `unavailable`, `skipped`). Stage metrics gain `jev_ms` and `jev_calls`. `jev_gate_start` marks the call in flight, for a `checking_jev` phase. | BUILT, offline tested | `nury/jev_gate.py`; `tests/test_jev_gate.py` | developer |
| Rules registry | Every floor rule, named check and Jev question has a plain-English description, a kind, the file it lives in and the stages that use it. Read-only. | BUILT, offline tested | `nury/rules.py`; `tests/test_rules.py`; the app route `GET /api/rules` is hack-artisans' | pastor, judge, developer |
| New-crisis scaffold | One command creates a playbook folder from a template, status soon, runs the loader's validation, and prints what is left: prompts, sources and their approval, scenarios, tests, then the status flip. | BUILT, offline tested | `tools/new_playbook.py`; `tests/test_new_playbook.py` | developer |
| How to add a rule | A written note with two worked examples (a data rule and a code check) whose code is run by a test. | BUILT, offline tested | `documents/product/ADD_A_RULE.md`; `tests/test_add_a_rule_doc.py` | developer |
| Run ledger | An append-only JSONL record, one line per stage and per run: attempts, rule categories fired, Jev decisions and probabilities, tokens, cost, latency, provider, outcome. Never text, names or case ids; a string that is not a short slug stops the write. | BUILT, offline tested | `nury/ledger.py`; `tests/test_ledger.py` (leak test with canaries) | developer, judge |
| Ops summary | `ledger.summarize()` and a read-only `GET /api/ops`: cost per case, latency p50 and p95 per stage, attempts, escalation and rejection rates, Jev decisions by question, provider mix. The app has to call the recorder and mount the route (hack-artisans). | BUILT, offline tested | `app/ops_api.py`; `tests/test_ledger.py` | developer |
| Feedback capture (off by default) | At each gate, records the pastor's action and the sentences that changed, with names already tokenized, plus rule categories, Jev decisions, an optional reason chip and the 'Something changed' answer. A strict counts mode stores no sentence. Whole drafts and Scripture are never stored. | BUILT, offline tested | `nury/feedback.py`; `tests/test_feedback.py` (canary leak test, both modes) | developer, judge |
| Learning report and candidate review | A script turns feedback into a report and proposed candidates (prompt line, rule, Jev question, scenario), each with evidence counts. A candidate file has a status, and approval needs a named person and a date; no script sets a status past proposed. | BUILT, offline tested | `tools/learning_report.py`, `tools/candidates.py`; `tests/test_learning_loop.py` | developer |
| Candidate before and after test | Runs a candidate on a copy of the repository against the core, attacker and case-file sets, prints before and after, and a no-regression gate. Never changes the repository. Live use costs about $10 for all sets and one repeat and has not been run. | BUILT, offline tested (mock agent only) | `tools/candidate_test.py` | developer |
| Learning loop on synthetic data | A worked example: 30 invented sessions, the real capture code, a report, five proposed candidates. No real pastor has used Nury. | BUILT, offline tested | `documents/product/learning_example/`; `LEARNING_LOOP.md` | developer, judge |
| Feedback in the app | The server calling `record_gate`, the reason chips, `POST /api/feedback`, and the consent sentence on screen when capture is on. | PLANNED | hack-artisans | pastor |
| Gloo retries | A transient failure (429, 500, 502, 503, 504, a dropped connection, a timeout) is retried up to 3 tries in all with 1 s then 2 s backoff. Never on 402, 403, other 4xx or a quota 429. A retry is not a draft attempt. | BUILT, offline tested | `nury/gloo_client.py`; `tests/test_gloo_retry.py` (11 tests); a live smoke on detention 01 (a clean call; no failure was injected live) | developer |
| Audit hook and monotonic times | `AuditLog.subscribe(fn)` and a monotonic `t_ms` on every event. A raising subscriber cannot break a run. | BUILT, offline tested | `nury/audit.py`; `tests/test_audit_hooks.py` | developer |
| Replay mode | With no Gloo key the app runs a recorded run of each playbook's sample intake: the model's words are recorded, the checks, the loop, the gates, the audit, the privacy layer, the case file and Scripture run live. Typed intakes are refused; the Jev scores shown are labelled recorded. Off when a key is present. | BUILT, offline tested; driven in a real browser | `nury/replay.py`, `code/replay/`, `tests/test_replay.py` | judge, developer |
| Prices as data | `pricing.json` holds model prices with a source and date; the engine computes cost per stage from it. Unknown models have no cost. Jev's public price ($0.042 per million input tokens, output free, read 2026-10-07) is in the file with its source; `pricing.jev_cost_usd` computes a gate cost, and the engine does not add it to a stage's cost. | BUILT, offline tested | `nury/pricing.json`, `nury/pricing.py`; `tests/test_pricing.py` | developer, judge |
| CI (offline tests and a key scan) | A workflow that runs the offline tests and fails if a tracked file holds a key-like string. It has not run: there was no runner. | BUILT, not yet checked live | `.github/workflows/ci.yml`, `code/tools/scan_keys.py`; `tests/test_ci.py` | developer |
| Skills A/B with repeats | The before-and-after script repeats each arm at least 3 times, alternates the order and compares the difference with the spread inside an arm. It has not been run live. | BUILT, offline tested (fake model only) | `evaluations/skills_ab.py`; `evaluations/tests/test_skills_ab.py` | developer |
| Verse bank in public-domain text | 12 verses (10 for detention, 12 for hospital), Reina-Valera 1909 in Spanish and World English Bible in English, both public domain, with source URL and licence recorded. A verse ships only after Juan approves it. | BUILT, offline tested | `playbooks/*/sources/scripture.json`, `approvals.json`; the review canvas | pastor, judge |
| Church's own verses | The church adds verses to `network/scripture.json` with the exact text, a source URL, a licence and a translation name. The loader refuses a verse without them. There is no screen for this yet. | BUILT, offline tested | `scripture.load_bank`; `tests/test_scripture.py` | pastor |
| Swap the verse at the gate | The engine can swap in any other approved verse (exact source text) and leave the why-lines alone. The selector in the app is not built. | PLANNED | `scripture.swap_verse`, `scripture.list_verses`; no screen yet | pastor |

## 2. Safety

| Feature | What it does | Status | Evidence | For |
|---|---|---|---|---|
| Safety floor in code | Rules every prompt carries and checks no playbook or skill can remove: no advice, no outcome prediction, no claim to be a pastor, lawyer or doctor. | BUILT, live verified | `nury/guardrails.py`, `nury/engine.py`; TECH_CLAIMS 5 to 8 | judge, developer |
| 20 named checks plus the floor | Labels, numbered facts, cited bullets, referral, vetted links, headings, word limit, agency names, stock phrases, endorsement words, listed contacts, network entries, official list, unauthorized promises, plus the three Scripture checks and the three panel-driven checks. | BUILT, live verified | `nury/checks.py` (20 entries in `REGISTRY`); every scored run | judge, developer |
| Correction loop | A failed draft goes back with the reasons, not the draft. Three attempts in all. | BUILT, live verified | `engine.run_stage`; `evaluations/results/live_checks_slot_b.md` (check f) | judge |
| Escalation | After the third failed attempt the stage ends with no draft shown and "I'll handle this manually." | BUILT, live verified | scenario 06 in the scored run (intended escalation); `tests/test_core.py` | pastor, judge |
| Disclaimer on every output | Every output says Nury is an AI assistant, not a lawyer, doctor, pastor, counselor or therapist, in English and Spanish. | BUILT, live verified | `playbooks/*/playbook.json`; loader refuses a weaker disclaimer; scored runs | pastor, judge |
| Link, phone, domain and email allowlist | A link, phone number, bare web address or email must come from the vetted sources or approved earlier text. Invented ones are rejected. | BUILT, offline tested | `guardrails.url_reasons`, `phone_reasons`, `email_reasons`; `tests/test_core.py` (BareDomains, Emails); FAILURE_LOG | judge, developer |
| The pastor's voice cannot promise action | The pastoral message may invite but may not say anyone is searching, preparing, sending or visiting, or say "soon", unless the pastor wrote it. | BUILT, live verified | `checks.no_unauthorized_promises`; `tests/test_core.py` (Promises); five live messages (BUILD_LOG 70) | pastor, judge |
| No agency names on screen | Triage, checklist and pastoral text say "immigration officers", never an agency name. | BUILT, live verified | `checks.no_agency_names`; scored runs | pastor, judge |
| Hospital medical guardrails | Twelve extra patterns block a prognosis, a diagnosis guess, medical advice, advice on ending care, and promised healing, in English and Spanish. | BUILT, offline tested | `playbooks/hospital/playbook.json` (`extra_banned`); `tests/test_core.py` (Hospital) | pastor, judge |
| HTTP 403 from Gloo counts as a failed try | If Gloo's guardrails block a request, Nury retries and then escalates with outcome "blocked". | BUILT, offline tested | `gloo_client.GuardrailBlock`; `tests/test_core.py` (GloLayer); no live 403 has happened | developer, judge |
| No send path | The product's outbound calls are the Gloo request, the Jev classifier gate (only when JEV_API_KEY is set, pseudonymized text only) and, only when YVP_APP_KEY is set, a passage-id request to YouVersion. Nothing reaches the family except through the pastor. | BUILT, offline tested | `tests/test_core.py` (NoSendPath) | pastor, judge |
| Fault injection | A switch forces one unsafe draft so the reject-and-regenerate beat can be shown and tested on demand. | BUILT, live verified | `engine.fault_injection`; `UNSAFE_SUFFIX`; slot B check f | judge, developer |

## 3. Privacy

| Feature | What it does | Status | Evidence | For |
|---|---|---|---|---|
| Tokens instead of identifiers | Names the pastor protected, phones, emails, street addresses, dates, A-numbers, case numbers and ID numbers become tokens before a request goes to the model, and become real again in the reply. | BUILT, live verified | `nury/privacy.py`; live A/B on three scenarios (PROMPT_NOTES, Privacy); BUILD_LOG 38 | pastor, judge |
| Leak test | Captured request bodies are searched for canary names and numbers: 90 checks per playbook, none found. The scored runs also check every string sent to the model. | BUILT, live verified | `tests/test_privacy.py`; `tools/show_proofs.py 3`; `privacy_no_leak` on all 20 scored runs (BUILD_LOG 66) | judge |
| Token repair | A mangled token is repaired. An unknown token makes Nury ask again (twice at most) and then shows a visible gap. | BUILT, offline tested | `PrivacyClient.ask`; `tests/test_privacy.py` | developer |
| Saved by the app, not uploaded | Cases, the church network and the token map are saved as files by the app on the server that runs it. They are not committed to git and are uploaded to no one. Only the model request leaves, with tokens instead of names. | BUILT, offline tested | `.gitignore` (cases/, network/); `casefile` guards; `tests/test_casefile.py` | pastor, judge |
| Privacy on and off | On by default. One switch turns it off for a before and after comparison. | BUILT, live verified | `privacy.make_client`; `NURY_PRIVACY`; live A/B (BUILD_LOG 38) | developer, judge |

## 4. Playbooks

| Feature | What it does | Status | Evidence | For |
|---|---|---|---|---|
| Detention playbook | The flagship crisis: an immigration detention or raid, five stages, official and church contacts. | BUILT, live verified | `code/playbooks/detention/`; scored run 20 scenarios (BUILD_LOG 66) | pastor, judge |
| Hospital playbook | A family member is in the ER or ICU: information brief, hospital resources, checklist, message. Sources approved by Juan. | BUILT, live verified | `code/playbooks/hospital/`; scored run 8 scenarios (BUILD_LOG 66); `sources/approvals.json` | pastor, judge |
| Coming-soon cards | Sudden death and house fire appear as labeled cards only. The engine refuses to run them. | BUILT, offline tested | `playbooks/sudden-death/`, `house-fire/` (status soon); `tests/test_core.py` | pastor, judge |
| A crisis is a folder | A new crisis is data: prompts, sources, stages, outcomes. The loader validates it and refuses an unsafe one. | BUILT, offline tested | `nury/playbook.py`; `test_second_playbook_zero_engine_changes`; `test_playbook_cannot_drop_disclaimer_floor` | judge, developer |
| Paths and prompt variants | A stage can run, be skipped or swap its prompt depending on triage fields. No shipped playbook uses a variant yet. | BUILT, offline tested | `playbook.when_matches`; `tests/test_core.py` (Playbooks) | developer |
| Approvals gate | A playbook whose sources are not all approved does not run. A rejected source is dropped. | BUILT, offline tested | `playbook._apply_approvals`; `tests/test_core.py` (Hospital) | judge, developer |

## 5. Sources

| Feature | What it does | Status | Evidence | For |
|---|---|---|---|---|
| Vetted rights file and attorney directory | Detention facts come only from a reviewed file with citations. National hotlines and directories come only from a reviewed list. | BUILT, live verified | `playbooks/detention/sources/`; scored runs | pastor, judge |
| Hospital sources | Five public sources approved by Juan (HIPAA family sharing, hospital patient rights, language access, 988, social workers). One weak source was rejected. | BUILT, live verified | `playbooks/hospital/sources/`; `approvals.json`; `SOURCES_DRAFT.json` | pastor, judge |
| Official Department of Justice list | 18 approved providers for Colorado with the "listed does not mean recommended" line, never called free. Seven held entries are never shown. | BUILT, live verified | `playbooks/detention/sources/official_list.json`; `nury/officiallist.py`; `tests/test_official.py`; slot B check a; slot C n01 | pastor, judge |
| Church network | The pastor's own contacts, matched by state, language and kind, listed first and labeled the church's own. Never ranked or endorsed. | BUILT, live verified | `nury/network.py`; `tests/test_network.py`; slot B checks a, b, d; slot C n01 (n02 sent to review) | pastor, judge |
| Pastor's private note | The note on a network contact stays on the pastor's screen. It never reaches a model or a family message. | BUILT, offline tested | `network.source_for`; `tests/test_network.py` | pastor, judge |

## 6. Skills

| Feature | What it does | Status | Evidence | For |
|---|---|---|---|---|
| voice skill | Plain words, short sentences, no stock AI phrases, natural Spanish. Added to the pastoral and checklist prompts with no extra model call. | BUILT, live verified | `code/skills/voice/`; `nury/skills.py`; audit event `skill_applied` | developer, judge |
| grounding skill | Every line comes from the vetted points or is a plain question for the expert. Added to the checklist and contact stages. | BUILT, live verified | `code/skills/grounding/` | developer, judge |
| Skill loader and off switch | The loader refuses a skill that overrides the floor. A switch turns skills off for a before and after run. | BUILT, offline tested | `nury/skills.py`; `tests/test_core.py` (Skills) | developer, judge |
| Skills before and after | The same scenarios with skills off and on, to see whether they help. | BUILT, not yet checked live | `evaluations/skills_ab.py`; `evaluations/results/skills_ab/NOTE_TEMPLATE.md`; not run yet | judge |

## 7. Evaluation

| Feature | What it does | Status | Evidence | For |
|---|---|---|---|---|
| Deterministic judges | Seven plain-code judges: banned phrases, disclaimers, allowlist, language, workflow, completeness, stock phrases. | BUILT, live verified | `evaluations/judges/deterministic.py`; scored runs | judge |
| Jev typed judges | Sixteen typed questions (ten yes or no, five scores, one choice) read the whole run; any one run is asked only the 4 to 8 its scenario needs. Accept at 0.80, fail at 0.20, the middle goes to a person. Jev is the Jev decision API from TypeSafe, a third-party service. At test time it judges the whole system, and it also runs as the run-time gate, so these eval verdicts are not independent of the product. The deterministic judges, the red team and the human review stay independent. | BUILT, live verified | `evaluations/judges/jev_judges.py`; BUILD_LOG 66; `tests/test_core.py` (EvalOnly) | judge |
| Judge validation | On ten checks the judge scored unsafe text 0.89 to 0.98 and safe text 0.02 to 0.24, after a first fix failed and was rejected. | BUILT, live verified | `evaluations/validation/JUDGE_VALIDATION.md` | judge |
| Red-team panel, first validation | Three reviewers from other model makers read what the pastor saw. First pass: two caught all injected problems but also flag safe text, so the panel only advises. | BUILT, live verified | `evaluations/judges/redteam_panel.py`; `evaluations/validation/PANEL_VALIDATION.md` | judge |
| Red-team panel on the final sets | The panel run over the final detention and hospital results. | BUILT, not yet checked live | `redteam_panel.py`; `evaluations/LIVE_CHECKS_OWED.md` step 11 | judge |
| Human review canvas | A page for Juan grouped by question, showing only what the pastor saw, with pass and fail buttons. | BUILT, live verified | `evaluations/make_review_canvas.py`; BUILD_LOG 32 | judge |
| Attacker intakes | Eighteen hostile intakes written by a non-Claude model and edited by a person, to try to break the rules. | BUILT, not yet checked live | `evaluations/scenarios_attacker/`; BUILD_LOG 44; not run yet | judge |
| Scenario sets and scorecards | Twenty detention and eight hospital scenarios, plus five case-file and three network scenarios, each with a scorecard. | BUILT, live verified | `evaluations/scenarios*/`; `evaluations/results/`; BUILD_LOG 56, 66 | judge |
| Tone check | A Jev score for "warm, plain and human" found the pastoral overpromising bug. The re-run on the fixed core is pending. | BUILT, live verified | `evaluations/results/tone_before_after.md`; BUILD_LOG 66, 70 | judge |

## 8. Tooling

| Feature | What it does | Status | Evidence | For |
|---|---|---|---|---|
| Live checks script | One command runs the owed live checks and logs tokens and dollars. | BUILT, live verified | `code/tools/live_checks.py`; `evaluations/results/live_checks_slot_b.md` | developer |
| Five proofs script | Prints five short on-screen proofs from the real code in about two seconds, with no key. | BUILT, offline tested | `code/tools/show_proofs.py`; TECH_CLAIMS | judge, developer |
| Architecture diagrams | Ten tabs of diagrams drawn from the code. | BUILT, offline tested | `documents/architecture/diagrams.html` | judge |
| Claims register | Every technical claim with its evidence and status. | BUILT, offline tested | `documents/TECH_CLAIMS.md` | judge |

## 9. Not built, and next

Nothing in this section may be claimed in the film, the deck or the description.

| Feature | What it does | Status | Evidence | For |
|---|---|---|---|---|
| **Hosting on a server** | Running Nury for real churches on a server needs sign-in, per-church separation of cases and the church network, and encryption at rest. None of the three exists. | NOT BUILT, next | `code/app/server.py` (no authentication), `nury/casefile.py` (plain files), `nury/network.py` (one shared network) | pastor, judge |
| Copyright line shown with a verse (our rule) | The provider's copyright text is shown as returned, except that lines with an email address are removed and a repeated second copyright block is cut. Author, year and licence name stay. Public domain versions show "Public Domain". This trimming is Nury's own rule, not the provider's. | BUILT, live verified | `scripture_providers.attribution`; `tests/test_scripture.py` | pastor, judge |
| Verse source you can swap | The verse text comes from a provider. The bank (public domain) is the default and the fallback. The YouVersion provider turns on only when YVP_APP_KEY and a Bible id are set (Spanish VBL, English BSB). On any failure Nury uses the bank and logs it. | BUILT, live verified | `nury/scripture_providers.py`; `tests/test_scripture.py`; live runs 2026-10-07 (LIVE_COST_LOG, slot F) | pastor, judge |
| Commercially licensed Bible versions | NVI and RVR1960 are not available to our YouVersion app key. The versions in use (BSB, VBL) are Public Domain or Creative Commons. Nothing licensed is claimed. | NOT BUILT | the app key's version list | pastor |
| Other traditions' canons | A verse list per tradition. The bank has a `tradition` field, set to none; the loader refuses any other value. | NOT BUILT | `scripture.load_bank` | pastor |
| Rule editor | Adding or changing a rule from the app, with review, approval and staged rollout. Today a rule goes in through a code change, the tests and a commit. | NOT BUILT | `documents/product/ADD_A_RULE.md` | developer |
| Workflow editor | Creating a new crisis from the app. Today a developer runs the scaffold and writes the files. | NOT BUILT | `tools/new_playbook.py` | developer |
| A loop that learns on its own | Changing prompts or rules without a person. Not built, and not planned: the loop only proposes. | NOT BUILT | `LEARNING_LOOP.md` | developer |
| Teams and roles | Several pastors or staff sharing a church account with different permissions. Nury today has one shared pool of cases and no sign-in. | NOT BUILT | not designed; everyone who can reach the app sees the same cases and the same church network | pastor |
| Shared cases | A case owned by a person or a church and opened by the right people. Today there is one shared pool of cases on the server. | NOT BUILT | cases live in one folder on the server; no owner field | pastor |
| Encryption at rest | Case files, the church network and the token map are saved as plain files on the server's disk. Nury adds no encryption. | NOT BUILT | `nury/casefile.py` writes plain files | pastor, judge |
| Accounts and sign-in | No login. Anyone who can reach the app can open every case and the church network. | NOT BUILT | `code/app/server.py` has no authentication | pastor |
| Offline mobile app | A phone app that works without a connection. Nury is a web page and needs the Gloo connection to draft. | NOT BUILT | no mobile or offline code | pastor |
| Backups and sync | Automatic copies of cases and the network. | NOT BUILT | export zip only | pastor |
| Case update loop | Nury proposing edits to case pages, with the pastor approving each one. Revision v1 to v2 exists; this does not. | PLANNED | `documents/ARCHITECTURE.md` (marked later) | pastor |
| Possible-paths map | A map of possible next paths built from vetted process sources. | PLANNED | `documents/ARCHITECTURE.md` (marked later) | pastor |
| Pastor-triggered "find more" search | A panel that finds unverified candidates, never in a family message, with one tap to add to the network after the pastor checks them. No open web at runtime today. | PLANNED | `documents/ARCHITECTURE.md`; after submission | pastor |
| More crises | Sudden death, house fire, and others. Only labeled cards exist. | PLANNED | `playbooks/sudden-death/`, `house-fire/` (no stages) | pastor |
| Official lists for other states | The DOJ list was read for Colorado only. Other states show no official section. | NOT BUILT | `officiallist.py` (state `CO`) | pastor |
| More family languages | Family output is Spanish or English only. | NOT BUILT | `LANG_NAME` in `nury/playbook.py` | pastor |
| User interface beyond English | The pastor's screens are in English only. | NOT BUILT | `code/app/static/index.html` | pastor |
| Screen reader test | The pages use labels and focus rings, but no one has tested them with a screen reader. | NOT BUILT | no evidence | pastor |
| Voice input or call transcription | Taking the call and writing the intake by voice. | NOT BUILT | no code | pastor |
| Printable PDF | A case exports as a zip of text pages and a picture. There is no PDF. | NOT BUILT | `export_zip` only | pastor |
| Testing with real pastors | No pastor outside the team has used Nury. All families are synthetic. | NOT BUILT | no study; BUILD_LOG | judge |
| Native-speaker review of the Spanish | Word checks catch stock phrases but not how natural the Spanish sounds. No native reader has scored it. | NOT BUILT | `NOTE_TEMPLATE.md` (what the test cannot show) | pastor, judge |
| Sending or sharing from Nury | Deliberately not built. The pastor copies or downloads and shares by hand. | NOT BUILT | `tests/test_core.py` (NoSendPath) | pastor, judge |
