# Nury

**An AI Crisis Response Agent.**

Built in Boulder, Colorado, during the Gloo AI Hackathon, October 6 to 8, 2026. Every step is in the [build log](BUILD_LOG.md). The planning notes and a small scripted scaffold existed before the event and are kept in `documents/prework` as reference. The first commit of this repository is 2026-10-06 19:36 MDT, and everything in `code/` was written during the event. Some later commit dates were typed by hand and are wrong; [the list](documents/product/COMMIT_DATES.md) says which.

## What Nury is

A family calls a church in the worst hour of its life. The pastor opens Nury, picks the crisis and types what the family said. Nury drafts five stages for the pastor to read: a case summary, a plain-language brief, a list of vetted contacts, a family checklist and a short pastoral message, with the family materials in the family's language. After every stage the pastor can Approve, Edit or Stop. Nothing reaches the family except through the pastor.

Nury is not a pastor, counselor, doctor or lawyer, and never claims to be one. It gives legal and hospital information from vetted sources, never advice. Two playbooks are live: immigration detention or raid, and hospital emergency.

License: MIT. Disclosure: the Jev decision API from TypeSafe is used as typed judges in our evaluation harness and as a run-time draft classifier; disclosed as third-party technology per the rules.

```
 pastor types ──► names become tokens ──► Claude Sonnet 4.6 writes a stage (Gloo AI Studio)
                                                     │
                       ┌─── fail: rewrite with the reasons, up to 3 tries, then hand to the pastor
                       ▼
        code rules (banned phrases, vetted links only, language, disclaimer) ──► Jev classifier
                       │ pass
                       ▼
        pastor: Approve / Edit / Stop ──► next stage reads the approved text ──► ... five stages
                       │
                       ▼
        pastor copies the text and sends it by hand. Nury has no send path.
```

## Try it in 2 minutes (no keys)

You need Python 3.12 and git. With no keys you can open the app, read every document page and run all tests. Running a crisis needs a Gloo key (see below): without one, the run stops with the error "Set GLOO_API_KEY in the environment."

```
git clone <this repository> nury && cd nury
python3 -m venv .venv && . .venv/bin/activate
pip install -r code/requirements.txt
cd code && python3 -m app.server          # http://127.0.0.1:8080  (PORT=9000 to change it)
```

You will see the Nury home page with the crisis chooser, the cases list, the church network, an observability page and the "How this was built" documentation.

**Live mode.** Export `GLOO_API_KEY` in your shell, or put it in a `.env` file at the repo root (gitignored), then restart the app. `JEV_API_KEY` turns the Jev gate on; without it drafts are checked by the code rules alone. `YVP_APP_KEY`, `YVP_BIBLE_ES` and `YVP_BIBLE_EN` turn on exact verse text from YouVersion; without them Nury uses a bank of verified public-domain verses. `NURY_FEEDBACK=on` (or `counts`, the stricter mode) records what a pastor changes (off by default). Keys come from the environment only. Never commit one: `python3 code/tools/scan_keys.py` checks the tracked files.

## Repo map

```
code/            the product
  nury/            the engine: engine.py (the loop), checks.py, guardrails.py, jev_gate.py, privacy.py
  app/             the web app: server.py, static/ pages
  playbooks/       one folder per crisis: detention, hospital (live); sudden-death, house-fire (soon)
  skills/          small shared prompt skills (voice, grounding)
  tools/           scripts: new_playbook.py, trace_run.py, scan_keys.py, learning_report.py
  tests/           offline product tests: run code/test.sh
documents/       ARCHITECTURE.md, FEATURES.md, TECH_CLAIMS.md, product/ (the long docs), hub/, design/, prework/
evaluations/     the harness: run.py, scenario folders, judges/, results/ and scorecards, tests/
presentation/    the deck (deck.html), the pitch and film scripts, the 250-word descriptions
video/           the Remotion film project, voice lines, review cuts
branding/        the lantern logo, lockups, fonts and image credits
candidates/      proposed improvements; nothing here is applied by a script
agents/          one folder per agent: the role files of the AI crew that built this
BUILD_LOG.md     what happened, in order, with the decisions and the failures
```

