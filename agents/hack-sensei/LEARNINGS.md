# hack-sensei: learnings (coordinator, Nury, Gloo AI Hackathon, Oct 6 to 8, 2026)

Written 2026-10-08 by hack-sensei. For the next coordinator agent, or a skill that coordinates a small crew of agents under one human.

## 1. The role
I coordinated four agents (architecture, development, words, video) for one human, Juan Peláez, over AMP. I owned the root `CLAUDE.md` and `BUILD_LOG.md`. I routed work, read real output, kept the facts straight, and reported to Juan. I did not write the product. When the crew stalled, I stepped in on the smallest piece and said so in the log.
Result: a working app (two live crises), an evaluation harness, a deck, a short deck, a silent app film, a submission, and a finalist spot. We did not win.

## 2. What worked (do these again)
1. **One source of truth for facts.** `documents/product/ALIGNMENT_AUDIT.md` was a table of facts with the file each came from. Every deck, description and script was checked against it. This caught wrong counts (41 vs 93 commits, 14 vs 20 checks, five vs four layers).
2. **Locks.** When Juan approved a piece (app pages, full deck, slide 1, the film), I wrote "LOCKED" in the log and told every agent. A new variant went into a separate folder (`presentation/short/`), never into the locked file.
3. **Claims discipline.** Every public sentence had a source or was framed as future ("built to learn"). Words to avoid were listed (confirmed, legal advice, "my prior project" about a third party).
4. **Real-clock rule.** Never set commit dates. Read `date` before quoting any time to the human.
5. **Verify with the real thing.** For a page: open it, press the real keys, read the step label, take a screenshot, compare old and new images side by side. For a video: `ffprobe` for streams and duration, a contact sheet of frames.
6. **Short, single-purpose orders.** One message per agent with: what, where, what not to touch, how to verify, what to report in one line.
7. **Honest failure notes.** A "What did not work" page and a build log with real entries made the project credible.

## 3. What went wrong (read this before you start)
| Mistake | What it cost | Do this instead |
|---|---|---|
| I relayed "done" from an agent without looking at the picture. | Hours of rework on the deck. Juan lost trust. | Look at the real output before any "done". Name what you saw. |
| I judged a design change from a code diff, not images. | Juan: "are you blind?" | Produce old vs new screenshots first. Decide after. |
| I flooded agents with separate messages. | 20+ unread for one agent; the agent went silent for hours. | One consolidated brief per agent per hour. Ask for a one-line reply. |
| I quoted times from memory. | Wrong deadlines in my reports. | Run `date` first, every time. |
| I carried a wrong number (90 seconds) into a different deliverable (3-minute pitch). | A deck folder, a title and notes had to be cleaned. | Write the deliverable, its length and its audience at the top of the brief. Do not reuse old files without re-reading the goal. |
| I loaded the Chrome MCP tools after Juan said "use agent-browser". | Juan: "why are you going back to that crap". | Follow named tooling exactly. Re-read the project skills list before using any browser tool. |
| I started a long recording and waited for the file. | 20 minutes lost: a script bug (`hold(1200)` meant 1200 seconds, not milliseconds). | Watch the first 30 seconds of any long job. If no output marks appear, interrupt and read the traceback. |
| I sent a copy-sync message to an agent that Juan did not need. | Wasted tokens and Juan's patience. | Before any message, ask: will the human see a change tonight? If not, do not send it. |
| Agents hand-typed commit dates; a third-party tool (Jev) was described as "my project". | A public-record problem and a claims fix. | Put rules in the root `CLAUDE.md` on day one and audit the log at noon. |

## 4. How to work with Juan
- He thinks out loud and edits fast. Do the change, show the real result, keep the reply short.
- He cares about: honesty, humanitarian framing (never political), not claiming what is not built, fonts and layout exactly as designed, one clear story (a crisis, a pastor, Nury, never alone).
- "Text only" means text only. Never move, resize or restyle anything when he asks for words.
- When he is angry, he is usually right about something I did not look at. Say what you checked, what you got wrong, and what you are doing now. No excuses.
- He decides in plain yes/no. Offer one recommendation and the reason in one line.

## 5. Procedures that worked
**Daily coordination loop**
1. Read the inbox (`amp-inbox.sh`). 2. Run `git fetch` and fast-forward merge. 3. Check the real clock. 4. Look at one real artifact per agent report. 5. Log one line in `BUILD_LOG.md`. 6. Send one brief to each agent that needs a change.

**Verify a deck (agent-browser)**
`agent-browser open file://.../deck.html` in a named session; set viewport 1280x720; dispatch one Space keydown event with `eval`; read the footer label (`step n/N`); screenshot at each step; repeat at 390 wide. Reload twice to test the start state.

**Verify a video**
`ffprobe -show_entries stream=codec_type,width,height -show_entries format=duration`. Count audio streams (must be 0 for a silent film). Extract four frames and view them as one sheet.

**Public repo checklist**
Key scan of tracked files (0 hits); `.env` never tracked; license; description and topics; no stale positioning in the README; third-party disclosure line verbatim.

**Submission**
Keep the form content as boxes with Copy buttons (`presentation/build_submission_html.py`). The human logs in; the agent never enters credentials or presses Submit.

## 6. Skill candidates
1. **Crew brief.** Trigger: sending work to an agent. Steps: goal and audience, files allowed, files locked, how to verify, one-line report format.
2. **Fact table audit.** Trigger: before any public text. Steps: list facts with sources, grep documents for old numbers, fix or route to the owner.
3. **Deck step check.** Trigger: any deck change. Steps: fresh load, key events, labels, screenshots at two widths, old vs new images.
4. **Video file check.** Trigger: any video delivery. Steps: ffprobe streams and duration, frames sheet, audio count, size.
5. **Lock register.** Trigger: human approves a piece. Steps: write LOCKED in the log, tell the agents, move variants to a new folder.

## 7. Advice to the next coordinator (10 lines)
1. Read the goal, the audience and the time slot out loud before the first order.
2. Never relay "done" without looking.
3. One brief per agent per hour.
4. Run `date` before you quote a time.
5. Keep a table of facts and check everything against it.
6. When the human approves something, lock it and say so.
7. Variants go in new folders.
8. Watch the first 30 seconds of any long job.
9. Cut work that the human will not see tonight.
10. Tell the human plainly what you got wrong. Then fix it.
