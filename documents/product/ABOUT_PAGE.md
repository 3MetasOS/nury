# About page: text for the app

Page-ready text for hack-artisans. Written 2026-10-07 by hack-ninja. Timeless on purpose: it describes what Nury is and how it is made, and keeps the hackathon as history. Facts come from `HOW_IT_WAS_BUILT.md`, `TECH_CLAIMS.md` and the scorecards. The memorial is not written here: hack-artisans inserts Juan's approved text at the marker.

Links used (the app's own pages): `/how-it-was-built`, `/what-did-not-work`, `/economics`, `/pattern`, `/standards`, `/build-log`.

---

## What Nury is

Nury is an AI Crisis Response Agent for churches.

When a family calls a pastor in crisis, the pastor picks the kind of crisis and types what the family said. Nury drafts the stages that crisis defines, for the pastor to read. Each live crisis has five. For an immigration matter they are a case summary, a plain-language brief with every point cited, a list of vetted contacts, a family checklist and a short pastoral message. Family materials come out in the family's language.

After every stage the pastor can Approve, Edit or Stop. Later stages build on the pastor's edits. Nothing reaches the family except through the pastor: Nury has no way to send a message. Nury is not a pastor, a counselor, a doctor or a lawyer, and it gives information, never advice.

## Built to grow

**Crises are workflows.** A crisis is a defined workflow, kept as a folder of plain files: its stages, its prompts, its vetted sources and its possible outcomes. Two are live and two more are listed as coming soon. Adding another means adding a folder, not changing the engine. A script scaffolds the folder from a template, in a state that cannot run until a person approves its sources, and a test checks that the scaffold loads.

**Rules can be added.** Every draft is checked by named rules. A new rule is one small function, a line that registers it and names it in a stage, one plain sentence for the rules page, and a test. It then shows up in the registry and on the rules page.

**Evaluations can be added.** Scenarios and hostile intakes are plain files, and the judge questions sit in one code file. A new crisis brings its own scenarios. A proposed improvement is a file too: a script runs it against the same sets before and after, with a gate, and only then does a person decide whether to adopt it.

Anyone with the repository can add a crisis, a rule or a scenario. See `documents/product/ADD_A_RULE.md` and the playbook folder (`code/playbooks/`) in the README. A person still approves the sources and the release.

## How it was made

**Writer.** Claude Sonnet 4.6, through Gloo AI Studio's guarded endpoint, with Gloo's guardrails. Claude writes each stage. It never writes a verse of Scripture.

**Checks.** Twenty named rules and a safety floor read every draft before the pastor does. Jev, a classifier from TypeSafe, checks the draft a second time with fixed yes or no questions. A draft that fails is held back and regenerated, up to three tries, and then Nury steps aside for the pastor. These checks are tripwires, not proofs. The pastor approves every stage.

**Scripture.** The model picks a verse from a list a person approved. The engine inserts the exact text, from YouVersion or from a bank of public-domain Bibles. The version name and its copyright show with every verse.

**Privacy.** Names, phone numbers, emails, addresses, dates of birth and ID numbers become tokens before anything leaves the app. The model sees tokens, not names, and the real values come back only inside the app. Details such as a workplace can still hint at who someone is.

**Our own engine.** The engine is hand-built Python with no agent framework. A crisis is data: a playbook folder holds its stages, prompts, sources and rules, so adding a crisis does not change the engine. Detention and hospital emergency are the two playbooks that can run; two more crises are listed as coming soon.

**Evaluation.** Hand-written scenarios, including hostile intakes meant to push Nury into advice and false claims, are scored by plain-code judges, by Jev as a typed judge, by an outside review and by people. We publish what did not work and the limits: [What did not work](/what-did-not-work).

**Outside review.** Three models from other makers (OpenAI GPT-5.4, Google Gemini 3.1 Pro and Meta Llama 4 Maverick), through Gloo, read sample drafts and flagged problems. We checked them first on 8 drafts with planted problems: all three caught 8 of 8, and they also over-flag safe drafts. The review runs by hand before a release. It is not part of the app at run time, and it only advises: we decide what to change. [Details](/how-it-was-built#outside-review).

**Learning loop.** Built, off by default, and nothing has been learned yet. If it is switched on, it records what a pastor changes, without names, for a person to review. It never changes Nury by itself.

## Where it came from

Nury was built in Boulder, Colorado, during the Gloo AI Hackathon, October 6 to 8, 2026. Every step is in the [build log](/build-log). The planning notes and a small scripted scaffold existed before the event and are kept as reference. Everything in the product code was written during the event.

Nury has been tested on synthetic families only. No real pastor has used it yet.

## In memory

MEMORIAL BLOCK

## Credits

- **Gloo AI Studio** runs the writer and the outside review.
- **TypeSafe** makes Jev, the classifier used as a second check on drafts and as a judge in our tests. We use it; we did not build it.
- **YouVersion** supplies Scripture text, with the public-domain Reina-Valera 1909 and World English Bible as the verified bank.
- **ElevenLabs** made the narration voice in the film. It is an AI-generated voice.
- **A team of AI agents** wrote and checked the code and the documents under Juan Peláez's direction. Entered under 3Metas.
- Photo, illustration and font credits: see the credits in the repository (`branding/IMAGES.md`).
