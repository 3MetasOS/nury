#!/usr/bin/env bash
# TRUE offline render check: turn Wi-Fi off, render the film, turn Wi-Fi back on (always, even on error or Ctrl-C), compare with the online render.
# Run it ONLY when nobody needs the network for ~5 minutes: AMP messages, the Claude session and every agent that uses the internet stop while it runs.
# macOS only. Usage: ./wifi_off_render.sh [online.mp4]   (online.mp4 = the render made with the network on)
set -uo pipefail
cd "$(dirname "$0")"
DEV="$(networksetup -listallhardwareports | awk '/Wi-Fi|AirPort/{getline; print $2; exit}')"
[ -z "$DEV" ] && { echo "no Wi-Fi device found"; exit 1; }
WAS="$(networksetup -getairportpower "$DEV" | awk '{print $NF}')"
restore() { [ "$WAS" = "On" ] && networksetup -setairportpower "$DEV" on && echo "Wi-Fi back on"; }
trap restore EXIT INT TERM
networksetup -setairportpower "$DEV" off; sleep 4
if curl -s -m 4 -o /dev/null https://example.com; then echo "STILL ONLINE (another network is up: unplug Ethernet or turn off the hotspot). Aborting."; exit 2; fi
echo "network is down: rendering"
START=$(date +%s); npx remotion render src/index.ts NuryA out/film_offline.mp4; RC=$?; echo "render exit $RC in $(( $(date +%s) - START )) s"
restore; trap - EXIT
if [ -f "${1:-}" ]; then
  for f in "$1" out/film_offline.mp4; do ffprobe -v error -show_entries format=duration -of csv=p=0 "$f" | xargs printf "%s duration %.2f s\n" "$f"; ffmpeg -hide_banner -i "$f" -af ebur128 -f null - 2>&1 | grep "I:" | tail -1 | xargs printf "%s loudness %s\n" "$f"; done
fi
