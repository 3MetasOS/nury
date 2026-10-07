import React from 'react';
import {Composition, staticFile} from 'remotion';
import {FPS, type Data} from './Nury';
import {Night, Lantern, Dawn, Clock} from './LookDev';
import {NuryA, buildA, JuanClip} from './NuryA';

const load = async (): Promise<Data> => {
  const j = (p: string) => fetch(staticFile(p)).then((r) => r.json());
  const confirmed = await j('confirmed.json').catch(() => ({}));
  const memorial = await j('memorial.json').catch(() => ({}));
  const tech = await j('tech.json').catch(() => ({}));
  const credits = await j('credits.json').catch(() => ({}));
  const voice = await j('voice.json').catch(() => ({}));
  return {marks: await j('marks.json'), proof: await j('proof.json'), confirmed, memorial, tech, credits, voice};
};

export const Root: React.FC = () => (
  <>
  <Composition id="NuryA" component={NuryA} width={1920} height={1080} fps={FPS} durationInFrames={90 * FPS} defaultProps={{data: {marks: {}, proof: {}}} as {data: Data}}
    calculateMetadata={async () => { const data = await load(); const t = buildA(data); console.log('A-TIMELINE', JSON.stringify(t.scenes.map((x: any) => [x.id, +x.start.toFixed(1), +x.dur.toFixed(1)]))); return {durationInFrames: Math.round(t.total * FPS), props: {data}}; }} />
  <Composition id="JuanClip" component={JuanClip as any} width={1920} height={1080} fps={FPS} durationInFrames={5 * FPS}
    defaultProps={{file: 'incoming/dummy_clean.mp4', start: 0, end: 5, duration: 5, captions: []}}
    calculateMetadata={({props}: any) => ({durationInFrames: Math.max(1, Math.round(props.duration * FPS))})} />
  <Composition id="LookNight" component={Night} width={1920} height={1080} fps={FPS} durationInFrames={30} />
  <Composition id="LookLantern" component={Lantern} width={1920} height={1080} fps={FPS} durationInFrames={30} />
  <Composition id="LookDawn" component={Dawn} width={1920} height={1080} fps={FPS} durationInFrames={30} />
  <Composition id="LookClock" component={Clock} width={1920} height={1080} fps={FPS} durationInFrames={30} />
  </>
);
