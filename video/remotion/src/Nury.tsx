import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill, Audio, Freeze, OffthreadVideo, Sequence, continueRender, delayRender,
  Img, interpolate, staticFile, useCurrentFrame, useVideoConfig, Easing,
} from 'remotion';

export const FPS = 30;
export type Marks = Record<string, number>;
export type Proof = {pass?: number | string; n?: number | string; caught?: number | string; src?: string};
export type Memorial = {intro?: boolean; approved?: boolean; option?: number; portrait?: string | null};
export type Voice = {noory?: boolean}; // voice.json: noory true = use the 'Noory' respelled takes (03, 06, 09, 10) once Juan says they sound right
export type Credits = {narration?: boolean}; // credits.json; narration false = no credit line (ElevenLabs Starter plan needs none)
export type Tech = {approved?: boolean; tests?: number | string}; // approved = Juan approved presentation/MEMORIAL.md
export type Data = {marks: Marks; proof: Proof; confirmed?: Record<string, boolean>; memorial?: Memorial; tech?: Tech; credits?: Credits; voice?: Voice};

// LIGHT video palette (Juan, Oct 6): warm paper, ink text, deep amber on paper (branding/BRAND.md). App footage stays dark.
export const C = {bg: '#f7f3ea', ink: '#0d1015', amber: '#b8680f', text: '#0d1015', muted: '#5b5547'};
const D = {bg: '#080a0e', text: '#ece7dc', muted: '#a79f8d', amber: '#e8a33d'}; // dark phone interior (lock card)
export const serif = '"Fraunces", Georgia, serif';
export const sans = '"Inter", -apple-system, sans-serif';

