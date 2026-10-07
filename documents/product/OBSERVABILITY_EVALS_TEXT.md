# Observability page: text for the Evaluations section

Written 2026-10-07 by hack-ninja for hack-artisans. For people who are not statisticians. Plain words, grade 6. Each card has a question for a title, one sentence with the result, a line on what the bar means, and one line on what the card does not tell you. Numbers in curly braces come from the scorecard, as the cards do today. The "now" column shows the values from the final scored build (core `9bc5c6d`) so you can check the wording.

## Section introduction (two lines)

**Evaluations.** We ran Nury on made-up families before release and checked each result with automatic judges. These cards show what the judges found. A person has not read every result yet.

## Card 1: Detention

**Title:** Did Nury handle the detention cases?
**Result sentence:** {passed} of {scenarios} detention cases passed the judges. (Now: 11 of 20.)
**What the bar means:** Each case is one small piece of the bar. Green passed the judges. Red failed. Amber is waiting for a person to read it. (Now: 11 passed, 1 failed, 8 waiting.)
**What this does not tell you:** A pass means the judges found no problem. It does not mean a person agreed. Eight cases still wait for a person. These families were made up for testing.
**Small print line:** Cost of the whole set {total} ({per run} for each case). (Now: $1.28, $0.06.) "Version" is the build of the engine that ran the test. (Now: `9bc5c6d`.)

## Card 2: Hospital

**Title:** Did Nury handle the hospital cases?
**Result sentence:** {passed} of {scenarios} hospital cases passed the judges. (Now: 5 of 8.)
**What the bar means:** Same colors. Green passed, red failed, amber waits for a person. (Now: 5 passed, 0 failed, 3 waiting.)
**What this does not tell you:** Eight cases is a small set, so one case moves the bar a lot. Three cases still wait for a person. No hospital staff have read the results.
**Small print line:** Cost {total}, {per run} for each case. (Now: $0.71, $0.09.) Version `9bc5c6d`.

## Card 3: Hostile intakes

**Title:** Did Nury hold up when someone pushed it?
**Result sentence:** {passed} of {scenarios} hostile cases passed the judges. (Now: 13 of 18.)
**What the bar means:** These are messages written to push Nury into giving advice, making promises or claiming a role. Green passed, red failed, amber waits for a person. (Now: 13 passed, 1 failed, 4 waiting.)
**What this does not tell you:** We wrote these tests ourselves, so a real attacker may try things we did not think of. A pass is a judge result, not a person's verdict.
**Small print line:** Cost {total}, {per run} for each case. (Now: $1.51, $0.08.) Version `9bc5c6d`.

## Card 4: A quick check you run yourself (shown when you press "Run a smoke evaluation")

**Title:** What did this quick check find?
**Result sentence:** {passed} of {scenarios} quick-check cases passed the judges. (The quick check runs 3 detention cases.)
**What the bar means:** Same colors as above. The bar is built from this run only, not from the saved scorecards.
**What this does not tell you:** Three cases are a spot check, not a score. Run it to see the system work, not to measure it. It costs real money (about {estimate}).
**Note under the button (replace the current one):** This runs 3 detention cases with the same checks as a full run. It costs about {estimate} of Gloo credit. Jev is paid for on its own key.

## Words to use, words to avoid

- Say "passed the judges", not "pass rate". We do not quote a pass rate, because people have not read every result.
- Say "waiting for a person" for the amber part. Never call amber "passed".
- Say "version" or "build of the engine", not "core commit", on the page. Keep the code in small print.
- Do not use "median", "probability", "band" or "percentile" in this section. If a number needs one of those, add a sentence in plain words.
- When the judge for tone ("is it warm?") is shown anywhere, add: "This judge gives different scores to the same text, and no person has rated warmth."
- Keep the line "A judge pass is not a review by a person." It is true on every card.

## Checks I ran

- Reading level of the card sentences (`documents/product/readability_check.py`, Flesch-Kincaid): median grade 3.7, highest 8.6.
- Numbers match `evaluations/results/build_comparison.md` for build `9bc5c6d` (detention 11 / 1 / 8, hospital 5 / 0 / 3, hostile 13 / 1 / 4) and the scorecards' cost lines ($1.2753, $0.7097, $1.51 in total).
- The page code in `code/app/static/observability.html` and `code/app/evals_api.py` reads the scorecards, so the numbers update when a scorecard changes; this text uses braces for those.
