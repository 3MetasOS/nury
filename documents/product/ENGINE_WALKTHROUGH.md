# How the engine thinks

This note explains how Nury's core works: the cycle for one stage, the five-stage run, a real trace, the files, what we chose not to build, and where the design came from. Line numbers are for `code/nury/engine.py` at commit `50668d6` and may move; the function names will not.

## 1. The cycle for one stage

One stage is one call of `run_stage` (`engine.py` line 154). The pastor sees only a draft that passed every layer below, or a plain "I'll handle this manually."

1. **Read the inputs.** The engine loads the playbook and the stage, and reads the fields from the approved triage text (line 169). A stage with a `when` condition that does not match is skipped (line 172). It gathers the approved text of the stages this one depends on (line 189) and builds the stage input (line 192, `playbook.build_input`).
2. **Fill in the sources.** Fixed sources come from the playbook's vetted JSON. Dynamic sources are chosen at run time: the church's own contacts, the official list for the state, and the approved verses (`dynamic_source`, line 89). The audit records which entries were offered (line 185).
3. **Build the prompt.** The engine's boundary rules, then the playbook's prompt with its variables filled in, then the skills' text (line 191). The boundary rules are the floor and no playbook can remove them.
4. **Write.** One call to the model (`client.ask`, line 233) through Gloo's guarded endpoint. The privacy layer sits in this call: names, phones, emails, addresses and IDs go out as tokens and come back as real values.
5. **Scripture (pastoral stage only).** The model returns `VERSE`, `WHY` and `MESSAGE`. The engine checks that the verse id is on the approved list (`scripture.parse_output`, line 257), asks a provider for the exact text (`_fetch_verse`, line 330) and builds the draft itself. The model never writes the verse.
6. **Floor and named checks.** `all_violations` (line 207) runs the floor first: banned phrases, one language, the link, phone and email allowlists. Then the checks named in the stage, the checks from its skills, and the checks the engine adds for Scripture. A check returns reasons, never a changed draft. On the pastoral stage the checks look at Nury's own sentences, not the quoted verse (line 260).
7. **Jev gate.** If the draft is clean and the stage lists Jev questions, one batched call to Jev asks them about the draft (line 268, `jev_gate.run`). Jev sees only tokens. A probability at or over the question's line rejects the draft. If Jev cannot answer, the draft passes on the floor and the audit says so.
8. **The loop.** Steps 4 to 7 sit inside `for attempt in range(1, MAX_ATTEMPTS + 1)` (line 224; `MAX_ATTEMPTS` is 3, line 21). A rejected draft is written to the audit as `draft_rejected` with its categories, and goes back to the model as reasons, not as text (`_correction_note`, line 139). The pastor never sees it. After the third failure the stage ends (line 294): no draft, status `escalated`, "I'll handle this manually."
9. **The gate.** A clean draft is shown with a label and the disclaimer (line 302). The pastor approves, edits or stops (line 303). An edit is checked and flagged, not blocked: the pastor owns it. The approved or edited text, with the disclaimer, is saved for later stages (line 325).
10. **The audit.** Every step above writes an event (`audit.py`). The audit holds categories, ids, probabilities and timings. It holds no draft text, except the hidden `draft_rejected` event.

### The run across five stages

`_run_pipeline` (line 384) runs the stages in order. A stage that is not approved, edited or skipped stops the run. **Chaining:** each stage reads the approved or edited text of the stages before it, so a pastor's edit flows forward. After the last stage, `compute_outcome` (line 356) names one of four outcomes: `package_complete`, `stopped_by_pastor`, `escalated` or `blocked` (Gloo's own guardrail refused). The pastor can always save the case or share the text by hand. Nothing is sent to the family.

## 2. A real trace: detention scenario 01

One live run on 2026-10-07 with privacy on, the Jev gate on and YouVersion on. The raw audit file is `documents/product/trace_detention_01.jsonl`. A check in `tools/trace_run.py` refuses to keep a file that contains a protected name, and the file passed: the audit has no names in it. The time is milliseconds since the first event. Each `check` line is written after the Jev gate has answered, because it closes the rules, Scripture and Jev layers together. "Model" is the Gloo time for that attempt.

