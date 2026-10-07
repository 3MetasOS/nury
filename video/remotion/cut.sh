#!/usr/bin/env bash
# Build a cut from a capture folder: prep the footage, print the voice plan, render, then check duration and loudness.
# Usage: ./cut.sh ../capture/raw out/nuryA_cut4.mp4 [../capture/raw_ui]
# Flags (public/memorial.json, tech.json, voice.json) decide what ships. For a REVIEW cut set memorial approved true first and set it back after.
set -euo pipefail
cd "$(dirname "$0")"; CAP="${1:?capture folder}"; OUT="${2:-out/cut.mp4}"; UI="${3:-../capture/raw_ui}"
./prep.sh "$CAP" "$UI" | tail -1
npx remotion compositions src/index.ts 2>&1 | grep -E "A-VOICE" | sed 's/.*A-VOICE//'
(time npx remotion render src/index.ts NuryA "$OUT") 2>&1 | grep -E "MB|rror|real|total"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT" | xargs printf "duration %.2f s\n"
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:" | tail -2
