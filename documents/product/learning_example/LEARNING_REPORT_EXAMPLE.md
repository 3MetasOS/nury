# Learning report

> **SYNTHETIC DATA.** This report was built from synthetic scenarios (scenario 16, pastor edits a stage, and the revision scenarios), not from any real pastor. No real pastor has used Nury. It shows how the loop works, not what pastors want.

Nothing in this report changes Nury. A candidate is a proposal. A person approves it in its review file, it passes the before and after test, and it ships in a normal release.

- Feedback read from: `documents/product/learning_example/feedback`. Modes seen: sentences. Lines that fell back to counts for lack of a pseudonymizer: 0.
- Gate lines: 60. Edits: 27. Evidence needed for a candidate: at least 3 separate edits or chips.

## What pastors changed, by crisis and stage

| Crisis | Stage | Gates | Edited | Edit rate | Shorter | Longer | Chips | Edits where a rule had rejected a draft | Edits where Jev was uncertain or rejected |
|---|---|---|---|---|---|---|---|---|---|
| detention | checklist | 20 | 3 | 0.15 | 0 | 3 | none | 0 | 0 |
| detention | pastoral | 20 | 17 | 0.85 | 15 | 0 | Good as is 2, Not my voice 3, Too long 13 | 5 | 0 |
| hospital | checklist | 10 | 3 | 0.3 | 0 | 3 | none | 0 | 0 |
| hospital | pastoral | 10 | 4 | 0.4 | 2 | 0 | Good as is 3 | 4 | 0 |

## 'Something changed' answers

| Crisis | Went as hoped | Did not go as hoped | Unknown |
|---|---|---|---|
| detention | 3 | 3 | 1 |
| hospital | 1 | 0 | 2 |

## Candidate improvements

### c-0001-detention-pastoral-length: Shorter pastoral drafts for detention

- TYPE: **prompt_line**   STATUS: proposed
- Evidence: {"playbook": "detention", "stage": "pastoral", "edits": 17, "edits_shorter": 15, "chip_too_long": 13, "target_words": 50}
- Why: In 17 edits of the pastoral stage, 15 made the text shorter and 13 pastors tapped 'Too long'. The median length of the shortened versions was 50 words.
- Draft change: a change block (see the candidate file)

```
{
 "kind": "append",
 "file": "code/playbooks/detention/prompts/pastoral.txt",
 "text": "\nKeep it to about 50 words.\n"
}
```

### c-0002-detention-pastoral-phrase: Pastors remove the phrase 'este paquete hay' in pastoral

- TYPE: **new_rule**   STATUS: proposed
- Evidence: {"playbook": "detention", "stage": "pastoral", "phrase_words": 3, "edits_removing_it": 15, "edits": 17}
- Why: 15 of 17 edits removed or replaced a sentence containing 'este paquete hay'.
- Draft change: a change block (see the candidate file)

```
{
 "kind": "json_append",
 "file": "code/playbooks/detention/playbook.json",
 "key": "extra_banned",
 "value": {
  "pattern": "\\beste\\s+paquete\\s+hay\\b",
  "why": "pastors removed this phrase in the learning loop (candidate: review before use)"
 }
}
```

### c-0003-detention-pastoral-phrase: Pastors remove the phrase 'de pasos para' in pastoral

- TYPE: **new_rule**   STATUS: proposed
- Evidence: {"playbook": "detention", "stage": "pastoral", "phrase_words": 3, "edits_removing_it": 15, "edits": 17}
- Why: 15 of 17 edits removed or replaced a sentence containing 'de pasos para'.
- Draft change: a change block (see the candidate file)

```
{
 "kind": "json_append",
 "file": "code/playbooks/detention/playbook.json",
 "key": "extra_banned",
 "value": {
  "pattern": "\\bde\\s+pasos\\s+para\\b",
  "why": "pastors removed this phrase in the learning loop (candidate: review before use)"
 }
}
```

### c-0004-detention-pastoral-voice: Voice or tone of pastoral drafts for detention

- TYPE: **prompt_line**   STATUS: proposed
- Evidence: {"playbook": "detention", "stage": "pastoral", "chip_not_my_voice": 3, "chip_wrong_tone": 0, "edits": 17}
- Why: 3 chips said 'Not my voice' or 'Wrong tone' on this stage.
- Draft change: none yet: a person writes it

### c-0005-detention-outcome: A scenario for detention cases that did not go as hoped

- TYPE: **new_scenario**   STATUS: proposed
- Evidence: {"playbook": "detention", "revisions_did_not_go_as_hoped": 3, "revisions_total": 7}
- Why: 3 of 7 'Something changed' answers for detention said it did not go as hoped.
- Draft change: a change block (see the candidate file)

```
{
 "kind": "add_file",
 "file": "evaluations/scenarios/99-detention-after-outcome-review.yaml",
 "content": "id: detention-after-outcome-review\nnumber: 99\nplaybook: detention\ncategory: workflow\ntitle: TODO a fictional case like those that did not go as hoped\nintake: TODO a person writes a fictional intake. Do not paste anything from a real case.\noutput_language: es\npastor_actions: {1: approve, 2: approve, 3: approve, 4: approve, 5: approve}\nexpected_behavior: TODO\npass_criteria:\n  deterministic: [banned_phrases, disclaimers, allowlist, language, workflow, completeness]\n  jev_noul: {}\n  jev_score: {}\nfault_injection: null\nflags: {}\n"
}
```

## Dropped for safety

Sentences dropped because they still looked like a protected value or a name: 0. They are counted, never stored.

