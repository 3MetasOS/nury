// Treatment A, "From night to light": the 90 s film built to presentation/FINALIST_SCRIPT.md (table 1: memorial option 3; table 2: option 2).
// Eric lines: public/arc/L1..L11.wav. Sound: public/arc/snd/*.wav (all synthesized, sound/build_arc_sound.py). Footage: public/run.mp4 + marks.json.
import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, serif, sans, ease, FPS, Fade, End, Memorial, Tech, Aside, useFonts, type Data, type Marks} from './Nury';
import {OffthreadVideo, Freeze} from 'remotion';

const INK = '#0d1015', GREY = '#d9d4c8', PAPER = '#f7f3ea';
type S = {id: string; dur: number; hold?: string; sub?: string; aside?: {text: string; at: number; x: number; y: number; arrow?: any}; kind: string; trim?: number; from?: [string, number]; to?: [string, number]; label?: string; start?: number};
const BASE: S[] = [
  {id: 'hook', kind: 'night', dur: 3},
  {id: 'persona', kind: 'persona', dur: 7, trim: 1},
  {id: 'stakes', kind: 'stakes', dur: 7, trim: 1, from: ['selector', 3.7], to: ['start', 0.3]},
  {id: 'nury', kind: 'name', dur: 8},
  {id: 'tool', kind: 'tool', dur: 10, trim: 2},
  {id: 'rights', kind: 'clip', dur: 7, trim: 2, from: ['gate2', 0], to: ['approve2', 0.4], label: 'Rights brief', sub: 'Vetted sources only.', aside: {text: 'every point cited', at: 1.5, x: 1130, y: 640, arrow: 'left'}},
  {id: 'turn', kind: 'clip', dur: 10, hold: 'reject', from: ['approve1', 1], to: ['gate2', 1], label: 'Rejected.\nRegenerated.\nPassed.', sub: 'The pastor never sees the rejected draft.'},
  {id: 'tech', kind: 'tech', dur: 12},
  {id: 'stages', kind: 'clip', dur: 8, trim: 2, from: ['approve2', 0.4], to: ['approve5', 0.4], label: 'Contacts.\nChecklist.\nMessage.'},
  {id: 'copy', kind: 'clip', dur: 6, from: ['approve5', 0.4], to: ['end', 0], label: 'Legal information only.'},
  {id: 'dawn', kind: 'dawn', dur: 4},
  {id: 'memorial', kind: 'memorial', dur: 8},
];

// ---- voice plan: Eric's lines placed against the scenes (presentation/SCRIPT_REVIEW.md, section 3). Lengths are the measured ones (vo/arc/durations.json). ----
const LEN: Record<string, number> = {L1: 2.23, L2: 2.0, E1: 1.25, L3: 0.88, L4: 1.76, E4: 2.14, E5: 1.39, L5: 2.04, E6: 1.39, L6: 2.28, E7: 1.63, L7: 2.88, L8: 2.04, E8: 2.18, L9: 1.44, E9: 1.39, L10: 2.51, L11: 1.81};
const PLAN: [string, string, number][] = [ // line, scene, seconds after the scene starts
  ['L1', 'persona', 0.5], ['L2', 'persona', 5.6], ['E1', 'stakes', 2.9], ['L3', 'nury', 0.6], ['L4', 'nury', 4.0], ['E4', 'tool', 1.0], ['E5', 'tool', 6.5],
  ['L5', 'rights', 1.0], ['E6', 'rights', 3.8], ['L6', 'turn', 1.3], ['E7', 'turn', -1], ['L7', 'tech', 0.5], ['L8', 'tech', 7.0],
  ['E8', 'stages', 0.2], ['L9', 'stages', 3.2], ['E9', 'stages', 5.6], ['L10', 'copy', 0.5], ['L11', 'dawn', 0.5]];
