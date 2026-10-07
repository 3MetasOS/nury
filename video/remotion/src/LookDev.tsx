// Look development stills for the "night to light" arc (creative reset). Not part of the 90 s cut.
import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {useFonts} from './Nury';

const serif = '"Fraunces", Georgia, serif', sans = '"Inter", -apple-system, sans-serif';
const Grain: React.FC<{o?: number; blend?: any}> = ({o = 0.08, blend = 'overlay'}) => (
  <svg width="100%" height="100%" style={{position: 'absolute', inset: 0, opacity: o, mixBlendMode: blend}}>
    <filter id="gr"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch" /><feColorMatrix type="saturate" values="0" /></filter>
    <rect width="100%" height="100%" filter="url(#gr)" />
  </svg>
);
const Vignette: React.FC<{s?: number}> = ({s = 0.7}) => (
  <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 50%, transparent 40%, rgba(0,0,0,${s}) 100%)`}} />
);

// 1. Night: a dark room, the phone is the only light.
export const Night: React.FC = () => {
  useFonts();
  return (
    <AbsoluteFill style={{background: '#07090c'}}>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, #07090c 0%, #0b0f14 58%, #121821 100%)'}} />
      {/* table edge */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 640, height: 440, background: 'linear-gradient(180deg, #151b25, #0a0d12)', borderTop: '1px solid rgba(180,200,230,.10)'}} />
      {/* light spill from the phone onto the table */}
      <div style={{position: 'absolute', left: 560, top: 600, width: 820, height: 330, borderRadius: '50%', background: 'radial-gradient(ellipse, rgba(150,185,235,.30), transparent 70%)', filter: 'blur(12px)'}} />
      {/* phone lying on the table, tilted, screen lit */}
      <div style={{position: 'absolute', left: 790, top: 520, width: 340, height: 240, borderRadius: 26, background: '#05070a', transform: 'perspective(900px) rotateX(58deg) rotateZ(-8deg)', boxShadow: '0 0 90px rgba(150,185,235,.55)', display: 'grid', placeItems: 'center'}}>
        <div style={{width: 316, height: 216, borderRadius: 18, background: 'linear-gradient(180deg, #dbe8fb, #a9c4ec)', display: 'grid', placeItems: 'center', color: '#0b1220', fontFamily: sans, textAlign: 'center'}}>
          <div><div style={{fontFamily: serif, fontSize: 64, fontWeight: 600, lineHeight: 1}}>2:07</div><div style={{fontSize: 20, marginTop: 8}}>Maria  ·  calling</div></div>
        </div>
      </div>
      <Vignette s={0.85} /><Grain o={0.1} />
      <div style={{position: 'absolute', left: 140, bottom: 110, fontFamily: serif, fontSize: 54, color: 'rgba(236,231,220,.92)'}}>2:07 AM.</div>
      <div style={{position: 'absolute', left: 140, bottom: 60, fontFamily: sans, fontSize: 26, color: 'rgba(167,159,141,.9)'}}>A pastor. No lawyer on the line.</div>
    </AbsoluteFill>
  );
};

// 2. The lantern lights: ink, amber, the light is the set.
export const Lantern: React.FC = () => {
  useFonts();
  return (
    <AbsoluteFill style={{background: '#0d1015'}}>
      <AbsoluteFill style={{background: 'radial-gradient(700px 600px at 50% 46%, rgba(232,163,61,.34), rgba(232,163,61,.08) 55%, transparent 75%)'}} />
      <Img src={staticFile('logo-mark.svg')} style={{position: 'absolute', left: 960 - 190, top: 300, width: 380, height: 380}} />
      <Vignette s={0.75} /><Grain o={0.1} />
      <div style={{position: 'absolute', top: 760, left: 0, right: 0, textAlign: 'center', fontFamily: serif, fontWeight: 600, fontSize: 96, color: '#ece7dc'}}>This is Nury.</div>
    </AbsoluteFill>
  );
};

// 3. Dawn on paper: the light has won.
export const Dawn: React.FC = () => {
  useFonts();
  return (
    <AbsoluteFill style={{background: '#f7f3ea'}}>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, #2a2f3a 0%, #6b6f78 14%, #c9a874 34%, #ecd7b2 48%, #f7f3ea 70%)'}} />
      <Img src={staticFile('logo-mark-paper.svg')} style={{position: 'absolute', left: 960 - 70, top: 520, width: 140, height: 140}} />
      <div style={{position: 'absolute', top: 700, left: 0, right: 0, textAlign: 'center', fontFamily: serif, fontSize: 64, color: '#0d1015'}}>Nury.</div>
      <div style={{position: 'absolute', top: 790, left: 0, right: 0, textAlign: 'center', fontFamily: serif, fontSize: 38, color: '#5b5547'}}>An AI Crisis Response Agent.</div>
      <Grain o={0.07} blend="multiply" />
    </AbsoluteFill>
  );
};

// 4. The clock (treatment C): 2:07 to 2:12, one stage per minute.
export const Clock: React.FC = () => {
  useFonts();
  const stages = ['Triage', 'Rights brief', 'Attorneys', 'Checklist', 'Message'];
  return (
    <AbsoluteFill style={{background: '#0d1015'}}>
      <AbsoluteFill style={{background: 'radial-gradient(800px 500px at 50% 40%, rgba(236,231,220,.05), transparent 70%)'}} />
      <div style={{position: 'absolute', top: 150, left: 0, right: 0, textAlign: 'center', fontFamily: serif, fontWeight: 600, fontSize: 300, color: '#ece7dc', lineHeight: 1}}>2:09</div>
      <div style={{position: 'absolute', top: 470, left: 0, right: 0, textAlign: 'center', fontFamily: sans, fontSize: 30, color: '#a79f8d', letterSpacing: '.18em'}}>AM</div>
      <div style={{position: 'absolute', left: 190, right: 190, top: 640, display: 'flex', gap: 18}}>
        {stages.map((s, i) => (
          <div key={s} style={{flex: 1}}>
            <div style={{height: 8, borderRadius: 4, background: i < 2 ? '#e8a33d' : i === 2 ? 'rgba(232,163,61,.45)' : 'rgba(236,231,220,.14)'}} />
            <div style={{marginTop: 16, fontFamily: sans, fontSize: 26, color: i < 3 ? '#ece7dc' : '#6b6558', textAlign: 'center'}}>{s}</div>
          </div>
        ))}
      </div>
      <div style={{position: 'absolute', bottom: 90, left: 0, right: 0, textAlign: 'center', fontFamily: serif, fontSize: 48, color: '#ece7dc'}}>Five minutes. One pastor decides.</div>
      <Vignette s={0.6} /><Grain o={0.08} />
    </AbsoluteFill>
  );
};
