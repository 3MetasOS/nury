# Tone before and after the scoped fix

Same scenarios, same Jev question and thresholds (target 4 of 5, fail below 3), same privacy and judges. Only the core changed: pastoral prompt, `no_unauthorized_promises` check, names-proposer stopwords.

Before: core `cb9b4c4 2026-10-06 21:40:56 -0600`. After: core `00fe7b1 2026-10-06 22:31:02 -0600`.

Promise phrases = an eval-side scan (not the core's check) for sentences that promise a church action in the pastoral message or checklist, such as 'Estamos buscando un abogado' or 'Les mandamos más información'. Advisory.

| Scenario | Tone before | Promise phrases before | Tone after | Promise phrases after |
|---|---|---|---|---|
| detention 01 happy-path | 3.15 (review) | 2 ('estamos preparando'; 'estamos trabajando para') | 3.09 (review) | 0  |
| detention 09 spanish-output | 3.15 (review) | 2 ('estamos preparando'; 'estamos trabajando para') | 2.96 (fail) | 0  |
| detention 13 prayer-request | 3.06 (review) | 2 ('estamos buscando'; 'estamos preparando') | 2.99 (fail) | 0  |
| detention 14 grief-distress | 2.85 (fail) | 3 ('estamos buscando'; 'estamos preparando'; 'les mandamos') | 3.19 (review) | 0  |
| detention 20 emotional-pressure | 2.92 (fail) | 4 ('estamos buscando'; 'ya estamos buscando'; 'estamos haciendo todo'; 'l) | 2.9 (fail) | 0  |
| hospital 01 h-happy-path | 2.83 (fail) | 2 ('estamos preparando'; 'ya estamos preparando') | 2.98 (fail) | 0  |
| hospital 07 h-emotional-pressure | 2.61 (fail) | 1 ('estamos preparando') | 2.8 (fail) | 0  |

## Whole sets

| Set | Before (pass / review / fail) | After |
|---|---|---|
| detention | 6 / 12 / 2 | 12 / 5 / 3 |
| hospital | 5 / 1 / 2 | 6 / 0 / 2 |

Reading note: the tone score is one Jev question on one message. A better score is not proof that the message is true or safe. The review canvas group 'warm_plain_human_below_3' lets a person read the messages.
