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
