# Proof numbers: where they go, and the cut rule

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
Hospital results go in only after hack-sensei confirms in writing that hospital runs and has at least 5 scored scenarios. Places: deck slide 7 table row, pitch script 1:35 block placeholder. If not confirmed by the cut time, delete both. Coming-soon cards are never described beyond their labels.

## Nury skill system (gated, added Oct 6)
Not claimed anywhere. Ships only after hack-sensei confirms in writing that it is built, tested and measured.
Planned lines, ready to paste:
- Deck slide 5 bullet: "Stages share reusable skills, such as voice and grounding, that a playbook includes by name."
- Pitch script, 1:35 block, after the folder line: "Playbooks share small skills, like voice and grounding. A stage includes them by name."
If a measured result is confirmed too (for example, a before and after score), add it with the real number only.

## Case file and next-steps map (gated, added Oct 6)
Not claimed anywhere. Ships only after hack-sensei confirms in writing that it is built and tested.
Required wording: "the pastor keeps a case file on their own computer". Never say it predicts or forecasts. The map is steps and questions, never outcomes.
Planned lines, ready to paste:
- Deck slide 5 bullet: "The pastor keeps a case file on their own computer, with a map of next steps and questions to ask."
- Pitch script, 1:35 block: "The pastor keeps a case file on their own computer. Nury adds a map of next steps and questions to bring to an attorney. It lists steps and questions. It does not say what will happen."

## Church network and official lists (gated, queued Oct 7, not started)
Rule change from Juan. Replaces "never recommends a specific attorney". Ship only on hack-sensei's written go, after it works.
Stale lines today:
- description.txt line 11: "Nury never recommends a specific attorney." (6 words)
- deck.html slide 4 flow item "Attorney resources": "Never one named attorney."
Planned replacements:
- Description: "Nury lists only pastor-vetted contacts and official lists, endorsing no one." (10 words, net +4: 249 alone; with the two-playbooks variant it reaches 253, so cut one sentence, for example "Family materials come out in Spanish.", only if both ship.)
- Deck: "Lists only contacts the pastor has vetted, labeled as the church's own, plus official lists. Never endorses anyone."
- Pitch script, 1:35 block: "Attorney resources come from two places: contacts the pastor has vetted, labeled as the church's own, and official lists. Nury endorses no one."
Do not say "find more" or any web search. It is after submission.
