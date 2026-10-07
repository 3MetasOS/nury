# Economics: what a package costs, and what could break it

Written 2026-10-07 by hack-ninja for hack-sensei. Sources: the final scored runs on build `9bc5c6d` (`evaluations/results/scorecard.md`, `evaluations/results/hospital/scorecard.md`), `evaluations/LIVE_COST_LOG.md`, `documents/product/TECHNICAL_REFERENCE.md` (constants) and hack-jedi's review note 3 (performance), quoted in BUILD_LOG entry 135. I did not see the note itself; its figures are marked "per review note 3". Prices are Gloo list prices for Claude Sonnet 4.6: $3 in and $15 out per million tokens, read 2026-10-06. This is arithmetic from small samples on synthetic families. It is not a forecast.

## 1. What a package costs today

A package is one run through five stages (triage, then four family-facing stages) with the privacy layer, the rules and the Jev gate on.

| Set (final build `9bc5c6d`) | Runs | Mean time per run | Tokens in / out | Cost, all runs | Cost per run |
|---|---|---|---|---|---|
| Detention | 20 | 34.2 s | 279,860 / 29,050 | $1.2753 | **$0.064** |
| Hospital | 8 | 49.5 s | 155,128 / 16,287 | $0.7097 | **$0.089** |
| Hostile intakes | 18 | 42 s | not split here | $1.51 | $0.084 |
| Network | 3 | 52 s | not split here | $0.27 | $0.09 |
| Case file | 5 | not recorded | not split here | $0.59 | $0.12 |

- **Range.** Review note 3 reports $0.063 to $0.126 per package across its sample. The scorecard means sit inside that range.
- **Per run in tokens.** Detention averages about 14,000 tokens in and 1,450 out. Hospital averages about 19,400 in and 2,000 out.
- **Input dominates tokens, not cost.** Input is about 90 percent of tokens. By cost it is about **66 percent** (computed from the detention and hospital totals above). Review note 3 says 72 percent on its sample. I could not reproduce 72 from the scorecards, so I use the numbers I can recompute.
- **Hospital costs more than detention** by about 39 percent per run ($0.089 against $0.064) and takes about 15 seconds longer. The reason I can show: hospital runs carry more input tokens (about 19,400 against 14,000). Why they carry more I did not investigate.
- **Order of magnitude.** At the scorecard means, 100 packages cost about $6.40 (detention) to $8.90 (hospital) in Gloo spend. 1,000 packages cost about $64 to $89. That excludes Jev, hosting, people and everything in section 3.

## 2. Where the time goes

Per review note 3: Gloo latency per stage has a median of **6.0 to 11.8 seconds**. Jev adds about **160 to 224 ms per draft**, about **3 percent** of the time. The stages run one after another because each reads the approved text of the stage before it, so five stages is roughly 30 to 60 seconds, which matches the scorecard means. Each Gloo call has a 120 second timeout in the code.

Two consequences:
- A pastor waits 30 to 50 seconds per package, plus however long they take to read and approve. The product is built around that wait, not around speed.
- Jev is cheap in time and in money (section 3.6).

## 3. What breaks the economics

Each item says what happens, how bad it could get, and what stands in the way today.

### 3.1 The retry loop, worst case
A stage can make several calls for one draft attempt. From the constants in the code: 5 stages × 3 attempts × 3 calls for privacy repair (the first call plus up to 2 repair calls) × 3 tries for HTTP errors (the first plus up to 2 retries) = **135 Gloo calls**, against 5 in the normal case. Jev adds up to 15 more calls (one per attempt, at most). That is up to 27 times the calls of a clean run. It needs every layer to fail every time, so it is a ceiling, not an expected value. The scored runs show corrections per run well below 1 and a handful of escalations.
- **Built:** the attempt limit (3), the repair limit (2), the HTTP retry limit (2) with a bounded wait (3 s without a `Retry-After`, up to 20 s with one), a Jev timeout (8 s) that fails open, and no retry on a 402.
- **Not built:** a cap on calls or dollars per package.

### 3.2 Long case summaries
Later stages read the approved triage text, so a long intake or long edits are paid for again in every later stage. I found no limit on intake length in the engine code, but my search was narrow, so check before you rely on that. A pasted email thread could multiply input tokens.
- **Not built (as far as I found):** an intake length limit.

