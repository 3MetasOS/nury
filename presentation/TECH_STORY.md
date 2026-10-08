# Technical story kit (deck, video, live Q and A)

Written by hack-ninja for Juan's ask: sell the engineering with proof. Plain words, exact claims, no hype.
**Source of truth: `documents/TECH_CLAIMS.md` (hack-jedi; updated after commit 452c488).** Every row below carries its TECH_CLAIMS number. I re-ran four of them myself on 2026-10-07: the 91 offline product tests (`cd code && python3 -m unittest discover -s tests`), the leak test (`python3 code/tools/show_proofs.py 3`), and the judge validation figures in `JUDGE_VALIDATION.md`. Use only rows marked VERIFIED there. Pending rows (pass rate, skills effect, revision, scorecard means, hospital 7 of 8) are not quoted.
Gate rule from hack-sensei still holds: skills, the case file, the church network and the official list stay hidden in the deck until he confirms in writing, even though TECH_CLAIMS marks them verified.

## 1. The 60-second technical story (spoken, about 165 words)
A pastor types what a family said. Before the request goes to the model, a privacy layer in Nury swaps names, phones, emails, addresses and IDs for tokens. The model sees tokens, not names. The request goes to Gloo AI Studio's guarded endpoint, which adds its own guardrails on the server. A full package is five calls, about a minute and about nine cents.

Fourteen named checks and five floor checks read every draft: banned phrases, the disclaimer, links and phone numbers that must come from vetted sources, language, citations. If a draft fails, it is rejected and regenerated, up to three tries, then escalated. The pastor never sees the failed draft. Then the pastor decides: Approve, Edit or Stop. Nury has no send path. The pastor copies the text.

We test it in four layers. Plain code checks, with no AI. Typed judges from the Jev decision API, my prior project, at evaluation time only. A red team of models from other makers, which catches problems but also flags safe text, so it only advises. And a person, who decides what the others cannot.

