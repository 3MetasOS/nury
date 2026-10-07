# Nury demo video: storyboard and shot list (90 s)

Owner: hack-video. Status: DRAFT v1 for hack-sensei. VO wording to be agreed with hack-ninja.
Recording starts only when hack-sensei says the app works (expected Oct 7, ~15:00 MDT).

## Story in one line
At 2 AM a family calls their pastor after a detention. The pastor types what they said. Nury runs five stages, the pastor approves each one, and a message for the family is ready for the pastor to send by hand.

## Rules the video must show or respect
- Humanitarian, never political. No flags, no agency logos, no officers on screen, no party or policy words. The subject is a family and a night.
- Nury is not a pastor. Say it once in VO and once on screen.
- No send path. The final screen has Copy, not Send. VO says "Nury does not send. The pastor does."
- The pastor never sees an unsafe draft. The video shows the guardrail catching one as a status line only. The unsafe text is never on screen.
- Legal information only. The disclaimer is visible on every output shot.
- English UI. Spanish output for the family, set in the serif face.
- Demo family: use the names in `documents/prework/demo/demo_scenario.py` (Maria, Jose, two children). Time changed to 2:07 AM. No real people, no real phone numbers.

## Look
Source: `documents/prework/refugio.html` and PRODUCT.md. "Lantern in the dark."
- Background ink `#0d1015`, surface `#131824`, text `#ece7dc`.
- One accent: amber `#e8a33d`. Green and red only for approved and rejected chips.
- Fraunces (serif) for family words. Inter for chrome.
- Phone-first. Record a phone-width viewport (390 x 844) at 2x, placed on the ink background. No device frame.
- Motion: slow fades, one amber pulse on approve. No whooshes, no zooms past 110%.
- Audio: low warm pad, VO dry and steady. Phone buzz only in shot 1.

## Shot list

| # | Time | Visual | VO (draft) | On-screen text |
|---|---|---|---|---|
| 1 | 0:00-0:08 | Black. A phone lights up: 2:07 AM, "Maria" calling. One amber glow. | "It is two in the morning. A family is calling their pastor." | "2:07 AM" |
| 2 | 0:08-0:15 | Slow push on the Intake view, empty cursor. Pastor types the intake (sped up, 3x). | "Her husband was taken today. The pastor has no staff, and no lawyer on the line." | "Solo pastor. No staff. No lawyer." |
| 3 | 0:15-0:25 | Intake sent. Pipeline view: five-step stepper, step 1 lights amber. Triage card fills: situation, people, location, language, urgency, 3 missing facts. | "Nury turns the call into a clear case. Facts only. No advice." | "1 Triage" |
| 4 | 0:25-0:30 | Thumb taps Approve. Amber pulse. Stepper moves to step 2. Show Approve / Edit / Stop for one beat. | "After every stage, the pastor decides." | "Approve / Edit / Stop" |
| 5 | 0:30-0:44 | Rights brief streams in Spanish (serif). Each point carries a citation chip. Pause on one chip. | "Rights in the family's own language. Built only from a vetted source. Every point cited." | "2 Rights brief. Vetted sources only." |
| 6 | 0:44-0:56 | **Guardrail beat.** A status strip appears under the brief: "Draft rejected by guardrail. Regenerating (2 of 3)." Red chip, then green "Passed". No draft text visible. The clean brief replaces the card. | "Sometimes a draft crosses the line from information into advice. Nury rejects it and tries again. The pastor never sees it." | "Guardrail: rejected, regenerated. Max 3 tries." |
| 7 | 0:56-1:06 | Fast montage, 2.5 s each: Attorney resources (hotlines, church-vetted entries, no named attorney); Family checklist (DO TONIGHT / DO NOT DO / GATHER THESE DOCUMENTS). Two taps on Approve. | "Attorney hotlines. A checklist for tonight." | "3 Attorney resources" then "4 Family checklist" |
| 8 | 1:06-1:18 | Stage 5 card: the pastoral message, under 120 words, in Spanish, serif, large. Pastor edits one word (Edit), then Approve. | "And a short, warm message, in the pastor's hands to edit." | "5 Pastoral message" |
| 9 | 1:18-1:25 | Package view. Buttons: Copy, Download. No Send. Cursor circles the empty place where Send would be. Disclaimer line visible. A phone shows the pastor pasting into their own messages app. | "Nury is not a pastor, and it never sends. The pastor does." | "Nury does not send. The pastor does." |
| 10 | 1:25-1:30 | End card on ink. Amber lantern mark. | "Nury. The crisis-response agent for solo pastors." | "Nury", tagline, "Legal information only. Not legal advice." |

VO runs about 105 words. At a calm 150 wpm that is about 42 s of speech across 90 s. Silence is intentional.

## Screen-capture plan
- App: run from the repo `code/` app in Chrome. Resize the window to 390 x 844 (Claude in Chrome `resize_window`). Hide bookmarks and extensions. Dark system theme, Do Not Disturb on.
- Capture: macOS `screencapture -v` or ffmpeg `avfoundation` on the browser window, 60 fps, then cut to 30 fps. Record each stage as its own take.
- Live vs canned: take one fully live run (Gloo). Gloo latency will be slow, so record each stage separately and cut the waits. Keep a `--dry-run` run as backup footage.
- Guardrail beat (shot 6) needs a real rejection. Ask hack-jedi for a switch or a seeded scenario that forces one rejection on the Rights brief. Record the status strip, not the text.
- Capture the guardrail log to a file for BUILD_LOG proof. It stays off screen.
- Make a clean-state script: fresh session, same intake text, same time stamp, so retakes match.
- Keys: `GLOO_API_KEY` stays in the environment. Check every frame for keys, URLs with tokens, and terminal history before export.

## Tooling decision
- ffmpeg (installed at `/opt/homebrew/bin/ffmpeg`) for cut, speed ramps, crossfades, captions (burned-in SRT) and final encode. Scripted, so retakes rebuild in minutes. Fits the commit-small rule.
- Chrome plus `screencapture` for footage. No paid editor. No new installs.
- VO: scratch track now with macOS `say` for timing. Final VO needs a human voice. Ask Juan whether he will read it at the venue, or whether to use a TTS voice. Decision needed by Oct 7, 17:00.
- Spanish text is shown, not spoken. If hack-sensei wants a spoken Spanish line, a native speaker should check it.
- Export: 1920x1080 H.264 MP4, AAC, under 100 MB, with the phone view centered on ink. Also a 1080x1920 vertical cut if time allows.
- Captions on by default (judges may watch muted).

## Overnight plan (Oct 7 to 8)
- Top 25 is announced at midnight. Stand by from 23:00.
- hack-ninja supplies the 90 s finalist script. Re-time shots 1-10 to that script. Same footage, new VO and captions.
- Budget: 00:30 script in hand, 03:00 rough cut, 06:00 final cut, 07:30 upload to Google Drive, 08:00 give hack-sensei the link. Hard deadline 09:00 MDT.
- Keep raw takes and the ffmpeg script in `video/` so a re-cut needs no new recording.

## Open questions
1. Show a redacted reason on the guardrail strip (for example "reason: advice, not information")? Only if the app already has the category. Needs hack-jedi.
2. Who reads the VO? Juan, or TTS?
3. Does the pitch deck use the same family and intake? Keep them identical across deck and video (hack-ninja).
4. Is a 3-minute prelim version of the video wanted, or only the 90 s? (JUDGING.md lists both lengths.)
