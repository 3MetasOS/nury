# Nury: 3-minute pitch script

Speaker: Juan Pelaez (3Metas). Target 3:00 spoken at a calm pace (about 140 words a minute, about 400 words).
Tags: `[90s]` lines stay in the 90-second cut. Untagged lines are 3-minute only.
Family and intake: see `SHARED_DEMO.md`. Slide numbers match `deck.html`.
`[NUMBER]` = placeholder. Fill from hack-artisans' scorecard only. If no real number exists, say the fallback line.

## 0:00 to 0:25  Slide 1 and 2: the user  (Concept/Product)
[90s] It is 2 AM. A solo pastor's phone rings.
[90s] A family. A husband was detained last evening. The pastor has no staff and no lawyer on the line.
[90s] The pastor wants to help. But they are not a lawyer. They have minutes, and a phone.
This is the job of a solo pastor, and nobody has built the tool for it. Meet Nury.
[90s] Nury. The crisis-response agent for solo pastors.

## 0:25 to 1:35  Slide 3: live demo  (Product, Use of AI)
Play the 90-second video, or run the app live on the locked intake. Speak over it or cue it.
[90s] The pastor types what the family said. Nury runs five stages: triage, rights brief, attorney resources, a family checklist, and a pastoral message.
[90s] After every stage, the pastor decides: Approve, Edit, or Stop. Later stages use the pastor's edits.
[90s] Watch this. A draft crosses from information into advice. Nury rejects it and regenerates. The pastor never sees it.
[90s] The rights brief comes out in Spanish, built only from a vetted source, every point cited.
[90s] At the end, the pastor has a package. Copy, not Send. Nury never sends. The pastor does.

## 1:35 to 2:10  Slide 4 and 5: why it works  (Innovation, Use of AI)
Two ideas make this safe enough for a crisis.
First, the approval gate. The agent drafts. The pastor decides. Nothing reaches the family except through the pastor's hands.
Second, the self-correction loop. Every draft is checked. Unsafe drafts are rejected and regenerated, up to three tries, then handed to the pastor. The pastor never sees the unsafe one.
Nury runs on Gloo's guarded Responses endpoint. It gives legal information only, from a vetted source file. No open web. It is not a pastor, a counselor, or a lawyer, and it says so.

## 2:10 to 2:40  Slide 6: proof  (Impact and Execution)
We did not trust it. We tested it.
[ONLY IF TRUE] Twenty hand-built scenarios, scored by typed judges. [NUMBER: pass rate], [NUMBER: drafts rejected and regenerated], [NUMBER: cost per run], [NUMBER: latency per run].
Fallback if no scorecard: "We built twenty scenarios and scored each stage. The scorecard is in our build document."
The harness uses the Jev decision API, my prior project, as typed judges. Disclosed as prior technology per the rules.

## 2:40 to 3:00  Slide 7 and 8: team and close  (Teamwork/Presentation)
Built by Juan Pelaez at 3Metas, with a small team of AI agents that coordinate over a messaging protocol. Every step is in the commit log.
[90s] Nury is named for my late tía Nury, a woman who was always ready to help at her church.
[90s] The next call will come at 2 AM. Nury makes sure the pastor is ready.
[90s] Nury. The crisis-response agent for solo pastors.

## 90-second cut: how to run it
Say only the `[90s]` lines. Run the 90-second video over the demo lines. Drop slides 4 to 6.
Judges' rules doc says 90 s, Discord says 3 min. Verify at the venue. Both versions are ready.

## Rules for the speaker
- Say "legal information", never "legal advice".
- Never say Nury "helps the family directly". It helps the pastor, who helps the family.
- Do not name an agency or a party. Humanitarian, never political.
- Do not claim a pastor tested it. We have not validated with one. Say so if asked.
