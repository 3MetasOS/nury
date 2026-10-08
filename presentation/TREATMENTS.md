# Three treatments for the 90-second film (Juan's creative reset)

Status: **Juan chose A** (2026-10-07). The final script is `FINALIST_SCRIPT.md`. Written by hack-ninja, 2026-10-06. Nothing existing is thrown away: the app footage, the dictionary card, the tech beat, the end card, the memorial card and Eric's voice are assets in all three. Further polish on them is on hold until Juan picks.

## Shared persona (synthetic)
Pastor Elias, 58. Solo pastor of a church of about forty in a storefront in Aurora, Colorado. No staff, no lawyer on speed dial. Seen only as a silhouette and as hands. In his hand: a phone. On the table: a cold mug and a worn notebook, under one lamp. His want: to give Maria something true and useful before she hangs up. His clock: it is 2:07 AM. The family: Maria, her children (8 and 11), and Jose, who was detained last evening. Seen only as silhouettes in a lit window and a few pairs of shoes by a door. All synthetic. No real people, no faces, no agency imagery.

## What I researched, and what it changed
| Source | What it says (verbatim) | How I used it |
|---|---|---|
| [WUNC News (NPR), "Meet the creator of the Story Spine, an 8-sentence tool to create and analyze stories", 2026-06-23](https://www.wunc.org/2026-06-23/meet-the-creator-of-the-story-spine-an-8-sentence-tool-to-create-and-analyze-stories) | Once upon a time / Every day / But one day / Because of that (x3) / Until finally / And ever since then | The eight sentence starters, in that order. I used the spine to write each treatment's one-paragraph story. |
| [Emma Coats, 22 Rules of Storytelling (via Laughing Squid)](https://laughingsquid.com/22-rules-of-storytelling-by-pixar-storyboard-artist/) | "Come up with your ending before you figure out your middle." (#7) "What is your character good at, comfortable with? Throw the polar opposite at them." (#6) "Why must you tell THIS story?" (#14) | We wrote the ending first: dawn, then the memorial. The pastor is good at answering alone; the 2:07 AM call with no lawyer is the polar opposite. |
| [Geoff Ralston, A Guide to Demo Day Presentations, Y Combinator, 2016-07-25](https://www.ycombinator.com/blog/guide-to-demo-day-pitches/) | "Briefly say what you are doing and why." "A common error is to avoid describing what you do until far into the presentation. That is always a mistake." "an audience cannot read a slide AND listen to you simultaneously." | This is the case for C (say it first) and the warning against B (withholding the name for 43 seconds). It also argues for few words on screen. |
| [Copyblogger, Problem-Agitate-Solve](https://copyblogger.com/problem-agitate-solve/) | "Identify a problem." "Agitate that problem." "Trot out the solution." | The page does not warn about over-agitating, so the limit is ours: we agitate through time and consequence (the clock, the call), never by showing a family in distress. |
| [Video Production Guide for Hackathons, AI Tinkerers](https://aitinkerers.org/docs/public/video_production_guide.md?markdown=1) | "Production quality does not affect your judging score." "Show actual functionality, not just slides." | An honest counterweight to a cinematic reset. The real app run must stay legible in every treatment, and none may trade clarity for mood. |
| [FilmDaft, What Is Sound Design in Film?](https://filmdaft.com/what-is-sound-design-in-film-definition/) | "Silence can be the stronger choice when small details or vulnerability matter." "Dynamic range and contrast often create more tension than constant volume." "Footsteps, cloth, and hand props give a scene timing and intimacy." | The audio arc in each treatment: sparse and tense, then release. B leans on foley. All three use a held silence before the turn. |
| [Wikipedia, Kuleshov effect](https://en.wikipedia.org/wiki/Kuleshov_effect) | "a cognitive phenomenon by which viewers derive more meaning from the interaction of two sequential shots than from a single shot in isolation" | The cut from the pastor's hands to the lit window in A and C does the emotional work without a face. |
| [Remotion documentation](https://www.remotion.dev/docs/spring) | spring(): "A physics-based animation primitive." interpolate(): "Allows you to map a range of values to another using a concise syntax." | The clock in C, the lantern's flame and the card reveals in all three are `interpolate` and `spring`: nothing new to learn, which is why they are feasible. |

**The honest tension.** The hackathon guide I read says "Production quality does not affect your judging score," and Y Combinator's guide says to say what you do early and keep slides light. A cinematic film is a bet against that advice. The bet is only safe if the real app run stays clear in every frame. Every treatment below keeps it.

**Our own limit on agitation.** Problem, agitate, solve works by making the problem felt. We agitate through time and consequence (the clock, the call) and never by showing a family in distress.

## My recommendation
My recommendation: **A, with one plain line borrowed from C** (the entry's second sense, "The crisis-response agent for solo pastors", is already on screen in the first 22 seconds). A gives the most feeling and the clearest arc, and its build is moderate. If time or hack-video's hours run short, **fall back to C**, the safest build and the clearest first ten seconds. I would not pick B for this deadline: it needs hands we do not have, and it withholds the name for 43 seconds against the advice I read. If Juan loves B, we can still borrow its sound idea (no music until the lantern) inside A.

## Hard rules all three keep
At most 90 s. Eric (ElevenLabs, disclosed) is the narrator, and every line is 8 words or fewer. The memorial is last and is text only, with no synthetic voice. No real people, no real children, no agency imagery or names, no stock photos of detainees. Humanitarian, never political. Technical claims from `documents/TECH_CLAIMS.md`, VERIFIED rows only, and the Jev disclosure caption verbatim. No unlicensed music: the pad, the ticks and the foley are synthesized.

## Treatment A: From night to light

**Concept.** Emotion first. The film starts in night (ink), the lantern lights at the turn of the first act, and it ends in dawn (paper). The story spine does the work: a pastor's night, one call, a decision.

**Story spine.** Once upon a time there was a solo pastor. Every day he answers what he can. One day, at 2:07 AM, a family called. Because of that he opened Nury. Because of that every stage waited for his decision. Because of that an unsafe draft never reached him. Until finally a message was ready, and he sent it by hand. And ever since then, a lantern stays lit.

**What makes it different.** Light is the structure: ink to amber to paper. "This is Nury" lands after the first act, as the release. Observer camera: a room, a window, silhouettes.

| Time | Picture | Eric (8 words or fewer) | Sound | On-screen type | Asset |
|---|---|---|---|---|---|
| 0:00 to 0:03 | HOOK. Black. A phone lights a dark table: "2:07 AM, Maria". | (none) | Room tone (a low hum), one clock tick, the phone buzzes twice. | 2:07 AM | NEW (vector, 3 s) |
| 0:03 to 0:09 | PERSONA. A man's silhouette at a kitchen table, one lamp, a cold mug. His hand takes the phone. | 2:07 AM. Maria is calling. | Hum, a chair creak, a held breath. The tick continues. | Solo pastor. No staff. No lawyer. | NEW (vector) |
| 0:09 to 0:15 | STAKES. The intake is typed (real app footage). Cut to a lit window: a mother and two children in silhouette, shoes by the door. | Her husband was detained last evening. | Keys, very soft. A distant murmur with no words. | Synthetic family. Not real people. | REUSE typing + NEW window shot |
| 0:15 to 0:22 | THIS IS NURY. The screen's glow warms. The lantern lights. The dictionary card builds on paper-grey. | This is Nury. | The tick stops. A warm low pad enters (first release). | Nury /NOO-ree/ proper noun. 1. A given name from Arabic nur, "light". 2. The crisis-response agent for solo pastors. see also: lantern | REUSE dictionary card, re-skinned |
| 0:22 to 0:30 | THE TOOL. Crisis selector: Detention. Intake, then the triage card. A thumb taps Approve (amber pulse). | Five stages. A gate after each. | Pad holds. A soft tap. | 1 Triage. Approve / Edit / Stop | REUSE real app footage |
| 0:30 to 0:37 | Rights brief in Spanish, every point with a citation chip. | Her language. Every point cited. | Pad. A page-turn tick on each chip. | 2 Rights brief. Vetted sources only. | REUSE real app footage |
| 0:37 to 0:46 | THE TURN. The pad cuts to silence. A slower tick. The strip: "Draft rejected by guardrail. Regenerating (2 of 3)." Then green: Passed. His hand stops, then moves. | Unsafe draft. Rejected. He never sees it. | One second of silence. A slow tick. A low note on "Passed". | Rejected. Regenerating (2 of 3). Passed. | REUSE footage + NEW sound |
| 0:46 to 0:58 | TECH BEAT. The lantern's light spreads over a clean line diagram: pastor, tokens, Gloo AI Studio, checks, a person. | Names become tokens before leaving his computer.  /  Checks reject unsafe drafts. A person decides. | Pad. A soft tick as each node lights. | Leak test: 90 checks per playbook, 0 found. Typed judge, ten checks: unsafe 0.89 to 0.98, safe 0.02 to 0.24. A full package: 50 to 56 s, about 9 cents. Disclosure caption, verbatim. | REUSE tech beat, re-skinned and re-timed |
| 0:58 to 1:06 | Attorney resources, the checklist, then the pastoral message. One word is edited. | A warm message. His to edit. | Pad. A key tap. | 3 Attorneys. 4 Checklist. 5 Message | REUSE real app footage |
| 1:06 to 1:11 | Copy, not Send. The disclaimer is on screen. His hand pastes into his own messages. | Nury never sends. He does. | Tap, paste. The pad resolves. | Nury does not send. The pastor does. Legal information only. | REUSE footage + NEW 1 s |
| 1:11 to 1:14 | DAWN. The ink washes to paper. The lantern, small. | The crisis-response agent for solo pastors. | The pad fades. One soft high tone, like first light. | Nury. the crisis-response agent for solo pastors | REUSE end card, re-skinned |
| 1:14 to 1:30 | MEMORIAL. Paper, a deep-amber lantern, Juan's words, text only. Slow fade in and out. | (none) | Near silence. Faint room tone only. No voice. | Juan's words, unedited (text only) | REUSE memorial card |

**Where the six musts land**
- 1. This is Nury (the name, the dictionary moment, the brand line): 0:15 to 0:22, 1:11 to 1:14
- 2. What it is (the crisis tool: five stages, a gate after each, nothing sent): 0:22 to 0:30, 0:30 to 0:37, 0:58 to 1:06, 1:06 to 1:11
- 3. The person and the tension (persona, the clock, a decision): 0:00 to 0:03, 0:03 to 0:09, 0:09 to 0:15
- 4. The turn (a draft rejected before the pastor sees it): 0:37 to 0:46
- 5. The technical sell, with proof (VERIFIED claims, the disclosure caption): 0:46 to 0:58
- 6. The memorial (Nury Pelaez, last, text only): 1:14 to 1:30

**Sound design.** Night: low room tone, a clock tick, a phone buzz. At the lantern: the tick stops and a warm low pad enters. At the turn: silence, then a slower tick. At the end: the pad fades to one soft high tone. The memorial is near silence.

**Type.** Large, calm, few words. Fraunces for the entry and the memorial. Captions on every beat for muted viewing.

**Feasibility (my estimate, not measured).** New: three vector night shots (the table, the window, the dawn wash) and the ink-to-paper grade; a synthesized pad and foley; about 11 new Eric lines. Reused: the real app run, the dictionary card, the tech beat, the end card and the memorial card. Estimate for hack-video: 6 to 8 hours.

**Risks.** Taste: silhouettes must stay generic (no identifiable person, no agency imagery). Time: the grade and the new shots are the long pole. Honesty: the window shot is a synthetic family and is labeled so.

**The live pitch tonight.** The live pitch tonight keeps the deck. Open on slide 3 (the call) with the buzz and "2:07 AM", then slide 1, 2. About 10 minutes of edits.

**Pick A if you want the most feeling and the clearest arc.**

## Treatment B: His hands

**Concept.** The whole film from the pastor's side of the phone, seen only through his hands and the screen. The viewer learns what Nury is as he does. The name is withheld until the product has earned it.

**Story spine.** Once upon a time there was a pair of hands that answered every call. Every day they did the work alone. One day a call came at 2:07 AM. Because of that they typed a stranger's fear into a screen. Because of that the screen asked for a decision at every step. Because of that it caught something unsafe before he saw it. Until finally the hands held a lantern, and learned its name. And ever since then, nothing leaves without his say.

**What makes it different.** Point of view, not light, is the structure. No face, no room, no window: hands, a phone, a table. "This is Nury" lands LATE, after the turn: an earned reveal. The sound is close and physical.

| Time | Picture | Eric (8 words or fewer) | Sound | On-screen type | Asset |
|---|---|---|---|---|---|
| 0:00 to 0:03 | HOOK. Macro: a hand flat on a dark table. The phone lights his fingers: "2:07 AM, Maria". | (none) | A tick, the buzz, a breath. | 2:07 AM | NEW (vector hands) |
| 0:03 to 0:09 | The other hand rubs his eyes, then takes the phone. The thumb hesitates. | He answers on the second ring. | Cloth, breath, the tick. | Solo pastor. No staff. No lawyer. | NEW (vector hands) |
| 0:09 to 0:16 | Hands type what Maria said. The words appear in amber at his fingertips. | Her husband was detained last evening. | Soft keys. A mug set down. | The intake text, as typed. Synthetic family. Not real people. | REUSE typing footage, framed by NEW hands |
| 0:16 to 0:25 | THE TOOL, UNNAMED. Thumb taps Detention. The triage card. Thumb taps Approve. He does not know what it is called yet. | A screen he has never seen. | Thumb taps. No music yet. | 1 Triage. Approve / Edit / Stop | REUSE real app footage |
| 0:25 to 0:33 | A finger traces a citation chip in the Spanish brief, line by line, like reading. | Her language. Every point cited. | A fingertip scrape. Faint pad. | 2 Rights brief. Vetted sources only. | REUSE real app footage |
| 0:33 to 0:43 | THE TURN. His hand freezes above the screen. The strip: rejected, regenerating, passed. The hand exhales back into motion. | Something unsafe. Caught. He never saw it. | Silence. A held breath. A slow tick. A low note on "Passed". | Rejected. Regenerating (2 of 3). Passed. | REUSE footage + NEW hands |
| 0:43 to 0:50 | THIS IS NURY, EARNED. The screen's glow becomes a lantern in his cupped hands. The dictionary card rises from it. | This is Nury. | The tick stops. The pad swells. | Nury /NOO-ree/ proper noun. 1. A given name from Arabic nur, "light". 2. The crisis-response agent for solo pastors. | REUSE dictionary card |
| 0:50 to 1:02 | TECH BEAT as what is under his hands: thin lines draw out from his fingertips: tokens, Gloo AI Studio, checks, judges, a person. | Names become tokens. Checks reject unsafe drafts.  /  A red team tests it. A person decides. | Pad. A faint tick per node. | Leak test: 90 checks per playbook, 0 found. Typed judge, ten checks: unsafe 0.89 to 0.98, safe 0.02 to 0.24. A full package: 50 to 56 s, about 9 cents. Disclosure caption, verbatim. | REUSE tech beat, restyled |
| 1:02 to 1:09 | His hand edits one word in the pastoral message. The checklist scrolls. | A warm message. His to edit. | A key tap. Pad. | 3 Attorneys. 4 Checklist. 5 Message | REUSE real app footage |
| 1:09 to 1:14 | His hand copies the text, switches to his own messages, pastes. Nury's screen has no Send. | Nury never sends. He does. | Tap, paste. The pad resolves. | Nury does not send. The pastor does. Legal information only. | REUSE footage + NEW hands |
| 1:14 to 1:17 | End card, on dawn paper. | The crisis-response agent for solo pastors. | The pad fades. | Nury. the crisis-response agent for solo pastors | REUSE end card |
| 1:17 to 1:30 | MEMORIAL. Paper, a deep-amber lantern, Juan's words, text only. | (none) | Near silence. Room tone only. | Juan's words, unedited (text only) | REUSE memorial card |

**Where the six musts land**
- 1. This is Nury (the name, the dictionary moment, the brand line): 0:43 to 0:50, 1:14 to 1:17
- 2. What it is (the crisis tool: five stages, a gate after each, nothing sent): 0:16 to 0:25, 0:25 to 0:33, 1:02 to 1:09, 1:09 to 1:14
- 3. The person and the tension (persona, the clock, a decision): 0:00 to 0:03, 0:03 to 0:09, 0:09 to 0:16
- 4. The turn (a draft rejected before the pastor sees it): 0:33 to 0:43
- 5. The technical sell, with proof (VERIFIED claims, the disclosure caption): 0:50 to 1:02
- 6. The memorial (Nury Pelaez, last, text only): 1:17 to 1:30

**Sound design.** Intimate foley: cloth, keys, a mug, a thumb on glass, breath. No music at all until the lantern lights (about 0:43), then the pad. The turn is a held breath and silence. The memorial is room tone only.

**Type.** Almost no type until the lantern. Then the entry, the proof captions and the disclosure. Very sparse.

**Feasibility (my estimate, not measured).** Hardest. There is no hand footage, and we have no actor. Option 1: animate flat vector hands (about 9 to 12 hours, and a risk of looking odd). Option 2: film real hands (anyone's, on a phone and a table). That needs Juan's rule: the brief says no real people, and hands are people. I would not do option 2 without his word. Eric needs about 10 new lines.

**Risks.** Craft: stylized hands can look uncanny at close range. Clarity: withholding the name for 43 seconds is a risk if a judge skims. Time: the highest of the three.

**The live pitch tonight.** The live pitch tonight cannot use this. It is a film idea. Keep the deck as it is.

**Pick B if you want the most distinctive film and accept the most risk.**

## Treatment C: The clock

**Concept.** Say it, then prove it. The film tells the viewer what Nury is in the first ten seconds, then shows it working against a visible clock that starts at 2:07 AM. The clock is the tension.

**Story spine.** Once upon a time it was 2:07 AM. Every minute, a family waited. But one day a solo pastor had no staff and no lawyer. Because of that he used five stages, one minute at a time. Because of that an unsafe draft was stopped. Because of that a message was ready. Until finally he sent it himself, by hand. And ever since then, the clock stops at dawn.

**What makes it different.** Clarity first, tension second: the opposite order from A and B. A visible clock sets the pace and the cuts. The clock is a device, not a product claim: the footage is sped up and labeled, and the only measured number on screen is the real compute time (50 to 56 s).

| Time | Picture | Eric (8 words or fewer) | Sound | On-screen type | Asset |
|---|---|---|---|---|---|
| 0:00 to 0:03 | HOOK. Black. A large clock: "2:07 AM". One tick. The phone buzz. | (none) | A synthesized tick, then the buzz. | 2:07 AM | NEW (clock component) |
| 0:03 to 0:12 | THIS IS NURY, FIRST. The dictionary card, with one plain line under it: what it is. A thin clock stays in the corner. | This is Nury. Watch it work at 2:07. | The tick bed under a soft pad. | Nury /NOO-ree/ proper noun. 1. A given name from Arabic nur, "light". 2. The crisis-response agent for solo pastors. Five stages. A gate after each. Nothing sent. | REUSE dictionary card + NEW line |
| 0:12 to 0:18 | PERSONA. A silhouette at a table, one lamp. Cut to the lit window and the family's shoes by the door. Clock: 2:08. | A solo pastor. No staff. No lawyer. | Hum. The tick. A distant murmur, no words. | Solo pastor. No staff. No lawyer. Synthetic family. Not real people. | NEW (vector) |
| 0:18 to 0:32 | THE TOOL AT SPEED. Crisis selector: Detention. Intake, triage, Approve, rights brief. Each gate is a tick of the clock: 2:09, 2:10. | Five stages. A gate after each. | Ticks, softer as it goes. Taps. | 1 Triage. 2 Rights brief. Approve / Edit / Stop | REUSE real app footage + NEW clock overlay |
| 0:32 to 0:42 | THE TURN. The clock freezes. The strip: rejected, regenerating, passed. Silence. The tick resumes, slower. | Rejected. He never sees that draft. | Silence for 1 s. A slow tick. | Rejected. Regenerating (2 of 3). Passed. | REUSE footage + NEW sound |
| 0:42 to 0:54 | TECH BEAT while the clock runs: the same diagram, the clock small in the corner. | Names become tokens. Checks reject unsafe drafts.  /  A red team tests it. A person decides. | Ticks, one per node. | Leak test: 90 checks per playbook, 0 found. Typed judge, ten checks: unsafe 0.89 to 0.98, safe 0.02 to 0.24. Disclosure caption, verbatim. | REUSE tech beat, restyled |
| 0:54 to 1:06 | Attorney resources, checklist, the pastoral message. Clock: 2:11. | A warm message. His to edit. | Ticks. A key tap. | 3 Attorneys. 4 Checklist. 5 Message | REUSE real app footage |
| 1:06 to 1:12 | Copy, not Send. Clock: 2:12. A proof line: the compute time, with the footage marked as sped up. | Nury never sends. He does. | The ticks stop on the last tap. The pad resolves. | Nury does not send. The pastor does. A full package: 50 to 56 seconds (footage sped up). | REUSE footage + NEW overlay |
| 1:12 to 1:15 | End card on dawn paper. The clock is gone. | The crisis-response agent for solo pastors. | The pad fades. | Nury. the crisis-response agent for solo pastors | REUSE end card |
| 1:15 to 1:30 | MEMORIAL. Paper, a deep-amber lantern, Juan's words, text only. | (none) | Near silence. Room tone only. | Juan's words, unedited (text only) | REUSE memorial card |

**Where the six musts land**
- 1. This is Nury (the name, the dictionary moment, the brand line): 0:03 to 0:12, 1:12 to 1:15
- 2. What it is (the crisis tool: five stages, a gate after each, nothing sent): 0:03 to 0:12, 0:18 to 0:32, 0:54 to 1:06, 1:06 to 1:12
- 3. The person and the tension (persona, the clock, a decision): 0:00 to 0:03, 0:12 to 0:18
- 4. The turn (a draft rejected before the pastor sees it): 0:32 to 0:42
- 5. The technical sell, with proof (VERIFIED claims, the disclosure caption): 0:42 to 0:54, 1:06 to 1:12
- 6. The memorial (Nury Pelaez, last, text only): 1:15 to 1:30

**Sound design.** A synthesized tick bed under everything. It slows at the turn, goes silent for one second, and stops at the end card. A pad enters only at the dictionary card and resolves at the end. The memorial is near silence.

**Type.** The clock is the typographic character: large, amber, tabular figures. One plain line says what Nury is. Captions throughout.

**Feasibility (my estimate, not measured).** Most feasible. New: a clock component (Remotion `interpolate` and `spring`), a tick sound, three vector shots (the table and the window). About 9 new Eric lines. Estimate for hack-video: 4 to 6 hours.

**Risks.** Honesty: a story clock from 2:07 to 2:12 can read as "five minutes to a package". We say "footage sped up" and show the real 50 to 56 s. Taste: the least emotional of the three. Clarity: the strongest.

**The live pitch tonight.** The live pitch tonight can adopt this almost as is: start the deck with a 2:07 AM clock. The deck already says what Nury is up front on slide 2.

**Pick C if you want the safest build and the clearest first ten seconds.**

## Deadlines, said plainly
The prelim pitch is tonight (Oct 7, 21:00 to 23:00 MDT) and the finalist film is due Oct 8, 09:00, only if we make the top 25. So the film has until the morning and the pitch does not. hack-video is the one builder for the film and hack-artisans is full. The hours above are my estimates and assume Eric's new lines are generated once, a few lines at a time. I have not built any of these.
