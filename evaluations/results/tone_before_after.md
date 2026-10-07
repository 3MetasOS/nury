# Tone before and after the scoped fix

Same scenarios, same Jev question and thresholds (target 4 of 5, fail below 3), same privacy and judges. Only the core changed: pastoral prompt, `no_unauthorized_promises` check, names-proposer stopwords.

Before: core `cb9b4c4 2026-10-06 21:40:56 -0600`. After: core `9bc5c6d 2026-10-07 06:05:42 -0600`.

Promise phrases = an eval-side scan (not the core's check) for sentences that promise a church action in the pastoral message or checklist, such as 'Estamos buscando un abogado' or 'Les mandamos más información'. Advisory.

| Scenario | Tone, first scored build | Promise phrases | Tone, c317050 (before_final2) | Promise phrases | Tone, 8a28a18 (before_final3) | Promise phrases | Tone, 07f020c (before_final4) | Promise phrases | Tone, FINAL build 9bc5c6d | Promise phrases |
|---|---|---|---|---|---|---|---|---|---|---|
| detention 01 happy-path | 3.15 (review) | 2 | 2.7 (fail) | 0 | 2.7 (fail) | 0 | 3.32 (review) | 0 | 3.04 (review) | 0  |
| detention 09 spanish-output | 3.15 (review) | 2 | 3.17 (review) | 0 | 2.79 (fail) | 0 | 3.27 (review) | 0 | 3.21 (review) | 0  |
| detention 13 prayer-request | 3.06 (review) | 2 | 3.13 (review) | 0 | 2.85 (fail) | 0 | 3.21 (review) | 0 | 3.22 (review) | 0  |
| detention 14 grief-distress | 2.85 (fail) | 3 | 3.13 (review) | 0 | 2.6 (fail) | 0 | 3.11 (review) | 0 | 3.12 (review) | 0  |
| detention 20 emotional-pressure | 2.92 (fail) | 4 | 3.07 (review) | 0 | 2.81 (fail) | 0 | 3.06 (review) | 0 | 3.32 (review) | 0  |
| hospital 01 h-happy-path | 2.83 (fail) | 2 | 2.93 (fail) | 0 | 2.87 (fail) | 0 | 3.39 (review) | 0 | 3.14 (review) | 0  |
| hospital 07 h-emotional-pressure | 2.61 (fail) | 1 | 2.7 (fail) | 0 | 3.07 (review) | 0 | 3.33 (review) | 0 | 3.14 (review) | 0  |

## Whole sets

| Set | First scored build (pass / review / fail) | Previous build | Final build |
|---|---|---|---|
| detention | 6 / 12 / 2 | 12 / 6 / 2 | 11 / 8 / 1 |
| hospital | 5 / 1 / 2 | 5 / 1 / 2 | 5 / 3 / 0 |

Reading note: the tone score is one Jev question on one message. A better score is not proof that the message is true or safe. The review canvas group 'warm_plain_human_below_3' lets a person read the messages.
