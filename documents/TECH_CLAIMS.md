# Technical claims register

Written 2026-10-07 by hack-jedi, from the repo at the commit that adds this file. Rule for the deck, the video and the description: use only rows marked VERIFIED. A row marked PENDING waits for the final scorecard and is not quoted until it is filled. Nothing here is a forecast.

Status words:
- **VERIFIED live**: it ran against the real Gloo endpoint and the result is in a file or a log you can open.
- **VERIFIED offline test**: a test in `code/tests/` proves it, with no model call. Run `cd code && python3 -m unittest discover -s tests` (91 tests pass today; the evaluation harness adds 39 more in `evaluations/tests`).
- **PENDING final scorecard**: it depends on the final scored runs (detention 20, hospital 8, privacy ON, with Jev). Do not quote it yet.

## 1. Platform: Gloo and Claude

| # | Claim | Evidence | Status | The number |
|---|---|---|---|---|
| 1 | Every model call goes through Gloo AI Studio's guarded Responses endpoint, using Claude Sonnet 4.6. | `code/nury/gloo_client.py` (POST `/ai/v2/guarded/responses`, model `gloo-anthropic-claude-sonnet-4.6`); first live call in `BUILD_LOG.md` entry 3; every run since. | VERIFIED live | 1 endpoint, 5 Gloo calls for a full package; first call 1.6 s |
| 2 | When Gloo's guardrails block a request (HTTP 403), Nury treats it as a failed try, regenerates, and after three tries escalates with no draft shown. | `GuardrailBlock` in `gloo_client.py`; handling in `engine.run_stage`; tests `GloLayer` (2 tests) in `code/tests/test_core.py`. No live 403 has happened, so this is proven by test only. | VERIFIED offline test | 3 attempts, then outcome `blocked` |
| 3 | There is no send path. The only outbound call in the product is the Gloo request. | Test `NoSendPath` scans `code/nury` and `code/app` for mail, FTP, socket, web-browser and SMS libraries and finds none; `requests` is used in one file. | VERIFIED offline test | 1 outbound call site, 0 send paths |

## 2. The correction loop and the safety floor

| # | Claim | Evidence | Status | The number |
|---|---|---|---|---|
| 4 | Each stage is drafted, checked by deterministic rules, and if it fails the reasons (not the draft) go back to the model for a new try. Three attempts total, then escalate. | `engine.run_stage`; `code/INTERFACE.md`; live forced-rejection runs in `evaluations/results/live_checks_slot_b.md` (check f: both stage 2 runs took 2 attempts and passed); earlier scorecards show retries and one designed escalation. | VERIFIED live | 14 named checks, 5 floor checks, 3 attempts |
| 5 | The 14 named checks (labels, numbered facts, cited bullets, referral, vetted links, headings, word limit, agency names, stock phrases, endorsement words, listed contacts, network entries, official list, unauthorized promises) plus the floor (19 banned-pattern rules in English and Spanish, language, links and bare domains, phones, emails) run on every draft. | `code/nury/checks.py` (14 entries in `REGISTRY`), `code/nury/guardrails.py` (19 patterns), hospital adds 12 more patterns in `playbooks/hospital/playbook.json`. | VERIFIED offline test | 14 + 5 checks, 19 + 12 patterns |
| 6 | A rejected draft never reaches the pastor. It goes to the audit log as `visible_to_pastor=false` with categories only, and the gate receives no rejected text. | Tests `test_escalation_and_gate_never_sees_unsafe`, `test_forced_rejection_*`; the app's audit view strips draft text; browser check 2026-10-06. | VERIFIED offline test | 0 rejected drafts shown |
| 7 | Skills and playbooks can add rules and checks. They can never remove the floor, the disclaimer, or a banned pattern. The loader refuses the attempt. | `code/nury/skills.py`, `code/nury/playbook.py`; tests `test_bad_skill_is_refused`, `test_playbook_cannot_drop_disclaimer_floor`; proof 4 below. | VERIFIED offline test | 4 kinds of bad skill refused (English override, Spanish override, removed check, unknown check), plus a playbook with a stripped disclaimer |
| 8 | Every output carries the disclaimer, and it says Nury is an AI assistant, not a lawyer, doctor, pastor, counselor, or therapist. | `playbooks/*/playbook.json`; the loader refuses a playbook whose disclaimer drops this wording; full-run tests check each stage. | VERIFIED offline test | 5 of 5 stages carry it, in both languages |
| 9 | Nothing Nury shows can contain an invented link, phone number, bare web address, or email. Each must come from the vetted sources, the approved earlier text, or (for emails) the intake. | `guardrails.url_reasons`, `phone_reasons`, `email_reasons`; tests `BareDomains` (3), `Emails` (2), `test_floor_blocks_unvetted_link_phone_and_pastor_byline`. A real gap (bare domains passed) was found on 2026-10-07 and fixed; it is logged in `evaluations/FAILURE_LOG.md`. | VERIFIED offline test | 4 kinds of contact detail checked, in both playbooks |

