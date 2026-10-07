# Pi review: why we did not use it, and what is worth taking

Written by hack-jedi, the architect of the engine, on 2026-10-07. Juan asked for a candid answer, not a defense. No code was changed for this review.

## The short answer

- **Why we did not use Pi:** Nobody chose against it. I never looked at it, or at any agent harness, before building. The prework brief set the stack (one Python agent, no frameworks, plain `requests`) and the clock was short. Having now read Pi's real source, I also think it would have been the wrong base: Pi lets the model decide what happens next, and Nury is built so the model cannot.
- **Is anything worth taking:** Yes, three small things and a handful of ideas. None needs Pi's code. The one I would do before 21:00, if Juan and hack-sensei approve a change to the frozen core, is a retry policy for transient Gloo failures. Today one bad network moment ends a stage.
- **Could Pi's loop sit under Nury later:** No for the five-stage run. Maybe for a future feature that needs tools.

## 1. Why I did not use Pi, in the order that really mattered

1. **The brief decided the stack, and I did not question it.** `documents/prework/PREWORK.md` says: "single Python agent, five sequential stages, each ending at a human approval gate. No frameworks, plain `requests` against Gloo AI Studio. A pastor must be able to run it with `pip install -r requirements.txt` + one command." That is a Python, no-framework, readable-by-one-person brief. Pi is a TypeScript monorepo. I took the brief as given.
2. **I did not look.** Your question is whether I looked at Pi, or any harness, before building. I did not. I did not read Pi, and I did not read any other open-source agent harness's code or documentation. I did not compare options, and I never made a decision against Pi. The first time I read Pi was today, for the short comparison in `ENGINE_WALKTHROUGH.md` (from its web pages), and today for this review (from a clone of its source).
3. **Time.** The deadline was a hackathon. The loop Nury needs is the attempt loop inside `run_stage` (`engine.py`, lines 224 to 292), about seventy lines of Python. Writing that was faster than learning a 14-package TypeScript repository, and I knew how to write it.
4. **Familiarity, stated plainly.** I know the generate, check, regenerate pattern from general knowledge, not from a particular project. I did not copy code. But "I did not read Pi" is not the same as "my design is independent of everything I know about agent loops". It is not independent of that. It is independent of any one codebase.
5. **Purpose.** This reason I only understood by reading the source. Pi's loop gives the model the steering wheel. Nury's whole safety argument is that the model has no wheel: the engine decides each step, the model only writes text, checks and a classifier decide what passes, and a person approves each stage. A harness built around model-chosen tool calls would have been something to fight, not something to build on.

## 2. What I read, and what I could not

**Read.** A shallow clone of https://github.com/earendil-works/pi at commit `2db5e359bf84c1c0be51d2c5c5c5c7cf27072c2b` (dated 2026-10-07), kept in a temporary folder outside this repository. I did not run any of its code and did not install anything from it. MIT licensed. The repository has 14 packages and about 947 TypeScript source files and 627 test files by my count. Files I read in full or in the parts cited:

- `packages/agent/src/agent-loop.ts` (949 lines; I read the loop body, lines 163 to 332) and `packages/agent/src/types.ts` (539 lines; hooks, config and events).
- `packages/coding-agent/docs/`: `how-pi-works.md`, `skills.md`, `session-format.md`, `security.md`, `extensions.md` (outline and the event section), `rpc.md` and `sdk.md` (introductions), `compaction.md` (overview).
- `packages/coding-agent/src/core/skills.ts` (constants and validation only), `packages/ai/src/utils/retry.ts` (the error patterns and policy comment), `packages/ai/src/types.ts` (`Usage`), `packages/ai/src/providers/` (the file list), `packages/ai/src/providers/faux.ts` (opening).
- `packages/evals/README.md`, `.github/workflows/ci.yml` (first 60 lines), `AGENTS.md` (first 50 lines).

**Not read.** I want this to be clear, because a review like this is easy to overstate:

- `session-manager.ts` (2,013 lines) and `extensions/types.ts` (2,271 lines): I read their documentation, not their source. What I say about sessions and the extension API rests on the docs.
- The provider implementations in `pi-ai` (213 files). I read the retry rules and the types, not how any one provider is implemented.
- The packages `tui`, `chord`, `durable`, `mcp`, `server`, `codemode`, `env`, `client`, `protocol` and `telemetry`. I did not open them.
- Pi's test files, apart from counting them and reading the testing rules in `AGENTS.md`. I cannot tell you how good its tests are.
- Pi's git history (the clone is shallow, one commit), its issues, and any security record.
- I did not run Pi, so I cannot say how it behaves.

