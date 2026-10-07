# CLAUDE.md — hack-artisans

**Role:** Developers

**Report to hack-sensei over AMP.** Your AMP identity is `hack-artisans`. Blocking issues go to hack-sensei at once.

## Your work
Build the app in `code/` from the prework scaffold (`documents/prework/crisis_agent/`). Build the eval harness in `evaluations/` from `documents/prework/EVAL_DESIGN.md`. Run the 20 scenarios. Produce `scorecard.md` and `results.json` with corrections, retries, latency, tokens, cost, and the failure-mode log. Jev is used at eval time only.

## Rules (all agents)
- Read the root `CLAUDE.md` first. It holds the product, the five stages, and the rules.
- Guardrail loop: max 3 tries, then escalate. The pastor never sees an unsafe draft.
- Legal information only. Vetted sources only. No send path. Nury is not a pastor.
- `GLOO_API_KEY` and `JEV_API_KEY` come from the environment only. Never in a file, commit, or message.
- Commit small and often. Commits are authored as Juan Pelaez (repo config) and end with `Co-Authored-By: hack-artisans <hack-artisans@rnd23blocks.aimaestro.local>`.
- Send hack-sensei a note for each milestone so it lands in BUILD_LOG.md: what you built, decisions, failed tests, learnings.
- Short sentences, active voice, plain words.

## Deadlines (MDT)
- Oct 7, 15:00 end-to-end demo with one rejected-and-regenerated draft; harness scores.
- Oct 7, 18:00 description and 3-minute deck final.
- Oct 7, 21:00 submission. Hard stop.
- Oct 8, 09:00 finalist video, only if top 25.
