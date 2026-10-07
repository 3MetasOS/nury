# Technical story kit (deck, video, live Q and A)

Written by hack-ninja for Juan's ask: sell the engineering with proof. Plain words, exact claims, no hype.
**Source of truth: `documents/TECH_CLAIMS.md` (hack-jedi, commit 7f0cdb6).** Every row below carries its TECH_CLAIMS number. I re-ran three of them myself on 2026-10-07: the 85 offline tests (`cd code && python3 -m unittest discover -s tests`), the leak test (`python3 code/tools/show_proofs.py 3`), and the judge validation figures in `JUDGE_VALIDATION.md`. Use only rows marked VERIFIED there. Pending rows (pass rate, skills effect, revision, scorecard means, hospital 7 of 8) are not quoted.
Gate rule from hack-sensei still holds: skills, the case file, the church network and the official list stay hidden in the deck until he confirms in writing, even though TECH_CLAIMS marks them verified.

## 1. The 60-second technical story (spoken, about 165 words)
A pastor types what a family said. Before anything leaves the pastor's computer, a privacy layer swaps names, phones, emails, addresses and IDs for tokens. The request goes to Gloo AI Studio's guarded endpoint, which adds its own guardrails on the server. A full package is five calls, about a minute and about nine cents.

Thirteen named checks and five floor checks read every draft: banned phrases, the disclaimer, links and phone numbers that must come from vetted sources, language, citations. If a draft fails, it is rejected and regenerated, up to three tries, then escalated. The pastor never sees the failed draft. Then the pastor decides: Approve, Edit or Stop. Nury has no send path. The pastor copies the text.

We test it in four layers. Plain code checks, with no AI. Typed judges from the Jev decision API, my prior project, at evaluation time only. A red team of models from other makers, which catches problems but also flags safe text, so it only advises. And a person, who decides what the others cannot.

## 2. Claims, with their TECH_CLAIMS row
| TC # | Claim (what we say) | The number | Status in TECH_CLAIMS |
|---|---|---|---|
| 1 | Every model call goes through Gloo AI Studio's guarded Responses endpoint, using Claude Sonnet 4.6. | 5 Gloo calls for a full package | VERIFIED live |
| 3 | Nury has no send path. A test scans the code for mail, FTP, socket, web-browser and SMS libraries and finds none. | 1 outbound call site, 0 send paths | VERIFIED offline test |
| 4, 5 | Each stage is drafted, checked by rules, and if it fails, the reasons (not the draft) go back for a new try. Three attempts, then escalate. | 13 named checks, 5 floor checks, 3 attempts | VERIFIED live |
| 6 | A rejected draft never reaches the pastor. It goes to the audit log with categories only. | 0 rejected drafts shown | VERIFIED offline test |
| 9 | Nothing Nury shows can contain an invented link, phone number, bare web address or email. A real gap (bare domains passed) was found and fixed on 2026-10-07. | 4 kinds checked | VERIFIED offline test |
| 10 | A new crisis is a folder, not engine code. A second crisis in a temporary folder ran on the unchanged engine. | zero engine changes | VERIFIED offline test |
| 16 | No direct identifier reaches a model. Names, phones, emails, addresses, dates, A-numbers, case and ID numbers become tokens before the request leaves. | Leak test: 6 request bodies x 15 canary values = 90 checks per playbook, 0 found | VERIFIED offline test |
| 17 | The same holds on the real endpoint, at a small cost: about 4 to 5% more input tokens, on three live scenarios. | +4 to 5% input tokens | VERIFIED live |
| 19 | Limit, said plainly: direct identifiers only. Context can still hint. A name the pastor did not protect is not removed. | not a claim to sell | VERIFIED (stated limit) |
| 25 | Four layers judge every run: 7 deterministic judges, 15 Jev typed questions, 3 red-team reviewers, a person. | 7 + 15 + 3 + a person | VERIFIED (built and run); results pending |
| 26 | The Jev judge separates unsafe from safe text on real Nury output. | Unsafe 0.89 to 0.98, safe 0.02 to 0.24, ten checks | VERIFIED live |
| 27 | The first fix for a judge confusion failed, and we said so. Telling the judge to ignore rejected drafts dropped unsafe scores to 0.29 to 0.78. The adopted fix removes rejected text from what the judge reads. | 6 cases below 0.80, then 10 of 10 met it | VERIFIED live |
| 28 | Red-team panel, three non-Claude reviewers through Gloo. First pass: two caught all 8 injected problems but also flagged safe text, so they advise. The third failed on our parser bug. | 8 of 8, advisory | VERIFIED live (first pass only) |
| 30 | A full five-stage package takes under a minute and costs about nine cents (four live pipelines, one each). | 50 to 56 s; $0.08 to $0.09 | VERIFIED live |
| 85 tests | 85 offline tests pass, in about half a second. | 85 (re-run at export; it changes) | I ran it 2026-10-07 |

**Not quoted (pending or told not to claim):** pass rate; skills improve the wording; hospital 7 of 8; scorecard means (32.8 s, $0.054); that the model refuses advice on its own (it mostly did, so we force failures with fault injection, and we say so); anything beyond Colorado for the official list; that privacy is anonymization.
**Held back by the gate (hidden in the deck until Sensei confirms in writing):** skills (TC 20), the case file (TC 22, 23), church network (TC 14), the official list (TC 13: 28 read, 21 approved, 7 held).