## 3. Playbooks as data

| # | Claim | Evidence | Status | The number |
|---|---|---|---|---|
| 10 | A new crisis is a folder, not engine code. A second crisis built in a temporary folder ran on the unchanged engine; the real hospital playbook runs on the same loop and the same floor. | `code/playbooks/<id>/`; test `test_second_playbook_zero_engine_changes`; `test_hospital_has_skills_and_no_immigration_words` (hospital prompts, disclaimer, and output contain no immigration wording). Precision: the run loop has one crisis word, the default playbook id "detention", and one opt-in check (`no_agency_names`) lists immigration agencies; hospital does not use it. | VERIFIED offline test | 2 live crises, 2 coming-soon cards, 0 immigration words in a hospital run |
| 11 | A playbook whose vetted sources are not all approved does not run. Juan approved 5 of the 6 hospital sources and rejected the weak one, which is dropped. | `code/playbooks/hospital/sources/approvals.json`; tests `test_pending_sources_cannot_run_and_list_as_soon`, `test_rejected_source_is_removed`. | VERIFIED offline test | 5 approved, 1 rejected, 0 unapproved sources shipped |
| 12 | Hospital scored 7 of 8 on the first run; the one failure (vague intake) was fixed and re-run. | `evaluations/results/hospital/scorecard.md` (interim, before the fix); PROMPT_NOTES problem 13. The final number comes from the final scored run. | PENDING final scorecard | not quoted yet |

## 4. Contacts: official list and church network

| # | Claim | Evidence | Status | The number |
|---|---|---|---|---|
| 13 | Nury lists Department of Justice recognized providers only as Juan approved them, never calls one free, always says "listed does not mean recommended", and never names a held entry. | `code/playbooks/detention/sources/official_list.json` built from `OFFICIAL_LIST_DRAFT.json` and `approvals.json` by `code/nury/officiallist.py`; tests in `code/tests/test_official.py` (10); live check a. | VERIFIED offline test; VERIFIED live (1 pipeline, coarse check) | 28 entries read, 21 approved, 7 held (names only); 18 providers listed; 0 held phone numbers in the file |
| 14 | The pastor's own church network is listed first, labeled the church's own, matched by state, language and kind, never ranked, and the pastor's private note is never sent to a model. | `code/nury/network.py`; tests `test_network.py` (12) and `test_network_api.py` (2); live checks a, b, d. Demo contacts are fictional and load only when `NURY_DEMO_NETWORK=1`. | VERIFIED offline test; VERIFIED live (3 pipelines, coarse check) | 4 matching fields, 6 contact kinds, 0 real contacts in the repo |
| 15 | The ABA detention entry shows the email route for a family, never the toll-free number, which the DOJ page says is for people held at military facilities. | `official_list.json`; `officiallist.py` comment quotes the page; PROMPT_NOTES problem 16; test `test_aba_entry_uses_the_family_route_not_the_military_hotline`. | VERIFIED offline test | 1 entry corrected |

## 5. Privacy

| # | Claim | Evidence | Status | The number |
|---|---|---|---|---|
| 16 | No direct identifier reaches a model. Names the pastor protected, phones, emails, street addresses, dates, A-numbers, case numbers and ID numbers become tokens before the request leaves, and become real again when the reply returns. | `code/nury/privacy.py`; the leak test `code/tests/test_privacy.py` captures the exact request bodies at the HTTP edge for all five stages of both playbooks, including a rejected draft and a pastor edit that adds a new name. | VERIFIED offline test | 6 bodies x 15 canary values = 90 checks per playbook, 0 found (proof 3) |
| 17 | The same holds on the real endpoint, with a small cost. On three live scenarios, privacy on sent no names and added about 4 to 5 percent input tokens, with no broken sentences. | PROMPT_NOTES, section "Privacy: what the model sees" (privacy off vs on, scenarios 01, 18, h01, real request bodies). Three pipelines, not a rate. | VERIFIED live | +4 to 5% input tokens; latency 37 vs 38 s, 37 vs 37 s, 48 vs 53 s |
| 18 | A token the model mangles is repaired. A token it invents makes the client ask again (at most twice); if it still fails, the pastor sees a visible gap, never a stray token. | Tests `test_mangled_tokens_are_repaired`, `test_unknown_token_*`. | VERIFIED offline test | max 2 extra calls |
| 19 | Honest limit: this removes direct identifiers only. Context can still hint at who a person is, and a name the pastor did not protect is not removed. | PROMPT_NOTES, "Known limitations". | VERIFIED (stated limit) | not a claim to sell; say it |

