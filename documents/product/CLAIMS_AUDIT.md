# Claims audit and consistency audit

Written 2026-10-07 by hack-ninja for hack-sensei (BUILD_LOG 120). Scope: every factual claim in the deck (all 23 slides and notes), the pitch and film scripts, the descriptions, the notes, the Q and A, the documentation page and its sources, the app's own pages, README and CLAUDE.md, checked against `TECH_CLAIMS.md`, `FEATURES.md`, the code, the evaluation files and BUILD_LOG. Read at the repo state after commit `845e107` plus the uncommitted working tree.

**What this audit does not do.** It does not fill the final numbers: the full re-run is not done (see section 6). It does not judge the memorial text (Juan's). It does not re-verify claims that earlier sources already checked and that nothing has changed since (listed in section 5).

## 1. Result in one page

- **2 blockers**: the video source still carries the old, wrong Jev disclosure and the old tagline, and the deck and talk disagree with the app about hospital.
- **10 high findings**: stale or soon-to-be-wrong claims, mostly about to be overtaken by the re-run.
- **Fixed in my own files during this audit: 14 items** (section 7, rows 1 to 12 plus M4 and M5), including one that mattered: the red-team claims in the deck, scripts and documentation described a superseded first pass and said "no reviewer invented a quote", which the newer validation file contradicts.
- **Open for others: none.** Everything the first version listed for others is closed (sections 1b and 1c).
- **Wait for the re-run: H2 and H3**, and 8 numbers or lines in the final fill (section 6).

| Severity | Meaning | Count open |
|---|---|---|
| BLOCKER | Wrong or contradicted if shown in the film, the talk or the submission | 2 |
| HIGH | Stale, or will be wrong after the final run | 7 (3 more fixed since the first version) |
| MEDIUM | True but misleading, or incomplete | 7 |
| LOW | Wording and tidiness | 3 |

## 1b. Update, 2026-10-07 evening (after the first version)

- **H8 fixed** by hack-artisans (`3bd1684`): the documentation page was rebuilt, and the evaluation suite passes (77 tests).
- **H9 fixed** (`1c1e6cc`, `f02e998`): the home list now reads the check count from the registry and names Jev's run-time role.
- **H10 resolved.** The learning-loop wiring is committed (`ca6d9aa`). My five files now say "built and browser-tested with a stub, not live", with capture off by default. The consent sentence (version B) is still held for hack-sensei's written word.
- **Three bugs I reported were fixed by hack-jedi:** a malformed POST body now returns 400 (`23e5288`); `fetch` treats any provider exception as unavailable (`6a5de3d`); `NURY_FORCE_REJECTION` follows the playbook (`6a5de3d`).
- **hack-jedi fact-checked `TECHNICAL_REFERENCE.md`**: about 110 anchors matched. Corrections applied: the test counts (264 product tests at the end of the evening, `test_core` 53, `test_scripture` 41, `test_panel_fixes` 15), the prompt-change note, the ledger wiring, and two items upgraded from "not verified".
- **H1 is sharper.** `GET /api/features` returns `named_checks: 20` (I ran it), and the app's home strip shows "20 named checks", while the deck, the pitch and the tech story still say 14. The deck and the product now disagree on screen. This resolves when hack-sensei gives the number.
- **Still open from the first version:** B1 (video source), B2 (hospital gate), H4 to H7 (the claims register and the prework file), and the decisions in section 10.

## 1c. Update, 2026-10-07 late evening: hack-sensei's answers

hack-sensei accepted the audit (the red-team correction in particular) and answered the five questions (message 01:46):

1. **Hospital gate: open, in writing.** Hospital is a live playbook with its own scorecard. Deck, pitch, film and description may name it as the second live playbook, with its numbers after the re-run. Selector screenshots show both live cards. Done: deck slides 4, 5 and 7, the pitch script, `PROOF_FILL.md`.
2. **Headline check count:** after the re-run, "20 named checks plus the safety floor". The 10 places change then (section 6, row 6). Not done yet, on purpose.
3. **Descriptions:** "when Jev is reachable" added to both; "in the family's language" in the main one only. Recounted twice (wc and a regex): **248** and **250**, both at or under 250. The two-playbooks file is exactly at the limit, so the final results sentence must not be longer than the placeholder sentence it replaces (10 words in the main file's version of it; the file has no room for more).
4. **README:** rewritten (two live playbooks, the pipeline in four lines, how to run it and test it, a map of the documents and the hub, hosting status, privacy, credits, the canonical disclosure line). The registrant line (a personal email and a ticket number) is kept and marked with an HTML comment for Juan to confirm before the repo goes public.
5. **Learning-loop lines:** "built" (done earlier this evening), still "off by default, nothing learned, not used by real pastors".

Also done at hack-sensei's request: `documents/prework/EVAL_DESIGN.md` lines 137 to 138 now carry the canonical line with the note "(corrected 2026-10-07: Jev is third-party)". hack-jedi fixed `TECH_CLAIMS.md` (`36909aa`): rows 26, 28, 33, 40, the header and line 79.

## 2. Blockers

| # | Where | What it says | Why it is wrong | Source | Owner | Status |
|---|---|---|---|---|---|---|
| B1 | `video/remotion/src/Nury.tsx` line 222 (`DISCLOSURE`) | "The evaluation harness uses the Jev decision API (my prior project), disclosed as prior technology per the rules." | Juan did not build Jev, and the canonical line changed twice (BUILD_LOG 98, 111 and CLAUDE.md line 33). This is the on-screen disclosure caption of the film. | CLAUDE.md line 33 | hack-video | **FIXED** by hack-video (2026-10-07): the canonical line, verbatim. |
| B1 | Same film source, other stale text: `Nury.tsx` lines 25 and 49 ("no staff", "Solo pastor. No staff. No lawyer."), 33 and 189 ("The crisis-response agent for solo pastors."), `LookDev.tsx` lines 35 and 61, `video/vo/READ_SHEET.md` lines 15 and 18 (old L8 "Tested with Jev. People review what is unsure." and old L11), `video/STORYBOARD.md` lines 32 and 40 | The old tagline and positioning, and the old L8 and L11 lines | Juan removed "solo pastors" and "no staff" everywhere (BUILD_LOG 99). L8 is now "Jev checks every draft. People decide." and L11 "An AI crisis response agent." | CLAUDE.md line 6; `presentation/ERIC_LINES.md` | hack-video | **FIXED** by hack-video: tagline, persona caption, dictionary sense 2, tech-beat labels, lower thirds. A grep of `video/` for the old wording is empty (I re-ran it). L8 and L11 audio were deleted and will be re-rendered after the final build. |
| B2 | Deck slides 4 and 5, pitch script slide 4, film | The talk says "Detention is the one you saw. Two more cards say coming soon" and hides hospital (gate `hospital`) | The app's chooser shows **hospital as live** plus two coming-soon cards (`GET /api/playbooks`, `index.html`). A selector screenshot in slide 5's slot will show a card the talk does not mention. FEATURES lists hospital as BUILT, live verified (8 scenarios scored). | FEATURES section 4; BUILD_LOG 116 | hack-sensei | **RESOLVED.** hack-sensei opened the hospital gate in writing (2026-10-07 01:46). Slide 4 shows hospital live, slide 7 says two crises run on one engine, the selector screenshot with both live cards is in slide 5. |

## 3. High findings

| # | Where | What it says | What is true now | Evidence | Owner | Status |
|---|---|---|---|---|---|---|
| H1 | Deck slide 6 (`deck_template.html` 180), `index.html` 324 ("14 named checks, 3 tries"), `PITCH_SCRIPT.md` 48, `TECH_STORY.md` 10, 20, 47, `ARCHITECTURE.md` 29 and 264, `HOW_IT_WAS_BUILT.md` 418 | "14 named checks" | The registry holds **20**. The registry holds **20**, and all 20 apply in a full run of the two playbooks: 17 are named in the stage files, the engine forces `no_model_scripture` and calls `verse_block_verbatim` on Scripture stages, and the voice skill adds `no_stock_phrases` (run: I loaded both playbooks and read `engine.all_violations`). TECH_CLAIMS row 4 now says "20 in the registry (the scored runs applied 14)". **I could not reproduce 14 from the code**; hack-jedi needs to say how it was counted. Until then the headline "14 named checks" cannot be supported, and the app itself shows 20. | `checks.REGISTRY` (run: 20 names); BUILD_LOG 116 | hack-sensei to give the number; I fill | **FIXED.** hack-jedi traced "14" to an older build and removed it from TECH_CLAIMS and FEATURES. The deck, the pitch, the tech story, `ARCHITECTURE.md` and `HOW_IT_WAS_BUILT.md` now say "20 named checks plus the safety floor". |
| H2 | Deck slide 8, `FINALIST_SCRIPT.md` 24 and 40, `ERIC_LINES.md` 28, `TREATMENTS.md`, `TECH_STORY.md` 8, 31, 60, 71 | "A full package: 50 to 56 s, about 9 cents" | It came from four live pipelines before the Jev gate (TC 30). The scored run on `c317050` measured detention 41 s and $0.072 per run, hospital 50 s and $0.087. "Under a minute" is still true; "50 to 56 s" is not the scored mean. | `evaluations/results/scorecard.md`; `hospital/scorecard.md` | I fill from the final scorecards | **WAITS** |
| H3 | `description.txt` 15 and `description_two_playbooks.txt` 15, `PITCH_SCRIPT.md` 61 (fallback), `TECH_STORY.md` 76, `PROOF_FILL.md` 9 | "We tested 20 hand-built scenarios" and "twenty scenarios and scored each stage" | The sets are 20 detention, 8 hospital and 18 hostile intakes (46). The hostile intakes were written by a non-Claude model and edited by a person, so "hand-built" is loose. Scenarios are scored per run, not per stage. | `evaluations/scenarios*/` (run: counts) | I fill | **WAITS** |
| H4 | `TECH_CLAIMS.md` rows 28 and 40 | "First pass: two reviewers caught all 8 ... the third failed on a parser bug. No reviewer invented a quote." | **Superseded.** The second validation pass: all three caught 8 of 8; gpt-5.4 flagged 8 of 8 safe reviews (10.8 findings each), gemini 7 of 8 (1.5), llama 8 of 8 (3.1). Llama quoted text that is not in the draft once in validation and four times in the run on 28 scenarios. A run on the 28 final scenarios exists (55 corroborated findings), on core `00fe7b1`. | `evaluations/validation/PANEL_VALIDATION.md` | hack-jedi | **FIXED** by hack-jedi (`36909aa`): rows 26, 28 and 40 now use the second pass. Also fixed in my files. |
| H5 | `TECH_CLAIMS.md` header and row 33 | "91 tests pass today; the evaluation harness adds 40 more" | 257 product tests when the audit started, 264 by the end of the evening (run), and 75 evaluation tests (74 passed and 1 failed because the committed documentation page was stale; 77 pass after the rebuild). | `code/test.sh`; `pytest evaluations/tests` | hack-jedi | **FIXED** (`36909aa`): header and row 33 say 264 + 77. |
| H6 | `TECH_CLAIMS.md` line 79 | "Disclosure, as the submission carries it: 'Evaluation harness uses the Jev decision API from TypeSafe as typed judges ...'" | The canonical line is the longer one (CLAUDE.md line 33), which names the run-time use. | CLAUDE.md line 33 | hack-jedi | **FIXED** (`36909aa`): line 79 copies the canonical line. |
| H7 | `documents/prework/EVAL_DESIGN.md` lines 137 and 138 | "Evaluation harness uses the Jev decision API (my prior project) as typed judges; disclosed as prior technology per the rules." | False, and Juan said so. The file is prework reference data, but it sits in the repo and the hub. | BUILD_LOG 98 | hack-sensei | **FIXED.** Corrected to the canonical line with the note "(corrected 2026-10-07: Jev is third-party)". |
| H8 | `code/app/static/how-it-was-built.html` (generated) | The page is older than `HOW_IT_WAS_BUILT.md` | `evaluations/tests/test_ui_ids.py::test_built_page_is_current_with_its_source` fails (74 pass, 1 fails). My Markdown changed three times since the last build. | run | hack-artisans | **FIXED** (`3bd1684`; the test passes) |
| H9 | `code/app/static/index.html` 324 to 326 (the home page's "How this was built" list) | "14 named checks, 3 tries" and "Jev typed judges, a red team, human review" | Jev also checks every draft at run time. The list reads as if Jev only judges after the fact. | TECH_CLAIMS 32, 35 and 50 | hack-artisans | **FIXED** (`1c1e6cc`, `f02e998`: the count is read from the registry; the list names Jev's run-time role) |
| H10 | The learning-loop lines: `TECH_STORY.md` Q13, deck slide 16, `HOW_IT_WAS_BUILT.md`, `ARCHITECTURE.md` section 12, `CONSENT_NOTE.md` | "The app wiring is in progress and not in the committed build" | True at 2026-10-07 01:50. BUILD_LOG 120 puts the wiring back in scope. When hack-artisans commits and tests it, the lines change to "built" with the commit. | `ca6d9aa` (pushed); 81 real-click checks at 390 and 1280 px with a stubbed gate | I changed the five files | **FIXED** ("built and browser-tested with a stub, not live") |

## 4. Medium and low findings

| # | Where | Finding | Owner | Status |
|---|---|---|---|---|
| M1 | `description.txt` 13 | "Each draft passes our rules and a Jev classifier." Jev fails open (8 s, no key, an error), so a draft can reach the pastor without a Jev answer. Suggested: "Each draft passes our rules and, when Jev is reachable, a Jev classifier." (+4 words: 242 to 246, and 246 to 250 for the two-playbooks file, at the limit.) | hack-sensei | **DONE.** "when Jev is reachable" added to both descriptions. |
| M2 | `description.txt` 9 | "Family materials come out in Spanish." The family's language is Spanish or English (`playbook.json: languages`). | hack-sensei | **DONE** in the main description only ("in the family's language"). Counts: 248 and 250. |
| M3 | Deck slide 7 and pitch slide 7 | "We tested that with a test playbook." Understates: hospital runs on the same engine with no engine change (TC 10 and 11). Rewrite when the hospital gate opens: "Two crises run on one engine." | I rewrite on release | **DONE.** Slide 7 and the pitch now say detention and hospital both run on the engine. |
| M4 | Pitch script slide 6 spoken text | Said only "named checks reject unsafe drafts"; Jev appeared at slide 8. The diagram node already reads "Checks, then Jev". | I fixed it | **FIXED** ("named checks, then Jev, reject unsafe drafts") |
| M5 | `TECH_STORY.md` 44 | "28 read, 21 approved, 7 held" and "18 providers listed" are both true (21 approved entries, 18 of them providers), but two "approved" counts in one document is a trap. | I fixed it | **FIXED** ("; 18 providers listed" added) |
| M6 | `README.md` | The first paragraph describes only the immigration crisis, but hospital is live. | hack-sensei | **DONE.** README rewritten. |
| M7 | `README.md` 5 | It prints the registrant's personal email and a ticket number in a public repo. | Juan | **KEPT, for Juan.** The registrant line stays (the rules required it) with a marker; Juan confirms before the repo goes public. |
| L1 | Deck slide 5 | A visible placeholder "[SCREENSHOT SLOT: crisis selector, live app, phone width ...]" in the default view. | hack-artisans supplies the shot | **DONE.** The selector screenshot (both live cards) is in slide 5. |
| L2 | `TECH_STORY.md` rows 26 and 38 | The register has two rows for one claim (judge separation). Harmless, but a source of "TC 26 versus TC 38" confusion. | hack-jedi | **FIXED** (`36909aa`): row 26 points to row 38. |
| L3 | Names | "Our network" (app), "church network" (docs), "Church network" (FEATURES). "Pastoral message" (deck) and "pastoral stage" (code). Consistent enough for readers; noted. | none | **NOTED** |

## 5. Claims I could not verify, and why they stay

| Claim | Where | Basis |
|---|---|---|
| "The engine was written during this event by the team's coding agent ... its author states that it copied no code from an open-source agent harness." | `HOW_IT_WAS_BUILT.md` section 2, Q12, `ENGINE_WALKTHROUGH.md` | The author's statement. The repo cannot prove it. Said so in the text. The app scaffold's origin is not audited. |
| The competitor descriptions (Rockpool, KineticFlow) | Deck slide 22 | `documents/prework/competition/*.md`. Not re-checked against the live sites. |
| The memorial text and facts (name, age, the sentence about her) | Deck slide 12, `MEMORIAL.md` | Juan's text, approval pending. Hidden. |
| "The video narration is an AI-generated voice (ElevenLabs)." | README, `SUBMISSION_NOTES.md` | True as far as I know; the render settings are hack-video's. |
| The earlier failures on slide 14 ("What broke and what changed") | Deck slide 14 | From `evaluations/FAILURE_LOG.md`, which I read on 2026-10-06. Not re-read tonight. |
| "TypeSafe's retention and terms are not reviewed" | `TECHNICAL_REFERENCE.md`, `HOW_IT_WAS_BUILT.md` | A statement about the team, true until Juan reads them. |
| Estimates: a live candidate test about $5.60 (core set) and about $10 (all three sets) | `ARCHITECTURE.md`, `HOW_IT_WAS_BUILT.md` | `LEARNING_LOOP.md` section 6, an estimate; never run live. Marked "by estimate". |
| "5 to 15 seconds added per stage" by a second reviewer in the loop | `HOW_IT_WAS_BUILT.md` | BUILD_LOG 102, an estimate. Marked "estimated". |

Claims I checked against their sources tonight and found current: the Jev gate lines (0.50, 0.60), the safe and unsafe ranges (0.02 to 0.35, 0.78 to 0.99), the 0.12 drift, 150 ms per call, 15 canaries in the Jev leak test, 90 leak-test checks per playbook, the judge validation (0.89 to 0.98 and 0.02 to 0.24), the stability check (0.03; 0.21 to 0.18), 12 verses, 18 official-list providers, 5 approved hospital sources and 1 rejected, 3 attempts, 5 Gloo calls per package, 257 product tests, FEATURES' own status counts (47, 37, 4, 7, 21; recounted from the rows).

## 6. Waits for the re-run: the final fill

hack-artisans runs every set once on the final build. When the scorecards exist I fill these, from the scorecards and nothing else. The held slide 9 template is ready (`presentation/RESULTS_DRAFT.md`, section B).

| # | Place | Now | Fill with |
|---|---|---|---|
| 1 | Deck slide 9 | `[held]` and `[PLACEHOLDER]` | Per set: judge pass / fail / awaiting; cost and time per run (means) |
| 2 | Deck slide 9, three held findings | Hidden | The hostile-intake result after the triage fix, with what changed; the tone line; the scenario 02 line (only if the re-run still shows it) |
| 3 | `description.txt`, `description_two_playbooks.txt` | "20 hand-built scenarios. Results: [PLACEHOLDER]" | The real sentence (H3). Keep each file at or under 250 words. |
| 4 | Pitch script slide 9 | `[NUMBER ...]` and the fallback | The numbers, one honest failure |
| 5 | `TECH_STORY.md` 76 and row 25 | `[NUMBER]` | Final counts |
| 6 | "14 named checks" in 10 places in 7 files (H1) | **Done 2026-10-07** | "20 named checks plus the safety floor" |
| 7 | "50 to 56 s" in 13 places in 7 files (H2) | 50 to 56 s, 9 cents | The scored means |
| 8 | `RESULTS_DRAFT.md` and `PROOF_FILL.md` | Interim numbers, labelled not for the deck | Remove the interim table |
| 9 | The red team | Run on core `00fe7b1` only | Say so, or the run on the final build when it exists |

**Rules for the fill.** No total until every review item is decided. Report failures. Say "judge pass", not "passed", for a count that is not yet reviewed. Say "synthetic" every time a number appears.

## 7. Fixed during this audit (my files)

| # | File | Fix |
|---|---|---|
| 1 | Deck slides 8, 13 and 17, speaker notes; `PITCH_SCRIPT.md` 57; `TECH_STORY.md` rows 30, 38 and Q6; `ARCHITECTURE.md` section 4; `HOW_IT_WAS_BUILT.md` section 3 | Red-team claims moved from the superseded first pass to the second validation pass (all three caught 8 of 8; the false-flag numbers; llama's invented quotes). "No reviewer invented a quote" removed. |
| 2 | `HOW_IT_WAS_BUILT.md` and `ARCHITECTURE.md` | "The red-team run on the final sets is pending" corrected: it ran on 28 scenarios on core `00fe7b1`; not on the final build. |
| 3 | `STANDARDS_ALIGNMENT.md`, deck slide 21, the standards Q and A | The "gaps" statement listed a consent note as missing. A consent note is in the app; the gap list now reads "case status with dates, an access log, and sign-in", and says nobody has reviewed the note against a standard. |
| 4 | `TECH_STORY.md` | "91 tests" (four places) corrected to 257, with the evaluation count. |
| 5 | `ARCHITECTURE.md`, `HOW_IT_WAS_BUILT.md` | "13 gate tests" corrected to 15; "All 163 must pass" to 257. |
| 6 | Deck notes | "163 tests" corrected to 257. |
| 7 | `FINALIST_SCRIPT.md` | L11 word count 6 corrected to 5. |
| 8 | `NAME_ENTRY.md`, `ERIC_LINES.md`, `PROOF_FILL.md` | Three dates written as 2026-10-08 corrected to 2026-10-07. |
| 9 | `ARCHITECTURE.md`, `HOW_IT_WAS_BUILT.md` | Scripture: added that all 31 verses in the scored runs came from YouVersion with no fallback. |
| 10 | `ARCHITECTURE.md` | "163 pass now" corrected to 257. |
| 11 | Deck | Rebuilt and re-checked in both states at 1280x720, 1920x1080 and 390x844: no overflow; no "first pass" text left. |
| 12 | `HOW_IT_WAS_BUILT.md` | "Technical reference" pointer; hub entry. |
| 13 | `PITCH_SCRIPT.md` 36, `TECH_STORY.md` 44 | M4 and M5 above. |
| 14 | Source-of-truth list | Recounted FEATURES; the stated counts are correct. |

## 8. Consistency audit: names and wording

Method: a script scanned 39 files (deck source, scripts, descriptions, notes, documentation, the app's pages, README, CLAUDE.md, the video Markdown) for each item below, and I read every hit.

| Item | Canonical | Where checked | Result |
|---|---|---|---|
| Tagline | Brand line "An AI Crisis Response Agent." Running text "an AI crisis response agent". | 39 files | **Consistent**, except the video source (B1). `index.html`, `shell.js`, the other app pages and `branding/` all match. |
| "solo pastors", "no staff" as positioning | None | 39 files + video | None left in my files, the app or the docs. **Left in** the video source (B1). README line 5 says "Solo Hacker ticket" (a hackathon ticket type, not positioning). |
| Jev disclosure line | CLAUDE.md line 33 (the longer line naming run-time use) | Whole repo | Present in **28 files** (the descriptions, notes, deck, film script, Eric lines, tech story, architecture, `report.py`, `build_docs.py`, the generated documentation page and the scorecards), all with the correct wording. **Wrong in 3**: `Nury.tsx` (B1), `TECH_CLAIMS.md` 79 (H6), `EVAL_DESIGN.md` (H7). |
| "Jev from TypeSafe, we did not build it" | Third-party, not Juan's | Whole repo | No "my project" or "prior project" in my files, the app or the docs. Present only in the three places above. |
| Jev role | Run-time classifier and test-time judge | 39 files | No "test time only" left. One accurate use: `jev_judges.py` and `redteam_panel.py` docstrings ("EVAL TIME ONLY") describe those two files, which is correct. The home-page list omits the run-time role (H9). |
| Writer | "Claude Sonnet 4.6 through Gloo AI Studio" | 39 files | **Consistent.** `pricing.json` also lists Sonnet 5.5 "for comparison; Nury does not run on it", correctly. |
| Red team | OpenAI GPT-5.4, Google Gemini 3.1 Pro, Meta Llama 4 Maverick; none is Claude | 39 files | **Consistent names** in 8 files. Claims about their results fixed (H4). |
| Named checks | 20 in the registry; 14 used in the earlier scored runs; plus 5 floor checks (banned phrases, language, links, phones, emails) | 39 files | "14" consistent, becoming stale (H1). "5 floor checks" consistent with TC 5. "19 banned patterns" and "12 hospital patterns" consistent. |
| Tests | 264 product and 77 evaluation, all passing at the end of the evening (257 and 74 plus 1 failing when the audit started) | 39 files | Fixed (7 places). `TECH_CLAIMS.md` still stale (H5). |
| Scenarios | 20 detention, 8 hospital, 18 hostile intakes, 5 case-file, 3 network | 39 files | Counts consistent. "20 hand-built" in the description is the stale one (H3). |
| Costs | $3 and $15 per million tokens; 8 to 9 cents per package (four pre-gate runs); scored means $0.072 and $0.087 | 39 files | Consistent among themselves; stale against the scored runs (H2). Jev price: **not quoted anywhere** (checked). |
| Attempts and gates | 3 attempts; Approve, Edit or Stop; "I'll handle this manually." | 39 files | **Consistent.** |
| Word limit | "Under 120 words" (the check allows 119) | 39 files | **Consistent.** |
| Gate lines | 0.50, and 0.60 for `assumes_facts`; uncertain from 0.30; 8 s timeout | 39 files | **Consistent.** Older figures (0.42, 0.74, 156 ms alone) remain only where they are labelled as the first pass. |
| Outbound calls | Gloo; Jev (only with a key, tokens only); YouVersion (only with a key) | 39 files | **Consistent.** No file says "one outbound call". |
| Sign-in, encryption | None, none | 39 files | **Consistent.** No file says "secure", "private", "encrypted", "confidential" or "HIPAA" about Nury. |
| Learning | "Not yet; built and tested on synthetic scenarios; we do not claim it improves Nury" | 39 files | **Consistent.** No file says Nury "learns", "improves itself" or "self-evolves" (searched). |

## 9. Gated lines: what can open

These are hidden until hack-sensei confirms in writing. Each now has a BUILT status in FEATURES. I have not opened any.

| Gate | Hidden line or slide | FEATURES status | What I need |
|---|---|---|---|
| `hospital` | Slide 4 chip; pitch slide 4 and 7 lines; the two-playbooks description | BUILT, live verified | **OPEN** (hack-sensei, 2026-10-07). Its numbers wait for the final re-run. |
| `scripture` | Slide 4 and 6 sentences; pitch slide 4; TECH_STORY Q7 | BUILT, live verified (YouVersion; 31 of 31 verses, no fallback) | Written go |
| `skills` | Slide 7 sentence; pitch slide 7 | BUILT, live verified; **effect not measured** | Written go; the line must say they exist, not that they help |
| `casefile` | Backup slide "The case file" | BUILT, live verified | Written go |
| `network` | Backup slide "Listed does not mean recommended" | BUILT, live verified | Written go |
| `memorial` | Slide 12 | Juan's text; approval pending | Juan, in writing, and his choices (name, photo, who speaks) |
| `results` (new) | Slide 9 earlier numbers and three findings | n/a | Release after the re-run |

## 10. Questions for hack-sensei

1. B2: open the hospital gate for the talk and the film, or keep hospital out and tell hack-artisans which screenshot to use?
2. H1: the number for the headline once the re-run is done: "20 named checks", or "20 in the registry, N applied per stage"?
3. M1 and M2: change the description sentences (M1 needs 4 words, M2 needs 1)? The two-playbooks file would reach 250.
4. H7 and M7: leave the prework file and the README email as they are, or correct them?
5. H10: do you want me to change the learning-loop lines to "built" as soon as hack-artisans commits, or wait for the re-run?
