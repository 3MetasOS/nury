#!/usr/bin/env bash
# Real-click browser test of the Package screen's "Save to case file" and the gate's edit-save. Needs agent-browser and the app
# running on PORT (default 8099): cd code && PORT=8099 python3 -m app.server. No Gloo call: the session is stubbed (pkgstub.js).
# A programmatic .click() or getElementById().click() is NOT a test: it hid the duplicate-id bug. This uses real mouse clicks.
PORT=${PORT:-8099}; HERE="$(cd "$(dirname "$0")" && pwd)"; FAIL=0
ev(){ agent-browser eval "$1" 2>&1 | tail -1; }
check(){ if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1 (got $2, want $3)"; FAIL=1; fi; }
for VP in "1280 800" "390 844"; do set -- $VP; W=$1
  agent-browser set viewport $1 $2 >/dev/null 2>&1; agent-browser open http://127.0.0.1:$PORT >/dev/null 2>&1; agent-browser wait ".pk" >/dev/null 2>&1
  ev "$(cat $HERE/pkgstub.js)" >/dev/null
  ev "sid='x';show('v-pkg');poll();1" >/dev/null; agent-browser wait 900 >/dev/null 2>&1
  check "$W: Save button has a layout box" "$(ev "document.getElementById('b-save').getBoundingClientRect().height>40")" "true"
  agent-browser click "#b-save" >/dev/null 2>&1; agent-browser wait 700 >/dev/null 2>&1
  check "$W: real click sends exactly one save request" "$(ev "window.__saveCalls.length")" "1"
  check "$W: confirmation is visible" "$(ev "!document.getElementById('saved').classList.contains('hidden')")" "true"
  check "$W: confirmation says nothing was sent" "$(ev "/Nothing was sent to anyone/.test(document.getElementById('saved').textContent)")" "true"
  check "$W: Open the case link present" "$(ev "!!document.querySelector('#saved a')")" "true"
  ev "window.__saveCalls=[];window.__saveReply={error:'Nothing was saved.'};sid='x';show('v-pkg');poll();1" >/dev/null; agent-browser wait 900 >/dev/null 2>&1
  agent-browser click "#b-save" >/dev/null 2>&1; agent-browser wait 700 >/dev/null 2>&1
  check "$W: a failed save shows the error" "$(ev "document.getElementById('save-err').textContent")" "\"Nothing was saved.\""
  check "$W: button usable again after an error" "$(ev "!document.getElementById('b-save').disabled")" "true"
  ev "window.__saveReply=null;1" >/dev/null
  ev "window.__decisions=[];const f=window.api;window.api=async(p,b)=>{if(p.includes('/decision')){window.__decisions.push(b);return{ok:true}}return f(p,b)};clearInterval(timer);show('v-pipe');['gate','g-edit-btns','g-edit'].forEach(i=>document.getElementById(i).classList.remove('hidden'));document.getElementById('g-edit').value='Texto editado.';1" >/dev/null
  agent-browser click "#b-edit-save" >/dev/null 2>&1; agent-browser wait 500 >/dev/null 2>&1
  check "$W: gate edit-save sends the edit decision" "$(ev "window.__decisions.length&&window.__decisions[0].action")" "\"edit\""
done
[ $FAIL = 0 ] && echo "ALL PASS" || { echo "SOME FAILED"; exit 1; }
