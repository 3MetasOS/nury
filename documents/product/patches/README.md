# Hardening patch set (applied in commit 0ac365a)

Written 2026-10-07 by hack-jedi for hack-sensei. It answers the findings in `documents/product/CODE_REVIEW.md`. **Both patches were applied together in commit `0ac365a` on 2026-10-07** (hack-sensei approved), with the output cap added after in `0dbfebb`. The files stay here as the record of what was proposed. There are two patches, made against `main` and tested in a scratch clone, on `main` at `636d782`:

- `hardening-app.patch`: the web app and the case files (`code/app/server.py`, `code/app/network_api.py`, `code/app/static/index.html`, `code/nury/casefile.py`) plus 18 tests. **Safe to apply while the re-run is going**: the evaluation harness does not import `app/`. (`casefile.py` is used by the case-file checks; the change only sets file rights and an export option.)
- `hardening-core.patch`: `code/nury/gloo_client.py`, `privacy.py`, `guardrails.py` plus 5 tests. **Apply after the re-run ends**: the harness uses all three.

Each applies alone, and both together. Tested on a fresh checkout: app alone 288 tests (1 skipped, it needs core), core alone 275, both 293, all exit 0.

To apply:

```
git apply --check documents/product/patches/hardening-app.patch    # prints nothing when it fits
git apply documents/product/patches/hardening-app.patch
code/test.sh                                                        # expect 288 tests, OK (1 skipped)
# after the re-run:
git apply documents/product/patches/hardening-core.patch
code/test.sh                                                        # expect 293 tests, OK
```

To undo: `git apply -R` with the same file. No prompt, rule verdict, gate or threshold is touched. Together the patches change 7 existing files and add two test files (`code/tests/test_hardening_app.py` 18 tests, `test_hardening_core.py` 5 tests).

## What it does, finding by finding

| Finding | Change | Test |
|---|---|---|
| SEC-01 CSRF | `POST`, `PUT` and `DELETE` must send `Content-Type: application/json`. The `Origin`, when present, must be this server. | app: `Guard` (5 tests) |
| SEC-02 DNS rebinding | The `Host` header must be `127.0.0.1:<port>`, `localhost:<port>` or `[::1]:<port>`. `NURY_ALLOWED_HOSTS` adds more (a reverse proxy). | app: `Guard` |
| SEC-03 quadratic regex | `privacy._EMAIL` and `guardrails._EMAIL_IN_TEXT` use `LinearEmail`: same matches, linear time. Intake, revision note and edit are capped at 20,000 characters, protected names at 50 of 80 characters. | core: `EmailRegex` (3); app: `Limits` |
| SEC-04 limits and timeouts | Body at most 1 MB (413), bad or negative `Content-Length` is 400, a stalled client gets 408 after 30 s. | app: `Limits` |
| SEC-09 cost | At most 3 runs writing at once (429), 60 Gloo calls per run, 50 sessions, 4 hour session life. `NURY_MAX_OUTPUT_TOKENS` sets `max_output_tokens` (off by default, see below). | app: `Sessions`, `SessionBudget`; core: `Budget` (2) |
| SEC-10 headers | `X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy`, and a CSP (`default-src 'self'`, inline scripts and styles still allowed, `frame-ancestors 'none'`) on every response. | app: `Guard` |
| SEC-11 files | Case files 0600, case folders 0700, the export zip 0600 and removed after it is sent, `privacy-map.json` left out of the export unless `?include_map=1`. | app: `Files` (3) |
| COR-06 stage check | The decision request carries `stage`. A request for any stage but the draft that is waiting is refused with 409. The page sends the stage it is showing. | app: `Sessions` |
| COR-01 network API | A JSON list or a damaged file is a 400 or 500 answer, never a dropped connection. | app: `Limits` |
| COR-07 start errors | Any error while a run starts is a 500 with a plain message (no key name, no trace). | app: `Sessions` |
| SEC-13 inputs | `language` must be one the playbook lists. | app: `Limits` |

## How it was checked

- Product suite on a fresh checkout of `main` at `636d782`: app alone 288 tests (1 skipped), core alone 275, both 293 (270 plus 23 new), every run exit 0. Evaluation suite: 83 passed.
- **The regex change is exact.** `LinearEmail` was compared with the old patterns on 20,046 strings (every playbook file, the test drafts, and 20,000 random strings built to hit the edge cases): 21,145 matches, 0 differences, for `finditer` and `sub`. A first version using a lookbehind was NOT exact (it missed two emails written back to back); the test found it, and `LinearEmail` replaced it. A 40,000 character token takes 0.001 s now; it took 4.09 s.
- **Real browser, fake model.** `agent-browser` drove the patched app with a stub model: begin, confirm names, five Approve clicks in the page, save, export, then the other pages. All worked. From inside the page, a decision for the wrong stage got 409 and one with no stage got 400, a `text/plain` POST got 415.
- Not checked: Windows (file modes), a reverse proxy, a phone browser, any live call.

## Behavior changes you should know about

1. A script that POSTs without the JSON header now gets 415 (the app's own pages already send it).
2. The export no longer contains the real names behind the tokens. Add `?include_map=1` to the export link for the old behavior.
3. The Content-Security-Policy still allows inline scripts and styles, because the pages use them. It stops other sites' scripts, framing and outside connections, not injected inline script.
4. `max_output_tokens`: not switched on. I did not confirm that Gloo's endpoint accepts it (no live call was allowed). One live call with `NURY_MAX_OUTPUT_TOKENS=1500` will tell. A stage reply is 170 to 640 tokens.
5. A person with a run waiting at a gate does not count as busy. If three people write at once, a fourth gets "Nury is busy"; raise `NURY_MAX_BUSY` if that happens.

## Not in this patch (decide separately)

COR-02 (a contact name with `{{x}}` breaks the attorney stage: a prompt-rendering change), COR-03 (one damaged case file breaks the list), COR-05 (non-atomic network file), SEC-05 to SEC-07 (floor and check recall: they change what a check accepts), SEC-08 (`.env` loading), SEC-12, SEC-14, QA-01 (PyYAML in the test requirements). See the review.
