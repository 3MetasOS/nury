Scored build c317050 (Jev run-time gate: reject at 0.50 for every question except assumes_facts at 0.60). Core clean at the start of each set.
Disclosed core touch: commit b47cc92 landed during the detention run. It changes `code/nury/rules.py` descriptions only; the modules were already loaded, so the run used c317050 code.
The shipped build differs only by a bounded retry on transient network errors; no prompt, rule, gate or threshold changed; commit PENDING (hack-jedi will give the id).
Judges: Jev judges, deterministic judges and human review score Nury's own words (the verse block is removed with `scripture.strip_block`; the verse is Scripture and is checked by `verse_block_verbatim`).
