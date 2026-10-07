# The learning loop: how a person can learn from what pastors change

**Read this first.** No real pastor has used Nury. Everything in this document, the example and the tests uses synthetic scenarios (scenario 16, "pastor edits a stage", and the revision scenarios). The loop is built and tested. It has not learned anything from anyone. We have not shown that it improves Nury.

**What it is not.** It is not a self-modifying agent. Nothing changes a prompt, a rule, a threshold or a model by itself. The loop proposes. A person decides.

## 1. The idea in five steps

| Step | What happens | File | Who |
|---|---|---|---|
| 1. Capture | At each gate, record what the pastor did (approve, edit, stop) and what changed, with names already turned into tokens. Optional: a one-tap reason chip and the "Something changed" answer. | `code/nury/feedback.py` | the app, automatically, only if switched on |
| 2. Analyze | A script reads the feedback and the run ledger and writes a report: what pastors changed most, by crisis and stage, and candidate improvements, each with a type, evidence counts and a draft change. | `code/tools/learning_report.py` | a developer runs it |
| 3. Test | Run a candidate on the evaluation sets, before and after, and print a table with a no-regression gate. | `code/tools/candidate_test.py` | a developer runs it |
| 4. Approve | A person reads the candidate file, the evidence and the test, and writes their name and the date in it. | `candidates/<id>.md` | a person |
| 5. Release | A normal commit makes the change, with the usual tests and a live check. | git | a developer |

A rule that holds the whole thing: **propose a change, score it with evaluators, promote it only if it improves quality under cost and safety thresholds, and only a person promotes.**

## 2. The research basis, and how little of it we use

Pages only, read on 2026-10-07 (abstracts, not the papers in full):

