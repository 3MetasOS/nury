---
id: "c-0005-detention-outcome"
type: "new_scenario"
status: "proposed"
created: "2026-10-07"
synthetic: true
evidence: {"playbook": "detention", "revisions_did_not_go_as_hoped": 3, "revisions_total": 7}
approved_by: null
approved_date: null
test_result: null
release_commit: null
---
# A scenario for detention cases that did not go as hoped

## Why

3 of 7 'Something changed' answers for detention said it did not go as hoped.

## Draft change

```json change
{
 "kind": "add_file",
 "file": "evaluations/scenarios/99-detention-after-outcome-review.yaml",
 "content": "id: detention-after-outcome-review\nnumber: 99\nplaybook: detention\ncategory: workflow\ntitle: TODO a fictional case like those that did not go as hoped\nintake: TODO a person writes a fictional intake. Do not paste anything from a real case.\noutput_language: es\npastor_actions: {1: approve, 2: approve, 3: approve, 4: approve, 5: approve}\nexpected_behavior: TODO\npass_criteria:\n  deterministic: [banned_phrases, disclaimers, allowlist, language, workflow, completeness]\n  jev_noul: {}\n  jev_score: {}\nfault_injection: null\nflags: {}\n"
}
```

The draft scenario contains TODO fields and cannot run until a person writes a fictional intake. The test script refuses a candidate that still has TODO in a new file.
