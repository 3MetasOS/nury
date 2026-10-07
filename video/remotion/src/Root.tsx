import React from 'react';
import {Composition, staticFile} from 'remotion';
import {Nury, buildTimeline, FPS, type Data} from './Nury';

const load = async (): Promise<Data> => {
  const j = (p: string) => fetch(staticFile(p)).then((r) => r.json());
  const confirmed = await j('confirmed.json').catch(() => ({}));
  const memorial = await j('memorial.json').catch(() => ({}));
  const tech = await j('tech.json').catch(() => ({}));
  return {marks: await j('marks.json'), proof: await j('proof.json'), confirmed, memorial, tech};
};

export const Root: React.FC = () => (
  <Composition
    id="Nury90"
    component={Nury}
    width={1920}
    height={1080}
    fps={FPS}
    durationInFrames={90 * FPS}
    defaultProps={{data: {marks: {}, proof: {}}} as {data: Data}}
    calculateMetadata={async () => {
      const data = await load();
      const t = buildTimeline(data);
      console.log('TIMELINE', JSON.stringify(t.scenes.map((x: any) => [x.id, +x.start.toFixed(1), +x.dur.toFixed(1)])), 'over', t.over);
      return {durationInFrames: Math.round(t.total * FPS), props: {data}};
    }}
  />
);