- Gao et al., 2025, "A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve on the Path to Artificial Super Intelligence", https://arxiv.org/abs/2507.21046. It organizes how agents can adapt: what changes (models, memory, tools), when it changes, and how.
- Fang et al., 2025, "A Comprehensive Survey of Self-Evolving AI Agents: A New Paradigm Bridging Foundation Models and Lifelong Agentic Systems", https://arxiv.org/abs/2508.07407. A second survey of agents that improve from interaction data and environmental feedback.
- Shinn et al., 2023, "Reflexion: Language Agents with Verbal Reinforcement Learning", https://arxiv.org/abs/2303.11366. Agents "verbally reflect on task feedback signals" and keep that text as memory for later trials.
- Wang et al., 2024, "Agent Workflow Memory", https://arxiv.org/abs/2409.07429. Agents learn reusable workflows from past experience and reuse them.
- Agrawal et al., 2025, "GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning", https://arxiv.org/abs/2507.19457. A prompt optimizer that reflects on trajectories in natural language, proposes and tests prompt updates, and keeps a Pareto frontier.
- DSPy (https://dspy.ai): a framework whose optimizers propose prompt changes and score them against a metric. I did not read its documentation. A search summary said an optimizer's result is saved to a file that production loads; I treat that as unverified.

**What we took, and what we left.** From these we took one pattern: reflect on what went wrong, propose a change, score it with evaluators, keep it only if it scores better. We left out everything that makes an agent change itself: no automatic prompt rewriting, no memory that feeds back into drafts, no optimizer that promotes a winner. In a product that speaks to frightened families, the part that decides is a person. The surveys describe agents that evolve on their own; Nury deliberately does not.

**What we did not show.** None of these papers is evidence that this loop helps Nury. They are evidence that the pattern exists and works in other settings. Whether it helps here depends on real pastors, which we do not have.

## 3. Capture: what is recorded

Switch: `NURY_FEEDBACK=off` (the default, nothing recorded), `on` (sentence mode) or `counts` (strict mode). The app shows the consent sentence only when it is on, and the sentence is a constant in the code, approved by Juan:

> Nury also records what you change, without names, to improve its drafts; a person reviews every change before it is used.

The server calls `feedback.record_gate(stage, action, draft_text, final_text, privacy_client, audit_events, outcome_label=None, reason_chip=None, ...)` at each gate. Reason chips are posted to `POST /api/feedback`, which the app adds on `feedback.record_chip`. The chips are `good_as_is`, `too_long`, `not_my_voice`, `wrong_tone` and `inaccurate`. The "Something changed" answer (`went as hoped`, `did not go as hoped`, `unknown`) goes in through `feedback.record_outcome`; the pastor's free-text note is never stored.

| | `on` (sentences) | `counts` (strict) |
|---|---|---|
| Stored | The sentences that changed (removed, added, replaced), pseudonymized, plus counts, tags, rule categories, Jev decisions and probabilities | Counts and edit-type tags only |
| Whole drafts | Never | Never |
| Sentences | **Yes, tokenized text.** Unlike the run ledger, this file holds text. | None |
| Quoted Scripture | Never stored; a changed verse is only a tag | Same |
| The report can say | How often and how much pastors changed things, and **what** they removed or replaced | How often and how much, never what |
| Candidates it can support | Length, a banned phrase, voice, accuracy, scenarios | Length, voice (by chip), accuracy (by chip), scenarios; **not** a phrase rule |

How a sentence gets in, and how it is kept out:

1. Both texts are pseudonymized with the case's own Pseudonymizer (the same one the Gloo path uses). If there is no pseudonymizer, sentence mode falls back to counts for that line (`degraded: true`).
2. The two texts are split into sentences, and only the sentences that **changed** are kept. An unchanged sentence, the disclaimer, the label and the verse block are never stored.
3. Every kept sentence is checked again. If it still holds something the Pseudonymizer would tokenize (an address, a phone, an email, a date, an ID), a name-like word, or a protected term the pastor named, the change is **dropped and counted** (`dropped_unsafe`), not stored.
4. Every field other than a changed sentence must be a number, a bool, null or a short slug. Otherwise nothing is written.
5. A failure never breaks a run: the function returns False.

**Proof:** `code/tests/test_feedback.py` runs edits full of canary names, a phone, an email, an address and an ID, plus a name the pastor typed that nobody had protected (Brunhilda Vandersloot), in both modes, and finds none of them in the file. The unprotected name's sentence is dropped and counted.

**What this cannot catch.** A sentence with no name or identifier that still points to a person ("the cashier at the pharmacy on the corner"). Pseudonymization removes direct identifiers; context can still hint. This is the same limit as the privacy layer and the same honest sentence applies. It is why sentence mode needs the consent sentence, why counts mode exists, and why the file is a short-lived working record.

**Retention.** Files are daily (`data/feedback/feedback-YYYYMMDD.jsonl`, gitignored). `feedback.prune(days)` deletes old days. Nothing calls it automatically: an operator has to decide the period and run it. We recommend 30 days for sentence mode, after which only the report and approved candidates remain. That is a recommendation, not a policy; it has not been reviewed by a lawyer or an ethics review.

## 4. Analyze: the report

`python3 code/tools/learning_report.py` reads `data/feedback/` and `data/ledger/` and writes `documents/product/LEARNING_REPORT.md`. It shows, by crisis and stage: gates, edits, edit rate, how many edits made the text shorter or longer, the chips, and how often a rule had rejected a draft or Jev had been uncertain on the drafts that were then edited. It shows the "Something changed" answers per crisis.

A candidate is proposed only when the same pattern shows up in at least `--min` (default 3) separate edits or chips. Below that the evidence is only listed. The four types:

| Type | Triggered by | Draft change |
|---|---|---|
| `prompt_line` (length) | At least 3 edits that shortened a stage, or 3 "Too long" chips | A line appended to the stage's prompt, with a target length from the median of the shortened versions |
| `prompt_line` (voice) | 3 "Not my voice" or "Wrong tone" chips | None yet: a person writes the line |
| `new_rule` | The same three-word phrase removed or replaced in at least 3 edits of one stage (sentence mode only) | An `extra_banned` entry for the playbook, with a caution that it applies to every stage |
| `new_jev_question` | 3 "Inaccurate" chips where Jev was uncertain or rejected | None: shared eval wording is written by hand |
| `new_scenario` | 3 revisions that "did not go as hoped" | A draft scenario file with TODO fields; it cannot run until a person writes a fictional intake |

## 5. The candidate file and who approves

`candidates/<id>.md`: a front matter with `id`, `type`, `status`, `created`, `synthetic`, `evidence`, `approved_by`, `approved_date`, `test_result` and `release_commit`; then why; then the draft change as JSON blocks (`append`, `replace`, `json_append`, `add_file`). `python3 code/tools/candidates.py` checks the files.

Statuses run `proposed`, `tested`, `approved`, `released`, or `rejected` at any point. The checker enforces:

- `tested` needs the saved before-and-after table and a change block.
- `approved` needs `approved_by` (a person's name; "nury", "auto", "bot" and "script" are refused) and `approved_date`.
- `released` needs the release commit.
- A change may not touch `.git` or `.env`, use an absolute path or climb out of the repository.
- A new Jev question is never a change block, because it changes shared wording that the evaluation harness also uses.

No script in the loop sets a status past `proposed`. A test reads the scripts' source to check it.

## 6. Test: before and after

```
cd code
python3 tools/candidate_test.py ../candidates/<id>.md --dry-run      # the diff; nothing runs
python3 tools/candidate_test.py ../candidates/<id>.md --mock         # the harness with the mock agent: machinery, not evidence
python3 tools/candidate_test.py ../candidates/<id>.md --live --yes --repeat 3 --save ../candidates/<id>.result.md
```

It copies `code/` and `evaluations/` to two temporary folders, applies the change to one, runs the same scenarios on both, and deletes the copies. **It never modifies the repository or the candidate file.** The sets: `core` (20 detention and 8 hospital scenarios), `attacker` (18) and `casefile` (5, through its own runner). The table shows runs, pass, review, fail, error, safety failures, escalations, tone and cost per run, before and after.

**The gate fails** if the candidate has more failures, more errors, more safety failures or more escalations (as rates, so arms of different size compare), a tone mean more than 0.15 lower, or a cost per run more than 10 percent higher. An empty table can never pass.

**Costs, by my estimate.** About $0.10 of Gloo per scenario, plus Jev on its own key. All three sets, both arms, one repeat: 51 scenarios times 2, about $10. The core set alone: about $5.60. Three repeats triple it. `--dry-run` prints the estimate first. I have not run a live candidate test, because there is no real candidate.

**Why a PASS is not proof.** Jev scored the same drafts up to 0.12 apart between two passes. One run per arm cannot tell a small effect from that noise, so use `--repeat 3` or more. The thresholds above (0.15, 10 percent) are my choice, not validated. The mock agent has its own failures (8 of 28 in the core set), identical in both arms; that run shows the table and the gate work, nothing else.

## 7. The worked example, on synthetic data

`python3 code/tools/learning_example.py` builds it again, deterministically. Files in `documents/product/learning_example/`:

- `feedback/`: 70 lines from 30 invented sessions (20 detention, 10 hospital) with fictional families and a scripted "pastor": shortens the pastoral message in most detention sessions, sometimes rewrites the voice, adds a sentence to a checklist, answers "Something changed". Captured by the real `feedback.record_gate` with the real Pseudonymizer. The files hold tokens only (a test checks that none of the fictional names is present).
- `LEARNING_REPORT_EXAMPLE.md`: what the report says. In this synthetic data, 17 of 20 detention pastoral drafts were edited, 15 shorter; 13 "Too long" chips.
- `candidates/`: five proposed candidates (a length line, two phrase rules, a voice note, a scenario). All `proposed`, `synthetic: true`, none approved.
- `dry_run_output.txt` and `mock_run_output.txt`: the test script on the first candidate.

The pattern in it was written into the scripted behavior, so the report finding it proves the pipeline works. It does not say pastors prefer shorter messages.

## 8. Honest limits

- **No real data.** Every number above is from invented sessions.
- **An edit is not a preference.** A pastor may shorten a message because it is late, or because the family's situation differs. A frequent edit is a lead, not a finding.
- **Small counts.** The minimum of 3 is a guard against noise in a demonstration, not a statistical test.
- **Selection.** Only the drafts that reached a pastor are in the feedback. Drafts the engine rejected never reach it.
- **The gate has thresholds I chose**, a noisy judge, and no real evaluation set drawn from real pastors' cases.
- **Counts mode says less**, by design.
- **Sentence mode holds tokenized text** in a file. It is protected by the checks above, the consent sentence, the gitignore and a short retention, not by a technical guarantee.
- **The app side is not built.** The server must call `record_gate`, the chips and the consent sentence must appear, and `POST /api/feedback` must be mounted. Until then nothing is captured. FEATURES lists those parts as planned.
- **No lawyer or ethics review** of consent, retention or the analysis. Juan approved the sentence.
- **Nothing has been learned yet.**

## 9. What the app has to do (hack-artisans)

1. At each gate: call `feedback.record_gate(...)` with the draft the pastor saw and the final text, the case's privacy client, the run's audit events, the playbook and the language.
2. Show `feedback.CONSENT_SENTENCE` only when `feedback.mode() != "off"`.
3. Show the five chips after the gate and post one to `POST /api/feedback` (a route calling `feedback.record_chip`). The chips' labels are `feedback.CHIP_LABELS`.
4. When a revision runs, call `feedback.record_outcome(playbook, revision["result"])`. Do not pass the note.
