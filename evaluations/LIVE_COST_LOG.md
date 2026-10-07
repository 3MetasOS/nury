# Live run cost log (Gloo `gloo-anthropic-claude-sonnet-4.6`, $3 / $15 per 1M tokens in / out)

One row per live run, from the run records. Privacy layer on. Jev not used in these runs.

| When (MDT) | Slot / step | Run | Result | Tokens in | Tokens out | Latency s | Cost |
|---|---|---|---|---|---|---|---|
| 2026-10-06 21:3x | A, step 1 smoke | detention 01 happy-path | pass | 16960 | 1764 | 38.7 | $0.0773 |
| 2026-10-06 21:3x | A, step 1 smoke | detention 16 pastor-edits-stage | pass | 11519 | 1839 | 38.8 | $0.0621 |
| 2026-10-06 21:3x | A, step 1 smoke | hospital h01 happy-path | pass | 15163 | 2673 | 49.1 | $0.0856 |
| | | **Slot A total** | 3 of 3 pass | 43642 | 6276 | | **$0.2251** |

Earlier runs (before the credit ran out) are in `FAILURE_LOG.md` and the commit messages; the merged estimate is in `LIVE_CHECKS_OWED.md`.
