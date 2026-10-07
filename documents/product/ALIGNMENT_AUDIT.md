# Alignment audit: one table of facts, and every document checked against it

Written 2026-10-07 by hack-ninja for hack-sensei. Part 1 is the single table of facts: the truth, with the file it comes from. Part 2 lists the documents I checked, the mismatches I found, what I fixed and what I sent to the file's owner. Facts were re-read from code, audit files and scorecards today, not copied from other documents.

## Part 1. The table of facts

| Fact | The truth | Source |
|---|---|---|
| Tagline | An AI Crisis Response Agent (always below the logo, never beside it) | `CLAUDE.md`; `branding/BRAND.md` |
| What Nury is, in one sentence | An AI crisis response agent for churches and the pastors who answer the call | `CLAUDE.md` |
| The pipeline, in one line | The pastor types the intake; names become tokens; Claude Sonnet 4.6 writes a stage through Gloo AI Studio; our named rules and Jev check it; a failing draft is rewritten up to three tries, then Nury steps aside; the pastor approves, edits or stops every stage; nothing is sent except by the pastor | `README.md`; `code/nury/engine.py` |
| Stages | Five (triage, rights brief or information brief, attorney or hospital resources, family checklist, pastoral message) | `CLAUDE.md`; `code/playbooks/*/stages.json` |
| Live crises | Two: Immigration matter (the card title; the playbook is `detention`) and Hospital emergency. Two cards say coming soon: Sudden loss, House fire | `code/playbooks/*/playbook.json`; commit `aabbd63` (title text only) |
| Named rules in the registry | 20, plus the safety floor | `len(code/nury/checks.REGISTRY)` = 20 (run today) |
| Plain-code checks that read each test run | 9: seven decide, two only advise | `evaluations/judges/deterministic.py`; hack-jedi's count |
| Typed Jev questions (test time) | 16: 10 yes or no, 5 scores, 1 choice; a run is asked 4 to 8 | `evaluations/judges/jev_judges.py` (`NOUL` 10, `SCORE` 5, one choice function) |
| Test-time layers | 4: Jev typed judges, plain-code judges, red team, human review (the run-time rules and gate are not layers; attacker intakes are a test set) | `documents/TECH_CLAIMS.md` row 25; hack-jedi's count |
| Product tests | 336, all passing | `cd code && ./test.sh` (run today) |
| Evaluation tests | 109, all passing | `python3 -m pytest -q evaluations/tests` (run today) |
| Scenarios | Detention 20, hospital 8, hostile intakes 18 (46 scored), network 3, case file 5; one extra privacy scenario file | `evaluations/scenarios*/`, `evaluations/network/` (counted today) |
| Scored build | `9bc5c6d`. The shipped build differs only in the crisis card titles and in the title text inside one context string given to the Jev gate; three pipelines on the shipped build completed with no draft rejected (a smoke check, not a rate) | `evaluations/results/build_comparison.md`; hack-jedi's check |
| Results, judge pass / fail / undecided | Detention 11 / 1 / 8; hospital 5 / 0 / 3; hostile intakes 13 / 1 / 4; all 46: 29 / 2 / 15; network 1 / 0 / 2; case file 5 / 0 / 0. These are judge results, not human verdicts, and no pass rate is quoted | `evaluations/results/build_comparison.md` |
| Cost and time per case | Detention about $0.064 and 34.2 s (mean of 20); hospital about $0.089 and 49.5 s (mean of 8); input is about 90 percent of tokens and 66 percent of cost | `evaluations/results/scorecard.md`, `hospital/scorecard.md` |
| A "case" | One full run of the five stages (older technical files call it a package) | commit `e67ed58`; this audit |
| Jev gate, final scored sets | 239 gate calls, all answered, none failed open (detention 92, hospital 40, hostile 92, network 15); longest call 435 ms of an 8,000 ms limit; median about 155 ms; about 2 percent of model-call time; about 10,000 input tokens and about $0.0003 to $0.0005 per case | audit files under `evaluations/results/`; hack-jedi's confirmation |
| Jev price | $0.042 per million input tokens, output free (public). TypeSafe's data retention and terms for run-time use have not been read | https://docs.typesafe.ai/models, read 2026-10-07 |
| Reading level (advisory) | Detention: Spanish INFLESZ 76.6, English grade 5.5. Hospital: INFLESZ 72.2, grade 5.2 | `evaluations/results/build_comparison.md` |
| Tone judge | Detention 3.04 to 3.32, hospital 3.14, target 4; it moves up to 0.75 between identical runs; no human has rated warmth | `evaluations/results/tone_before_after.md`; `CODE_REVIEW.md` HON-03 |
| Red team | GPT-5.4, Gemini 3.1 Pro, Llama 4 Maverick, through Gloo. Validation: all three caught 8 of 8 planted problems and over-flag safe text; Llama sometimes quotes text not in the draft (once in validation, four times in the live run). 55 corroborated findings in 25 of 28 scenarios, on core `00fe7b1`. Not re-run on the final build. Advice only | `documents/product/HOW_IT_WAS_BUILT.md` (Outside review); `evaluations/results/panel_digest.md` |
| Scripture | The model never writes a verse. It picks an id from 12 approved verses. Text from YouVersion (Berean Standard Bible 3034; Biblia Libre Versión Bíblica 3291) or the public-domain bank (Reina-Valera 1909, World English Bible). On the final build 44 of 45 verses came from YouVersion, one from the bank | audit files; `code/nury/scripture_providers.py` |
| Privacy | Names and identifiers become tokens before any model request; leak test 90 checks per playbook, 0 found | `documents/TECH_CLAIMS.md` row 16 |
| Pages in the app | Home, Cases (case tabs: summary, one per stage, People, Documents, Timeline, Intake, Changes, Log; Export / Print menu), Network, About, How this was built, Observability, Self-improvement, What did not work, Economics, The pattern, Standards we use, Run your own case, build log | `code/app/server.py`; `code/app/static/shell.js` |
| PDF export | Family copy and pastor copy as PDF, plus a zip. Needs Chrome or Chromium; without one, the print view | `code/app/pdf_export.py` |
| Replay mode | With no Gloo key the app runs a recorded run of each sample intake; the model's words are recorded, the checks, gates and privacy layer run for real; it is not a live run | `documents/product/HOW_IT_WAS_BUILT.md`; commit `ee674bf` |
| CLI and MCP | Shipped, read-only, no key: `python -m nury.cli ...` and `python -m nury.mcp_server`, from `code/` | `documents/product/CLI_AND_MCP.md`; commit `fd4b851` |
| Jev disclosure line (verbatim) | The Jev decision API from TypeSafe is used as typed judges in our evaluation harness and as a run-time draft classifier; disclosed as third-party technology per the rules. | `CLAUDE.md` |
| Provenance sentence (verbatim) | Built in Boulder, Colorado, during the Gloo AI Hackathon, October 6 to 8, 2026. Every step is in the build log. | `README.md`; the app footer |
| Commit dates | 41 hack-ninja commits (and some hack-video commits) carry hand-typed dates; the first commit (2026-10-06 19:36 MDT) and all others use the real clock | `documents/product/COMMIT_DATES.md` |
| Memorial | Gated. The deck slide and the About block stay hidden until Juan approves the text in writing. The text is Juan's, and nobody edits it | `presentation/MEMORIAL.md` ("DRAFT until Juan approves") |

