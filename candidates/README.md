# Candidates

A candidate is a proposed improvement to Nury: a prompt line, a rule, a Jev question or a scenario. It lives here as `<id>.md`
with a status: `proposed`, `tested`, `approved`, `released` or `rejected`.

- Nothing in this folder is applied by any script. The only way a candidate becomes real is a person writing their name and the
  date in the file, and a normal release (a commit) that makes the change.
- `python3 code/tools/candidates.py candidates` checks that every file is well formed.
- `python3 code/tools/candidate_test.py candidates/<id>.md --dry-run` shows what would change and runs nothing.
- The format and the loop are described in `documents/product/LEARNING_LOOP.md`.
- A worked example on SYNTHETIC data is in `documents/product/learning_example/`. No real pastor has used Nury, so this folder has no real candidates yet.
