import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill, Audio, Freeze, OffthreadVideo, Sequence, continueRender, delayRender,
  Img, interpolate, staticFile, useCurrentFrame, useVideoConfig, Easing,
} from 'remotion';

export const FPS = 30;
export type Marks = Record<string, number>;
export type Proof = {pass?: number | string; n?: number | string; caught?: number | string; src?: string};
export type Memorial = {intro?: boolean; approved?: boolean}; // approved = Juan approved presentation/MEMORIAL.md
export type Data = {marks: Marks; proof: Proof; confirmed?: Record<string, boolean>; memorial?: Memorial};

// LIGHT video palette (Juan, Oct 6): warm paper, ink text, deep amber on paper (branding/BRAND.md). App footage stays dark.
const C = {bg: '#f7f3ea', ink: '#0d1015', amber: '#b8680f', text: '#0d1015', muted: '#5b5547'};
const D = {bg: '#080a0e', text: '#ece7dc', muted: '#a79f8d', amber: '#e8a33d'}; // dark phone interior (lock card)
const serif = '"Fraunces", Georgia, serif';
const sans = '"Inter", -apple-system, sans-serif';

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
};
// Seconds of speech per line (macOS say, 150 wpm; see ../vo/out/durations.txt). Real voice: update these.
const VOLEN: Record<string, number> = {'01': 3.56, '02': 5.79, '03': 4.79, '04': 2.96, '05': 5.67, '06': 7.5, '07': 3.05, '08': 3.9, '09': 4.18, '10': 3.78};
type Scene = {
  id: string; dur: number; trim?: number; kind: 'intro' | 'lock' | 'clip' | 'proof' | 'end' | 'memorial';
  from?: [string, number]; to?: [string, number]; // src range as [mark, offset]
  label?: string; vo?: {k: string; at: number}[];
  needs?: string; trimN?: number; trimM?: number; trimI?: number; // needs: scene shows only if marks[needs] exists AND confirmed[needs] is true
};
const SCENES: Scene[] = [
  {id: 'intro', kind: 'intro', dur: 4, needs: 'intro'},
  {id: 'lock', kind: 'lock', dur: 9, trimI: 3.5, vo: [{k: '01', at: 1.5}]},
  {id: 'selector', kind: 'clip', dur: 4, from: ['selector', 0], to: ['selector', 3.7], label: 'The pastor picks the crisis.'},
  {id: 'intake', kind: 'clip', dur: 6, trim: 0, from: ['selector', 3.7], to: ['start', 0.3], label: 'Solo pastor. No staff. No lawyer.', vo: [{k: '02', at: 0.3}]},
  {id: 'protected', kind: 'clip', dur: 4, needs: 'protected', from: ['protected', 0], to: ['protected', 3.7], label: 'Nury keeps names on this computer'},
  {id: 'triage', kind: 'clip', dur: 11, trim: 2, trimN: 1, from: ['start', 0.3], to: ['approve1', 0.4], label: '1  Triage', vo: [{k: '03', at: 4.5}, {k: '04', at: 8.2}]},
  {id: 'rights', kind: 'clip', dur: 18, trim: 3, from: ['approve1', 0.4], to: ['approve2', 0.4], label: '2  Rights brief. Vetted sources only.', vo: [{k: '05', at: 6}, {k: '06', at: 10.5}]},
  {id: 'montage', kind: 'clip', dur: 12, trimN: 1, trimM: 1.5, from: ['approve2', 0.4], to: ['approve4', 0.4], label: '3  Attorneys   4  Checklist', vo: [{k: '07', at: 4}]},
  {id: 'pastoral', kind: 'clip', dur: 11, trimN: 1, trimM: 2, from: ['approve4', 0.4], to: ['approve5', 0.4], label: '5  Pastoral message', vo: [{k: '08', at: 3}]},
  {id: 'proof', kind: 'proof', dur: 8},
  {id: 'package', kind: 'clip', dur: 11, trim: 3, trimN: 1, trimM: 2, from: ['approve5', 0.4], to: ['end', 0], label: 'Nury does not send. The pastor does.', vo: [{k: '09', at: 1}]},
  {id: 'end', kind: 'end', dur: 8, trimM: 3, vo: [{k: '10', at: 0.5}]},
  {id: 'memorial', kind: 'memorial', dur: 8, needs: 'memorial'},
];
const hasProof = (p: Proof) => p.pass != null && p.n != null && p.caught != null;
export const buildTimeline = (d: Data) => {
  const proof = hasProof(d.proof);
  const intro = d.memorial?.intro === true, mem = d.memorial?.approved === true;
  const ok = (n?: string) => !n || (n === 'intro' ? intro : n === 'memorial' ? mem : d.marks[n] != null && d.confirmed?.[n] === true);
  const names = ok('protected') && d.marks['protected'] != null;
  let t = 0;
  const scenes = SCENES.filter((s) => (s.kind !== 'proof' || proof) && ok(s.needs)).map((s) => {
    const dur = s.dur - (proof ? s.trim ?? 0 : 0) - (names ? s.trimN ?? 0 : 0) - (mem ? s.trimM ?? 0 : 0) - (intro ? s.trimI ?? 0 : 0);
    const r = {...s, dur, start: t}; t += dur; return r;
  });
  return {scenes, total: t};
};

