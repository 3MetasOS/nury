# Technical story kit (deck, video, live Q and A)

Written by hack-ninja for Juan's ask: sell the engineering with proof. Plain words, exact claims, no hype.
**Status of the claims.** hack-jedi's `documents/TECH_CLAIMS.md` did not exist when I wrote this. Every claim below is tied to a file I read or a test I ran on 2026-10-07. Before export, match each row to TECH_CLAIMS.md: if a row is not marked VERIFIED there, cut it. Numbers that depend on the final scorecard are placeholders under the cut rule (Oct 7 16:00 MDT).

## 1. The 60-second technical story (spoken, about 160 words)
A pastor types what a family said. Before anything leaves the pastor's computer, a privacy layer swaps names, phones, emails, addresses and IDs for tokens. The request goes to Gloo AI Studio's guarded endpoint, which adds its own guardrails on the server.

Named checks read every draft: banned phrases, the disclaimer, links and phone numbers that must come from vetted sources, the language, the citations. If a draft fails, it is rejected and regenerated, up to three tries, then escalated. The pastor never sees the failed draft. Then the pastor decides: Approve, Edit or Stop. Nury sends nothing. The pastor copies the text.

We test it in four layers. Plain code checks, with no AI. Typed judges from the Jev decision API, my prior project, at evaluation time only. A red team of models from other makers, which catches problems but also flags safe text, so it only advises. And a person, who decides what the others cannot.

## 2. Claims, evidence and status
| # | Claim (what we say) | Evidence | Status |
|---|---|---|---|
| 1 | Names, phones, emails, addresses, dates of birth and IDs become tokens before a request leaves the computer. The map stays local and responses are restored locally. | `code/nury/privacy.py`; BUILD_LOG item 38 | Seen. Match to TECH_CLAIMS. |
| 2 | A leak test captures the exact request body at the HTTP boundary. A synthetic intake full of canary names and numbers goes through all five stages, detention and hospital, with a forced rejection and a pastor edit that adds a new name. Zero canaries appear in any request body, and tokens do go out. | `code/tests/test_privacy.py` (I ran it: 11 passed); BUILD_LOG item 38 | Verified by running the test. |
| 3 | The privacy layer costs about 4 to 5% more input tokens and about the same latency. | BUILD_LOG item 38: live A/B on three scenarios (01, 18, h01), off vs on | Seen. Small sample: say "on three scenarios". |
| 4 | Nury runs on Gloo's guarded Responses endpoint, which adds server-side guardrails to every request. | `code/nury/gloo_client.py`; `documents/prework/BUILD_DOC.md` section 4 | Seen. |
| 5 | Every draft passes named checks: banned phrases, the disclaimer, links and phone numbers that appear in the vetted sources or approved earlier text, language, cited bullets, required labels, no agency names. | `code/playbooks/detention/PROMPT_NOTES.md`; `evaluations/judges/deterministic.py` | Seen. Do not quote a count of checks unless TECH_CLAIMS gives one. |
| 6 | An unsafe draft is rejected and regenerated, up to three attempts in all, then escalated. The pastor sees the accepted draft only. | `documents/ARCHITECTURE.md`; BUILD_LOG; FAILURE_LOG | Seen. |
| 7 | After every stage the pastor chooses Approve, Edit or Stop. Later stages use the edited text. There is no send path. | `documents/ARCHITECTURE.md`; FAILURE_LOG (edit fix) | Seen. |
| 8 | Four evaluation layers: plain code checks, typed judges (Jev), a red-team panel of models from other makers, a person. | BUILD_LOG item on layers; `evaluations/README.md` | Seen. |
| 9 | The typed judge separates safe from unsafe. On a five-scenario smoke test, safe runs scored 0.17 to 0.30 and the same runs with one unsafe paragraph added scored 0.83 to 0.90. | `evaluations/validation/JUDGE_VALIDATION.md` | Seen. Say "smoke test, five scenarios". |
| 10 | The red-team panel caught 8 of 8 injected problems in its first validation pass, and it also flagged every safe review, so it advises and never gates. | `evaluations/validation/PANEL_VALIDATION.md` (the file says its raw data was overwritten; say "first pass") | Seen. |
| 11 | 121 tests pass offline in under a second (82 in `code/tests`, 39 in `evaluations/tests`). | I ran both suites on 2026-10-07 | Verified now. **Re-run at export:** the count changes. |
| 12 | Cost per run, latency per run, pass rate, drafts rejected and regenerated. | Final scorecard only | **Placeholder: [NUMBER]**. The interim scorecard has no total. Do not quote it. |
| 13 | The Jev decision API is used at evaluation time only, never in the product. It is the speaker's prior project, disclosed. | `CLAUDE.md` rule; submission text | Seen. |

