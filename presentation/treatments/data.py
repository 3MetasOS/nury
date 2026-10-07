"""The three treatments, as data. build.py renders TREATMENTS.md, the frame files and the canvas from this."""
import frames as F

# Row: (start, end, picture, eric, sound, on_screen, asset, tags)   tags: M1 name, M2 tool, M3 tension+person, M4 turn, M5 tech, M6 memorial
BR = "An AI crisis response agent."
TECH1 = "Names become tokens before they reach the model."
TECH2 = "Checks reject unsafe drafts. A person decides."

A_ROWS = [
 (0, 3, "HOOK. Black. A phone lights a dark table: \"2:07 AM, Maria\".", "", "Room tone (a low hum), one clock tick, the phone buzzes twice.", "2:07 AM", "NEW (vector, 3 s)", ["M3"]),
 (3, 9, "PERSONA. A man's silhouette at a kitchen table, one lamp, a cold mug. His hand takes the phone.", "2:07 AM. Maria is calling.", "Hum, a chair creak, a held breath. The tick continues.", "A pastor. No lawyer on the line.", "NEW (vector)", ["M3"]),
 (9, 15, "STAKES. The intake is typed (real app footage). Cut to a lit window: a mother and two children in silhouette, shoes by the door.", "Her husband was detained last evening.", "Keys, very soft. A distant murmur with no words.", "Synthetic family. Not real people.", "REUSE typing + NEW window shot", ["M3"]),
 (15, 22, "THIS IS NURY. The screen's glow warms. The lantern lights. The dictionary card builds on paper-grey.", "This is Nury.", "The tick stops. A warm low pad enters (first release).", "Nury /NOO-ree/ proper noun. 1. A given name from Arabic nur, \"light\". 2. An AI crisis response agent. see also: lantern", "REUSE dictionary card, re-skinned", ["M1"]),
 (22, 30, "THE TOOL. Crisis selector: Detention. Intake, then the triage card. A thumb taps Approve (amber pulse).", "Five stages. A gate after each.", "Pad holds. A soft tap.", "1 Triage. Approve / Edit / Stop", "REUSE real app footage", ["M2"]),
 (30, 37, "Rights brief in Spanish, every point with a citation chip.", "Her language. Every point cited.", "Pad. A page-turn tick on each chip.", "2 Rights brief. Vetted sources only.", "REUSE real app footage", ["M2"]),
 (37, 46, "THE TURN. The pad cuts to silence. A slower tick. The strip: \"Draft rejected by guardrail. Regenerating (2 of 3).\" Then green: Passed. His hand stops, then moves.", "Unsafe draft. Rejected. He never sees it.", "One second of silence. A slow tick. A low note on \"Passed\".", "Rejected. Regenerating (2 of 3). Passed.", "REUSE footage + NEW sound", ["M4"]),
 (46, 58, "TECH BEAT. The lantern's light spreads over a clean line diagram: pastor, tokens, Gloo AI Studio, checks, a person.", TECH1 + " | " + TECH2, "Pad. A soft tick as each node lights.", "Leak test: 90 checks per playbook, 0 found. Typed judge, ten checks: unsafe 0.89 to 0.98, safe 0.02 to 0.24. A full case: 34 to 50 s, 6 to 9 cents. Disclosure caption, verbatim.", "REUSE tech beat, re-skinned and re-timed", ["M5"]),
 (58, 66, "Attorney resources, the checklist, then the pastoral message. One word is edited.", "A warm message. His to edit.", "Pad. A key tap.", "3 Attorneys. 4 Checklist. 5 Message", "REUSE real app footage", ["M2"]),
 (66, 71, "Copy, not Send. The disclaimer is on screen. His hand pastes into his own messages.", "Nury never sends. He does.", "Tap, paste. The pad resolves.", "Nury does not send. The pastor does. Legal information only.", "REUSE footage + NEW 1 s", ["M2"]),
 (71, 74, "DAWN. The ink washes to paper. The lantern, small.", BR, "The pad fades. One soft high tone, like first light.", "Nury. An AI Crisis Response Agent", "REUSE end card, re-skinned", ["M1"]),
 (74, 90, "MEMORIAL. Paper, a deep-amber lantern, Juan's words, text only. Slow fade in and out.", "", "Near silence. Faint room tone only. No voice.", "Juan's words, unedited (text only)", "REUSE memorial card", ["M6"]),
]
B_ROWS = [
 (0, 3, "HOOK. Macro: a hand flat on a dark table. The phone lights his fingers: \"2:07 AM, Maria\".", "", "A tick, the buzz, a breath.", "2:07 AM", "NEW (vector hands)", ["M3"]),
 (3, 9, "The other hand rubs his eyes, then takes the phone. The thumb hesitates.", "He answers on the second ring.", "Cloth, breath, the tick.", "A pastor. No lawyer on the line.", "NEW (vector hands)", ["M3"]),
 (9, 16, "Hands type what Maria said. The words appear in amber at his fingertips.", "Her husband was detained last evening.", "Soft keys. A mug set down.", "The intake text, as typed. Synthetic family. Not real people.", "REUSE typing footage, framed by NEW hands", ["M3"]),
 (16, 25, "THE TOOL, UNNAMED. Thumb taps Detention. The triage card. Thumb taps Approve. He does not know what it is called yet.", "A screen he has never seen.", "Thumb taps. No music yet.", "1 Triage. Approve / Edit / Stop", "REUSE real app footage", ["M2"]),
 (25, 33, "A finger traces a citation chip in the Spanish brief, line by line, like reading.", "Her language. Every point cited.", "A fingertip scrape. Faint pad.", "2 Rights brief. Vetted sources only.", "REUSE real app footage", ["M2"]),
 (33, 43, "THE TURN. His hand freezes above the screen. The strip: rejected, regenerating, passed. The hand exhales back into motion.", "Something unsafe. Caught. He never saw it.", "Silence. A held breath. A slow tick. A low note on \"Passed\".", "Rejected. Regenerating (2 of 3). Passed.", "REUSE footage + NEW hands", ["M4"]),
 (43, 50, "THIS IS NURY, EARNED. The screen's glow becomes a lantern in his cupped hands. The dictionary card rises from it.", "This is Nury.", "The tick stops. The pad swells.", "Nury /NOO-ree/ proper noun. 1. A given name from Arabic nur, \"light\". 2. An AI crisis response agent.", "REUSE dictionary card", ["M1"]),
 (50, 62, "TECH BEAT as what is under his hands: thin lines draw out from his fingertips: tokens, Gloo AI Studio, checks, judges, a person.", "Names become tokens. Checks reject unsafe drafts. | A red team tests it. A person decides.", "Pad. A faint tick per node.", "Leak test: 90 checks per playbook, 0 found. Typed judge, ten checks: unsafe 0.89 to 0.98, safe 0.02 to 0.24. A full case: 34 to 50 s, 6 to 9 cents. Disclosure caption, verbatim.", "REUSE tech beat, restyled", ["M5"]),
 (62, 69, "His hand edits one word in the pastoral message. The checklist scrolls.", "A warm message. His to edit.", "A key tap. Pad.", "3 Attorneys. 4 Checklist. 5 Message", "REUSE real app footage", ["M2"]),
 (69, 74, "His hand copies the text, switches to his own messages, pastes. Nury's screen has no Send.", "Nury never sends. He does.", "Tap, paste. The pad resolves.", "Nury does not send. The pastor does. Legal information only.", "REUSE footage + NEW hands", ["M2"]),
 (74, 77, "End card, on dawn paper.", BR, "The pad fades.", "Nury. An AI Crisis Response Agent", "REUSE end card", ["M1"]),
 (77, 90, "MEMORIAL. Paper, a deep-amber lantern, Juan's words, text only.", "", "Near silence. Room tone only.", "Juan's words, unedited (text only)", "REUSE memorial card", ["M6"]),
]
C_ROWS = [
 (0, 3, "HOOK. Black. A large clock: \"2:07 AM\". One tick. The phone buzz.", "", "A synthesized tick, then the buzz.", "2:07 AM", "NEW (clock component)", ["M3"]),
 (3, 12, "THIS IS NURY, FIRST. The dictionary card, with one plain line under it: what it is. A thin clock stays in the corner.", "This is Nury. Watch it work at 2:07.", "The tick bed under a soft pad.", "Nury /NOO-ree/ proper noun. 1. A given name from Arabic nur, \"light\". 2. An AI crisis response agent. Five stages. A gate after each. Nothing sent.", "REUSE dictionary card + NEW line", ["M1", "M2"]),
 (12, 18, "PERSONA. A silhouette at a table, one lamp. Cut to the lit window and the family's shoes by the door. Clock: 2:08.", "A pastor. No lawyer on the line.", "Hum. The tick. A distant murmur, no words.", "A pastor. No lawyer on the line. Synthetic family. Not real people.", "NEW (vector)", ["M3"]),
 (18, 32, "THE TOOL AT SPEED. Crisis selector: Detention. Intake, triage, Approve, rights brief. Each gate is a tick of the clock: 2:09, 2:10.", "Five stages. A gate after each.", "Ticks, softer as it goes. Taps.", "1 Triage. 2 Rights brief. Approve / Edit / Stop", "REUSE real app footage + NEW clock overlay", ["M2"]),
 (32, 42, "THE TURN. The clock freezes. The strip: rejected, regenerating, passed. Silence. The tick resumes, slower.", "Rejected. He never sees that draft.", "Silence for 1 s. A slow tick.", "Rejected. Regenerating (2 of 3). Passed.", "REUSE footage + NEW sound", ["M4"]),
 (42, 54, "TECH BEAT while the clock runs: the same diagram, the clock small in the corner.", "Names become tokens. Checks reject unsafe drafts. | A red team tests it. A person decides.", "Ticks, one per node.", "Leak test: 90 checks per playbook, 0 found. Typed judge, ten checks: unsafe 0.89 to 0.98, safe 0.02 to 0.24. Disclosure caption, verbatim.", "REUSE tech beat, restyled", ["M5"]),
 (54, 66, "Attorney resources, checklist, the pastoral message. Clock: 2:11.", "A warm message. His to edit.", "Ticks. A key tap.", "3 Attorneys. 4 Checklist. 5 Message", "REUSE real app footage", ["M2"]),
 (66, 72, "Copy, not Send. Clock: 2:12. A proof line: the compute time, with the footage marked as sped up.", "Nury never sends. He does.", "The ticks stop on the last tap. The pad resolves.", "Nury does not send. The pastor does. A full case: 50 to 56 seconds (footage sped up).", "REUSE footage + NEW overlay", ["M2", "M5"]),
 (72, 75, "End card on dawn paper. The clock is gone.", BR, "The pad fades.", "Nury. An AI Crisis Response Agent", "REUSE end card", ["M1"]),
 (75, 90, "MEMORIAL. Paper, a deep-amber lantern, Juan's words, text only.", "", "Near silence. Room tone only.", "Juan's words, unedited (text only)", "REUSE memorial card", ["M6"]),
]

