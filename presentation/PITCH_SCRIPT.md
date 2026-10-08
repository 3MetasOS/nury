# Nury: 3-minute pitch script (deck v2, with the technical story)

Speaker: Juan Pelaez (3Metas). Target about 2:54 with the memorial, 3:00 at most, at a calm pace. Slide numbers match `deck.html` (default view, gated items hidden). Press `n` for notes, `g` to reveal gated items for review, `b` to jump to backup.
Tags: `[90s]` lines and slides stay in the 90-second cut. The video plays inside the demo slide (approved).
`[NUMBER]` = real scorecard number only. If none by Oct 7 16:00 MDT, use the fallback line.
Family and intake: `SHARED_DEMO.md`. Do not say "ICE" or name any agency.
Technical claims and the five hard questions: `TECH_STORY.md`. Numbers come from `documents/TECH_CLAIMS.md`, VERIFIED rows only.

## Timing table (3-minute version, with the name entry)
| Slide | Content | Time | Length |
|---|---|---|---|
| 1 | This is Nury | 0:00 to 0:06 | 6 s |
| 2 | The name entry (new, approved) | 0:06 to 0:14 | 8 s |
| 3 | The call | 0:14 to 0:28 | 14 s |
| 4 | The demo (cut to about 34 s; was 42 s) | 0:28 to 1:02 | 34 s |
| 5 | How it is built | 1:02 to 1:22 | 20 s |
| 6 | Concept and product | 1:22 to 1:37 | 15 s |
| 7 | Innovation | 1:37 to 1:52 | 15 s |
| 8 | Use of AI | 1:52 to 2:10 | 18 s |
| 9 | Impact and execution | 2:10 to 2:22 | 12 s |
| 10, 11 | Teamwork, then close | 2:22 to 2:34 | 12 s |
| 12 | Memorial (gated until Juan approves) | 2:34 to 2:54 | 20 s |
Total 2:54. Without the memorial: 2:34. The 8 s for the name entry come from the demo slide (42 s to 34 s).

## 0:00 to 0:06  Slide 1: This is Nury  [90s]
The lantern lights. [90s] This is Nury. The crisis-response agent for solo pastors.

## 0:06 to 0:14  Slide 2: the name entry  [90s]
The dictionary entry builds itself: Nury, /NOO-ree/, proper noun. [90s] "A given name from Arabic nur, light. The crisis-response agent for solo pastors." Say only those two senses, then "see also: lantern". Do not say her name here; it appears once, in the memorial.

## 0:14 to 0:28  Slide 3: the call  [90s]
[90s] It is 2:07 in the morning. A solo pastor's phone rings.
[90s] A family. A husband was detained last evening. The pastor has no staff, no lawyer on the line, a phone, and a few minutes.
That is the job Nury is built for.

## 0:28 to 1:02  Slide 4: the demo  [90s]
Play the cut of the demo (the guardrail strip and the approval gate), or run the app on the locked intake. The full 90-second video does not fit this slot. The selector screenshot goes in the slot.
[90s] The pastor types what the family said. Nury runs five stages. After every stage the pastor decides: Approve, Edit, or Stop.
[90s] Watch the strip: a draft is rejected, regenerated, passed. The pastor never saw the unsafe one.
[90s] At the end, Copy, not Send. Nury never sends. The pastor does.

## 1:02 to 1:22  Slide 5: how it is built  [90s]
Trace the line once. [90s] The pastor types. A privacy layer swaps names for tokens on the pastor's computer. Only tokens go to Gloo AI Studio's guarded endpoint. The reply comes back, the names are restored here, and named checks reject unsafe drafts, up to three tries. The pastor decides. Nothing leaves with a name in it.
Under the diagram: fourteen named checks plus five floor checks, five Gloo calls, no send path. Point at the bottom strip: "That is how we test it. Four layers, at evaluation time only."

