# Nury: 3-minute pitch script (deck v2, with the technical story)

Speaker: Juan Peláez (3Metas). Target about 2:53 with the memorial, 3:00 at most, at a calm pace. Slide numbers match `deck.html` (default view, gated items hidden). Press `n` for notes, `g` to reveal gated items for review, `b` to jump to backup.
Tags: `[90s]` lines and slides stay in the 90-second cut. The video plays inside the demo slide (approved).
`[NUMBER]` = real scorecard number only. If none by Oct 7 16:00 MDT, use the fallback line.
Family and intake: `SHARED_DEMO.md`. Do not say "ICE" or name any agency.
Technical claims and the five hard questions: `TECH_STORY.md`. Numbers come from `documents/TECH_CLAIMS.md`, VERIFIED rows only.

## Timing table (3-minute version; the arc is night, lantern, light, dawn)
Revised 2026-10-07 after SCRIPT_REVIEW (hack-sensei approved). Slides 2 and 3 are one slide now. Speaking pace about 2.5 words a second.
| Slide | Act | Content | Time | Length |
|---|---|---|---|---|
| 1 | Night | 2:07 AM, the call (dark slide) | 0:00 to 0:14 | 14 s |
| 2 | Lantern | This is Nury, and the name entry (one slide) | 0:14 to 0:26 | 12 s |
| 3 | Light | Concept and product | 0:26 to 0:40 | 14 s |
| 4 | Light | The demo: Eric's film plays, Juan speaks before and after | 0:40 to 1:14 | 34 s |
| 5 | Light | How it is built | 1:14 to 1:36 | 22 s |
| 6 | Light | Innovation | 1:36 to 1:50 | 14 s |
| 7 | Light | Use of AI | 1:50 to 2:09 | 19 s |
| 8 | Light | Impact and execution | 2:09 to 2:22 | 13 s |
| 9 | Light | Teamwork, and what is next | 2:22 to 2:32 | 10 s |
| 10 | Dawn | Close | 2:32 to 2:37 | 5 s |
| 11 | Dawn | Memorial (option 2, about 16 s; gated until Juan approves) | 2:37 to 2:53 | 16 s |
Total 2:53 with the memorial, 2:37 without. With memorial option 3 (8 s) the total is 2:45. Slide numbers match the rebuilt deck (default view, 11 talk slides).

## 0:00 to 0:14  Slide 1 (night): the call  [90s]
The slide is dark. Play the phone buzz if the room allows. [90s] It is 2:07 in the morning. A pastor's phone rings. A family. A husband was detained last evening. The pastor has no lawyer on the line, a phone, and a few minutes.

## 0:14 to 0:26  Slide 2 (lantern): This is Nury, and the name entry  [90s]
The slide turns from night to paper and the lantern lights. [90s] "This is Nury." Pause. The entry builds itself. [90s] "A given name from Arabic nur, light. An AI crisis response agent." Then "see also: lantern" appears on its own. Do not say her name here; it appears once, in the memorial.

## 0:26 to 0:40  Slide 3 (light): concept and product
"Five stages, one gate after each. The app opens on a crisis selector. Detention and hospital emergency are live, and two more are coming soon. Nothing is sent without the pastor." (30 words, 12 s)
[ONLY AFTER SENSEI CONFIRMS IN WRITING THAT THE VERSE BANK IS BUILT: The pastoral message carries a Bible verse, quoted from a verified list. The AI never writes Scripture.]
Do not say "the one you saw": the demo comes next. Say nothing more about the coming-soon cards.

## 0:40 to 1:14  Slide 4 (light): the demo  [90s]
DECIDED (hack-sensei, 2026-10-07): Eric's film plays and Juan stays silent while it plays. It is the reliable choice: no wifi, no credit, and Eric's voice stays consistent. Juan speaks before it starts and right after it ends.
Play rows 5 to 7 of the film (the tool, the rights brief, the turn: 0:25 to 0:52 in table 1, about 27 s), with Eric's lines. Do not run the live app on stage.
- Juan BEFORE (about 3 s): "Here is one call, start to finish."
- The film plays (27 s). Juan says nothing.
- Juan AFTER (about 4 s): "The pastor never saw the unsafe draft. Nury never sends. The pastor does."
The selector screenshot is the first frame the audience sees. If the film fails to play, Juan says the three sentences of the old demo text (types, five stages with a gate after each, rejected draft regenerated) and shows the screenshots; no live app.

