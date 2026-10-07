#!/usr/bin/env bash
# Prepare Remotion inputs from the capture: public/run.mp4, public/marks.json
# Usage: ./prep.sh [capture_dir]   (default ../capture/raw)
set -euo pipefail
cd "$(dirname "$0")"; CAP="${1:-../capture/raw}"; mkdir -p public
if [ -f "$CAP/run.mp4" ]; then cp "$CAP/run.mp4" public/run.mp4; else ffmpeg -y -loglevel error -i "$CAP/run.webm" -r 30 -c:v libx264 -pix_fmt yuv420p -crf 14 -an public/run.mp4; fi   # run.mp4 = DevTools screencast (current recorder); run.webm = the old recorder
python3 - "$CAP/marks.txt" <<'PY'
import json,re,sys
m={}
for l in open(sys.argv[1]):
    t,rest=l.strip().split(None,1); k=rest.split()[0].rstrip(':')
    if k in("strip",): continue
    m.setdefault(k,float(t))
json.dump(m,open("public/marks.json","w"),indent=1); print(m)
PY
# Eric lines live in public/arc/ (committed); sound in public/arc/snd/ (sound/build_arc_sound.py)
[ -f public/proof.json ] || echo '{}' > public/proof.json   # real scorecard numbers only: {"pass":..,"n":..,"caught":..,"src":".."}

# non-live screens from the current app (capture/record_ui.py)
UI="${2:-../capture/raw_ui}"
if [ -f "$UI/ui.mp4" ]; then cp "$UI/ui.mp4" public/ui.mp4; cp "$UI/ui_marks.json" public/ui_marks.json; fi