```
+     0 ms  stage_start      triage    reads: the intake
+     0 ms  gloo_call        triage    attempt 1
+  6380 ms  jev_gate_start   triage    1 question(s) in one call
+  6529 ms  jev_gate         triage    assumes_facts = 0.33 (uncertain)
+  6529 ms  jev_call         triage    149 ms, 898 in / 23 out
+  6529 ms  check            triage    passed=True, 5902 in / 264 out, model 6.377 s
+  6529 ms  gate             triage    approve
+  6529 ms  stage_start      rights    reads: triage
+  6529 ms  gloo_call        rights    attempt 1
+ 11118 ms  jev_gate_start   rights    3 question(s) in one call
+ 11270 ms  jev_gate         rights    gives_legal_advice = 0.06 (pass)
+ 11271 ms  jev_gate         rights    predicts_outcome = 0.03 (pass)
+ 11271 ms  jev_gate         rights    assumes_facts = 0.1 (pass)
+ 11271 ms  jev_call         rights    152 ms, 2001 in / 64 out
+ 11271 ms  check            rights    passed=True, 1990 in / 331 out, model 4.582 s
+ 11271 ms  gate             rights    approve
+ 11280 ms  dynamic_source   attorney  church_network: 1 entries, official_list: 5 entries
+ 11280 ms  stage_start      attorney  reads: triage, rights
+ 11280 ms  skill_applied    attorney  grounding 1.0.0
+ 11280 ms  gloo_call        attorney  attempt 1
+ 31552 ms  jev_gate_start   attorney  1 question(s) in one call
+ 31737 ms  jev_gate         attorney  assumes_facts = 0.42 (uncertain)
+ 31738 ms  jev_call         attorney  185 ms, 3405 in / 23 out
+ 31738 ms  check            attorney  passed=True, 3064 in / 874 out, model 20.258 s
+ 31738 ms  gate             attorney  approve
+ 31738 ms  stage_start      checklist reads: triage, rights, attorney
+ 31739 ms  skill_applied    checklist voice 1.0.0
+ 31739 ms  skill_applied    checklist grounding 1.0.0
+ 31739 ms  gloo_call        checklist attempt 1
+ 47811 ms  jev_gate_start   checklist 1 question(s) in one call
+ 47970 ms  jev_gate         checklist gives_legal_advice = 0.27 (pass)
+ 47970 ms  jev_call         checklist 158 ms, 3451 in / 25 out
+ 47970 ms  check            checklist passed=True, 3909 in / 740 out, model 16.063 s
+ 47970 ms  gate             checklist approve
+ 47971 ms  dynamic_source   pastoral  scripture: 10 entries
+ 47972 ms  stage_start      pastoral  reads: triage, rights, checklist
+ 47972 ms  skill_applied    pastoral  voice 1.0.0
+ 47972 ms  gloo_call        pastoral  attempt 1
+ 54400 ms  jev_gate_start   pastoral  4 question(s) in one call
+ 54542 ms  jev_gate         pastoral  predicts_outcome = 0.03 (pass)
+ 54542 ms  jev_gate         pastoral  claims_pastoral_office = 0.07 (pass)
+ 54542 ms  jev_gate         pastoral  claims_counselor = 0.06 (pass)
+ 54542 ms  jev_gate         pastoral  promises_action = 0.19 (pass)
+ 54542 ms  jev_call         pastoral  142 ms, 2125 in / 83 out
+ 54542 ms  check            pastoral  passed=True, 4282 in / 153 out, model 6.066 s
+ 54542 ms  scripture        pastoral  verse php4_6_7 from youversion
+ 54542 ms  gate             pastoral  approve
+ 54542 ms  outcome                    package_complete
```

What to see: each stage is one model call (4 to 20 seconds) and then one Jev call (about 150 ms). The attorney stage is the slowest (20 seconds) because it writes the longest text. The whole run took about 54 seconds and every stage passed on the first attempt. Two Jev answers fell in the uncertain band and passed (triage 0.33, attorney 0.42).

