# Nury architecture diagrams

Open `diagrams.html` in a browser. It is one page with ten tabs, drawn as inline SVG from the code in this repo. It works offline and fits a phone screen.

| Tab | What it shows |
|---|---|
| Context | The pastor, the Nury app, the Gloo guarded Responses endpoint, the vetted sources, and the audit log. It also shows what Nury does not have: open web access and any way to send to the family. |
| Layers | App, engine, safety floor, playbook, and evals. The engine owns running a stage. The safety floor lives in code. A playbook is data and cannot remove the floor. |
| Playbook | The folder a crisis is made of, what the loader checks, how `when` paths work, and which playbooks exist. Detention is the first. Hospital is a test fixture. |
| Run flow | Five stages, an approval gate after each, how edited text carries forward, and the four outcomes. |
| Correction | One stage: draft, check, reject with a reason category, regenerate, three attempts, then escalate. It also marks where fault injection plugs in. |
| Privacy | How names and numbers become tokens before a request leaves, where the map stays, and the leak test that checks the request body. |
| Sources | The playbook sources, the DOJ official list and the church network, and the checks that keep contacts exact and unranked. |
| Skills | The voice and grounding skills, what the loader refuses, and how the audit log records them. |
| Case file | The case folder the app saves, the next-steps map, and revision v1 to v2. |
| Evals | Scenarios and attacker intakes to the scorecard, the three judge layers (deterministic, Jev, the red-team panel), the review canvas, and where each API key is used. |

## How to read the boxes

- Solid: the thing exists in the repo.
- Amber: where a guarantee lives.
- Dashed red: something Nury does not have, on purpose.
- Dashed grey: a test fixture, planned, or built but not yet checked live. The box label says which.

## Keeping it true

Every box names a file or folder you can open. If code changes shape, change the diagram in the same commit. The SVG is plain markup, so edit `diagrams.html` directly.

The same page is published as a canvas for Juan. This file is the source.

## Privacy

Nury sends no direct identifiers to a model. Names the pastor protected, phones, emails, street addresses, dates, A-numbers, case numbers and ID numbers are swapped for tokens before the request goes to the model, and swapped back when the reply arrives. The map is kept by the app and in the saved case, and is never sent to the model. Honest limit: this removes direct identifiers. Context can still hint at who a person is. The proof is a leak test that captures the exact request body for all five stages of both playbooks, including a rejected draft and a pastor edit that adds a new name, and finds none of the canary names or numbers. Details: `code/INTERFACE.md`, section Privacy.