// ---- Timeline (seconds). VO lines are the LOCKED text in presentation/SHARED_DEMO.md. ----
const VO: Record<string, string> = {
  '01': 'It is two in the morning. A family is calling their pastor.',
  '02': 'Her husband was detained last evening. The pastor has no staff, and no lawyer on the line.',
  '03': 'Nury turns the call into a clear case. Facts only. No advice.',
  '04': 'After every stage, the pastor decides.',
  '05': "Rights in the family's own language. Built only from a vetted source. Every point cited.",
  '06': 'When a draft crosses the line from information into advice, Nury rejects it and tries again. The pastor never sees it.',
  '07': 'Attorney hotlines. A checklist for tonight.',
  '08': "And a short, warm message, in the pastor's hands to edit.",
  '09': 'Nury is not a pastor, and it never sends. The pastor does.',
  '10': 'Nury. The crisis-response agent for solo pastors.',
  // 'T' line removed: its audio said 'the pastor's computer'. This old cut (Nury90) is superseded by NuryA.
};
// Seconds of speech per line: ElevenLabs Eric (vo/eleven_durations.json). Update if the voice changes.
const VOLEN: Record<string, number> = {'01': 3.3, '02': 5.2, '03': 4.4, '04': 2.2, '05': 4.8, '06': 7.3, '07': 2.4, '08': 3.1, '09': 3.5, '10': 3.4}; // Eric, max of normal and Noory takes
type Scene = {
  id: string; dur: number; min?: number; kind: 'intro' | 'lock' | 'clip' | 'proof' | 'end' | 'memorial' | 'tech';
  from?: [string, number]; to?: [string, number]; // src range as [mark, offset]
  label?: string; vo?: {k: string; at: number}[];
  needs?: string; // scene shows only when its gate is open (see ok() below)
  fixed?: boolean; // fixed scenes keep their length; the others (min set) shrink to fit 90 s
};
const SCENES: Scene[] = [
  {id: 'intro', kind: 'intro', dur: 5, fixed: true, needs: 'intro'},
  {id: 'lock', kind: 'lock', dur: 9, min: 5.1, vo: [{k: '01', at: 1.5}]},
  {id: 'selector', kind: 'clip', dur: 4, min: 3, from: ['selector', 0], to: ['selector', 3.7], label: 'The pastor picks the crisis.'},
  {id: 'intake', kind: 'clip', dur: 6, min: 5.6, from: ['selector', 3.7], to: ['start', 0.3], label: 'Solo pastor. No staff. No lawyer.', vo: [{k: '02', at: 0.2}]},
  {id: 'protected', kind: 'clip', dur: 4, fixed: true, needs: 'protected', from: ['protected', 0], to: ['protected', 3.7], label: 'Tokens, not names'},
  {id: 'triage', kind: 'clip', dur: 11, min: 6.8, from: ['start', 0.3], to: ['approve1', 0.4], label: '1  Triage', vo: [{k: '03', at: 4.5}, {k: '04', at: 8.2}]},
  {id: 'rights', kind: 'clip', dur: 18, min: 13, from: ['approve1', 0.4], to: ['approve2', 0.4], label: '2  Rights brief. Vetted sources only.', vo: [{k: '05', at: 6}, {k: '06', at: 10.5}]},
  {id: 'tech', kind: 'tech', dur: 12, fixed: true, needs: 'tech'},
  {id: 'montage', kind: 'clip', dur: 12, min: 4.5, from: ['approve2', 0.4], to: ['approve4', 0.4], label: '3  Attorneys   4  Checklist', vo: [{k: '07', at: 4}]},
  {id: 'pastoral', kind: 'clip', dur: 11, min: 4.8, from: ['approve4', 0.4], to: ['approve5', 0.4], label: '5  Pastoral message', vo: [{k: '08', at: 3}]},
  {id: 'proof', kind: 'proof', dur: 8, fixed: true},
  {id: 'package', kind: 'clip', dur: 11, min: 4.8, from: ['approve5', 0.4], to: ['end', 0], label: 'Nury does not send. The pastor does.', vo: [{k: '09', at: 1}]},
  {id: 'end', kind: 'end', dur: 8, min: 4.2, vo: [{k: '10', at: 0.5}]},
  {id: 'memorial', kind: 'memorial', dur: 8, fixed: true, needs: 'memorial'},
];
const hasProof = (p: Proof) => p.pass != null && p.n != null && p.caught != null;
const MEM_SECONDS: Record<number, number> = {0: 12, 1: 12, 2: 16, 3: 8}; // by memorial option
export const buildTimeline = (d: Data) => {
  const proof = hasProof(d.proof);
  const mem = d.memorial?.approved === true, intro = d.memorial?.intro === true, tech = d.tech?.approved === true;
  const ok = (n?: string) => !n || (n === 'intro' ? intro : n === 'memorial' ? mem : n === 'tech' ? tech : d.marks[n] != null && d.confirmed?.[n] === true);
  const on = SCENES.filter((s) => (s.kind !== 'proof' || proof) && ok(s.needs)).map((s) => ({...s, dur: s.kind === 'memorial' ? MEM_SECONDS[d.memorial?.option ?? 3] ?? 8 : s.dur}));
  // Fit to 90 s: fixed scenes keep their length, flexible scenes shrink toward their minimum, never below it.
  const fixed = on.filter((s) => s.fixed).reduce((a, s) => a + s.dur, 0);
  const flex = on.filter((s) => !s.fixed);
  const pref = flex.reduce((a, s) => a + s.dur, 0), mins = flex.reduce((a, s) => a + (s.min ?? s.dur), 0);
  const budget = 90 - fixed, k = pref <= budget ? 1 : mins >= budget ? 0 : (budget - mins) / (pref - mins);
  let t = 0;
  const scenes = on.map((s) => {
    const dur = s.fixed ? s.dur : k === 1 ? s.dur : (s.min ?? s.dur) + (s.dur - (s.min ?? s.dur)) * k;
    // keep every VO line inside its scene and never overlapping the next one
    const vo = (s.vo ?? []).map((v) => ({...v}));
    for (let i = vo.length - 1; i >= 0; i--) {
      const len = VOLEN[vo[i].k] ?? 4;
      vo[i].at = Math.min(vo[i].at, i === vo.length - 1 ? dur - len - 0.3 : vo[i + 1].at - len - 0.2);
      vo[i].at = Math.max(0, vo[i].at);
    }
    const r = {...s, dur, vo, start: t}; t += dur; return r;
  });
  return {scenes, total: t, over: mins > budget};
};

