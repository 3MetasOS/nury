# Deck copy: the words for every slide

Written 2026-10-07 by hack-ninja for hack-artisans (visual design) and hack-sensei. hack-artisans owns the look of `presentation/deck.html`. hack-ninja owns these words, `PITCH_SCRIPT.md`, `FINALIST_SCRIPT.md` and the claims check.

Limits per slide: headline up to 8 words, one supporting line up to 15 words, up to three labels of 1 to 4 words, no paragraphs. Every number comes from `documents/product/ALIGNMENT_AUDIT.md`. Slide names are the URL anchors in the current deck. The talk has 13 slides, not 12: "The evaluation system" was added on sensei's order. The current deck (c57f421) has more text on some slides than this file allows. Cut to this file.

Real screens live in `presentation/screens/` (1280 wide, light mode). `06-final-es-1280.png` is broken (2560x48): do not use it. Other images: `images/family-copy-p1.png`, `images/pastor-copy-p2.png` (real PDF pages), `images/app/export-menu.png`. Crops used now are in `images/app/`.

## Talk

### 1. the-call (dark)
- Headline: 2:07 AM. A pastor's phone rings.
- Line: A husband was detained last evening. The family needs help now.
- Labels: none. Phone buzz sound if the room allows.
- Spoken (11 s): "It is 2:07 in the morning. A pastor's phone rings. A husband was detained last evening. The pastor has a phone and no lawyer on the line."
- Notes: Open in the dark. The pastor is a character, not a market. Say no agency name and never "ICE". Humanitarian, not political. Family: Maria, Jose, two children (SHARED_DEMO.md).
- Screens: none.

### 2. the-name (lantern)
- Headline: Nury
- Line: A given name from Arabic nur, light. An AI Crisis Response Agent.
- Labels: noun · /NOO-ree/ · see also: lantern
- Spoken (6 s): "This is Nury." Entry builds in about 2.4 s. The tagline sits BELOW the logo.
- Notes: Do not say her name here: it appears once, in the memorial. Sources in NAME_ENTRY.md.
- Screens: none.

### 3. one-engine
- Headline: One engine. Every crisis is its own workflow.
- Line: Each crisis has its own stages. Two run today.
- Labels: Immigration matter · Hospital emergency · Two coming soon
- Spoken (12 s): "Each crisis is its own workflow, with its own stages. Both live ones have a gate after each. Two more are coming soon. Nothing is sent without the pastor."
- Notes: Stage names per crisis from `stages.json` (immigration: Triage, Rights brief, Attorney resources, Family checklist, Pastoral message; hospital: Triage, Family information brief, Hospital resources, Family checklist, Pastoral message). Both live ones have five; the engine allows any number. Do not say "the one you saw". Criterion: Concept and Product.
- Screens: `03-chooser-1280.png` (optional thumbnail).

### 4. the-demo
- Headline: One call. Start to finish.
- Line: Nothing moves on without the pastor. Nothing is sent.
- Labels: Pick the crisis · Read each stage · Approve, edit or stop
- Spoken: before (3 s) "Here is one call, start to finish." Film plays (27 s), Juan silent. After (4 s) "A draft that failed was held back. Nury never sends. The pastor does."
- Notes: Eric's film plays; no live app on stage. If the film fails, show the screens and say the three lines. Real screens, made-up family.
- Screens: `03-chooser-1280.png`, `04-intake-1280.png`, `05-gate-1280.png`, `07-case-overview-1280.png`.

### 5. what-the-family-gets
- Headline: What the family gets.
- Line: A PDF the pastor can hand over.
- Labels: Family copy, in Spanish · Pastor copy
- Spoken (8 s): "This is what the family gets: a copy in their own language, as a PDF the pastor can hand over."
- Notes: Real pages from a recorded run on the sample intake (made-up family). Do not say a family has received one. PDF needs Chrome or Chromium; otherwise a print view.
- Screens: `images/family-copy-p1.png`, `images/pastor-copy-p2.png`.

### 6. built-to-grow
- Headline: A new crisis is a new folder.
- Line: Add a folder, not engine code. Rules and tests are files too.
- Labels: Add a crisis · Add a rule · Add a test
- Spoken (10 s): "Nury is built to grow. A crisis is a folder of plain files. Add a folder, not engine code. Rules and tests are files too."
- Notes: Evidence: `code/nury/playbook.py`, `code/tools/new_playbook.py`, `documents/product/ADD_A_RULE.md`, test `test_second_playbook_zero_engine_changes`. Criterion: Innovation. Say nothing about skills or the church network.
- Screens: none (file tree diagram).