## 3. The files in `code/nury`

| File | What it does | Lines |
|---|---|---|
| `engine.py` | Runs a stage and a whole run: prompts, the loop, the checks, the gates, chaining, outcomes. | 439 |
| `playbook.py` | Loads a crisis folder, validates it, renders prompts, matches `when` paths. | 302 |
| `guardrails.py` | The floor: boundary rules, banned phrases, language, link, phone and email checks. | 152 |
| `checks.py` | The named checks a playbook can list. | 368 |
| `jev_gate.py` | The Jev classifier gate: questions, lines, privacy step, fail-open. | 176 |
| `privacy.py` | Names and IDs to tokens and back; the wrapper around the model client. | 445 |
| `gloo_client.py` | The one call to Gloo's guarded endpoint. | 87 |
| `skills.py` | Loads the versioned voice and grounding text and checks. | 103 |
| `scripture.py` | The verse bank: approvals, parsing the model's choice, the verse block. | 200 |
| `scripture_providers.py` | Where verse text comes from: the verified bank or YouVersion. | 195 |
| `network.py` | The church's own contacts, kept by the app. | 258 |
| `officiallist.py` | Selects entries from the approved official list by state. | 91 |
| `casefile.py` | Saves an approved package as a case folder and a next-steps map. | 412 |
| `rules.py` | Plain-English descriptions of every rule, for the Rules page. | 96 |
| `audit.py` | The event log. | 30 |
| `stages.py` | An old import path kept so older code still works. | 11 |

The app (`code/app`) is separate: it calls the engine and shows its results. Evaluation (`evaluations/`) drives the same engine and judges the result.

## 4. What we deliberately did not build

- **No agent framework.** The core is plain Python and plain `requests`. A pastor can read all of it.
- **No tool use by the model.** The model writes text. It does not call functions, browse, search or run code. The engine decides every step.
- **No memory beyond the case file.** Nothing carries from one case to the next. A case is the approved text, saved when the pastor chooses.
- **No open web.** Every fact comes from a vetted source file with an approval status. The model has no way to look anything up.
- **No second language model as a reviewer at run time.** Claude writes, our named rules check, and Jev classifies. The red team of three models from other makers is a test-time audit only.
- **No send path.** Nothing reaches the family except through the pastor.

## 5. Where the design came from

Only what the repo and the prework files show:

- **Juan's plan.** The prework brief (`documents/prework/PREWORK.md`) set the shape: a single Python agent, five sequential stages, each ending at a human approval gate, "no frameworks, plain `requests`". Its cycle is: ask, guardrail check, on failure feed the reasons back and retry (at most two retries), and if all fail, escalate to the human. That is the loop in section 1, and `MAX_ATTEMPTS = 3` is the first draft plus two retries.
- **The pattern.** Generate, verify, regenerate, with a person at the gate. We did not invent this pattern and we do not claim to. The choices that are ours: the checks are deterministic code, not another model; the model is shown reasons and never the rejected text; and the pastor never sees an unsafe draft.
- **The judging layer.** `documents/prework/EVAL_DESIGN.md` cites two sources for typed judges that accept when confident and escalate when unsure: the DAIR.AI Academy lab "Jev-as-a-Judge for Agent Evaluations" and "JEV-as-a-Judge: Accept When Confident, Escalate When Unsure" (Li et al., 2026). The 0.80 and 0.20 thresholds for the test-time judges are recorded in that file. Jev is the Jev decision API from TypeSafe, a third-party service. We use it; we did not build it.
- **What was added later, by decision.** The run-time Jev gate (Juan, 2026-10-07), Scripture with a verified bank and YouVersion, the privacy layer, the church network and the official list, and the case file.
- **What the repo shows about borrowed code.** The product code (`code/nury` and the server in `code/app`) imports only the Python standard library and `requests`. The evaluation harness also uses PyYAML and pytest, and the documentation build uses python-markdown. No agent framework or harness is imported anywhere in the repo. The engine in `code/nury` was written during this event by the team's coding agent, hack-jedi, from the prework plan, and its author states that it copied no code from an open-source agent harness. That last point is the author's statement: the repo cannot prove it. The app began from a scaffold named in the project plan, and its origin has not been audited. We did not invent generate, check and regenerate; it is a common pattern.

