# Consent and confidentiality note (draft for Juan to approve)

Status: **DRAFT. Not in the app.** hack-sensei assigned the build to hack-jedi and hack-artisans after Juan approves the words. Written by hack-ninja, 2026-10-07. Source: `documents/STANDARDS_ALIGNMENT.md` (informed by NASW's consent and confidentiality wording, and by the pastoral confidentiality norm; this note does not meet either one).

## Recommended text (3 sentences)
> Nury saves cases so you can come back to them. There is no sign-in yet: anyone who can open this app can open the saved cases. Share only what the family has agreed to share.

## Fuller option (4 sentences, adds what is saved and that nothing is sent)
> Nury saves approved cases, with the names you typed, so you can come back to them. There is no sign-in yet: anyone who can open this app can open the saved cases. Nury sends nothing to the family. Share only what the family has agreed to share.

## Why each sentence is true today
| Sentence | Evidence |
|---|---|
| "Nury saves cases so you can come back to them." | `FEATURES.md` section 1: "Save as a case" and "Open cases and read them" (BUILT, live verified). Cases are saved by the app. |
| "...with the names you typed" | The saved case holds approved text and the pastor's original intake (`intake.md`), so it contains the real names. The token map is also saved with the case. (`FEATURES.md` section 3, "Saved by the app".) |
| "There is no sign-in yet: anyone who can open this app can open the saved cases." | `FEATURES.md` section 9: "Accounts and sign-in: No login. Anyone who can reach the app can open every case and the church network." `code/app/server.py` has no authentication. |
| "Nury sends nothing to the family." | `FEATURES.md` section 2, "No send path"; `tests/test_core.py` (NoSendPath). |
| "Share only what the family has agreed to share." | An instruction to the pastor, not a claim about Nury. It is plain good practice (NASW: information is released "only with written permission of the client"), but it is Juan's call whether to say it in these words. |

## What the note does not say, on purpose
No "confidential", "private", "secure", "encrypted", "protected" or "safe". None of those is true yet: there is no sign-in, no separation between churches, and no encryption at rest (`FEATURES.md` section 9). No word about where the files are kept. No claim that the AI model never sees a name: it sees tokens, but that belongs in the privacy section, not in a consent note. No statement of the pastor's legal duties: that would be legal advice, and Nury gives legal information only.

## When to change it
When sign-in exists, rewrite the second sentence. Until then, the note must keep saying there is none. If the note ever says more than is true, it is worse than no note.

## Where it goes (for the builders)
On the intake screen, above the Start button, and at the top of a saved case. Short, plain, one block, not a checkbox. English for the pastor. Spanish is for the family's drafts and does not apply here.