### 7. how-it-is-built
- Headline: The model sees tokens, not names.
- Line: Only tokens reach Gloo AI Studio. The pastor decides every stage.
- Labels: Pastor · Tokens · Gloo AI Studio
- Spoken (14 s): "The pastor types. Names become tokens before anything leaves Nury. Only tokens reach Gloo AI Studio. The pastor decides every stage. A leak test ran 90 checks per playbook and found no names."
- Notes: Evidence: `documents/TECH_CLAIMS.md` rows 1, 3, 4, 5, 16. Details such as a workplace can still hint at who someone is: say so if asked. Jev sees tokens only.
- Screens: none (diagram).

### 8. use-of-ai
- Headline: Claude writes. Rules and Jev check.
- Line: Other models reviewed it once, before release.
- Labels: While a pastor uses it · Before release · Never at run time
- Spoken (12 s): "While a pastor uses it, Claude writes through Gloo AI Studio. Our rules check every draft, and Jev, from TypeSafe, checks it again. Before release, other models reviewed it."
- Notes: Keep two times apart. Run time: Claude Sonnet 4.6 via Gloo, 20 named rules plus the safety floor, Jev, the pastor at each gate. Before release, by hand: test layers and the outside review (GPT-5.4, Gemini 3.1 Pro, Llama 4 Maverick; advice only; not re-run on the final build). A full case: 34 to 50 s, 6 to 9 cents. The checks are tripwires, not proofs. Criterion: Use of AI.
- Screens: none.

### 9. the-evaluation-system
- Headline: Two evaluation systems. One builds the prompts. One checks every draft.
- Line: Jev works in both. It is a decision API, not a chat model.
- Labels: Before release · While a pastor uses it · Jev in both
- Chips: 46 test cases (20 immigration, 8 hospital, 18 hostile) · Jev answered 239 of 239 calls in scored runs.
- Spoken (15 s): "We built two evaluation systems. One runs before release: we test, judge, compare, and a person decides what ships. One runs on every draft: rules, then Jev, then up to three rewrites. Jev works in both."
- Lane 1 boxes: Change a prompt or rule · Run 46 test cases · Judge every run · Compare with the last build · A person decides what ships. Lane 2 boxes: Claude writes a draft · 20 rules and a safety floor · Jev answers yes or no · Fails: rewrite, up to 3 tries · The pastor approves, edits or stops.
- Notes: Judges: plain code, Jev, outside AI reviewers, a person. Do not say "in about a second": the longest Jev call was 435 ms. Criterion: Technical Execution.
- Screens: none.

### 10. impact
- Headline: What we measured.
- Line: Judge results, not human verdicts. Made-up families only.
- Labels: Passed · Failed · Waiting for a person
- Table: Immigration (20): 11 / 1 / 8. Hospital (8): 5 / 0 / 3. Hostile intakes (18): 13 / 1 / 4. Cost 6 to 9 cents a case, 34 to 50 s. One line: "11 of 18 hostile intakes stopped at triage. We changed the triage prompt. None did on the final build."
- Always on slide (verbatim): The Jev decision API from TypeSafe is used as typed judges in our evaluation harness and as a run-time draft classifier; disclosed as third-party technology per the rules.
- Spoken (14 s): "We judged 46 made-up cases: 29 pass, 2 fail, 15 wait for a person. A case costs 6 to 9 cents. Tone is still under target, and no person has rated warmth."
- Notes: Build 9bc5c6d. No Before column, no pass rate. If asked for another failure: the tone judge sits near 3 of 5 against 4 and moves up to 0.75 between identical runs. Criterion: Impact and Execution.
- Screens: none.

### 11. what-we-built (was where-we-stand; the "Not done yet" column is removed, per Juan)
- Headline: One founder. Five AI agents.
- Line: Every step is in the commit log.
- Labels: none. Six big ticks, one line each, 1 to 6 words:
  1. Two live crises, plain files
  2. The app, with PDF export
  3. Rules, a safety floor, Jev
  4. Verses from a verified list
  5. 46 test cases, outside review
  6. Learning loop, replay, command line
- Spoken (6 s): "One founder and five AI agents built it. Every step is in the commit log."
- Notes: 2:22 to 2:28. Criterion: Presentation and Teamwork. Every tick is checked against documents/product/ALIGNMENT_AUDIT.md (46 scenarios, replay, CLI and MCP shipped, learning loop built and off). Honest status is NOT on this slide on purpose: it lives on the Impact slide ("Made-up families only."), the About page, How this was built (Limits) and What did not work. If asked: no real pastor has used it, no attorney has reviewed our sources, nothing has been learned yet. Do not volunteer "not read" or "nothing learned" on a slide. "Five AI agents" has no audit row: sensei to confirm.
- Screens: none.

