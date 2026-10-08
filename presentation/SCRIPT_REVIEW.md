# Script review: pace, spacing and the accent

Written 2026-10-07 by hack-ninja for hack-sensei, to show Juan. Covers the 90-second film (`FINALIST_SCRIPT.md`, `ERIC_LINES.md`), the 3-minute pitch (`PITCH_SCRIPT.md`) and the older locked demo voice-over (`SHARED_DEMO.md`). Nothing here is rendered or changed in the film yet. **New Eric lines need hack-sensei's approval and a render.**

## Status

APPROVED by hack-sensei, 2026-10-07: E1 to E9 as written, the screen-text cuts, the pitch tightening (2:53), and slide 5 = the film plays and Juan stays silent. KEEP "see also: lantern". Applied to `FINALIST_SCRIPT.md`, `ERIC_LINES.md`, `PITCH_SCRIPT.md` and `SHARED_DEMO.md`.

## 1. The accent

"Pelaez" is now "Peláez" in every file I own: the memorial text (`MEMORIAL.md`, 5 places, including "Nury Peláez, 83"), the pitch script (2), the deck (3: slides 2, 10 and 12), the descriptions (1 each), `SUBMISSION_NOTES.md`, `CREATIVE_BRIEF.md`, `TREATMENTS.md` (3), `treatments/data.py` and `README.md`. 19 places. The deck was rebuilt. The email address (`jkpelaez@...`) stays as it is: it is an address, not a name.

**Not mine, so not changed:**

| Where | What | Owner |
|---|---|---|
| `video/remotion/src/Nury.tsx` lines 48 to 50 | The three memorial options still read "Nury Pelaez" | hack-video. **Needs the change before the film renders**, and a check that the font draws the "á". |
| `LICENSE` line 3 | "Juan Pelaez" | hack-sensei |
| `CLAUDE.md` (root and the five agent files) | "Author is Juan Pelaez" | hack-sensei. The git author name in the repo config is a separate setting; changing it rewrites nothing, but ask before changing it. |
| `code/playbooks/*/sources/approvals.json`, `scripture.json`, `official_list.json` | `"approved_by": "Juan Pelaez"` (data, and a test may compare it) | hack-jedi. Left alone: it is a record of who approved, not display text. |

## 2. What is wrong now: the silence map

Eric's lines measured by hack-video (`video/vo/arc/durations.json`): L1 2.23 s, L2 2.00, L3 0.88, L4 1.76, L5 2.04, L6 2.28, L7 2.88, L8 3.02 (the old line; the new one is shorter), L9 1.44, L10 2.51, L11 2.28. The average is 0.36 s per word.

**Eric speaks for 23.3 s of a 90 s film: 26 percent.** The longest stretches without a voice, in the default table (memorial 8 s):

| From | To | Gap | What is on screen |
|---|---|---|---|
| L4 ends 27.8 s | L5 36.0 s | **8.2 s** | The tool: selector, intake, triage card, Approve |
| L3 ends 18.5 s | L4 26.0 s | **7.5 s** | The dictionary card builds |
| L6 ends 45.6 s | L7 52.5 s | **6.9 s** | The turn: rejected, regenerating, passed |
| L9 ends 66.4 s | L10 72.5 s | **6.1 s** | Attorneys, checklist, message, one word edited |
| L2 ends 12.5 s | L3 17.6 s | **5.1 s** | The intake is typed, then a lit window |
| L5 ends 38.0 s | L6 43.3 s | 5.3 s | Rights brief (1.3 s of it is the designed silence) |
| L1 ends 5.7 s | L2 10.5 s | 4.8 s | The pastor takes the phone |

Three silences are **designed and should stay**: the hook (0 to 3.5 s, a phone in the dark), the beat of quiet at the start of the turn (42.0 to 43.3 s), and the memorial (82 to 90 s, text only, no voice).

**Also found:** L4 ("Five stages. A gate after each.") repeats the on-screen plain line in row 4, but plays 8 s later, in the middle of the tool demo, where it explains nothing new.

## 3. The proposal for the film

**Rule for every new line:** 1.5 to 3 seconds, 8 words or fewer, no number, plain, and tied to something that is on screen and true. No new claims. Each has its evidence below.

### New Eric lines (7)

