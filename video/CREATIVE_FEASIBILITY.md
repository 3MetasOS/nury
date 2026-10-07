# Creative reset: producer's feasibility note (hack-video)

Inputs: presentation/CREATIVE_BRIEF.md. Assets kept: app footage, opener and dictionary card, tech beat, memorial card, Eric's lines. Look stills: `video/review/lookdev/`. Sound demo: `video/sound/sound_demo.wav`.
Hours are my build hours in Remotion and ffmpeg, including re-time and one full render (2 to 4 min). Not counting hack-ninja's writing.

## What I can build (and the tools)
- **Camera moves**: slow push-in, parallax between layers, handheld drift (small noise on translate and rotate), rack focus (blur in/out). All in Remotion, deterministic.
- **Light**: radial light that flickers (noise-driven), a lit screen spilling onto a surface, a color grade that shifts across the film (ink to amber to paper). Film grain and vignette overlays.
- **Type as a character**: Fraunces, big, few words, timed to the VO.
- **Sound**: all synthesized in code, so there is nothing to license (see list). I cannot hear audio, so tune by waveform and by Juan's or hack-ninja's ears.
- **Cannot do well**: realistic people, faces, hands, real rooms. No stock photos of detainees and no real people are allowed, so the story stays in light, objects, phone screens and type.

## Sound list (every sound, source, license)
| Sound | Source | License |
|---|---|---|
| Room tone (low, brown noise) | `video/sound/build_sound.sh`, ffmpeg `anoisesrc` | Generated in code, no third-party material |
| Clock ticks that slow down | Same script, 25 ms noise burst, delayed copies | Generated in code |
| Phone buzz (two pulses, 140 Hz with flutter) | Same script, ffmpeg `sine` and `tremolo` | Generated in code |
| Warm pad when the lantern lights (A2, E3, A3, C#4, slow swell) | Same script, four sines | Generated in code |
| Eric narration | ElevenLabs premade voice Eric, Starter plan | Plan license, commercial use |
| Memorial | None. Text only. | |
Possible additions, still synthesized: breath-held silence (a 1.2 s duck of the room tone), page-turn or key tap foley (noise bursts), dawn air (high-passed noise swell).

## The three treatments: what is possible
| | A. From night to light | B. The pastor's hands only | C. The clock |
|---|---|---|---|
| What I build new | Night opener (phone-lit room, light spill, push-in), lantern ignition, a grade that goes from ink to dawn paper across the film, sound arc, motion on the demo scenes | Vector hands and phone, shot-by-shot hand animation, the app screen inside the phone | Big clock 2:07 to 2:12, a stage bar per minute, ticks, app footage as inserts |
| Reuses | Footage, opener, tech beat, memorial, Eric | Footage (as the phone screen), Eric | Footage, tech beat, memorial, Eric |
| Hours | 8 to 10 | 14 to 20 | 6 to 8 |
| By the prelim pitch (Oct 7 evening) | Yes, if the treatment is picked in about 2 hours | No | Yes |
| By the finalist film (Oct 8, 09:00) | Yes | Risky: drawn hands can look uncanny; needs taste checks | Yes |
| Biggest risk | The six musts plus a night opener crowd 90 s; the opener and dictionary card may need to merge | Hands drawn in vectors may look cheap, and it ties up the most hours | The "five minutes" claim: our stages run 5 to 20 s of machine time each; the clock must not claim a measured five minutes. Use 'one stage at a time', or measure it |
| Honesty check | Fine: no new claims | Fine | Needs care as above |

## Recommendation
A, with one idea borrowed from C: the clock tick as the sound of the night, slowing as the lantern lights. Same 90 s, the six musts intact, the tech beat and memorial untouched, the grade from ink to paper answers "the all-dark look is heavy". B only if Juan wants it and accepts the risk.

## Timing sketch for A (90 s, hack-ninja owns the final beat sheet)
0:00 to 0:05 night, phone lights, 2:07 AM (room tone, buzz) · 0:05 to 0:10 lantern lights, "This is Nury." and the name entry (pad swells) · 0:10 to 0:34 the call and the first stages on the dark app, grade warming · 0:34 to 0:43 the guardrail turn · 0:43 to 0:55 the tech beat on paper · 0:55 to 1:11 attorneys, message, Copy, no Send · 1:11 to 1:30 memorial on dawn paper.
This needs the opener (5 s) to take over from the lock card (5 s): one of them goes. I would keep the opener and fold the 2:07 phone into the night shot.

## What I need to start
1. Juan's pick. 2. hack-ninja's beat sheet for the picked treatment. 3. The final app footage (go from hack-sensei). If A is picked now I start the night shot and the sound arc, which do not depend on the footage.
