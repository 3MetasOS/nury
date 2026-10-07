# Short track: five slides, about 90 seconds

Written 2026-10-07 by hack-ninja for hack-sensei (Juan's request). Just the hook, the why, the video and the "so what?". No architecture, no evaluation, no numbers tables. Pace 2.6 words a second. 142 spoken words and a 27 s film. The film plays with no voice. The deck file is not edited here.

## Spoken script with times (re-budgeted 2026-10-07 for Juan's new slides 1 and 2)
| Slide | Name in the deck | Existing or new | Time | Spoken line (exact) | Words |
|---|---|---|---|---|---|
| 1 | the-call | new copy | 0:00 to 0:13 | "A crisis doesn't wait for morning. A pastor's phone rings at 2 AM. A husband was detained, and a family needs answers now. The pastor has care to give, but not the facts." | 32 |
| 2 | the-name | new copy | 0:13 to 0:25 | "That is why we built Nury. Nury prepares the right information for the pastor to review: comfort, spiritual support, and what to do tonight and next. The pastor is never alone." | 31 |
| 3 | why-it-matters | NEW | 0:25 to 0:35 | "The family gets help in their own language. A first draft is ready in under a minute. The pastor approves every word." | 22 |
| 4 | the-demo | existing | 0:35 to 1:11 | Before (0:35 to 0:38): "Here is one call, start to finish." Film plays, no voice (0:38.3 to 1:05.3, 27 s). After (1:06 to 1:11): "A draft that failed was held back. Nury never sends. The pastor does." | 20 |
| 5 | so-what | NEW | 1:11 to 1:21 | "A pastor starts with a careful draft, not a blank page. Every crisis can become a folder. Nothing is sent unless the pastor sends it." | 24 |
| 6 | close | existing | 1:21 to 1:30 | "The next call will come. Nury is there when the pastor picks up." Then the two memory lines stay on screen, silent, for the last 4 s. | 13 |

Total 90 s: 142 spoken words plus the 27 s film. Slide 3 lost its opening clause ("When a pastor has Nury,") and slide 5 line 1 changed, so "never alone" appears only once (slide 2). No voice gap over about 3 s except the film and the last 4 s.
Slide 3's beats stay as written below. The "five slides" are 1 to 5; the Close (6) is the closing frame.

## New slide 3: why-it-matters
- **Headline (7 words):** What changes when a pastor has Nury
- **One line (8 words):** A careful first draft, in the family's language.
- **Three labels:** In the family's language · A first draft in under a minute · The pastor approves every word
- **Beats (3 presses):** 1 at 0.0 "The family gets help": the first label; 2 at 3.2 "A first draft": the second label; 3 at 6.8 "approves every word": the third label.
- **Notes (time 0:17 to 0:30, 13 s; criterion: Impact and Concept):** Say the three claims in order. VERIFIED: family materials come out in the family's language (Spanish for both live crises; ALIGNMENT_AUDIT.md, Stages). A first draft in under a minute: a full case, all stages, took 34 to 50 seconds of model time in the final scored runs (detention 34.2 s mean of 20, hospital 49.5 s mean of 8). That excludes the pastor's reading and editing. The pastor approves, edits or stops after every stage. DO NOT SAY: hours saved, faster than anything, or any comparison, because we measured none. Do not say "ready in under a minute" without "first draft".

## Existing slides, as built
- **1 the-call and 2 the-name:** new copy, in `presentation/short/COPY_1_2.md` (on-screen text, voice, beats, notes).
- **4 the-demo:** the film (or the raw app video) plays, with no voice. The slide shows "How this case went" and the caption "Nothing moves on without the pastor." Before and after lines as in the table. If the film fails, leave the slide up and say the same two lines.

## New slide 5: so-what
- **Headline (2 words):** So what?
- **One line (6 words):** Three things stay true, every time.
- **Three lines (the answer):**
  1. A pastor starts with a careful draft, not a blank page.
  2. Every crisis can become a folder.
  3. Nothing is sent unless the pastor sends it.
- **Beats (3 presses):** 1 at 0.0 "A pastor starts": line 1; 2 at "Every crisis": line 2; 3 at "Nothing is sent": line 3.
- **Notes (time 1:08 to 1:20, 12 s; criterion: Concept and Innovation):** Line 1 replaces "never alone" (now said on slide 2). It is the product's purpose: the pastor gets a structured case, a sourced brief and a draft message to read, edit or reject. Line 2 is "built to grow": a crisis is a folder of plain files, two run today. Line 3 is the rule: Nury has no send path. Nothing here claims a pastor has used it; do not say so. Do not add numbers.

## Close (the closing frame)
- Logo, tagline below it ("An AI Crisis Response Agent."), the two small lines "In memory of Tía Nury" and "08-2026". The voice stops after "picks up." The lines stay silent.

## Claims check against ALIGNMENT_AUDIT.md
- 34 to 50 s per case (all stages, model time): audit row Cost and time. Said as "a first draft in under a minute".
- Family language: Stages row (Spanish output). Two live crises: Live crises row.
- Pastor approves every stage; nothing is sent: Pipeline row; README.
- "Every crisis can become a folder": Built to grow, HOW_IT_WAS_BUILT; a new crisis is a folder, adding one does not change the engine.
- Not in this track: Jev, rules, evaluation, numbers, tables. The Jev disclosure line is in the description and the About page, not on these slides.
- The Arabic nur: NAME_ENTRY.md ("light").

## Cuts if it runs long
1. Slide 3, the first label sentence if needed: "The family gets help in their own language." keeps the label on screen (3.2 s)
2. Slide 5, line 2: "Every crisis can become a folder." (2.4 s)
3. Slide 1: "The pastor has care to give, but not the facts." (3.8 s)
Never cut: the film, "Nury never sends. The pastor does.", and the last two lines of the close.
