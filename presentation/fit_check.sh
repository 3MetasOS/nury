#!/bin/sh
# Real-size fit check for deck.html: renders it in exact-size iframes (same origin, local http) and reports overflow.
# Usage: sh presentation/fit_check.sh     (needs agent-browser and python3; uses port 18150 and stops it after)
D=$(cd "$(dirname "$0")" && pwd)
T=$(mktemp -d); cp "$D/deck.html" "$T/fitdeck.html"; cp -r "$D/images" "$D/fonts" "$T/"
JS=$(cat "$D/fit_check.js")
lsof -ti tcp:18150 | xargs kill 2>/dev/null
(cd "$T" && python3 -m http.server 18150 >/dev/null 2>&1 &)
sleep 1
export AGENT_BROWSER_SESSION=fit-check-deck
for q in "?gated" "" "?track=short" "?track=short&gated"; do for vp in "1280 720" "1920 1080" "390 844"; do
  W=${vp% *}; H=${vp#* }
  printf '<!doctype html><body style="margin:0"><iframe id="f" src="fitdeck.html%s" style="width:%spx;height:%spx;border:0"></iframe></body>' "$q" "$W" "$H" > "$T/fit.html"
  agent-browser open "http://127.0.0.1:18150/fit.html" >/dev/null 2>&1; sleep 3
  echo "[${q:-default}] $W x $H: $(agent-browser eval "$JS" 2>&1 | tail -1)"
done; done
agent-browser close >/dev/null 2>&1; lsof -ti tcp:18150 | xargs kill 2>/dev/null