## 3. Deck: where the story sits
- Slide 4, "How it is built": one diagram, names in text, no third-party logos. It shows the path in claim 1 to 7 and the evaluation strip.
- Slide 7, "Use of AI": the four layers, with the numbers from claims 9, 10 and 11. The numbers from claim 12 go on slide 8 when final.
- Slide 8: "what broke and what changed" stays as the proof of honesty.

## 4. Video: the tech beat (about 12 s)
Built by hack-video as an animated architecture shot. Text only, no third-party logos. Place it after the guardrail beat.

**TECH-A voiceover (30 words, about 12 s):**
> Names become tokens before anything leaves the pastor's computer. Gloo's guarded endpoint writes, and named checks reject unsafe drafts. Jev judges and a red team test it. A person decides.

**Three on-screen proof captions** (VERIFIED claims only; one per beat, about 3 s each):
1. "Leak test: canary names and numbers, zero in any request" (claim 2)
2. "Typed judge, five-scenario check: safe 0.17 to 0.30, unsafe 0.83 to 0.90" (claim 9)
3. "121 tests pass, offline" (claim 11; re-run at export and change the number if it moved)

**Disclosure caption, verbatim, small, on screen with the beat:** "The evaluation harness uses the Jev decision API (my prior project), disclosed as prior technology per the rules."
Lower-third labels already decided: "Built on Gloo AI Studio" and "Tested with Jev". TECH-B (the red team) is allowed now that the panel is validated, but only if there is time: "A red team from other model makers checks it too. It advises; a person decides."

## 5. Live Q and A: the five hardest technical questions
Say the short answer first. Give the limit before the judge finds it.

**1. Why not a bigger model?**
Short: The model is not what makes it safe. The checks, the gate and the human are. Nury's writer is `gloo-anthropic-claude-sonnet-4.6` through Gloo. A bigger model would cost more and run slower, and it would still need every check.
Honest: We did not run a bigger-model comparison. We could not make the model write legal advice on demand (it refused), so we test the checks with forced unsafe drafts instead. Cost and latency per run: [NUMBER] and [NUMBER] from the final scorecard.

**2. How do you know the guardrails work?**
Short: Four layers, and we say where each one fails. Plain checks are tested offline (121 tests today). A leak test captures the real outbound request. A typed judge separated safe from unsafe on a smoke test. A red team of other models and a person cover the rest.
Honest: The unsafe cases are synthetic, five scenarios is small, and the panel flags safe text too. We found and fixed real failures, and we list them in the deck. Pass rate on 20 hand-built scenarios: [NUMBER]. 18 attacker intakes written by a different model: [NUMBER, if run].

**3. What about hallucinated links?**
Short: Every link and phone number must appear in the vetted sources or in text the pastor already approved. There is no open web at runtime.
Honest: We shipped a bug. A made-up bare site such as "detentionlocator.org" passed the link check, because it only looked at text starting with http or www. We found it, fixed it to cover bare domains, and added tests. Emails with an unknown domain are now flagged too. The model once named a detainee locator that was not in our sources: the check rejected it three times and the stage escalated.

**4. What about personal information?**
Short: Names, phones, emails, addresses, dates of birth and IDs become tokens before a request leaves the computer. The map stays local. A leak test captured the real request body across all five stages: zero canaries.
Honest: It covers direct identifiers only. Context can still hint. A name the pastor did not protect is not removed. It cost about 4 to 5% more input tokens on three scenarios, and one pastoral message lost the family's name.

**5. What did Jev add that deterministic checks cannot?**
Short: Meaning. A banned-phrase list catches phrases we thought of. A typed judge answers a yes or no question about the whole run, such as "does any text give legal advice about this family's case?". On our smoke test it scored safe runs 0.17 to 0.30 and unsafe runs 0.83 to 0.90.
Honest: Our first wording scored every safe run 0.36 to 0.42, because vetted text like "do not sign anything without a lawyer" reads close to advice. We added explicit yes and no definitions. We have validated one question, not measured how stable verdicts are, and middle scores go to a person. Jev is my prior project, used at evaluation time only, and disclosed.

## 6. Rules
- Use only claims that TECH_CLAIMS.md marks VERIFIED. Cut the rest.
- Say "smoke test" and "first pass" where the file does. Do not round up.
- Final numbers (claim 12) only from the final scorecard. Otherwise the placeholder stays or the line is cut at 16:00 Oct 7.
- No hype words. No third-party logos.