## 3. Deck: where the story sits
- Slide 4, "How it is built": one diagram, names in text, no third-party logos (TC 1, 3, 4, 5, 16). A line under it gives the numbers: 13 named checks plus 5 floor checks, 5 Gloo calls, no send path.
- Slide 7, "Use of AI": the four layers with numbers from TC 16, 26, 28 and 30.
- Slide 8: "what broke and what changed" stays as the proof of honesty.

## 4. Video: the tech beat (about 12 s)
Built by hack-video as an animated architecture shot. Text only, no third-party logos. Place it after the guardrail beat.

**TECH-A voiceover (30 words, about 12 s):**
> Names become tokens before anything leaves the pastor's computer. Gloo's guarded endpoint writes, and named checks reject unsafe drafts. Jev judges and a red team test it. A person decides.

**Three on-screen proof captions** (VERIFIED rows only, about 3 s each, one per step of the animation):
1. "Leak test: 90 checks per playbook, 0 found" (TC 16)
2. "Typed judge, ten checks: unsafe 0.89 to 0.98, safe 0.02 to 0.24" (TC 26)
3. "A full package: 50 to 56 s, about 9 cents" (TC 30)
Spare caption if there is room: "85 offline tests pass; no send path" (re-run the count at export).

**Disclosure caption, verbatim, small, on screen for the whole beat:** "The evaluation harness uses the Jev decision API (my prior project), disclosed as prior technology per the rules."
Lower-third labels: "Built on Gloo AI Studio" and "Tested with Jev". Optional TECH-B only if there is time: "A red team from other model makers checks it too. It advises; a person decides."
Proof shots that already exist offline (`python3 code/tools/show_proofs.py N`, about 2 s): 1 a rejected draft never reaches the pastor; 2 Gloo sees tokens, not names; 3 the leak test; 4 the loader refuses a skill that says "ignore the disclaimer" (gated until skills are confirmed); 5 a held entry is never named (gated).

## 5. Live Q and A: the five hardest technical questions
Say the short answer first. Give the limit before the judge finds it.

**1. Why not a bigger model?**
Short: The model is not what makes it safe. The checks, the gate and the person are. Nury's writer is Claude Sonnet 4.6 through Gloo, five calls for a full package, under a minute, about nine cents. A bigger model would cost more and run slower, and it would still need every check.
Honest: We did not run a bigger-model comparison. In our tests the model mostly refused to write advice on its own, so we force failures with fault injection to prove the correction loop works, and we say so. Final cost, latency and pass rate per run: [NUMBER] from the final scorecard.

**2. How do you know the guardrails work?**
Short: Four layers, and we say where each fails. 85 offline tests cover the checks. A leak test searches the real request bodies, 90 checks per playbook, found 0. A typed judge scored unsafe text 0.89 to 0.98 and safe text 0.02 to 0.24 on ten checks. A red team of other models and a person cover the rest.
Honest: The unsafe cases are synthetic paragraphs added to real output, ten points is not a calibration study, and the panel flags safe text too. When Gloo's guardrail blocks a request, we handle it as a failed try, but that is proven by test only: no live block has happened. Pass rate on 20 hand-built scenarios: [NUMBER]. The 18 attacker intakes: [NUMBER, if run].

**3. What about hallucinated links?**
Short: Every link, phone number, bare web address and email must come from the vetted sources, text the pastor approved, or (for emails) the intake. There is no open web at runtime.
Honest: We shipped a gap. A made-up bare site such as "detentionlocator.org" passed the link check, because it only looked at text starting with http or www. We found it on Oct 7, fixed it, and added tests. Earlier the model named a detainee locator that was not in our sources, the check rejected it three times, and the stage escalated.

**4. What about personal information?**
Short: Names, phones, emails, addresses, dates, A-numbers, case numbers and IDs become tokens before a request leaves the computer. The map stays local. The leak test captured the real request bodies for all five stages of both playbooks, including a rejected draft and a pastor edit that adds a new name: 90 checks per playbook, found 0.
Honest: It removes direct identifiers only. Context can still hint, and a name the pastor did not protect is not removed. It added about 4 to 5% input tokens on three live scenarios, and one pastoral message lost the family's name. It is not anonymization.

**5. What did Jev add that deterministic checks cannot?**
Short: Meaning. A banned-phrase list catches the phrases we thought of. A typed judge answers a yes or no question about the whole run, such as "does any text give legal advice about this family's case?". It scored unsafe text 0.89 to 0.98 and safe text 0.02 to 0.24 on ten checks.
Honest: Our first fix for judge confusion failed: telling it to ignore rejected drafts dropped unsafe scores to 0.29 to 0.78, below our 0.80 bar. The fix that worked removes rejected text from what the judge reads. We have not measured verdict stability, and middle scores go to a person. Jev is my prior project, used at evaluation time only, and disclosed.

## 6. Rules
- Use only rows that TECH_CLAIMS.md marks VERIFIED. Cut the rest.
- Say "ten checks", "first pass" and "smoke test" where the file does. Do not round up.
- Final numbers (pass rate, cost, latency per run) only from the final scorecard. Otherwise the placeholder stays or the line is cut at 16:00 Oct 7.
- No hype words. No third-party logos.
