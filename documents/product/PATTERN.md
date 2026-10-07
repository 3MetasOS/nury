# Pattern: an approve-gated stage pipeline for high-stakes drafting

Written 2026-10-07 by hack-ninja for hack-sensei. One page. This is the part of Nury you can lift out and use somewhere else. The code references are real files in this repository. What it does not give you is listed at the end, and the other domains are ideas, not claims.

## The one-sentence version
A model drafts a piece of text in stages. After each stage, rules and an independent classifier check the draft before a human ever sees it. A failing draft is rewritten a bounded number of times, then handed to the human. The human approves, edits or stops each stage, and later stages are built from the human's version. Nothing leaves the system except through the human.

## When to use it
- The output goes to a person in a hard moment, and one wrong sentence has a real cost (a promise, a prediction, a made-up phone number).
- A trained human is available and must stay responsible. The model is a drafting aid, not the decision maker.
- The text must be built only from sources you have vetted, and every point must be traceable.
- You can write down, in plain words, what an unsafe draft looks like.

Do not use it when speed matters more than review, when no human will read each stage, or when the model must act on the world directly.

## The five parts

1. **Stages.** The task is cut into steps, each with its own prompt, its own list of checks and its own inputs. A stage may read the approved text of earlier stages and nothing else. Files: `code/playbooks/*/stages.json`, `code/playbooks/*/prompts/`, `code/nury/stages.py`, `code/nury/playbook.py`.
2. **A gate after each stage.** The human approves, edits or stops. Approve passes the text on. Edit replaces it, and later stages use the edited text. Stop hands the whole job back to the human. Files: the gate in `code/app/server.py` and the run loop in `code/nury/engine.py`.
3. **Rules plus an independent classifier, before the human sees a draft.** Code rules (banned phrases, required disclaimer, only vetted links and numbers, the right language) reject first. Then a second classifier that is not the writer (Jev, in Nury) answers fixed yes/no questions with a probability. Reject at a set line, ask for a rewrite with the reasons (never the unsafe draft). Files: `code/nury/guardrails.py`, `code/nury/checks.py`, `code/nury/rules.py`, `code/nury/jev_gate.py`.
4. **Bounded retries, then escalate to the human.** Three attempts per stage (the first draft and two rewrites). After that the stage stops and the human takes over. The loop has hard limits on repair calls and HTTP retries too, so cost and time stay bounded. Files: `MAX_ATTEMPTS` in `code/nury/engine.py`, `code/nury/gloo_client.py`.
5. **Audit trail, privacy in, no send path.** Every call, rule hit, Jev decision and human action is logged. Names and identifiers become tokens before anything goes to a model, and the real values come back only inside the app. The app has no button that sends to the family. The human copies the text and sends it by hand. Files: `code/nury/audit.py`, `code/nury/ledger.py`, `code/nury/privacy.py`.

## What to copy
- The engine loop in `code/nury/engine.py`, and the stage and playbook loaders (`stages.py`, `playbook.py`).
- The check registry and the rule files (`checks.py`, `rules.py`, `guardrails.py`). Keep the safety floor in code, so a playbook can add rules and cannot remove them.
- The Jev gate (`jev_gate.py`) as a template for any second-opinion classifier with fixed questions and a failing-open rule.
- The privacy layer (`privacy.py`) and the audit and ledger files.
- The test habit: a leak test (90 checks per playbook), a negative test for every rule, and a rule that a new playbook can be built from scratch by a test (`ADD_A_RULE.md` and the playbook tests).
- The written limits: `documents/product/WHAT_DID_NOT_WORK.md` and `ECONOMICS.md` say where this pattern broke for us.

## What it does not give you
- **Safety by itself.** Rules and a classifier lower the chance that an unsafe draft reaches the human. They do not make the human's review unnecessary. In our runs a model sometimes wrote sentences no vetted source supported, and the checks passed them.
- **A calibrated classifier.** Our Jev gate was smoke-tested on 20 pairs. We do not know its false-reject rate.
- **Quality of tone or truth.** A judge for warmth sits near 3 of 5 against a target of 4, it is noisy, and no human has rated warmth.
- **Security and hosting.** No sign-in, no encryption at rest, one shared pool of cases, one shared key with no budget cap.
- **Evidence from real users.** Tested on synthetic families only. No real pastor has used it.
- **Low cost under failure.** A stage that never passes still costs three attempts. The worst case computed from the code is 135 model calls for one case (`ECONOMICS.md`).

## Three other places it could apply (ideas, not claims)
We have not built or tested any of these.
1. **A small clinic drafting patient discharge instructions,** where a nurse approves each section and the rules block dosage changes the chart does not support.
2. **A legal aid office drafting plain-language letters to tenants,** where a paralegal approves each step and the rules allow only statutes and forms the office has vetted.
3. **A disaster relief hotline drafting evacuation and shelter messages,** where a coordinator approves each message and the rules allow only addresses and phone numbers from a verified list.

In each case the human stays the sender, and the sources are vetted by a person who knows the field. Each would need its own rules and its own review by an expert, which we did not do for Nury either (no attorney has reviewed our sources).
