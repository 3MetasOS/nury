#!/usr/bin/env bash
# Prepare Remotion inputs from the capture: public/run.mp4, public/marks.json, public/vo/NN.wav
# Usage: ./prep.sh [capture_dir]   (default ../capture/raw)
set -euo pipefail
cd "$(dirname "$0")"; CAP="${1:-../capture/raw}"; mkdir -p public/vo
ffmpeg -y -loglevel error -i "$CAP/run.webm" -r 30 -c:v libx264 -pix_fmt yuv420p -crf 14 -an public/run.mp4
python3 - "$CAP/marks.txt" <<'PY'
import json,re,sys
m={}
for l in open(sys.argv[1]):
    t,rest=l.strip().split(None,1); k=rest.split()[0].rstrip(':')
    if k in("strip",): continue
    m.setdefault(k,float(t))
json.dump(m,open("public/marks.json","w"),indent=1); print(m)
PY
cp ../vo/final/*.wav public/vo/ 2>/dev/null || cp ../vo/out/*.wav public/vo/ 2>/dev/null || echo "no VO yet"   # vo/final = Eric (ElevenLabs); vo/out = scratch TTS
[ -f public/proof.json ] || echo '{}' > public/proof.json   # real scorecard numbers only: {"pass":..,"n":..,"caught":..,"src":".."}