MUSTS = [("M1", "1. This is Nury (the name, the dictionary moment, the brand line)"), ("M2", "2. What it is (the crisis tool: five stages, a gate after each, nothing sent)"),
         ("M3", "3. The person and the tension (persona, the clock, a decision)"), ("M4", "4. The turn (a draft rejected before the pastor sees it)"),
         ("M5", "5. The technical sell, with proof (VERIFIED claims, the disclosure caption)"), ("M6", "6. The memorial (Nury Peláez, last, text only)")]

def A_frames():
    return [
     (0, F.svg(F.glow(320,200,150,90)+F.phone(320,190,84)+F.txt(320,196,"2:07 AM",14,F.INK,"middle",700,"Arial,sans-serif")+F.txt(320,216,"Maria",12,F.INK,"middle",400,"Arial,sans-serif"),"0:00",F.INK)),
     (3, F.svg(F.glow(180,170,190,120)+F.table()+F.pastor(300,225)+F.mug(430,246)+F.hand(250,258,-20,"#05070a",.6)+F.phone(250,228,34)+F.eric("2:07 AM. Maria is calling."),"0:03",F.INK)),
     (9, F.svg(F.glow(320,170,240,150)+F.family_window(320,150,.95)+F.txt(320,292,"Synthetic family. Not real people.",12,F.MUT,"middle",400,"Arial,sans-serif",True)+F.eric("Her husband was detained last evening."),"0:09",F.INK)),
     (15, F.svg(F.card_entry(330,70,True)+F.eric("This is Nury."),"0:15","#e9e2d2","#6f6a5f")),
     (22, F.svg(F.glow(320,180,170,120)+F.app(320,180,150,1)+F.txt(500,150,"1 Triage",20,F.AMB,"start",600)+F.txt(500,178,"Approve / Edit / Stop",13,F.TXT,"start",400,"Arial,sans-serif")+F.eric("Five stages. A gate after each."),"0:22",F.INK)),
     (37, F.svg(F.app(320,180,150,2,"red")+F.txt(500,150,"Rejected.",22,F.RED,"start",600)+F.txt(500,178,"Regenerating (2 of 3)",13,F.TXT,"start",400,"Arial,sans-serif")+F.eric("Unsafe draft. Rejected. He never sees it."),"0:37","#06080b")),
     (46, F.svg(F.glow(320,170,300,100,F.AMB,.12)+F.tech()+F.eric("Names become tokens before they reach the model."),"0:46",F.INK)),
     (71, F.svg(F.lantern(320,140,70,F.DAMB)+F.txt(320,250,"Nury",40,F.INK,"middle",600)+F.txt(320,282,"An AI Crisis Response Agent",15,"#5b564c","middle",400,"Arial,sans-serif"),"1:11",F.PAPER and F.PAPER, "#6f6a5f")),
     (74, F.svg(F.memorial(),"1:14",F.PAPER,"#6f6a5f")),
    ]

