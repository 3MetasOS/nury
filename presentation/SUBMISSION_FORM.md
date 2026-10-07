# Submission form: paste-ready content

Written 2026-10-07 by hack-ninja for hack-sensei and Juan. Every fact comes from `documents/product/ALIGNMENT_AUDIT.md`. Humanizer run on the prose. Placeholders are in [BRACKETS]. Hard stop: **Wed Oct 7, 9:00 PM MDT** (solution plus the 250-word English description).

## Fields I could NOT confirm
The actual form is not in the repo. `documents/prework` (PREWORK.md, JUDGING.md) says only: preliminary entry = working solution plus a 250-word English description, "via organizer-provided GitHub and/or Drive"; video optional at this stage; finalists send a 90-second video to Google Drive by 9:00 AM MDT Oct 8. Juan will paste the real fields. I could not confirm: the exact field names and limits; whether the track is a drop-down; whether "built with", "challenges", "learned" and "next" exist as fields; whether a demo video or a deck link is asked for; whether the submission is a repo link, a Drive folder or both; team size limits; bonus-challenge checkboxes (the notes list: MCP endpoint, practitioner quote, what-didn't-work section); the 3-minute versus 90-second pitch format (the rules doc says 90 s, the newer Discord post says 3 min: verify at the venue).

## Basics
- **Project name:** Nury
- **Tagline:** An AI Crisis Response Agent
- **Track:** Agents
- **Category notes (if asked):** crisis response for churches; humanitarian, not political.
- **Team:** Juan Peláez, 3Metas, with five AI agents (hack-sensei coordinator, hack-jedi architecture and integration, hack-artisans developers, hack-ninja presentation, hack-video video).
- **Built in:** Boulder, Colorado, during the Gloo AI Hackathon, October 6 to 8, 2026. Every step is in the build log.
- **Registrant line (from the README):** Entered by Juan Peláez under 3Metas. Hackathon registration is under jkpelaez@hotmail.com (Solo Hacker ticket T000857383). *Juan: this prints a personal email and a ticket number. Confirm it before it goes in any public field.*
- **License:** MIT

## The 250-word description (two-playbooks version; use this one)
Strictest word count 246 (240 by `wc` is for the one-playbook variant; this one is 242 by `wc`).

```
Nury. An AI Crisis Response Agent.

Nury is a crisis-management engine. A crisis is a defined workflow, a folder of plain files people can add. So can rules and evaluations. Two run: detention, hospital.

It is 2 AM. A pastor's phone rings. A panicked family says a relative was detained. No lawyer, only a phone.

Nury turns that call into a response. The pastor types what the family said. Each crisis defines its own stages. Detention has five, from triage and a plain-language rights brief to a pastoral message. Family materials come out in Spanish.

After every stage, the pastor can Approve, Edit, or Stop. Nothing reaches the family except through the pastor.

Nury gives legal information only, never advice or predictions. Every rights point cites a vetted source. There is no open web. Every output carries a disclaimer and urges an attorney. Nury never endorses anyone. Nury is not a pastor, counselor, or lawyer.

Each draft is checked by our rules and by Jev, a classifier. A draft that fails is held back and regenerated, up to three tries, then Nury steps aside for the pastor. Nothing moves on without the pastor's approval.

Nury runs on Gloo's guarded endpoint. 46 scenarios, judged: 29 pass, 2 fail, 15 undecided.

The Jev decision API from TypeSafe is used as typed judges in our evaluation harness and as a run-time draft classifier; disclosed as third-party technology per the rules.

Entry by Juan Peláez, 3Metas.
```

## The 250-word description (one-playbook fallback)
Strictest word count 244. Use only if the form or the judges expect a single crisis.

```
Nury. An AI Crisis Response Agent.

Nury is a crisis-management engine. A crisis is a defined workflow, a folder of plain files people can add. So can rules and evaluations.

It is 2 AM. A pastor's phone rings. A panicked family says a relative was detained. No lawyer, only a phone.

Nury turns that call into a response. The pastor types what the family said. Each crisis defines its own stages. Detention has five, from triage and a plain-language rights brief to a pastoral message. Family materials come out in the family's language.

After every stage, the pastor can Approve, Edit, or Stop. Nothing reaches the family except through the pastor.

Nury gives legal information only, never advice or predictions. Every rights point cites a vetted source. There is no open web. Every output carries a disclaimer and urges an attorney. Nury never endorses anyone. Nury is not a pastor, counselor, or lawyer.

Each draft is checked by our rules and by Jev, a classifier. A draft that fails is held back and regenerated, up to three tries, then Nury steps aside for the pastor. Nothing moves on without the pastor's approval.

Nury runs on Gloo's guarded endpoint. 46 scenarios, judged: 29 pass, 2 fail, 15 undecided.

The Jev decision API from TypeSafe is used as typed judges in our evaluation harness and as a run-time draft classifier; disclosed as third-party technology per the rules.

Entry by Juan Peláez, 3Metas.
```

## Short descriptions
### 25 words (25)
Nury is an AI crisis response agent for churches. A pastor types what a family said; Nury drafts careful, sourced stages. The pastor approves each.

### 60 words (60)
Nury is an AI crisis response agent for churches. A pastor picks the crisis and types what the family said. Nury drafts the stages that crisis defines, such as a cited plain-language brief and a pastoral message, in the family's language. Rules and a second check review every draft. The pastor approves every stage. Nothing is sent without the pastor.

## Long fields (60 to 100 words each)
### What it does
(about 87 words)

When a family calls a pastor in crisis, the pastor picks the kind of crisis and types what the family said. Nury drafts the stages that crisis defines. For an immigration matter that means a case summary, a plain-language brief where every point cites a vetted source, a list of vetted contacts, a family checklist and a short pastoral message, in the family's language. After each stage the pastor can approve, edit or stop. Nury has no way to send anything. It gives legal information, never advice.

### How we built it
(about 83 words)

Claude Sonnet 4.6 writes each stage through Gloo AI Studio's guarded endpoint. Twenty named rules and a safety floor read every draft. Jev, a decision API from TypeSafe, checks it again with yes or no questions. A failing draft is rewritten up to three times, then the pastor takes over. Names become tokens before any model sees them. A crisis is a folder of plain files, so adding one does not change the engine. The engine is plain Python with no agent framework.

### Challenges we ran into
(about 78 words)

Our own checks found the hard problems. The tone judge never reached its target, and warm drafts sometimes made promises the church had not made. A judge scored drafts the pastor never saw. Eleven of eighteen hostile intakes stopped at triage until we rewrote the triage prompt. A made-up website passed our link check. Our first outside-review result was wrong, so we re-ran it and fixed every claim. We typed some commit dates by hand and disclosed it.

### What we learned
(about 83 words)

A judge has to read only what the pastor saw. A low score can reveal a real bug: the tone score exposed the promises. A number copied between documents drifts, so we write claims last, from one table of verified facts. The model should never write Scripture: it picks a verse from a list a person approved, and the engine inserts the exact text. Rules and a second check lower the chance of an unsafe draft. They do not replace the pastor's reading.

### What is next
(about 76 words)

The next step is to put Nury in front of real pastors, carefully, with a consent process in place. An immigration attorney and a hospital chaplain should review our vetted sources, and a native Spanish speaker should read the family copies. We want to finish calibrating the Jev check and measure how often it rejects a safe draft. Then come the two crises marked coming soon, sudden loss and house fire, each added as a folder.


## Built with
Gloo AI Studio (guarded endpoint) and Claude Sonnet 4.6 · Jev decision API from TypeSafe · YouVersion API (Scripture text) · ElevenLabs (AI-generated narration voice for the film) · Python (plain, no agent framework) · plain HTML and JavaScript (the app and the deck) · Remotion (the film).

## Disclosure (verbatim)
The Jev decision API from TypeSafe is used as typed judges in our evaluation harness and as a run-time draft classifier; disclosed as third-party technology per the rules.

## Other notes for the notes field
- The video narration is an AI-generated voice (ElevenLabs).
- With no Gloo key the app runs a recorded run of each sample intake (replay mode). The model's words are recorded; the checks, gates and privacy layer run for real. It is not a live run, and it is off when a key is present.
- The shipped build differs from the scored build (`9bc5c6d`) only in the crisis card titles and in the title text inside one context string given to the Jev check. Judge results are not human verdicts, and we quote no pass rate.
- The planning notes and a small scripted scaffold existed before the event and are kept as reference. Everything in the product code was written during the event.
- Nury is tested on made-up families only. Hand-typed commit dates are disclosed in `documents/product/COMMIT_DATES.md`.

## Links (placeholders; fill when public)
- **Repository (public at submission):** [REPO URL]
- **Deck:** [DECK URL] (`presentation/deck.html`)
- **Demo video:** [VIDEO URL] (finalists: Google Drive, by 9:00 AM MDT Oct 8)
- **About page:** [APP URL]/about (or the README if the app is not hosted: there is no hosting)
- **Build log:** [REPO URL]/blob/main/BUILD_LOG.md

## Checklist before pressing Submit
Hard stop: **9:00 PM MDT, Wed Oct 7.** Judging window 9:00 to 11:00 PM MDT. Prelim pitch: 3 minutes (rules doc says 90 s: verify at the venue). Top 25 at midnight. Finalist video by 9:00 AM MDT Oct 8 (Google Drive).
1. Repo is public, and `LICENSE` (MIT) is at the root.
2. README: the registrant line (email and ticket) confirmed or removed; the clone URL placeholder replaced.
3. No key anywhere: scan the repo and the history for `GLOO_API_KEY` and `JEV_API_KEY` values; `.env` is gitignored.
4. `cd code && ./test.sh` passes (336 product tests) and `python3 -m pytest -q evaluations/tests` passes (109).
5. The app starts with no key (replay mode) and with a key (live), on the final build.
6. Description pasted: 246 words or fewer, the disclosure line verbatim, "Entry by Juan Peláez, 3Metas."
7. The deck opens from the link, at 1280 and on a phone; the Close shows "In memory of Tía Nury" and "08-2026" (Juan approved these two lines in writing: confirm).
8. Nobody has written "pass rate", "package" or a claim that a pastor, attorney or family used Nury.
9. `COMMIT_DATES.md` is in the repo and linked from the notes; the README says every step is in the build log.
10. The form's real fields are matched to this file; anything this file does not cover is answered from the same facts (ALIGNMENT_AUDIT.md).
11. Submit before 8:30 PM to leave a margin. Keep a screenshot of the confirmation.
12. Then: deck and script in Juan's hands by 8:30 PM; pitch window 9:00 to 11:00 PM.
