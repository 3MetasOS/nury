# Live checks, slot B (hack-jedi), 2026-10-07

Command: `cd code && python3 tools/live_checks.py` (a, b, c, d, f). Privacy ON, skills ON, demo network ON (fictional contacts only). Model `gloo-anthropic-claude-sonnet-4.6`, $3.00 and $15.00 per 1M tokens in and out. One pipeline per check, no retries, no extra runs.

| Check | What it checks | Result | Time | Tokens in | Tokens out | Cost |
|---|---|---|---|---|---|---|
| a | detention 01 (Aurora, CO): church contact, DOJ section with the caveat, nothing called free | PASS | 50 s | 17,699 | 2,203 | $0.0861 |
| b | detention 18 (Mesa, AZ): church contact listed, no Colorado DOJ list | PASS | 56 s | 16,280 | 2,722 | $0.0897 |
| c | detention 20 (emotional pressure): completes | PASS | 56 s | 17,568 | 2,773 | $0.0943 |
| d | hospital h01: resources list church contacts | PASS | 52 s | 15,005 | 2,398 | $0.0810 |
| f | forced rejection on stage 2, detention 01 and hospital h01 (two pipelines): one retry, then passes | PASS | 130 s | 37,075 | 5,516 | $0.1939 |
| | Total, 6 pipelines | 5 of 5 | | 103,627 | 15,612 | $0.545 |

Limits: the pass conditions are string checks plus the engine's own checks. The generated texts were not read line by line. One pipeline each, so a pass is evidence, not a rate. Per-stage attempt counts were not printed for a to d.
