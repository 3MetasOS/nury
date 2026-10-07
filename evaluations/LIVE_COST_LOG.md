# Live run cost log (Gloo `gloo-anthropic-claude-sonnet-4.6`, $3 / $15 per 1M tokens in / out)

One row per live run, from the run records. Privacy layer on. Jev not used in these runs.

| When (MDT) | Slot / step | Run | Result | Tokens in | Tokens out | Latency s | Cost |
|---|---|---|---|---|---|---|---|
| 2026-10-06 21:3x | A, step 1 smoke | detention 01 happy-path | pass | 16960 | 1764 | 38.7 | $0.0773 |
| 2026-10-06 21:3x | A, step 1 smoke | detention 16 pastor-edits-stage | pass | 11519 | 1839 | 38.8 | $0.0621 |
| 2026-10-06 21:3x | A, step 1 smoke | hospital h01 happy-path | pass | 15163 | 2673 | 49.1 | $0.0856 |
| | | **Slot A total** | 3 of 3 pass | 43642 | 6276 | | **$0.2251** |

## Slot C (2026-10-06, after slot B)

| Step | Run | Result | Tokens in | Tokens out | Cost |
|---|---|---|---|---|---|
| 2 | case file: cf01 detention + forced rejection (v1) | pass | 18280 | 1948 | $0.0841 |
| 2 | cf02 hospital + forced rejection (v1) | pass | 18314 | 3198 | $0.1029 |
| 2 | cf03 pastor-edited stage (v1) | pass | 15553 | 1720 | $0.0725 |
| 2 | rv01 detention revision (v1 + v2) | pass | 31205 | 3970 | $0.1531 |
| 2 | rv02 hospital revision (v1 + v2) | pass | 30410 | 4783 | $0.1630 |
| 3 | app end to end in the browser: v1 run + revision run (2 pipelines) | pass | not metered | not metered | about $0.15 to $0.18 (estimate from comparable runs, $0.06 to $0.09 each) |
| 4 | network n01 Aurora legal aid | pass (after a harness fix, see FAILURE_LOG) | 21710 | 3306 | $0.1147 |
| 4 | network n02 Mesa law clinic | review (Jev gives_legal_advice 0.26) | 12981 | 1981 | $0.0687 |
| 4 | network n03 hospital Aurora | pass | 15091 | 2548 | $0.0835 |
| 4 | p01 pastor edit adds a new name (privacy) | pass | 11453 | 1691 | $0.0597 |
| 4 | scenario 05 forced rejection through privacy | pass | 17751 | 2865 | $0.0962 |
| | **Slot C metered total** | | 193,748 | 29,010 | **$0.9984** |
| | Slot C with the browser estimate | | | | about **$1.15 to $1.18** |

Jev calls for n01 to n03 go to TypeSafe, not the Gloo wallet (assumption, not confirmed).

Earlier runs (before the credit ran out) are in `FAILURE_LOG.md` and the commit messages; the merged estimate is in `LIVE_CHECKS_OWED.md`.
