# Nury film: Remotion project (hack-video)

Composition `NuryA` is the 90-second film (treatment A, "From night to light"). `JuanClip` splices a clip Juan records. `Look*` are look-development stills.

## Render (proven)
1. `cd video/remotion && npm install` (once; node 20+).
2. Footage: `cd ../capture && python3 record.py http://127.0.0.1:<port>/` (live app, one session) then `cd ../remotion && ./prep.sh` (makes `public/run.mp4`, `public/marks.json`).
3. Sound assets (once): `python3 ../sound/build_arc_sound.py`.
4. Flags in `public/*.json` (nothing ships until these are true): `memorial.json` {approved, option 3|2|1, portrait}, `tech.json` {approved, tests, package, redteam, redteamNames}, `voice.json` {retakes, fresh:["L8","L11"]}, `credits.json`, `confirmed.json`, `proof.json`.
5. Render: `npx remotion render src/index.ts NuryA out/film.mp4`  (about 1.5 to 4 minutes).
6. Final check, twice: once with the network on, once with it off (wifi off). Compare duration (90.0 s) and loudness (`ffmpeg -i out/film.mp4 -af ebur128 -f null -`).
Fonts are self-hosted in `public/fonts`; nothing is fetched at render time.

## Files
`src/NuryA.tsx` the film and JuanClip · `src/Nury.tsx` shared pieces (tech beat, end card, memorial) · `src/LookDev.tsx` stills · `public/arc/` Eric lines · `public/arc/snd/` synthesized sound.
