---
id: "c-0001-detention-pastoral-length"
type: "prompt_line"
status: "proposed"
created: "2026-10-07"
synthetic: true
evidence: {"playbook": "detention", "stage": "pastoral", "edits": 17, "edits_shorter": 15, "chip_too_long": 13, "target_words": 50}
approved_by: null
approved_date: null
test_result: null
release_commit: null
---
# Shorter pastoral drafts for detention

## Why

In 17 edits of the pastoral stage, 15 made the text shorter and 13 pastors tapped 'Too long'. The median length of the shortened versions was 50 words.

## Draft change

```json change
{
 "kind": "append",
 "file": "code/playbooks/detention/prompts/pastoral.txt",
 "text": "\nKeep it to about 50 words.\n"
}
```
