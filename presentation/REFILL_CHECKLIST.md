# Refill checklist: after the next final commit and re-run

The fill from build `8a28a18` is **INTERIM** (hack-sensei, 2026-10-07). hack-jedi commits a tone fix (if it works) and the security hardening, then announces one final commit. hack-artisans re-runs all five sets. Then refill from the NEW `evaluations/results/scorecard.md`. Target: 20 minutes. Never fill from a partial run. Never call Gloo.

## Update 2026-10-07 04:41: final commit is `07f020c`
hack-artisans re-runs all five sets on it (about 45 minutes). Last scorecards in the repo are still for `8a28a18` (commit 16e8177). Refill only when the scorecard table shows core `07f020c`. Tone wording must stay honest: the judge is noisy (up to 0.75 between identical runs), not independent of Jev, and no human has rated warmth. The limits L1 to L5 (documents/product/CODE_REVIEW.md section 4) stay in the docs. Also refill: both descriptions (recount, 250 or fewer), pitch, FINALIST scripts, TECH_STORY, ECONOMICS, the hub; and write the change list.

## 0. Read first (3 min)
- `evaluations/results/scorecard.md`: the "Build comparison" table (core commit per row) and the failures list. Confirm the final core commit id in the table equals the announced commit.
- `evaluations/results/hospital/scorecard.md`, `attacker/scorecard.md`: cost and time per run.
- Write a CHANGE LIST (what moved, old to new) for hack-sensei.

## 1. The numbers to take (fill the right column)
| Item | Interim value (8a28a18) | New value |
|---|---|---|
| Detention pass / fail / undecided (20) | 12 / 6 / 2 | |
| Hospital (8) | 5 / 1 / 2 | |
| Hostile intakes (18) | 11 / 2 / 5 | |
| Total scenarios, pass, fail, undecided | 46: 28 / 9 / 9 | |
| Detention cost per run, time | $0.0642, 33.5 s | |
| Hospital cost per run, time | $0.0878, 48.7 s | |
| Tone range, detention / hospital | 2.60 to 2.85 / 2.87 to 3.07 | |
| Hostile triage escalations | 1 of 18 | |
| Reading level (Spanish INFLESZ, English grade) | about 72, 5.2 to 5.4 | |
| Jev tokens per package (from the audit files, see ECONOMICS section 3.6) | 8,220 detention, 11,486 hospital | |
| Product tests, evaluation tests | 270, 86 | recount (`code/test.sh`, `pytest evaluations/tests`) |

## 2. Where each goes
1. **Deck** (`presentation/deck_template.html`, then `python3 presentation/build_deck.py`): slide "08 Impact" table (3 rows, cost, time), the four bullets, the notes; backup "Why two judges" final row; slide 7 "A full package" row (`33 to 49 s, 6 to 9 cents`).
2. **Descriptions**: the one sentence `46 scenarios, judged: 28 pass, 9 fail, 9 undecided.` in `description.txt` and `description_two_playbooks.txt`. Keep the two-playbooks file at 250 words or fewer (`python3 -c "print(len(open('presentation/description_two_playbooks.txt').read().split()))"`).
3. **Pitch** (`PITCH_SCRIPT.md`): the impact section (about 30 words) and nothing else.
4. **Captions "A full package: 33 to 49 s, 6 to 9 cents"**: `deck_template.html`, `ERIC_LINES.md`, `FINALIST_SCRIPT.md` (two rows), `TECH_STORY.md` (row 30 and the caption list), `TREATMENTS.md`, `treatments/data.py`, `treatments/frames.py`; tell hack-video (`tech.json`, `NuryA.tsx`).
5. **`documents/product/HOW_IT_WAS_BUILT.md`**: the paragraph "On the final build, a full package took ..." (section 2). Warn hack-artisans to rebuild the page before editing.
6. **`documents/product/ECONOMICS.md`**: table in section 1 and the Jev tokens in 3.6. **`WHAT_DID_NOT_WORK.md`**: items 1, 2, 5 (tone and hostile-intake numbers).
7. **`CLAIMS_AUDIT.md`**: append a section 1f with the change list.
8. Rebuild: `python3 presentation/treatments/build.py`, `python3 documents/hub/build.py`, fit check at 1280x720, 1920x1080, 390x844 in default and `?gated` views.

## 3. Claims that depend on the tone fix
- "Tone: plainer text reads easier and the judge scores it colder" (deck slide 8, WHAT_DID_NOT_WORK item 1, ECONOMICS none, pitch). **Keep only if still true.** If the fix lifts tone to 3 or above, say what changed and drop "scores it colder". If it does not, keep the sentence and say the fix did not work.
- "Five detention messages fell below 3" needs the new count.

## 4. Do not forget
- The red-team panel was NOT re-run on 8a28a18 (deck backup row says so). If it is re-run, update the row; if not, keep the words.
- Commit with the real clock. No date variables.