## 3. Section by section

Each item: what Pi does (with the file and line), what we do, a verdict and a rough cost. The costs are my estimates, not measured. Verdicts: **ADOPT NOW** (small and safe before 21:00), **ADOPT LATER** (after the hackathon), **IDEA ONLY**, **NO**.

### 3.1 The agent loop and its hooks

**Pi.** `runLoop` (`agent-loop.ts` line 163) has an outer loop for follow-up messages (line 179) and an inner loop "while there are more tool calls or pending messages" (line 183). Each pass calls the model (`streamAssistantResponse`), runs any tool calls the model asked for (`executeToolCalls`, parallel by default), and stops when no tool calls and no queued messages remain. Hooks named in `types.ts`: `beforeToolCall` can block a call (declared at line 326; its result type at line 66); `afterToolCall` can rewrite a result (line 341; result type at line 92); `finishTurn` runs after each turn and can return `end` or `continue` (line 264; the decision type at line 147); `prepareNextTurn` can replace context or append messages before the next request (line 278; called in the loop at line 186); `getSteeringMessages` (line 293) and `getFollowUpMessages` (line 306) let a caller inject messages.

**What this settles from my earlier note.** In `ENGINE_WALKTHROUGH.md` I wrote that I had not verified whether `finishTurn` could carry a correction message. Now I have read it: a verify-and-regenerate loop can be built on these hooks. `finishTurn` can return `continue`, and `prepareNextTurn` can append a message, so a correction message can go in before the next model request. But Pi has no attempt cap of its own, no notion of "reject the draft and drop it", and no human gate. We would write all of that ourselves, on top of a loop designed for tools.

**Ours.** `run_stage`, line 224: `for attempt in range(1, MAX_ATTEMPTS + 1)`.

**Verdict: NO** for replacing our loop. Cost of the experiment I do not recommend: 30 or more hours (a bridge to Python, plus our checks, gate and audit written again on top of a tool loop).

### 3.2 Steering and follow-ups

**Pi.** A person can type while the agent works. Steering enters after the current turn (`types.ts` line 293, `getSteeringMessages`); follow-ups wait until the agent would stop.

**Ours.** The pastor acts at the gate, after every stage, and cannot interrupt a stage in progress.

**Verdict: NO.** Interrupting a stage mid-run has no place in a loop whose point is that the pastor sees only finished, checked drafts.

### 3.3 The event stream and our audit log

**Pi.** One typed union, `AgentEvent` (`types.ts` lines 516 to 539): `agent_start/end`, `turn_start/end`, `message_start/update/end`, `tool_execution_start/update/end`. `tool_execution_end` carries `durationMs`, "measured with a monotonic clock". Listeners subscribe, and are awaited in registration order (README). JSON mode writes the same events as JSONL (`how-pi-works.md`).

**Ours.** `AuditLog` (`audit.py`, 30 lines) appends events to a list and optionally a JSONL file. The app builds its progress phase by reading that list.

**What is worth taking.** Two small ideas. First, a subscribe hook on `AuditLog`, so the app is told about each event instead of re-reading the list. Second, a monotonic duration on timed events, so timings do not depend on comparing wall-clock timestamps (which is how I computed the trace in `ENGINE_WALKTHROUGH.md`). Neither changes behavior.

**Verdict: ADOPT LATER** for both. Cost about 2 hours with tests. **Complements** the audit log; does not replace it, because our log has facts Pi's does not (floor reasons, Jev probabilities, which sources were offered).

### 3.4 Context and message handling

**Pi.** `transformContext` prunes or injects messages before each request (`types.ts` line 244); compaction summarizes old messages when context grows (`compaction.md`); sessions rebuild context from the active branch.

**Ours.** Each stage is a single model call with a fixed, small input: the intake or the approved earlier text, the vetted sources and the rules. There is no conversation to prune.

**Verdict: NO.** The problem it solves does not exist for us. It would return if we ever added a free-form chat with the pastor.

### 3.5 Session persistence and branching, and our case versions

**Pi.** Sessions are JSONL files; each entry has an `id` and a `parentId`, so a session is a tree and "continuing from an earlier entry creates another branch in the same file" (`session-format.md`, intro and "Entry Base"). Compaction adds a summary entry and "the original entries remain in the session tree" (`how-pi-works.md`, Sessions).

