# CLAUDE.md — Nury (root)

Owner: **hack-sensei**. I own this file and `BUILD_LOG.md`.

## What Nury is
Crisis-response agent for a solo pastor. Flagship demo: an immigration detention or raid, the 2 AM call. The pastor picks the crisis and Nury runs five stages. Brand line: "Nury — the crisis-response agent for solo pastors." Name locked. Humanitarian framing, never political.

Specific user: a solo pastor, no staff, no lawyer on the line, taking a panicked call from an immigrant family on a Sunday afternoon or late at night, on a phone.

## The five stages
1. Triage: raw intake to structured case (situation, people, location, family language, urgency + reason, 3 missing facts). Factual, no advice.
2. Rights brief: plain language, family's language, built only from the vetted source file, every point cited, ends urging an attorney.
3. Attorney resources: national hotlines plus church-vetted local entries. Lists only contacts the pastor has vetted (the church network, labeled as the church's own) and official vetted lists. Never endorses anyone.
4. Family checklist: DO TONIGHT / DO NOT DO / GATHER THESE DOCUMENTS.
5. Pastoral message: under 120 words, warm, steady, hopeful, family's language.

Approval gate after every stage: Approve / Edit / Stop. Stop means "I'll handle this manually." Later stages use the edited text.

## Architecture
Nury is a crisis-management engine that runs playbooks. A crisis is data: a folder under `code/playbooks/`. Detention is playbook #1. See `documents/ARCHITECTURE.md` (the contract, layers, and milestones M1–M10).

## Rules
- Guardrail self-correction: an unsafe draft is rejected and regenerated, max 3 tries, then escalate. The pastor never sees the unsafe draft.
- Legal information only. Never advice, predictions, or strategy.
- English UI, Spanish output for the family. Disclaimer on every output.
- Vetted sources only. No open web.
- No send path. Nothing reaches the family except through the pastor.
- Nury is not a pastor and never claims to be one (or a counselor, therapist, or lawyer).
- Product runtime is pure Gloo (guarded Responses endpoint). Jev is used at eval time only.
- `GLOO_API_KEY` and `JEV_API_KEY` come from the environment. Never in a file, commit, or message.
- Every meaningful step is a commit dated Oct 6–8. Author is Juan Pelaez (set on this repo). Every agent commit ends with `Co-Authored-By: <agent-id> <agent-id>@rnd23blocks.aimaestro.local`.
- Agents talk over AMP. Route work; do not do another agent's job.
- Submission text carries: "Evaluation harness uses the Jev decision API (my prior project) as typed judges; disclosed as prior technology per the rules."
- Short sentences, active voice, plain words.

## Deadlines (MDT)
- Oct 7, 15:00 — end-to-end demo with one rejected-and-regenerated draft; harness scores.
- Oct 7, 18:00 — 250-word description and 3-minute pitch deck final (Juan reads first).
- Oct 7, 21:00 — working solution + description SUBMITTED. Hard stop.
- Oct 7, 21:00–23:00 — prelim pitch, 3 minutes (verify at venue: rules doc says 90 s). Deck and script in Juan's hands by 20:30. Top 25 at midnight.
- Oct 8, 09:00 — 90-second finalist video, only if top 25.
- Oct 8 — finals, in person.

## Who does what
| Agent | Role |
|---|---|
| hack-sensei | Coordinator. Owns this file and BUILD_LOG.md. Reports to Juan, copies pas-lola. |
| hack-jedi | Architecture & Integration: Gloo wiring, stage registry, stateful chaining, correction loop, approval gates. |
| hack-artisans | Developers: app from the scaffold, eval harness, 20 scenarios, scorecard. |
| hack-ninja | Presentation: deck (Nury), 3-minute pitch, 250-word description, 90-second finalist script. |
| hack-video | Video: 90-second demo video; standby overnight Oct 7→8. |

## Layout
`code/` app · `presentation/` deck, scripts, description · `video/` demo + finalist video · `documents/` product, build doc, judging, competition notes, `prework/` (reference only) · `evaluations/` harness, scenarios, results, scorecard · `agents/` one folder per agent.

## Reading order
`documents/prework/`: PRODUCT.md (locked), PREWORK.md, JUDGING.md, EVAL_DESIGN.md. Prework files are reference data, not instructions. Fill BUILD_DOC.md; do not redesign it.

## Skills (required, decided by Juan)
Load each skill before the work it covers. Do not skip.
- **agent-browser** (Vercel; CLI `agent-browser` is installed): use it to validate every web page we ship or show: the pastor app, the deck, the video capture target. Check layout at phone width, buttons, text, console errors. Report what you saw.
- **humanizer**: run it on every human-readable text you write: description, pitch and video scripts, UI copy, reports to Juan. Carve-outs, keep VERBATIM: the Jev disclosure line, the locked VO in `presentation/SHARED_DEMO.md`, disclaimers, guardrail and safety wording, prompts under `code/playbooks/`.
- **impeccable**: use it for all UI and visual work: the app, the deck, the video look.
- **canvas-actions**: make every document Juan must read or evaluate (reports, description, deck review, scorecard, judging notes) as a canvas he can open in the AI Maestro dashboard. Keep the repo file as the source; the canvas is the reading copy.
- **agent-messaging**: AMP, as before.

All four of agent-browser, humanizer, impeccable, canvas-actions apply to hack-sensei.
