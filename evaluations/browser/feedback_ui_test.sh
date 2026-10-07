#!/usr/bin/env bash
# Real-click test: the feedback chips, the consent sentence (both states), the Jev progress line and the Improvement page.
# PORT = app with NURY_FEEDBACK unset (default 8099). PORT2 = app with NURY_FEEDBACK=on (default 8098). No model call is made.
PORT=${PORT:-8099}; PORT2=${PORT2:-8098}; HERE="$(cd "$(dirname "$0")" && pwd)"; FAIL=0; SHOTS=${SHOTS:-/tmp/nury_shots}; mkdir -p "$SHOTS"
ev(){ agent-browser eval "$1" 2>&1 | tail -1; }
check(){ if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1 (got $2, want $3)"; FAIL=1; fi; }
click(){ agent-browser click "$1" >/dev/null 2>&1; agent-browser wait 500 >/dev/null 2>&1; }
scan(){ ev "$(cat $HERE/contrast.js)"; }
ov(){ ev "document.documentElement.scrollWidth<=innerWidth"; }
FOUR="Nury saves approved cases, with the names you typed, so you can come back to them. There is no sign-in yet: anyone who can open this app can open the saved cases. Nury sends nothing to the family. Share only what the family has agreed to share."
FIFTH="Nury also records what you change, without names, to improve its drafts; a person reviews every change before it is used."
open(){ agent-browser open "$1" >/dev/null 2>&1; agent-browser wait 1500 >/dev/null 2>&1; }
for TH in dark light; do for W in 390 1280; do H=800; [ $W = 390 ] && H=844; T="$TH-$W"
  agent-browser set viewport $W $H >/dev/null 2>&1
  open "http://127.0.0.1:$PORT/#/"; ev "try{localStorage.setItem('nury-theme','$TH')}catch(e){};1" >/dev/null
  for P in $PORT $PORT2; do
    if [ $P = $PORT ]; then MODE=off; else MODE=on; fi
    open "http://127.0.0.1:$P/#/crisis/detention"; agent-browser wait "[data-begin]" >/dev/null 2>&1
    ev "(()=>{const b=[...document.querySelectorAll('[data-begin]')].find(x=>x.getBoundingClientRect().height>0);b.click();return 1})()" >/dev/null; agent-browser wait 700 >/dev/null 2>&1
    read -r -d '' J <<JS
(()=>{const t=document.querySelector('#v-intake [data-consent]').textContent.trim();return t===$(printf '%s' "\"$FOUR\"")||t===$(printf '%s' "\"$FOUR $FIFTH\"")})()
JS
    check "$T consent($MODE): the intake note is exactly the approved text for this mode" "$(ev "$J")" "true"
    if [ $MODE = off ]; then check "$T consent(off): four sentences, no capture sentence, on the intake" "$(ev "document.querySelector('#v-intake [data-consent]').textContent.trim()===\"$FOUR\"")" "true"
    else check "$T consent(on): the fifth sentence is appended on the intake" "$(ev "document.querySelector('#v-intake [data-consent]').textContent.trim()===\"$FOUR $FIFTH\"")" "true"; fi
    open "http://127.0.0.1:$P/how-it-was-built"
    if [ $MODE = off ]; then check "$T consent(off): the how page note has four sentences" "$(ev "document.querySelector('[data-consent]').textContent.trim()===\"$FOUR\"")" "true"
    else check "$T consent(on): the how page note has the fifth sentence" "$(ev "document.querySelector('[data-consent]').textContent.trim()===\"$FOUR $FIFTH\"")" "true"; fi
    # gate: chips only when capture is on
    open "http://127.0.0.1:$P/#/"; ev "$(cat $HERE/gatestub.js)" >/dev/null; ev "window.__phase='ready';sid='x';show('v-pipe');poll();1" >/dev/null; agent-browser wait 1200 >/dev/null 2>&1
    if [ $MODE = off ]; then
      check "$T chips(off): no feedback row at the gate" "$(ev "document.getElementById('fb-row').classList.contains('hidden')")" "true"
    else
      read -r -d '' J <<'JS'