// ---- fonts ----
export const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    const l = document.createElement('link'); l.rel = 'stylesheet';
    l.href = staticFile('fonts/fonts.css'); // self-hosted: renders offline
    document.head.appendChild(l);
    Promise.all([document.fonts.load('600 80px Fraunces'), document.fonts.load('400 30px Fraunces'), document.fonts.load('400 30px Inter')])
      .then(() => document.fonts.ready).finally(() => continueRender(h));
  }, [h]);
};

export const PH = 900;
export const ease = Easing.bezier(0.16, 1, 0.3, 1);
export const Fade: React.FC<{dur: number; slow?: boolean; children: React.ReactNode}> = ({dur, slow, children}) => {
  const f = useCurrentFrame();
  const a = slow ? 30 : 10, b = slow ? 45 : 10;
  const o = interpolate(f, [0, a, dur * FPS - b, dur * FPS], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

const Backdrop: React.FC = () => (
  <AbsoluteFill>
    <AbsoluteFill style={{background: 'linear-gradient(180deg, #f7f3ea, #efe9db)'}} />
    {/* fine static grain: breaks up banding in flat light gradients after H.264 */}
    <svg width="100%" height="100%" style={{position: 'absolute', inset: 0, opacity: 0.07, mixBlendMode: 'multiply'}}>
      <filter id="g"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" /><feColorMatrix values="0 0 0 0 0.3  0 0 0 0 0.25  0 0 0 0 0.15  0 0 0 0.9 0" /></filter>
      <rect width="100%" height="100%" filter="url(#g)" />
    </svg>
  </AbsoluteFill>
);

// phone-size footage on ink, caption right
export const Clip: React.FC<{s: any; marks: Marks}> = ({s, marks}) => {
  const a = marks[s.from[0]] + s.from[1], b = marks[s.to[0]] + s.to[1];
  const srcLen = b - a;
  const rate = Math.min(4, Math.max(0.85, srcLen / s.dur));
  const playFrames = Math.floor((srcLen / rate) * FPS);
  const f = useCurrentFrame();
  const slide = interpolate(f, [0, 24], [24, 0], {easing: ease, extrapolateRight: 'clamp'});
  const vid = (
    <OffthreadVideo src={staticFile('run.mp4')} startFrom={Math.round(a * FPS)} playbackRate={rate} muted
      style={{width: 780 * (PH / 1688), height: PH}} />
  );
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', left: 470, top: 40, width: 780 * (PH / 1688), height: PH, borderRadius: 28, overflow: 'hidden',
        boxShadow: '0 40px 90px rgba(70,45,10,.28), 0 8px 24px rgba(70,45,10,.16), 0 0 0 1px rgba(13,16,21,.14)', transform: `translateY(${slide}px)`}}>
        {playFrames >= s.dur * FPS ? vid : (
          <>
            <Sequence durationInFrames={Math.max(1, playFrames)}>{vid}</Sequence>
            <Sequence from={Math.max(1, playFrames)}>
              <Freeze frame={Math.max(1, playFrames) - 1}>{vid}</Freeze>
            </Sequence>
          </>
        )}
      </div>
      {s.label && (
        <div style={{position: 'absolute', left: 1000 + 110, top: 0, bottom: 0, width: 600, display: 'grid', alignContent: 'center'}}>
          <div style={{fontFamily: serif, fontSize: 64, lineHeight: 1.15, color: C.text, textWrap: 'balance' as any, whiteSpace: 'pre-line',
            opacity: interpolate(f, [8, 30], [0, 1], {extrapolateRight: 'clamp'})}}>{s.label}</div>
        </div>
      )}
    </AbsoluteFill>
  );
};