| ID | Line | Words | Est. s | On screen | Evidence |
|---|---|---|---|---|---|
| E1 | He types what she says. | 5 | 2.0 | The intake is typed | The pastor types the intake (the product's first step) |
| E4 | Pick a crisis. Triage comes first. | 6 | 2.4 | The selector, then the triage card | Selector in the app; triage is stage 1 (TC 4) |
| E5 | Approve, edit or stop. | 4 | 1.6 | The thumb taps Approve | The gate has exactly these three actions (FEATURES section 1) |
| E6 | Only from vetted sources. | 4 | 1.6 | The rights brief with citation chips | Vetted sources only; every point cited (TC 4, 8) |
| E7 | It rewrites. It checks again. | 5 | 2.0 | Regenerating, then Passed | The correction loop (TC 4) |
| E8 | Then contacts, a checklist, a message. | 6 | 2.4 | Stages 3, 4 and 5 appear | The five stages (CLAUDE.md) |
| E9 | He changes one word. | 4 | 1.6 | One word is edited | The scripted edit in the demo (row 9) |

Estimates use 0.4 s per word, a little slower than Eric's measured 0.36. Real lengths come after the render.

**One approved line moves, with no new render:** L4 ("Five stages. A gate after each.") moves from 26.0 s to 21.0 s, so it plays while the plain line is on screen in row 4. The tool beat then gets E4 and E5.

**One approved line changes length:** the new L8 ("Jev checks every draft. People decide.", 6 words) is already waiting for a render; estimated 2.3 s.

### Proposed timeline, table 1 (memorial option 3, 8 s): exact times

| Row | Time | Eric (start to end) | Gap before | Verdict |
|---|---|---|---|---|
| 1 Hook | 0:00 to 0:03 | none | n/a | **Keep.** Designed silence: a phone in the dark. |
| 2 Persona | 0:03 to 0:10 | L1 3.5 to 5.7 | 3.5 | Keep. |
| | | L2 **8.6** to 10.6 (was 10.5) | 2.9 (was 4.8) | **Tighten:** L2 moves up 1.9 s and starts over the persona shot. |
| 3 Stakes | 0:10 to 0:17 | E1 12.2 to 14.2 | 1.6 | **New line** over the typing. |
| | | (no voice 14.2 to 17.6) | | The lit window and the shoes. A 3.4 s beat of picture. **Keep.** |
| 4 This is Nury | 0:17 to 0:25 | L3 17.6 to 18.5 | 3.4 | Keep. |
| | | L4 **21.0** to 22.8 (was 26.0) | 2.5 | **Move.** Same words, 5 s earlier. |
| 5 The tool | 0:25 to 0:35 | E4 26.0 to 28.4 | 3.2 | **New line.** |
| | | E5 31.5 to 33.1 | 3.1 | **New line** as the thumb taps Approve. |
| 6 Rights brief | 0:35 to 0:42 | L5 36.0 to 38.0 | 2.9 | Keep. |
| | | E6 38.8 to 40.4 | 0.8 | **New line.** |
| 7 The turn | 0:42 to 0:52 | (silence 42.0 to 43.3) | | **Keep.** Designed silence, 1.3 s. |
| | | L6 43.3 to 45.6 | 2.9 (1.3 designed) | Keep. |
| | | E7 48.0 to 50.0 | 2.4 | **New line** on the way to "Passed". hack-video aligns it to the strip. |
| 8 Tech beat | 0:52 to 1:04 | L7 52.5 to 55.4 | 2.5 | Keep. |
| | | L8 58.5 to 60.8 | 3.1 | **Tighten:** the new, shorter L8. |
| 9 Stages | 1:04 to 1:12 | E8 64.2 to 66.6 | 3.4 | **New line.** |
| | | L9 67.2 to 68.6 | 0.6 | **Move** 2.2 s later, so it lands when the message appears. |
| | | E9 69.6 to 71.2 | 1.0 | **New line** on the edit. |
| 10 Copy, not Send | 1:12 to 1:18 | L10 72.5 to 75.0 | 1.3 | Keep. |
| 11 Dawn | 1:18 to 1:22 | L11 78.5 to 80.8 | 3.5 | Keep. The resolving chord needs the 3.5 s. |
| 12 Memorial | 1:22 to 1:30 | none | | **Keep.** Designed silence: no voice. |

**Result.** Eric speaks about **36 s of 90 (40 percent), up from 23 s (26 percent).** The longest gap outside the designed silences falls from **8.2 s to 3.5 s.** All six gaps over 5 s are gone (8.2, 7.5, 6.9, 6.1, 5.3 and 5.1 s).

### Proposed timeline, table 2 (memorial option 2, 16 s)

Rows are shorter, so the lines shift by each row's offset. E9 is dropped (row 9 is only 6 s).

| Line | Start to end | Row |
|---|---|---|
| L1 | 3.5 to 5.7 | 2 |
| L2 | 7.6 to 9.6 | 2 and 3 |
| E1 | 11.0 to 13.0 | 3 |
| L3 | 15.6 to 16.5 | 4 |
| L4 | 18.8 to 20.6 | 4 |
| E4 | 23.2 to 25.6 | 5 |
| E5 | 28.2 to 29.8 | 5 |
| L5 | 31.2 to 33.2 | 6 |
| E6 | 33.8 to 35.4 | 6 |
| L6 | 37.3 to 39.6 | 7 (silence 36.0 to 37.3) |
| E7 | 42.0 to 44.0 | 7 |
| L7 | 46.5 to 49.4 | 8 |
| L8 | 52.5 to 54.8 | 8 |
| E8 | 58.2 to 60.6 | 9 |
| L9 | 61.2 to 62.6 | 9 |
| L10 | 64.5 to 67.0 | 10 |
| L11 | 70.5 to 72.8 | 11 |
| Memorial | 74 to 90 | 12 (no voice) |

Longest gap: 3.5 s (L10 to L11). The one tight spot is E8 to L9 (0.6 s).

### Slow screen text: proposed cuts

Reading speed for a caption is about 3 words a second. These do not fit their time.

| Row | Now | Words | Proposal |
|---|---|---|---|
| 4 (8 s) | The dictionary entry plus "see also: lantern" plus the plain line "Five stages. A gate after each. Nothing sent." | about 35 | **Keep the entry** (Juan approved it). **Cut "see also: lantern"** if Juan agrees. The voice now says "Five stages. A gate after each." at 21.0 s, so the on-screen plain line only needs "Nothing sent." Decision for Juan. |
| 8 (12 s) | Three proof captions of 3 s, the second at 12 words (`Typed judge, ten checks: unsafe 0.89 to 0.98, safe 0.02 to 0.24`), plus the 27-word disclosure | 12 on one caption | Shorten the second to `Judge test: unsafe 0.89 to 0.98, safe 0.02 to 0.24` (10 tokens) or hold it for 4 s. The disclosure line stays whole: it is required. The third caption changes after the re-run. |
| 10 (6 s) | "Nury is not a pastor. Nury does not send. The pastor does. Legal information only." | 15 | **Cut to "Legal information only."** Eric already says "Nury is not a pastor. It never sends." The disclaimer stays on screen. |
| 3 (7 s) | "Synthetic family. Not real people." | 5 | **Keep.** Honest and short. |
| 2 (7 s) | "A pastor. No lawyer on the line." | 7 | Keep. |

### What does not change

L1, L2, L3, L5, L6, L7, L9, L10 and L11 keep their words. The memorial keeps its silence. The hook keeps its silence. No number is read aloud. No line names a person, an agency or a maker.

## 4. The 3-minute pitch, against the cut

Speaking at a calm 2.5 words a second. Word counts are from the script text (a script count of the spoken sentences, not the stage directions), so treat them as within a few words. "Dead air" is time where nobody speaks and nothing on screen needs the time. A slide is **over** when the words need more time than the slot gives.

| # | Slide | Slot | Words now | Time needed | Verdict |
|---|---|---|---|---|---|
| 1 | Night: the call | 0:00 to 0:14 (14 s) | 33 | 13 s | **Keep.** Fills the slot; the first buzz is the designed silence. |
| 2 | Lantern: This is Nury | 0:14 to 0:20 (6 s) | 3 | 1.2 s | **Merge into 3.** 4.8 s of dead air. |
| 3 | The name entry | 0:20 to 0:28 (8 s) | 16 | 6.4 s | **Merge with 2**: one 12 s beat, "This is Nury." then the entry. Saves 2 s. |
| 4 | Concept and product | 0:28 to 0:43 (15 s) | about 50 | 20 s | **Over by 5 s. Tighten.** Also: the text says "Detention is the one you saw", but the demo comes in slide 5, after it. Say "the one you are about to see". |
| 5 | The demo | 0:43 to 1:17 (34 s) | about 61 | 24 s | **Keep, with one decision.** If Eric's film plays here, Juan stays silent. If Juan speaks over the live app, no film. The script says both. Pick one. |
| 6 | How it is built | 1:17 to 1:37 (20 s) | about 70 | 28 s | **Over by 8 s. Tighten** to about 45 words. |
| 7 | Innovation | 1:37 to 1:52 (15 s) | about 42 | 17 s | **Over by 2 s. Tighten:** the last sentence repeats slides 5 and 6. |
| 8 | Use of AI | 1:52 to 2:10 (18 s) | 47 | 19 s | **Keep.** 1 s over; give it 19 s. |
| 9 | Impact and execution | 2:10 to 2:22 (12 s) | about 25 plus the 28-word disclosure | 21 s | **Over by 9 s.** Do not read the disclosure aloud: it is on the slide. Speak the numbers and one failure. |
| 10 | Teamwork and next | 2:22 to 2:30 (8 s) | 38 | 15 s | **Over by 7 s. Tighten** to about 17 words. |
| 11 | Dawn: close | 2:30 to 2:34 (4 s) | 13 | 5 s | **Give it 5 s.** |
| 12 | Memorial | 2:34 to 2:50 (16 s) | text only | | **Keep.** Designed silence. |

### Proposed pitch timeline (total 2:53, with the memorial)

| # | Slide | Time | Proposed words |
|---|---|---|---|
| 1 | Night | 0:00 to 0:14 | Unchanged. |
| 2 and 3 | This is Nury, and the entry | 0:14 to 0:26 | "This is Nury." (the lantern lights) "A given name from Arabic nur, light. An AI crisis response agent." |
| 4 | Concept | 0:26 to 0:40 | "Five stages, one gate after each. The app opens on a crisis selector. Detention and hospital emergency are live, and two more are coming soon. Nothing is sent without the pastor." (30 words, 12 s) |
| 5 | Demo | 0:40 to 1:14 | Unchanged, once the voice decision above is made. |
| 6 | How it is built | 1:14 to 1:36 | "The pastor types. Names become tokens inside Nury. Only tokens reach Gloo AI Studio. Named checks, then Jev, reject unsafe drafts, up to three tries. The pastor decides. The leak test ran 90 checks per playbook and found no names." (42 words, 17 s) |
| 7 | Innovation | 1:36 to 1:50 | "Adding a crisis is adding a playbook folder. The engine does not change. Detention and hospital both run on it, and a test builds a new crisis from scratch." (30 words, 12 s) |
| 8 | Use of AI | 1:50 to 2:09 | Unchanged (47 words). |
| 9 | Impact | 2:09 to 2:22 | The numbers and one failure only (about 30 words). The disclosure stays on the slide. |
| 10 | Teamwork | 2:22 to 2:32 | "Built by one founder and five AI agents. Next: real pastors, and an attorney to review our sources." (18 words, 7 s) |
| 11 | Close | 2:32 to 2:37 | "The next call will come. Nury is there when the pastor picks up." |
| 12 | Memorial | 2:37 to 2:53 | Text only. |

That leaves 7 s under the 3:00 limit. The "90-second cut" (slides 1, 2 and 3 merged, 5, 6, 11 and the memorial) still comes to about 88 s.

Whatever is not spoken moves into the speaker notes, which are already in the deck (press `n`). No claim is removed.

## 5. The older voice-over in `SHARED_DEMO.md`

It was the older 10-line version, written before the treatments. **Correction:** my first draft said it still carried old wording about staff. It does not (that wording is in `Nury.tsx` and the prework files). It is now marked SUPERSEDED and points to `ERIC_LINES.md`.

## 6. What needs a decision

1. **Approve the seven new lines** (E1, E4, E5, E6, E7, E8, E9), or strike any. They need a render and a length check. Each is true and has evidence above.
2. **Move L4 and L2 and L9** as proposed (no re-render, only placement).
3. **Screen text:** cut "see also: lantern" (Juan's call), shorten proof caption 2, cut row 10's caption to "Legal information only."
4. **Pitch slide 5:** film or live app, not both.
5. **Pitch:** accept the tightened text for slides 4, 6, 7, 9 and 10, and the merge of slides 2 and 3.
6. **hack-video:** change the memorial name in `Nury.tsx` (lines 48 to 50) to "Peláez".

## 7. Method and checks

- Line lengths: `video/vo/arc/durations.json` (measured). New lines: estimated at 0.4 s per word.
- Every proposed time was checked for overlap (no line starts before the previous one ends, minimum gap 0.4 s) and against its row's time range in `FINALIST_SCRIPT.md`.
- Humanizer: the new lines are short, active and plain. E8 is a three-item list because the screen shows three items; it is an enumeration, not a rhythm device. No em dashes. The locked lines (the Jev disclosure, the disclaimers, the memorial text) are untouched.
- Not checked: the exact second the strip says "Passed" (hack-video's timeline) and the real length of the new L8 and of E1 to E9. hack-video prints the table; I will adjust any start time that collides.
