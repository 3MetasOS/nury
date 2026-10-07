# BUILD_LOG — Nury

Timestamped build record for the judges. One entry per milestone: what was built, decisions, commits, failed tests, learnings. Owner: hack-sensei.

## 1. 2026-10-06 19:36 MDT — Repo created

- Repo created from scratch; prework carried as reference in `documents/prework/` (no history copied).
- Skeleton: code, presentation, video, documents, evaluations, agents (five folders), root CLAUDE.md.
- Decision: the brief sets the guardrail loop at max 3 tries, then escalate. PRODUCT.md said 2 retries. The brief governs.
- Commits: first commit c9c4c97.

## 2. 2026-10-06 19:42 MDT — Gloo API key stored locally

- Juan supplied the Gloo key ("Hackaton 2026") and directed it into a local `.env` at the repo root.
- Decision: `.env` is gitignored and never committed. The key is not in any tracked file, commit, or message. Verified with `git check-ignore`.
- Learning: the key appeared once in the session transcript. Rotate it in Gloo Studio after the hackathon.
