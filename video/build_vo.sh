#!/usr/bin/env bash
# Scratch TTS voiceover from vo/lines.txt (macOS say). Lines match presentation/SHARED_DEMO.md.
# Usage: ./build_vo.sh [voice] [rate_wpm]   Output: vo/out/NN.wav and vo/out/durations.txt
set -euo pipefail
cd "$(dirname "$0")"
VOICE="${1:-Samantha}"; RATE="${2:-150}"
mkdir -p vo/out; : > vo/out/durations.txt
while IFS='|' read -r n text; do
  say -v "$VOICE" -r "$RATE" -o "vo/out/$n.aiff" "$text"
  ffmpeg -y -loglevel error -i "vo/out/$n.aiff" -ar 48000 -ac 1 "vo/out/$n.wav" && rm "vo/out/$n.aiff"
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "vo/out/$n.wav")
  printf '%s %.2f\n' "$n" "$d" >> vo/out/durations.txt
done < vo/lines.txt
awk '{s+=$2} END {printf "total speech: %.1f s\n", s}' vo/out/durations.txt
