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
export type Tech = {approved?: boolean; tests?: number | string; redteam?: boolean; redteamNames?: boolean; package?: string}; // approved = Juan approved presentation/MEMORIAL.md
export type Data = {uimarks?: Marks; marks: Marks; proof: Proof; confirmed?: Record<string, boolean>; memorial?: Memorial; tech?: Tech; credits?: Credits; voice?: Voice};

// LIGHT video palette (Juan, Oct 6): warm paper, ink text, deep amber on paper (branding/BRAND.md). App footage stays dark.
export const C = {bg: '#f7f3ea', ink: '#0d1015', amber: '#b8680f', text: '#0d1015', muted: '#5b5547'};
const D = {bg: '#080a0e', text: '#ece7dc', muted: '#a79f8d', amber: '#e8a33d'}; // dark phone interior (lock card)
export const serif = '"Fraunces", Georgia, serif';
export const sans = '"Inter", -apple-system, sans-serif';

// ---- Timeline (seconds). VO lines are the LOCKED text in presentation/SHARED_DEMO.md. ----
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

// Juan's words, verbatim from presentation/MEMORIAL.md (sections 1 and 4). Never edit, shorten or voice with TTS.
// memorial.json: {approved: false|true, option: 0..3, portrait: null | "file in public/"}. Nothing shows until Juan approves.
export const MEMORIALS: Record<number, string[]> = {
  0: ['Nury is named for my aunt, Nury.', 'For 83 years she served her church in the small things and the big ones, always with a smile, always with Jesus in her heart.', 'She never married.', 'She passed away a month ago.', 'This is for her.'],
  1: ['Nury is named for my aunt, Nury Peláez.', 'She served her church for 83 years, in the small things and the big ones,', 'always with a smile, always with Jesus in her heart.', 'She passed away a month ago. This is for her.'],
  2: ['In memory of Nury Peláez, 83.', 'She served her church in the small things and the big ones,', 'always with a smile, always with Jesus in her heart.', 'Nury is named for her.', 'May it be ready to help, the way she always was.'],
  3: ['In memory of Nury Peláez.', 'Always ready to help. Always with a smile.', 'Always with Jesus in her heart.'],
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
// Disclosure: canonical line from root CLAUDE.md, verbatim. Never reword.
export const DISCLOSURE = 'The Jev decision API from TypeSafe is used as typed judges in our evaluation harness and as a run-time draft classifier; disclosed as third-party technology per the rules.';
const NODES = [
  {t: "Pastor's phone", s: 'types the call', at: 0.2},
  {t: 'Privacy layer', s: 'tokens, not names', at: 1.2},
  {t: 'Gloo AI Studio', s: 'Claude Sonnet 4.6', at: 3.6},
  {t: 'Jev (from TypeSafe)', s: 'checks every draft', at: 5.6},
  {t: 'A person', s: 'Approve, Edit or Stop', at: 9.4},
];
export type TechOptsPlaceholder = never;

// Hand-lettered aside: Gochi Hand, a highlighter underline and a hand-drawn arrow (the same device as the app's own notes). One accent: deep amber.
export const Aside: React.FC<{text: string; x: number; y: number; arrow?: 'left' | 'down' | 'down-left'; opacity?: number; size?: number}> = ({text, x, y, arrow = 'left', opacity = 1, size = 52}) => (
  <div style={{position: 'absolute', left: x, top: y, opacity, fontFamily: '"Gochi Hand", cursive', fontSize: size, color: C.ink, lineHeight: 1.1, whiteSpace: 'nowrap'}}>
    <span style={{backgroundImage: 'linear-gradient(transparent 62%, rgba(232,163,61,.55) 62%, rgba(232,163,61,.55) 88%, transparent 88%)', padding: '0 6px'}}>{text}</span>
    <svg width="120" height="80" viewBox="0 0 120 80" fill="none" stroke={C.amber} strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" style={{position: 'absolute', ...(arrow === 'down' ? {left: 30, top: size * 1.15, transform: 'rotate(-80deg) scaleX(-1)'} : arrow === 'down-left' ? {left: -92, top: size * 0.6} : {left: -110, top: size * 0.15})}}>
      <path d="M112 14 C 78 6, 40 14, 14 52" /><path d="M14 52 L 12 30 M14 52 L 34 46" />
    </svg>
  </div>
);

export type TechOpts = {redteam?: boolean; redteamNames?: boolean};
export const Tech: React.FC<{tests: number | string; captions?: string[]; times?: number[]; evalAt?: number; opts?: TechOpts}> = ({tests, captions, times, evalAt: evalAtProp, opts}) => {
  const f = useCurrentFrame(); const sec = f / FPS;
  const caps = captions ?? ['Leak test: canary names and numbers, zero in any request', 'Judge test: unsafe 0.89 to 0.98, safe 0.02 to 0.24', `${tests} tests pass, offline`];
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
              <div style={{fontFamily: serif, fontSize: n.t.length > 16 ? 24 : 29, fontWeight: 600, color: C.text, whiteSpace: 'nowrap'}}>{n.t}</div>
              <div style={{fontSize: 22, color: C.muted, lineHeight: 1.25}}>{n.s}</div>
            </div>
          </React.Fragment>
        );
      })}
      {/* correction loop arrow under the Jev box: a rejected draft goes back to the writer */}
      <div style={{position: 'absolute', left: X0 + 2 * (W + GAP) + W / 2, top: Y + H + 14, width: W + GAP, height: 36, border: `3px solid ${C.amber}`, borderTop: 'none', borderRadius: '0 0 24px 24px', opacity: vis(6.4)}} />
      <div style={{position: 'absolute', left: X0 + 2 * (W + GAP), top: Y + H + 58, width: 2 * W + GAP, textAlign: 'center', fontSize: 22, color: C.muted, opacity: vis(6.4)}}>rejected? regenerate, up to 3 tries</div>
      <div style={{position: 'absolute', top: Y - 62, width: W + 100, left: X0 + 2 * (W + GAP) - 50, textAlign: 'center', whiteSpace: 'nowrap', fontSize: 26, color: C.amber, fontWeight: 500, opacity: vis(3.9)}}>Built on Gloo AI Studio</div>
      <Aside text="Checked by Jev" x={X0 + 3 * (W + GAP) - 10} y={Y - 92} arrow="down" opacity={vis(5.9)} />
      {/* who does what */}
      <div style={{position: 'absolute', left: 150, top: 560, width: 1620, minHeight: 170, borderRadius: 24, border: `3px dashed ${C.amber}`, opacity: vis(evalAt), display: 'grid', alignContent: 'center', justifyItems: 'center', gap: 12, padding: '18px 24px'}}>
        <div style={{display: 'flex', gap: 28, fontFamily: serif, fontSize: 30, color: C.text, flexWrap: 'nowrap', whiteSpace: 'nowrap', justifyContent: 'center'}}>
          <span>Writer: Claude Sonnet 4.6 via Gloo AI Studio</span><span style={{color: C.amber}}>·</span><span>Jev (TypeSafe): typed judges</span><span style={{color: C.amber}}>·</span><span>People review what is unsure</span>
        </div>
        {opts?.redteam && <div style={{fontSize: 26, color: C.muted, textAlign: 'center'}}>
          A red team from other model makers audits it before release. It advises; a person decides.{opts?.redteamNames ? ' Red team: OpenAI GPT-5.4, Google Gemini 3.1 Pro, Meta Llama 4 Maverick.' : ''}
        </div>}
      </div>
      {/* proof captions, one at a time */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 820, textAlign: 'center'}}>
        <span key={ci} style={{fontSize: 34, color: C.text, background: 'rgba(247,243,234,.94)', boxShadow: '0 2px 14px rgba(70,45,10,.14)', padding: '10px 22px', borderRadius: 12,
          opacity: interpolate((sec - [0, 3.6, 7.2][ci]) , [0, 0.4, 3.0, 3.6], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) * (sec > 1 ? 1 : 0)}}>{caps[ci]}</span>
      </div>
      <div style={{position: 'absolute', left: 150, right: 150, bottom: 26, textAlign: 'center', fontSize: 22, lineHeight: 1.35, color: C.muted, textWrap: 'balance' as any}}>{DISCLOSURE}</div>
    </AbsoluteFill>
  );
};

export const End: React.FC<{credit?: boolean}> = ({credit}) => (
  <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', textAlign: 'center', gap: 34}}>
    {/* branding/logo-lockup-light.svg: lantern, Nury and the brand line "An AI Crisis Response Agent." */}
    <Img src={staticFile('logo-lockup-light.svg')} style={{width: 1000}} />
    <div style={{fontFamily: sans, fontSize: 30, color: C.muted, maxWidth: 1200, textWrap: 'balance' as any}}>
      Nury is an AI assistant, not a pastor, counselor or lawyer. Legal information only. Not legal advice.
    </div>
    {credit && <div style={{fontFamily: sans, fontSize: 24, color: C.muted, marginTop: 8}}>Narration voice by ElevenLabs.</div>}
  </AbsoluteFill>
);
