# Nury: 3-minute pitch script (deck v2, with the technical story)

Speaker: Juan Pelaez (3Metas). Target about 2:50 with the memorial, 3:00 at most, at a calm pace. Slide numbers match `deck.html` (default view, gated items hidden). Press `n` for notes, `g` to reveal gated items for review, `b` to jump to backup.
Tags: `[90s]` lines and slides stay in the 90-second cut. The video plays inside the demo slide (approved).
`[NUMBER]` = real scorecard number only. If none by Oct 7 16:00 MDT, use the fallback line.
Family and intake: `SHARED_DEMO.md`. Do not say "ICE" or name any agency.
Technical claims and the five hard questions: `TECH_STORY.md`. Numbers come from `documents/TECH_CLAIMS.md`, VERIFIED rows only.

## Timing table (3-minute version; the arc is night, lantern, light, dawn)
| Slide | Act | Content | Time | Length |
|---|---|---|---|---|
| 1 | Night | 2:07 AM, the call (dark slide) | 0:00 to 0:14 | 14 s |
| 2 | Lantern | This is Nury (the slide turns to paper) | 0:14 to 0:20 | 6 s |
| 3 | Lantern | The name entry | 0:20 to 0:28 | 8 s |
| 4 | Light | Concept and product | 0:28 to 0:43 | 15 s |
| 5 | Light | The demo: the call, the work, the rejected draft (cut to about 34 s) | 0:43 to 1:17 | 34 s |
| 6 | Light | How it is built | 1:17 to 1:37 | 20 s |
| 7 | Light | Innovation | 1:37 to 1:52 | 15 s |
| 8 | Light | Use of AI | 1:52 to 2:10 | 18 s |
| 9 | Light | Impact and execution | 2:10 to 2:22 | 12 s |
| 10 | Light | Teamwork, and what is next | 2:22 to 2:30 | 8 s |
| 11 | Dawn | Close | 2:30 to 2:34 | 4 s |
| 12 | Dawn | Memorial (option 2, about 16 s; gated until Juan approves) | 2:34 to 2:50 | 16 s |
Total 2:50 with the memorial, 2:34 without. With memorial option 3 (8 s) the total is 2:42.

## 0:00 to 0:14  Slide 1 (night): the call  [90s]
The slide is dark. Play the phone buzz if the room allows. [90s] It is 2:07 in the morning. A pastor's phone rings. A family. A husband was detained last evening. The pastor has no lawyer on the line, a phone, and a few minutes.

## 0:14 to 0:20  Slide 2 (lantern): This is Nury  [90s]
The slide turns from night to paper and the lantern lights. [90s] This is Nury.

## 0:20 to 0:28  Slide 3 (lantern): the name entry  [90s]
The entry builds itself: Nury, /NOO-ree/, proper noun. [90s] "A given name from Arabic nur, light. An AI crisis response agent." Then "see also: lantern". Do not say her name here; it appears once, in the memorial.

## 0:28 to 0:43  Slide 4 (light): concept and product
Five stages, one gate after each. [ONLY AFTER SENSEI CONFIRMS IN WRITING THAT THE VERSE BANK IS BUILT: The pastoral message carries a Bible verse, quoted from a verified list. The AI never writes Scripture.] The app opens on a crisis selector. Each card is a playbook. Detention is the one you saw. Two more cards say coming soon. Nothing is sent without the pastor.
A second playbook, hospital emergency, runs on the same engine (open: hack-sensei, in writing, 2026-10-07). [PLACEHOLDER: hospital scenario count and pass rate]
Say nothing more about the coming-soon cards.

## 0:43 to 1:17  Slide 5 (light): the demo  [90s]
Play the cut of the demo (the guardrail strip and the approval gate), or run the app on the locked intake. The full 90-second film does not fit this slot. The selector screenshot goes in the slot.
[90s] The pastor types what the family said. Nury runs five stages. After every stage the pastor decides: Approve, Edit, or Stop.
[90s] Watch the strip: a draft is rejected, regenerated, passed. The pastor never saw the unsafe one.
[90s] At the end, Copy, not Send. Nury is not a pastor. It never sends. The pastor does.

## 1:17 to 1:37  Slide 6 (light): how it is built  [90s]
Trace the line once. [90s] The pastor types. A privacy layer in Nury swaps names for tokens. Only tokens go to Gloo AI Studio's guarded endpoint. The reply comes back, the names are put back inside Nury, and named checks, then Jev, reject unsafe drafts, up to three tries. The pastor decides. The model sees tokens, not names. The leak test ran 90 checks per playbook and found no names.
Under the diagram: twenty named checks plus the safety floor, five Gloo calls, no send path. Point at the bottom strip: "That is how we test it before release. Four layers."

