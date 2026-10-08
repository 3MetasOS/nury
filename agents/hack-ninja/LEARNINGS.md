# LEARNINGS: hack-ninja (Presentation)

Written 2026-10-08 by hack-ninja for the next agent or skill that has to do this job. It comes from my commits (about 145 carry the hack-ninja trailer), my messages and my memory notes from the Gloo AI Hackathon, October 6 to 8, 2026. Plain words. No keys, no personal data.

## 1. Role and what I was asked to deliver
**Role:** Presentation. I reported to hack-sensei (coordinator) over AMP. Juan Peláez owned the product and made the final calls.

**What I delivered, in `presentation/` unless noted:**
- The deck (`deck.html`, built from `deck_template.html` by `build_deck.py`): first all of it, later only the words and claims. In the end hack-artisans owned the visual design and I owned the words.
- The 250-word description, in two versions (`description_two_playbooks.txt`, `description.txt`), kept at 246 words or fewer by the strictest count.
- The 3-minute pitch (`PITCH_SCRIPT.md`), the finalist script and audio script (`FINALIST_SCRIPT.md`, `FINALIST_AUDIO_SCRIPT.md`), the presenter card (`PRESENTER_CARD.md`), the deck copy file (`DECK_COPY.md`), the short deck copy (`SHORT_TRACK.md`, `short/COPY_1_2.md`).
- The submission form text (`SUBMISSION_FORM.md`, page `submission_form.html` from `build_submission_html.py`).
- Documents that grew out of the job: `documents/product/ALIGNMENT_AUDIT.md` (one table of verified facts), `ABOUT_PAGE.md`, `HOW_IT_WAS_BUILT.md`, `WHAT_DID_NOT_WORK.md`, `PATTERN.md`, `ECONOMICS.md`, `COMMIT_DATES.md`, `README.md` (public rewrite).

## 2. How I actually worked: procedures that worked
**A. Start of every task**
1. Read the message in full with `python3 -c` on the inbox JSON (the notification text is cut). Mark it read with `amp-read.sh <exact id>`. A guessed or shortened id does not register and the stop hook keeps nagging.
2. `git fetch -q origin && git merge --ff-only origin/main` before editing. Never autostash: other agents have uncommitted edits in the same tree.
3. Check `git status --short <my paths>` for other agents' uncommitted edits before any build that rewrites a shared file.

**B. A fact goes in a document only from one table**
1. Keep one table of facts with the source file for each (`ALIGNMENT_AUDIT.md`). Write claims last, from that table.
2. Before reporting a number, read it from the source (scorecard, code, audit file), not from another document. Copied numbers drift: "14 checks" was really 20, "41 commits" was really 93, "264 tests" was 336.
3. Scan all text for old patterns after any change to a fact: `grep -rIn` for the old number, old names, "package", "pass rate", "terms". A clean scan means no known stale fact. It cannot find a new false claim.

**C. The deck build and check (the loop that worked)**
1. Edit `deck_template.html`. Run `python3 presentation/build_deck.py`.
2. Run `sh presentation/fit_check.sh`. It loads the deck in exact-size iframes (1280x720, 1920x1080, 390x844) over a local server on port 18150, in the default and `?gated` views, and prints overflow problems. It kills its server by port.
3. Take a real screenshot with `agent-browser` and LOOK at it: `agent-browser open "file://$PWD/deck.html#<slide-name>"`, `agent-browser set viewport 1280 720`, `agent-browser screenshot /tmp/x.png`, then read the image. The fit check cannot tell you a slide is crowded or unclear.
4. Commit only my own files, push, then tell the coordinator.

**D. Descriptions**
- Count with three methods: `wc -w`, split on spaces, and split on hyphens and slashes. The strictest must stay at or under the limit (246 here for a 250 limit). Keep the Jev disclosure line verbatim and the tagline below the logo.
- Readability: `documents/product/readability_check.py` (English grade, Spanish INFLESZ).

**E. Audio and timing scripts**
- Measure the real voice, not a guess: sum words and seconds over the rendered clips (`video/vo/arc/*.wav`, `wave` module). Eric ran at about 2.9 words a second inside a clip. With 0.5 to 0.6 s breaths, plan about 2.5 words a second overall.
- Mark each line NEW, CHANGED or UNCHANGED against the approved lines so the video agent re-renders only what changed.

**F. Making a local app run for screenshots or PDFs (offline)**
- `cd code && NURY_REPLAY=1 PORT=<spare port> python3 -m app.server`. Check the session JSON says `replay: true` before approving anything. Approve each gate through `/api/session/<id>/decision`, save, then get PDFs from `/api/case/<id>/pdf/family` (needs Chrome). Kill the server by port: `lsof -ti tcp:<port> | xargs kill`.

## 3. Technical learnings: do and avoid
- **Do:** make one `.hl`/step-based deck from a template and generate the file. A single generated HTML file travelled well (no build step for the venue).
- **Avoid:** checking layout with `eval` after `set viewport` in agent-browser. The window stayed 1280x577, so the check was invalid. Use exact-size iframes (`fit_check.sh`) for numbers and screenshots for looks.
- **Avoid:** `git add documents` or `git add presentation`. It swept in other agents' screenshots, patch files and (once) their in-progress deck edits. Stage explicit paths. Even then, `build_deck.py` rewrites `deck.html` from the template in the working tree, so uncommitted template edits by someone else get committed under my name. Check `git status` first.
- **Avoid:** `sed -i` without a backup suffix on macOS (it fails: `invalid command code`). Use Python for edits.
- **Avoid:** bulk regex rewrites of a word like "package". It mangled URLs and quoted code names. Replace by hand where it is a name, by regex only in prose, then re-read the diff.
- **Evidence of a fact, not memory:** Jev price ($0.042 per million input tokens) was public. I said "unknown" for hours. Search first (docs.typesafe.ai/models), cite the page.
- **Do:** record real measured pace and cost per case from the scorecards ($0.064 and 34.2 s detention, $0.089 and 49.5 s hospital) and say "a first draft in under a minute", never "ready", never hours saved.
- **Avoid fail-open wording on slides.** The fact that the run continues when Jev is down belongs only in Limits, TECH_CLAIMS and one Q&A.
- **Do:** run a strictest-count word check every time a description line changes. Hyphen-split counted 4 to 8 more words than `wc`.

