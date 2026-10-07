# Nury

Nury — An AI Crisis Response Agent. When an immigrant family faces a detention, raid, or sudden legal emergency, the pastor types what the family told them. Nury works through five stages (triage, rights brief, attorney resources, family checklist, pastoral message) and pauses for the pastor's approval after each one. Unsafe drafts are rejected and regenerated before the pastor sees them. Legal information comes only from vetted sources, and nothing reaches the family except through the pastor. Nury is not a pastor and never claims to be one.

Entered by Juan Pelaez under 3Metas. Hackathon registration is under jkpelaez@hotmail.com (Solo Hacker ticket T000857383).

License: MIT.

## Privacy

Nury removes direct identifiers before anything reaches a language model. Names, phone numbers, emails, street addresses, dates of birth and ID numbers become tokens inside Nury before a request goes to the model; the model sees tokens, not names, and the real values are put back in the answers the pastor sees. The pastor confirms which names to protect. Limits: details such as a workplace or a rare job can still hint at who someone is, and a name the pastor did not protect is not removed. Cases are saved in Nury; nothing is sent to the family.

## Credits

The video narration is an AI-generated voice (ElevenLabs).

Photo, illustration and font credits: `branding/IMAGES.md`.

## Status of hosting

Nury is a web app. Today one shared pool of cases and one shared church network are visible to everyone who can reach the app. There is no sign-in, no accounts and no encryption at rest yet. A hosted version for many churches needs all three, plus separation between churches. See `documents/FEATURES.md`.