const Lock: React.FC = () => {
  const f = useCurrentFrame();
  const glow = 0.5 + 0.5 * Math.sin(f / 9);
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
      <div style={{width: 430, height: 880, borderRadius: 56, background: D.bg, boxShadow: '0 40px 90px rgba(70,45,10,.30), 0 8px 24px rgba(70,45,10,.18)',
        display: 'grid', alignContent: 'center', justifyItems: 'center', gap: 18, color: D.text, fontFamily: sans}}>
        <div style={{fontFamily: serif, fontSize: 112, fontWeight: 600}}>2:07</div>
        <div style={{color: D.muted, fontSize: 26, letterSpacing: '.04em'}}>AM</div>
        <div style={{marginTop: 70, fontFamily: serif, fontSize: 44}}>Maria</div>
        <div style={{color: D.amber, fontSize: 26, opacity: 0.6 + 0.4 * glow}}>calling</div>
      </div>
    </AbsoluteFill>
  );
};

// Opener (5 s, no VO): the lantern lights, "This is Nury." (about 1.2 s), then the dictionary entry (about 3.5 s). Text approved by Juan via hack-sensei.
const Intro: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / FPS;
  const fadeIn = (a: number, b: number) => interpolate(t, [a, b], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const lit = interpolate(t, [0.1, 1.0], [0.2, 1], {easing: ease, extrapolateRight: 'clamp'});
  const cap = interpolate(t, [0.2, 0.6, 1.2, 1.5], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const move = interpolate(t, [1.2, 1.7], [0, 1], {easing: ease, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', textAlign: 'center'}}>
      <Img src={staticFile('logo-mark-paper.svg')} style={{position: 'absolute', left: 960 - 75 - move * 360, top: 465 - move * 220, width: 150 - move * 70, height: 150 - move * 70, opacity: lit}} />
      <div style={{position: 'absolute', top: 640, fontFamily: serif, fontWeight: 600, fontSize: 120, color: C.text, opacity: cap}}>This is Nury.</div>
      <div style={{position: 'absolute', top: 330, left: 0, right: 0, display: 'grid', justifyItems: 'center', gap: 16}}>
        <div style={{display: 'flex', alignItems: 'baseline', gap: 28, opacity: fadeIn(1.5, 2.2)}}>
          <span style={{fontFamily: serif, fontWeight: 600, fontSize: 120, color: C.text}}>Nury</span>
          <span style={{fontFamily: sans, fontSize: 38, color: C.muted}}>/NOO-ree/ <i style={{fontFamily: serif}}>proper noun</i></span>
        </div>
        <div style={{fontFamily: serif, fontSize: 44, color: C.text, marginTop: 22, opacity: fadeIn(2.2, 2.7)}}>1. A given name from Arabic <i>nūr</i>, “light”.</div>
        <div style={{fontFamily: serif, fontSize: 44, color: C.text, opacity: fadeIn(3.6, 4.1)}}>2. The crisis-response agent for solo pastors.</div>
      </div>
    </AbsoluteFill>
  );
};

// Juan's words, verbatim from presentation/MEMORIAL.md (sections 1 and 4). Never edit, shorten or voice with TTS.
// memorial.json: {approved: false|true, option: 0..3, portrait: null | "file in public/"}. Nothing shows until Juan approves.
export const MEMORIALS: Record<number, string[]> = {
  0: ['Nury is named for my aunt, Nury.', 'For 83 years she served her church in the small things and the big ones, always with a smile, always with Jesus in her heart.', 'She never married.', 'She passed away a month ago.', 'This is for her.'],
  1: ['Nury is named for my aunt, Nury Pelaez.', 'She served her church for 83 years, in the small things and the big ones,', 'always with a smile, always with Jesus in her heart.', 'She passed away a month ago. This is for her.'],
  2: ['In memory of Nury Pelaez, 83.', 'She served her church in the small things and the big ones,', 'always with a smile, always with Jesus in her heart.', 'Nury is named for her.', 'May it be ready to help, the way she always was.'],
  3: ['In memory of Nury Pelaez.', 'Always ready to help. Always with a smile.', 'Always with Jesus in her heart.'],
};
export const Memorial: React.FC<{m?: Memorial}> = ({m}) => {
  const f = useCurrentFrame();
  const lines = MEMORIALS[m?.option ?? 3] ?? MEMORIALS[3];
  const step = Math.max(14, Math.round(130 / lines.length));
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', textAlign: 'center', gap: 22, padding: '0 300px'}}>
      {m?.portrait ? (
        <Img src={staticFile(m.portrait)} style={{width: 220, height: 220, borderRadius: 110, objectFit: 'cover', boxShadow: '0 12px 40px rgba(70,45,10,.25)', opacity: interpolate(f, [0, 40], [0, 1], {extrapolateRight: 'clamp'})}} />
      ) : null}
      <Img src={staticFile('logo-mark-paper.svg')} style={{width: 96, height: 96, opacity: interpolate(f, [0, 40], [0, 1], {extrapolateRight: 'clamp'}), marginBottom: 14}} />
      {lines.map((l, i) => (
        <div key={i} style={{fontFamily: serif, fontSize: i === lines.length - 1 ? 52 : 44, lineHeight: 1.3, color: C.text, textWrap: 'balance' as any,
          opacity: interpolate(f, [24 + i * step, 56 + i * step], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>{l}</div>
      ))}
    </AbsoluteFill>
  );
};

// Tech beat: animated architecture. Names in text only, no third-party logos. Claims are VERIFIED ones from documents/TECH_CLAIMS.md.
const DISCLOSURE = 'The evaluation harness uses the Jev decision API (my prior project), disclosed as prior technology per the rules.';
const NODES = [
  {t: "Pastor's phone", s: 'types the call', at: 0.2},
  {t: 'Privacy layer', s: 'tokens, not names', at: 1.2},
  {t: 'Gloo AI Studio', s: 'guarded endpoint', at: 3.6},
  {t: 'Checks', s: 'reject and regenerate, up to 3 tries', at: 5.6},
  {t: 'Approval gate', s: 'Approve, Edit or Stop', at: 9.4},
];
export const Tech: React.FC<{tests: number | string; captions?: string[]; times?: number[]; evalAt?: number}> = ({tests, captions, times, evalAt: evalAtProp}) => {
  const f = useCurrentFrame(); const sec = f / FPS;
  const caps = captions ?? ['Leak test: canary names and numbers, zero in any request', 'Typed judge, ten checks: unsafe 0.89 to 0.98, safe 0.02 to 0.24', `${tests} tests pass, offline`];
  const ci = sec < 3.6 ? 0 : sec < 7.2 ? 1 : 2; // each caption about 3.6 s
  const X0 = 145, W = 270, GAP = 70, Y = 250, H = 170;
  const vis = (a: number) => interpolate(sec, [a, a + 0.6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const evalAt = evalAtProp ?? 7.6;
  return (
    <AbsoluteFill style={{fontFamily: sans}}>
      <div style={{position: 'absolute', left: 150, top: 80, fontFamily: serif, fontSize: 52, color: C.text, opacity: vis(0)}}>How it is built</div>
      {NODES.map((n0, i) => {
        const n = times ? {...n0, at: times[i]} : n0;
        const x = X0 + i * (W + GAP), o = vis(n.at);
        return (
          <React.Fragment key={n.t}>
            {i > 0 && (() => {
              const x1 = x - GAP + 4, x2 = x - 6, lo = vis(n.at);
              const p = ((sec * 0.9 + i * 0.3) % 1);
              return (
                <div style={{position: 'absolute', left: x1, top: Y + H / 2 - 2, width: x2 - x1, height: 4, background: 'rgba(13,16,21,.28)', opacity: lo}}>
                  <div style={{position: 'absolute', left: `${p * 100}%`, top: -4, width: 12, height: 12, borderRadius: 6, background: C.amber}} />
                </div>
              );
            })()}
            <div style={{position: 'absolute', left: x, top: Y + (1 - o) * 14, width: W, height: H, borderRadius: 18, background: '#fffdf8', border: '2px solid rgba(13,16,21,.82)',
              boxShadow: '0 14px 34px rgba(70,45,10,.14)', opacity: o, display: 'grid', alignContent: 'center', justifyItems: 'center', gap: 8, padding: 14, textAlign: 'center'}}>
              <div style={{fontFamily: serif, fontSize: 30, fontWeight: 600, color: C.text, whiteSpace: 'nowrap'}}>{n.t}</div>
              <div style={{fontSize: 22, color: C.muted, lineHeight: 1.25}}>{n.s}</div>
            </div>
          </React.Fragment>
        );
      })}
      {/* correction loop arrow under the Checks box */}
      <div style={{position: 'absolute', left: X0 + 3 * (W + GAP) + 40, top: Y + H + 14, width: W - 80, height: 36, border: `3px solid ${C.amber}`, borderTop: 'none', borderRadius: '0 0 24px 24px', opacity: vis(6.4)}} />
      <div style={{position: 'absolute', left: X0 + 3 * (W + GAP), top: Y + H + 58, width: W, textAlign: 'center', fontSize: 22, color: C.muted, opacity: vis(6.4)}}>correction loop</div>
      <div style={{position: 'absolute', left: X0 + 2 * (W + GAP), top: Y - 62, width: W + 100, left: X0 + 2 * (W + GAP) - 50, textAlign: 'center', whiteSpace: 'nowrap', fontSize: 26, color: C.amber, fontWeight: 500, opacity: vis(3.9)}}>Built on Gloo AI Studio</div>
      {/* evaluation strip */}
      <div style={{position: 'absolute', left: 150, top: 560, width: 1620, height: 190, borderRadius: 24, border: `3px dashed ${C.amber}`, opacity: vis(evalAt), display: 'grid', alignContent: 'center', justifyItems: 'center', gap: 14}}>
        <div style={{fontSize: 24, color: C.muted, letterSpacing: '.06em'}}>EVALUATION TIME ONLY</div>
        <div style={{display: 'flex', gap: 56, fontFamily: serif, fontSize: 40, color: C.text}}>
          <span>Jev typed judges</span><span style={{color: C.amber}}>·</span><span>Red team</span><span style={{color: C.amber}}>·</span><span>Human review</span>
        </div>
      </div>
      <div style={{position: 'absolute', left: 150, top: 770, fontSize: 26, color: C.amber, fontWeight: 500, opacity: vis(8.4)}}>Tested with Jev</div>
      {/* proof captions, one at a time */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 850, textAlign: 'center'}}>
        <span key={ci} style={{fontSize: 34, color: C.text, background: 'rgba(247,243,234,.94)', boxShadow: '0 2px 14px rgba(70,45,10,.14)', padding: '10px 22px', borderRadius: 12,
          opacity: interpolate((sec - [0, 3.6, 7.2][ci]) , [0, 0.4, 3.0, 3.6], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) * (sec > 1 ? 1 : 0)}}>{caps[ci]}</span>
      </div>
      <div style={{position: 'absolute', left: 150, right: 150, bottom: 28, textAlign: 'center', fontSize: 20, color: C.muted}}>{DISCLOSURE}</div>
    </AbsoluteFill>
  );
};

const Proof: React.FC<{p: Proof}> = ({p}) => !hasProof(p) ? null : (
  <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: '0 200px'}}>
    <div style={{fontFamily: serif, fontSize: 76, lineHeight: 1.2, color: C.text, textWrap: 'balance' as any}}>
      <b style={{color: C.amber, fontWeight: 600}}>{p.pass}</b> of <b style={{color: C.amber, fontWeight: 600}}>{p.n}</b> scenarios passed.{' '}
      <b style={{color: C.amber, fontWeight: 600}}>{p.caught}</b> unsafe drafts caught and regenerated.
    </div>
    <div style={{fontFamily: sans, fontSize: 30, color: C.muted, marginTop: 36}}>{p.src ?? 'Scorecard in our build document.'}</div>
  </AbsoluteFill>
);

export const End: React.FC<{credit?: boolean}> = ({credit}) => (
  <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', textAlign: 'center', gap: 30}}>
    <Img src={staticFile('logo-mark-paper.svg')} style={{width: 132, height: 132}} />
    <div style={{fontFamily: serif, fontWeight: 600, fontSize: 188, color: C.amber, lineHeight: 1}}>Nury</div>
    <div style={{fontFamily: serif, fontSize: 54, color: C.text}}>The crisis-response agent for solo pastors.</div>
    <div style={{fontFamily: sans, fontSize: 30, color: C.muted, maxWidth: 1200, textWrap: 'balance' as any}}>
      Nury is an AI assistant, not a pastor, counselor or lawyer. Legal information only. Not legal advice.
    </div>
    {credit && <div style={{fontFamily: sans, fontSize: 24, color: C.muted, marginTop: 8}}>Narration voice by ElevenLabs.</div>}
  </AbsoluteFill>
);

export const Caption: React.FC<{text: string; dur: number}> = ({text, dur}) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 8, dur - 8, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 46, textAlign: 'center', opacity: o}}>
      <span style={{fontFamily: sans, fontSize: 34, color: C.text, background: 'rgba(247,243,234,.94)', boxShadow: '0 2px 14px rgba(70,45,10,.14)', padding: '10px 22px', borderRadius: 12, textWrap: 'balance' as any}}>{text}</span>
    </div>
  );
};

