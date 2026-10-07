#!/usr/bin/env bash
# Screenshots of every page at 390 and 1280 px, Night and Day, into documents/design/review/<label>/. Offline: no model call.
# usage: shoot_review.sh before|after    (PORT 8099 app, PORT2 8098 app with NURY_FEEDBACK=on for the gate with chips)
LABEL=${1:-after}; PORT=${PORT:-8099}; PORT2=${PORT2:-8098}; HERE="$(cd "$(dirname "$0")" && pwd)"; OUT="$HERE/../../documents/design/review/$LABEL"; mkdir -p "$OUT"
ev(){ agent-browser eval "$1" 2>&1 | tail -1; }
open(){ agent-browser open "$1" >/dev/null 2>&1; agent-browser wait 1600 >/dev/null 2>&1; }
shot(){ agent-browser screenshot --full "$OUT/$1-$TH-$W.png" >/dev/null 2>&1; }
CASE=$(curl -s localhost:$PORT/api/cases | python3 -c "import sys,json;print(json.load(sys.stdin)['cases'][0]['id'])")
for TH in dark light; do for W in 390 1280; do H=800; [ $W = 390 ] && H=844
  agent-browser set viewport $W $H >/dev/null 2>&1
  open "http://127.0.0.1:$PORT/#/"; ev "try{localStorage.setItem('nury-theme','$TH')}catch(e){};1" >/dev/null; open "http://127.0.0.1:$PORT/#/"
  shot home
  ev "document.getElementById('hero-btn').click();1" >/dev/null; agent-browser wait 600 >/dev/null 2>&1; shot chooser
  ev "document.getElementById('chooser').close();1" >/dev/null
  open "http://127.0.0.1:$PORT/#/cases"; shot cases
  open "http://127.0.0.1:$PORT/#/case/$CASE"; shot case
  open "http://127.0.0.1:$PORT/#/crisis/detention"; shot crisis
  ev "(()=>{const b=[...document.querySelectorAll('[data-begin]')].find(x=>x.getBoundingClientRect().height>0);b.click();return 1})()" >/dev/null; agent-browser wait 700 >/dev/null 2>&1; shot intake
  open "http://127.0.0.1:$PORT/network"; shot network
  open "http://127.0.0.1:$PORT/how-it-was-built"; shot how
  open "http://127.0.0.1:$PORT/observability"; shot observability
  open "http://127.0.0.1:$PORT/improvement"; shot self-improvement
  open "http://127.0.0.1:$PORT2/#/"; ev "$(cat $HERE/gatestub.js)" >/dev/null; ev "window.__phase='ready';sid='x';show('v-pipe');poll();1" >/dev/null; agent-browser wait 1300 >/dev/null 2>&1; shot gate
done; done
ev "try{localStorage.setItem('nury-theme','dark')}catch(e){};1" >/dev/null
ls "$OUT" | wc -l