def B_frames():
    return [
     (0, F.svg(F.glow(320,200,160,90)+F.table(230)+F.hand(300,230,0,"#05070a",1.1)+F.phone(390,240,60)+F.txt(390,250,"2:07",15,F.INK,"middle",700,"Arial,sans-serif"),"0:00",F.INK)),
     (3, F.svg(F.glow(320,190,200,110)+F.table(250)+F.hand(250,250,-12,"#05070a",1.0)+F.phone(390,215,50)+F.eric("He answers on the second ring."),"0:03",F.INK)),
     (16, F.svg(F.glow(320,190,170,110)+F.app(320,170,135,1)+F.hand(250,300,-8,"#05070a",1.0)+F.hand(400,300,8,"#05070a",1.0)+F.eric("A screen he has never seen."),"0:16",F.INK)),
     (33, F.svg(F.app(320,170,135,2,"red")+F.hand(320,110,0,"#05070a",1.1)+F.eric("Something unsafe. Caught. He never saw it."),"0:33","#06080b")),
     (43, F.svg(F.glow(320,200,200,130)+F.lantern(320,170,110,F.AMB)+F.hand(250,260,-30,"#05070a",1.0)+F.hand(390,260,30,"#05070a",1.0)+F.eric("This is Nury."),"0:43",F.INK)),
     (50, F.svg(F.hand(110,250,10,"#05070a",.9)+"".join(f'<path d="M110 200 Q{200+i*60} {120+i*20} {260+i*70} {150}" stroke="{F.AMB}" stroke-width="2" fill="none" opacity=".8"/>' for i in range(4))+F.txt(470,160,"tokens · Gloo AI Studio",14,F.TXT,"middle",400,"Arial,sans-serif")+F.txt(470,184,"checks · judges · a person",14,F.TXT,"middle",400,"Arial,sans-serif")+F.eric("A red team tests it. A person decides."),"0:50",F.INK)),
     (69, F.svg(F.table(250)+F.phone(250,200,60,True,F.AMB)+F.phone(400,200,60,True,"#2a3140")+F.hand(325,250,0,"#05070a",1.0)+F.txt(250,300,"Nury (no Send)",11,F.MUT,"middle",400,"Arial,sans-serif")+F.txt(400,300,"his own messages",11,F.MUT,"middle",400,"Arial,sans-serif")+F.eric("Nury never sends. He does."),"1:09",F.INK)),
     (77, F.svg(F.memorial(),"1:17",F.PAPER,"#6f6a5f")),
    ]

