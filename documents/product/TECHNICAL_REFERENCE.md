# Nury technical reference

For engineers. Exact facts, with file and line anchors. Written 2026-10-07 by hack-ninja from the code at commit `6a5de3d` and later (the learning-loop wiring in `ca6d9aa` included). hack-jedi fact-checked it the same evening: about 110 line anchors, the constants and defaults, and the environment table all matched; the corrections below come from that check and from three bug fixes made after I wrote it. Line numbers move; function and constant names will not.

**How each claim was checked.** Every row or paragraph carries one of these:

| Mark | Meaning |
|---|---|
| **run** | I ran it or ran a test and saw the result. |
| **test** | A named test in `code/tests/` proves it, and the offline suite passes (264 tests on 2026-10-07 evening, see section 11). |
| **code** | I read the code and did not run it. |
| **NOT VERIFIED** | I could not check it. Section 12 lists these in one place. |

Nothing here is written from memory or from another document. Where a document and the code disagree, the code wins and the difference is noted.

## Contents

1. [The Gloo client and the network retry](#1-the-gloo-client-and-the-network-retry)
2. [How the retry meets the correction loop, Jev and YouVersion](#2-how-the-retry-meets-the-correction-loop-jev-and-youversion)
3. [The audit log, the ledger and the price table](#3-the-audit-log-the-ledger-and-the-price-table)
4. [The Jev gate](#4-the-jev-gate)
5. [The YouVersion provider](#5-the-youversion-provider)
6. [The privacy pipeline](#6-the-privacy-pipeline)
7. [Error taxonomy](#7-error-taxonomy)
8. [Environment variable reference](#8-environment-variable-reference)
9. [Data folders and retention](#9-data-folders-and-retention)
10. [HTTP API reference](#10-http-api-reference)
11. [CI and test commands](#11-ci-and-test-commands)
12. [What I could not verify, and things to know](#12-what-i-could-not-verify-and-things-to-know)

## 1. The Gloo client and the network retry

File: `code/nury/gloo_client.py`. Added in commit `1e019ea`.

**The call.** `GlooClient.respond` (line 88 on) POSTs JSON to `{base_url}/responses` with `Authorization: Bearer <GLOO_API_KEY>` and `timeout=120` (line 102). Default base URL: `https://platform.ai.gloo.com/ai/v2/guarded` (line 54). Default model: `gloo-anthropic-claude-sonnet-4.6` (line 55). **code**

**The constants** (lines 20 to 23, **code**, tested):

| Constant | Value | Meaning |
|---|---|---|
| `MAX_TRIES` | 3 | Tries in all: the first call and at most 2 retries. |
| `RETRY_STATUS` | 429, 500, 502, 503, 504 | HTTP statuses that may be retried. |
| `RETRY_AFTER_CAP_S` | 10.0 | The most seconds a `Retry-After` header can ask us to wait. |
| `_QUOTA` | `insufficient_quota`, `insufficient_credit`, `quota exceeded`, `out of budget`, `billing`, `usage limit` | If a 429 body contains one of these (case-insensitive), it is not transient. |

**What is retried.** **test** (`tests/test_gloo_retry.py`)

- HTTP 429, 500, 502, 503 and 504, unless the 429 body matches `_QUOTA` (`retryable_status`, line 34).
- `requests.exceptions.ConnectionError` and `requests.exceptions.Timeout` raised by `requests.post` (the `except` at line 104). By the `requests` class hierarchy this also covers `ConnectTimeout`, `ReadTimeout`, `SSLError` and `ProxyError`. The tests use the two base classes. hack-jedi confirmed the subclass relationships by running Python: `SSLError`, `ProxyError`, `ConnectTimeout` and `ReadTimeout` are subclasses of `ConnectionError` or `Timeout`, and are retried; `InvalidURL`, `ChunkedEncodingError` and `TooManyRedirects` are not, as the list below says. **run** (hack-jedi), no test.

**What is never retried.** **test**

- **402** (no credit). It falls through to `raise_for_status()` and raises `requests.HTTPError`.
- **403**. This is the guardrail block, a safety answer. It raises `GuardrailBlock` at line 111 before any retry logic runs.
- **Any other 4xx** (400, 401, 404, 422 and so on). `raise_for_status()` raises `HTTPError`.
- **A 429 whose body names quota or billing.** Waiting does not help.
- Any `requests` exception that is not a `ConnectionError` or `Timeout` (for example `InvalidURL`, `ChunkedEncodingError`). It propagates at once. **code**

**The backoff.** `_wait(attempt, resp)` (line 42): the wait before try number `attempt + 1` is `NURY_GLOO_RETRY_BASE * 2 ** (attempt - 1)` seconds, base default 1.0. So the first retry waits **1 s** and the second waits **2 s**. **test** (`test_5xx_codes_are_retried_with_backoff_one_then_two_seconds`: waits recorded as `[1.0, 2.0]`).

- **There is no jitter.** The schedule is exact and the same for every caller. **code**
- **Retry-After.** If the response has a `Retry-After` header that parses as a number, that value replaces the backoff for that wait, capped at 10 s (line 51). It is a replacement, not an addition. A header that does not parse as a number, which includes an HTTP-date, raises a `ValueError` that is caught, so `ra` becomes None and the normal backoff applies (lines 48 to 50). **test** (`test_retry_after_is_honored_up_to_ten_seconds` covers the number form and a non-numeric value, `soon`); a real HTTP-date takes the same path but no test uses one. Retry-After is read only from a response, so a dropped connection or timeout always uses the backoff.

**The most it can wait.** Waits happen between tries, at most twice. Without `Retry-After`: 1 s + 2 s = **3 s**. With `Retry-After` on both: up to 10 s + 10 s = **20 s**. **code** (computed from the constants). Each try can itself last up to the 120 s `requests` timeout, which `requests` applies to the connect step and to each wait for data, so there is no deadline over the whole call. If every try hung until its timeout, one call could take about three times 120 s plus the waits, roughly 6 minutes. That worst case is computed from the code and **NOT VERIFIED** by running.

**When the tries run out.** The last error is raised exactly as it would have been without a retry: `HTTPError` for a bad status after `raise_for_status()`, or the original `ConnectionError` or `Timeout`. **test** (`test_after_three_tries_the_last_error_is_raised_as_before`, `test_the_engine_error_path_is_unchanged_when_the_tries_run_out`).

**What the call returns.** `(json, meta)`. `meta` holds `latency_s`, `input_tokens`, `output_tokens`, `model` and `http_retries` (the number of retries used, 0 to 2; line 126). **code**

- `latency_s` is measured from before the first try to after the last, using `time.monotonic()` (line 94). **It includes the failed tries and the backoff waits.** A call that retried twice reports a longer latency, with no separate field. **code**
- **`http_retries` is not logged anywhere.** A search of `code/` and `evaluations/` finds it only in `gloo_client.py` and its test. The engine does not copy it into the audit log, the stage metrics or the ledger. A retry is therefore invisible after the fact, except as extra latency. **code**

**Tests** (`code/tests/test_gloo_retry.py`, 11 tests, no network, sleeping recorded and not done): 429 then success; the 5xx codes with waits `[1.0, 2.0]`; three tries then the last error; dropped connections and timeouts; 402, 403 and other 4xx never retried; a quota 429 not retried; Retry-After honored to 10 s; a clean call has `http_retries` 0; the status rule itself; the engine error path unchanged; a retried call inside a stage is not counted as a draft attempt. **test**

## 2. How the retry meets the correction loop, Jev and YouVersion

**The correction loop (`engine.run_stage`, lines 221 to 288).** The loop is `for attempt in range(1, MAX_ATTEMPTS + 1)` with `MAX_ATTEMPTS = 3` (line 22). One loop pass is one draft attempt.

- **A transient HTTP error does not consume a draft attempt.** The HTTP retries happen inside one `client.ask` call, so a call that retries twice and then succeeds counts as one attempt. **test** (`test_a_retried_call_succeeds_inside_a_stage_and_is_not_counted_as_a_draft_attempt`).
- **An HTTP error that survives the retries ends the stage; it is not a rewrite.** The `except Exception` at line 239 logs `error`, sets the stage message to `Gloo call failed (<ExceptionName>). I'll handle this manually.`, and **returns at once**. The stage status stays `error`. It does not loop back for another attempt. **code**, **test** (`test_the_engine_error_path_is_unchanged_when_the_tries_run_out`)
- **A 403 does consume a draft attempt.** `GuardrailBlock` is caught at line 231, logged as `gloo_block`, counted as a self-correction, and the loop continues with a correction note. After three, the stage escalates. **code**, **test** (`GloLayer` tests in `test_core.py`)

**The privacy client's own extra calls.** `PrivacyClient.ask` (`privacy.py` line 392) can call the inner client up to **3 times** per draft attempt: once, plus up to `MAX_FIX_CALLS = 2` repair calls when the reply holds a token the map does not know (lines 403 to 413). Each of those calls goes through `GlooClient.respond` with its own retries. So one draft attempt can make up to 3 requests, and each can retry up to 2 times: the most is 9 HTTP tries for one attempt. **code**. The merged `meta` sums latency and tokens across the calls (line 406) but keeps `http_retries` from the last call only (line 418). **code**

**Jev (`jev_gate.py`).** Jev has **no retry**. One `requests.post` with `timeout=8.0` (line 38 and line 115). Any exception, any status other than 200 and any unusable answer is one failure. The gate then fails open (section 4). The Gloo retry code is not used for Jev. The Jev gate runs after the Gloo call and after the named checks, so a Gloo retry delays Jev; Jev's own 8 s timeout does not include Gloo's waits. **code**, **test** (`test_jev_gate.py`: timeout, HTTP 500 and garbage answers all complete the run)

**YouVersion (`scripture_providers.py`).** YouVersion has **no retry** either. Each of its two GETs per verse has `timeout=4.0` (line 137). Any failure raises `ProviderUnavailable`, and the engine falls back to the bank (section 5). **code**

**The two clocks.** The engine's `latency_s` and the Jev gate's `ms` are measured separately. Gloo's latency includes retries and waits. Jev's `ms` is reported on its own and added to `jev_ms`. They are not summed into one field. **code**

## 3. The audit log, the ledger and the price table

### The audit log (`code/nury/audit.py`)

- **What it is.** An in-memory list of events, plus an optional JSONL file if a path is given. **code**
- **In the app, it is in memory only.** `Session.__init__` creates `AuditLog()` with no path (`server.py` line 223), so the app's audit events are **not written to disk** and are lost when the server restarts or the session ends. The only code that writes an audit JSONL file is `code/tools/trace_run.py` (line 32). **code**
- **Each event** carries `ts` (wall clock, UTC, millisecond ISO string), `t_ms` (milliseconds on a monotonic clock since the log was created, rounded to 0.1) and `kind`, plus fields (lines 40 to 55). Subtract two `t_ms` values to get a duration that does not depend on the wall clock changing. **test** (`test_audit_hooks.py`: `t_ms` never goes backwards, and the file carries it).
- **`audit.subscribe(fn)`** (line 29) adds a listener and returns a function that removes it. After each event is recorded, `fn(event)` is called **outside the lock**, so a slow subscriber cannot block the log. A subscriber that raises is ignored; it can never break a run. The listener gets the event itself and must not change it. **test**
- **The event kinds the code can write** (counted by searching `audit.log("` in `code/nury` and `code/app`): `stage_start`, `stage_skipped`, `skills_off`, `skill_applied`, `dynamic_source`, `gloo_call`, `gloo_block`, `error`, `fault_injected`, `check`, `draft_rejected`, `escalated`, `scripture`, `scripture_trimmed`, `scripture_fallback`, `jev_gate_start`, `jev_gate`, `jev_call`, `gate`, `edit_check`, `outcome`. **code**
- **`draft_rejected` holds the rejected draft text** (the field `draft`, `engine.py` line 285), with `visible_to_pastor=False`. It stays in memory. `server.safe_event` (line 193) removes the keys `draft`, `detail`, `reasons` and `text` before an event reaches the pastor's screen, and reduces violations to their category. **code**, **test**
- **`gloo_block` holds up to 500 characters of Gloo's 403 response body** in its `detail` field (`gloo_client.py` line 111, `engine.py` line 232). It is in memory and removed by `safe_event`. **code**

### The run ledger (`code/nury/ledger.py`)

- **What it is.** An append-only JSONL record of how runs behaved, never of what they said. One line per stage and one per run, in `data/ledger/ledger.jsonl` (gitignored). `NURY_LEDGER_DIR` changes the folder. **code**
- **It holds numbers, bools, null and short slugs only.** A string must match `[a-z0-9_.\-]{1,40}` (`SLUG`, line 31) or the line is not written (`_check_clean`, line 148). So no draft, no intake, no name and no case id can be in it. It **fails closed**: a bad field means nothing is written. **test** (`test_a_string_that_is_not_a_slug_stops_the_write_and_nothing_is_written`, and a canary test across a real run with a rejection).
- **A ledger failure never breaks a run.** `stage_done` and `finish` catch every exception and return `False` (lines 176 to 190). **test**
- **Stage line fields** (`stage_line`, line 74): `type`, `ts`, `run`, `playbook`, `stage`, `language`, `status`, `escalated`, `attempts`, `rule_categories` (category to count), `jev` (per question: decisions, max and last probability, list of probabilities), `jev_calls`, `jev_ms`, `tokens_in`, `tokens_out`, `cost_usd`, `latency_s`, `duration_ms`, `skills` (name@version), `scripture_provider`. **code**
- **Run line fields** (`run_line`, line 115): `type`, `ts`, `run`, `playbook`, `language`, `outcome`, `failed_stage`, `stages`, `attempts`, `tokens_in`, `tokens_out`, `cost_usd` (null if any stage has no price), `latency_s`, `jev_ms`, `jev_calls`, `duration_ms`. **code**
- **The run id** is `uuid4().hex[:12]`, random and not derived from the case (line 44). **test**
- **Reading it back.** `summarize()` and `ops_view()` (lines 239 and 289) feed `GET /api/ops`. **code**

### The price table (`code/nury/pricing.json`, loader `pricing.py`)

- **Data, not code.** Prices are USD per 1,000,000 tokens (`per_tokens: 1000000`). **code**
- **`gloo-anthropic-claude-sonnet-4.6`:** input 3.0, output 15.0. Source: "Gloo models API, the pricing field, read by the team on 2026-10-06 (BUILD_LOG entry 16)". As of 2026-10-06. Note: "Cache pricing is not used. Recheck before relying on it: prices change." **code**
- **`gloo-anthropic-claude-sonnet-5.5`:** input 2.0, output 10.0, same source and date, "Listed for comparison. Nury does not run on it." **code**
- **Jev:** the file holds the public price, $0.042 per million input tokens, output free (docs.typesafe.ai/models, read 2026-10-07), with its source and date. The helper `jev_cost_usd` computes the gate's cost from its input tokens. The engine does not add it to a stage's cost (commit `ed66d99`). **code**, **test** (`test_pricing.py`)
- **A model not in the file has no cost.** `cost_usd` stays `None`; nothing is guessed. The loader refuses a model entry missing `input`, `output`, `source` or `as_of`. **test**
- **Override.** If both `NURY_PRICE_IN` and `NURY_PRICE_OUT` are set and numeric, they win over the table for every model (`pricing.cost_usd`, line 31). **test**
- **Cost formula.** `round((tokens_in * price_in + tokens_out * price_out) / 1_000_000, 6)`. **code**
- **The engine's cost** is the sum over attempts of the tokens reported by Gloo, priced with the model name Gloo returns in the response (`engine._cost`, line 131). Tokens from a failed HTTP try are not counted, because no response with usage came back. **code**

## 4. The Jev gate

File: `code/nury/jev_gate.py`. Hooked into the engine at `engine.py` line 266. **code**, **test** (`tests/test_jev_gate.py`, 15 tests)

**When it runs.** After a draft passes the floor and the named checks (`if not violations and stage.jev and jev_gate.enabled()`). It is on if `NURY_JEV_GATE` is `on`, `1`, `true` or `yes`; off if `off`, `0`, `false` or `no`; and, if unset, on only when `JEV_API_KEY` is non-empty (lines 82 to 89). **code**

**The request.** One `POST {JEV_BASE_URL}/v1/systemone` (default base `https://api.typesafe.ai`) per draft attempt, batching all of the stage's questions, with `Authorization: Bearer <JEV_API_KEY>`, `timeout=8.0` (lines 109 to 116). Each question is `{"type": "noul", "instructions": <wording>}` and may carry `criteria`. The model name is `JEV_MODEL`, default `jev-latest`. The `state` object holds the task, stage, language, the crisis the pastor chose, the pseudonymized intake, earlier approved text, vetted sources (cut to 20,000 characters, pseudonymized names only) and the draft (lines 134 to 147). **code**

**The reading.** Each question must come back with `type == "noul"` and a numeric `noul`, the probability of "yes". Any missing or non-numeric answer raises. **code**

**The lines** (`decide`, line 96; data in `REJECT_AT`, line 37):

| Probability of yes | Decision | Effect |
|---|---|---|
| at or over the question's line | `reject` | A violation with category `jev_<question>` and a plain reason. The draft is regenerated. |
| from 0.30 up to the line | `uncertain` | The draft passes. The audit logs `uncertain`. |
| below 0.30 | `pass` | Passes. |

The line is **0.50 for every question except `assumes_facts`, which is 0.60** (`REJECT_AT = {"assumes_facts": 0.60}`). `UNCERTAIN` is 0.30. `jev_gate.line(question)` returns the line. The 0.60 was set after seeing validation data; see `evaluations/validation/JEV_GATE_VALIDATION.md`. **code**, **test** (`0.6 rejects`, `0.49 passes`, `0.50 rejects`, `0.55 passes for assumes_facts and rejects for gives_legal_advice`).

**The fail-open rule** (`run`, lines 150 to 176). `run` never raises. Any exception inside it (no key, timeout, connection error, HTTP status other than 200, malformed or incomplete answer):

1. sets `case_state.jev_down = True`;
2. logs `jev_gate` with `question="*"`, `decision="unavailable"` and `reason="<ExceptionName>: <first 80 characters of the message>"`;
3. returns no violations, so the draft goes on under the floor and the named checks.

**Later stages of the same run skip the gate.** If `jev_down` is already set, `run` logs `jev_gate` with `decision="skipped"` (reason "an earlier Jev call failed in this run") and returns without a request. The flag lives on the `CaseState`, so a new run tries Jev again. **code**, **test**

**What Jev sees.** Only pseudonymized text. The intake, earlier approved text and the draft go through the case's own `Pseudonymizer`; the vetted sources go through it with `patterns=False` (names only, so vetted phone numbers and links stay readable). The token map is never sent. **test** (`test_privacy.py::test_the_jev_gate_requests_carry_tokens_never_names_or_the_map`: 15 canaries, none found, across all stages, a correction loop and a pastor edit that adds a new name).

**What is logged** per attempt: `jev_gate_start` (questions), one `jev_gate` per question (`probability` rounded to 3 places, `decision`), and `jev_call` (`ms`, `usage`). **code**

**Timing.** `ms` is measured with `time.time()` at lines 158, 163 and 168, which is the wall clock, not the monotonic clock. A wall-clock change during the call would distort `ms`. **code** (an observation, see section 12).

**Pastor edits are not gated.** The gate runs only on a model draft. An edited text is checked and flagged by `all_violations`, not sent to Jev (`engine.py` line 316). **code**

## 5. The YouVersion provider

File: `code/nury/scripture_providers.py`. **code**, **test** (`tests/test_scripture.py`, 41 tests; live runs 2026-10-07 in `evaluations/LIVE_COST_LOG.md`)

**When it is on.** `default_chain()` (line 175) returns `[YouVersionProvider, BankProvider]` when `YVP_APP_KEY` is set, otherwise `[BankProvider]`. A Bible id is read from `YVP_BIBLE_ES` and `YVP_BIBLE_EN`; a language with no id has no YouVersion version. The bank is always last, and the engine adds it if the chain lacks one (`engine._fetch_verse`, line 328). **code**

**The requests.** For each verse, two GETs to `https://api.youversion.com` with header `X-YVP-App-Key`, `Accept: application/json` and `timeout=4.0`: `/v1/bibles/{bible}/passages/{usfm}?format=html`, then `/v1/bibles/{bible}` for the version name and copyright (lines 140 to 158). What leaves the app: the key header, a Bible version id and a passage id such as `PSA.46.1`. Never a name, never case text. **code**

**The fallback conditions.** Each raises `ProviderUnavailable`, and `scripture_providers.fetch` (line 187) moves to the next provider, ending at the bank. **code**, **test**

| Condition | Where |
|---|---|
| No Bible id for the language, no `usfm` on the verse, or the verse's origin is `church` | line 155 |
| Any exception from the request (including a timeout) | line 144 |
| HTTP status other than 200 (this includes 429) | line 146 |
| A response that is not JSON | line 150 |
| The HTML holds a class Nury does not know (`verse_from_html` raises) | line 102 |
| No verse text after trimming | line 163 |
| No version name, or no copyright, so it could not be shown | line 165 |
| The verse is over the word cap (default 52) | line 167 |
| The bank entry has no text or reference (the bank itself) | line 126 |

**No retry, no cache.** One attempt per verse per provider. Nothing is cached, because no cache rule was found in the YouVersion docs (module docstring, lines 16 and 17). **code**

**The trimming rule.** The plain-text format puts a Psalm title before verse 1 and cannot drop it, so Nury asks for HTML and drops elements with a title or heading class (`d`, `s1` to `s4`, `ms`, `mr`, `r`, `sp` and others, lines 46 to 50), verse numbers and notes. Any class not on the keep or drop lists means "unavailable". The attribution keeps the provider's copyright text except lines holding an email address and a repeated second copyright block (`attribution`, line 106). This trimming is Nury's rule, not the provider's. **code**, **test**

**What is logged.** On success with dropped classes: `scripture_trimmed` (`dropped`, `raw_chars`). On any fallback: `scripture_fallback` (`provider` that answered, `reasons` list). On every verse: `scripture` (`verse` id and `provider`). The ledger records `scripture_provider`. **code**

**Fixed after I wrote the first version.** `fetch` now catches any exception from a provider, not only `ProviderUnavailable`, notes the provider and the exception name as the fallback reason, and moves to the next provider (`scripture_providers.py` lines 193 to 196, commit `6a5de3d`, with tests). A YouVersion answer of an unexpected shape, for example a list instead of an object, now falls back to the bank and is logged as `scripture_fallback` with the exception name. **code**, **test**

## 6. The privacy pipeline

File: `code/nury/privacy.py`. The engine takes `client=`, so the privacy layer wraps the Gloo client without changing the core. **code**, **test** (`tests/test_privacy.py`, 13 tests)

**Step by step, for one stage:**

1. **The pastor confirms protected terms.** `propose_terms(text)` (line 115) suggests capitalized words from the intake. The pastor ticks, adds and unticks (`POST /api/propose-terms`). The confirmed list is what counts. With `NURY_PRIVACY=off` the client is the plain Gloo client and nothing below happens. **code**
2. **A `Pseudonymizer` is built per session** with the confirmed terms (`make_client`, line 434; `Session.__init__`, `server.py` line 210). It holds `_tok` (value to token), `_val` (token to value) and per-type counters. **code**
3. **Vetted contact details are allowed through.** The church network's phones, links and emails, and the playbook's vetted phones and links, are stashed so later patterns cannot cut into them and are restored unchanged (`allow_network`, `allow_playbook`; `_allowed`, `_stash`, lines 194 to 195 and 274 to 275). **code**
4. **Outbound `pseudonymize(text)`** (line 254) replaces, in this order: emails, SSN-shaped IDs, A-numbers, receipt numbers (three letters and ten digits), case numbers after a cue word, five date forms (a date near a birth cue becomes `DOB`, otherwise `DATE`), street addresses (English, Spanish, PO boxes), 10-digit and 7-digit phones, then the pastor's protected terms. Tokens are `[PERSON_1]`, `[PLACE_1]`, `[PHONE_1]`, `[EMAIL_1]`, `[ADDRESS_1]`, `[DOB_1]`, `[DATE_1]`, `[ANUMBER_1]`, `[CASE_1]`, `[ID_1]` (`_TYPES`, line 20). The same value always gets the same token. **code**
5. **What goes where.** The user input is pseudonymized with patterns and names. The instructions (rules and vetted sources) are pseudonymized for names only (`patterns=False`, `privacy.py` line 397), so vetted phones and links stay readable. If any token is present, a fixed `PRIVACY:` note is appended to the instructions telling the model to copy tokens exactly (lines 315 to 317, 399 to 400). **code**
6. **The call.** `inner.ask(out_in, instructions=out_ins)`, which is `GlooClient.ask` with its retries (section 1). **code**
7. **Inbound `detokenize(text)`** (line 297) turns tokens back into real values. It repairs mangled tokens: `[PERSON 1]`, `PERSON_1` and `[person_1]` all resolve (`_BRACKETED` line 22, `_BARE` line 23). A token the map does not know is reported as unresolved. **code**, **test**
8. **Unknown tokens.** If any are unresolved, the client asks again with a note listing the valid tokens, **at most 2 more calls** (`MAX_FIX_CALLS = 2`, line 323; loop lines 403 to 413). If it still has unknown tokens, each becomes `[?]` so the pastor sees a gap at the gate, never a stray token (lines 414 to 417). **test**
9. **At the gate.** `wrap_gate` (line 370) protects names the pastor adds in an edit before the next stage runs: a suggested name that is mid-sentence and not already known becomes a protected term, logged as `edit_name_protected` in the client's own `events`. **code**, **test**
10. **The token map** (`ps.map()`, line 250) lives in memory for the session and is saved with a case as `privacy-map.json` (real values; `casefile.py` line 353). It is never sent to a model or to Jev. **code**

**The client's own events** (`PrivacyClient.events`, kept in memory, no values): `unknown_token`, `token_dropped`, `edit_name_protected`. They are not in the audit log. **code**

**What the leak test captures** (`tests/test_privacy.py`). It replaces `requests.post` with a stub that records every JSON body (`http.bodies`; Jev bodies separately in `http.jev_bodies`). The intake holds 15 canary strings (`CANARIES`, lines 23 and 24): names, a phone in two forms, an email and its domain, a street address, a date of birth, an A-number, a case number, and a name the pastor typed without protecting it. The test runs full pipelines on both playbooks, with a correction loop and a pastor edit, then asserts that no canary appears anywhere in any captured request body (case-folded), and that tokens (`[person_1]`) really did go out. TECH_CLAIMS 16 counts this as 6 request bodies times 15 canaries, 90 checks per playbook, 0 found. The same test class covers the Jev requests. **test**

**The honest limit.** It removes direct identifiers. Context ("14 years", "his workplace") can still hint at a person. Cities and states are kept on purpose. The unprotected-name case is covered only for names the pastor typed in an edit (step 9) and for names the pastor protected (step 2). **code**

## 7. Error taxonomy

Every failure mode the code handles, what the pastor sees, what is logged, and what the engine does. "Audit" means the in-memory audit log (section 3). "Pastor sees" is what the screen shows; the app never shows a rejected draft.

| # | Failure | What the pastor sees | What is logged | What the engine does | Checked |
|---|---|---|---|---|---|
| 1 | A draft fails the floor or a named check | A strip: the draft was rejected and is being rewritten (attempt n of 3). Never the draft. | `check` (passed false, violations, categories); `draft_rejected` (with the draft, hidden) | Regenerates with the reasons, not the text. Uses one attempt. | test |
| 2 | Jev scores a question at or over its line | Same as 1 | `jev_gate` (question, probability, `reject`); `check` with category `jev_<question>` | Same as 1 | test |
| 3 | Three failed attempts | "Nury could not produce a safe draft after 3 attempts. I'll handle this manually." and the vetted sources list | `escalated` (attempts, categories); outcome `escalated` | Stage ends, status `escalated`. The run stops. | test |
| 4 | Gloo returns 403 (guardrail block) | As 1 (attempt strip), then as 3 | `gloo_block` (category, `detail` up to 500 characters of the body, hidden from the pastor) | Counts as a failed attempt. If all three attempts are `gloo_block`, the outcome is `blocked`, not `escalated`. | test |
| 5 | Gloo 429, 5xx, a dropped connection or a timeout, then success within 3 tries | Nothing | Nothing. `http_retries` is in the call's metadata only; the stage latency includes the waits. | Retries after 1 s then 2 s (or Retry-After up to 10 s). Not a draft attempt. | test |
| 6 | The same, but all 3 tries fail | "Nury stopped. Nothing was sent." The stage message reads "Gloo call failed (HTTPError). I'll handle this manually." (the exception name varies) | `error` (stage, attempt, exception name only) | Stage status `error`; returns at once; the run stops. The outcome is `blocked`. | test |
| 7 | Gloo returns 402, or any other 4xx, or a 429 about quota or billing | As 6 | As 6 | No retry. `raise_for_status` raises `HTTPError`; then as 6. | test |
| 8 | Jev: no key, timeout (8 s), non-200, or an unusable answer | Nothing. The draft goes on. | `jev_gate` `question="*"` `decision="unavailable"` with a reason; later stages log `skipped` | Fails open. Later stages of this run skip the gate. | test |
| 9 | YouVersion unavailable (any condition in section 5) | A verse from the verified bank, with its own version name and copyright | `scripture_fallback` (reasons) and `scripture` (provider `bank`) | Falls back to the bank. | test |
| 10 | The model writes Scripture, names a verse not on the approved list, or the verse block does not match the source word for word | As 1 | `check` with categories such as `no_model_scripture`, `verse_block_verbatim` | Regenerates | test |
| 11 | The model reply holds a token the map does not know | Nothing, or a visible `[?]` gap at the gate if it still fails after 2 repair calls | The client's own event `unknown_token`, then `token_dropped` (not in the audit log) | Asks again up to 2 times | test |
| 12 | The pastor chooses Stop | "I'll handle this manually." | `gate` (action `stop`); outcome `stopped_by_pastor` | Stage and run end | test |
| 13 | The pastor edits and the edit would fail a check | The edit is kept | `edit_check` (warnings) | Flags, never blocks: the pastor owns the edit | code |
| 14 | An unexpected exception escapes `run_stage` (for example a bug in the engine, or the privacy layer raising) | "Nury stopped. Nothing was sent." (`s.error` is set) | None in the audit log. The ledger run line is written with the partial results. | `Session.work` catches `Exception` and sets `self.error` to the exception name; the run ends (`server.py` lines 286 to 293) | code |
| 15 | The ledger or the feedback file cannot be written | Nothing | Nothing | `record_*` and `stage_done` return `False`; the run goes on | test |
| 16 | Save a case before every stage is approved or edited | "Nothing was saved. Every stage must be approved or edited first." (HTTP 400) | None | `CaseError`, nothing written | code |
| 17 | `POST /api/run` for a crisis that is `soon`, unknown, or has a source still pending approval | "That crisis is not available yet." (HTTP 400) | None | `PlaybookError` is caught and the message is fixed, so the reason is not shown | code |
| 18 | `POST /api/run` with an empty intake | "Type what the family told you." (HTTP 400) | None | Refused | code |
| 19 | An unknown session id | `{"error": "no such session"}` (HTTP 404) | None | None | code |
| 20 | A gate decision when no gate is waiting | `{"ok": false}` | None | `decide` returns False | code |
| 21 | A request body that is not valid JSON, or valid JSON that is not an object, to any main-server POST route | `{"error": "The request was not valid JSON."}` or `{"error": "The request must be a JSON object."}` (HTTP 400) | None | `do_POST` wraps `_body()` in a `try` and checks the type (`server.py` lines 542 to 547, commit `23e5288`). Before that commit the connection was dropped with a traceback. | **run** (curl to `/api/propose-terms` with `{bad json` and with `[1,2]`) |
| 22 | The same to the network API (`/api/network...`) | `{"error": "that was not valid JSON"}` (HTTP 400) | None | Handled | code |
| 23 | An unknown route | `{"error": "not found"}` (HTTP 404) | None | None | **run** |
| 24 | A write to the demo network (`NURY_DEMO_NETWORK=1`) | "These are fictional demo contacts. They are read only." (HTTP 403) | None | Refused | code |
| 25 | `GLOO_API_KEY` missing (and no repo-root `.env`) | Unknown | Unknown | `GlooClient()` raises `RuntimeError("Set GLOO_API_KEY in the environment.")` while `Session.__init__` builds the client; `/api/run` catches only `PlaybookError`, so the `RuntimeError` would escape `do_POST` and drop the connection with a traceback (the 400 in row 21 covers only the body, not this) | **NOT VERIFIED**: my test could not reproduce it because the repo-root `.env` supplied a key |
| 26 | The server restarts | A running session is gone (HTTP 404 on its id). Saved cases remain. | None | `SESSIONS` is a dict in memory (`server.py` line 37); there is no persistence and no expiry | code |

**Outcomes** (`compute_outcome`, `engine.py` lines 354 to 379): `package_complete`; `stopped_by_pastor` (a stage was stopped); `blocked` (a stage ended in status `error`, **or** every rejection category was `gloo_block`); `escalated` (any other failure). **The `blocked` label covers two different causes: a Gloo guardrail refusal and a network or HTTP failure.** The audit log tells them apart (`gloo_block` versus `error`); the outcome does not. **code**

## 8. Environment variable reference

Every variable the code reads (searched `NURY_*`, `YVP_*`, `JEV_*`, `GLOO_*`, `PORT`, `AIM_*` across `code/` and `evaluations/`). **code**

**Keys come from the environment or from the repo-root `.env`.** `GlooClient.__init__` calls `load_env()` (`gloo_client.py` lines 58 and 81), which finds the first `.env` in the file's parent folders and sets each `KEY=value` line with `os.environ.setdefault`, so a variable already in the environment wins. This loads **every** variable in `.env`, including `JEV_API_KEY` and `YVP_*`, but only once a `GlooClient` has been built in the process. Keys are never written to a tracked file; `.env` is gitignored and `code/tools/scan_keys.py` checks tracked files in CI.

| Variable | Default | Read in | Effect |
|---|---|---|---|
| `GLOO_API_KEY` | none | `gloo_client.py:82` | Required to build a client. |
| `GLOO_BASE_URL` | `https://platform.ai.gloo.com/ai/v2/guarded` | `gloo_client.py:54` | Base URL of the Gloo guarded Responses endpoint. |
| `GLOO_MODEL` | `gloo-anthropic-claude-sonnet-4.6` | `gloo_client.py:86`, `evaluations/adapter_nury.py:16` | The model name sent. |
| `NURY_GLOO_RETRY_BASE` | `1.0` | `gloo_client.py:29` | Backoff base in seconds. An invalid value falls back to 1.0. Tests set it small. |
| `JEV_API_KEY` | none | `jev_gate.py:111`, `evaluations/judges/jev_judges.py:97` | Jev key. Without it the gate is off by default and the eval judges cannot run. |
| `JEV_BASE_URL` | `https://api.typesafe.ai` | `jev_gate.py:114`, `jev_judges.py:23` | Jev base URL. |
| `JEV_MODEL` | `jev-latest` | `jev_gate.py:106`, `jev_judges.py:104` | Jev model name sent. |
| `NURY_JEV_GATE` | unset | `jev_gate.py:84` | `on`, `1`, `true`, `yes` force it on; `off`, `0`, `false`, `no` force it off; unset means on only if `JEV_API_KEY` is set. |
| `YVP_APP_KEY` | none | `scripture_providers.py:179` | Turns the YouVersion provider on. |
| `YVP_BIBLE_ES`, `YVP_BIBLE_EN` | none | `scripture_providers.py:181` | Bible version id per language. A language with no id has no YouVersion version. |
| `NURY_PRIVACY` | `on` | `privacy.py:431` | `off`, `0`, `false` or `no` returns the plain client: no tokenization. For before-and-after comparison only. |
| `NURY_SKILLS` | `on` | `engine.py:115` | `off`, `0`, `false` or `no` turns skills off. |
| `NURY_FEEDBACK` | `off` | `feedback.py:53` | `on`, `sentences`, `1` or `true`: sentence mode. `counts`: strict mode. Anything else, including unset: off. |
| `NURY_FEEDBACK_DIR` | `data/feedback` | `feedback.py:58` | Where feedback files go. |
| `NURY_LEDGER_DIR` | `data/ledger` | `ledger.py:41` | Where the ledger goes. |
| `NURY_NETWORK_DIR` | `network` | `network_api.py:28` | Where the church network is kept (the server passes its own path for the engine; see section 9). |
| `NURY_DEMO_NETWORK` | unset | `network.py:206` | `1`: use fictional demo contacts, read only. |
| `NURY_ALLOW_PENDING` | unset | `playbook.py:72`, `scripture.py:86`, `tools/new_playbook.py` | `1`: allow sources and verses whose approval is pending. For tests and the new-playbook scaffold. Never in the app. |
| `NURY_FORCE_REJECTION` | unset | `engine.py:147` | `1`: inject one unsafe draft on the first stage after triage, once, in whichever playbook runs (`rights` in detention, `info` in hospital; `_fault_for`, `engine.py` lines 142 to 149, commit `6a5de3d`). |
| `NURY_TEST_ESCALATE` | unset | `server.py:228` | `1`: with the demo box ticked, the stage 2 fault repeats 3 times so the escalation path can be seen. Test only. |
| `NURY_PRICE_IN`, `NURY_PRICE_OUT` | unset | `pricing.py:34`, `tools/live_checks.py`, `evaluations/skills_ab.py`, `adapter_nury.py:20` | USD per 1M tokens. Both must be set and numeric; they then override the price table. |
| `NURY_ALLOW_EVAL_RUN` | unset | `app/evals_api.py:121,153` | `1`: allows `POST /api/evals/smoke`, which starts real Gloo and Jev calls and costs money. |
| `PORT` | `8080` (server), `8120` (standalone `network_api`) | `server.py:634`, `network_api.py:109` | Listening port. Both bind `127.0.0.1`. |
| `AIM_AGENT_ID` | unset | `evaluations/make_review_canvas.py:88` | Evaluation tooling only: finds the review canvas folder. |

## 9. Data folders and retention

**Relative paths depend on the working directory.** Several defaults are relative, so they resolve against the directory the process is started from, not the repo root. Start the server from `code/` (as `python3 -m app.server` expects) or set the directory variables. **code**

| What | Default path | Written by | Gitignored | Holds | Retention |
|---|---|---|---|---|---|
| Saved cases | `code/cases/<case_id>/` (the server's `CASES_ROOT`, absolute: `server.py` line 35) | `casefile.save_case` | yes (`cases/`) | `case.json`, `intake.md` (the intake **with real names**), one page per stage, `people.md`, `documents.md`, `timeline.md`, `log.md` (categories only), `nextsteps.svg`, and `privacy-map.json` (**the real values behind the tokens**). A revision is saved as `<id>-v2` beside the original. | **None.** No code deletes or expires a case. |
| Church network | `network/` relative to the working directory (`network.py:24`). Three places compute the path and they agree only when the server is started from `code/`: the engine's own network source (`engine.py` lines 96 and 104, default root `network`), the network screen's API (`NURY_NETWORK_DIR`, else `network`), and the session's privacy allow-list (`code/network`, `server.py` line 219) | `network.py`, `network_api.py` | yes (`network/`) | The pastor's contacts, notes and last-used dates; `.import.json` is a temporary file during an import | **None.** |
| Run ledger | `data/ledger/ledger.jsonl` relative to the working directory | `ledger.py` | yes (`data/`) | Numbers and slugs only (section 3) | **None.** Append-only; no pruning code. |
| Feedback | `data/feedback/feedback-YYYYMMDD.jsonl` relative to the working directory | `feedback.py` (when `NURY_FEEDBACK` is on) | yes (`data/`) | Sentence mode: changed sentences, tokenized, plus counts, tags and categories. Strict mode: counts and tags only. Never a whole draft or quoted Scripture. | `feedback.prune(days)` deletes old daily files. **Nothing calls it.** The suggested 30 days for sentence mode has not been reviewed. |
| Audit log | **Memory only** in the app | `AuditLog()` per session | n/a | Every event (section 3), including `draft_rejected` with the draft | Gone when the session or the server ends. Only `tools/trace_run.py` writes an audit file. |
| Learning candidates | `candidates/` at the repo root | people, by hand | **no, tracked** | Candidate files with status, evidence counts and a draft change | Kept in git |
| Evaluation results | `evaluations/results/` | the harness | **tracked** | Scorecards, runs, per-run audit files that **can include rejected draft text** (synthetic families only) | Kept in git |
| Keys | `.env` at the repo root | a person | yes (`.env`, `*.key`) | `GLOO_API_KEY`, `JEV_API_KEY`, `YVP_APP_KEY`, Bible ids | n/a |

**There is no encryption at rest and no per-church separation.** Cases, the network and the token map are plain files on the server's disk. Anyone who can reach the app can read every case through the API (section 10). **code** (`server.py` has no authentication). Retention for cases, the network and the ledger does not exist. A search for `prune` and `retention` in `code/nury`, `code/app` and `code/tools` finds only `feedback.prune`.

## 10. HTTP API reference

Source: `code/app/server.py` (class `H`, `do_GET` line 426, `do_POST` line 533, `do_PUT` line 420, `do_DELETE` line 423) and `code/app/network_api.py`. The server binds **`127.0.0.1`** (`server.py` line 636), uses `ThreadingHTTPServer`, has **no authentication**, and writes **no request log** (`log_message` is a no-op, so intake text stays out of logs). JSON responses carry `Cache-Control: no-store`. **code**

All routes below are committed. The server has 27 route branches since `ca6d9aa` (24 before the learning-loop wiring). **code**

### Pages and static files

| Method and path | Purpose |
|---|---|
| `GET /` | The app (`index.html`). |
| `GET /network` | The church network screen (`network.html`). |
| `GET /how-it-was-built` | The documentation page (built from `HOW_IT_WAS_BUILT.md` by `app/build_docs.py`). |
| `GET /observability` | The ops page. |
| `GET /improvement` | The learning-loop reviewer page. |
| `GET /<name>.html`, `.css`, `.js`, `.svg`, `/fonts/<name>.woff2` | Static files. Only names matching `^/(fonts/)?[A-Za-z0-9_-]+\.(html\|css\|js\|svg\|woff2)$` and existing in `code/app/static/` are served (`STATIC_OK`, line 33). Fonts are cached for 7 days. |

### The pastor's run

| Method and path | Purpose | Never returns |
|---|---|---|
| `GET /api/playbooks` | The crisis cards: id, title, description, status (`live` or `soon`). | Anything from a case. |
| `GET /api/playbook/<id>` | Plain-words detail of one playbook (stages, checks, sources). 404 `unknown playbook`. | Prompts' vetted text beyond the descriptions. |
| `GET /api/privacy` | `{"on": bool}`: whether tokenization is on. | |
| `POST /api/propose-terms` | Body `{"intake"}`. Returns names the pastor may protect. Empty when privacy is off. | |
| `POST /api/run` | Body `{intake, playbook, language, protected, demo_guardrail, revise}`. Starts a session on a background thread and returns `{"id"}`. 400 on an empty intake, an unavailable crisis, or a bad revision. **This starts real Gloo (and Jev) calls.** | The intake or any draft. |
| `GET /api/session/<id>` | The session view: stages, the gate, a progress phase, the audit **through `safe_event`**, the package once done (a package is one full run of the five stages; the app calls it a case), and the next-steps map. 404 `no such session`. | A rejected draft, a Gloo error body, or the token map. |
| `POST /api/session/<id>/decision` | Body `{action: approve\|edit\|stop, text}`. `edit` needs text. Returns `{"ok": bool}`. 400 `bad request`. | |
| `POST /api/session/<id>/save` | Saves the approved package as a case. 400 unless every stage is approved or edited. Returns `{id, version, path}`. | |
| `POST /api/feedback` | Body `{session, stage, chip}`. Records a reason chip when `NURY_FEEDBACK` is on and the chip is one of the five. Returns `{"ok": bool}`. | |
| `GET /api/features` | `{network, followup, feedback, consent_sentence, chips}`. The consent sentence and chips are non-empty only when `NURY_FEEDBACK` is not `off`. | |

### Cases

| Method and path | Purpose | Never returns |
|---|---|---|
| `GET /api/cases` | The list of saved cases with status, version count and the follow-up flag. | Case text. |
| `GET /api/case/<id>` | One case: its pages and versions. 400 `bad id`, 404 `case not found`. **This returns the pages, including the intake with real names.** | |
| `GET /api/case/<id>/export` | A zip of the case folder. | |
| `GET /api/case/<a>/compare/<b>` | A red and green diff of the two cases' stage pages. | |
| `POST /api/case/<id>/followup` | Body `{"value": true\|false}`. Sets or clears the follow-up flag only. 501 if the build lacks it. | |
| `POST /api/revision-preview` | Builds the intake for a revision from a saved case and the pastor's note. | |

Case ids must match `^[A-Za-z0-9._-]{1,80}$` (`CASE_ID`, line 36). **There is no per-user check: anyone who can reach the server can read any case.**

### The church network (`network_api.py`, mounted under `/api/network`)

| Method and path | Purpose |
|---|---|
| `GET /api/network` | The pastor's contacts and the church's home place. |
| `GET /api/network/export` | `{"entries": [...]}`. |
| `POST /api/network` | Add a contact (201). |
| `POST /api/network/home` | Set the church's city and state. |
| `POST /api/network/import` | Import entries (writes a temporary `.import.json`, then deletes it). |
| `PUT /api/network/<id>` | Update a contact. |
| `POST /api/network/<id>/used` | Mark a contact as used. |
| `DELETE /api/network/<id>` | Delete a contact. |

In demo mode (`NURY_DEMO_NETWORK=1`) every POST, PUT and DELETE returns 403 `These are fictional demo contacts. They are read only.` A body that is not valid JSON returns 400. `network_api.handle` never raises. **code**

### Observability and evaluation

| Method and path | Purpose | Never returns |
|---|---|---|
| `GET /api/ops` | The run ledger summary (`evals_api.ops()`; a stub built from stored evaluation runs when the ledger is empty, with a `source` line saying so). | Text, names or case ids. |
| `GET /api/evals` | The evaluation summary and the smoke-run estimate. | Draft text. |
| `POST /api/evals/smoke` | Starts a 3-scenario evaluation in the background (`run.py --agent nury --jev --only 01,09,12`). **Costs money.** 403 unless `NURY_ALLOW_EVAL_RUN=1`; 400 unless the body confirms `{"confirm": true, "estimate_usd": <the shown estimate>}`; 409 if one is running or another live job is found with `pgrep`. | |
| `GET /api/rules` | The rules table for the documentation page (`rules_info.rules()`). | |
| `GET /api/improvement` | The reviewer's view of the learning loop: the latest report's aggregate tables and the candidates' metadata. Shows the synthetic example, labelled, until a real report exists. | Any feedback line, draft or name. |

**Methods not listed return 404** `{"error": "not found"}`; `PUT` and `DELETE` are answered only for the network. **run** for the unknown-route 404. **A POST body that is not a JSON object returns 400** (row 21 of the error table). `GET /api/features` also returns `named_checks` (the registry count, read from the code; 20 on 2026-10-07). **run**

## 11. CI and test commands

**Product tests (offline, no network, no keys).**

```
code/test.sh                       # = cd code && python3 -m unittest discover -s tests
cd code && python3 -m unittest discover -s tests
```

`tests/nonet.py` removes the live keys from the environment and turns the Jev gate off for every test. Count on 2026-10-07 evening: **264 tests, OK** (3.3 s), run with `GLOO_API_KEY`, `JEV_API_KEY` and `YVP_APP_KEY` unset. **run**

| File | Tests | File | Tests |
|---|---|---|---|
| `test_core.py` | 53 | `test_casefile.py` | 11 |
| `test_scripture.py` | 41 | `test_official.py` | 10 |
| `test_learning_loop.py` | 19 | `test_ci.py` | 8 |
| `test_jev_gate.py` | 15 | `test_pricing.py` | 7 |
| `test_feedback.py` | 15 | `test_rules.py` | 6 |
| `test_ledger.py` | 14 | `test_new_playbook.py` | 5 |
| `test_privacy.py` | 13 | `test_audit_hooks.py` | 5 |
| `test_panel_fixes.py` | 15 | `test_network_api.py`, `test_add_a_rule_doc.py` | 2 each |
| `test_network.py` | 12 | `test_gloo_retry.py` | 11 |

(Counts are `def test_` per file, counted with grep; they sum to 264, the same as the suite's own count. (hack-jedi counted 259 earlier the same evening, before two more commits; always recount after the final commit.)) **run**, **code**

**Evaluation tests (offline).**

```
python3 -m pytest -q evaluations/tests
```

On 2026-10-07 evening: **77 passed**. Earlier the same day it was 74 passed and 1 failed: `test_ui_ids.py::test_built_page_is_current_with_its_source` caught a committed `how-it-was-built.html` older than its Markdown, until hack-artisans rebuilt it. That test is the staleness guard doing its job. The page is rebuilt with `cd code && python3 -m app.build_docs`, which hack-artisans runs before each commit. **run**

**The evaluation harness (live; spends money).** `python3 evaluations/run.py --agent nury [--jev] [--only 05,06] [--playbook detention|hospital] [--scenarios <folder>] [--out <dir>]` (flags in `run.py` lines 38 to 44). Needs `GLOO_API_KEY`; `--jev` needs `JEV_API_KEY`. About $0.10 of Gloo per scenario. **code**

**Learning-loop tools** (offline unless `--live`): `python3 code/tools/learning_report.py`, `python3 code/tools/candidates.py`, `python3 code/tools/candidate_test.py <candidate> --dry-run | --mock | --live --yes --repeat N`. **code**

**CI** (`.github/workflows/ci.yml`). Two jobs on `ubuntu-24.04`, Python 3.12, actions pinned to commit SHAs, `permissions: contents: read`, no secret and no key set. **code**, **test** (`test_ci.py` checks the pins, the runner and the absence of secrets)

1. `tests` (15 min limit): installs `code/requirements.txt` (`requests==2.32.5`) plus `pytest PyYAML markdown`, then `code/test.sh` and `python3 -m pytest -q evaluations/tests`.
2. `key-scan` (5 min limit): `python3 code/tools/scan_keys.py` fails if a tracked file holds a key-like string. It reports the file, line number and kind, never the value. Allowed fixtures are named with a reason.

**The workflow has not run.** The file says so: "This workflow has not run yet: there was no runner to try it on when it was written." **NOT VERIFIED** on a real runner.

**Dependencies.** Product runtime: the standard library and `requests` (pinned `requests==2.32.5`). Evaluation harness: `pytest`, `PyYAML`. Documentation build: `markdown` (python-markdown). `python-dotenv` is **not** used: `.env` is read by `load_env()` in `gloo_client.py`. **code** (imports searched across `code/` and `evaluations/`)

## 12. What I could not verify, and things to know

**NOT VERIFIED (no run, no test):**

1. The worst-case duration of one Gloo call (about three times the 120 s timeout plus waits). Computed from the code.
2. (Resolved by hack-jedi, who ran Python: the subclasses are retried. No test uses them.)
3. (Partly resolved: a non-numeric `Retry-After` is tested; a real HTTP-date is not, though it takes the same path.)
4. Behavior with `GLOO_API_KEY` missing (row 25). My test could not remove the key because the repo-root `.env` supplied one. By the code it escapes `do_POST` like malformed JSON.
5. (Resolved by `6a5de3d`: `fetch` catches any provider exception.)
6. The `1,000,000`-token price table values against Gloo today. They are as of 2026-10-06 and Gloo may change them.
7. The CI workflow on a real runner.
8. Whether `requests`' `timeout=8.0` for Jev can be exceeded by a slow-drip response. The `requests` documentation says a single value applies to the connect step and to each wait for data, so a response that sends a byte every few seconds could outlast 8 s in total. Not tested.

**Things an engineer should know** (read from the code; none is a safety defect on its own, but each is easy to trip over):

- A retried Gloo call is invisible in the audit log and the ledger. If you need to see retries, log `meta["http_retries"]` in `run_stage`. hack-jedi agrees this is a visibility gap and not a bug; the fix is two lines in `run_stage` plus a ledger field, and has not been made.
- The outcome `blocked` means either a Gloo guardrail refusal or a network failure. Use the audit (`gloo_block` versus `error`) to tell them apart. hack-jedi: the ledger and the ops page already map `blocked` to `error`, so it stays.
- The Jev gate measures its time with `time.time()`, not the monotonic clock, while the audit log uses the monotonic clock.
- (Fixed in `6a5de3d`: `NURY_FORCE_REJECTION` now targets the first stage after triage in whichever playbook runs.)
- Data folders for the ledger, the feedback files and the church network are relative to the working directory, and the church network path is computed in three places (section 9). They agree only when the server is started from `code/`. Run it from the same place every time, or set `NURY_LEDGER_DIR`, `NURY_FEEDBACK_DIR` and `NURY_NETWORK_DIR`. If they disagree, the network screen could save contacts in one folder while the engine reads another.
- (Fixed in `23e5288`: a malformed or non-object POST body returns 400. A missing `GLOO_API_KEY` is still unverified, row 25.)
- Sessions live in a dict in memory and never expire. Under load or over days the dict grows.
- The `draft_rejected` audit event holds the rejected draft. It never reaches the pastor's screen, but anything that dumps `audit.events` to disk or to a log would write unsafe draft text. Only `tools/trace_run.py` and the evaluation harness do that, with synthetic families.
- The evaluation results under `evaluations/results/` are tracked in git and can contain rejected drafts. They are synthetic.
- The triage prompts changed in commit `fe1fd7b` and the eight later-stage prompts of both playbooks each got one context line in commit `e4d19b6` (both pushed). Prompt text only; a test proves the line is in all eight (hack-jedi). The behavior described here does not depend on those prompts. The sets are being re-run, so recount tests after the final commit.
- **The ledger is wired.** `Session.__init__` creates a `ledger.Recorder` per run (`server.py` lines 240 to 241), calls `stage_done` after each stage (278) and `finish` at the end (290). Its lines go to `data/ledger` relative to the working directory. The server also calls `feedback.record_gate` (263), `record_outcome` (587) and `record_chip` (597) only when `NURY_FEEDBACK` is not `off`.