### Comparison: Pi, a minimal open-source agent harness

Read on 2026-10-07. Nury is not built on Pi and was not inspired by it: the engine was written before this comparison, from the prework brief, and without reference to Pi. This section is only a comparison, so a reader can see what is different and why.

**Sources and how far I verified them.** I read the pages below with a fetch tool. The tool returned summaries of the pages, not the raw text, so the quotes are the summaries' quotes and I did not read the loop source line by line. The project's GitHub page named `github.com/earendil-works/pi` as its final address; search results had named `github.com/badlogic/pi-mono`, and the repository page I opened under that name pointed to the `earendil-works` organization. I treat `earendil-works/pi` as the canonical one. Pi is by Mario Zechner, from the search results; I did not verify that from the pages.

- Repository: https://github.com/earendil-works/pi. Description: "AI agent toolkit: unified LLM API, agent loop, TUI, coding agent CLI". License: MIT. Packages include `pi-ai` ("Unified multi-provider LLM API (OpenAI, Anthropic, Google, etc.)"), `pi-agent-core` ("Agent runtime with tool calling and state management"), `pi-coding-agent` ("Interactive coding agent CLI") and `pi-tui` ("Terminal UI library with differential rendering"). The page also lists packages for telemetry, durable state and an application runtime.
- Agent package README: https://github.com/badlogic/pi-mono/tree/main/packages/agent (the `pi-agent-core` package).
- Loop source: https://github.com/earendil-works/pi/blob/main/packages/agent/src/agent-loop.ts
- Product page: https://pi.dev. README of the coding agent: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/README.md

**Not verified:** the four default tools (`read`, `write`, `edit`, `bash`). The pages I could read do not list them. Nor did I verify how the extension API is typed, or any detail of Pi's behavior that I did not see in the pages above.

#### 1. What Pi is for

Pi describes itself as "a minimal, extensible agent harness that you can make your own." It "ships with powerful defaults but skips features like sub-agents and plan mode." Customization goes through "extensions, skills, prompt templates, and themes," bundled as packages shared through npm or git. Extensions are "TypeScript modules with access to tools, commands, keyboard shortcuts, events, and the full TUI," and skills are "capability packages with instructions and tools, loaded on-demand" (pi.dev). Its main product is a coding agent that a person runs in a terminal and shapes to their own workflow.

#### 2. How the loops differ

| | Pi (`pi-agent-core`) | Nury (`engine.py`) |
|---|---|---|
| Who decides what happens next | The model. After each answer the loop looks for tool calls and runs them. | The engine. The five stages and their order are fixed in the playbook. |
| Tools | The model calls tools. Tool calls run in sequence or in parallel (per the README). | None. The model writes text only. |
| Loop shape | Per the loop source summary: an outer loop for follow-up messages and an inner loop "while there are more tool calls or pending messages": call the model, run tool calls, check for new steering messages. | `for attempt in range(1, 4)` inside each stage: write, check, classify, then regenerate or stop. |
| When it stops | When there are no tool calls and no steering or follow-up messages, on an error or abort, or when a `finishTurn` callback returns `end`. The README also says the loop stops early only if every finalized tool result in a batch sets `terminate: true`. | When a draft passes every layer, after three failed attempts (escalate), or when the pastor stops. |
| What judges the output | The model's own choice to stop. Hooks `beforeToolCall` and `afterToolCall` can block or change a tool call. | Deterministic checks first (the floor and named checks), then a classifier (Jev) with a reject line, then a human gate after every stage. |
| People in the loop | A person can steer or queue follow-up messages while it runs. | A person approves, edits or stops after every stage. An edit is checked and flagged, and the checks themselves do not change. |
| Events | A stream: `agent_start`, `turn_start`, `message_*`, `tool_execution_*`, `turn_end`, `agent_end`. | An audit log: `stage_start`, `gloo_call`, `check`, `jev_gate`, `gate`, `outcome` and others (section 2). |

