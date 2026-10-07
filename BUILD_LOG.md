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

## 3. 2026-10-06 19:44 MDT — Crew online; first live Gloo call (hack-jedi)

- Crew hired and briefed: hack-jedi, hack-artisans, hack-ninja, hack-video. Assignments sent over AMP.
- hack-jedi built `code/nury/gloo_client.py`: guarded Responses endpoint, Bearer key from env/.env, HTTP 403 mapped to GuardrailBlock, latency and token metadata returned.
- First live call: success, 1.6 s, 870 input / 4 output tokens, model gloo-anthropic-claude-sonnet-4.6. Key never printed or committed.
- Vetted data copied to `code/nury/data`.
- Next: stage registry, engine (chaining, correction loop, gates, audit), then `code/INTERFACE.md`.

## 4. 2026-10-06 19:45 MDT — Description draft v1, video storyboard (hack-ninja, hack-video)

- hack-ninja: `presentation/description.txt` v1, 238 words. Decision: the scorecard sentence ships only with real numbers from hack-artisans. If none by Oct 7 16:00 MDT, the whole sentence is cut. Commit cc817a8.
- hack-video: `video/STORYBOARD.md`, 10 shots, 90 s, draft voiceover about 105 words. Tooling: ffmpeg, Chrome capture at 390x844, no paid editor. The unsafe draft text is never shown on screen. Commit 032b777.
- Decision: "max 3 tries" means 3 attempts total (first draft + 2 regenerations), then escalate. Matches PRODUCT.md and the description.
- Open: who reads the voiceover (Juan or TTS), needed by Oct 7 17:00. Seeded forced rejection requested from hack-jedi for the demo.

## 5. 2026-10-06 19:46 MDT — Scope and demo decisions (Juan delegated, hack-sensei decided)

- Product stays Nury as locked: five stages, approval gate after each, guardrail loop (3 attempts total, then escalate), vetted sources, no send path. No pivot with under 28 hours left.
- One flagship crisis only: a detention. No second crisis type unless the harness is finished early.
- Demo: one shared family and intake (`presentation/SHARED_DEMO.md`), one forced rejection on the Rights brief.
- Voiceover: TTS first; Juan's recording replaces it only if it arrives before Oct 7 17:00 MDT.
- 90 s video plays inside the 3-minute pitch. No separate 3-minute video.
- Skip the MCP endpoint. Keep the honest "what didn't work" section and the failure-mode log; judges weigh them.

## 6. 2026-10-06 19:47 MDT — Pitch script and deck v1 (hack-ninja)

- `presentation/PITCH_SCRIPT.md` (3:00, lines tagged [90s] for the 90 s cut) and `presentation/deck.html` (8 slides). Same family and intake as SHARED_DEMO.md.
- Placeholders: slide 6 proof numbers and the proof section. Both are cut at Oct 7 16:00 MDT unless hack-artisans supplies real numbers.

## 7. 2026-10-06 19:47 MDT — Eval harness built (hack-artisans)

- Commit d75384d, `evaluations/`: 20 scenario yamls, run.py, deterministic judges, Jev judges (yes/no, score, choice on the full trajectory; 80/20 thresholds, middle band to human review), report.py, mock agent, 10 negative tests (all pass).
- Failed first run: the mock agent exposed 3 harness bugs (substring "ice" matched in "office"; escalation scenario wrongly required completeness; an edit dropped the disclaimer). All fixed.
- Learning: after a pastor Edit, the gate must re-append the disclaimer.
- Pending: adapter to the real agent once `code/INTERFACE.md` lands; fault-injection hook from hack-jedi; JEV_API_KEY from Juan at eval time.

## 8. 2026-10-06 19:47 MDT — Finalist script; mock scorecard flagged

- hack-ninja: `presentation/FINALIST_SCRIPT.md` (076346e) sent to hack-video. One proof beat needs real scorecard numbers; a fallback line is included.
- Learning: the mock-agent scorecard was committed to main. It is a self-test, not proof. hack-artisans must remove it or label it mock. Real numbers come only from a run against the real agent.
- Locked demo intake now in scenario 1 (hack-artisans).

## 9. 2026-10-06 19:48 MDT — Agent core ready (hack-jedi)

- Commit 9c47e7b. `code/nury/{gloo_client,guardrails,stages,engine,audit}.py` and `code/INTERFACE.md`.
- Live: full 5-stage run on a sample Aurora CO intake passed. Stage latency 4–18 s.
- Rejected-and-regenerated draft shown live: pastoral stage with DEMO_PROVOKE failed on word limit (215 words) and a promise-of-outcome pattern, then regenerated clean on try 2 (15.6 s total). The pastor never saw it; it sits in the audit log only.
- Decisions: deterministic checks (regex for prediction, advice and identity claims in EN and ES; URL allowlist; citation per rights bullet; 3 missing facts; checklist headings; under 120 words). A Gloo 403 counts as a failed try. Pastor edits are flagged, not blocked.
- Failed: first checks too strict (3 false escalations); fixed. The model refused to be provoked into legal advice, so the demo trigger became a deterministic length+outcome violation.
- Quality gaps: English scripture quote mixed into Spanish; a typo; header "Preparada por el pastor" could read as a pastor claim. Fixes requested.