export const planVoice = (d: Data, scenes: any[]) => {
  const by: Record<string, any> = Object.fromEntries(scenes.map((s) => [s.id, s]));
  const trimOn = (d.memorial?.option ?? 3) === 2 && d.memorial?.approved === true; // table 2 drops E9
  const techOn = d.tech?.approved === true, m = d.marks, rt = (k: string) => (d.voice as any)?.retakes === true ? ({L3: 1.67, L9: 2.23} as any)[k] : undefined;
  const out: {k: string; start: number; end: number; scene: string}[] = []; let prev = -9;
  for (const [k, sc, off] of PLAN) {
    const s = by[sc]; if (!s || (k === 'E9' && trimOn) || ((k === 'L7' || k === 'L8') && !techOn)) continue;
    const len = rt(k) ?? LEN[k]; let at = off;
    if (k === 'E7') { // land just before "Passed" shows (the gate-2 mark) when we have the footage mark, else near the end of the beat
      let passed = s.dur - 1.0;
      if (m.reject != null && m.gate2 != null && m.approve1 != null) { const a = m.approve1 + 1, b = m.gate2 + 1, mm = Math.min(Math.max(m.reject - 0.4, a), b), d2 = Math.min(b - mm, s.dur - 1); passed = (s.dur - d2) + (m.gate2 - mm); }
      at = passed - len - 0.35;
    }
    let abs = s.start + Math.max(0, at); abs = Math.max(abs, prev + 0.5); // never closer than 0.5 s to the line before; a line may run past the end of its scene
    out.push({k, start: abs, end: abs + len, scene: sc}); prev = abs + len;
  }
  return out;
};
export const voiceReport = (d: Data, scenes: any[]) => {
  const v = planVoice(d, scenes), speech = v.reduce((a, x) => a + x.end - x.start, 0); const gaps: string[] = []; let longest = 0, prev = 0, prevScene = 'start';
  for (const x of v) { const g = x.start - prev; if (g > 1.2) gaps.push(`${prev.toFixed(1)}-${x.start.toFixed(1)} s (${g.toFixed(1)}) before ${x.k} [${prevScene}]`); if (prev > 0 && g > longest) longest = g; prev = x.end; prevScene = x.scene; }
  return {lines: v.map((x) => `${x.k} ${x.start.toFixed(1)}-${x.end.toFixed(1)}`).join(' | '), speech: +speech.toFixed(1), gaps, longest: +longest.toFixed(1)};
};

export const buildA = (d: Data) => {
  const opt = d.memorial?.option ?? 3, approved = d.memorial?.approved === true;
  const trimOn = opt === 2 ? 1 : opt === 1 ? 0.5 : 0; // table 2 takes rows 2,3,5,6,9 down by 1,1,2,2,2 (option 1 takes half)
  let t = 0;
  const scenes = BASE.map((s) => {
    let dur = s.dur - (s.trim ?? 0) * trimOn;
    if (s.kind === 'memorial') dur = approved ? ({3: 8, 2: 16, 1: 12} as any)[opt] ?? 8 : 0;
    if (s.kind === 'dawn' && !approved) dur = 12; // no memorial yet: the end card holds to 1:30
    const r = {...s, dur, start: t}; t += dur; return r;
  }).filter((s) => s.dur > 0);
  return {scenes, total: t};
};


