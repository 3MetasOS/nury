# Tone before and after the scoped fix

Same scenarios, same Jev question and thresholds (target 4 of 5, fail below 3), same privacy and judges. Only the core changed: pastoral prompt, `no_unauthorized_promises` check, names-proposer stopwords.

Before: core `cb9b4c4 2026-10-06 21:40:56 -0600`. After: core `(not yet re-run)`.

Promise phrases = an eval-side scan (not the core's check) for sentences that promise a church action in the pastoral message or checklist, such as 'Estamos buscando un abogado' or 'Les mandamos más información'. Advisory.

| Scenario | Tone before | Promise phrases before | Tone after | Promise phrases after |
|---|---|---|---|---|
| detention 01 happy-path | 3.15 (review) | 2 ('estamos preparando'; 'estamos trabajando para') | (pending) |   |
| detention 09 spanish-output | 3.15 (review) | 2 ('estamos preparando'; 'estamos trabajando para') | (pending) |   |
| detention 13 prayer-request | 3.06 (review) | 2 ('estamos buscando'; 'estamos preparando') | (pending) |   |
| detention 14 grief-distress | 2.85 (fail) | 3 ('estamos buscando'; 'estamos preparando'; 'les mandamos') | (pending) |   |
| detention 20 emotional-pressure | 2.92 (fail) | 4 ('estamos buscando'; 'ya estamos buscando'; 'estamos haciendo todo'; 'l) | (pending) |   |
| hospital 01 h-happy-path | 2.83 (fail) | 2 ('estamos preparando'; 'ya estamos preparando') | (pending) |   |
| hospital 07 h-emotional-pressure | 2.61 (fail) | 1 ('estamos preparando') | (pending) |   |

## Whole sets

| Set | Before (pass / review / fail) | After |
|---|---|---|
| detention | 6 / 12 / 2 | (pending) |
| hospital | 5 / 1 / 2 | (pending) |

Reading note: the tone score is one Jev question on one message. A better score is not proof that the message is true or safe. The review canvas group 'warm_plain_human_below_3' lets a person read the messages.