## Part 2. Documents checked

I searched 29 documents for the patterns of an old fact: old counts (14 checks, five layers, fifteen questions, seven judges, old test counts), old card titles, the word "package", "when Jev is reachable", old time and cost, old results, "solo pastor", an old build named as final, an unknown Jev price, "not yet run", and old page names. I also compared the Jev disclosure line with the verbatim text.

Files checked: `README.md`, `ARCHITECTURE.md`, `FEATURES.md`, `TECH_CLAIMS.md`, `TECHNICAL_REFERENCE.md`, `HOW_IT_WAS_BUILT.md`, `ENGINE_WALKTHROUGH.md`, `OBSERVABILITY.md`, `LEARNING_LOOP.md`, `ADD_A_RULE.md`, `PATTERN.md`, `ECONOMICS.md`, `STANDARDS_PAGE.md`, `STANDARDS_ALIGNMENT.md`, `CLI_AND_MCP.md`, `ABOUT_PAGE.md`, `WHAT_DID_NOT_WORK.md`, `JUDGES_CARDS.md`, `PLAIN_LANGUAGE_SAMPLES.md`, `FINAL_PAGE_GUIDE.md`, `OBSERVABILITY_EVALS_TEXT.md`, `PI_REVIEW.md`, `CODE_REVIEW.md`, `description.txt`, `description_two_playbooks.txt`, `SUBMISSION_NOTES.md`, `TECH_STORY.md`, `PITCH_SCRIPT.md`, `FINALIST_SCRIPT.md`, `ERIC_LINES.md`.

