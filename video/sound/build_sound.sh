#!/usr/bin/env bash
# Synthesized sound bed demo (no samples, no licenses): room tone, clock ticks that slow, phone buzz, warm pad when the lantern lights.
# Usage: ./build_sound.sh [out.wav]   (15 s, 48 kHz mono)
set -euo pipefail
OUT="${1:-sound/sound_demo.wav}"; T=$(mktemp -d)
# room tone: brown noise, low-passed
ffmpeg -y -loglevel error -f lavfi -i "anoisesrc=d=15:c=brown:a=0.08:r=48000" -af "lowpass=f=380,volume=0.9" "$T/room.wav"
# one clock tick: 25 ms of high-passed noise with a fast decay
ffmpeg -y -loglevel error -f lavfi -i "anoisesrc=d=0.03:c=white:a=0.9:r=48000" -af "highpass=f=1800,afade=t=out:st=0:d=0.03,volume=0.6" "$T/tick.wav"
# ticks at times that slow down (seconds)
TIMES="0.4 1.4 2.5 3.8 5.3"; ins=""; fl=""; n=0
for t in $TIMES; do ms=$(python3 -c "print(int($t*1000))"); ins="$ins -i $T/tick.wav"; fl="$fl[$n:a]adelay=$ms|$ms[t$n];"; n=$((n+1)); done
labs=$(for i in $(seq 0 $((n-1))); do printf "[t$i]"; done)
ffmpeg -y -loglevel error $ins -filter_complex "${fl}${labs}amix=inputs=$n:normalize=0,apad=whole_dur=15" -t 15 -ar 48000 -ac 1 "$T/ticks.wav"
# phone buzz: two pulses of a 140 Hz tone with a 25 Hz flutter
ffmpeg -y -loglevel error -f lavfi -i "sine=f=140:d=15:r=48000" -af "tremolo=f=25:d=0.9,volume='if(between(t,3.0,3.4)+between(t,3.6,4.0),0.35,0)':eval=frame" "$T/buzz.wav"
# warm pad: A2 + E3 + A3 + C#4, slow swell from 6 s (the lantern lights), gentle tremolo
ffmpeg -y -loglevel error -f lavfi -i "sine=f=110:d=15:r=48000" -f lavfi -i "sine=f=164.8:d=15:r=48000" -f lavfi -i "sine=f=220:d=15:r=48000" -f lavfi -i "sine=f=277.2:d=15:r=48000" \
  -filter_complex "[0][1][2][3]amix=inputs=4:normalize=0,tremolo=f=0.25:d=0.25,lowpass=f=900,volume='clip((t-6)/3,0,1)*0.09':eval=frame" "$T/pad.wav"
ffmpeg -y -loglevel error -i "$T/room.wav" -i "$T/ticks.wav" -i "$T/buzz.wav" -i "$T/pad.wav" -filter_complex "amix=inputs=4:normalize=0,afade=t=in:d=0.5,afade=t=out:st=13.5:d=1.5,loudnorm=I=-20:TP=-2" -ar 48000 -ac 1 "$OUT"
echo "$OUT"; rm -rf "$T"