## 1:14 to 1:36  Slide 5 (light): how it is built  [90s]
Trace the line once. [90s] "The pastor types. Names become tokens inside Nury. Only tokens reach Gloo AI Studio. Named checks, then Jev, reject unsafe drafts, up to three tries. The pastor decides. The leak test ran 90 checks per playbook and found no names." (42 words, 17 s)
Under the diagram: twenty named checks plus the safety floor, five Gloo calls, no send path. Point at the bottom strip: "That is how we test it before release. Four layers."

## 1:36 to 1:50  Slide 6 (light): innovation
"Adding a crisis is adding a playbook folder. The engine does not change. Detention and hospital both run on it, and a test builds a new crisis from scratch." (30 words, 12 s)
Unsafe drafts never reach the pastor: say it once, on slide 6. Not again here.
[ONLY AFTER SENSEI CONFIRMS IN WRITING] Playbooks share small skills, like voice and grounding.

## 1:50 to 2:09  Slide 7 (light): use of AI, and why two judges
[47 words, about 19 s] The writer is Claude, through Gloo AI Studio. Our rules check every draft, and Jev, from TypeSafe, classifies it with a probability before the pastor sees it. Before release, a red team of three models from other makers hunts for what we missed, and a person decides.
If asked for more, go to the backup slide "Why two judges" (press `b`): who each model is (the red team is OpenAI GPT-5.4, Google Gemini 3.1 Pro and Meta Llama 4 Maverick; none is Claude, on purpose), the numbers (unsafe 0.89 to 0.98, safe 0.02 to 0.24), the stability check (TC 37: five stored runs, within 0.03 an hour later; one verdict near a threshold flipped, 0.21 to 0.18), and the honest limits. In validation all three red-team reviewers caught 8 of 8 injected problems and also flagged safe text, so it advises. Final panel numbers: [PLACEHOLDER until hack-artisans finishes]. Jev is from TypeSafe, not ours: say "used at run time and at test time, and disclosed as third-party technology".

## 2:09 to 2:22  Slide 8 (light): impact and execution
Do NOT read the disclosure aloud: it is on the slide. Speak only the numbers and one failure (about 30 words).
[ONLY IF TRUE] Hand-built scenarios, scored by typed judges. [NUMBER: pass rate], [NUMBER: drafts rejected and regenerated], [NUMBER: cost per run], [NUMBER: latency per run].
Fallback if no scorecard: "We built twenty scenarios and scored each stage. The scorecard is in our build document."
No number from any interim run. Say one failure, plainly: a checklist named a detainee locator that was not in our vetted sources. We fixed the prompt and the check.
On the slide, not spoken: "The Jev decision API from TypeSafe is used as typed judges in our evaluation harness and as a run-time draft classifier. Disclosed as third-party technology per the rules."

## 2:22 to 2:32  Slide 9 (light): teamwork, and what is next
"Built by one founder and a small team of AI agents. Next: real pastors, and an attorney to review our sources." (20 words, 8 s) Not done yet.

## 2:32 to 2:37  Slide 10 (dawn): close  [90s]
[90s] "The next call will come. Nury is there when the pastor picks up."

## 2:37 to 2:53  Slide 11 (dawn): the memorial  [90s]  [ONLY AFTER JUAN APPROVES THE TEXT IN WRITING]
Option 2 of `MEMORIAL.md` (about 16 s, recommended for the deck and the live pitch). The words are on the slide; Juan chooses whether anyone reads them. Nothing else is on screen. A hidden slot is ready for one portrait (Juan sends it tomorrow). Until Juan approves, the slide is hidden (press `g` to preview) and the pitch ends on slide 11 at about 2:37.
Do not edit, shorten or humanize the text. Do not add a photo unless Juan provides one.

## 90-second cut
Slides 1, 2, 4, 5, 10 and the memorial: about 10 + 8 + 34 + 12 + 5 + 16 = 85 s. The rules doc says 90 s and Discord says 3 min. Verify at the venue. Both versions are ready.

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