## 1:22 to 1:37  Slide 6: concept and product
Five stages, one gate after each. The app opens on a crisis selector. Each card is a playbook. Detention is the one you saw. Two more cards say coming soon.
[ONLY AFTER SENSEI CONFIRMS IN WRITING THAT HOSPITAL RUNS AND IS SCORED] A second playbook, hospital emergency, runs on the same engine. [PLACEHOLDER: hospital scenario count and pass rate]
Say nothing more about the coming-soon cards.

## 1:37 to 1:52  Slide 7: innovation
Adding a crisis is adding a playbook folder. The engine does not change. We tested that with a test playbook.
Unsafe drafts never reach the pastor: rejected, regenerated, up to three tries, then escalated.
[ONLY AFTER SENSEI CONFIRMS IN WRITING] Playbooks share small skills, like voice and grounding.

## 1:52 to 2:10  Slide 8: use of AI
Four layers check it: plain code checks, typed judges, a red-team panel of models from other makers, and a person. The leak test ran 90 checks per playbook and found no names. The typed judge scored unsafe text 0.89 to 0.98 and safe text 0.02 to 0.24, on ten checks. The red team caught 8 of 8 injected problems and also flagged safe text, so it advises and a person decides. A full package takes 50 to 56 seconds and costs about nine cents.

## 2:10 to 2:22  Slide 9: impact and execution
[ONLY IF TRUE] Hand-built scenarios, scored by typed judges. [NUMBER: pass rate], [NUMBER: drafts rejected and regenerated], [NUMBER: cost per run], [NUMBER: latency per run].
Fallback if no scorecard: "We built twenty scenarios and scored each stage. The scorecard is in our build document."
Say one failure, plainly: a checklist named a detainee locator that was not in our vetted sources. We fixed the prompt and the check.
The harness uses the Jev decision API, my prior project, as typed judges. Disclosed as prior technology per the rules.

## 2:22 to 2:34  Slide 10: teamwork, then slide 11: close
Built by Juan Pelaez at 3Metas with a small team of AI agents that coordinate over a messaging protocol. Next is the human team: pastors to pilot with, and an attorney to review the sources. Not done yet.
[90s] Slide 11. The next call will come. Nury is there when the pastor picks up.

## 2:34 to 2:54  Slide 12: the memorial  [90s]  [ONLY AFTER JUAN APPROVES THE TEXT IN WRITING]
Juan's words, unedited. He says them himself, slowly, with the slide on screen and nothing else. About 20 seconds, because the text is 45 words and needs pauses. This is the last thing in the pitch.
```
Nury is named for my aunt, Nury.
For 83 years she served her church in the small things and the big ones, always with a smile, always with Jesus in her heart.
She never married.
She passed away a month ago.
This is for her.
```
Open from Juan: her full name for "In memory of", years or omit, a photo only if he provides one. Until he approves, the memorial slide is hidden (press `g` to preview) and the pitch ends on slide 11 at about 2:34.
Do not edit, shorten or humanize these words. Do not add a photo.

## 90-second cut
Slides 1, 2, 3, 4, 5, 11 and the memorial: the `[90s]` lines (about 4 + 7 + 10 + 28 + 10 + 4 + 20 = 83 s).
The rules doc says 90 s and Discord says 3 min. Verify at the venue. Both versions are ready.

## Backup slides (do not speak; use for questions). Press `b`.
What broke and what changed. Four evaluation layers, with what each cannot do. Privacy that is tested. How we differ. Credits.
Gated, hidden until Sensei confirms in writing: the case file, and "listed does not mean recommended" (church network and official list).
For technical questions, use `TECH_STORY.md` section 5: why not a bigger model, how we know the guardrails work, hallucinated links, personal information, and what Jev adds.

## Rules for the speaker
- Say "legal information", never "legal advice".
- Nury helps the pastor, who helps the family. It never speaks to the family directly.
- Humanitarian, never political. Name no agency and no party.
- Do not claim a pastor, attorney or family has used it. We have not validated with one.
- Say "smoke test" and "first pass" where the numbers come from one. Do not round up.
- Say nothing about the church network, the skill system, the case file or hospital until Sensei confirms in writing.