def C_frames():
    return [
     (0, F.svg(F.clock("2:07 AM",320,200,92)+F.txt(320,240,"tick",14,F.MUT,"middle",400,"Arial,sans-serif",True),"0:00",F.INK)),
     (3, F.svg(F.card_entry(330,80,True)+F.clock("2:07",600,40,22,F.DAMB,"end")+F.txt(320,300,"Five stages. A gate after each. Nothing sent.",15,"#5b564c","middle",400,"Arial,sans-serif")+F.eric("This is Nury. Watch it work at 2:07."),"0:03","#e9e2d2","#6f6a5f")),
     (12, F.svg(F.glow(220,190,200,120)+F.table()+F.pastor(260,225)+F.family_window(500,150,.5)+F.clock("2:08",620,40,22,F.AMB,"end")+F.eric("A pastor. No lawyer on the line."),"0:12",F.INK)),
     (18, F.svg(F.glow(320,180,170,120)+F.app(320,180,150,2)+F.clock("2:09",620,40,22,F.AMB,"end")+F.txt(410,150,"1 Triage",20,F.AMB,"start",600)+F.txt(410,176,"2 Rights brief",16,F.AMB,"start",600)+F.eric("Five stages. A gate after each."),"0:18",F.INK)),
     (32, F.svg(F.app(320,180,150,2,"red")+F.clock("2:10",620,40,22,F.RED,"end")+F.txt(410,150,"clock frozen",16,F.RED,"start",600)+F.txt(410,176,"Rejected. He never",13,F.TXT,"start",400,"Arial,sans-serif")+F.txt(410,194,"sees that draft.",13,F.TXT,"start",400,"Arial,sans-serif")+F.eric("Rejected. He never sees that draft."),"0:32","#06080b")),
     (42, F.svg(F.tech()+F.clock("2:10",620,40,22,F.AMB,"end")+F.eric("Names become tokens. Checks reject unsafe drafts."),"0:42",F.INK)),
     (66, F.svg(F.glow(320,170,200,120)+F.app(260,170,130,5)+F.clock("2:12",620,40,22,F.AMB,"end")+F.txt(470,150,"A full case:",16,F.TXT,"start",400,"Arial,sans-serif")+F.txt(470,178,"50 to 56 s",30,F.AMB,"start",600)+F.txt(470,202,"(footage sped up)",12,F.MUT,"start",400,"Arial,sans-serif",True)+F.eric("Nury never sends. He does."),"1:06",F.INK)),
     (75, F.svg(F.memorial(),"1:15",F.PAPER,"#6f6a5f")),
    ]

