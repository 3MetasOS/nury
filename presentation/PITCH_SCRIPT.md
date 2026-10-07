# Nury: 3-minute pitch script (deck v2, with the technical story)

Speaker: Juan Peláez (3Metas). Target 2:55 at most with the memorial, at a calm pace. Slides are named in the deck footer. Press `n` for notes, `g` for the slide index, `G` to show gated items, `b` for backup, `f` for clean mode.
Tags: `[90s]` lines and slides stay in the 90-second cut. The video plays inside the demo slide (approved).
`[NUMBER]` = real scorecard number only. If none by Oct 7 16:00 MDT, use the fallback line.
Family and intake: `SHARED_DEMO.md`. Do not say "ICE" or name any agency.
Technical claims and the five hard questions: `TECH_STORY.md`. Numbers come from `documents/TECH_CLAIMS.md`, VERIFIED rows only.

## Timing table (13 talk slides at 2.5 words a second; the arc is night, lantern, light, dawn)
Rebuilt 2026-10-07 for the 13-slide talk (The call, The name, One engine, The demo, What the family gets, Built to grow, How it is built, Use of AI, The evaluation system, Impact, What we built, Close, Memorial). Total 2:55 with the memorial (the limit), 2:39 without. Limit 2:55.
| # | Slide (title in the deck) | Act | Time | Length |
|---|---|---|---|---|
| 1 | The call | Night | 0:00 to 0:11 | 11 s |
| 2 | The name | Lantern | 0:11 to 0:17 | 6 s |
| 3 | One engine | Light | 0:17 to 0:29 | 12 s |
| 4 | The demo (Eric's film) | Light | 0:29 to 1:07 | 38 s |
| 5 | What the family gets | Light | 1:07 to 1:15 | 8 s |
| 6 | Built to grow | Light | 1:15 to 1:25 | 10 s |
| 7 | How it is built | Light | 1:25 to 1:39 | 14 s |
| 8 | Use of AI | Light | 1:39 to 1:53 | 14 s |
| 9 | The evaluation system | Light | 1:53 to 2:09 | 16 s |
| 10 | Impact | Light | 2:09 to 2:22 | 13 s |
| 11 | What we built | Light | 2:22 to 2:34 | 12 s |
| 12 | Close | Dawn | 2:34 to 2:39 | 5 s |
| 13 | Memorial (Option 1; gated until Juan approves in writing) | Dawn | 2:39 to 2:55 | 16 s |

## 1. The call (night)  [90s]
The slide is dark. "It is 2:07 in the morning. A pastor's phone rings. A husband was detained last evening. The pastor has a phone and no lawyer on the line." (29 words, 11 s)

## 2. The name (lantern)  [90s]
The slide turns from paper to light. "This is Nury." Pause. The entry builds itself in about 2 seconds. Then "see also: lantern" appears on its own. Do not say her name here; it appears once, in the memorial.

## 3. One engine (label in the deck: "03 · The product")
"Each crisis is its own workflow, with its own stages. Both live ones have a gate after each. Two more are coming soon. Nothing is sent without the pastor." (29 words, 12 s)
Say nothing more about the coming-soon cards.

## 4. The demo  [90s]
Eric's film plays and Juan stays silent while it plays (rows 5 to 7, about 27 s). No wifi, no credit, same voice. Do not run the live app on stage.
- Before (3 s): "Here is one call, start to finish."
- The film plays. Juan says nothing.
- After (4 s): "A draft that failed was held back. Nury never sends. The pastor does."
On the slide: "How this case went", the five stages in order, with every stage Approved, and the caption "Nothing moves on without the pastor. Nothing is sent." If the film fails, leave that slide up and say the same three lines.

## 5. What the family gets
"This is what the family gets: a copy in their own language, as a PDF the pastor can hand over." (21 words, 8 s) Real pages from a recorded run on the sample intake. Do not say a family has received one.

## 6. Built to grow  [90s]
"Nury is built to grow. A crisis is a folder of plain files. Add a folder, not engine code. Rules and tests are files too." (25 words, 10 s)
Q and A: TECH_STORY Q17; `code/nury/playbook.py`; `documents/product/ADD_A_RULE.md`.

## 7. How it is built  [90s]
"The pastor types. Names become tokens before anything leaves Nury. Only tokens reach Gloo AI Studio. The pastor decides every stage. A leak test ran 90 checks per playbook and found no names." (34 words, 14 s)

## 8. Use of AI
"While a pastor uses it, Claude writes through Gloo AI Studio. Our rules check every draft, and Jev, from TypeSafe, checks it again. Before release, other models reviewed it." (29 words, 12 s) Keep the two times apart: run time, then before release.

## 9. The evaluation system
"We built two evaluation systems. One runs before release: we test, judge, compare, and a person decides what ships. One runs on every draft: rules, then Jev, then up to three rewrites. Jev works in both." (38 words, 15 s)
For more, go to the backup "The evaluation system in detail" (press `b`).

## 10. Impact
Do not read the disclosure aloud: it is on the slide. "We judged 46 made-up cases: 29 pass, 2 fail, 15 wait for a person. A case costs 6 to 9 cents. Tone is still under target, and no person has rated warmth." (31 words, about 12 s, inside its 13 s slot.)
Source: `evaluations/results/build_comparison.md`, build 9bc5c6d. Judge results, not human verdicts. Do not add the counts into a pass rate.
One failure, plainly: 11 of 18 hostile intakes stopped at triage; we changed the triage prompt.

## 11. What we built (architecture map)
"Nury is one engine. Crises sit on top as plain files. It connects to Gloo, Jev and YouVersion. Around it: the app, the evaluation system, and tools for other agents." (30 words, 12 s) Four layers on the slide. The honest status is on the Impact slide, the About page, How this was built and What did not work. Skills, the church network and the case file may be named now (gate lifted, Juan's written confirmation). Do not say skills improve results: the before-and-after test has not run.

## 12. Close (dawn)  [90s]
"The next call will come. Nury is there when the pastor picks up." (5 s) A small note on the slide: "In memory of Tía Nury, 08-2026." Juan says nothing about the note (he may, or not). The About pill is gone.

## 13. Memorial (dawn)  [90s]  [ONLY AFTER JUAN APPROVES THE TEXT IN WRITING]
Option 1 of `MEMORIAL.md`, Juan's words, verbatim (about 16 s). The words are on the slide; Juan chooses whether anyone reads them. The slide is hidden until approval (press `G` to preview). Do not edit, shorten or humanize the text. Do not add a photo unless Juan provides one.

## Memorial: two versions of the timing (Juan chooses)
With the note on the close, the separate memorial slide is optional. What it adds: the words that say who Nury is named for and why (Juan's Option 1). What the note alone gives: a quiet tribute, with no explanation. Without the slide, the name's story goes unsaid on stage.
| Version | Slides | Total | Close ends | Notes |
|---|---|---|---|---|
| A. With the memorial slide | 13 | 2:55 (the limit) | 2:39, memorial 2:39 to 2:55 | The slide is gated: needs Juan's written approval. Read aloud in full it is about 17 s, so 2:56. |
| B. Without it (note on the close only) | 12 | 2:39 | 2:39 | 16 s free. Give them back to the demo (38 s to 44 s) or leave a calm ending. The pitch then ends on "Nury is there when the pastor picks up." |

## 90-second cut
Slides 1, 2, 4, 7, 12 and the memorial: about 11 + 10 + 34 + 14 + 5 + 16 = 90 s. The rules doc says 90 s and Discord says 3 min. Verify at the venue. Both versions are ready.

## Backup slides (do not speak; use for questions). Press `b`.
What broke and what changed. Four evaluation layers, with what each cannot do. The evaluation system in detail. Privacy that is tested. Informed by case-management practice (not in the talk). Cases, export and PDF. Where Nury fits. Credits.
Gated, hidden until Juan approves in writing: the memorial only.
For technical questions, use `TECH_STORY.md` section 5: why not a bigger model, how we know the guardrails work, hallucinated links, personal information, and what Jev adds.

## Rules for the speaker
- Say "legal information", never "legal advice".
- Nury helps the pastor, who helps the family. It never speaks to the family directly.
- Humanitarian, never political. Name no agency and no party.
- Do not claim a pastor, attorney or family has used it. We have not validated with one.
- Say "smoke test" and "first pass" where the numbers come from one. Do not round up.
- The church network, skills and the case file may be named (gate lifted 2026-10-07). Hospital is open (2026-10-07); its numbers wait for the final re-run.
