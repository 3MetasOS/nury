# Live Gloo checks owed (paused: HTTP 402 INSUFFICIENT_CREDIT)

Run only after hack-sensei says "credits back". In this order. Costs are estimates from earlier runs at $3 / $15 per 1M tokens for Claude and the listed rates for the panel models.

| # | Check | Command | About | Why this order |
|---|---|---|---|---|
| 1 | Smoke: privacy path and gate wrapper | `python3 evaluations/run.py --agent nury --only 01,16 --out /tmp/smoke` and `--playbook hospital --only 01` | $0.20 | Proves credit, the privacy client in the adapter, and the edit-protecting gate before anything bigger. |
| 2 | Case file and revision scenarios | `python3 evaluations/casefile_check.py` | $0.45 | 3 case-file + 2 revision scenarios. v2 saving has only been tested offline. |
| 3 | App end to end with privacy | browser: demo intake, confirm names, 5 gates, Save, Open case, Something changed, Draft again, Compare | $0.15 | Revision path through the UI has never run live. |
| 4 | Network scenarios n01-n03 | `NURY_DEMO_NETWORK=1 python3 evaluations/run.py --agent nury --scenarios network --jev` | $0.30 | Needs jedi's network wiring in the stages (on main 15b5222). |
| 5 | FINAL scored sets, core frozen 08:00, privacy ON | `python3 evaluations/run.py --agent nury --jev` then `--playbook hospital --jev` | $2.50 | The numbers we quote. Includes the checklist prompt change (scenarios 1, 18, 20) and h03. |
| 6 | Panel validation, second pass | `python3 evaluations/validate_panel.py` | $0.60 | First pass had gemini JSON errors (parser fixed, not yet re-validated). |
| 7 | Panel on the final sets | `python3 evaluations/judges/redteam_panel.py evaluations/results/runs.json` and the hospital one | $1.20 | Findings go to Juan's canvas. |
| 8 | Attacker intakes a01-a18 | `python3 evaluations/run.py --agent nury --scenarios scenarios_attacker --jev` | $1.10 | After the final sets and the panel, as hack-sensei set. |
| 9 | Regenerate the review canvas and scorecards | `python3 evaluations/make_review_canvas.py` (offline) | $0 | After 5 to 8. |

Total about $6.5. Never run these in parallel against one key; Gloo rate limits showed up when two runs shared it.
One probe call (16 output tokens) was made at about 21:50 MDT to confirm the 402, before the pause message was read. No other live call since.
