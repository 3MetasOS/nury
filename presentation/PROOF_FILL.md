# Proof numbers: where they go, and the cut rule

> **DONE 2026-10-07 04:08.** All placeholders filled from the final scorecards. This file is history.


Source: a clean `evaluations/results/scorecard.md` from `--agent nury` (real Gloo). Not `Agent: mock`. hack-sensei says when it exists.
Cut rule: no real numbers by Oct 7 16:00 MDT, then cut every item below that needs them.

| Number | Description.txt | deck.html slide 6 | PITCH_SCRIPT 2:10 block | FINALIST_SCRIPT beat 9 |
|---|---|---|---|---|
| Pass rate | "Results: [PLACEHOLDER...]" | Pass rate card | [NUMBER: pass rate] | [NUMBER: pass rate] |
| Scenarios run | "20 hand-built scenarios" | intro line | "Twenty hand-built scenarios" | [NUMBER: scenarios] |
| Rejected and regenerated | same sentence | card | [NUMBER: ...] | [NUMBER: rejected drafts] |
| Cost per run | no | card | [NUMBER: cost per run] | no |
| Latency per run | no | card | [NUMBER: latency per run] | no |

## If cut
- description.txt: delete the sentence "We tested 20 hand-built scenarios. Results: [PLACEHOLDER: scorecard numbers]." (11 words, leaves about 234).
- deck.html: delete slide 6 (`id="s6"`); the counter updates itself.
- PITCH_SCRIPT: use the fallback line; drop "[ONLY IF TRUE]" sentence.
- FINALIST_SCRIPT: use the fallback VO; hack-video gives the 8 s back to beats 5 and 6.
- Jev disclosure stays in the description either way.

## Check before filling
- Numbers match the scorecard exactly. No rounding up. Say "hand-built scenarios", never "benchmark".
- Report failures too. If any scenario failed, say pass rate honestly and name the fix in the build log.

## Hospital (added Oct 6)
Hospital is OPEN (hack-sensei, in writing, 2026-10-07): it may be named as the second live playbook. Its results go in only after the final re-run, from its own scorecard. Places: deck slide 7 table row, pitch script 1:35 block placeholder. If not confirmed by the cut time, delete both. Coming-soon cards are never described beyond their labels.

## Nury skill system (gated, added Oct 6)
Not claimed anywhere. Ships only after hack-sensei confirms in writing that it is built, tested and measured.
Planned lines, ready to paste:
- Deck slide 5 bullet: "Stages share reusable skills, such as voice and grounding, that a playbook includes by name."
- Pitch script, 1:35 block, after the folder line: "Playbooks share small skills, like voice and grounding. A stage includes them by name."
If a measured result is confirmed too (for example, a before and after score), add it with the real number only.

## Case file and next-steps map (gated, added Oct 6)
Not claimed anywhere. Ships only after hack-sensei confirms in writing that it is built and tested.
Required wording (updated: Nury is a web app on a server): "Nury saves each approved case". Do not say where it is stored beyond "saved in Nury", and do not claim sign-in, accounts or encryption. Never say it predicts or forecasts. The map is steps and questions, never outcomes.
Planned lines, ready to paste:
- Deck bullet: "Nury saves each approved case, with a map of next steps and questions to ask."
- Pitch script, 1:35 block: "Nury saves each approved case. Nury adds a map of next steps and questions to bring to an attorney. It lists steps and questions. It does not say what will happen."

## Church network and official lists (gated, queued Oct 7, not started)
Rule change from Juan. Replaces "never recommends a specific attorney". Ship only on hack-sensei's written go, after it works.
Stale lines today:
- description.txt line 11: "Nury never recommends a specific attorney." (6 words)
- deck.html slide 4 flow item "Attorney resources": "Never one named attorney."
Planned replacements:
- Description: "Nury lists only pastor-vetted contacts and official lists, endorsing no one." (10 words, net +4: 249 alone; with the two-playbooks variant it reaches 253, so cut one sentence, for example "Family materials come out in Spanish.", only if both ship.)
- Deck (slide 4, Attorney resources): "Lists only contacts the pastor has vetted, labeled as the church's own, plus official lists. Never endorses anyone." This is the rule wording from hack-sensei.
- Pitch script, 1:35 block: "Attorney resources come from two places: contacts the pastor has vetted, labeled as the church's own, and official lists. Nury endorses no one."
Do not say "find more" or any web search. It is after submission.

Note: the full rule wording is 18 words, too long for the 250-word description (it would reach 257). The description keeps the compact form above. The deck and script use the full wording.

## Scripture in the pastoral message (gated, added Oct 7, not built yet)
Not claimed anywhere. Ships only after hack-sensei confirms in writing that it is built, and TECH_CLAIMS has a VERIFIED row.
The idea, from BUILD_LOG item 83: a verified verse bank. The model only picks a verse id. The engine inserts the exact text (public-domain translations: Reina-Valera 1909 and the World English Bible). Checks verify the verse verbatim. The model writes at most two short sentences on why.
Prepared lines, all hidden until confirmed:
- Deck (concept slide, stage 5): "With a Bible verse, quoted from a verified list." (already in the deck, hidden; press `g` to preview)
- Pitch script, concept slide: "The pastoral message carries a Bible verse, quoted from a verified list. The AI never writes Scripture."
- Film, row 9 caption: "A verse, quoted from a verified list. Never written by the AI." No new Eric line. If a line is wanted: "A message with a verse. His to edit." (8 words) would replace L9, and it needs a new generation and Sensei's review.
- Q and A: "Does the AI write Scripture?" is Q7 in TECH_STORY.md, marked gated.
Do not say: that a verse "will happen", that God will act, or anything about outcomes. Do not name a licensed version until the YouVersion terms are met.

Outbound-calls wording (added Oct 7): "one outbound call" is no longer true if YouVersion is on. Default line: "No send path." Gated line, only after hack-sensei confirms YouVersion is on in the final build: "Gloo for the model, YouVersion for exact Scripture text; only tokens and a verse reference leave the app; no send path." If YouVersion is off: "Only the model request leaves Nury, with tokens instead of names; no send path."