TREATMENTS = [
 dict(id="A", title="From night to light", rows=A_ROWS, frames=A_frames,
  concept="Emotion first. The film starts in night (ink), the lantern lights at the turn of the first act, and it ends in dawn (paper). The story spine does the work: a pastor's night, one call, a decision.",
  spine="Once upon a time there was a pastor. Every day he answers what he can. One day, at 2:07 AM, a family called. Because of that he opened Nury. Because of that every stage waited for his decision. Because of that an unsafe draft never reached him. Until finally a message was ready, and he sent it by hand. And ever since then, a lantern stays lit.",
  difference="Light is the structure: ink to amber to paper. \"This is Nury\" lands after the first act, as the release. Observer camera: a room, a window, silhouettes.",
  sound="Night: low room tone, a clock tick, a phone buzz. At the lantern: the tick stops and a warm low pad enters. At the turn: silence, then a slower tick. At the end: the pad fades to one soft high tone. The memorial is near silence.",
  type_style="Large, calm, few words. Fraunces for the entry and the memorial. Captions on every beat for muted viewing.",
  feasible="New: three vector night shots (the table, the window, the dawn wash) and the ink-to-paper grade; a synthesized pad and foley; about 11 new Eric lines. Reused: the real app run, the dictionary card, the tech beat, the end card and the memorial card. Estimate for hack-video: 6 to 8 hours.",
  risks="Taste: silhouettes must stay generic (no identifiable person, no agency imagery). Time: the grade and the new shots are the long pole. Honesty: the window shot is a synthetic family and is labeled so.",
  pitch="The live pitch tonight keeps the deck. Open on slide 3 (the call) with the buzz and \"2:07 AM\", then slide 1, 2. About 10 minutes of edits.",
  pick="Pick A if you want the most feeling and the clearest arc."),
 dict(id="B", title="His hands", rows=B_ROWS, frames=B_frames,
  concept="The whole film from the pastor's side of the phone, seen only through his hands and the screen. The viewer learns what Nury is as he does. The name is withheld until the product has earned it.",
  spine="Once upon a time there was a pair of hands that answered every call. Every day they did the work alone. One day a call came at 2:07 AM. Because of that they typed a stranger's fear into a screen. Because of that the screen asked for a decision at every step. Because of that it caught something unsafe before he saw it. Until finally the hands held a lantern, and learned its name. And ever since then, nothing leaves without his say.",
  difference="Point of view, not light, is the structure. No face, no room, no window: hands, a phone, a table. \"This is Nury\" lands LATE, after the turn: an earned reveal. The sound is close and physical.",
  sound="Intimate foley: cloth, keys, a mug, a thumb on glass, breath. No music at all until the lantern lights (about 0:43), then the pad. The turn is a held breath and silence. The memorial is room tone only.",
  type_style="Almost no type until the lantern. Then the entry, the proof captions and the disclosure. Very sparse.",
  feasible="Hardest. There is no hand footage, and we have no actor. Option 1: animate flat vector hands (about 9 to 12 hours, and a risk of looking odd). Option 2: film real hands (anyone's, on a phone and a table). That needs Juan's rule: the brief says no real people, and hands are people. I would not do option 2 without his word. Eric needs about 10 new lines.",
  risks="Craft: stylized hands can look uncanny at close range. Clarity: withholding the name for 43 seconds is a risk if a judge skims. Time: the highest of the three.",
  pitch="The live pitch tonight cannot use this. It is a film idea. Keep the deck as it is.",
  pick="Pick B if you want the most distinctive film and accept the most risk."),
 dict(id="C", title="The clock", rows=C_ROWS, frames=C_frames,
  concept="Say it, then prove it. The film tells the viewer what Nury is in the first ten seconds, then shows it working against a visible clock that starts at 2:07 AM. The clock is the tension.",
  spine="Once upon a time it was 2:07 AM. Every minute, a family waited. But one day a pastor had no lawyer on the line. Because of that he used five stages, one minute at a time. Because of that an unsafe draft was stopped. Because of that a message was ready. Until finally he sent it himself, by hand. And ever since then, the clock stops at dawn.",
  difference="Clarity first, tension second: the opposite order from A and B. A visible clock sets the pace and the cuts. The clock is a device, not a product claim: the footage is sped up and labeled, and the only measured number on screen is the real compute time (50 to 56 s).",
  sound="A synthesized tick bed under everything. It slows at the turn, goes silent for one second, and stops at the end card. A pad enters only at the dictionary card and resolves at the end. The memorial is near silence.",
  type_style="The clock is the typographic character: large, amber, tabular figures. One plain line says what Nury is. Captions throughout.",
  feasible="Most feasible. New: a clock component (Remotion `interpolate` and `spring`), a tick sound, three vector shots (the table and the window). About 9 new Eric lines. Estimate for hack-video: 4 to 6 hours.",
  risks="Honesty: a story clock from 2:07 to 2:12 can read as \"five minutes to a case\". We say \"footage sped up\" and show the real 34 to 50 s. Taste: the least emotional of the three. Clarity: the strongest.",
  pitch="The live pitch tonight can adopt this almost as is: start the deck with a 2:07 AM clock. The deck already says what Nury is up front on slide 2.",
  pick="Pick C if you want the safest build and the clearest first ten seconds."),
]

