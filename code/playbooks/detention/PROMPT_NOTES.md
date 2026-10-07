# Prompt notes: v1 vs shipped (detention playbook)

Judges ask what changed and why. Verbatim shipped prompts are in `prompts/*.txt`. The shared boundary rules are `SYSTEM_BOUNDARY` in `nury/guardrails.py`, prepended to every stage prompt.

## v1
The v1 prompts came from the prework reference (`documents/prework/crisis_agent/stages.py`). The first live runs of the new core used the same wording with the engine's checks added.

## What was wrong with v1 (seen in live runs, Oct 6)
| # | Problem | Seen in | Fix in shipped version |
|---|---|---|---|
| 1 | Output carried a header such as "Preparada por el pastor". It read as if a pastor wrote it. | attorney, checklist | Rule 9 in the boundary: no title, byline, signature, or line saying who wrote it. Banned-pattern check for "prepared / written / drafted by the pastor" (EN and ES). The engine adds the label "Borrador de Nury para revisión del pastor" to what the pastor sees. |
| 2 | English scripture quote inside a Spanish message, plus a typo ("prometeries"). | pastoral | Rule 8: one language, translate every quote, no scripture or quotes that are not in the sources. New `language` check rejects English words mixed into Spanish. |
| 3 | Rights brief had no fixed citation format. The model added a pastor note and "---" separators, and one bullet had no source. | rights | Prompt says "end every bullet with its source name in parentheses", "output only the bullets and that sentence". The `cited_bullets` check rejects any bullet without a vetted source name. |
| 4 | Triage had free-form output. Missing facts were not always 3. | triage | Fixed labels and "exactly 3 numbered facts". `required_labels` and `numbered_after` checks. |
| 5 | Disclaimer never said Nury is an AI assistant. | all | Disclaimer rewritten (EN and ES): "Nury is an AI assistant, not a lawyer, pastor, counselor, or therapist." The loader refuses a playbook disclaimer that drops this wording. |
| 6 | Links and phone numbers were only checked on two stages. | all | Floor check on every stage: a link or phone number must appear in the vetted sources or in approved earlier text. |
| 7 | An edited rights brief did not reach stages 3-5. | attorney, checklist, pastoral | Stage `deps` now include `rights`. |
| 8 | Checks too strict: translated attorney names and "---" lines caused 3 false escalations. | attorney, rights | Attorney check matches vetted links, not names. Bullet check ignores separators. |

## Model behavior worth knowing
The model refused to write legal advice when asked to. We could not make it fail on demand. The demo and the eval therefore use fault injection (a forced unsafe suffix on the draft), which is deterministic and costs no extra Gloo call.
