# Nury architecture: an AI crisis response agent that runs playbooks

Rewritten 2026-10-07 by hack-ninja for hack-sensei (owner). Sources: `documents/FEATURES.md`, `documents/TECH_CLAIMS.md`, BUILD_LOG entries 1 to 102, and the code at commit `e39a6b5` plus the uncommitted working tree. Where a fact was not in FEATURES or TECH_CLAIMS, it was read from the code and the path is named. This is the single current architecture document. Decisions are by Juan and hack-sensei; the engine is by hack-jedi; the app and the eval harness are by hack-artisans.

## Status words

- **BUILT, live verified**: ran against the real endpoint; the result is in a file or BUILD_LOG.
- **BUILT, offline tested**: a test or a browser check without a model call proves it.
- **IN PROGRESS**: code or files exist but the item is not finished, not committed, or not checked live. It is not claimed anywhere.
- **PLANNED**: written down, no code.
- **NOT BUILT**: nothing exists, or we left it out on purpose.

"Live verified" means it ran, not that it scored well. No scorecard number is quoted here. The final scored runs are pending (see Milestones).

## 1. Idea

Nury is **An AI Crisis Response Agent.** It helps churches, and the pastors who answer the call, respond to a family in crisis. The pastor picks the crisis. Nury drafts five stages. The pastor approves, edits or stops after every stage. Nothing reaches the family except through the pastor. Nury is not a pastor, counselor, therapist, doctor or lawyer, and never says so.

Nury is one engine that runs crisis playbooks. A **crisis is data, not code.** A new crisis is a new playbook folder. The engine does not change. Detention is playbook 1 and the flagship demo. Hospital is playbook 2.

The film's pastor at 2:07 AM is a story character. He is not a market limit.

## 2. Layers

| # | Layer | Where | What it does | Status |
|---|---|---|---|---|
| 1 | Engine | `code/nury/engine.py`, `stages.py`, `audit.py` | Runs stages in order, chains approved or edited text, runs the correction loop (3 attempts), runs the approval gate, writes the audit log. Knows nothing about any one crisis. | BUILT, live verified |
| 2 | Safety floor | `code/nury/guardrails.py`, `engine.py` | No advice, no outcome prediction, no claim to be a pastor, counselor or lawyer, disclaimer on every output, link and phone allowlist, no send path. A playbook or skill can add checks, never remove these. | BUILT, live verified |
| 3 | Named checks | `code/nury/checks.py` | Plain-code rules on each draft. **20 in the registry.** The scored runs used 14. The other 6 (3 Scripture, 3 from the red-team panel) are offline tested and not part of any scored run yet. The headline stays "14 named checks" until the final scored build. | 14 live verified, 6 offline tested |
| 4 | Jev gate | `code/nury/jev_gate.py` | Jev classifies every draft at run time, after the named checks. See section 3. | **IN PROGRESS** |
| 5 | Privacy | `code/nury/privacy.py` | Tokens instead of identifiers before any outbound request. See section 6. | BUILT, live verified |
| 6 | Playbooks | `code/playbooks/<id>/` | Everything specific to one crisis. See section 7. | BUILT, live verified (2 live) |
| 7 | Skills | `code/skills/`, `nury/skills.py` | `voice` and `grounding` instruction modules added to stage prompts. No extra model call. | BUILT, live verified |
| 8 | App | `code/app/` | The pastor's screens. See section 10. | Mixed, see section 10 |
| 9 | Evals | `evaluations/` | Test-time layers. See section 4. | BUILT, live verified (final runs pending) |

## 3. The run-time pipeline