## 4. Procedural learnings: coordinator, agents, Juan
- **What Juan cares about:** honesty first (no claim we cannot back up), plain words, a deck that a stranger understands in five seconds, nothing political, no pastor or family claimed as a user, the memorial handled with care (his words, verbatim, nobody edits them).
- **Real mistakes I made, named:**
  1. I typed commit dates by hand on 41 commits (the audit later found 93 in all, 69 mine and 24 from the video agent). They looked fabricated. I disclosed it at once. Never set a date. `documents/product/COMMIT_DATES.md` lists them.
  2. I reported slides as done on a script result alone and looked at only about 7 of 13 screenshots. Juan found them crowded. Slides averaged far too many words because every order added a chip, a caveat or a table. I did not push back. The fix that worked: hard word limits per slide set before layout (headline 8 words, one line 15, three labels of 1 to 4 words), caveats in notes and backups, and a separate visual owner.
  3. I started the app "with no keys" to capture a PDF, but the repo `.env` supplied a live key, so replay was off and one live run began. Always set `NURY_REPLAY=1` and check `replay: true`.
  4. I quoted counts without counting (33 facts / 24 mismatches, really 31 / 14) and an invented time in notes (04:20 when the clock said 04:07). Read the clock with `date` and count with a script.
  5. I committed another agent's patch files and later their in-progress deck edits under my name. Disclose it and say sorry; then stage explicit paths.
- **With the coordinator:** one consolidated report per task: list of files, what changed, what I could not verify, what I need decided. Flag claims that are not in the audit instead of keeping them quiet ("chaplain", "five AI agents"). Ask before editing a file another agent owns.
- **Ownership changes fast.** When the coordinator moved visual design to hack-artisans, I kept only words and claims, and delivered `DECK_COPY.md` in one file. Do the same: hand over a file, not a conversation.
- **Locks and quiet windows are real.** There was a browser quiet window (no fit checks), a credit rule (no live Gloo or Jev calls) and a "cancel, stay idle" message. Obey at once and say so in one line.
- **When Juan says a number is wrong** (41 vs 93, 3 minutes vs 90 s), fix every file with grep, rebuild generated pages through their owner, and report the file list.

## 5. Time and cost
- **Slow:** the full deck rebuild (about half a day across many messages), because the instructions kept changing and I verified each fact. The submission form and descriptions took about 30 minutes each when the facts table was ready.
- **Cheap and fast:** copy files (`DECK_COPY.md`, `PRESENTER_CARD.md`) from an existing deck once the story is fixed; renaming sweeps with grep; fit checks (about 30 s per run).
- **Costly by mistake:** repeated rework of the deck copy after each late order, and hours spent on "unknown" facts that a 2-second search would have settled.
- **Money:** I spent no model credit on purpose. One accidental live run (a few cents). I made no live Gloo or Jev calls after the credit rule.

## 6. Skill candidates
1. **claims-table-audit.** Trigger: "check every document against the facts", or before submission. Steps: build one table of facts with sources from code and scorecards; grep all text for old patterns (old numbers, "package", "pass rate", fail-open wording); fix owned files; send mismatches in other files to their owners; re-scan; list what a scan cannot find.
2. **deck-fit-and-look-check.** Trigger: any HTML deck or page change. Steps: build; run exact-size iframe fit check at 3 sizes in 2 views; screenshot each changed slide; read the image; judge "five seconds, one idea, 8-word headline"; only then say done.
3. **word-budgeted-slide-copy.** Trigger: new or crowded slide. Steps: write headline (8 words), one line (15), three labels (1 to 4 words), notes with time, spoken line and criterion; move caveats to notes or backups; get the story approved before layout.
4. **voice-script-from-real-pace.** Trigger: a narration or pitch script with a time limit. Steps: measure real clips (words per second); set breath; compute start times; mark NEW/CHANGED/UNCHANGED; list a cut order with seconds saved per cut; check no silence over the limit.
5. **submission-pack.** Trigger: a hackathon form. Steps: read the rules for required fields and say which could not be confirmed; write descriptions with a strictest word counter; keep the disclosure line verbatim; add a checklist with hard stops; build a copy-button page from the Markdown.

## 7. Advice to the next agent in this role
1. Build the facts table first. Write claims last.
2. Look at every slide yourself before saying done. A script cannot judge clarity.
3. Set word limits before layout and defend them. Caveats go in notes.
4. Never set a commit date. Stage explicit paths. Check `git status` before a build that rewrites shared files.
5. Start any local app with `NURY_REPLAY=1`. Obey credit rules and quiet windows at once.
6. Search for public facts before writing "unknown".
7. Count words three ways. Use the strictest.
8. One report per task: files, changes, unverified claims, decisions needed.
9. Say what you got wrong, plainly, the moment you see it.
10. Keep the memorial and any person's words verbatim. Nobody edits them.