**Ours.** A saved case is a folder. A revision (v2) is a second folder; v1 is never touched, and a test checks that the files are byte-identical.

**Compared.** Pi's design is append-only and keeps history in one file, which is good for audit and for "what changed". Ours gives a stronger guarantee for the thing we care about: the approved v1 cannot change, because it is a separate folder nobody writes to. Pi's tree could not make that promise by itself, because it lives in one file that is written to.

**What could help.** A per-case, append-only event log with parent ids would answer "who opened, edited or revised this case and when", which the roadmap lists as not built. It would sit beside the folders, not replace them.

**Verdict: IDEA ONLY**, and **ADOPT LATER** for the audit-of-access log. Cost 8 to 16 hours for a real design with sign-in. Not before 21:00.

### 3.6 The extension API

**Pi.** Extensions are TypeScript modules loaded into the Pi process; they register tools, commands, providers and event handlers (`extensions.md`, "Choose an integration point"). Handlers run in load order and some events "notify; others transform data, replace results, or cancel an operation". Pi's own security page says extensions run with the permissions of the account (`security.md`, line 3).

**Ours.** Named checks in `checks.py`, listed per stage in `stages.json`, described in `rules.py`. Data rules in a playbook's JSON. No plugin loading.

**Verdict: NO** to loading arbitrary code as a plugin: in a safety product, a rule must be reviewed code, not something dropped into a folder. **ADOPT LATER** (idea): the clean contract of "declared handlers with typed results", for a future rule pack that is data (patterns and required headings), not code, behind a review and approval flow. That flow is the thing we have not built. Cost 20 to 40 hours.

### 3.7 Permissions and approvals, compared to our gates

**Pi.** "Pi can read, change, and execute files with the permissions of the account that started it, and it does not ask for approval before every tool call" (`security.md`, line 3). Safety comes from isolation: "Safety comes from limiting the files, credentials, processes, and network services Pi can access... Watching the transcript, using project trust, and reviewing changes do not create..." a boundary (same page). It recommends running Pi in a container or VM (the table in `security.md`; I did not read `containerization.md`). "Project trust" decides whether to load a folder's extensions and skills.

**Ours.** A human approval after every stage and a deterministic floor in every draft. No tools, so nothing to sandbox at the model level.

**Compared.** These are opposite answers to the same worry. Pi accepts that a model acting on a computer cannot be made safe by prompts, and moves the safety to the operating system. Nury removes the model's ability to act, and puts the safety on the text. Both are honest. Ours would not survive adding tools; Pi's would not give us what we need for words a family will read.

**What is worth taking.** The hosting lesson. When Nury runs on a server for real churches, run it the way Pi's page advises: a dedicated user, no more files and credentials than the task needs, and outbound network limited to Gloo, Jev and (if set) YouVersion. That is the "hosting and secrets" item in the roadmap.

**Verdict: NO** to their approval model. **ADOPT LATER** for the hosting hardening (cost 4 to 8 hours of work plus a review).

### 3.8 RPC and SDK modes

**Pi.** RPC mode runs Pi as a subprocess driven by JSONL commands on stdin and events on stdout, "for language-independent integrations, process isolation, IDEs, and custom user interfaces". The SDK embeds it in a Node or Bun process (`rpc.md` and `sdk.md`, introductions).

**Ours.** The engine is a Python library; the app calls it in process. The audit is already JSONL.

**Verdict: IDEA ONLY.** RPC is the way a Python program could host Pi if we ever wanted Pi's tool loop for a feature. We do not.

### 3.9 The provider layer `pi-ai`, and whether it could replace `gloo_client.py`

**Pi.** `pi-ai` is a unified layer over many providers, with a `Usage` type that carries input, output, cache and reasoning tokens and a `cost` breakdown (`ai/src/types.ts` lines 433 to 454), a `maxRetries` option (line 182), and a retry module with a stated policy: "bounded attempts with exponential backoff (`baseDelayMs * 2^(attempt-1)`)" (`ai/src/utils/retry.ts`, line 110). Its rules separate failures worth retrying (rate limits, 429, 500 to 504, overloaded, connection and timeout errors) from "non-retryable provider limit" errors such as `insufficient_quota`, billing and "quota exceeded" (`retry.ts`, the two pattern lists at the top). A search of `packages/ai/src` found no provider for Gloo.