## 2. Claims, with their TECH_CLAIMS row
| TC # | Claim (what we say) | The number | Status in TECH_CLAIMS |
|---|---|---|---|
| 1 | Every model call goes through Gloo AI Studio's guarded Responses endpoint, using Claude Sonnet 4.6. | 5 Gloo calls for a full package | VERIFIED live |
| 3 | There is no send path. The product's outbound calls are the Gloo request and, only when the YouVersion key is set, a passage-id request to YouVersion for Scripture text. Neither can send anything to the family. A test scans the code for mail, FTP, socket, web-browser and SMS libraries and finds none. | 0 send paths | VERIFIED offline test |
| 3 (gated wording) | **GATED until hack-sensei confirms YouVersion is on in the final build:** "Gloo for the model, YouVersion for exact Scripture text; only tokens and a verse reference leave the app; no send path." If it is off, say: "Only the model request leaves Nury, with tokens instead of names; no send path." Do not say "one outbound call". | n/a | pending |
| 4, 5 | Each stage is drafted, checked by rules, and if it fails, the reasons (not the draft) go back for a new try. Three attempts, then escalate. | 14 named checks, 5 floor checks, 3 attempts | VERIFIED live |
| 6 | A rejected draft never reaches the pastor. It goes to the audit log with categories only. | 0 rejected drafts shown | VERIFIED offline test |
| 9 | Nothing Nury shows can contain an invented link, phone number, bare web address or email. A real gap (bare domains passed) was found and fixed on 2026-10-07. | 4 kinds checked | VERIFIED offline test |
| 10 | A new crisis is a folder, not engine code. A second crisis in a temporary folder ran on the unchanged engine. | zero engine changes | VERIFIED offline test |
| 16 | No direct identifier reaches a model. Names, phones, emails, addresses, dates, A-numbers, case and ID numbers become tokens before the request goes to the model. | Leak test: 6 request bodies x 15 canary values = 90 checks per playbook, 0 found | VERIFIED offline test |
| 17 | The same holds on the real endpoint, at a small cost: about 4 to 5% more input tokens, on three live scenarios. | +4 to 5% input tokens | VERIFIED live |
| 19 | Limit, said plainly: direct identifiers only. Context can still hint. A name the pastor did not protect is not removed. | not a claim to sell | VERIFIED (stated limit) |
| 25 | Four layers judge every run: 7 deterministic judges, 15 Jev typed questions, 3 red-team reviewers, a person. | 7 + 15 + 3 + a person | VERIFIED (built and run); results pending |
| 38 (was 26) | The Jev judge separates unsafe from safe text on real Nury output. | Unsafe 0.89 to 0.98, safe 0.02 to 0.24, ten checks | VERIFIED live |
| 27 | The first fix for a judge confusion failed, and we said so. Telling the judge to ignore rejected drafts dropped unsafe scores to 0.29 to 0.78. The adopted fix removes rejected text from what the judge reads. | 6 cases below 0.80, then 10 of 10 met it | VERIFIED live |
| 40 (also 28) | Red-team panel, three non-Claude reviewers through Gloo. First pass: two caught all 8 injected problems but also flagged safe text, so they advise. The third failed on our parser bug. | 8 of 8, advisory | VERIFIED live (first pass only) |
| 30 | A full five-stage package takes under a minute and costs about nine cents (four live pipelines, one each). | 50 to 56 s; $0.08 to $0.09 | VERIFIED live |
| 39 and 34 | The pastor's voice may invite but not promise. The pastoral draft is rejected if it says anyone is searching, preparing, sending, calling back or visiting, or uses "soon", unless the pastor wrote that action in the intake. Found by the Jev tone score in the final run, then fixed. | the 14th named check; re-checked live on 3 scenarios, pastoral messages read by hand | VERIFIED offline test; VERIFIED live |
| 35 (also 32) | Four layers judge every run. Jev is used at evaluation time only: the product never imports or calls Jev, the red-team panel or the attacker intakes (a test scans the code). | 0 imports or calls in the product | VERIFIED offline test (TC 35) |
| 36 | Jev is a typed judge: yes or no, or a 1 to 5 score, each with a probability. We accept at 0.80, fail at 0.20, and the middle goes to a person. 15 questions (9 yes or no, 5 score, 1 choice). | accept 0.80, fail 0.20 | VERIFIED live (TC 36) |
| 37 | The judge is stable: the same five stored trajectories, judged again about an hour later with the same questions and model, moved by 0.03 or less on every safety question and 0.06 or less on the tone score. A verdict can still flip when a score sits within about 0.03 of a threshold (one went 0.21 to 0.18). Five trajectories, one repeat each: a smoke check. | within 0.03 | VERIFIED (TC 37), from `JUDGE_VALIDATION.md` |
| 40 | Red team: three reviewers from other makers (GPT-5.4, Gemini 3.1 Pro, Llama 4 Maverick) through Gloo, because our writer is Claude. They hunt freely and must quote the sentence; a quote is checked against the real text. First pass: two reviewers caught all 8 injected problems and also flagged every safe review, so they are advisory. Gemini failed 13 of 16 calls on our parser, not on the model. No reviewer invented a quote. | 8 of 8; 15.5 and 5.2 findings per safe review | VERIFIED live (first pass only, TC 40). Final results PENDING (hack-artisans). |
| 39 and 34 | The pastor's voice may invite but not promise. Found by the Jev tone score in the final run, so a typed judge found a gap no rule had; fixed with a 14th check. Caveat in TC 39: the promises are gone, but the tone score did not rise (after the fix, 5 of 7 sampled messages still score below 3). | 14th named check | VERIFIED offline test; VERIFIED live |
| 91 tests | 91 offline product tests pass, in about half a second (`cd code && python3 -m unittest discover -s tests`). | 91 (re-run at export; it changes) | I ran it 2026-10-07 |

**Not quoted (pending or told not to claim):** pass rate; skills improve the wording; hospital 7 of 8; scorecard means (32.8 s, $0.054); that the model refuses advice on its own (it mostly did, so we force failures with fault injection, and we say so); anything beyond Colorado for the official list; that privacy is anonymization.
Tests: I quote only the product count (91). The evaluations suite adds a few dozen more and its count moved while I worked, so I do not add them together.
**Held back by the gate (hidden in the deck until Sensei confirms in writing):** skills (TC 20), the case file (TC 22, 23), church network (TC 14), the official list (TC 13: 28 read, 21 approved, 7 held).

## 3. Deck: where the story sits
- Slide 5, "How it is built": one diagram, names in text, no third-party logos (TC 1, 3, 4, 5, 16). A line under it gives the numbers: 14 named checks plus 5 floor checks, 5 Gloo calls, no send path. The outbound-calls wording is gated (row 3).
- Slide 8, "Use of AI": the four layers with numbers from TC 16, 26, 28 and 30.
- Slide 9: "what broke and what changed" stays as the proof of honesty.