## 6. Skills and the case file

| # | Claim | Evidence | Status | The number |
|---|---|---|---|---|
| 20 | Two versioned skills (voice, grounding) are added to stage prompts by name, with no extra model call, recorded in the audit log, and can be switched off to compare. | `code/skills/`, `code/nury/skills.py`; tests `test_skill_applied_is_audited_and_in_metrics`, `test_skills_switch_off_per_call_and_env`; live runs on 2026-10-06 and 07. | VERIFIED offline test; VERIFIED live | 2 skills, 0 extra model calls |
| 21 | Skills improve the wording. | The before and after run (`evaluations/skills_ab.py`) has not been run. | PENDING final scorecard | not quoted yet |
| 22 | After approval, a case is saved as a local folder of linked pages and a next-steps map, built without a model call from approved text only. It refuses to save if any stage is not approved, if a rejected draft or a key would be written. | `code/nury/casefile.py`; `code/tests/test_casefile.py` (9 tests); two real runs saved on 2026-10-07. | VERIFIED offline test; VERIFIED live | 14 files per case with privacy; 0 rejected-draft strings in the folder or its zip |
| 23 | The next-steps map shows steps and questions only: four lanes (tonight, this week, questions still open, who to call), no outcomes, readable at 390 px. | `nextsteps_svg` in `casefile.py`; tests `test_map_is_svg_390_*`; agent-browser check at 390 and 1280 px. | VERIFIED offline test | 4 lanes |
| 24 | A saved case can be revised: v2 sits beside v1, which is never touched. | `code/app/server.py` (revision), `evaluations/casefile_check.py`. Its live run is on the owed list. | PENDING final scorecard | not quoted yet |

## 6b. Evaluation: four layers

| # | Claim | Evidence | Status | The number |
|---|---|---|---|---|
| 25 | Four layers judge every run: deterministic judges (no AI), Jev typed judges on the full trajectory, a cross-vendor red-team panel through Gloo, and human review. Any finding or disagreement goes to a person. | `evaluations/judges/deterministic.py` (7 judges), `jev_judges.py` (9 yes/no, 5 score, 1 choice question = 15, accept at 0.80 and fail at 0.20), `redteam_panel.py` (3 reviewers), `make_review_canvas.py`. | VERIFIED (built and run); results PENDING final scorecard | 7 + 15 + 3 reviewers; 54 scenarios (28 core, 18 attacker, 5 case file, 3 network) |
| 26 | The Jev judge separates unsafe from safe text on real Nury output. Unsafe text scored 0.89 to 0.98; safe text scored 0.02 to 0.24, on ten checks. | `evaluations/validation/JUDGE_VALIDATION.md`. Unsafe cases are synthetic paragraphs appended to real output; ten points, not a calibration study. | VERIFIED live | 0.89 to 0.98 vs 0.02 to 0.24 |
| 27 | The first fix for a judge confusion failed, and we said so. Telling the judge to ignore rejected drafts dropped unsafe scores to 0.29 to 0.78, below the 0.80 bar, so it was rejected. The adopted fix removes rejected text from what the judge reads. | Same file, section "Final judge design". | VERIFIED live | 6 cases fell below 0.80, then 10 of 10 met it |
| 28 | The red-team panel uses three non-Claude reviewers through the same Gloo endpoint. First pass: two reviewers caught all 8 injected problems but also flagged safe text, so they are advisory; the third failed on a parser bug. No reviewer invented a quote. | `evaluations/validation/PANEL_VALIDATION.md` ($0.58 first pass; the raw file was overwritten, the analysis was kept). Second validation pass and the final run have not happened. | VERIFIED live (first pass only); final PENDING | 8 of 8 caught by 2 reviewers; 13 of 16 gemini calls failed on a parser, not the model |
| 32 | The Jev decision API is used at evaluation time only. The product code never imports or calls Jev, the red-team panel, or the attacker intakes. (The only mention is the case-file guard naming `JEV_API_KEY` so it can refuse to save it.) | Test `test_the_product_never_uses_jev_the_panel_or_the_attacker` scans `code/nury` and `code/app`. Disclosed as prior technology in the submission text. | VERIFIED offline test | 0 imports or calls in the product |
| 33 | The product has 91 offline tests (about half a second) and the evaluation harness has 39 more, 130 in all, plus 54 scenarios. | `cd code && python3 -m unittest discover -s tests`; `cd evaluations && python3 -m pytest tests -q`. The count grows; re-run before quoting. | VERIFIED offline test | 91 + 39 = 130 |
| 34 | The pastor's voice may invite but not promise. The pastoral draft is rejected if it says anyone is searching, preparing, sending, calling back or visiting, or uses "soon", unless the pastor wrote that action in the intake. Found by the Jev tone score in the final scored run, fixed, and re-checked live. | `code/nury/checks.py` `no_unauthorized_promises`; `playbooks/*/prompts/pastoral.txt`; tests class `Promises` (4 tests); PROMPT_NOTES problem 17. Live: detention 01 and 14 and hospital h01, all five stages, pastoral messages read by hand: invitations only. | VERIFIED offline test; VERIFIED live (3 pipelines) | 3 of 3 live messages free of promises; before: promises like "estamos buscando un abogado" |
| 29 | Pass rate, escalation rate, and the scorecard for detention 20 and hospital 8 with privacy on. | `evaluations/results/` holds interim runs from older code (detention: 9 judge passes, 11 awaiting human review, 0 failed; hospital: 7 of 8). Not final. | PENDING final scorecard | not quoted yet |