## 1:37 to 1:52  Slide 7 (light): innovation
Adding a crisis is adding a playbook folder. The engine does not change. Detention and hospital emergency both run on it, and a test builds a new crisis from scratch.
Unsafe drafts never reach the pastor: rejected, regenerated, up to three tries, then escalated.
[ONLY AFTER SENSEI CONFIRMS IN WRITING] Playbooks share small skills, like voice and grounding.

## 1:52 to 2:10  Slide 8 (light): use of AI, and why two judges
[47 words, about 18 s] The writer is Claude, through Gloo AI Studio. Our rules check every draft, and Jev, from TypeSafe, classifies it with a probability before the pastor sees it. Before release, a red team of three models from other makers hunts for what we missed, and a person decides.
If asked for more, go to the backup slide "Why two judges" (press `b`): who each model is (the red team is OpenAI GPT-5.4, Google Gemini 3.1 Pro and Meta Llama 4 Maverick; none is Claude, on purpose), the numbers (unsafe 0.89 to 0.98, safe 0.02 to 0.24), the stability check (TC 37: five stored runs, within 0.03 an hour later; one verdict near a threshold flipped, 0.21 to 0.18), and the honest limits. In validation all three red-team reviewers caught 8 of 8 injected problems and also flagged safe text, so it advises. Final panel numbers: [PLACEHOLDER until hack-artisans finishes]. Jev is from TypeSafe, not ours: say "used at run time and at test time, and disclosed as third-party technology". If asked, the test-time Jev judges are not independent of the run-time gate.

## 2:10 to 2:22  Slide 9 (light): impact and execution
[ONLY IF TRUE] Hand-built scenarios, scored by typed judges. [NUMBER: pass rate], [NUMBER: drafts rejected and regenerated], [NUMBER: cost per run], [NUMBER: latency per run].
Fallback if no scorecard: "We built twenty scenarios and scored each stage. The scorecard is in our build document."
No number from any interim run. Say one failure, plainly: a checklist named a detainee locator that was not in our vetted sources. We fixed the prompt and the check.
The Jev decision API from TypeSafe is used as typed judges in our evaluation harness and as a run-time draft classifier. Disclosed as third-party technology per the rules.

## 2:22 to 2:30  Slide 10 (light): teamwork, and what is next
Built by Juan Pelaez at 3Metas with a small team of AI agents that coordinate over a messaging protocol. Next is the human team: pastors to pilot with, and an attorney to review the sources. Not done yet.

## 2:30 to 2:34  Slide 11 (dawn): close  [90s]
[90s] The next call will come. Nury is there when the pastor picks up.

## 2:34 to 2:50  Slide 12 (dawn): the memorial  [90s]  [ONLY AFTER JUAN APPROVES THE TEXT IN WRITING]
Option 2 of `MEMORIAL.md` (about 16 s, recommended for the deck and the live pitch). The words are on the slide; Juan chooses whether anyone reads them. Nothing else is on screen. A hidden slot is ready for one portrait (Juan sends it tomorrow). Until Juan approves, the slide is hidden (press `g` to preview) and the pitch ends on slide 11 at about 2:34.
Do not edit, shorten or humanize the text. Do not add a photo unless Juan provides one.

## 90-second cut
Slides 1, 2, 3, 5, 6, 11 and the memorial: about 10 + 5 + 7 + 36 + 10 + 4 + 16 = 88 s. The rules doc says 90 s and Discord says 3 min. Verify at the venue. Both versions are ready.

## Backup slides (do not speak; use for questions). Press `b`.
What broke and what changed. Four evaluation layers, with what each cannot do. Why two judges. Privacy that is tested. Informed by case-management practice (not in the talk). How we differ. Credits.
Gated, hidden until Sensei confirms in writing: the case file, and "listed does not mean recommended" (church network and official list).
For technical questions, use `TECH_STORY.md` section 5: why not a bigger model, how we know the guardrails work, hallucinated links, personal information, and what Jev adds.

## Rules for the speaker
- Say "legal information", never "legal advice".
- Nury helps the pastor, who helps the family. It never speaks to the family directly.
- Humanitarian, never political. Name no agency and no party.
- Do not claim a pastor, attorney or family has used it. We have not validated with one.
- Say "smoke test" and "first pass" where the numbers come from one. Do not round up.
- Say nothing about the church network, the skill system or the case file until Sensei confirms in writing. Hospital is open (2026-10-07); its numbers wait for the final re-run.
