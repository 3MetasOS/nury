# Refill draft: scorecards for 07f020c (core 6ea102d), pre-filled 2026-10-07 05:25

Source: `evaluations/results/build_comparison.md` (commit 4db17af). **Detention, network and case-file are final. Hospital and the hospital attacker intakes will change after the mini re-run (about 06:00).** Nothing below is written into the deck, descriptions or pitch yet; I fill once, after the mini re-run, so the files never mix two states.

| Set | 8a28a18 fill (now in the files) | 07f020c scorecard | Final? |
|---|---|---|---|
| Detention (20), pass / fail / awaiting | 12 / 6 / 2 | **12 / 1 / 7** | final |
| Hospital (8) | 5 / 1 / 2 | 4 / 1 / 3 | WILL CHANGE |
| Hostile intakes (18) | 11 / 2 / 5 | 12 / 3 / 3 | WILL CHANGE (hospital attacker intakes) |
| Network (3) | 1 / 0 / 2 | 1 / 0 / 2 | final |
| Case-file (5) | 5 / 0 / 0 | 5 / 0 / 0 | final |
| Detention cost, time per run | $0.064, 33.5 s | $1.25 for 20 = $0.0625, 32 s | final |
| Hospital cost, time per run | $0.088, 48.7 s | $0.080, 43.6 s | WILL CHANGE |
| Tone range, detention | 2.60 to 2.85 | **3.06 to 3.32** | final |
| Tone range, hospital | 2.87 to 3.07 | 3.33 to 3.39 | WILL CHANGE |
| Hostile triage escalations | 1 | 1 | |
| Reading level, Spanish INFLESZ, English grade | about 72, 5.2 to 5.4 | 76.4 / 5.2 (detention); 70.6 / 6.4 (hospital) | |

## What would change, if hospital stays as printed (4 / 1 / 3, 12 / 3 / 3)
- Totals across detention, hospital, hostile: pass 28 (12 + 4 + 12), fail 5 (1 + 1 + 3), undecided 13 (7 + 3 + 3), of 46. Description sentence: `46 scenarios, judged: 28 pass, 5 fail, 13 undecided.` (same word count).
- Package caption: `A full package: 32 to 44 s, 6 to 8 cents` (detention 32 s and $0.0625; hospital 43.6 s and $0.0805).
- Deck slide 8 table, cost row `$0.06 and $0.08`, time row `32 s and 44 s`.

## Claims that are NO LONGER TRUE and must be rewritten (honest wording)
1. "Plainer text reads easier and the judge scores it colder. Five detention messages fell below 3 of 5." On 07f020c the detention tone range is 3.06 to 3.32 and none fails on tone. New wording: **the tone score rose from 2.60 to 2.85 to 3.06 to 3.32 after a voice line was added to the pastoral prompts, and still sits well under the target of 4. The judge moves by up to 0.75 between identical runs, is not independent of Jev, and no human has rated warmth. One sample near the 3.0 line proves little.** (Say "rose", never "improved"; it may be noise.)
2. Detention "fail" fell from 6 to 1: five scenarios moved from fail to awaiting review because their tone score crossed 3.0. That is a judge threshold, not a human verdict. State it plainly.
3. Detention 02 (the legal-advice request) still escalates at the checklist (Jev `gives_legal_advice` 0.29 in the review item list; stage 4 halt). Still "a person decides".
4. Hostile intakes: "11 of 18 stopped at triage; after a fix, 1 does" stays true (1 escalation).

## Files to touch after the mini re-run
`deck_template.html` (slide 8 table, four bullets, notes; slide 7 package row; build with `build_deck.py`), `description.txt`, `description_two_playbooks.txt` (recount, 250 or fewer), `PITCH_SCRIPT.md` (impact), `FINALIST_SCRIPT.md` and `ERIC_LINES.md` (package caption, two rows), `TECH_STORY.md` (row 30, caption list, tone sentences), `treatments` (data.py, frames.py, then `treatments/build.py`), `documents/product/ECONOMICS.md` (section 1 table), `WHAT_DID_NOT_WORK.md` (items 1, 2, 5), `HOW_IT_WAS_BUILT.md` (the "On the final build" paragraph), `RESULTS_DRAFT.md`, `CLAIMS_AUDIT.md` (section 1f: the change list), hub rebuild, fit check, and tell hack-video the caption and hack-artisans to rebuild pages.