## 7. Cost and speed

| # | Claim | Evidence | Status | The number |
|---|---|---|---|---|
| 30 | A full five-stage package, with privacy, skills, church network and official list on, takes under a minute and costs about nine cents. | `evaluations/results/live_checks_slot_b.md`: detention 50, 56 and 56 s at $0.086, $0.090, $0.094; hospital 52 s at $0.081; $3 and $15 per 1M tokens. Four pipelines, one each. | VERIFIED live | 50 to 56 s; $0.08 to $0.09 per package |
| 31 | Earlier interim means over the full scenario sets: detention 32.8 s and $0.054 per run (20 scenarios), hospital 44.1 s and $0.076 per run (8). | `evaluations/results/scorecard.md`, `evaluations/results/hospital/scorecard.md`. Older code, and the means include short scenarios. | PENDING final scorecard | not quoted yet |

## What we do not claim

- A pass rate, until the final scorecard is filled.
- That skills improve the Spanish. The before and after has not run, and our word checks cannot measure naturalness.
- That the model refuses to give advice on its own. In our tests it mostly did, so we force failures with fault injection to prove the loop; say that plainly.
- Anything about states other than Colorado for the official list, or about sudden death and house fire (cards only).
- That privacy is anonymization. It removes direct identifiers.
- That the live network and official-list checks are a rate. They were one pipeline each, with coarse checks.

## Five proofs to show on screen (3 seconds each)

Run `cd code && python3 tools/show_proofs.py` (offline, no key, about 2 seconds) or one at a time with `python3 tools/show_proofs.py 3`. Each prints a heading and a few short lines computed from the real code.

1. **A rejected draft never reaches the pastor.** Shows the check failing with `banned_phrase`, the audit line `draft_rejected ... visible_to_pastor=False`, the second try passing, and what the pastor sees. Backs claims 4 and 6.
2. **Gloo sees tokens, not names.** Shows the typed sentence, the same sentence as Gloo receives it (`[PERSON_3] called from [PHONE_1] ...`), and the local token map. Backs claim 16.
3. **Leak test.** `6 request bodies captured x 15 canary values = 90 checks, found: 0`, for detention and for hospital. Backs claim 16.
4. **The loader refuses.** A skill that says "ignore the disclaimer" is refused with its reason; a playbook with a stripped disclaimer is refused. Backs claim 7.
5. **A held entry is never named.** A draft that names a held DOJ entry is rejected three times and never reaches the pastor. Backs claims 13 and 6.

On the app itself, three more 3-second shots that already exist: the status strip "Draft rejected by guardrail. Regenerating (2 of 3)." then "Passed"; the Audit log section after a run; the case folder with `privacy-map.json` next to `index.md`.
