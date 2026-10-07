# Finalist video: continuous audio script (90 s)

Written 2026-10-07 by hack-ninja for hack-video and hack-sensei. Rule from Juan: the voice never stops for more than a few seconds. No silence over 2.5 s anywhere except the last 3 s (the end card). Eric narrates all the way, calm and warm. The order and wording follow the 12 deck slides in `DECK_COPY.md`, in the same order; no new claims, no "package", Jev is "a second check", the tagline sits below the logo, "two evaluation systems".

## Pace and budget
- **212 words** in 25 lines. Measured Eric pace on the 15 rendered clips (`video/vo/arc/*.wav`): 86 words in 29.5 s, about 2.9 words a second inside a clip. Lengths below use the measured length for lines already rendered and words ÷ 2.9 for new lines.
- **Breath between lines: 0.58 s** (inside your 0.4 to 0.8 s).
- **Voice runs from 0.3 s to 86.8 s.** Then the end card, silent, to 90 s. The longest gap is 0.58 s.
- New-line lengths are estimates. After the real render, re-time from the actual durations. If it runs long, cut from the list below, in order.
- Sensei's estimate was 235 words at 2.6 words a second including breaths. This script has 212 words and fills the 87 s of voice with no spare time, so the trim list below is the margin: if a real render runs long, cut from it.

## Timed table
Status is against `ERIC_LINES.md`. Re-render only NEW and CHANGED. UNCHANGED lines use the existing `video/vo/arc/` files (L1, L2, L3 or its retake, L4, L5, L6, L10, L11, E1, E4, E5, E7).

| Start (s) | ID | Eric line | Status | Caption on screen | Section and screen |
|---|---|---|---|---|---|
| 0.3 | L1 | 2:07 AM. Maria is calling. | UNCHANGED | 2:07 AM. A pastor's phone rings. | 1 The call: Dark; the phone lights up |
| 3.1 | L2 | Her husband was detained last evening. | UNCHANGED | A husband was detained last evening. | 1 The call: Porch light at night |
| 5.7 | N1 | The pastor has a phone, and no lawyer on the line. | NEW | A pastor. No lawyer on the line. | 1 The call: Same; the hand note |
| 10.1 | L3 | This is Nury. | UNCHANGED | Nury (the dictionary entry builds) | 2 The name: Paper turns, the lantern lights |
| 11.5 | N2 | The name comes from the Arabic word for light. | NEW | nur, light · see also: lantern | 2 The name: The entry; "see also: lantern" |
| 15.2 | N3 | Nury is one engine. Each crisis has its own stages. | NEW | One engine. Every crisis is its own workflow. | 3 One engine: The chooser, then the stage rows |
| 19.2 | N4 | Two run today, immigration and hospital. | NEW | Immigration matter · Hospital emergency | 3 One engine: The two live cards; two coming soon |
| 21.9 | E1 | He types what she says. | UNCHANGED | The intake is typed | 4 The demo: Intake screen (screens/04-intake) |
| 23.7 | E4 | Pick a crisis. Triage comes first. | UNCHANGED | Pick the crisis | 4 The demo: Chooser, then the triage card (screens/03, 05) |
| 26.4 | L4 | Five stages. A gate after each. | UNCHANGED | Five stages. A gate after each. | 4 The demo: "How this case went": five stages |
| 28.8 | E5 | Approve, edit or stop. | UNCHANGED | Approve · Edit · Stop | 4 The demo: The thumb taps Approve (screens/05-gate) |
| 30.7 | L5 | Her language. Every point cited. | UNCHANGED | Her language. Every point cited. | 4 The demo: The rights brief and its source chips |
| 33.4 | L6 | Unsafe draft. Rejected. He never sees it. | UNCHANGED | Rejected: held back | 4 The demo: The rejected-and-regenerated moment |
| 36.2 | E7 | It rewrites. It checks again. | UNCHANGED | Regenerating, then Passed | 4 The demo: Regenerating, then Passed strip |
| 38.4 | N5 | The family gets a Spanish copy, as a PDF the pastor can hand over. | NEW | A PDF the pastor can hand over. | 5 The family copy: Family copy page 1 and pastor copy page 2 (images/family-copy-p1.png) |
| 43.8 | N6 | A new crisis is a new folder. Add a folder, not engine code. | NEW | A new crisis is a new folder. | 6 Built to grow: The folder tree; the tags |
| 48.9 | N7 | The engine is plain Python, with no framework. Shared skills keep the words plain and the facts sourced. | NEW | Nury engine · shared skills: voice, grounding | 7 The agent and its skills: Architecture map, Layer 2 (The agent) |
| 55.7 | N8 | Claude Sonnet 4.6 writes through Gloo AI Studio, seeing tokens, not names. | CHANGED (L7: adds the model name, "through") | Only tokens reach Gloo AI Studio. | 8 Gloo and Claude: The token line; Gloo node lights |
| 60.4 | N9 | Jev, from TypeSafe, is a second check on every draft. People decide. | CHANGED (L8) | Jev, a second check | 9 Jev: Use of AI band; Jev node lights |
| 65.1 | N10 | Bible verses come from YouVersion. The model never writes one. | NEW | Verses from a verified list | 10 Verses: Architecture map, Layer 3 (YouVersion) |
| 69.2 | N11 | We built two evaluation systems. One tests before release. One checks every draft. | NEW | Two evaluation systems | 11 Evaluation: The two lanes; Jev pill |
| 74.2 | N12 | Forty-six made-up cases: twenty-nine pass, two fail, fifteen wait for a person. | NEW | 46 cases: 29 passed · 2 failed · 15 waiting | 12 The numbers: Impact counts run up |
| 78.9 | N13 | A case costs six to nine cents. | NEW | 6 to 9 cents a case · 34 to 50 seconds | 12 The numbers: Impact cost chips |
| 81.9 | L10 | Nury is not a pastor. It never sends. | UNCHANGED | Nury is not a pastor. | 13 The close: The close slide |
| 85.0 | L11 | An AI crisis response agent. | UNCHANGED | An AI Crisis Response Agent (below the logo) | 13 The close: Logo, tagline below it |

