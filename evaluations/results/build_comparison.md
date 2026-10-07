# Build comparison: c317050, 8a28a18, 07f020c and the final build 9bc5c6d

Pass / fail / awaiting review are judge results, not human verdicts. Tone range is the Jev warm, plain and human score (target 4, fail below 3). Reading level is advisory and was first recorded in the final build. A column names the core commit it ran on.

| Set | Build | Core | Pass / fail / awaiting | Escalations | Tone range | Cost | Mean time per run | Reading level |
|---|---|---|---|---|---|---|---|---|
| Detention (20) | c317050 | `c317050` | 12 / 2 / 6 | 2 | 2.70 to 3.17 | $1.44 | 41 s | not recorded |
| Detention (20) | 8a28a18 | `8a28a18` | 12 / 6 / 2 | 2 | 2.60 to 2.85 | $1.28 | 33 s | ES INFLESZ 72.8 (65), EN grade 5.4 (4) |
| Detention (20) | 07f020c | `6ea102d` | 12 / 1 / 7 | 2 | 3.06 to 3.32 | $1.25 | 32 s | ES INFLESZ 76.4 (65), EN grade 5.2 (4) |
| Detention (20) | final 9bc5c6d | `9bc5c6d` | 11 / 1 / 8 | 2 | 3.04 to 3.32 | $1.28 | 34 s | ES INFLESZ 76.6 (65), EN grade 5.5 (4) |
| Hospital (8) | c317050 | `b47cc92` | 5 / 2 / 1 | 0 | 2.70 to 2.93 | $0.69 | 50 s | not recorded |
| Hospital (8) | 8a28a18 | `8a28a18` | 5 / 1 / 2 | 0 | 2.87 to 3.07 | $0.70 | 49 s | ES INFLESZ 71.3 (28), EN grade 5.2 (4) |
| Hospital (8) | 07f020c | `6ea102d` | 4 / 1 / 3 | 1 | 3.33 to 3.39 | $0.64 | 44 s | ES INFLESZ 70.6 (24), EN grade 6.4 (4) |
| Hospital (8) | final 9bc5c6d | `9bc5c6d` | 5 / 0 / 3 | 0 | 3.14 to 3.14 | $0.71 | 50 s | ES INFLESZ 72.2 (28), EN grade 5.2 (4) |
| Attacker (18) | c317050 | `b47cc92` | 6 / 11 / 1 | 11 | n/a | $1.20 | 40 s | not recorded |
| Attacker (18) | 8a28a18 | `8a28a18` | 11 / 2 / 5 | 1 | n/a | $1.38 | 38 s | ES INFLESZ 70.1 (68) |
| Attacker (18) | 07f020c | `6ea102d` | 12 / 3 / 3 | 1 | n/a | $1.42 | 38 s | ES INFLESZ 70.7 (68) |
| Attacker (18) | final 9bc5c6d | `9bc5c6d` | 13 / 1 / 4 | 0 | n/a | $1.51 | 42 s | ES INFLESZ 71.1 (72) |
| Network (3) | c317050 | `?` | 2 / 0 / 1 | 0 | n/a | $0.27 | 53 s | not recorded |
| Network (3) | 8a28a18 | `8a28a18` | 1 / 0 / 2 | 0 | n/a | $0.33 | 67 s | ES INFLESZ 71.1 (12) |
| Network (3) | 07f020c | `6ea102d` | 1 / 0 / 2 | 0 | n/a | $0.28 | 54 s | ES INFLESZ 74.0 (12) |
| Network (3) | final 9bc5c6d | `9bc5c6d` | 1 / 0 / 2 | 0 | n/a | $0.27 | 52 s | ES INFLESZ 70.5 (12) |
| Case-file (5) | c317050 | n/a | 5 / 0 / 0 | n/a | n/a | $0.58 | n/a | n/a |
| Case-file (5) | 8a28a18 | n/a | 5 / 0 / 0 | n/a | n/a | $0.59 | n/a | n/a |
| Case-file (5) | 07f020c | n/a | 5 / 0 / 0 | n/a | n/a | $0.59 | n/a | n/a |
| Case-file (5) | final 9bc5c6d | n/a | 5 / 0 / 0 | n/a | n/a | $0.59 | n/a | n/a |

`b47cc92` is c317050 plus a change to rule descriptions only (disclosed in the scorecard note); the hospital and attacker rows marked before ran on it. The network and case-file rows marked before were last run on an earlier build than c317050 (see the Core column); only detention, hospital and attacker were re-run on c317050.