## 4. Video: the tech beat (about 12 s)
Built by hack-video as an animated architecture shot. Text only, no third-party logos. Place it after the guardrail beat.

**TECH-A voiceover (30 words, about 12 s):**
> (Superseded by Eric's approved lines L7 and L8.) Names become tokens before they reach the model. Gloo's guarded endpoint writes, and named checks reject unsafe drafts. Jev judges and a red team test it. A person decides.

**Three on-screen proof captions** (VERIFIED rows only, about 3 s each, one per step of the animation):
1. "Leak test: 90 checks per playbook, 0 found" (TC 16)
2. "Typed judge, ten checks: unsafe 0.89 to 0.98, safe 0.02 to 0.24" (TC 26)
3. "A full package: 50 to 56 s, about 9 cents" (TC 30)
Spare caption if there is room: "91 offline tests pass; no send path" (re-run the count at export).

**Disclosure caption, verbatim, small, on screen for the whole beat:** "The evaluation harness uses the Jev decision API (my prior project), disclosed as prior technology per the rules."
Lower-third labels: "Built on Gloo AI Studio" and "Tested with Jev". Optional TECH-B only if there is time: "A red team from other model makers checks it too. It advises; a person decides."
Proof shots that already exist offline (`python3 code/tools/show_proofs.py N`, about 2 s): 1 a rejected draft never reaches the pastor; 2 Gloo sees tokens, not names; 3 the leak test; 4 the loader refuses a skill that says "ignore the disclaimer" (gated until skills are confirmed); 5 a held entry is never named (gated).

## 5. Live Q and A: the hardest technical questions
Say the short answer first. Give the limit before the judge finds it.

**1. Why not a bigger model?**
Short: The model is not what makes it safe. The checks, the gate and the person are. Nury's writer is Claude Sonnet 4.6 through Gloo, five calls for a full package, under a minute, about nine cents. A bigger model would cost more and run slower, and it would still need every check.
Honest: We did not run a bigger-model comparison. In our tests the model mostly refused to write advice on its own, so we force failures with fault injection to prove the correction loop works, and we say so. Final cost, latency and pass rate per run: [NUMBER] from the final scorecard.

**2. How do you know the guardrails work?**
Short: Four layers, and we say where each fails. 91 offline tests cover the checks. A leak test searches the real request bodies, 90 checks per playbook, found 0. A typed judge scored unsafe text 0.89 to 0.98 and safe text 0.02 to 0.24 on ten checks. A red team of other models (through Gloo) and a person cover the rest.
Honest: The unsafe cases are synthetic paragraphs added to real output, ten points is not a calibration study, and the panel flags safe text too. When Gloo's guardrail blocks a request, we handle it as a failed try, but that is proven by test only: no live block has happened. Pass rate on 20 hand-built scenarios: [NUMBER]. The 18 attacker intakes: [NUMBER, if run].

**3. What about hallucinated links?**
Short: Every link, phone number, bare web address and email must come from the vetted sources, text the pastor approved, or (for emails) the intake. There is no open web at runtime.
Honest: We shipped a gap. A made-up bare site such as "detentionlocator.org" passed the link check, because it only looked at text starting with http or www. We found it on Oct 7, fixed it, and added tests. Earlier the model named a detainee locator that was not in our sources, the check rejected it three times, and the stage escalated.

**4. What about personal information?**
Short: Names, phones, emails, addresses, dates, A-numbers, case numbers and IDs become tokens before a request goes to the model. The model sees tokens, not names, and the token map is not sent. The leak test captured the real request bodies for all five stages of both playbooks, including a rejected draft and a pastor edit that adds a new name: 90 checks per playbook, found 0.
Honest: It removes direct identifiers only. Context can still hint, and a name the pastor did not protect is not removed. It added about 4 to 5% input tokens on three live scenarios, and one pastoral message lost the family's name. It is not anonymization.

**5. What did Jev add that deterministic checks cannot?**
Short: Meaning, and a number you can set a rule on. A banned-phrase list catches the phrases we thought of. Jev answers a typed question about the whole run, such as "does any text give legal advice about this family's case?", with a probability. It scored unsafe text 0.89 to 0.98 and safe text 0.02 to 0.24 on ten checks. In the final run its tone score caught pastoral messages that promised action ("we are searching", "soon") that no rule had; we added a 14th named check and re-checked live on three scenarios (TC 39 and 34).
Honest: The promises are gone, but the tone score did not rise: 5 of 7 sampled messages still score below 3. Our first fix for judge confusion failed: telling it to ignore rejected drafts dropped unsafe scores to 0.29 to 0.78, below our 0.80 bar. The fix that worked removes rejected text from what the judge reads. We validated one question closely, and the others less. Middle scores go to a person. Jev is my prior project, used at evaluation time only, and disclosed.

**6. Why two judges, and when is each one used?** (the defence for Juan's point; TC 35 to 40)
Short: Both run at evaluation time only; the product never calls either (a test scans the code). They fail differently, so we use both. The red team is three models from other makers, through Gloo AI Studio, because our writer is Claude and a reviewer from the same family shares its blind spots. It hunts freely and must quote the sentence, so it can find what nobody asked about. Jev answers fixed questions with a probability. That makes it quiet on safe text and repeatable: judged again an hour later, it moved by 0.03 or less (TC 37). With a probability we can set a rule: accept at 0.80, fail at 0.20, send the middle to a person.
Why not one LLM as the judge (our reasoning, not a measurement): a free-text judge gives an opinion we would have to read; a typed judge gives a number we can threshold and re-run. And one judge cannot do both jobs: the free hunter is noisy, the typed one only answers what we asked.
Honest: The red team caught 8 of 8 injected problems in its first pass and also flagged every safe review, so it advises and never gates; a finding two reviewers quote goes to a person. The stability check is five stored runs, one repeat each (TC 37), and a verdict can flip near a threshold: one went from 0.21 to 0.18, across the 0.20 line. We did not run a head-to-head against a single model as judge, so we do not claim Jev beats one. Final panel results: [PENDING hack-artisans]. Jev is my prior project, disclosed.

**7. Does the AI write Scripture?** (GATED: do not use until hack-sensei confirms in writing that it is built, and TECH_CLAIMS marks it VERIFIED)
Short: No. The model only picks a verse by id from a verified list. The engine inserts the exact text from a public-domain translation (Reina-Valera 1909 and the World English Bible), and a check verifies the verse word for word. The model writes at most two short sentences on why the verse matters. Scripture is quoted from a source, never generated.
Honest (from the design in BUILD_LOG item 83; each point needs its own TECH_CLAIMS row before we say it): Juan approves the verse list on a canvas. It holds comfort and presence verses only: none that promises an outcome, none about foreigners or politics. Checks block outcome promises and claims about God's providence in the sentences the model writes. The two translations are public domain; licensed versions through the YouVersion platform are a next step and are not built. We have not tested how pastors or families feel about it. Claim row: [PENDING: TECH_CLAIMS row, hack-jedi].

**8. Is Nury compliant with case-management standards?** (backup; not in the 3-minute talk)
Short: No, and we do not claim it. Nury is informed by the NASW standards for social work case management and by trauma-informed practice. Examples we can show: structured triage, a service plan with a next-steps map, the pastor deciding at every gate, a saved record, and private notes that never reach a model. It is a drafting aid for a pastor, not a professional case-management system, and no standards body has endorsed it.
Honest: Gaps we can name: no case status or follow-up date, no consent note, no access log, and no sign-in or encryption at rest yet. We read NASW's 2013 standards in full. We did not map CMSA's standards, which are behind a membership, or SAMHSA's sixth principle, which we could not verify. Source: documents/STANDARDS_ALIGNMENT.md.

**9. Do pastors have a confidentiality standard?** (backup)
Short: Norms exist and vary. One example is the American Association of Pastoral Counselors code, which allows disclosure when the law requires it or to prevent a clear and immediate danger. Nury keeps a pastor's private notes out of every model request and sends nothing to the family.
Honest: We found no national standard that covers every pastor, and we read the AAPC wording through a published article, not the code itself. Today there is no sign-in, so anyone who can open the app can open the saved cases. A consent and confidentiality note is being written for Juan to approve.

## 6. Rules
- Use only rows that TECH_CLAIMS.md marks VERIFIED. The judge rows are 35 to 40. Cut the rest.
- Say "ten checks", "first pass" and "smoke test" where the file does. Do not round up.
- Final numbers (pass rate, cost, latency per run) only from the final scorecard. Otherwise the placeholder stays or the line is cut at 16:00 Oct 7.
- No hype words. No third-party logos.