Placement note: the numbered ids N1 to N13 are new line ids for this script (N8 is the changed L7, N9 the changed L8). Rename them as you like.

## End card (last 3 s, no voice)
The logo with the tagline below it, and two small lines: "In memory of Tía Nury" and "08-2026". No narration. No other text.

## What to render
- **NEW (11 lines):** N1, N2, N3, N4, N5, N6, N7, N10, N11, N12, N13.
- **CHANGED (2):** N8 (was L7: now names Claude Sonnet 4.6 and says "through"), N9 (was L8: now "a second check", from TypeSafe).
- **UNCHANGED:** the other 12 lines.
- Pronunciation: Gloo as GLOO, Jev as JEV, "2:07 AM" as "two oh seven A M", Nury normal spelling. Numbers as words: "forty-six", "twenty-nine", "fifteen", "six to nine cents".

## Most cuttable sentence in each section (trim in this order if the real render runs long)
| Order | Section | Cut this | Saves (est.) |
|---|---|---|---|
| 1 | 12 Numbers | N13 "A case costs six to nine cents." | 3.0 s |
| 2 | 10 Verses | N10 "Bible verses come from YouVersion. The model never writes one." | 4.0 s |
| 3 | 2 The name | N2 "The name comes from the Arabic word for light." | 3.8 s |
| 4 | 1 The call | N1 "The pastor has a phone, and no lawyer on the line." | 4.3 s |
| 5 | 7 Agent and skills | the second sentence of N7: "Shared skills keep the words plain and the facts sourced." | 3.4 s |
| 6 | 3 One engine | N4 "Two run today, immigration and hospital." | 2.6 s |
| 7 | 6 Built to grow | the second sentence of N6: "Add a folder, not engine code." | 2.4 s |
| 8 | 4 The demo | E7 "It rewrites. It checks again." (the screen still shows Regenerating, then Passed) | 2.2 s |
| 9 | 8 Gloo and Claude | the clause in N8: "seeing tokens, not names" (the caption still says it) | 2.0 s |
| 10 | 11 Evaluation | the sentence in N11: "One tests before release." (keep "One checks every draft.") | 1.7 s |
| 11 | 9 Jev | the sentence in N9: "People decide." | 1.5 s |
| last resort | 5 Family copy | N5 (the screen shows the PDF with its caption) | 5.0 s |
| never | 13 Close | L10 and L11 stay: the honesty line and the tagline | |
Cutting the first four saves about 15 s of voice. Each gap stays under 2.5 s only if the next line starts after the cut: close the gap, do not leave a hole.

## Checks against the final truth (ALIGNMENT_AUDIT.md)
- 46 cases, 29 pass, 2 fail, 15 undecided ("wait for a person"): audit row Results. Judge results, not human verdicts; no pass rate is spoken.
- 6 to 9 cents a case: audit row Cost and time.
- Claude Sonnet 4.6 through Gloo AI Studio; tokens, not names: audit rows Pipeline and Privacy.
- Jev, from TypeSafe, a second check on every draft: audit row Jev gate.
- Verses: the model picks an id from an approved list; text from YouVersion (44 of 45 on the final build): audit row Scripture.
- Two evaluation systems: DECK_COPY slide 9.
- "Engine is plain Python, no framework": README and HOW_IT_WAS_BUILT; "shared skills": FEATURES section 6 (voice and grounding built and live verified). Nothing says skills improve results.
- The name: Arabic nur, "light" (`NAME_ENTRY.md`). Sources differ on "luminous" and "my light"; both say light. The memorial text is not read.
- Not claimed: that any pastor, attorney or family used Nury.
