Scored build 07f020c (the final commit). All five sets ran on it, from a clean checkout, on 7 October between 04:41 and 05:14 MDT (network re-run at 05:10, because its scenario folder is not in git and the first step ran on an empty folder). Core clean at the start and at the end of each set; the last core commit was 6ea102d. The run used one Gloo key and one Jev key, one job at a time, about $4.2 of a $5.5 cap (the four pipeline sets $3.60, the case-file set $0.59).
Commits since the earlier scored build c317050, and what each changed in behavior:
- b47cc92: rule descriptions only (a disclosed touch during the earlier run).
- 1e019ea: infrastructure. Bounded Gloo retry, audit events with timing, a price table, CI.
- fe1fd7b: both triage prompts treat the intake as untrusted text and always require the six labelled lines.
- e4d19b6: one later-stage context line in eight prompts.
- 8a28a18: plain-language prompts for the family-facing stages; an advisory readability event per stage.
- dde6746: one line on pastoral voice in the prompts (the tone line).
- 0ac365a: hardening (input and request limits, security headers in the app).
- 0dbfebb: an output cap of 1500 on every stage except the checklist.
- f4af33b: robustness; single-pass prompt rendering.
- 6ea102d and d6e8b1a: logging and dead code. 6ea102d is the last commit that touches `code/nury`, `code/playbooks` or `code/skills`.
- dba209c: PyYAML dependency. cbc75db: sanitizer. ed66d99: Jev price in the cost table (public price $0.042 per million input tokens, output free).
Behavior changes that can move a score: 8a28a18 (family-facing wording), dde6746 (pastoral voice), 0dbfebb (output cap), f4af33b (prompt rendering). The rest do not change what the model is asked. No check, gate or threshold changed. The product's reply limits and the 60-call budget live in the app, not in the harness, so no scenario touches them.
Tone, said plainly: the tone judge moves by up to 0.75 between identical runs. One sample near its 3.0 line proves little. Measured on the voice line: baseline 2.89 over 12 draws, 3.20 over 8 draws with the line. In this run the tone scores of the family-facing scenarios are 3.06 to 3.32 in detention and 3.33 to 3.39 in hospital, all in the review band and none below 3.0; on 8a28a18 the same five detention scenarios scored 2.6 to 2.85 and the hospital happy path 2.87. That is a better number from one run, not proof that the messages are warmer.
Build comparison (c317050, 8a28a18, 07f020c): see `build_comparison.md`. The attacker set went from 11 triage escalations at c317050 to 1 at 8a28a18 and 1 now. c317050 results are in `results/before_final2/`, 8a28a18 results in `results/before_final3/`; neither is part of this scorecard.
Reading level (advisory, from the audit events, not tuned): Spanish INFLESZ median 71.4 over 157 family-facing stage drafts, 143 of them at or above 55 (8a28a18: 71.6 over 161, 147). English Flesch-Kincaid grade median 5.65 over 8 drafts, 7 of them at or below grade 8 (8a28a18: 5.15, 6). The formula is a tripwire, not a review: no native Spanish speaker has read the Spanish.
Family-facing stages (rights, attorney, checklist, pastoral) written on the first attempt, across detention, hospital and attacker: 137 of 141 (97.2 percent). Recounted the same way on 8a28a18: 138 of 143 (96.5 percent). Measured, not tuned. (The earlier note gave 165 of 171 for 8a28a18 under a different counting rule; use these two figures.)
Escalations in this run: 4 in 49 runs across the pipeline sets: detention 06 (designed), detention 02 at the checklist, hospital h02 at triage (three banned_phrase rejections), attacker a02 at triage (three banned_phrase rejections). Network 0. Case-file 5 of 5.
Jev judges, deterministic judges and human review score Nury's own words (the verse block is removed with `scripture.strip_block`; the verse is Scripture and is checked by `verse_block_verbatim`).
