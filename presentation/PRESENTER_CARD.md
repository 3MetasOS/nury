# Presenter card: the live pitch (2:55, 2.5 words a second)

Juan reads this one page. Keys: `n` notes, `g` slide index, `G` show gated, `b` backup, `f` clean mode. The memorial stays hidden until Juan approves in writing.

| # | Slide | Say, in 8 words | Cue |
|---|---|---|---|
| 1 | The call | A pastor's phone rings at 2:07 AM. | Dark slide. Phone buzz. 11 s. |
| 2 | The name | This is Nury. | Pause. Entry builds in 2 s. 6 s. |
| 3 | One engine | Each crisis is its own workflow. Two live. | Point at the two live cards. 12 s. |
| 4 | The demo | Here is one call, start to finish. | Start the film. Stay silent 27 s. Then: "Nury never sends. The pastor does." 38 s. |
| 5 | What the family gets | A PDF the pastor can hand over. | Point at the Spanish page. 8 s. |
| 6 | Built to grow | A new crisis is a new folder. | Point at the folder tree. 10 s. |
| 7 | How it is built | The model sees tokens, not names. | Trace the line left to right. 14 s. |
| 8 | Use of AI | Claude writes. Rules and Jev check. | Top band first, then the bottom band. 14 s. |
| 9 | The evaluation system | Two evaluation systems. One builds, one checks. | Top lane, then bottom lane. 16 s. |
| 10 | Impact | 46 made-up cases: 29 pass, 2 fail. | Do not read the Jev line. Say the tone gap. 13 s. |
| 11 | What we built | One engine. Crises on top. Tools around it. | Point at the four layers. 12 s. |
| 12 | Close | The next call will come. | Pause. 5 s. The small note "In memory of Tía Nury, 08-2026" is on the slide; Juan may stay silent on it. (90-second cut ends here.) |
| 13 | Memorial | Juan's words, only after written approval. | Nothing else on screen. 16 s. |

## Never say
- "ICE" or any agency. "Legal advice" (say "legal information"). "Pass rate".
- That a pastor, attorney or family has used Nury.
- Her name before the memorial.

## If asked
- Another failure: the tone score sits near 3 of 5 against a target of 4, and no person has rated warmth.
- Who is Jev: a decision API from TypeSafe. We use it. We did not build it.
- Backups (press `b`): the evaluation system in detail, what broke, Jev, privacy, cases and PDF, credits.

## Beats: press Space on these words (as built)
Source: the CHOREO block in `deck.html` and `ANIMATION_LOG.md`. On arrival a slide shows its base content (step 0). Each Space press reveals the next step; after the last step Space moves to the next slide. Times are seconds from the start of the slide, at 2.5 words a second, spoken lines exactly as in `PITCH_SCRIPT.md`. "Early" or "late" says how far the step is from its words.

| # | Slide (slot, steps) | Step 1 | Step 2 | Step 3 | Step 4 |
|---|---|---|---|---|---|
| 1 | The call (11 s, 4) | 0.0 "It is 2:07": the porch-light photo flickers | 1.6 "in the morning": the headline "2:07 AM. A pastor's phone rings." (second sentence about 1 s early) | 4.0 "A husband was detained": the line "A husband was detained last evening. The family needs help now." | 8.8 "no lawyer": the hand note "no lawyer on the line" |
| 2 | The name (6 s, 0) | No presses. It builds itself in about 2.4 s from "This is Nury." | | | |
| 3 | One engine (12 s, 2) | 0.0 "Each crisis": the crisis chooser (shows all four cards, so "coming soon" is about 7 s early) | 4.0 "Both live ones have a gate": the stage rows | | |
| 4 | The demo (38 s, 3) | 0.0 "Here is one call": the first screen | 2.6 just before the film starts: the pulse ring on the screen (the play cue) | 30.0 film ends, "A draft that failed": "How this case went", the five stages ticking in order | |
| 5 | What the family gets (8 s, 3) | 2.4 "a copy in their own language": the Spanish family copy slides up | 6.4 "the pastor can hand over": the pastor copy slides up | 7.2 "hand over": the caption "A PDF the pastor can hand over." | |
| 6 | Built to grow (10 s, 3) | 2.0 "A crisis is a folder": the folder tree, then its file names about 0.7 s later | 5.2 "Add a folder": the tag "Add a crisis" | 7.6 "Rules and tests": the tags "Add a rule" and "Add a test" | |
| 7 | How it is built (14 s, 3) | 0.0 "The pastor types": boxes 1 and 2, then the note "names stay inside Nury" 0.7 s later | 4.0 "Only tokens reach": box 3 (Gloo AI Studio) and the token dot | 6.4 "The pastor decides": boxes 4 and 5 (checks, pastor approves) | |
| 8 | Use of AI (12 s, 4) | 0.0 "While a pastor uses it": the Claude box | 4.4 "Our rules": the rules box | 6.8 "and Jev": the Jev box and the pastor box | 9.2 "Before release": the bottom band fades in and its boxes light 0.25 s later |
| 9 | The evaluation system (15 s, 3) | 2.0 "One runs before release": lane 1 boxes light and a progress line runs | 7.6 "One runs on every draft": lane 2 boxes light and 239 counts up | 12.8 "Jev works in both": the Jev pill between the lanes | |
| 10 | Impact (13 s, 2) | 0.0 "We judged 46": the bars wipe and all counts run up | 5.6 "A case costs": "6 to 9 cents a case", "34 to 50 seconds", the hostile-intake line and the Jev disclosure | | |
| 11 | What we built (12 s, 4) | 0.0 "Nury is one engine": Layer 2, The agent | 1.6 "Crises sit on top": Layer 1, Crises | 4.4 "It connects to": Layer 3, Connected to | 7.2 "Around it": Layer 4, Around it |
| 12 | Close (5 s, 2) | 0.0 "The next call": the logo, the tagline and the whole line "The next call will come. Nury is there when the pastor picks up." (second sentence 2 s early) | 4.5 "picks up": the memory note "In memory of Tía Nury, 08-2026", the photo and the disclaimer | | |
| 13 | Memorial (16 s, 0) | No presses. The text is on screen. | | | |

## Where a step does not match the words (after hack-artisans synced the steps, 15d5cb5)
Fixed: What we built now builds 2, 1, 3, 4; the evaluation Jev pill is step 3; Use of AI has four steps; How it is built has three; Built to grow splits the tags; Close has two presses.
Still true:
1. **The call, step 2:** the headline carries "2:07 AM." and "A pastor's phone rings." about 1 s early. Acceptable.
2. **Close:** the tagline line shows both sentences at once, so the second is about 2 s early. Acceptable.
3. **The demo:** step 3 depends on the film length (rows 5 to 7, about 27 s). Check on the final film.
4. **One engine:** the chooser shows all four cards from step 1, so "coming soon" is about 7 s early.
5. **Memorial:** read aloud in full it is about 17 s (43 words), one second over its slot, so the pitch would be 2:56.
6. **Impact:** the spoken line is 31 words (12 s), inside its 13 s slot.

## Timing, with and without the memorial slide
- **With** the separate memorial slide: 13 slides, 2:55 (2:56 if the memorial is read aloud in full).
- **Without** it (the note on the close only): 12 slides, 2:39. 16 s are free: give them to the demo or end calmly on the close.
