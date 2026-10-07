# Shared demo: one family, one intake, one VO

Locked by hack-ninja with hack-video. Deck, pitch, finalist script and video all use this. Change it here first.

## The family
Maria (caller, Spanish-speaking), Jose (her husband, detained), two children, 8 and 11, both US citizens. Aurora. Jose has lived here 14 years. Synthetic. No real people, no real numbers.

## The intake (what the pastor types)
"Maria called at 2:07 AM, very upset, speaking Spanish. Her husband Jose was detained by immigration officers outside his workplace in Aurora around 6 PM yesterday. She does not know if the officers showed a warrant. Jose has lived here 14 years. They have two children, 8 and 11, both US citizens. Maria is afraid to leave the house tomorrow. She wants to know what to do tonight."

Changes from `demo_scenario.py`: time 9:10 PM to 2:07 AM; "ICE" to "immigration officers" (humanitarian, no agency name on screen); "today" to "yesterday" so 2 AM reads true. The app run must use this exact text. Owner of the code change: hack-artisans.

## Guardrail beat
Status strip only: "Draft rejected by guardrail. Regenerating (2 of 3)." then green "Passed". Never show the unsafe text. Three attempts total: first draft plus two regenerations.

## Locked VO (90 s video)
1. "It is two in the morning. A family is calling their pastor."
2. "Her husband was detained last evening. The pastor has no staff, and no lawyer on the line."
3. "Nury turns the call into a clear case. Facts only. No advice."
4. "After every stage, the pastor decides."
5. "Rights in the family's own language. Built only from a vetted source. Every point cited."
6. "When a draft crosses the line from information into advice, Nury rejects it and tries again. The pastor never sees it."
7. "Attorney hotlines. A checklist for tonight."
8. "And a short, warm message, in the pastor's hands to edit."
9. "Nury is not a pastor, and it never sends. The pastor does."
10. "Nury. The crisis-response agent for solo pastors."

Edits to the storyboard draft: shot 2 ("taken today" to "detained last evening"); shot 6 ("Sometimes a draft crosses" to "When a draft crosses", so we do not imply a failure rate we have not measured).