(()=>{const c=[...document.querySelectorAll('#fb-chips .chip')].map(b=>b.textContent);return JSON.stringify(c)==='["Good as is","Too long","Not my voice","Wrong tone","Inaccurate"]'&&!document.getElementById('b-approve').disabled&&!document.getElementById('fb-row').classList.contains('hidden')})()
JS
      check "$T chips(on): five chips with the approved labels, Approve still available" "$(ev "$J")" "true"
      check "$T chips(on): each chip is a 44 px target and the row is labelled optional" "$(ev "[...document.querySelectorAll('#fb-chips .chip')].every(b=>b.getBoundingClientRect().height>=44)&&/Optional/.test(document.getElementById('fb-l').textContent)")" "true"
      click "#fb-chips .chip:nth-child(2)"
      check "$T chips(on): a tap posts the slug and says so; Approve stays enabled" "$(ev "JSON.stringify(window.__fbCalls[0])==='{\"session\":\"x\",\"stage\":\"pastoral\",\"chip\":\"too_long\"}'&&/Thanks/.test(document.getElementById('fb-msg').textContent)&&document.querySelector('#fb-chips .chip:nth-child(2)').getAttribute('aria-pressed')==='true'&&!document.getElementById('b-approve').disabled")" "true"
      check "$T chips(on): contrast scan clean" "$(scan)" '"[]"'
      agent-browser screenshot $SHOTS/chips-$T.png >/dev/null 2>&1
    fi
    # the Jev phase shows as its own progress line, from a real event
    ev "window.__phase='checking_jev';poll();1" >/dev/null; agent-browser wait 1500 >/dev/null 2>&1
    check "$T progress($MODE): Jev phase reads 'Checking the draft with Jev'" "$(ev "/Checking the draft with Jev/.test(document.getElementById('strip-text').textContent)")" "true"
  done
  # the Improvement page
  open "http://127.0.0.1:$PORT/#/"; click "#imp-link"; agent-browser wait "#cands" >/dev/null 2>&1; agent-browser wait 1200 >/dev/null 2>&1
  check "$T improvement: the header link opens /improvement, marked current" "$(ev "location.pathname+'|'+document.querySelector('#imp-link').getAttribute('aria-current')")" '"/improvement|page"'
  check "$T improvement: the page says nothing changes without a person approving it" "$(ev "document.getElementById('honest').textContent")" '"Nothing changes without a person approving it."'
  check "$T improvement: synthetic data is labelled, capture state is shown" "$(ev "!document.getElementById('syn-note').hidden&&/synthetic/.test(document.getElementById('src').textContent)&&/Feedback capture: off/.test(document.getElementById('mode').textContent)")" "true"
  check "$T improvement: candidates show type, status, evidence and that they are not approved" "$(ev "(()=>{const c=[...document.querySelectorAll('.cand')];return c.length>=1&&c.every(k=>k.querySelector('.ty')&&k.querySelector('.st')&&k.querySelector('.ev li')&&/Not approved|Approved by/.test(k.textContent))})()")" "true"
  check "$T improvement: the report tables are counts only" "$(ev "document.querySelectorAll('#report table').length>=1&&!/Maria|Carlos|Jose|Lopez/.test(document.body.textContent)")" "true"
  check "$T improvement: no sideways scroll" "$(ov)" "true"
  check "$T improvement: contrast scan clean" "$(scan)" '"[]"'
  agent-browser screenshot $SHOTS/improvement-$T.png >/dev/null 2>&1
done; done
ev "try{localStorage.setItem('nury-theme','dark')}catch(e){};1" >/dev/null
[ $FAIL = 0 ] && echo "ALL PASS" || { echo "SOME FAILED"; exit 1; }
