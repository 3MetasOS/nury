#!/usr/bin/env bash
# Clean a human voice recording so it drops into the cut: denoise, trim silence, light compression, -16 LUFS, 48 kHz mono WAV.
# Usage: ./clean_voice.sh in.(wav|m4a|mp3) out.wav
set -euo pipefail
ffmpeg -y -loglevel error -i "$1" \
  -af "highpass=f=80,afftdn=nr=12:nf=-35,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.15:stop_periods=1:stop_threshold=-45dB:stop_silence=0.4,acompressor=threshold=-20dB:ratio=2.5:attack=15:release=200:makeup=2,loudnorm=I=-16:TP=-1.5:LRA=8" \
  -ar 48000 -ac 1 "$2"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$2" | awk '{printf "%s: %.2f s\n", "'"$2"'", $1}'