### 3.3 The pastoral stage and the verse list
The pastoral prompt carries the approved verse bank so the model can choose a verse id. That list rides along on every pastoral attempt, including retries. The bank is 12 verses today and the cost is small. It grows if the bank grows.
- **Built:** the model chooses an id only; the engine inserts the text.
- **Not built:** sending only the verses that fit the situation.

### 3.4 A stage that never passes
A stage that fails all three attempts costs three full calls (plus repair calls) and ends in an escalation to the pastor, who gets nothing for that stage. Two scenarios do this on purpose or by habit: the unsafe-after-retries test (detention 06) and the legal-advice case (detention 02, three drafts rejected at 0.52 to 0.58). The hostile-intake set shows the pattern at scale: on build `c317050`, 11 of 18 intakes failed triage three times each. The run spends money and returns no package.
- **Built:** the limit of three attempts, so the cost of a failing stage is bounded.
- **Not built:** a cheaper path for a stage that is failing for the same reason on every attempt.

### 3.5 A shared key with no budget cap
Today Nury uses one Gloo key. Credit ran out twice during the build (HTTP 402). One heavy user, or one bug that loops, can end service for everyone. The app has no accounts, so there is also no per-church limit and no rate limit.
- **Built:** a cost log for every live run, a price table kept as data, and a ledger that records tokens, cost and latency per stage (`ledger.summarize()`, an ops endpoint that the app must mount).
- **Not built:** a per-key or per-church budget cap, quotas, alerts, or a switch that stops spending at a ceiling.

### 3.6 Jev is a rounding error
Jev's price is public: $0.042 per million input tokens, output tokens free, with rate limits of 100,000 tokens and 80 requests a second (https://docs.typesafe.ai/models, read 2026-10-07; a second page, flaviocopes.com/jev-pricing, says the same). From the audit files of the final scored runs, one package sends about 8,200 to 11,500 Jev input tokens (detention mean 8,220 over 20 runs; hospital mean 11,486 over 8; hostile intakes mean 9,510 over 18; median 5 gate calls per package; maximum 12,933). In short: about 10,000 Jev input tokens and four hundredths of a cent per package. hack-jedi computed the same from the same audit files (commit `ed66d99`, TECH_CLAIMS row 63). At $0.042 per million that is about **$0.0003 (detention) to $0.0005 (hospital) per package**, under 1 percent of the Gloo cost. This is an estimate from our own token counts, not a bill. Not checked: a billing page for our account, volume discounts, free-tier terms. Separate from price: **nobody on the team has read TypeSafe's data retention and terms for run-time use.** Jev sees tokens, not names, but the terms are unread.

### 3.7 Hosting and people are not included
Every figure above is the Gloo bill only. Not included: hosting, a database and storage, sign-in, encryption at rest, monitoring, backups, support, and the review of sources and drafts by an attorney or a native Spanish speaker. The app has no sign-in and no encryption at rest today, and a hosted product for many churches needs them (see `documents/FEATURES.md`).

### 3.8 Price drift
The price file says: "Cache pricing is not used. Recheck before relying on it: prices change." Prices were read once, on 2026-10-06. A different model changes every number here.

## 4. Mitigations, in one table

| Risk | Built | Not built |
|---|---|---|
| Retry loop | Attempt, repair and HTTP limits; bounded waits; no retry on 402; Jev fails open | A cap on calls or dollars per package |
| Long input | Nothing found | An intake length limit |
| Verse list | Id only; engine inserts the text | Sending only fitting verses |
| Stage that never passes | Three attempts, then escalate | A cheaper path for a repeat failure |
| Shared key | Cost log per run; price table; ledger | Budget caps, quotas, rate limits, alerts |
| Jev cost and terms | Fails open if down; price is public and tiny | A review of TypeSafe's terms and data retention |
| Hosting, people | Nothing | All of it |

## 5. What we still do not know

- The cost with real intakes. Every number comes from synthetic scenarios written by us.
- The cost of a pastor's second pass: an edit and a revision runs the pipeline again (a revision run cost about $0.15 to $0.16 in slot C of the cost log).
- TypeSafe's data retention and terms, and the cost of the red-team panel. The panel is a pre-release audit, not part of a package. I have not added its cost to the figures above.
- Whether 34 to 50 seconds is acceptable to a pastor at 2 AM. We have not asked one.
