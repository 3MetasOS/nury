# Pattern: an approve-gated stage pipeline for high-stakes drafting

The part of Nury you can lift out and use somewhere else. The code references are real files in this repository. What it does not give you is listed at the end. The other domains are ideas, not claims. Crises, rules and evaluations are plain files: see About.

## The one-sentence version

> A model drafts in stages. Rules and a second classifier check each draft before a human sees it. A failing draft is rewritten a few times, then handed to the human, who approves, edits or stops every stage. Nothing leaves except through the human.

In more detail: later stages are built from the human's version of the earlier ones, and the human sends anything that goes out.

## When to use it
- The output goes to a person in a hard moment, and one wrong sentence has a real cost, such as a promise, a prediction or a made-up phone number.
- A trained human is available and must stay responsible. The model is a drafting aid, not the decision maker.
- The text must come only from sources you have vetted, and every point must be traceable.
- You can write down, in plain words, what an unsafe draft looks like.

Do not use it when speed matters more than review. Do not use it when no human will read each stage, or when the model must act on the world directly.

## The five parts

1. **Stages.** The task is cut into steps. Each step has its own prompt, its own list of checks and its own inputs. A stage may read the approved text of earlier stages and nothing else. Files: `code/playbooks/*/stages.json`, `code/playbooks/*/prompts/`, `code/nury/stages.py`, `code/nury/playbook.py`.
2. **A gate after each stage.** The human approves, edits or stops. Approve passes the text on. Edit replaces it, and later stages use the edited text. Stop hands the whole job back to the human. Files: the gate in `code/app/server.py` and the run loop in `code/nury/engine.py`.
3. **Rules plus a second opinion.** Code rules reject first. They cover banned phrases, the required disclaimer, only vetted links and numbers, and the right language. Then a second classifier that is not the writer (Jev, in Nury) answers fixed yes or no questions with a probability. A draft over the set line is rejected. The writer gets the reasons for a rewrite, never the unsafe draft. Files: `code/nury/guardrails.py`, `code/nury/checks.py`, `code/nury/rules.py`, `code/nury/jev_gate.py`.
4. **Bounded retries.** Each stage gets three attempts: the first draft and two rewrites. After that the stage stops and the human takes over. Hard limits on repair calls and HTTP retries keep cost and time bounded too. Files: `MAX_ATTEMPTS` in `code/nury/engine.py`, `code/nury/gloo_client.py`.
5. **Audit, privacy, no send path.** The system logs every call, rule hit, Jev decision and human action. Names and identifiers become tokens before anything goes to a model. The real values come back only inside the app. The app has no button that sends to the family. The human copies the text and sends it by hand. Files: `code/nury/audit.py`, `code/nury/ledger.py`, `code/nury/privacy.py`.

## What to copy
- The engine loop in `code/nury/engine.py`, and the stage and playbook loaders (`stages.py`, `playbook.py`).
- The check registry and the rule files (`checks.py`, `rules.py`, `guardrails.py`). Keep the safety floor in code, so a playbook can add rules but cannot remove them.
- The Jev gate (`jev_gate.py`) as a template for any second-opinion classifier. It has fixed questions and a rule for when the classifier cannot answer.
- The privacy layer (`privacy.py`) and the audit and ledger files.
- The test habit: a leak test (90 checks per playbook), a negative test for every rule, and a test that builds a new playbook from scratch (`ADD_A_RULE.md` and the playbook tests).
- The written limits. `documents/product/WHAT_DID_NOT_WORK.md` and `ECONOMICS.md` say where this pattern broke for us.

## What it does not give you
- **Safety by itself.** Rules and a classifier lower the chance that an unsafe draft reaches the human. They do not make the human's review unnecessary. In our runs a model sometimes wrote sentences no vetted source supported, and the checks passed them.
- **A calibrated classifier.** We smoke-tested our Jev gate on 20 pairs. We do not know its false-reject rate.
- **Quality of tone or truth.** A judge for warmth sits near 3 of 5 against a target of 4. It is noisy, and no human has rated warmth.
- **Security and hosting.** There is no sign-in and no encryption at rest. There is one shared pool of cases and one shared key with no budget cap.
- **Evidence from real users.** We tested on synthetic families only. No real pastor has used it.
- **Low cost under failure.** A stage that never passes still costs three attempts. The worst case computed from the code is 135 model calls for one case (`ECONOMICS.md`).

## Three other places it could apply (ideas, not claims)
We have not built or tested any of these.
1. **A small clinic drafting patient discharge instructions.** A nurse approves each section. The rules block dosage changes the chart does not support.
2. **A legal aid office drafting plain-language letters to tenants.** A paralegal approves each step. The rules allow only statutes and forms the office has vetted.
3. **A disaster relief hotline drafting evacuation and shelter messages.** A coordinator approves each message. The rules allow only addresses and phone numbers from a verified list.

In each case the human stays the sender, and a person who knows the field vets the sources. Each would need its own rules and its own expert review. We did not do that review for Nury either: no attorney has reviewed our sources.
