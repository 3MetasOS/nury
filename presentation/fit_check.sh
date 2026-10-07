#!/bin/sh
# Real-size fit check for deck.html: renders it in exact-size iframes (same origin, local http) and reports overflow.
# Usage: sh presentation/fit_check.sh     (needs agent-browser and python3; uses port 18150, stops it after)
set -e
T=$(mktemp -d); cp "$(dirname "$0")/deck.html" "$T/fitdeck.html"; cp -r "$(dirname "$0")/images" "$(dirname "$0")/fonts" "$T/"
cd "$T"; python3 -m http.server 18150 >/dev/null 2>&1 & P=$!; sleep 1
export AGENT_BROWSER_SESSION=fit-check-deck
for q in "?gated" ""; do for vp in "1280 720" "1920 1080" "390 844"; do
  W=${vp% *}; H=${vp#* }
  printf '<!doctype html><body style="margin:0"><iframe id="f" src="fitdeck.html%s" style="width:%spx;height:%spx;border:0"></iframe></body>' "$q" "$W" "$H" > fit.html
  agent-browser open "http://127.0.0.1:18150/fit.html" >/dev/null 2>&1; sleep 3
  echo "[${q:-default}] $W x $H: $(agent-browser eval '(()=>{const w=document.getElementById("f").contentWindow;return w.eval("(()=>{const S=vis();const r=[];for(let k=0;k<S.length;k++){go(k);const d=document.documentElement;const f=document.querySelector(\".foot\");const fx=getComputedStyle(f).position===\"fixed\";if(d.scrollWidth>innerWidth+2)r.push((k+1)+\"H\");if(fx&&d.scrollHeight>innerHeight+2)r.push((k+1)+\"V:\"+(d.scrollHeight-innerHeight))}return innerWidth+\"x\"+innerHeight+\" \"+S.length+\" slides, problems: \"+(r.join(\" \")||\"none\")})()")})()' 2>&1 | tail -1)"
done; done
agent-browser close >/dev/null 2>&1 || true; kill $P 2>/dev/null || true