// ---- fonts ----
const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    const l = document.createElement('link'); l.rel = 'stylesheet';
    l.href = staticFile('fonts/fonts.css'); // self-hosted: renders offline
    document.head.appendChild(l);
    Promise.all([document.fonts.load('600 80px Fraunces'), document.fonts.load('400 30px Fraunces'), document.fonts.load('400 30px Inter')])
      .then(() => document.fonts.ready).finally(() => continueRender(h));
  }, [h]);
};

const PH = 900;
const ease = Easing.bezier(0.16, 1, 0.3, 1);
const Fade: React.FC<{dur: number; slow?: boolean; children: React.ReactNode}> = ({dur, slow, children}) => {
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
const Clip: React.FC<{s: any; marks: Marks}> = ({s, marks}) => {
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
          <div style={{fontFamily: serif, fontSize: 64, lineHeight: 1.15, color: C.text, textWrap: 'balance' as any,
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

const Intro: React.FC = () => {
  const f = useCurrentFrame();
  const lit = interpolate(f, [6, 34], [0.18, 1], {easing: ease, extrapolateRight: 'clamp'});
  const t1 = interpolate(f, [30, 52], [0, 1], {extrapolateRight: 'clamp'});
  const t2 = interpolate(f, [58, 84], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', textAlign: 'center', gap: 28}}>
      <Img src={staticFile('logo-mark-paper.svg')} style={{width: 150, height: 150, opacity: lit}} />
      <div style={{fontFamily: serif, fontWeight: 600, fontSize: 120, color: C.text, opacity: t1}}>This is Nury.</div>
      <div style={{fontFamily: serif, fontSize: 40, color: C.muted, opacity: t2}}>the crisis-response agent for solo pastors.</div>
    </AbsoluteFill>
  );
};

// Juan's words, verbatim from presentation/MEMORIAL.md. Never edit, shorten or voice with TTS. Gated by memorial.json approved.
const MEMORIAL = [
  'Nury is named for my aunt, Nury.',
  'For 83 years she served her church in the small things and the big ones, always with a smile, always with Jesus in her heart.',
  'She never married.',
  'She passed away a month ago.',
  'This is for her.',
];
const Memorial: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', textAlign: 'center', gap: 22, padding: '0 300px'}}>
      <Img src={staticFile('logo-mark-paper.svg')} style={{width: 96, height: 96, opacity: interpolate(f, [0, 40], [0, 1], {extrapolateRight: 'clamp'}), marginBottom: 14}} />
      {MEMORIAL.map((l, i) => (
        <div key={i} style={{fontFamily: serif, fontSize: i === 4 ? 56 : 44, lineHeight: 1.3, color: C.text, textWrap: 'balance' as any,
          opacity: interpolate(f, [24 + i * 22, 56 + i * 22], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>{l}</div>
      ))}
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

const End: React.FC = () => (
  <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', textAlign: 'center', gap: 30}}>
    <Img src={staticFile('logo-mark-paper.svg')} style={{width: 132, height: 132}} />
    <div style={{fontFamily: serif, fontWeight: 600, fontSize: 188, color: C.amber, lineHeight: 1}}>Nury</div>
    <div style={{fontFamily: serif, fontSize: 54, color: C.text}}>The crisis-response agent for solo pastors.</div>
    <div style={{fontFamily: sans, fontSize: 30, color: C.muted, maxWidth: 1200, textWrap: 'balance' as any}}>
      Nury is an AI assistant, not a pastor, counselor or lawyer. Legal information only. Not legal advice.
    </div>
  </AbsoluteFill>
);

const Caption: React.FC<{text: string; dur: number}> = ({text, dur}) => {
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
            {s.kind === 'memorial' && <Memorial />}
            {s.kind === 'clip' && <Clip s={s} marks={data.marks} />}
            {s.kind === 'proof' && <Proof p={data.proof} />}
            {s.kind === 'end' && <End />}
          </Fade>
          {(s.vo ?? []).map((v: any) => {
            const len = VOLEN[v.k] + 0.5;
            const text = VO[v.k];
            return (
              <React.Fragment key={v.k}>
                <Sequence from={Math.round(v.at * FPS)} durationInFrames={Math.round(Math.min(len, s.dur - v.at) * FPS)}>
                  <Caption text={text} dur={Math.round(Math.min(len, s.dur - v.at) * FPS)} />
                </Sequence>
                <Sequence from={Math.round(v.at * FPS)}><Audio src={staticFile(`vo/${v.k}.wav`)} /></Sequence>
              </React.Fragment>
            );
          })}
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
