# Observability: what Nury records about its own runs

Nury keeps three records. Each answers a different question, and none of them holds a family's words.

| Record | Question it answers | Holds text? | Where |
|---|---|---|---|
| **The audit log** | What happened in this one run, step by step? | One event only: `draft_rejected` (hidden from the pastor) | `AuditLog` in memory; a JSONL file if a path is set |
| **The run ledger** | How are runs behaving over time? | **Never** | `data/ledger/ledger.jsonl`, gitignored |
| **The case file** | What did the pastor approve? | Yes, approved text only; it is the pastor's record | `cases/`, gitignored |

This note is about the ledger. It is new, and it is built for an operator: someone who needs to know whether Nury is healthy without reading a family's case.

## What the ledger records

One JSON line per stage and one per run. Everything in a line is a number, a true or false, null, or a short id.

**Stage line** (`"type": "stage"`):

- `ts`: when, in UTC. `run`: a random 12-character run id.
- `playbook`, `stage`, `language`: which crisis, which stage, which family language.
- `status` (approved, edited, escalated, stopped, error), `escalated`, `attempts` (1 to 3).
- `rule_categories`: for each rule category that rejected a draft, how many times (for example `banned_phrase`, `language`, `jev_assumes_facts`). Categories are fixed names, never the text that matched.
- `jev`: for each Jev question, the decisions (`pass`, `uncertain`, `reject`, `unavailable`, `skipped`) and the highest and last probability.
- `jev_calls`, `jev_ms`: how many Jev calls and how long they took.
- `tokens_in`, `tokens_out`, `cost_usd`, `latency_s` (model time), `duration_ms` (wall time, if the app measured it).
- `skills`: names and versions, for example `voice@1.0.0`.
- `scripture_provider`: `bank` or `youversion`, on the pastoral stage.

**Run line** (`"type": "run"`): `ts`, `run`, `playbook`, `language`, `outcome` (`package_complete`, `stopped_by_pastor`, `escalated`, `blocked`), `failed_stage`, the number of stages, total attempts, tokens, cost, model latency, Jev time and calls, and `duration_ms` (monotonic).

## What it never records

- No draft, no intake, no approved text, no edit, no prompt, no model reply.
- No name, phone number, email, address, date of birth or ID, real or tokenized.
- No case id, case title or anything that maps a run to a family. The run id is random and is not stored in the case file.
- No pastor identity. There is no sign-in yet, so there is nothing to record.
- No API key, and no request or response from Gloo, Jev or YouVersion.

## How the ledger keeps that promise

1. **Fields are copied one by one.** A line is built from a fixed list. Nothing is passed through from the audit log or a result.
2. **Every string must be a short slug**: lowercase letters, digits, `_`, `.`, `-`, up to 40 characters. A sentence, a name with a space or a capital letter, or a phone number cannot pass. If anything fails the check, no line is written (it fails closed).
3. **A ledger failure never breaks a run.** The recorder returns False and the run goes on. The cost is a gap in the ledger, not a failed case.
4. **A leak test** (`code/tests/test_ledger.py`) runs a whole pipeline on an intake full of canary names, a phone, an email and an ID, with an unsafe draft containing a canary name forced into the correction loop. The rejected text is in the audit log, as designed, and is not in the ledger. It also checks that no value in any line contains a space.
5. **Append-only.** The file is only ever opened for append. A test checks that earlier bytes are unchanged after later writes.

What the slug rule cannot catch: a short, plain-looking word that is itself a name (for example, a playbook id named after a person). Playbook and stage ids are chosen by developers, not by families, and the tests check the real ones.

## How to read it

```
python3 -c "from nury import ledger; import json; print(json.dumps(ledger.summarize(since=86400), indent=1))"   # from code/
GET /api/ops?since=86400
```

`summarize(since)` returns: runs and cases (complete runs); cost per case and total cost; latency p50 and p95 per stage (model time plus Jev time); how many attempts stages took; the escalation rate (per stage and per run); the share of stages where each rule category fired; Jev decisions per question; and the Scripture provider mix. `since` is seconds back, a timedelta, a datetime or an ISO UTC time. Without `since` it reads everything.

Cost per case is only as good as the price in `NURY_PRICE_IN` and `NURY_PRICE_OUT` (Gloo, per 1M tokens). If they are unset, the cost fields are null and the summary says so. Jev's own cost is not included (public price: $0.042 per million input tokens, about $0.0003 to $0.0005 per case).

## How the app uses it

- `Recorder(playbook, language)` at the start of a run, `stage_done(result, audit.events)` after each stage, `finish(state.outcome)` at the end. Or `record_run(...)` once after a run.
- `app/ops_api.py` serves `GET /api/ops`. It is read-only and mounted the same way as the network API.

## Infrastructure that feeds it (added with Part B, 2026-10-07)

- **Event hook.** `AuditLog.subscribe(fn)` calls `fn(event)` after each event is recorded. A subscriber that raises is ignored, so it can never break a run. The ledger, a progress bar or a future ops stream can hang off it instead of re-reading the list.
- **Monotonic time.** Every audit event carries `t_ms`, milliseconds on a monotonic clock since the log was created. Subtract two `t_ms` values for a duration that does not depend on the wall clock.
- **Price table as data.** `code/nury/pricing.json` holds the model prices (input and output per 1M tokens), with a source and a date. The engine reads it; `NURY_PRICE_IN` and `NURY_PRICE_OUT` still override. A model that is not in the file has no cost (null): nothing is guessed. Each stage's metrics now record the `model` that answered. **Jev now has its public price in the file ($0.042 per million input tokens, output free, source and date included), and a `jev_cost_usd` helper computes the gate's cost from its input tokens. It is not added to a stage's cost: the Gloo cost stays separate (hack-jedi, commit ed66d99).**
- **Gloo retries.** `meta["http_retries"]` says how many times the same request was repeated after a 429, a 5xx or a dropped connection. It is not a draft attempt. The ledger does not yet record it.
- **CI.** `.github/workflows/ci.yml` runs the offline product and evaluation tests and a scan for key-like strings in tracked files. **It has not run**: there was no runner to try it on. Its actions are pinned to commit hashes and its runner to `ubuntu-24.04`; the Python packages it installs for the evaluation tests (pytest, PyYAML, markdown) are not pinned.

## What an operator would add next

Not built. Listed so nobody assumes it exists.

- **Alerts.** A threshold on the escalation rate, on Gloo retries (a rising count means Gloo is flaky), on `unavailable` Jev decisions (Jev is down and the gate is failing open), on a 402 from Gloo (credit gone), and on cost per case.
- **Retention.** A rule for how long lines are kept and where old files go. Today the file grows without limit.
- **Rotation and size.** Daily files, and a cap.
- **Dashboards.** A page that draws the summary over time, not just the latest totals.
- **Per-church views.** Needs sign-in and per-church separation first (both NOT BUILT). Until then the ledger is one pool.
- **Access record.** Who opened which case. This needs sign-in too, and it is a different record from this one.
- **Jev repeatability.** The same draft scored up to 0.12 apart between two passes. A scheduled re-score of a few stored drafts would show drift over time.
