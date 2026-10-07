import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill, Audio, Freeze, OffthreadVideo, Sequence, continueRender, delayRender,
  interpolate, staticFile, useCurrentFrame, useVideoConfig, Easing,
} from 'remotion';

export const FPS = 30;
export type Marks = Record<string, number>;
export type Proof = {pass?: number | string; n?: number | string; caught?: number | string; src?: string};
export type Data = {marks: Marks; proof: Proof; confirmed?: Record<string, boolean>};

const C = {bg: '#0d1015', surface: '#131824', amber: '#e8a33d', text: '#ece7dc', muted: '#a79f8d'};
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
  id: string; dur: number; trim?: number; kind: 'lock' | 'clip' | 'proof' | 'end';
  from?: [string, number]; to?: [string, number]; // src range as [mark, offset]
  label?: string; vo?: {k: string; at: number}[];
  needs?: string; trimN?: number; // needs: scene shows only if marks[needs] exists AND confirmed[needs] is true
};
const SCENES: Scene[] = [
  {id: 'lock', kind: 'lock', dur: 9, vo: [{k: '01', at: 1.5}]},
  {id: 'selector', kind: 'clip', dur: 4, from: ['selector', 0], to: ['selector', 3.7], label: 'The pastor picks the crisis.'},
  {id: 'intake', kind: 'clip', dur: 6, trim: 0, from: ['selector', 3.7], to: ['start', 0.3], label: 'Solo pastor. No staff. No lawyer.', vo: [{k: '02', at: 0.3}]},
  {id: 'protected', kind: 'clip', dur: 4, needs: 'protected', from: ['protected', 0], to: ['protected', 3.7], label: 'Nury keeps names on this computer'},
  {id: 'triage', kind: 'clip', dur: 11, trim: 2, trimN: 1, from: ['start', 0.3], to: ['approve1', 0.4], label: '1  Triage', vo: [{k: '03', at: 4.5}, {k: '04', at: 8.2}]},
  {id: 'rights', kind: 'clip', dur: 18, trim: 3, trimN: 1, from: ['approve1', 0.4], to: ['approve2', 0.4], label: '2  Rights brief. Vetted sources only.', vo: [{k: '05', at: 6}, {k: '06', at: 10.5}]},
  {id: 'montage', kind: 'clip', dur: 12, trimN: 1, from: ['approve2', 0.4], to: ['approve4', 0.4], label: '3  Attorneys   4  Checklist', vo: [{k: '07', at: 4}]},
  {id: 'pastoral', kind: 'clip', dur: 11, from: ['approve4', 0.4], to: ['approve5', 0.4], label: '5  Pastoral message', vo: [{k: '08', at: 3}]},
  {id: 'proof', kind: 'proof', dur: 8},
  {id: 'package', kind: 'clip', dur: 11, trim: 3, trimN: 1, from: ['approve5', 0.4], to: ['end', 0], label: 'Nury does not send. The pastor does.', vo: [{k: '09', at: 1}]},
  {id: 'end', kind: 'end', dur: 8, vo: [{k: '10', at: 1}]},
];
const hasProof = (p: Proof) => p.pass != null && p.n != null && p.caught != null;
export const buildTimeline = (d: Data) => {
  const proof = hasProof(d.proof);
  const ok = (n?: string) => !n || (d.marks[n] != null && d.confirmed?.[n] === true);
  const names = ok('protected') && d.marks['protected'] != null;
  let t = 0;
  const scenes = SCENES.filter((s) => (s.kind !== 'proof' || proof) && ok(s.needs)).map((s) => {
    const dur = s.dur - (proof ? s.trim ?? 0 : 0) - (names ? s.trimN ?? 0 : 0);
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
const Fade: React.FC<{dur: number; children: React.ReactNode}> = ({dur, children}) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 10, dur * FPS - 10, dur * FPS], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

const Backdrop: React.FC = () => (
  <AbsoluteFill style={{background: `radial-gradient(900px 700px at 30% 50%, rgba(232,163,61,.09), transparent 70%), ${C.bg}`}} />
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
        boxShadow: '0 30px 80px rgba(0,0,0,.55), 0 0 0 1px rgba(236,231,220,.10)', transform: `translateY(${slide}px)`}}>
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
      <div style={{width: 430, height: 880, borderRadius: 56, background: '#080a0e', boxShadow: `0 0 ${60 + 50 * glow}px rgba(232,163,61,${0.18 + 0.14 * glow})`,
        border: '1px solid rgba(236,231,220,.12)', display: 'grid', alignContent: 'center', justifyItems: 'center', gap: 18, color: C.text, fontFamily: sans}}>
        <div style={{fontFamily: serif, fontSize: 112, fontWeight: 600}}>2:07</div>
        <div style={{color: C.muted, fontSize: 26, letterSpacing: '.04em'}}>AM</div>
        <div style={{marginTop: 70, fontFamily: serif, fontSize: 44}}>Maria</div>
        <div style={{color: C.amber, fontSize: 26}}>calling</div>
      </div>
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
      <span style={{fontFamily: sans, fontSize: 34, color: C.text, background: 'rgba(13,16,21,.78)', padding: '10px 22px', borderRadius: 12, textWrap: 'balance' as any}}>{text}</span>
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
          <Fade dur={s.dur}>
            {s.kind === 'lock' && <Lock />}
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
