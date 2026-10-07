# For judges and reviewers: three short cards

Each card says what the document is, the most useful fact in it, and the biggest limit. Full text in the linked file.

## What did not work
Fifteen things we tried that failed, in plain words: what we tried, what happened, what we changed and what we still do not know. Half are about the product (a tone score that did not rise, 11 of 18 hostile intakes stopped at triage, a link check a made-up website could pass). Half are about us (a first red-team result that was wrong, "14 checks" that was 20, commit dates we typed by hand). **Limit:** every failure was found by our own checks, a red team or an audit. No pastor or family has used Nury. Read: `WHAT_DID_NOT_WORK.md`.

## Economics
A case costs about 6 cents (detention) to 9 cents (hospital) in model spend and takes 34 to 50 seconds, from the final scored runs. The document also lists what could break the economics: a worst case of 135 model calls for one case, long intakes, a stage that never passes, and a shared key with no budget cap. **Limit:** Gloo spend only. Jev's price, hosting and people are not included, and every number comes from synthetic cases. Read: `ECONOMICS.md`.

## The pattern
An approve-gated stage pipeline for high-stakes drafting: stages, a human gate after each, rules plus an independent classifier before the human sees a draft, bounded retries then escalation to the human, edits carried forward, an audit trail, privacy tokens in, no send path. One page, with the files to copy. **Limit:** it lowers risk; it does not replace the human. Three other domains are named as ideas, not claims. Read: `PATTERN.md`.
