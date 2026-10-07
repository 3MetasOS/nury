# Skills off vs on: reading (fill in after the run)

Run: <date, commit>. Command: `python3 evaluations/skills_ab.py`. Raw data: `runs.json`. Table: `summary.md`.
Scenarios: 1, 9, 13, 14, 20 (detention) and h01, h07 (hospital), skills off then on, privacy ON in both.

## What the numbers say (copy from summary.md, then read them)
- Stock phrases and dashes (off vs on): <n> vs <n>. A real effect needs the "on" count to be lower in most scenarios, not in one.
- Unsourced checklist tip lines: <n> vs <n>.
- Self-corrections and attempts: <n> vs <n>. Skills add checks, so a higher count with skills on is expected and is not a failure.
- Tokens and dollars per run: <n> vs <n>. Skills add prompt text, so input tokens rise a little.
- Runs that did not complete: <n> vs <n>.

## Does it help? Answer in one of three ways
1. Yes, by <how much>, shown by <which measure>.
2. Not measurably. The measures did not move. Say so, and say what we still believe and why that is only a belief.
3. It hurt, by <how>. Say what to change.

## What this test cannot show
- Seven scenarios, one run each. Model output varies from run to run; a difference of one or two is noise.
- The measures are deterministic word checks. They do not measure how natural the Spanish sounds. A native reader or a tone judge would.
- The skills were not tested against a tone judge (Jev) in this run.

## Next step if we continue
<one line>
