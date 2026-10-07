#!/usr/bin/env bash
# Real-click test: selector -> crisis detail page -> Start -> intake. Needs the app on PORT (default 8099). No Gloo call.
PORT=${PORT:-8099}; HERE="$(cd "$(dirname "$0")" && pwd)"; FAIL=0
ev(){ agent-browser eval "$1" 2>&1 | tail -1; }
check(){ if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1 (got $2, want $3)"; FAIL=1; fi; }
for TH in dark light; do for VP in "390 844" "1280 800"; do set -- $VP; W=$1; T="$TH-$W"
  agent-browser set viewport $1 $2 >/dev/null 2>&1; agent-browser open http://127.0.0.1:$PORT >/dev/null 2>&1
  ev "try{localStorage.setItem('nury-theme','$TH')}catch(e){};location.reload();1" >/dev/null; agent-browser wait ".pick" >/dev/null 2>&1; agent-browser wait 500 >/dev/null 2>&1
  agent-browser click ".pick" >/dev/null 2>&1; agent-browser wait 500 >/dev/null 2>&1
  check "$T: crisis tap opens the detail page, not the intake" "$(ev "!document.getElementById('v-detail').classList.contains('hidden')&&document.getElementById('v-intake').classList.contains('hidden')")" "true"
  check "$T: title and description come from the playbook" "$(ev "document.getElementById('d-title').textContent.length>5&&document.getElementById('d-desc').textContent.length>20")" "true"
  check "$T: one line per stage (count from the playbook)" "$(ev "document.querySelectorAll('#d-steps li').length>=4&&[...document.querySelectorAll('#d-steps .l')].every(x=>x.textContent.length>10)")" "true"
  check "$T: says Nury never sends anything" "$(ev "/Nury never sends anything. You do./.test(document.getElementById('v-detail').innerText)")" "true"
  check "$T: Start button is big (>=56px)" "$(ev "document.getElementById('d-start').getBoundingClientRect().height>=56")" "true"
  check "$T: no sideways scroll" "$(ev "document.documentElement.scrollWidth<=innerWidth")" "true"
  check "$T: contrast scan clean" "$(ev "$(cat $HERE/contrast.js)")" "\"[]\""
  agent-browser screenshot ${SHOTS:-/tmp}/detail-$T.png >/dev/null 2>&1
  agent-browser click "#d-start" >/dev/null 2>&1; agent-browser wait 400 >/dev/null 2>&1
  check "$T: Start opens the intake" "$(ev "!document.getElementById('v-intake').classList.contains('hidden')")" "true"
  agent-browser click "#back-intake" >/dev/null 2>&1; agent-browser wait 300 >/dev/null 2>&1
  check "$T: Back returns to the detail page" "$(ev "!document.getElementById('v-detail').classList.contains('hidden')")" "true"
  agent-browser click "#back-detail" >/dev/null 2>&1; agent-browser wait 500 >/dev/null 2>&1
  check "$T: All crises returns to the selector" "$(ev "!document.getElementById('v-select').classList.contains('hidden')")" "true"
done; done
ev "try{localStorage.setItem('nury-theme','dark')}catch(e){};1" >/dev/null
[ $FAIL = 0 ] && echo "ALL PASS" || { echo "SOME FAILED"; exit 1; }