**Ours.** `gloo_client.py` is 87 lines: one POST with a 120-second timeout; HTTP 403 becomes `GuardrailBlock`; any other error status raises, and the engine then ends the stage as an error with "Gloo call failed" and no retry (`engine.py` line 242, the `except Exception` branch). Usage is two token counts; cost comes from price environment variables.

**Could `pi-ai` replace it?** **NO.** We would write a Gloo provider for it, map Gloo's 403 guardrail block, keep our privacy wrapper around it, and run TypeScript beside Python, to gain streaming we do not use. The Gloo client is 87 lines that we understand.

**But the retry policy is worth taking.** It is a real gap, and it is the one place where reading Pi changed my mind about our code. A single 429, 502 or dropped connection ends a stage today. The Gloo credit outage earlier (HTTP 402, quota) is the other kind: retrying would waste time. A bounded retry with backoff on 429, 5xx and network errors, and none on 402 or 403, is about twenty lines.

**Verdict: ADOPT NOW, if hack-sensei and Juan approve touching the frozen core:** the retry policy in `gloo_client.py`, with tests for each error class and one live smoke run. Cost about 1.5 hours. Risk: low, and it can only turn some errors into successes. It is the only item in this review I would do before 21:00. **ADOPT LATER:** a small price table so cost is computed from the model name instead of environment variables (1 hour). **NO** to streaming for now.

### 3.10 Evaluation and testing practices

**Pi.** Tests with a fake model: `packages/ai/src/providers/faux.ts` is a provider whose replies you script (`setResponses`, lines 140 and 153), and `AGENTS.md` (line 38) says the coding-agent suite uses it: "No real provider APIs, keys, or paid tokens." A separate `packages/evals` package runs behavioral evals; its documentation-lift eval "runs each case in isolated `without_docs` and `with_docs` containers and reports lift" and expands cases into `(case, variant, repetition)` tasks (`evals/README.md`). Tests carry the issue number they fix (`AGENTS.md`). I counted 627 test files; the four top-level test files of the agent package hold 77 `test(` or `it(` calls. I did not read them.

**Ours.** The same idea twice over: `FakeClient` stands in for the model in our tests, `nonet.py` keeps tests off the network, and the skills A/B (`evaluations/skills_ab.py`) compares with and without a skill. We write the exact sentence that started a rule into its test.

**What is worth taking.** Repetition. Pi's paired evals run each case several times and report the difference. Our skills A/B is written but not yet run, and one run per arm would not tell a real effect from Jev's repeatability noise (we saw scores move by up to 0.12 between two passes of the same drafts). When it is run, run each arm more than once.

**Verdict: IDEA ONLY** now; fold into the skills A/B when it runs. Cost: the extra live runs, about 1 hour of work.

### 3.11 Continuous integration and dependency hygiene

**Pi.** `.github/workflows/ci.yml`: actions pinned to commit hashes (line 18), `npm ci --ignore-scripts` (line 33), then build, check and test. `AGENTS.md` (Dependency and Install Security): direct dependencies "stay pinned to exact versions", lockfile changes are "reviewed code", and lifecycle scripts do not run on install. A pre-commit hook blocks lockfile commits unless explicitly allowed.

**Ours.** I found no CI workflow and no requirements file for the product in this repository (`documents/prework/requirements.txt` is a reference copy). The product needs only `requests`, but nothing pins it, and the one-command test run is a remembered command.

**Verdict: ADOPT NOW (small, not core):** a `code/requirements.txt` with `requests` pinned and a `code/test.sh` that runs the offline tests, about 0.5 hour. **ADOPT LATER:** a CI workflow that runs the offline tests on every push, if the repository is hosted where that can run, about 2 hours.

### 3.12 Documentation habits

**Pi.** `AGENTS.md` asks for short, direct answers, and says to explain a non-trivial design as "problem, concrete example or short trace, then solution." The docs are split by topic (`how-pi-works.md`, `security.md`, `containerization.md`, `session-format.md`), and `security.md` is candid about its limits ("Project trust is not a complete startup boundary").

**Ours.** Similar habits: a claims register with a status per row, honest NOT BUILT lists, and `ENGINE_WALKTHROUGH.md`'s trace.

**Verdict: ADOPT, no cost:** use "problem, trace, solution" for the About page's hard parts (for example the Jev line: the problem, the detention 14 trace, the 0.60 fix). This is already close to what we did in PROMPT_NOTES.

