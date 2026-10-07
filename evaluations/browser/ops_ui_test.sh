#!/usr/bin/env bash
# Real-click test of the Observability page at 390 and 1280 px, Night and Day. Never confirms a smoke run (that would spend Gloo credit).
# Needs agent-browser, the app on PORT (default 8099, flag OFF) and a second app on PORT2 (default 8098) started with NURY_ALLOW_EVAL_RUN=1.
PORT=${PORT:-8099}; PORT2=${PORT2:-8098}; HERE="$(cd "$(dirname "$0")" && pwd)"; FAIL=0; SHOTS=${SHOTS:-/tmp/nury_shots}; mkdir -p "$SHOTS"
ev(){ agent-browser eval "$1" 2>&1 | tail -1; }
check(){ if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1 (got $2, want $3)"; FAIL=1; fi; }
click(){ agent-browser click "$1" >/dev/null 2>&1; agent-browser wait 500 >/dev/null 2>&1; }
scan(){ ev "$(cat $HERE/contrast.js)"; }
ov(){ ev "document.documentElement.scrollWidth<=innerWidth"; }
for TH in dark light; do for W in 390 1280; do H=800; [ $W = 390 ] && H=844; T="$TH-$W"
  agent-browser set viewport $W $H >/dev/null 2>&1; agent-browser open "http://127.0.0.1:$PORT/#/" >/dev/null 2>&1
  ev "try{localStorage.setItem('nury-theme','$TH')}catch(e){};1" >/dev/null
  agent-browser open "http://127.0.0.1:$PORT/#/" >/dev/null 2>&1; agent-browser wait "#h-home" >/dev/null 2>&1; agent-browser wait 800 >/dev/null 2>&1
  SIG="$(cat $HERE/shellsig.js)"; HOMESIG=$(ev "$SIG")
  click ".fnav a[data-nav=ops]"; agent-browser wait "#cards .card" >/dev/null 2>&1; agent-browser wait 1200 >/dev/null 2>&1
  check "$T ops: the footer link opens /observability" "$(ev "location.pathname")" '"/observability"'
  check "$T ops: same shared header and footer, Observability marked current" "$(ev "$SIG")|$(ev "document.querySelector('.fnav a[data-nav=ops]').getAttribute('aria-current')")" "$HOMESIG|\"page\""
  check "$T ops: the honesty line is on the page" "$(ev "document.getElementById('honest').textContent")" '"No alerts, no retention policy, no per-church separation yet."'
  check "$T ops: the source line says where the numbers come from" "$(ev "/^Source: /.test(document.getElementById('src').textContent)")" "true"
  check "$T ops: seven headline cards, each with a one-line explanation" "$(ev "[...document.querySelectorAll('#cards .card')].length===7&&[...document.querySelectorAll('#cards .card')].every(c=>c.querySelector('p').textContent.length>20&&c.title.length>20)")" "true"
  check "$T ops: five charts, each an image with a text label" "$(ev "[...document.querySelectorAll('#charts svg')].length===5&&[...document.querySelectorAll('#charts svg')].every(s=>s.getAttribute('role')==='img'&&s.getAttribute('aria-label').length>10)")" "true"
  check "$T ops: the runs table has at most 50 rows and cells are short labels" "$(ev "(()=>{const r=[...document.querySelectorAll('#runs tbody tr')];return r.length>=1&&r.length<=50&&[...document.querySelectorAll('#runs td')].every(t=>t.textContent.length<=32)})()")" "true"
  check "$T ops: no sideways scroll" "$(ov)" "true"
  check "$T ops: contrast scan clean" "$(scan)" '"[]"'
  check "$T ops: nothing from a draft or a name is on the page" "$(ev "!/Maria|Carlos|Jose|Lopez|Hernandez|Garcia/.test(document.body.textContent)")" "true"
  # exports: real clicks, the blob is captured and read
  ev "window.__cap=[];const o=URL.createObjectURL;URL.createObjectURL=b=>{b.text().then(t=>window.__cap.push(t));return o(b)};1" >/dev/null
  click "#x-json"; agent-browser wait 500 >/dev/null 2>&1
  check "$T ops: Export JSON gives valid JSON with the agreed keys and no names" "$(ev "(()=>{try{const j=JSON.parse(window.__cap[0]);return !!j.headline&&Array.isArray(j.runs)&&!/Maria|Carlos|Jose|Lopez/.test(window.__cap[0])}catch(e){return false}})()")" "true"
  click "#x-csv"; agent-browser wait 500 >/dev/null 2>&1
  check "$T ops: Export CSV has the header row and no names" "$(ev "(()=>{const t=window.__cap[1]||'';return t.split('\n')[0]==='time,crisis,stages,attempts,cost_usd,latency_s,outcome'&&!/Maria|Carlos|Jose|Lopez/.test(t)})()")" "true"
  check "$T ops: an export confirms in words" "$(ev "/Saved nury-runs\.csv/.test(document.getElementById('x-msg').textContent)")" "true"
  # evaluations
  check "$T ops: the evaluation sets show their numbers" "$(ev "document.querySelectorAll('#evcards .card').length>=2&&/Version [0-9a-f]{7}/.test(document.getElementById('evcards').textContent)")" "true"
  check "$T ops: on this server the smoke run is off and the button is disabled with a reason" "$(ev "document.getElementById('smoke-btn').disabled&&/switched off/.test(document.getElementById('smoke-note').textContent)")" "true"
  agent-browser screenshot $SHOTS/ops-$T.png >/dev/null 2>&1
  # the same page on a server where the run is allowed: confirm dialog only, never confirmed
  agent-browser open "http://127.0.0.1:$PORT2/observability" >/dev/null 2>&1; agent-browser wait "#cards .card" >/dev/null 2>&1; agent-browser wait 1200 >/dev/null 2>&1
  read -r -d '' J <<'JS'
!document.getElementById('smoke-btn').disabled&&/About \$[0-9.]+ of Gloo credit/.test(document.getElementById('smoke-note').textContent)
JS
  check "$T ops(flag on): the button is enabled and the cost estimate is stated" "$(ev "$J")" "true"
  click "#smoke-btn"
  read -r -d '' J <<'JS'
document.getElementById('confirm').open&&/It will spend about \$[0-9.]+/.test(document.getElementById('confirm-p').textContent)&&document.getElementById('smoke-bar').hidden
JS
  check "$T ops(flag on): a click asks for confirmation first, with the amount" "$(ev "$J")" "true"
  click "#confirm-no"
  check "$T ops(flag on): Cancel closes it, nothing started, focus returns to the button" "$(ev "!document.getElementById('confirm').open&&document.getElementById('smoke-bar').hidden&&document.activeElement.id==='smoke-btn'")" "true"
  click "#smoke-btn"; agent-browser press Escape >/dev/null 2>&1; agent-browser wait 300 >/dev/null 2>&1
  check "$T ops(flag on): Escape closes it too, and nothing started" "$(ev "!document.getElementById('confirm').open&&document.getElementById('smoke-bar').hidden&&document.getElementById('smoke-out').textContent===''")" "true"
  agent-browser eval "document.getElementById('smoke-btn').click();1" >/dev/null 2>&1; agent-browser wait 400 >/dev/null 2>&1
  check "$T ops(flag on): the confirm dialog contrast is clean" "$(scan)" '"[]"'
  agent-browser press Escape >/dev/null 2>&1
done; done
ev "try{localStorage.setItem('nury-theme','dark')}catch(e){};1" >/dev/null
[ $FAIL = 0 ] && echo "ALL PASS" || { echo "SOME FAILED"; exit 1; }
