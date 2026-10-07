# Live Gloo checks owed: ONE merged plan (paused: HTTP 402 INSUFFICIENT_CREDIT)

Run only after hack-sensei says "credits back". In this order. Never run two of these in parallel on one key (rate limits showed up when two runs shared it).

Unit costs, measured: detention pipeline about $0.055 (20 runs cost $1.09), hospital pipeline about $0.076 (8 runs cost $0.61), panel review of one scenario about $0.076 (3 reviewers). Model `gloo-anthropic-claude-sonnet-4.6` at $3 / $15 per 1M tokens. Privacy adds about 4 to 5 percent input tokens (hack-jedi's measurement), not included below. Every figure is an estimate except the panel validation pass.

| # | Tier | Owner | Step | How | Est. cost | Running total |
|---|---|---|---|---|---|---|
| 0 | SMOKE | artisans | Smoke: 1 pipeline through the adapter with privacy on | `run.py --agent nury --only 01 --out /tmp/smoke` (Proves credit, privacy client, gate wrapper. Stop here if it fails.) | $0.06 | $0.06 |
| 1 | MUST | artisans | Forced rejection through privacy | scenario 05 (rejected-and-regenerated) + scenario 16 (pastor edit adds a name) (The demo beat and the edit-protection path.) | $0.11 | $0.17 |
| 2 | MUST | artisans | FINAL scored detention 20, privacy on, Jev on | `run.py --agent nury --jev` on the frozen core (08:00) (Jev is billed by TypeSafe, not the Gloo wallet (assumed; confirm).) | $1.10 | $1.27 |
| 3 | MUST | artisans | FINAL scored hospital 8 (incl. h03), privacy on, Jev on | `run.py --agent nury --playbook hospital --jev` | $0.61 | $1.87 |
| 4 | MUST | hack-jedi | Core checks: detention 01, 18, 20; hospital h01; 2 forced rejections (about 12 pipelines) | jedi's own list (Estimate: 8 detention + 4 hospital pipelines.) | $0.74 | $2.62 |
| 5 | MUST | hack-video | 1 capture of the demo | one full detention demo run with the forced rejection (Screen recording of one run.) | $0.06 | $2.67 |
| 6 | SHOULD | artisans | Case file: 3 save checks | `casefile_check.py` cf01-cf03 | $0.17 | $2.84 |
| 7 | SHOULD | artisans | Revision: 2 scenarios (each is 2 pipelines) | rv01 detention, rv02 hospital (v1 then v2.) | $0.26 | $3.10 |
| 8 | SHOULD | artisans | Revision and privacy through the real UI, once | browser: demo, confirm names, 5 gates, Save, Something changed, Draft again, Compare (Revision has never run live.) | $0.11 | $3.21 |
| 9 | SHOULD | artisans | Network scenarios n01-n03 | `run.py --scenarios network --jev` with NURY_DEMO_NETWORK=1 (Needs jedi's network wiring (on main).) | $0.19 | $3.40 |
| 10 | SHOULD | artisans | Panel validation, second pass | `validate_panel.py` (16 reviews x 3 reviewers) (First pass cost $0.58 (measured).) | $0.58 | $3.98 |
| 11 | SHOULD | artisans | Panel on the final sets (28 scenarios) | `judges/redteam_panel.py` on both runs.json (Measured $0.076 per scenario for 3 reviewers.) | $2.13 | $6.10 |
| 12 | COULD | artisans | Attacker intakes a01-a18 | `run.py --scenarios scenarios_attacker --jev` (12 detention + 6 hospital.) | $1.12 | $7.22 |
| 13 | COULD | artisans | Panel on the attacker runs | 18 scenarios x panel (Only if the attacker run finds something.) | $1.37 | $8.59 |
| 14 | COULD | hack-jedi | Skills before/after (scenarios 1, 9, 13, 14, 20, h01, h07, OFF and ON) | 14 pipelines (5 detention + 2 hospital, each twice.) | $0.85 | $9.44 |
| 15 | COULD | hack-video | 1 retake | one more full demo run | $0.06 | $9.50 |

## Totals by tier

- SMOKE: $0.06. Through SMOKE: $0.06.
- MUST: $2.62. Through MUST: $2.67.
- SHOULD: $3.43. Through SHOULD: $6.10.
- COULD: $3.39. Through COULD: $9.50.

**Everything: $9.50.** Suggested top-up: through SHOULD plus 30 percent for retries and reruns after a fix, about $7.93; add the COULD tier only if there is time.

## Notes
- MUST = the final scored runs, the privacy path and the forced rejection. SHOULD = panel final, revision, network. COULD = attacker, skills A/B, retake.
- A fix after a failed run means rerunning that run. The 30 percent covers that.
- Jev judge calls go to the TypeSafe API with `JEV_API_KEY`. I have assumed that is a separate balance from the Gloo wallet. Please confirm.
- One 16-token probe call was made at about 21:50 MDT to confirm the 402, before the pause message was read. No other live call since.
- Regenerate the review canvas and scorecards after the final runs (`make_review_canvas.py`, offline, free).

## Owed after the 402 pause (hack-artisans, 2026-10-07)

All need credit and sensei's "credits back". One job at a time. Before the first one: a single plain Gloo call to confirm the key works (a 402 mid-set would score as errors).

| Order | What | Command (from evaluations/) | Estimate (Gloo) |
|---|---|---|---|
| 1 | Detention, all 20, on the final commit | `python3 run.py --agent nury --jev --out results` | $1.5 |
| 2 | Hospital, all 8 | `python3 run.py --agent nury --jev --playbook hospital --out results/hospital` | $0.7 |
| 3 | Attacker a01 to a18 (record stage and categories of any escalation) | `python3 run.py --agent nury --jev --scenarios scenarios_attacker --out results/attacker` | $1.2 |
| 4 | Network n01 to n03 | `NURY_DEMO_NETWORK=1 python3 run.py --agent nury --jev --scenarios network --out results/network` | $0.2 |
| 5 | Case-file cf01 to cf05 | `python3 casefile_check.py` | $0.3 |
| 6 | Regenerate: scorecards (`python3 report.py <dir>/runs.json`), `python3 tone_compare.py`, `python3 make_review_canvas.py` | offline | none |

Total about $3.9 of Gloo credit, plus Jev on its own key. The c317050 results are kept in `results/before_final2/`. The scorecard note (`scorecard_final_note.md`) must list every commit since c317050: b47cc92 (descriptions), 1e019ea (infrastructure), fe1fd7b and the later-stage context commit (prompt text), and name the final commit id.
Not owed live: the smoke-evaluation button on the Observability page (off by default; tests never confirm it).
