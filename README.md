# Nury

Nury — An AI Crisis Response Agent.

A family calls a church in the worst hour of its life. The pastor opens Nury, picks the crisis and types what the family said. Nury drafts five stages for the pastor to read: a case summary for the pastor, then a plain-language brief, a list of vetted contacts, a family checklist and a short pastoral message, with the family materials in the family's language. After every stage the pastor can Approve, Edit or Stop. Nothing reaches the family except through the pastor. Nury is not a pastor, counselor, doctor or lawyer, and never claims to be one.

Entered by Juan Peláez under 3Metas. Hackathon registration is under jkpelaez@hotmail.com (Solo Hacker ticket T000857383). <!-- Juan: confirm this line before the repo goes public. It prints a personal email and a ticket number. -->

License: MIT.

## Two live playbooks

- **Immigration detention or raid.** Legal information from a reviewed source file, with every point cited, and a pointer to an attorney.
- **Hospital emergency.** A family member is in the ER or ICU. Information only: no medical advice, diagnosis or prognosis.

Two more crises (sudden death in a family, house fire or displacement) appear as "coming soon" cards and cannot be run. A crisis is a folder under `code/playbooks/`, not engine code.

## How it works, in four lines

1. The pastor types the intake and confirms which names to protect. Nury swaps names, phones, addresses and IDs for tokens before anything leaves the app.
2. Claude (Sonnet 4.6) writes each stage through Gloo AI Studio's guarded endpoint. Plain-code rules check the draft, then Jev, a classifier from TypeSafe, checks it too.
3. A draft that fails is rewritten with the reasons, up to three tries, then handed to the pastor. The pastor never sees an unsafe draft.
4. After every stage the pastor approves, edits or stops. Nury has no send path: the pastor copies the text and shares it by hand.

## Run it

Needs Python 3.12.

```
pip install -r code/requirements.txt
export GLOO_API_KEY=...            # or put it in a .env file at the repo root (gitignored)
cd code
python3 -m app.server              # http://127.0.0.1:8080  (set PORT to change it)
```

Keys come from the environment only. Never commit one: `python3 code/tools/scan_keys.py` checks the tracked files.

- `JEV_API_KEY` turns the Jev gate on. Without it, drafts are checked by the plain-code rules alone.
- `YVP_APP_KEY`, `YVP_BIBLE_ES` and `YVP_BIBLE_EN` turn on exact verse text from YouVersion. Without them Nury uses a verified bank of public-domain verses.
- `NURY_FEEDBACK` (off by default) records what a pastor changes, without names, for a person to review. Nothing has been learned from real use.

## Test it

```
code/test.sh                              # product tests: offline, no keys, no network
python3 -m pytest -q evaluations/tests    # evaluation tests (needs pytest, PyYAML, markdown)
```

The evaluation harness runs the scenarios against the real service and spends money: see `evaluations/README.md`.

## Where to read more

| You want | Read |
|---|---|
| The whole story, in plain words | `documents/product/HOW_IT_WAS_BUILT.md` (also in the app at `/how-it-was-built`) |
| Exact facts for engineers | `documents/product/TECHNICAL_REFERENCE.md` |
| What is built and what is not | `documents/FEATURES.md` |
| Every technical claim, with its evidence | `documents/TECH_CLAIMS.md` and `documents/product/CLAIMS_AUDIT.md` |
| The architecture | `documents/ARCHITECTURE.md` and `documents/architecture/diagrams.html` (11 tabs, open in a browser) |
| Everything in one page with a side menu | `documents/hub/index.html` (rebuild with `python3 documents/hub/build.py`) |
| How the engine thinks | `documents/product/ENGINE_WALKTHROUGH.md` |
| The learning loop | `documents/product/LEARNING_LOOP.md` |
| The decision log | `BUILD_LOG.md` |
| The deck and scripts | `presentation/` |

Layout: `code/` (the engine in `code/nury`, the app, the playbooks, tools, tests), `evaluations/`, `presentation/`, `video/`, `documents/`, `branding/`, `candidates/`, `agents/`.

## Privacy

Nury removes direct identifiers before anything reaches a language model or Jev. Names, phone numbers, emails, street addresses, dates of birth and ID numbers become tokens inside Nury before a request goes out; the model sees tokens, not names, and the real values are put back in the answers the pastor sees. The pastor confirms which names to protect. Limits: details such as a workplace or a rare job can still hint at who someone is, and a name the pastor did not protect is not removed. Cases are saved in Nury; nothing is sent to the family.

## Status

Tested on synthetic families only. No real pastor has used Nury.

Nury is a web app. Today one shared pool of cases and one shared church network are visible to everyone who can reach the app. There is no sign-in, no accounts and no encryption at rest yet. A hosted version for many churches needs all three, plus separation between churches. See `documents/FEATURES.md`.

## Disclosure

The Jev decision API from TypeSafe is used as typed judges in our evaluation harness and as a run-time draft classifier; disclosed as third-party technology per the rules.

## Credits

The video narration is an AI-generated voice (ElevenLabs).

Photo, illustration and font credits: `branding/IMAGES.md`.
