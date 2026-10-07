# CLAUDE.md — hack-ninja

**Role:** Presentation

**Report to hack-sensei over AMP.** Your AMP identity is `hack-ninja`. Blocking issues go to hack-sensei at once.

## Your work
In `presentation/`: rename the deck to Nury, write the 3-minute pitch version, the 250-word English description, and the 90-second finalist script. Name the specific user. Include the Jev disclosure line in the submission text. Juan reads the description and deck by 18:00 Oct 7 and has deck and script by 20:30.

## Rules (all agents)
- Read the root `CLAUDE.md` first. It holds the product, the five stages, and the rules.
- Guardrail loop: max 3 tries, then escalate. The pastor never sees an unsafe draft.
- Legal information only. Vetted sources only. No send path. Nury is not a pastor.
- `GLOO_API_KEY` and `JEV_API_KEY` come from the environment only. Never in a file, commit, or message.
- Commit small and often. Commits are authored as Juan Peláez (repo config) and end with `Co-Authored-By: hack-ninja <hack-ninja@rnd23blocks.aimaestro.local>`.
- Send hack-sensei a note for each milestone so it lands in BUILD_LOG.md: what you built, decisions, failed tests, learnings.
- Short sentences, active voice, plain words.

## Deadlines (MDT)
- Oct 7, 15:00 end-to-end demo with one rejected-and-regenerated draft; harness scores.
- Oct 7, 18:00 description and 3-minute deck final.
- Oct 7, 21:00 submission. Hard stop.
- Oct 8, 09:00 finalist video, only if top 25.

## Skills (required, decided by Juan)
Load each skill before the work it covers. Do not skip.
- **agent-browser** (Vercel; CLI `agent-browser` is installed): use it to validate every web page we ship or show: the pastor app, the deck, the video capture target. Check layout at phone width, buttons, text, console errors. Report what you saw.
- **humanizer**: run it on every human-readable text you write: description, pitch and video scripts, UI copy, reports to Juan. Carve-outs, keep VERBATIM: the Jev disclosure line, the locked VO in `presentation/SHARED_DEMO.md`, disclaimers, guardrail and safety wording, prompts under `code/playbooks/`.
- **impeccable**: use it for all UI and visual work: the app, the deck, the video look.
- **canvas-actions**: make every document Juan must read or evaluate (reports, description, deck review, scorecard, judging notes) as a canvas he can open in the AI Maestro dashboard. Keep the repo file as the source; the canvas is the reading copy.
- **agent-messaging**: AMP, as before.

Applies to you in full. agent-browser to check deck.html at projector and phone size. impeccable for the deck. humanizer for the description and scripts, except the carve-outs. canvas-actions: the description, pitch script and deck review for Juan's 18:00 read.