What happens when a pastor runs a crisis, in order. The writer is **Claude Sonnet 4.6 through Gloo AI Studio**. There is **no second LLM reviewer** in the product (Juan's decision, BUILD_LOG 102).

1. **Intake.** The pastor types what the family said and picks the family's language (Spanish or English). `code/app/static/index.html` (intake view). BUILT, live verified.
2. **Protected names.** Nury proposes names to hide. The pastor ticks, adds, unticks. Phones, emails, addresses, dates and ID numbers are always protected. `privacy.propose_terms`. BUILT, live verified.
3. **For each stage** (detention: triage, rights, attorney resources, checklist, pastoral message; hospital: triage, information, resources, checklist, pastoral message):
   1. **Build the prompt.** Floor rules, skill text, the playbook's stage prompt, the vetted sources, and the earlier approved or edited text. `engine.py`, `playbook.py`, `skills.py`.
   2. **Tokenize.** The privacy client swaps protected values for tokens. The token map stays in the app.
   3. **Write.** One call to the Gloo guarded Responses endpoint, model `gloo-anthropic-claude-sonnet-4.6`. A full package is 5 Gloo calls (TECH_CLAIMS 1). A Gloo HTTP 403 counts as a failed try.
   4. **Detokenize.** Tokens become the real names again. A mangled token is repaired; an unknown token makes Nury ask again, twice at most.
   5. **Named checks.** The stage's checks plus the floor run in plain code. Any violation sends the draft back.
   6. **Jev gate.** *IN PROGRESS.* If the draft passed step 5, one batched call to the Jev decision API (from TypeSafe) asks the stage's yes/no questions. Each question is one where "yes" is the unsafe answer. At 0.50 or more, the draft is rejected and the reason category is `jev_<question>`. From 0.30 to 0.50 the draft passes and the audit logs "uncertain". Below 0.30 it passes.
   7. **Loop.** A rejected draft is regenerated. The model gets the reasons, never the rejected text. Three attempts in all. After the third failure the stage escalates with no draft shown and "I'll handle this manually." The pastor never sees an unsafe draft.
   8. **Scripture** (pastoral stage only). The model returns a verse id from an approved list and at most two short why-lines. The app inserts the exact verse text. See section 8.
   9. **Approval gate.** The pastor sees only the draft that passed. Approve, Edit or Stop. Stop ends the run with "I'll handle this manually." Names the pastor adds in an edit are protected before the next stage.
4. **Package.** Every approved stage, with Copy all and Download. "Nury never sends anything. You do."
5. **Save as a case** (optional). See section 9.

### The Jev gate: what exists, what does not

| Item | Status | Evidence |
|---|---|---|
| Gate code: one batched call per draft per attempt, reject at 0.50, uncertain band logged, 8 s timeout | BUILT, offline tested | `code/nury/jev_gate.py`, commit `98fc221`; engine hook at `engine.py` line 268 |
| 13 gate tests, no network | BUILT, offline tested | `code/tests/test_jev_gate.py` (13 pass, run 2026-10-07 with no keys set) |
| Jev request carries tokens, never names or the map | BUILT, offline tested | `code/tests/test_privacy.py` (`test_the_jev_gate_requests_carry_tokens_never_names_or_the_map`) |
| The question wording equals the wording validated for the eval harness | BUILT, offline tested | `test_jev_gate.py` compares the two copies |
| Line-at-0.50 smoke test on real drafts | BUILT, live verified (small) | `evaluations/validation/JEV_GATE_VALIDATION.md` (untracked file): 20 question and draft pairs from two scenarios, safe 0.02 to 0.42, unsafe 0.74 to 0.99, none missed, no false reject, Jev median 156 ms per call (30 calls) |
| **Full live run with the gate on, end to end** | **NOT DONE** | The gate stays IN PROGRESS until a live pipeline passes with `provider` and gate events in the audit log. Then it becomes BUILT, live verified. |
| Gate on by default | Only when `JEV_API_KEY` is set | `jev_gate.enabled`; override with `NURY_JEV_GATE=on|off` |

**Fails open.** With no key, a timeout, an error or a bad answer, the draft goes on to the pastor on the strength of the named checks and the floor. The audit logs decision "unavailable" with the reason, and later stages of the same run skip the gate. The product never blocks on Jev.

**Known soft spot** (from the smoke test): the `assumes_facts` and `promises_action` questions score safe drafts at 0.26 to 0.42. Four of 20 safe pairs landed in the uncertain band. The highest, 0.42, is 0.08 from a false reject. A false reject costs an attempt, not safety. Three in a row escalate the stage. Stability across repeated calls was not measured for the gate.

## 4. Test-time layers

These judge the system before pastors use it. They never run inside a pastor's session, except that Jev now also has the run-time role in section 3.

| Layer | What it is | Status | Evidence |
|---|---|---|---|
| Deterministic judges | Seven plain-code judges over whole runs: banned phrases, disclaimers, allowlist, language, workflow, completeness, stock phrases. | BUILT, live verified | `evaluations/judges/deterministic.py` |
| Jev typed judges | Fifteen typed questions (nine yes or no, five scores, one choice) read the whole run. Accept at 0.80, fail at 0.20, the middle goes to a person. Jev is the Jev decision API from TypeSafe. We use it; we did not build it. | BUILT, live verified | `evaluations/judges/jev_judges.py`; TECH_CLAIMS 36 to 39 |
| Judge validation | On ten checks, unsafe text scored 0.89 to 0.98 and safe text 0.02 to 0.24. Five stored runs rejudged an hour later moved 0.03 or less. | BUILT, live verified | `evaluations/validation/JUDGE_VALIDATION.md`; TECH_CLAIMS 37, 38 |
| Red-team panel | Three models from three other makers through Gloo AI Studio: OpenAI GPT-5.4, Google Gemini 3.1 Pro, Meta Llama 4 Maverick. None is Claude, on purpose. They quote sentences that give advice, predict outcomes or invent facts. **Advisory only**: first pass caught 8 of 8 injected problems and also flagged safe text, so they cannot gate anything. It is a pre-release audit, and it found real defects (the garbled "call Maria" sentence, unsourced triage lines, a hospital checklist line). | BUILT, live verified (first validation). Run on the final sets: pending | `evaluations/judges/redteam_panel.py`; `evaluations/validation/PANEL_VALIDATION.md`; `evaluations/LIVE_CHECKS_OWED.md` step 11 |
| Human review | A canvas for Juan, grouped by question, showing only what the pastor saw. | BUILT, live verified | `evaluations/make_review_canvas.py` |
| Attacker intakes | 18 hostile intakes written by a non-Claude model and edited by a person. | BUILT, not yet run | `evaluations/scenarios_attacker/` |
| Scenario sets | 20 detention and 8 hospital scenarios, plus 5 case-file and 3 network scenarios. | BUILT, live verified (final scored set pending) | `evaluations/scenarios*/`, `evaluations/results/` |

**What changed with the run-time gate.** The Jev typed judges are **no longer independent** of the run-time gate. The gate asks Jev the same validated questions on every draft, so a draft that reaches a Jev judge has already passed Jev's gate on those questions. Agreement between the two is no longer fresh evidence. The independent evidence is the deterministic judges, the red team (different vendors), human review and the attacker intakes. Any scorecard line that rests on Jev must say this.

## 5. Providers, keys and outbound calls

| Provider | When | What leaves the app | Status |
|---|---|---|---|
| **Gloo AI Studio** (guarded Responses endpoint, `platform.ai.gloo.com/ai/v2/guarded`) | Run time and test time | Tokenized prompts. Test time also sends what the pastor saw to the red-team models, through the same endpoint. | BUILT, live verified |
| **Jev decision API from TypeSafe** (`api.typesafe.ai`) | Run time (the gate) and test time (the typed judges) | Run time: the tokenized draft, a tokenized context and the vetted sources for that stage. Never a real name, never the token map. Test time: synthetic families only. | Test time: live verified. Run time: **IN PROGRESS** |
| **YouVersion Platform** | Run time, optional, only when `YVP_APP_KEY` and the Bible ids are set | A key header, a version id and a passage id. No case data. | BUILT, live verified |

Nothing else goes out. There is no mail, SMS, chat or share path. `NoSendPath` in `code/tests/test_core.py` scans `code/nury` and `code/app` for mail, FTP, socket, browser and SMS libraries and finds none. It proves nothing can reach the family. It does not make the three calls above disappear, and the docs say all three.

**Not reviewed:** TypeSafe's data retention and terms for the run-time use. The text sent is tokenized, but the review has not been done. Read the terms before any real church uses the gate.

**Keys.** `GLOO_API_KEY`, `JEV_API_KEY`, `YVP_APP_KEY`, `YVP_BIBLE_ES`, `YVP_BIBLE_EN` come from the environment or the gitignored repo-root `.env`. They are never in a tracked file, a commit, a log or a message (`code/nury/gloo_client.py` reads them and never logs them).

**Switches** (all read from the environment): `NURY_PRIVACY` (on), `NURY_SKILLS` (on), `NURY_JEV_GATE` (on only with a key), `NURY_DEMO_NETWORK`, `NURY_NETWORK_DIR`, `NURY_FORCE_REJECTION` (shows the reject-and-regenerate beat on demand), and the test-only `NURY_TEST_ESCALATE` and `NURY_ALLOW_PENDING`. Prices come from `NURY_PRICE_IN` and `NURY_PRICE_OUT`.

**Cost and time.** A full package takes 50 to 56 seconds and costs about nine cents (four live pipelines, $3 and $15 per 1M tokens; TECH_CLAIMS 30, `evaluations/results/live_checks_slot_b.md`). That was measured before the gate. The gate adds one Jev call per draft; its effect on a full run is not measured yet.

## 6. Privacy

Nury sends no direct identifier to any model or classifier. A **PrivacyClient** wraps the Gloo client, and the Jev gate uses the same pseudonymizer.

- **Outbound.** Protected names, phones, emails, street addresses, dates, A-numbers, case numbers and ID numbers become tokens (`[PERSON_1]`, `[PHONE_1]`). BUILT, live verified (`nury/privacy.py`, live A/B in BUILD_LOG 38).
- **The map never leaves.** It lives in memory for the run and in the saved case (`privacy-map.json`) on the server that runs the app.
- **Inbound.** The reply is detokenized so the pastor sees real names.
- **Detection.** Rules for phones, emails, IDs, dates and addresses. For names, the pastor confirms the protected list.
- **Leak test.** Captured request bodies are searched for canary names and numbers: 90 checks per playbook, none found (TECH_CLAIMS 16; `code/tests/test_privacy.py`). The scored runs also check every string sent to the model. The test is extended to the Jev requests (offline tested). BUILT, live verified for Gloo; offline tested for Jev.
- **Honest limit.** Tokens remove direct identifiers. Context ("14 years", "his workplace") can still hint at who a person is.
- **Saved by the app, not uploaded.** Cases, the church network and the token map are plain files in `cases/` and `network/` on the server that runs the app. They are gitignored and uploaded to no one. **There is no sign-in, no separation between churches and no encryption at rest.** Demo and evals use synthetic families only. The consent note says this on screen (section 10).

## 7. Playbooks

```
code/playbooks/<crisis_id>/
  playbook.json     id, title, status (live or soon), languages, disclaimer (EN, ES), extra banned patterns
  stages.json       ordered stages: id, prompt file, sources, extra checks by name, Jev questions ("jev"), output language
  prompts/          one prompt file per stage (verbatim prompts are judged evidence)
  sources/          vetted JSON files; the only facts a stage may use; approvals.json
  outcomes.json     package_complete, stopped_by_pastor, escalated, blocked
```

The loader (`code/nury/playbook.py`) validates a playbook and refuses an unsafe one: a weaker disclaimer, a skill that overrides the floor, or a source Juan has not approved. Test: `test_second_playbook_zero_engine_changes`, `test_playbook_cannot_drop_disclaimer_floor`. BUILT, offline tested. Stage paths (a stage runs, skips or swaps its prompt on triage fields) are built and unused by the shipped playbooks.

| Playbook | Status | Evidence |
|---|---|---|
| `detention`: an immigration detention or raid. Vetted rights file, national hotlines, the church network, the Department of Justice list of recognized legal service providers (18 approved providers, Colorado only). | BUILT, live verified | `code/playbooks/detention/`; 20 scenarios |
| `hospital`: a family member in the ER or ICU. Information only, no medical advice, diagnosis or prognosis; 12 extra banned patterns in EN and ES. Five public sources approved by Juan; one weak source rejected. | BUILT, live verified | `code/playbooks/hospital/`; `sources/approvals.json`; 8 scenarios |
| `sudden-death` and `house-fire`: labeled "coming soon" cards. They have no stages. The engine refuses to run them. Nothing is claimed about them. | BUILT, offline tested (cards only) | `code/playbooks/sudden-death/`, `house-fire/` |

`GET /api/playbooks` returns id, title, description and status. The UI never hardcodes a crisis.

## 8. Scripture

Only in the pastoral message. The model never writes Scripture (TECH_CLAIMS 44 to 49).

- **The model may** pick one verse id from the approved list for this case and write at most two short why-lines that speak to the family. If no verse fits, no verse is added.
- **The model may not** write a Bible reference or a quotation, name a verse outside the list, or say what God will do, why this happened, or what God knows, sees, feels, wants or intends beyond what the chosen verse says. Three checks enforce this: `no_model_scripture`, `no_providence_claims`, `verse_block_verbatim`. A failing draft is rejected and regenerated like any other. BUILT, offline tested (checks); the flow BUILT, live verified (8 runs on 2026-10-07, BUILD_LOG 96).
- **The app inserts** the exact verse text, reference and translation name from the provider, with the provider's copyright line. Nury trims lines that hold an email address and a repeated second copyright block; author, year and licence name stay. That trimming is Nury's own rule, not the provider's. BUILT, live verified.
- **Verified bank (default and fallback).** 12 verses (10 for detention, 12 for hospital), Reina-Valera 1909 and World English Bible, both public domain, with source URL and licence recorded. Juan approved all 12 (BUILD_LOG 93). BUILT, offline tested. `playbooks/*/sources/scripture.json`, `approvals.json`.
- **YouVersion provider (optional).** On only when `YVP_APP_KEY` and both Bible ids are set: Versión Biblia Libre (id 3291) for Spanish, Berean Standard Bible (id 3034) for English. On any failure (error, 429, version unavailable, no attribution, a verse over the 52-word cap) Nury uses the bank and logs `provider=bank` with the reason. Live: 8 verses fetched, 1 fallback (VBL Romans 8:38-39 is over the cap). BUILT, live verified. `nury/scripture_providers.py`.
- **Not claimed.** NVI and RVR1960 are not available to our app key. Nothing licensed is used. Nothing is cached, because no cache rule was found in the docs. Juan should read the Platform terms before the key runs on a public server.
- **Verse swap at the gate.** The engine can swap in any other approved verse (`scripture.swap_verse`, `list_verses`). There is no selector in the app yet. **PLANNED** (the selector); the engine function is offline tested.
- **The church's own verses.** `network/scripture.json`, with exact text, source URL, licence and translation name. The loader refuses a verse without them. There is no screen for it. BUILT, offline tested.

## 9. Case file, revision, network and official list

| Piece | What it does | Status | Evidence |
|---|---|---|---|
| Case file | One tap saves the approved package as linked markdown pages (index, one page per stage, people, documents, timeline, log). Approved content only. A rejected draft never enters a case. Built with no model call. | BUILT, live verified | `nury/casefile.py`; BUILD_LOG 56 |
| Next-steps map | One SVG: tonight, this week, questions still open, who to call. Steps and questions, never outcomes. | BUILT, live verified | `casefile.nextsteps_svg` |
| Revision v1 to v2 and Compare | The pastor records what happened. Nury reruns from triage with the same gates. v1 stays byte-identical; v2 is saved beside it. | BUILT, live verified | `evaluations/casefile_check.py` |
| Needs follow-up flag | A flag only, no reminder, no date, saved in `case.json`. The endpoint `POST /api/case/<id>/followup` is built. The button in the app is in the working tree, not committed. | Endpoint BUILT, offline tested. Button **IN PROGRESS** | `casefile.set_follow_up`, `server.py`; `index.html` (`case-follow`, uncommitted) |
| Church network | The pastor's own contacts, matched by state, language and kind, listed first, labeled the church's own, never ranked or endorsed. The pastor's private note never reaches a model. | BUILT, live verified | `nury/network.py`, `tests/test_network.py` |
| Official list | The DOJ list for Colorado, with "listed does not mean recommended". Seven held entries are never shown. Other states: none. | BUILT, live verified | `nury/officiallist.py`, `playbooks/detention/sources/official_list.json` |

Rule: Nury lists only contacts the pastor vetted, labeled as the church's own, plus official vetted lists. It never endorses anyone. There is no open web at run time.

## 10. The app

`code/app/server.py` serves a single-page web app and a small JSON API. English UI, family output in Spanish or English.

| Item | Status | Evidence |
|---|---|---|
| Crisis selector: live cards for detention and hospital, muted cards for the two coming-soon crises | BUILT, live verified | `index.html`, `GET /api/playbooks` |
| Intake, protected names, pipeline with progress and rejection strip, halt card, package view, audit view (reason categories only, never a rejected draft) | BUILT, live verified | `index.html`; BUILD_LOG 22, 56 |
| Cases: save, open, read, export a zip | BUILT, live verified | `casefile.list_cases`, `export_zip` |
| Our network screen (`/network`): add, edit, tag, delete, import, export; "Fictional demo contacts" banner in demo mode | BUILT, offline tested | `code/app/static/network.html`, `network_api.py`, `tests/test_network_api.py` |
| Consent note on the intake screen, at the top of a saved case and in the About sheet: saved with the names you typed, no sign-in yet, nothing sent to the family, share only what the family agreed to | BUILT, offline tested | `presentation/CONSENT_NOTE.md`; `data-consent` in `index.html` |
| Home with "Continue where you left off" and Cases, and a crisis detail page per crisis | **IN PROGRESS** (part committed, part in the working tree) | `index.html` (`v-home`, `v-cases`, `v-crisis`), `code/app/crisis_detail.json` |
| Chooser: "A family needs help" (modal on laptop, bottom sheet on phone); a primary button never silently scrolls | **IN PROGRESS** (working tree only) | `index.html` (`chooser`); BUILD_LOG 97 |
| One shared shell on every page (logo, brand line, Home, Cases, Our network, Day/Night, "How this was made", phone tab bar) | **IN PROGRESS** (`shell.js`, `shell.css`, `icons.svg` are untracked) | BUILD_LOG 95; `evaluations/browser/app_ui_test.sh` (being updated) |
| Day and Night toggle, Night by default, remembered | BUILT, offline tested (commit `52c7346`); moving into the shell | `shell.js` |
| About sheet with a clear block for the writer, the red team and Jev | **IN PROGRESS** | BUILD_LOG 98 |
| Accounts, sign-in, roles, shared cases, encryption at rest | **NOT BUILT** | `server.py` has no authentication |

Brand: the lantern mark with the "An AI Crisis Response Agent" lockup (`branding/`). The mobile minimum for the lockup is 260 px wide.

## 11. Skills

A skill is a small versioned instruction module (plain text, not a Claude Code skill) that a stage includes by name. `code/skills/<name>/SKILL.md`, with optional `checks.json`; a stage lists `"skills": [...]`.

- **Safety floor wins.** The loader refuses a skill that tries to override it. The audit logs a `skill_applied` event each time.
- `voice`: plain words, no stock AI phrases, natural Spanish, on the pastoral and checklist stages. BUILT, live verified.
- `grounding`: every line comes from the vetted points or is a plain question for the expert, on the checklist and resource stages. BUILT, live verified.
- A switch turns skills off for a before and after run. BUILT, offline tested.
- **The effect of the skills is not measured.** The before and after runs exist as a script (`evaluations/skills_ab.py`), BUILT, not yet run. Nothing is claimed about whether they help.

## 12. Milestones (MDT)

| # | When | Milestone | What happened |
|---|---|---|---|
| M1 | Oct 6, done | Gloo client live; engine with correction loop and gates | Done. |
| M2 | Oct 6, done | Playbook refactor: detention runs from `code/playbooks/detention/` | Done. Same tests pass. |
| M2b, M2c | Oct 6 to 7, done | Hospital sources approved; hospital playbook runs | Juan approved five sources and rejected one. Hospital ran live, 8 scenarios. |
| M3 | Oct 6 to 7 | Pastor app | Selector, intake, pipeline, package, audit, cases, revision, network built. Home, chooser and shared shell **in progress** (BUILD_LOG 95, 97). |
| M3b | Oct 6 to 7 | Scripture | 12 verses approved (BUILD_LOG 93); YouVersion live end to end (BUILD_LOG 96); last Scripture rule added. |
| M3c | Oct 7 00:12 | Core frozen for scoring | Build `7742e7f` (boundary prompt says "a pastor"). 149 product tests then; **163 pass now** (run 2026-10-07 with no keys set). |
| M3d | Oct 7 00:14 and after | Jev run-time gate (Juan, BUILD_LOG 101) | Approved as the one core change after the freeze. Committed `98fc221`. **Live end-to-end check pending.** |
| M4 | Oct 7 | Scored runs | Earlier scorecards exist in `evaluations/results/`. The final scored set (detention 20, hospital 8), the attacker set (18) and the red-team run on the final sets are owed by hack-artisans. No number is quoted until every review item is decided. |
| M5 | Oct 7 | Description draft; deck | Drafts done by hack-ninja. Real numbers only from the final run. |
| M6 | Oct 7, 15:00 | End-to-end demo with one rejected-and-regenerated draft; harness scores | Open. |
| M7 | Oct 7, 18:00 | Description and 3-minute deck final; Juan reads | Open. |
| M8 | Oct 7, 20:30 | Deck, script, video in Juan's hands | Open. |
| M9 | Oct 7, 21:00 | Submitted. Hard stop. | Open. |
| M10 | Oct 8, 09:00 | 90-second finalist video, only if top 25 | Open. |

## 13. Honest limits: NOT BUILT, and what we do not know

Nothing here may be claimed in the film, the deck or the description.

**Not built, and needed before real churches use Nury on a server:** accounts and sign-in; teams and roles; separation of cases and the church network per church; encryption at rest; backups and sync.

**Not built, other:** more crises than two (sudden death and house fire are cards only); official lists for states other than Colorado; family languages beyond Spanish and English; a UI beyond English; voice input; a printable PDF; an offline mobile app; licensed Bible versions; other traditions' canons; a screen reader test; native-speaker review of the Spanish; any use by a real pastor (every family is synthetic); the case update loop, the possible-paths map and the pastor-triggered "find more" search (all PLANNED, after submission); the verse selector at the gate (PLANNED).

**Not known, and said plainly:**
- The Jev gate has not passed a full live pipeline. Until it does, it is IN PROGRESS and the product's safety rests on the floor and the named checks.
- Jev as a gate was smoke-tested on 20 pairs from two scenarios. It was not calibrated, and its stability across calls was not measured.
- The red team cannot gate: it flags safe text. It is advisory.
- The Jev typed judges are not independent of the gate any more (section 4).
- Jev's retention and terms for run-time use are not reviewed.
- The tone score did not rise after the promises fix; the re-run on the fixed core is pending.
- "14 named checks" is the headline until the final scored build; the registry holds 20.
- The effect of the skills is not measured.

## 14. Rules that stay

Vetted sources only. No open web. No send path. Legal and medical information only, never advice, prediction or strategy. Nury is not a pastor. Humanitarian, never political. An unsafe draft is rejected and regenerated, three tries, then handed to the pastor, and the pastor never sees it. Keys come from the environment only. The submission carries: "Evaluation harness uses the Jev decision API from TypeSafe as typed judges; disclosed as third-party technology per the rules." When the run-time gate is verified live, hack-sensei gives the exact new truth for that line and for "Jev at test time only", which no longer holds.
