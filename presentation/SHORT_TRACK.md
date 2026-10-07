# Short track: five slides, about 90 seconds

Written 2026-10-07 by hack-ninja for hack-sensei (Juan's request). Just the hook, the why, the video and the "so what?". No architecture, no evaluation, no numbers tables. Pace 2.6 words a second. 127 spoken words and a 27 s film. The film plays with no voice. The deck file is not edited here.

## Spoken script with times
| Slide | Name in the deck | Existing or new | Time | Spoken line (exact) | Words |
|---|---|---|---|---|---|
| 1 | the-call | existing | 0:00 to 0:11 | "It is 2:07 in the morning. A pastor's phone rings. A husband was detained last evening. The pastor has a phone and no lawyer on the line." | 29 |
| 2 | the-name | existing, short | 0:11 to 0:17 | "This is Nury. The name comes from the Arabic word for light." (the entry builds in about 2 s) | 12 |
| 3 | why-it-matters | NEW | 0:17 to 0:30 | "When a pastor has Nury, the family gets help in their own language. A first draft is ready in under a minute. And the pastor approves every word." | 28 |
| 4 | the-demo | existing | 0:30 to 1:08 | Before (0:30 to 0:33): "Here is one call, start to finish." Film plays, no voice (0:33.5 to 1:00.5, 27 s). After (1:01.5 to 1:07): "A draft that failed was held back. Nury never sends. The pastor does." | 20 |
| 5 | so-what | NEW | 1:08 to 1:20 | "A pastor never faces the call alone with a blank page. Every crisis can become a folder. Nothing is sent unless the pastor sends it." | 25 |
| 6 | close | existing | 1:20 to 1:30 | "The next call will come. Nury is there when the pastor picks up." Then the two memory lines stay on screen, silent, for the last 4 s. | 13 |

Total 90 s. The gap with no voice, other than the film, is never over about 3 s; the last 4 s are the silent memory lines.
The "five slides" are 1 to 5; the Close (6) is the closing frame, with the two memorial lines.

## New slide 3: why-it-matters
- **Headline (7 words):** What changes when a pastor has Nury
- **One line (8 words):** A careful first draft, in the family's language.
- **Three labels:** In the family's language · A first draft in under a minute · The pastor approves every word
- **Beats (3 presses):** 1 at "the family gets help": the first label; 2 at "A first draft": the second label; 3 at "approves every word": the third label.
- **Notes (time 0:17 to 0:30, 13 s; criterion: Impact and Concept):** Say the three claims in order. VERIFIED: family materials come out in the family's language (Spanish for both live crises; ALIGNMENT_AUDIT.md, Stages). A first draft in under a minute: a full case, all stages, took 34 to 50 seconds of model time in the final scored runs (detention 34.2 s mean of 20, hospital 49.5 s mean of 8). That excludes the pastor's reading and editing. The pastor approves, edits or stops after every stage. DO NOT SAY: hours saved, faster than anything, or any comparison, because we measured none. Do not say "ready in under a minute" without "first draft".

## Existing slides, as built
- **1 the-call and 2 the-name:** the text and beats are the same as the long pitch (DECK_COPY slides 1 and 2). On the name slide, say only the two sentences above.
- **4 the-demo:** the film (or the raw app video) plays, with no voice. The slide shows "How this case went" and the caption "Nothing moves on without the pastor." Before and after lines as in the table. If the film fails, leave the slide up and say the same two lines.

## New slide 5: so-what
- **Headline (2 words):** So what?
- **One line (6 words):** Three things stay true, every time.
- **Three lines (the answer):**
  1. A pastor never faces the call alone with a blank page.
  2. Every crisis can become a folder.
  3. Nothing is sent unless the pastor sends it.
- **Beats (3 presses):** 1 at "A pastor never faces": line 1; 2 at "Every crisis": line 2; 3 at "Nothing is sent": line 3.
- **Notes (time 1:08 to 1:20, 12 s; criterion: Concept and Innovation):** Line 1 is the product's purpose: the pastor gets a structured case, a sourced brief and a draft message to read, edit or reject. Line 2 is "built to grow": a crisis is a folder of plain files, two run today. Line 3 is the rule: Nury has no send path. Nothing here claims a pastor has used it; do not say so. Do not add numbers.

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
1. Slide 2: "The name comes from the Arabic word for light." (3.5 s)
2. Slide 5, line 2: "Every crisis can become a folder." (2.4 s)
3. Slide 1: "The pastor has a phone and no lawyer on the line." (4 s)
Never cut: the film, "Nury never sends. The pastor does.", and the last two lines of the close.