// The real app, LARGE: the phone window is 645x900 (83% of the frame height) and the video is zoomed 1.55x so the strip, the card and the gate text can be read.
// Caption is a quiet line on the right. `y` = how far down the app (0 to 1) the window starts.
const AppClip: React.FC<{s: any; marks: Marks; y?: number; file?: string}> = ({s, marks, y = 0.0, file = 'run.mp4'}) => {
  const a = marks[s.from[0]] + s.from[1], b = marks[s.to[0]] + s.to[1];
  const m = s.hold && marks[s.hold] != null ? Math.min(Math.max(marks[s.hold] - (s.holdLead ?? 0.4), a), b) : null; // hold = a mark: from there, play in real time
  const f = useCurrentFrame();
  const W = 645, H = 900, VH = W * 1688 / 780;
  const slide = interpolate(f, [0, 20], [18, 0], {easing: ease, extrapolateRight: 'clamp'});
  const seg = (from: number, to: number, durS: number, rate: number) => {
    const play = Math.floor(((to - from) / rate) * FPS), full = Math.round(durS * FPS);
    const v = <OffthreadVideo src={staticFile(file)} startFrom={Math.round(from * FPS)} playbackRate={rate} muted style={{width: W, height: VH, marginTop: -y * VH}} />;
    return play >= full ? v : (<><Sequence durationInFrames={Math.max(1, play)}>{v}</Sequence><Sequence from={Math.max(1, play)}><Freeze frame={Math.max(1, play) - 1}>{v}</Freeze></Sequence></>);
  };
  let body: React.ReactNode;
  if (m != null && m > a + 0.5) {
    // fast through the wait, then REAL TIME for the last d2 seconds before the end mark (the READY gate, the strip, the tap): d2 is the part from the hold mark, capped so the fast part keeps at least 1.2 s
    const d2 = Math.min(b - m, s.dur - 1.2), d1 = s.dur - d2, m2 = b - d2;
    body = (<>
      <Sequence durationInFrames={Math.round(d1 * FPS)}>{seg(a, m2, d1, Math.min(8, Math.max(0.85, (m2 - a) / d1)))}</Sequence>
      <Sequence from={Math.round(d1 * FPS)}>{seg(m2, b, d2, 1)}</Sequence>
    </>);
  } else body = seg(a, b, s.dur, Math.min(4, Math.max(0.85, (b - a) / s.dur)));
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', left: 330, top: 90, width: W, height: H, borderRadius: 30, overflow: 'hidden', boxShadow: '0 40px 90px rgba(70,45,10,.30), 0 8px 24px rgba(70,45,10,.16), 0 0 0 1px rgba(13,16,21,.16)', transform: `translateY(${slide}px)`}}>
        {body}
      </div>
      {s.label && (
        <div style={{position: 'absolute', left: 1060, top: 0, bottom: 0, width: 700, display: 'grid', alignContent: 'center', gap: 22}}>
          <div style={{fontFamily: serif, fontWeight: 600, fontSize: 76, lineHeight: 1.12, color: C.text, whiteSpace: 'pre-line', textWrap: 'balance' as any, opacity: interpolate(f, [8, 28], [0, 1], {extrapolateRight: 'clamp'})}}>{s.label}</div>
          {s.sub && <div style={{fontFamily: sans, fontSize: 34, color: C.muted, opacity: interpolate(f, [20, 40], [0, 1], {extrapolateRight: 'clamp'})}}>{s.sub}</div>}
        </div>
      )}
      {s.aside && <Aside text={s.aside.text} x={s.aside.x} y={s.aside.y} arrow={s.aside.arrow ?? 'left'} opacity={interpolate(f, [s.aside.at * FPS, s.aside.at * FPS + 14], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />}
    </AbsoluteFill>
  );
};

// ---- night shots (vector, no faces) ----
const Grain: React.FC<{o?: number}> = ({o = 0.09}) => (
  <svg width="100%" height="100%" style={{position: 'absolute', inset: 0, opacity: o, mixBlendMode: 'overlay'}}>
    <filter id="g2"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch" /><feColorMatrix type="saturate" values="0" /></filter>
    <rect width="100%" height="100%" filter="url(#g2)" />
  </svg>
);
const Vig: React.FC<{s?: number}> = ({s = 0.8}) => <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 55%, transparent 38%, rgba(0,0,0,${s}) 100%)`}} />;
const PhoneOnTable: React.FC<{x: number; y: number; lift?: number; glow?: number}> = ({x, y, lift = 0, glow = 1}) => (
  <div style={{position: 'absolute', left: x, top: y - lift, width: 300, height: 210, borderRadius: 24, background: '#05070a', transform: `perspective(900px) rotateX(${58 - lift / 3}deg) rotateZ(-8deg)`, boxShadow: `0 0 ${90 * glow}px rgba(150,185,235,${0.55 * glow})`, display: 'grid', placeItems: 'center'}}>
    <div style={{width: 278, height: 188, borderRadius: 16, background: 'linear-gradient(180deg,#dbe8fb,#a9c4ec)', display: 'grid', placeItems: 'center', color: '#0b1220', textAlign: 'center', fontFamily: sans}}>
      <div><div style={{fontFamily: serif, fontSize: 58, fontWeight: 600, lineHeight: 1}}>2:07</div><div style={{fontSize: 18, marginTop: 6}}>Maria  ·  calling</div></div>
    </div>
  </div>
);
const NightHook: React.FC = () => {
  const f = useCurrentFrame(), t = f / FPS;
  const on = interpolate(t, [0.5, 0.9], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const buzz = (t > 1.6 && t < 1.95) || (t > 2.3 && t < 2.65) ? Math.sin(t * 90) * 3 : 0;
  return (
    <AbsoluteFill style={{background: '#06080b'}}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 640, height: 440, background: 'linear-gradient(180deg,#141a23,#080b10)', borderTop: '1px solid rgba(180,200,230,.08)'}} />
      <div style={{position: 'absolute', left: 520, top: 610, width: 880, height: 340, borderRadius: '50%', background: 'radial-gradient(ellipse, rgba(150,185,235,.30), transparent 70%)', filter: 'blur(12px)', opacity: on}} />
      <div style={{opacity: on, transform: `translate(${buzz}px, ${buzz / 2}px)`}}><PhoneOnTable x={810} y={520} /></div>
      <Vig s={0.9} /><Grain o={0.11} />
      <div style={{position: 'absolute', left: 150, bottom: 110, fontFamily: serif, fontSize: 64, color: 'rgba(236,231,220,.95)', opacity: interpolate(t, [0.9, 1.4], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>2:07 AM</div>
    </AbsoluteFill>
  );
};
const Persona: React.FC<{dur: number}> = ({dur}) => {
  const f = useCurrentFrame(), t = f / FPS;
  const reach = interpolate(t, [dur * 0.35, dur * 0.7], [0, 1], {easing: ease, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const lift = interpolate(t, [dur * 0.72, dur * 0.95], [0, 1], {easing: ease, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const push = interpolate(t, [0, dur], [1, 1.05]);
  const px = 960, py = 560 - lift * 120;               // phone position
  const hx = 1700 - reach * 640, hy = 760 - reach * 140 - lift * 120; // the hand slides in from the right edge
  return (
    <AbsoluteFill style={{background: '#07090c', transform: `scale(${push})`, transformOrigin: '50% 60%'}}>
      <div style={{position: 'absolute', left: 1180, top: 60, width: 560, height: 620, borderRadius: '50%', background: 'radial-gradient(ellipse, rgba(232,163,61,.38), transparent 68%)', filter: 'blur(10px)'}} />
      <svg viewBox="0 0 1920 1080" width="1920" height="1080" style={{position: 'absolute', inset: 0}}>
        <rect x="0" y="700" width="1920" height="380" fill="#0f141b" />
        <rect x="0" y="696" width="1920" height="6" fill="rgba(232,163,61,.24)" />
        <path d="M1340 700 L1340 500 L1296 420 L1444 420 L1400 500 L1400 700 Z" fill="#171c25" />
        <ellipse cx="1370" cy="420" rx="86" ry="22" fill="#e8a33d" opacity=".92" />
        <rect x="700" y="640" width="62" height="64" rx="8" fill="#10151c" stroke="rgba(236,231,220,.2)" />
        <path d="M762 655 q26 4 0 36" stroke="rgba(236,231,220,.2)" strokeWidth="6" fill="none" />
        {/* the hand: a shadow shape with a warm rim from the lamp side, forearm entering from the lower right */}
        {(() => {
          const ex = hx + 30, ey = hy + 18; // wrist / palm centre
          const fingers = [[-88, -36], [-96, -10], [-90, 16], [-78, 40]]; // fingertip offsets from the palm
          const draw = (col: string, extra: number) => (<g stroke={col} fill={col} strokeLinecap="round">
            <line x1="1930" y1="1110" x2={ex + 40} y2={ey + 10} strokeWidth={122 + extra} />
            <circle cx={ex} cy={ey} r={54 + extra / 2} stroke="none" />
            {fingers.map(([dx, dy], i) => <line key={i} x1={ex - 10} y1={ey + (i - 1.5) * 18} x2={ex + dx} y2={ey + dy} strokeWidth={26 + extra} />)}
            <line x1={ex + 10} y1={ey + 36} x2={ex - 46} y2={ey + 78} strokeWidth={28 + extra} />
          </g>);
          return <>{draw('rgba(232,163,61,.34)', 6)}{draw('#090c10', 0)}</>;
        })()}
      </svg>
      <PhoneOnTable x={px} y={py} lift={lift * 40} glow={0.9} />
      <Vig s={0.85} /><Grain o={0.1} />
      <div style={{position: 'absolute', left: 150, bottom: 100, fontFamily: serif, fontSize: 52, color: 'rgba(236,231,220,.95)', opacity: interpolate(t, [1, 1.6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>A pastor. No lawyer on the line.</div>
    </AbsoluteFill>
  );
};
// a lit window and shoes by a door: the family is felt, never seen
const WindowShot: React.FC<{dur: number}> = ({dur}) => {
  const f = useCurrentFrame(), t = f / FPS, push = interpolate(t, [0, dur], [1, 1.07]);
  return (
    <AbsoluteFill style={{background: '#080a0e', transform: `scale(${push})`, transformOrigin: '50% 40%'}}>
      <div style={{position: 'absolute', left: 560, top: 140, width: 800, height: 520, background: 'linear-gradient(180deg,#f3c77c,#d9923c)', borderRadius: 6, boxShadow: '0 0 160px rgba(232,163,61,.45)'}} />
      {[0, 1].map((i) => <div key={i} style={{position: 'absolute', left: 560 + 398 * i, top: 140, width: 4, height: 520, background: '#0a0d12'}} />)}
      <div style={{position: 'absolute', left: 560, top: 396, width: 800, height: 4, background: '#0a0d12'}} />
      <div style={{position: 'absolute', left: 560, top: 140, width: 200, height: 520, background: 'linear-gradient(90deg, rgba(10,13,18,.55), transparent)'}} />
      <div style={{position: 'absolute', left: 1160, top: 140, width: 200, height: 520, background: 'linear-gradient(270deg, rgba(10,13,18,.55), transparent)'}} />
      <div style={{position: 'absolute', left: 520, top: 664, width: 880, height: 16, background: '#10151c'}} />
      <div style={{position: 'absolute', left: 0, right: 0, top: 680, bottom: 0, background: '#07090c'}} />
      {/* shoes by the door: two adult, two small */}
      {[[820, 60, 22], [900, 56, 20], [1010, 34, 14], [1060, 30, 13]].map(([x, w, h], i) => <div key={i} style={{position: 'absolute', left: x, top: 920 - h, width: w, height: h, borderRadius: '40% 60% 20% 20%', background: '#12171f', border: '1px solid rgba(236,231,220,.08)'}} />)}
      <Vig s={0.8} /><Grain o={0.1} />
      <div style={{position: 'absolute', left: 150, bottom: 90, fontFamily: sans, fontSize: 30, color: 'rgba(167,159,141,.95)'}}>Synthetic family. Not real people.</div>
    </AbsoluteFill>
  );
};
// This is Nury: the lantern lights, the dictionary card builds on paper-grey
const NameCard: React.FC = () => {
  const f = useCurrentFrame(), t = f / FPS;
  const fi = (a: number, b: number) => interpolate(t, [a, b], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const lit = interpolate(t, [0.1, 1.0], [0.2, 1], {easing: ease, extrapolateRight: 'clamp'});
  const dark = t < 2.2 ? '#ece7dc' : INK; // text colour follows the washing background
  const move = interpolate(t, [1.6, 2.4], [0, 1], {easing: ease, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', textAlign: 'center'}}>
      <AbsoluteFill style={{background: 'radial-gradient(700px 520px at 50% 40%, rgba(255,214,140,.55), transparent 70%)', opacity: interpolate(t, [0.6, 1.6, 3.4], [0, 1, 0.25], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}} />
      <Img src={staticFile(t < 2.4 ? 'logo-mark.svg' : 'logo-mark-paper.svg')} style={{position: 'absolute', left: 960 - 75 - move * 380, top: 450 - move * 250, width: 150 - move * 70, height: 150 - move * 70, opacity: lit}} />
      <div style={{position: 'absolute', top: 640, fontFamily: serif, fontWeight: 600, fontSize: 112, color: '#ece7dc', opacity: interpolate(t, [0.3, 0.7, 1.7, 2.1], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>This is Nury.</div>
      <div style={{position: 'absolute', top: 290, left: 0, right: 0, display: 'grid', justifyItems: 'center', gap: 14, color: dark}}>
        <div style={{display: 'flex', alignItems: 'baseline', gap: 28, opacity: fi(2.2, 2.9)}}>
          <span style={{fontFamily: serif, fontWeight: 600, fontSize: 116}}>Nury</span>
          <span style={{fontFamily: sans, fontSize: 36, color: C.muted}}>/NOO-ree/ <i style={{fontFamily: serif}}>proper noun</i></span>
        </div>
        <div style={{fontFamily: serif, fontSize: 42, marginTop: 14, opacity: fi(3.2, 3.8)}}>1. A given name from Arabic <i>nūr</i>, “light”.</div>
        <div style={{fontFamily: serif, fontSize: 42, opacity: fi(4.2, 4.8)}}>2. An AI crisis response agent.</div>
        <div style={{fontFamily: sans, fontSize: 24, color: C.muted, opacity: fi(5.0, 5.5)}}>see also: lantern</div>
        <div style={{fontFamily: serif, fontSize: 44, color: C.amber, marginTop: 34, opacity: fi(5.6, 6.3)}}>Five stages. A gate after each. Nothing sent.</div>
      </div>
    </AbsoluteFill>
  );
};

// ---- grade: ink to paper, one way ----
const mix = (a: string, b: string, k: number) => { const h = (x: string, i: number) => parseInt(x.slice(1 + i * 2, 3 + i * 2), 16); return '#' + [0, 1, 2].map((i) => Math.round(h(a, i) + (h(b, i) - h(a, i)) * k).toString(16).padStart(2, '0')).join(''); };
// keyframes: [seconds, colour]. Ink, a warm brown as the lantern lights, an amber glow, warm paper, paper. No neutral grey anywhere.
const Grade: React.FC<{k: [number, string][]}> = ({k}) => {
  const t = useCurrentFrame() / FPS;
  let bg = k[0][1];
  for (let i = 0; i < k.length - 1; i++) if (t >= k[i][0]) bg = t >= k[i + 1][0] ? k[i + 1][1] : mix(k[i][1], k[i + 1][1], (t - k[i][0]) / (k[i + 1][0] - k[i][0]));
  return <AbsoluteFill style={{background: bg}} />;
};

const Snd: React.FC<{f: string; at: number; v?: number; dur?: number; fadeOut?: number; dir?: string}> = ({f, at, v = 0.3, dur, fadeOut = 0, dir = 'arc/snd/'}) => (
  <Sequence from={Math.round(at * FPS)} durationInFrames={dur ? Math.round(dur * FPS) : undefined} layout="none">
    <Audio src={staticFile(`${dir}${f}.wav`)} volume={(fr) => v * (fadeOut && dur ? Math.min(1, (dur * FPS - fr) / (fadeOut * FPS)) : 1)} />
  </Sequence>
);

export const NuryA: React.FC<{data: Data}> = ({data}) => {
  useFonts();
  const {scenes} = buildA(data);
  const by: Record<string, any> = Object.fromEntries(scenes.map((s: any) => [s.id, s]));
  const st = (id: string) => by[id]?.start ?? 0, dur = (id: string) => by[id]?.dur ?? 0;
  const memorialOn = !!by.memorial;
  const techOn = data.tech?.approved === true;
  const sound = [
    <Snd key="room" f="room" at={0} v={0.5} dur={st('nury') + 1.5} fadeOut={1.5} />,
    <Snd key="buzz1" f="buzz" at={1.6} v={0.5} />, <Snd key="buzz2" f="buzz" at={2.3} v={0.5} />,
    <Snd key="tick0" f="tick" at={0.8} v={0.3} />,
    ...[...Array(7)].map((_, k) => <Snd key={'tp' + k} f="tick" at={st('persona') + k} v={0.25} />),
    ...[...Array(7)].map((_, k) => <Snd key={'ts' + k} f="tick" at={st('stakes') + k} v={0.25} />),
    <Snd key="creak" f="creak" at={st('persona') + 1.2} v={0.35} />, <Snd key="breath" f="breath" at={st('persona') + 2.6} v={0.3} />,
    <Snd key="keys" f="keys" at={st('stakes')} v={0.4} dur={3.5} />,
    <Snd key="pad" f="pad" at={st('nury')} v={0.14} dur={st('turn') - st('nury')} fadeOut={0.6} />,
    <Snd key="tap1" f="tap" at={st('tool') + dur('tool') - 3} v={0.5} />,
    ...[1.5, 2.2, 2.9, 3.6, 4.3].map((a) => <Snd key={'pg' + a} f="page" at={st('rights') + a} v={0.3} />),
    ...[0.8, 2.8, 4.8, 6.8].map((a) => <Snd key={'sl' + a} f="tick" at={st('turn') + a} v={0.3} />),
    <Snd key="note" f="note" at={st('turn') + 6.5} v={0.5} />,
    <Snd key="padb" f="pad_back" at={st('turn') + 8.5} v={0.14} dur={st('copy') + 3.2 - (st('turn') + 8.5)} fadeOut={0.5} />,
    ...[0.2, 1.0, 2.4, 3.6, 5.0, 6.4].map((a) => <Snd key={'tt' + a} f="tick" at={st('tech') + a} v={0.22} />),
    <Snd key="tap2" f="tap" at={st('stages') + dur('stages') - 2.5} v={0.5} />,
    <Snd key="paste" f="paste" at={st('copy') + 3.0} v={0.5} />, <Snd key="res" f="resolve" at={st('copy') + 3.0} v={0.14} dur={dur('copy') + 2 - 3} fadeOut={1.5} />,
    <Snd key="dawn" f="dawn" at={st('dawn')} v={0.16} />,
    ...(memorialOn ? [<Snd key="rt" f="room" at={st('memorial')} v={0.03} dur={dur('memorial')} />] : []),
  ];
  const retake = (k: string) => (data.voice as any)?.retakes === true && (k === 'L3' || k === 'L9') ? k + '_retake' : k; // voice.json {retakes:true} = slower L3 and L9
  const voice = planVoice(data, scenes).map((x) => <Snd key={x.k} f={retake(x.k)} at={x.start} v={1} dir="arc/" />);
  const caps = ['Leak test: 90 checks per playbook, 0 found', 'Judge test: unsafe 0.89 to 0.98, safe 0.02 to 0.24', data.tech?.package ?? 'A full package: 33 to 49 s, 6 to 9 cents'];
  return (
    <AbsoluteFill>
      <Grade k={[[0, INK], [st('nury'), INK], [st('nury') + 1.2, '#4a2f14'], [st('nury') + 2.3, '#dfa04c'], [st('nury') + 3.6, '#f3e6cc'], [st('tool') + 4, '#f5ecd9'], [st('dawn'), PAPER]]} />
      {scenes.map((s: any) => (
        <Sequence key={s.id} from={Math.round(s.start * FPS)} durationInFrames={Math.round(s.dur * FPS)}>
          {s.kind === 'night' && <NightHook />}
          {s.kind === 'persona' && <Fade dur={s.dur}><Persona dur={s.dur} /></Fade>}
          {s.kind === 'stakes' && (<>
            <Sequence durationInFrames={Math.round(s.dur * FPS * 0.5)}><AbsoluteFill style={{background: '#07090c'}}><AppClip s={{...s, dur: s.dur * 0.5, label: undefined, from: ['intake_empty', 0.3], to: ['end', 0]}} marks={data.uimarks ?? data.marks} file={data.uimarks ? 'ui.mp4' : 'run.mp4'} y={data.uimarks ? 0.05 : 0} /></AbsoluteFill></Sequence>
            <Sequence from={Math.round(s.dur * FPS * 0.5)}><WindowShot dur={s.dur * 0.5} /></Sequence>
          </>)}
          {s.kind === 'name' && <NameCard />}
          {s.kind === 'tool' && (<Fade dur={s.dur}>
            <Sequence durationInFrames={Math.round(3.6 * FPS)}><AppClip s={{dur: 3.6, from: ['selector', 0.3], to: ['crisis', 0.2], label: 'Pick the crisis.', aside: {text: 'both are live', at: 1.0, x: 1130, y: 600, arrow: 'left'}}} marks={data.uimarks ?? data.marks} file={data.uimarks ? 'ui.mp4' : 'run.mp4'} y={data.uimarks ? 0.27 : 0} /></Sequence>
            <Sequence from={Math.round(3.6 * FPS)}><AppClip s={{dur: s.dur - 3.6, hold: 'gate1', from: ['start', 0.3], to: ['approve1', 0.4], label: 'Triage', aside: {text: 'you decide', at: 1.8, x: 1130, y: 760, arrow: 'down-left'}}} marks={data.marks} /></Sequence>
          </Fade>)}
          {s.kind === 'clip' && <Fade dur={s.dur}><AppClip s={s} marks={data.marks} y={s.id === 'stages' || s.id === 'copy' ? 0.0 : 0.0} /></Fade>}
          {s.kind === 'tech' && <Fade dur={s.dur}><Tech tests={86} captions={caps} times={[0.2, 1.0, 2.4, 3.6, 5.0]} evalAt={6.4} opts={{redteam: data.tech?.redteam === true, redteamNames: data.tech?.redteamNames === true}} /></Fade>}
          {s.kind === 'dawn' && <Fade dur={s.dur}><End /></Fade>}
          {s.kind === 'memorial' && <Fade dur={s.dur} slow><Memorial m={data.memorial} /></Fade>}
        </Sequence>
      ))}
      {sound}{voice}
    </AbsoluteFill>
  );
};

// ---- JuanClip: a clip Juan records, in the film's look. Cut to fit, speed at most +-5 percent, never stretched; soft rounded frame on paper; captions from an SRT. ----
export type ClipProps = {file: string; start: number; end: number; duration: number; captions: {from: number; to: number; text: string}[]};
export const JuanClip: React.FC<ClipProps> = ({file, start, end, duration, captions}) => {
  useFonts();
  const f = useCurrentFrame(), t = f / FPS;
  const src = Math.max(0.1, end - start), rate = Math.min(1.05, Math.max(0.95, src / duration));
  const play = Math.floor((src / rate) * FPS), full = Math.round(duration * FPS);
  const clip = Math.min(play, full);
  const o = interpolate(f, [0, 12, full - 12, full], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const vid = <OffthreadVideo src={staticFile(file)} startFrom={Math.round(start * FPS)} playbackRate={rate} style={{width: '100%', height: '100%', objectFit: 'contain', background: '#0d1015'}} />;
  const cs = t * rate + start; // source time, to match SRT times to the recording
  const cap = captions.find((c) => cs >= c.from && cs <= c.to);
  return (
    <AbsoluteFill style={{background: PAPER, opacity: o}}>
      <div style={{position: 'absolute', left: 240, top: 70, width: 1440, height: 810, borderRadius: 28, overflow: 'hidden', boxShadow: '0 40px 90px rgba(70,45,10,.28), 0 8px 24px rgba(70,45,10,.16), 0 0 0 1px rgba(13,16,21,.14)'}}>
        {play >= full ? vid : (<><Sequence durationInFrames={Math.max(1, play)}>{vid}</Sequence><Sequence from={Math.max(1, play)}><Freeze frame={Math.max(1, play) - 1}>{vid}</Freeze></Sequence></>)}
      </div>
      {cap && <div style={{position: 'absolute', left: 0, right: 0, bottom: 70, textAlign: 'center'}}>
        <span style={{fontFamily: sans, fontSize: 36, color: INK, background: 'rgba(247,243,234,.95)', padding: '10px 24px', borderRadius: 12, boxShadow: '0 2px 14px rgba(70,45,10,.14)', textWrap: 'balance' as any}}>{cap.text}</span>
      </div>}
    </AbsoluteFill>
  );
};
