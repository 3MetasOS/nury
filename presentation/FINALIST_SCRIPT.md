# Nury: 90-second finalist script (video, due 09:00 MDT Oct 8)

For hack-video. Same family, intake and footage as `SHARED_DEMO.md` and `video/STORYBOARD.md`. Re-timed for three additions: "This is Nury" at the start, the technical beat (about 12 s), and the memorial as the last thing on screen (`MEMORIAL.md`). The video is at most 90 s total.
`[NUMBER]` = real scorecard number from hack-artisans only. The proof beat from the earlier cut is dropped: the tech beat's captions carry the numbers now.
**The memorial is gated: it ships only after Juan approves the text in writing.** Until then, use the version without it (end of this file).
Technical claims: `TECH_STORY.md`. Only rows that `documents/TECH_CLAIMS.md` marks VERIFIED go on screen.

## Re-timed shot list (sums to 90 s)
| # | Time | Visual | VO | On-screen text |
|---|---|---|---|---|
| 0 | 0:00-0:03 | The lantern lights (flame fades in, outline warms to amber). | none (optional: Juan says "This is Nury.") | This is Nury. then the brand line, smaller |
| 1 | 0:03-0:08 | Shot 1: phone lights up, 2:07 AM, Maria calling | "It is two in the morning. A family is calling their pastor." | 2:07 AM |
| 2 | 0:08-0:15 | Shot 2: intake typed | "Her husband was detained last evening. The pastor has no staff, and no lawyer on the line." | Solo pastor. No staff. No lawyer. |
| 3 | 0:15-0:22 | Shot 3: triage card | "Nury turns the call into a clear case. Facts only. No advice." | 1 Triage |
| 4 | 0:22-0:26 | Shot 4: Approve pulse | "After every stage, the pastor decides." | Approve / Edit / Stop |
| 5 | 0:26-0:34 | Shot 5: Spanish rights brief, citation chip | "Rights in the family's own language. Built only from a vetted source. Every point cited." | 2 Rights brief. Vetted sources only. |
| 6 | 0:34-0:43 | Shot 6: guardrail strip, no draft text | "When a draft crosses the line from information into advice, Nury rejects it and tries again. The pastor never sees it." | Rejected. Regenerating (2 of 3). Passed. |
| T | 0:43-0:55 | TECH BEAT: animated architecture shot (below). Text only, no third-party logos. | TECH-A (below) | Three proof captions, then the disclosure caption |
| 7 | 0:55-0:59 | Shot 7: attorney resources, checklist | "Attorney hotlines. A checklist for tonight." | 3 Attorneys, 4 Checklist |
| 8 | 0:59-1:04 | Shot 8: pastoral message, one edit | "And a short, warm message, in the pastor's hands to edit." | 5 Pastoral message |
| 9 | 1:04-1:09 | Shot 9: Copy, no Send; disclaimer | "Nury is not a pastor, and it never sends. The pastor does." | Nury does not send. The pastor does. |
| 10 | 1:09-1:11 | Shot 10: end card, lockup on ink | "Nury. The crisis-response agent for solo pastors." (if it does not fit 2 s, speak it over the first 2 s of the memorial card's fade) | Nury · Legal information only. Not legal advice. |
| 11 | 1:11-1:30 | Memorial card: light paper, deep-amber lantern, Fraunces. Slow fade. Nothing else on screen. | Juan, in his own voice (strongly recommended), slowly. | Juan's words, below, unedited |

Time check, VO: the 10 locked lines run about 45 s of speech at 150 words a minute. Slots are tight on shots 2 (7 s for 17 words) and 6 (9 s for 20 words). hack-video confirms against real footage and may borrow up to 1 s from shot 7 or the end card.
Time check, memorial: Juan's words are 45 words, about 18 to 22 s spoken with pauses. The card is 19 s. Do not shorten his words or speed him up. If Juan needs more time, take it from shots 5 and 6 before touching the memorial.

## Tech beat (T), about 12 s
Animated architecture shot by hack-video. Draw the same line as deck slide 4: pastor types, privacy layer, Gloo AI Studio guarded endpoint, named checks and the correction loop, approval gate, pastor sends. Then the evaluation strip. Text only, no third-party logos.

**TECH-A voiceover (30 words, about 12 s):**
> Names become tokens before anything leaves the pastor's computer. Gloo's guarded endpoint writes, and named checks reject unsafe drafts. Jev judges and a red team test it. A person decides.

**Three on-screen proof captions** (VERIFIED rows in `documents/TECH_CLAIMS.md` only, about 3 s each, one per step of the animation):
1. "Leak test: 90 checks per playbook, 0 found" (TC 16)
2. "Typed judge, ten checks: unsafe 0.89 to 0.98, safe 0.02 to 0.24" (TC 26)
3. "A full package: 50 to 56 s, about 9 cents" (TC 30)
Spare if there is room: "85 offline tests pass; no send path" (re-run the count at export).

**Disclosure caption, verbatim, small, on screen for the whole beat:** "The evaluation harness uses the Jev decision API (my prior project), disclosed as prior technology per the rules."
Lower-third labels: "Built on Gloo AI Studio" and "Tested with Jev". Optional TECH-B only if there is time: "A red team from other model makers checks it too. It advises; a person decides."

## Memorial text (Juan's words, unedited; do not change, shorten or humanize)
```
Nury is named for my aunt, Nury.
For 83 years she served her church in the small things and the big ones, always with a smile, always with Jesus in her heart.
She never married.
She passed away a month ago.
This is for her.
```
Open from Juan: her full name for "In memory of", years or omit, a photo only if he provides one, and who speaks it.

## Version without the memorial (use until Juan approves)
Same rows 0 to 10, then the end card holds from 1:09 to 1:30 (21 s) with the lockup and the brand line. The video is never longer than 90 s.

## Notes
- The Jev disclosure is on screen in the tech beat, in the submission text, and on the deck's proof slide.
- Check every frame for keys, tokens and terminal history before export.
- Brand rules (`branding/BRAND.md`): lantern upright, no glow, rays or gradients; deep amber on light, amber on ink.