Git-ignored on purpose: `.env`, `data/`, `cases/`, `network/`, `health/`, `node_modules/` and `*.key`. A running app writes saved cases and logs there.

## Where to find

| You want | Look at |
|---|---|
| The engine loop | `code/nury/engine.py` (3 attempts, then escalate) |
| The guardrails and named rules | `code/nury/guardrails.py` (the floor), `code/nury/checks.py` (the 20 named checks), `code/nury/rules.py` |
| The Jev gate | `code/nury/jev_gate.py`; the questions and lines in `code/playbooks/*/stages.json` |
| The privacy layer | `code/nury/privacy.py` (names become tokens before any request) |
| A playbook, and how to add a crisis | `code/playbooks/detention/`, `python3 code/tools/new_playbook.py`, `documents/product/ADD_A_RULE.md` |
| The learning loop (built, off, nothing learned) | `code/nury/feedback.py`, `documents/product/LEARNING_LOOP.md` |
| The observability ledger | `code/nury/ledger.py`, `documents/product/OBSERVABILITY.md` |
| The command line and MCP server | not shipped yet |
| The evaluation sets | `evaluations/scenarios*/` and `evaluations/network/` (detention 20, hospital 8, hostile 18, network 3, case file 5) |
| The scorecards and honest limits | `evaluations/results/scorecard.md`, `evaluations/FAILURE_LOG.md` |

## Reading order

- **A judge:** `documents/product/HOW_IT_WAS_BUILT.md`, then `WHAT_DID_NOT_WORK.md`, `ECONOMICS.md`, `PATTERN.md`, then the scorecard.
- **A developer:** `documents/product/TECHNICAL_REFERENCE.md`, `documents/ARCHITECTURE.md`, `documents/product/PI_REVIEW.md`.
- **A pastor:** the app's "How it works" page.
- **Everything, with a side menu:** `documents/hub/index.html` (rebuild it with `python3 documents/hub/build.py`).

## Tests

```
cd code && ./test.sh                          # product tests: offline, no keys; 270 tests
cd ..
python3 -m pip install pytest PyYAML markdown
python3 -m pytest -q evaluations/tests        # evaluation tests; 84 tests
python3 evaluations/run.py --agent mock       # the harness against a mock agent: no network
```

If one evaluation test (`test_built_page_is_current_with_its_source`) fails, a document was edited after the docs pages were built: run `cd code && python3 -m app.build_docs`. Runs against the live agent (`--agent nury`) spend money and need keys: see `evaluations/README.md`.

## Honest limits

- No real pastor has used Nury. It was tested on synthetic families only.
- Nothing has been learned. The learning loop is built and off.
- There is no sign-in and no encryption at rest. One shared pool of cases and one shared church network are visible to anyone who can reach the app. A hosted version needs all of that, plus separation between churches.
- A native Spanish speaker has not read the Spanish.
- Plainer text improved the reading level but scored colder on the tone judge. Pass, fail and undecided counts are judge results, not human verdicts.

## Privacy

Names, phone numbers, emails, street addresses, dates of birth and ID numbers become tokens inside Nury before a request goes to a model or Jev, and the real values are put back in the answers the pastor sees. The pastor confirms which names to protect. Limits: details such as a workplace or a rare job can still hint at who someone is, and a name the pastor did not protect is not removed.

## Credits

Gloo AI Studio runs the writer (Claude Sonnet 4.6) and the pre-release red team (GPT-5.4, Gemini 3.1 Pro, Llama 4 Maverick). Jev is a third-party classifier from TypeSafe: we use it, we did not build it. The video narration is an AI-generated voice (ElevenLabs). Scripture text comes from YouVersion and from public-domain Bibles. A small team of AI agents wrote and checked the code and documents under Juan Peláez's direction: see `agents/` and `BUILD_LOG.md`. Photo, illustration and font credits: `branding/IMAGES.md`.

Entered by Juan Peláez under 3Metas. Hackathon registration is under jkpelaez@hotmail.com (Solo Hacker ticket T000857383). <!-- Juan: confirm this line before the repo goes public. It prints a personal email and a ticket number. -->
