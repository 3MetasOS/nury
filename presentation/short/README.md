# Nury (90 seconds): the short deck

A separate presentation from the full deck. Nothing here is shared with `presentation/deck.html`: this folder has its own page, fonts, images and tests, and it opens by itself.

## Open it
Open `short/deck.html` in a browser (a double click works: it runs from `file://`). No server, no build step, no URL parameter. The page title is "Nury (90 seconds)".

## The six slides
1. `the-call` (dark): 2:07 AM, a pastor's phone rings.
2. `the-name`: the lantern lights and the name builds.
3. `why-it-matters`: What changes when a pastor has Nury (three labels).
4. `the-demo`: the headline and a 16:9 frame (60 percent of the slide width) where the film plays.
5. `so-what`: So what? (three lines).
6. `close`: logo, tagline below it, the line, the lantern photo and the two small memory lines.

Words come from `presentation/SHORT_TRACK.md` (hack-ninja). Slide names are the URL anchors (`deck.html#so-what`).

## Keys
Space or Right arrow: next step, then next slide. Left arrow: back one step. `a`: AUTO (all steps play 400 ms apart). `g`: slide index. `n`: speaker notes. `h`: one-line help. `f`: hide the footer. Home and End jump to the first and last slide. A click on the right half is one step forward, on the left half one step back. Reduced motion and `?clean=1` show every slide complete.

## Files
- `deck.html`: the whole deck (styles and script inside). This file is the source: edit it directly.
- `fonts/GochiHand-400.woff2`, `images/porch-light.jpg`, `images/lanterns-hand.jpg`: its own copies of what it uses. (Fraunces and Inter load from Google Fonts when online; offline the page falls back to system serif and sans.)
- `fit_check.sh`, `fit_check.js`: real-size fit check (1280x720, 1920x1080, 390x844). Run `sh presentation/short/fit_check.sh`.
- `anim_test.py`: keys, the final state of every slide before and after its animation, and the auto time per slide (at most 3 s). Run `python3 presentation/short/anim_test.py`. Run it alone: two programs driving the browser at once break each other's sessions.

Both scripts need `agent-browser` and Python 3 (Pillow for the animation test).
