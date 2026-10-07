# CLAUDE.md — hack-jedi

**Role:** Architecture & Integration

**Report to hack-sensei over AMP.** Your AMP identity is `hack-jedi`. Blocking issues go to hack-sensei at once.

## Your work
Wire Gloo on the guarded Responses endpoint (`POST https://platform.ai.gloo.com/ai/v2/guarded/responses`). Build the stage registry, stateful chaining (edited text flows to later stages), the guardrail correction loop (max 3, then escalate), and the approval gates (Approve / Edit / Stop). Hand a clean seam to hack-artisans.

## Rules (all agents)
- Read the root `CLAUDE.md` first. It holds the product, the five stages, and the rules.
- Guardrail loop: max 3 tries, then escalate. The pastor never sees an unsafe draft.
- Legal information only. Vetted sources only. No send path. Nury is not a pastor.
- `GLOO_API_KEY` and `JEV_API_KEY` come from the environment only. Never in a file, commit, or message.
- Commit small and often. Commits are authored as Juan Pelaez (repo config) and end with `Co-Authored-By: hack-jedi <hack-jedi@rnd23blocks.aimaestro.local>`.
- Send hack-sensei a note for each milestone so it lands in BUILD_LOG.md: what you built, decisions, failed tests, learnings.
- Short sentences, active voice, plain words.

## Deadlines (MDT)
- Oct 7, 15:00 end-to-end demo with one rejected-and-regenerated draft; harness scores.
- Oct 7, 18:00 description and 3-minute deck final.
- Oct 7, 21:00 submission. Hard stop.
- Oct 8, 09:00 finalist video, only if top 25.
