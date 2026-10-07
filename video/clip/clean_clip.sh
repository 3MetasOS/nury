#!/usr/bin/env bash
# Clean the audio of a phone recording and keep the picture: high-pass, denoise, light compression, -16 LUFS. Prints before/after numbers.
# Usage: clip/clean_clip.sh in.mp4 out.mp4
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ffmpeg -y -loglevel error -i "$1" -c:v copy \
  -af "highpass=f=80,lowpass=f=12000,afftdn=nr=14:nf=-38:tn=1,agate=threshold=0.012:ratio=1.6:attack=20:release=250,acompressor=threshold=-21dB:ratio=2.5:attack=15:release=220:makeup=3,loudnorm=I=-16:TP=-1.5:LRA=8" \
  -c:a aac -b:a 160k -ar 48000 "$2"
python3 "$HERE/measure.py" "$1" before; python3 "$HERE/measure.py" "$2" after