In short: Pi lets the model decide and gives a person the means to steer. Nury does the opposite on purpose: the engine decides, the model only writes, and checks and a human decide what is allowed through.

#### 3. What we could learn or borrow

- **A small core.** Pi's pitch is that the loop stays small and everything else is an extension. Our engine is 439 lines and the rest sits in separate modules, which is the same instinct. We should keep it that way.
- **A clear event stream.** Pi emits start and end events for runs, turns, messages and tools, and listeners subscribe. Our audit log already records the same kind of facts, and the app derives its progress phases from it. A small subscribe-style hook on `AuditLog` would be a cleaner way to feed the app than reading the list. That is an idea, not built.
- **Extension points with names.** Pi's `beforeToolCall` and `afterToolCall` are named places to add behavior. Our named checks and the Jev questions are the same idea for drafts. Nothing to change.
- **Skills as optional modules.** We already have skills (`voice`, `grounding`), versioned and switched off for comparison. Pi loads skills "on-demand"; ours are listed by name in each stage and always apply.
- **We already have an audit log and skills.** So the new things to learn are small: the event naming and the idea of subscribers.

#### 4. What would not fit

- **Open tool use.** Our safety rests on the model not acting. It cannot search, fetch, run code or read files. Giving it tools reopens the open web and the open filesystem, which the rules rule out.
- **Shell access.** A coding agent's `bash` is the opposite of a crisis agent's floor.
- **No deterministic floor.** Pi leaves permission and confirmation to extensions ("Run in a container, or build your own confirmation flow with extensions"). For Nury those checks are the product, so they are in the core, not an add-on.
- **A model that decides when it is done.** Our stages end when a draft passes the layers or after three attempts, not when the model stops.
- **Parallel tool execution and mid-run steering.** Neither has a place in a fixed five-stage run with a human gate after each.
- **Language.** Pi is TypeScript. Nury is Python, and a pastor can read it. Moving would be a rewrite for no gain.

#### 5. Could `pi-agent-core` be the loop under Nury later?

**Maybe, for one narrow case, and no for the main run.** For the five-stage run: no. Our loop is not a tool loop. Using Pi's loop with no tools would wrap one model call, and we would add a TypeScript runtime and a bridge to the Python engine for nothing. The parts that matter, the checks, the Jev gate, the correction loop and the human gate, would all stay ours.

For a later feature that needs tools, such as a read-only search of a church's saved cases, a harness like this could make sense, behind our floor and our approval gate, with each tool whitelisted and logged. That would need a design review first. It is not planned.

**Not verified:** whether the loop's `finishTurn` callback could carry a correction message and run another turn, which is what our regenerate step does. I saw the callback named in the summary and did not read how it works. I would read the source itself before any decision.

## 6. How a developer extends it

| To add | Where | Start here |
|---|---|---|
| A rule or check | `code/nury/checks.py`, named in `stages.json`, described in `rules.py` | `documents/product/ADD_A_RULE.md` |
| A banned pattern for one crisis | `extra_banned` in the playbook's `playbook.json` | `documents/product/ADD_A_RULE.md`, example 1 |
| A Jev question | `QUESTIONS`, `REASONS` and `CRITERIA` in `code/nury/jev_gate.py`, the same wording in `evaluations/judges/jev_judges.py`, a line in `REJECT_AT` if it needs its own, and a test | `code/INTERFACE.md`, section Jev gate |
| A stage | An entry in the playbook's `stages.json` and a prompt file | an existing stage in `code/playbooks/detention/` |
| A skill | A folder under `code/skills/` with a `SKILL.md`, named in the stage | `code/skills/voice/` |
| A crisis | `python3 tools/new_playbook.py <id> "<Title>"` from `code/` | `code/tools/new_playbook.py`; it creates a folder that cannot run until a person approves its sources and flips its status |
| A source | A JSON file with a `source_id` per entry, approved in `sources/approvals.json` | `code/playbooks/hospital/sources/` |

What is not built: a rule editor, a workflow editor, and a review and approval flow for new rules. Today a change goes in through code, tests and a commit.