export const Nury: React.FC<{data: Data}> = ({data}) => {
  useFonts();
  const {scenes} = buildTimeline(data);
  const {width} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: C.bg}}>
      <Backdrop />
      {scenes.map((s: any) => (
        <Sequence key={s.id} from={Math.round(s.start * FPS)} durationInFrames={Math.round(s.dur * FPS)}>
          <Fade dur={s.dur} slow={s.kind === 'memorial'}>
            {s.kind === 'intro' && <Intro />}
            {s.kind === 'lock' && <Lock />}
            {s.kind === 'memorial' && <Memorial m={data.memorial} />}
            {s.kind === 'tech' && <Tech tests={data.tech?.tests ?? 'N'} />}
            {s.kind === 'clip' && <Clip s={s} marks={data.marks} />}
            {s.kind === 'proof' && <Proof p={data.proof} />}
            {s.kind === 'end' && <End credit={data.credits?.narration === true} />}
          </Fade>
          {(s.vo ?? []).map((v: any) => {
            const showCap = s.kind !== 'tech'; // the tech beat carries its own captions
            const len = VOLEN[v.k] + 0.5;
            const text = VO[v.k];
            return (
              <React.Fragment key={v.k}>
                {showCap && <Sequence from={Math.round(v.at * FPS)} durationInFrames={Math.round(Math.min(len, s.dur - v.at) * FPS)}>
                  <Caption text={text} dur={Math.round(Math.min(len, s.dur - v.at) * FPS)} />
                </Sequence>}
                <Sequence from={Math.round(v.at * FPS)}><Audio src={staticFile(`vo/${v.k}${data.voice?.noory && ['03', '06', '09', '10'].includes(v.k) ? '_noory' : ''}.wav`)} /></Sequence>
              </React.Fragment>
            );
          })}
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