SOURCES = [
 ("Story spine", "Once upon a time / Every day / But one day / Because of that (x3) / Until finally / And ever since then", "WUNC News (NPR), \"Meet the creator of the Story Spine, an 8-sentence tool to create and analyze stories\", 2026-06-23", "https://www.wunc.org/2026-06-23/meet-the-creator-of-the-story-spine-an-8-sentence-tool-to-create-and-analyze-stories", "The eight sentence starters, in that order. I used the spine to write each treatment's one-paragraph story."),
 ("Pixar rules", "\"Come up with your ending before you figure out your middle.\" (#7) \"What is your character good at, comfortable with? Throw the polar opposite at them.\" (#6) \"Why must you tell THIS story?\" (#14)", "Emma Coats, 22 Rules of Storytelling (via Laughing Squid)", "https://laughingsquid.com/22-rules-of-storytelling-by-pixar-storyboard-artist/", "We wrote the ending first: dawn, then the memorial. The pastor is good at answering alone; the 2:07 AM call with no lawyer is the polar opposite."),
 ("Say what it is", "\"Briefly say what you are doing and why.\" \"A common error is to avoid describing what you do until far into the presentation. That is always a mistake.\" \"an audience cannot read a slide AND listen to you simultaneously.\"", "Geoff Ralston, A Guide to Demo Day Presentations, Y Combinator, 2016-07-25", "https://www.ycombinator.com/blog/guide-to-demo-day-pitches/", "This is the case for C (say it first) and the warning against B (withholding the name for 43 seconds). It also argues for few words on screen."),
 ("Problem, agitate, solve", "\"Identify a problem.\" \"Agitate that problem.\" \"Trot out the solution.\"", "Copyblogger, Problem-Agitate-Solve", "https://copyblogger.com/problem-agitate-solve/", "The page does not warn about over-agitating, so the limit is ours: we agitate through time and consequence (the clock, the call), never by showing a family in distress."),
 ("Hackathon videos", "\"Production quality does not affect your judging score.\" \"Show actual functionality, not just slides.\"", "Video Production Guide for Hackathons, AI Tinkerers", "https://aitinkerers.org/docs/public/video_production_guide.md?markdown=1", "An honest counterweight to a cinematic reset. The real app run must stay legible in every treatment, and none may trade clarity for mood."),
 ("Sound design", "\"Silence can be the stronger choice when small details or vulnerability matter.\" \"Dynamic range and contrast often create more tension than constant volume.\" \"Footsteps, cloth, and hand props give a scene timing and intimacy.\"", "FilmDaft, What Is Sound Design in Film?", "https://filmdaft.com/what-is-sound-design-in-film-definition/", "The audio arc in each treatment: sparse and tense, then release. B leans on foley. All three use a held silence before the turn."),
 ("Editing", "\"a cognitive phenomenon by which viewers derive more meaning from the interaction of two sequential shots than from a single shot in isolation\"", "Wikipedia, Kuleshov effect", "https://en.wikipedia.org/wiki/Kuleshov_effect", "The cut from the pastor's hands to the lit window in A and C does the emotional work without a face."),
 ("Motion in Remotion", "spring(): \"A physics-based animation primitive.\" interpolate(): \"Allows you to map a range of values to another using a concise syntax.\"", "Remotion documentation", "https://www.remotion.dev/docs/spring and https://www.remotion.dev/docs/interpolate", "The clock in C, the lantern's flame and the card reveals in all three are `interpolate` and `spring`: nothing new to learn, which is why they are feasible."),
]
