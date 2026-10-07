---
id: "c-0003-detention-pastoral-phrase"
type: "new_rule"
status: "proposed"
created: "2026-10-07"
synthetic: true
evidence: {"playbook": "detention", "stage": "pastoral", "phrase_words": 3, "edits_removing_it": 15, "edits": 17}
approved_by: null
approved_date: null
test_result: null
release_commit: null
---
# Pastors remove the phrase 'de pasos para' in pastoral

## Why

15 of 17 edits removed or replaced a sentence containing 'de pasos para'.

## Draft change

```json change
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

Caution: `extra_banned` applies to every stage of the playbook, not only this one. A person decides if a ban or a prompt line is the better fix.