### 3.13 Skills

**Pi.** Skills follow the Agent Skills specification: a directory with `SKILL.md` and frontmatter (`name`, `description`, `license`, `compatibility`, `allowed-tools`, `disable-model-invocation`). Pi puts only name and description in the system prompt, and the model reads the full file when a task matches (`skills.md`, "Understand how skills load"). Limits: name up to 64 characters, description up to 1,024 (`skills.ts`, lines 11 and 14). Most invalid fields produce warnings, not errors. Pi warns that "a model might fail to load a relevant skill".

**Ours.** `code/skills/<name>/SKILL.md`, versioned, in English and Spanish, with checks attached. The engine applies a skill to the stages that name it, every time. The loader refuses an override. The audit records `skill_applied`.

**Compared.** Pi's skills are optional help the model may choose to read. Ours are guaranteed rules and wording the engine inserts. Pi's design would let a skill be skipped, which is the one thing a safety skill must never be.

**Verdict: NO** to on-demand loading. **IDEA ONLY:** add the `license` and `compatibility` fields to our `SKILL.md` frontmatter, so our skills could be read by other tools; and cap description length as the spec does. Cost 0.5 hour.

## 4. The verdicts at a glance

| Item | Verdict | Rough cost |
|---|---|---|
| Retry policy for Gloo (429, 5xx, network; none on 402 or 403) | **ADOPT NOW**, needs approval to touch the frozen core | 1.5 h |
| `code/requirements.txt` and `code/test.sh` | **ADOPT NOW** (not core) | 0.5 h |
| Event subscribe hook and monotonic durations on the audit log | ADOPT LATER | 2 h |
| Price table instead of price environment variables | ADOPT LATER | 1 h |
| CI workflow running the offline tests | ADOPT LATER | 2 h |
| Hosting hardening: dedicated user, limited files, outbound network limited to Gloo, Jev, YouVersion | ADOPT LATER | 4 to 8 h plus review |
| Append-only per-case access and revision log | ADOPT LATER (idea) | 8 to 16 h |
| Rule packs as reviewed data with typed handlers | ADOPT LATER (idea) | 20 to 40 h |
| Repeat each arm in the skills A/B | IDEA ONLY | about 1 h |
| `license` and `compatibility` in our SKILL.md | IDEA ONLY | 0.5 h |
| Pi's loop and hooks as Nury's loop | NO | 30+ h, for no gain |
| Steering and follow-up messages | NO | n/a |
| Context transforms and compaction | NO | n/a |
| Arbitrary code extensions | NO | n/a |
| Pi's approval and permission model | NO | n/a |
| `pi-ai` in place of `gloo_client.py` | NO | 15+ h |
| On-demand skills | NO | n/a |
| RPC or SDK modes | IDEA ONLY | n/a |

## 5. Recommendation for the roadmap "from hackathon to real product"

I would not build on Pi. I would keep the engine as it is and take the lessons in this order:

1. **Before 21:00, if approved:** the Gloo retry policy (1.5 hours) and the requirements and test files (0.5 hour). Both are small, and the first protects the live demo from one flaky moment.
2. **First weeks of a real product:** CI on every push; the event subscribe hook so the app and any monitoring read events instead of polling; a price table so cost per package is computed, not assumed; the hosting hardening, because Nury will hold families' information on a server.
3. **Before real churches:** sign-in, per-church separation and encryption at rest (already on the NOT BUILT list), plus an append-only access and revision log per case, so a church can answer who opened a case.
4. **Later:** rule packs as reviewed data with an approval flow, and a rule editor, so a church or a denomination could add a rule without a developer. Never as loadable code.
5. **Revisit Pi only if Nury needs tools.** For example a read-only search of a church's saved cases. Then a harness like `pi-agent-core` could run that feature, behind our floor and our approval gate, with each tool listed and logged. That needs its own design review, and I have not planned it.

What I would not change: the model has no tools, the engine decides each step, a person approves each stage, and the floor is not an add-on.

## 6. What this review does not prove

- I did not run Pi, so I cannot say how it behaves.
- I did not read most of its code (section 2), so a verdict of NO on a part I only read about in documentation is a verdict on the design as documented.
- The hour costs are my estimates.
- I read Pi at one commit. It changes quickly.
- Nothing here changes the claims in `TECH_CLAIMS.md`: Nury was not built on Pi and was not inspired by it.