### 12. close (dawn)
- Headline: Nury. An AI Crisis Response Agent.
- Line: The next call will come. Nury is there when the pastor picks up.
- Labels: Read more: the About page
- Always on slide: Nury is an AI assistant, not a lawyer, pastor, counselor, or therapist. This is general legal information, not legal advice. Built in Boulder, Colorado, during the Gloo AI Hackathon, October 6 to 8, 2026. Every step is in the build log.
- Spoken (5 s): "The next call will come. Nury is there when the pastor picks up." 90-second cut ends here.
- Screens: none (lanterns photo).

### 13. memorial (gated; hidden until Juan approves in writing)
- Text, Juan's words, Option 1, VERBATIM, nobody edits, shortens or humanizes:
  "Nury is named for my aunt, Nury Peláez. / She served her church for 83 years, in the small things and the big ones, / always with a smile, always with Jesus in her heart. / She passed away a month ago. This is for her."
- Labels: none. Nothing else on screen. A hidden slot for one portrait if Juan sends one.
- Spoken (16 s): Juan chooses whether anyone reads it.
- Notes: Pending Juan's written approval. Do not show or publish as approved.
- Screens: none.

## Backups (not spoken; press b)

| Name | Headline | One line | Labels | Notes (source) |
|---|---|---|---|---|
| the-evaluation-system-in-detail | The evaluation system in detail | Red team before release only. Jev at run time and test time. | Red team · Jev | Three models from three makers; they flag safe text too. Not independent: Jev also judges at test time. Evidence: HOW_IT_WAS_BUILT, TECH_CLAIMS. |
| what-broke-and-what-changed | What broke and what changed | Nine of fifteen items on the What did not work page. | Broke · Changed | WHAT_DID_NOT_WORK items 1, 2, 3, 5, 7, 8, 10, 11, 15. Our own checks found them; no pastor did. |
| jev-checks-every-draft | Jev checks every draft | 239 of 239 calls answered in the scored runs. | Yes or no questions · Rewrite up to 3 · Pastor decides | Longest call 435 ms, typical about 155 ms, about 2 percent of model time, about $0.0003 to $0.0005 a case. Lines 0.50 (0.60 for facts). Not calibrated. Do NOT add the fail-open fact here: it lives only in Limits, TECH_CLAIMS and TECH_STORY Q15. |
| does-nury-learn-from-pastors | Does Nury learn from pastors? | Built, off by default. Nothing learned yet. | Records changes · No names · A person reviews | Never changes Nury by itself. |
| four-test-layers | Four test layers | Before release, never at run time. | Plain code · Jev · Red team · A person | Each layer and what it cannot do. |
| privacy-that-is-tested | Privacy that is tested | Names become tokens before any model request. | Tokens · Leak test | 90 checks per playbook, 0 found. Details like a workplace can still hint at who. |
| cases-export-and-pdf | Cases, export and PDF | Family copy and pastor copy, as PDF or a zip. | Export · Family copy · Pastor copy | Screen: `images/app/export-menu.png`. PDF needs Chrome or Chromium. The next-steps map lists steps and questions; it never says what will happen. |
| listed-does-not-mean-recommended (gated) | Listed does not mean recommended | Nury lists vetted contacts. It never endorses anyone. | Church's own list · Official lists | Show only after sensei confirms in writing. |
| informed-by-case-management-practice | Informed by case-management practice | Six functions from the NASW standards. | none | STANDARDS_PAGE.md. |
| where-nury-fits | Where Nury fits | Routine church tools and Nury cover different moments. | Routine · Crisis | Neutral. No team or product names. |
| credits | Credits | Photos, fonts, Scripture, voice and technology. | none | Porch light (Henryemix, CC0), lanterns (Peter Hershey, CC0); fonts Fraunces, Inter, Gochi Hand (SIL OFL); YouVersion; Gloo AI Studio; TypeSafe (Jev, not built by us); ElevenLabs (AI voice). Details: branding/IMAGES.md. |

## Rules that hold for every slide
- Say "case", never "package". Say "pass, fail, waiting for a person"; judge results are not human verdicts; never quote a pass rate.
- Tagline always below the logo. No team or product names of other entries.
- No claim that a pastor, attorney or family has used Nury.
- Keep verbatim: the Jev disclosure line, the memorial text, disclaimers.
- Keys never appear.

## Claims I could not verify
- "Five AI agents" (slide 11) is not in ALIGNMENT_AUDIT.md.
- Word counts for the spoken lines are mine at 2.5 words a second, not timed aloud.
- The chooser thumbnail on slide 3 is optional: there was no room in the current layout.
