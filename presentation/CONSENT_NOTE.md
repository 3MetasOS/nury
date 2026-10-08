# Consent and confidentiality note (draft for Juan to approve)

Status: **APPROVED by hack-sensei (2026-10-07): the fuller four-sentence version is the default.** Juan can edit the words later; he should be told it is the default. hack-sensei sends it to hack-artisans for the intake screen (above Begin), the top of a saved case and the About sheet. Version B (below) adds one sentence that **Juan approved on 2026-10-07**; it is shown only when feedback capture is on. The four-sentence text is in the app (`data-consent` in `code/app/static/index.html`). Written by hack-ninja, 2026-10-07. Source: `documents/STANDARDS_ALIGNMENT.md` (informed by NASW's consent and confidentiality wording, and by the pastoral confidentiality norm; this note does not meet either one).

## Shorter text (3 sentences, not the default)
> Nury saves cases so you can come back to them. There is no sign-in yet: anyone who can open this app can open the saved cases. Share only what the family has agreed to share.

## Version A: DEFAULT text, feedback capture OFF (today). 4 sentences, approved: says what is saved and that nothing is sent
> Nury saves approved cases, with the names you typed, so you can come back to them. There is no sign-in yet: anyone who can open this app can open the saved cases. Nury sends nothing to the family. Share only what the family has agreed to share.

## Version B: capture ON (only after phase 2 is built and verified). The four sentences plus one
> Nury saves approved cases, with the names you typed, so you can come back to them. There is no sign-in yet: anyone who can open this app can open the saved cases. Nury sends nothing to the family. Share only what the family has agreed to share. Nury also records what you change, without names, to improve its drafts; a person reviews every change before it is used.

**Approval.** Juan approved the new sentence on 2026-10-07 (relayed by hack-sensei, message of 01:04 MDT). The sentence is: "Nury also records what you change, without names, to improve its drafts; a person reviews every change before it is used."

**When it is shown.** Only when feedback capture is on. While capture is off, the app shows version A and nothing about recording. The app must pick the text from the switch, so the sentence can never appear when nothing is recorded, and can never be missing when something is.

**Do not claim it yet.** Nothing about recording changes goes in the deck, the film, the description or the Q and A until hack-sensei confirms in writing that phase 2 is built and verified. Version B is held, like the other gated lines.

## Why the new sentence would be true: what must exist first
`feedback.py` has not landed. Until it does, none of these rows is evidenced, and version B stays off.

| Clause | What must be true | Evidence needed (not yet there) |
|---|---|---|
| "Nury also records what you change" | When a pastor edits a draft at a gate, the edit is stored. A pastor who approves unchanged records nothing. | `feedback.py` (when it lands); a test that an edit is stored and an unchanged approval is not |
| "without names" | The stored change holds no name, phone, email, address, date or ID. It passes through the same pseudonymizer as the Gloo path, and a leak test with canary names finds none. | A leak test on the stored feedback, like `tests/test_privacy.py`; the same method as TECH_CLAIMS row 16 and 53 |
| "to improve its drafts" | The recorded changes are used for that purpose and no other. Say what "improve" means in the code, and do not promise more than it does. | The design note for phase 2; a line in `FEATURES.md` |
| "a person reviews every change before it is used" | No recorded change reaches a prompt, a rule, a skill or a check until a named person approves it. | A review step in code (not only a policy), and a test that an unreviewed change is never used. Today there is no review queue (`HOW_IT_WAS_BUILT.md`, section 9). |

If any row fails, the sentence is wrong. Change the sentence or leave capture off. Do not ship version B on hope.

## Words to watch in version B
It still avoids "confidential", "private", "secure", "encrypted", "protected" and "safe". "Without names" is a narrow claim: it says the recorded change has no direct identifiers. It does not say the context cannot hint at who someone is. Nury's privacy limit still applies (the HOW_IT_WAS_BUILT section on privacy says it). Do not shorten "without names" to "anonymous".

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
On the intake screen above the Begin button, at the top of a saved case, and on the About sheet. Short, plain, one block, not a checkbox. English for the pastor. Spanish is for the family's drafts and does not apply here.
