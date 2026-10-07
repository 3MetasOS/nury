# Build comparison: c317050 against the final build

Pass / fail / awaiting review are judge results, not human verdicts. Tone range is the Jev warm, plain and human score (target 4, fail below 3). Reading level is advisory and was first recorded in the final build. A column names the core commit it ran on.

| Set | Build | Core | Pass / fail / awaiting | Escalations | Tone range | Cost | Mean time per run | Reading level |
|---|---|---|---|---|---|---|---|---|
| Detention (20) | before | `c317050` | 12 / 2 / 6 | 2 | 2.70 to 3.17 | $1.44 | 41 s | not recorded |
| Detention (20) | final | `8a28a18` | 12 / 6 / 2 | 2 | 2.60 to 2.85 | $1.28 | 33 s | ES INFLESZ 72.8 (65), EN grade 5.4 (4) |
| Hospital (8) | before | `b47cc92` | 5 / 2 / 1 | 0 | 2.70 to 2.93 | $0.69 | 50 s | not recorded |
| Hospital (8) | final | `8a28a18` | 5 / 1 / 2 | 0 | 2.87 to 3.07 | $0.70 | 49 s | ES INFLESZ 71.3 (28), EN grade 5.2 (4) |
| Attacker (18) | before | `b47cc92` | 6 / 11 / 1 | 11 | n/a | $1.20 | 40 s | not recorded |
| Attacker (18) | final | `8a28a18` | 11 / 2 / 5 | 1 | n/a | $1.38 | 38 s | ES INFLESZ 70.1 (68) |
| Network (3) | before | `?` | 2 / 0 / 1 | 0 | n/a | $0.27 | 53 s | not recorded |
| Network (3) | final | `8a28a18` | 1 / 0 / 2 | 0 | n/a | $0.33 | 67 s | ES INFLESZ 71.1 (12) |
| Case-file (5) | before | n/a | 5 / 0 / 0 | n/a | n/a | $0.58 | n/a | n/a |
| Case-file (5) | final | n/a | 5 / 0 / 0 | n/a | n/a | $0.59 | n/a | n/a |

`b47cc92` is c317050 plus a change to rule descriptions only (disclosed in the scorecard note); the hospital and attacker rows marked before ran on it. The network and case-file rows marked before were last run on an earlier build than c317050 (see the Core column); only detention, hospital and attacker were re-run on c317050.