### Fixed by me (files I own)

| File | Mismatch | Fix |
|---|---|---|
| `README.md` | Test counts 335 and 88; no PDF export, About page, Built to grow, pages list, localhost URL, CLI run command; a card title in running text ("immigration detention or raid"); disclosure line in lower case | Updated to 336 and 109; added all of those; wrote the disclosure line verbatim |
| `TECH_STORY.md` | Test counts 264, 270, 296 and 335 in four places; "placeholder stays" rule; "evaluations suite has 88" | 336 and 109; no placeholders remain, never quote a pass rate |
| `JUDGES_CARDS.md` | "33 to 49 seconds" | 34 to 50 seconds |
| `PITCH_SCRIPT.md` | The disclosure line was a variant | Verbatim |
| (earlier today) | "package" in people-facing text; "when Jev is reachable"; five layers; fifteen questions; Jev price unknown; old results and costs | Fixed in my files; see `CLAIMS_AUDIT.md` sections 1d to 1f |

### Sent to the owner (not my files)

| File | Mismatch | Truth |
|---|---|---|
| `TECH_CLAIMS.md` | Row 33 says 311 product tests and 87 evaluation tests (398 in all); line 7 says 264 tests | 336 and 109 |
| `TECH_CLAIMS.md` | Row 30: "takes under a minute and costs about nine cents" | 34.2 s and $0.064 (detention), 49.5 s and $0.089 (hospital) |
| `TECH_CLAIMS.md` | Rows 55, 62, 63 use "package" | A case is one full run; add the definition or say "case" |
| `ARCHITECTURE.md` | Line 107: "A full package takes 50 to 56 seconds and costs about nine cents (four live pipelines)" | 34 to 50 s and 6 to 9 cents on the final scored runs |
| `ARCHITECTURE.md` | Line 66: the gate "BUILT, live verified (3 scenarios ... build `50668d6`)" | Also ran on every scored set: 239 of 239 calls answered |
| `ARCHITECTURE.md` | Line 86: attacker intakes "BUILT, not yet run" | Run on the final build: 13 / 1 / 4 |
| `ARCHITECTURE.md`, `FEATURES.md`, `OBSERVABILITY.md` | "package" in 11 places | Say "case", or keep "package" only with the one-line definition at first use |
| `TECHNICAL_REFERENCE.md` | Lines 10 and 379: "264 tests" | 336 |
| `CODE_REVIEW.md`, `PI_REVIEW.md` | Count and "3 percent" lines from the review time (270 tests, 84 evaluation tests, Jev 3 percent) | These are a dated review; I left them. Say so at the top if they stay in the hub |

### Open

- **Memorial:** gated until Juan approves the text in writing (deck slide, About block, film). Not a mismatch. Needs Juan.
- **Registrant line in the README** (personal email and ticket number): Juan has not confirmed it for a public repo. The HTML comment is still there.
- **Clone URL** in the README is a placeholder (`<this repository>`) until the public address exists.
- **Three build ids appear in the docs** (`c317050`, `8a28a18` and `9bc5c6d`). That is on purpose (the comparison table), but the final scored build is `9bc5c6d` only.

## Method and limits

- The table was written from code, audit files and scorecards that I read or ran today (registry count, typed-question definitions, scenario files, test suites, Jev audit events). Where a number comes from another agent's count (nine plain-code checks, the Jev timing), the source says so.
- The scan finds old patterns. It cannot find a new false claim that matches none of them. Treat a clean scan as "no known stale fact", not as proof.
- `CODE_REVIEW.md` and `PI_REVIEW.md` are dated reviews, so stale numbers there are expected.
