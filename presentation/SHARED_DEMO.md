# Shared demo: one family, one intake, one VO

Locked by hack-ninja with hack-video. Deck, pitch, finalist script and video all use this. Change it here first. The voice-over is in `ERIC_LINES.md`.

## The family
Maria (caller, Spanish-speaking), Jose (her husband, detained), two children, 8 and 11, both US citizens. Aurora. Jose has lived here 14 years. Synthetic. No real people, no real numbers.

## The intake (what the pastor types)
"Maria called at 2:07 AM, very upset, speaking Spanish. Her husband Jose was detained by immigration officers outside his workplace in Aurora around 6 PM yesterday. She does not know if the officers showed a warrant. Jose has lived here 14 years. They have two children, 8 and 11, both US citizens. Maria is afraid to leave the house tomorrow. She wants to know what to do tonight."

Changes from `demo_scenario.py`: time 9:10 PM to 2:07 AM; "ICE" to "immigration officers" (humanitarian, no agency name on screen); "today" to "yesterday" so 2 AM reads true. The app run must use this exact text. Owner of the code change: hack-artisans.

## Guardrail beat
Status strip only: "Draft rejected by guardrail. Regenerating (2 of 3)." then green "Passed". Never show the unsafe text. Three attempts total: first draft plus two regenerations.

## Voice-over (90 s film): see `ERIC_LINES.md`
SUPERSEDED 2026-10-07. The old ten-line voice-over that stood here is gone. Eric's approved lines (L1 to L11 and the seven added lines E1 to E9) live in `ERIC_LINES.md`, with exact times in `FINALIST_SCRIPT.md`. Do not render from this file.
