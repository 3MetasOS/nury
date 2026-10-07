#!/usr/bin/env bash
# Real-click test of the app shell: home, crisis detail, cases, case viewer, sheets, unsaved-work guard, keyboard, motion.
# Needs agent-browser and the app on PORT (default 8099). No Gloo call: the package screen uses a stubbed session (pkgstub.js).
# Real mouse and key events only. A programmatic .click() would not have caught the duplicate-id bug.
PORT=${PORT:-8099}; HERE="$(cd "$(dirname "$0")" && pwd)"; FAIL=0; SHOTS=${SHOTS:-/tmp/nury_shots}; mkdir -p "$SHOTS"
ev(){ agent-browser eval "$1" 2>&1 | tail -1; }
check(){ if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1 (got $2, want $3)"; FAIL=1; fi; }
# polls an expression for up to ~3 s: routing is async (it loads data first), so a fixed pause can race
waitexp(){ for i in 1 2 3 4 5 6; do r=$(ev "$1"); [ "$r" = "true" ] && { echo true; return; }; agent-browser wait 500 >/dev/null 2>&1; done; echo "$r"; }
click(){ agent-browser click "$1" >/dev/null 2>&1; agent-browser wait 500 >/dev/null 2>&1; }
view(){ ev "document.body.dataset.view"; }
scan(){ ev "$(cat $HERE/contrast.js)"; }
ov(){ ev "document.documentElement.scrollWidth<=innerWidth"; }
for TH in dark light; do for W in 390 1280; do H=800; [ $W = 390 ] && H=844; T="$TH-$W"
  agent-browser set viewport $W $H >/dev/null 2>&1; agent-browser open "http://127.0.0.1:$PORT/#/" >/dev/null 2>&1
  ev "try{localStorage.setItem('nury-theme','$TH')}catch(e){};location.reload();1" >/dev/null; agent-browser wait "#h-home" >/dev/null 2>&1; agent-browser wait 900 >/dev/null 2>&1
  # ---- home
  check "$T home: view" "$(view)" '"home"'
  check "$T home: two live crisis links, two coming-soon cards that are not links" "$(ev "document.querySelectorAll('#picks a.pk').length===2&&document.querySelectorAll('#picks .pk.soon').length===2&&[...document.querySelectorAll('#picks .pk.soon')].every(e=>e.tagName==='DIV'&&e.tabIndex<0)")" "true"
  check "$T home: hero says Respond to a crisis" "$(ev "document.getElementById('hero-btn').textContent.trim()")" '"Respond to a crisis"'
  check "$T home: section is 'A family needs help'" "$(ev "document.getElementById('h-start').textContent")" '"A family needs help"'
  check "$T home: no sideways scroll" "$(ov)" "true"
  check "$T home: contrast scan clean" "$(scan)" '"[]"'
  check "$T home: wording rule (no computer, local, device, encrypt, sign in, account, start a crisis)" "$(ev "!/computer|\blocal\b|device|encrypt|sign.?in|account|start a (new )?crisis|start this crisis/i.test(document.body.innerText)")" "true"
  agent-browser screenshot $SHOTS/home-$T.png >/dev/null 2>&1
  # ---- keyboard: skip link first, visible focus ring
  agent-browser press Tab >/dev/null 2>&1; agent-browser press Tab >/dev/null 2>&1
  check "$T keyboard: focus ring visible on a focused control" "$(ev "(()=>{const e=document.activeElement;const s=getComputedStyle(e);return e!==document.body&&s.outlineStyle!=='none'&&parseFloat(s.outlineWidth)>=2})()")" "true"
  # ---- crisis detail
  click "#picks a.pk"
  check "$T crisis: hash and view" "$(ev "location.hash+'|'+document.body.dataset.view")" '"#/crisis/detention|crisis"'
  check "$T crisis: five stages from the playbook, rail present" "$(ev "document.querySelectorAll('#crisis-page .st').length===5&&document.querySelectorAll('#crisis-page .rail .n').length===5")" "true"
  check "$T crisis: 911 line, never list, time note" "$(ev "/call 911 first/.test(document.body.innerText)&&/What Nury will never do/.test(document.body.innerText)&&/about a minute/i.test(document.body.innerText)")" "true"
  check "$T crisis: Begin button reachable without scrolling" "$(ev "(()=>{const b=[...document.querySelectorAll('[data-begin]')].find(x=>x.getBoundingClientRect().height>0&&getComputedStyle(x).display!=='none');if(!b)return false;const r=b.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight&&r.height>=56})()")" "true"
  check "$T crisis: no sideways scroll" "$(ov)" "true"
  check "$T crisis: contrast scan clean" "$(scan)" '"[]"'
  check "$T crisis: tab bar hidden on phone for a task page" "$(ev "getComputedStyle(document.querySelector('.tabs')).display!=='none'===(innerWidth>=960)")" "true"
  agent-browser screenshot $SHOTS/crisis-$T.png >/dev/null 2>&1
  # ---- begin the response -> intake -> back -> all crises
  ev "(()=>{const b=[...document.querySelectorAll('[data-begin]')].find(x=>x.getBoundingClientRect().height>0&&getComputedStyle(x).display!=='none');b.scrollIntoView({block:'center'});return 1})()" >/dev/null
  agent-browser eval "document.querySelectorAll('[data-begin]').forEach(b=>b.dataset.t='1');1" >/dev/null 2>&1
  if [ $W -ge 960 ]; then agent-browser click ".aside [data-begin]" >/dev/null 2>&1; else agent-browser click "#startbar-btn" >/dev/null 2>&1; fi; agent-browser wait 500 >/dev/null 2>&1
  check "$T begin: opens the intake" "$(view)" '"intake"'
  check "$T begin: intake button says Begin" "$(ev "document.getElementById('btn-start').textContent.trim()")" '"Begin"'
  check "$T intake: the consent note sits above the Begin button" "$(ev "document.querySelector('#v-intake [data-consent]').getBoundingClientRect().bottom<=document.getElementById('btn-start').getBoundingClientRect().top")" "true"
  click "#back-intake"; check "$T back: returns to the crisis page" "$(view)" '"crisis"'
  click "#crisis-back"; check "$T all crises: returns home" "$(view)" '"home"'
  # ---- cases
  agent-browser eval "location.hash='#/cases';1" >/dev/null 2>&1; agent-browser wait "#h-cases" >/dev/null 2>&1; agent-browser wait 800 >/dev/null 2>&1
  check "$T cases: view and rows" "$(ev "document.body.dataset.view==='cases'&&document.querySelectorAll('#rows li').length>=1")" "true"
  check "$T cases: current tab marked" "$(ev "document.querySelector('.tabs a[aria-current=page]').dataset.nav")" '"cases"'
  agent-browser click "#q" >/dev/null 2>&1; agent-browser type "#q" "zzzz-no-such-family" >/dev/null 2>&1; agent-browser wait 400 >/dev/null 2>&1
  check "$T cases: no-match state and count line" "$(ev "!document.getElementById('no-match').hidden&&/0 of/.test(document.getElementById('count').textContent)")" "true"
  click "#clear"; check "$T cases: clear filters restores the rows" "$(ev "document.getElementById('no-match').hidden&&document.querySelectorAll('#rows li').length>=1")" "true"
  click "#f-status button[data-v=v2]"; check "$T cases: Version 2 filter pressed" "$(ev "document.querySelector('#f-status button[data-v=v2]').getAttribute('aria-pressed')")" '"true"'
  click "#clear"
  check "$T cases: no sideways scroll" "$(ov)" "true"
  check "$T cases: contrast scan clean" "$(scan)" '"[]"'
  agent-browser screenshot $SHOTS/cases-$T.png >/dev/null 2>&1
  # ---- open a case, then back to cases
  click "#rows a.lrow"
  check "$T case: viewer opens by route" "$(ev "/^#\/case\//.test(location.hash)&&document.body.dataset.view==='case'")" "true"
  check "$T case: viewer wording (Read-only, no storage claims)" "$(ev "/Read-only\./.test(document.body.innerText)&&!/computer|stays here|local/i.test(document.body.innerText)")" "true"
  check "$T case: the consent note is at the top, exact text" "$(ev "(()=>{const c=document.querySelector('#v-case [data-consent]');return !!c&&c.textContent.trim()==='Nury saves approved cases, with the names you typed, so you can come back to them. There is no sign-in yet: anyone who can open this app can open the saved cases. Nury sends nothing to the family. Share only what the family has agreed to share.'&&c.getBoundingClientRect().top<innerHeight})()")" "true"
  check "$T case: contrast scan clean" "$(scan)" '"[]"'
  click "#back-case"; check "$T case: back returns to cases" "$(view)" '"cases"'
  # ---- settings sheet: theme radio, Escape, focus returns
  agent-browser eval "location.hash='#/';1" >/dev/null 2>&1; agent-browser wait "#h-home" >/dev/null 2>&1; agent-browser wait 500 >/dev/null 2>&1
  click "#open-settings"; check "$T settings: opens as a modal dialog" "$(ev "document.getElementById('settings').open")" "true"
  OTHER=light; [ $TH = light ] && OTHER=dark
  agent-browser click "input[name=th][value=$OTHER] + span" >/dev/null 2>&1; agent-browser wait 300 >/dev/null 2>&1
  check "$T settings: choosing $OTHER switches the theme" "$(ev "document.documentElement.dataset.theme")" "\"$OTHER\""
  agent-browser click "input[name=th][value=$TH] + span" >/dev/null 2>&1; agent-browser wait 300 >/dev/null 2>&1
  agent-browser press Escape >/dev/null 2>&1; agent-browser wait 300 >/dev/null 2>&1
  check "$T settings: Escape closes and focus returns to the gear" "$(ev "!document.getElementById('settings').open&&document.activeElement.id==='open-settings'")" "true"
  # ---- about sheet
  click "#open-about"; check "$T about: opens" "$(ev "document.getElementById('about').open")" "true"
  check "$T about: carries the consent note" "$(ev "!!document.querySelector('#about [data-consent]')")" "true"
  check "$T about: names the three red-team models, states the limits" "$(ev "(()=>{const t=document.getElementById('about').innerText;return /GPT-5\.4/.test(t)&&/Gemini 3\.1 Pro/.test(t)&&/Llama 4 Maverick/.test(t)&&/not encrypted/.test(t)&&/no pass rate/.test(t)&&!/anonymi/i.test(t)})()")" "true"
  check "$T about: no sideways scroll and contrast clean inside the sheet" "$(ev "(()=>{const d=document.getElementById('about');return d.scrollWidth<=d.clientWidth+1})()")" "true"
  agent-browser press Escape >/dev/null 2>&1; agent-browser wait 300 >/dev/null 2>&1
  check "$T about: Escape closes" "$(ev "!document.getElementById('about').open")" "true"
  # ---- unsaved-work guard (stubbed package screen)
  ev "$(cat $HERE/pkgstub.js)" >/dev/null; ev "sid='x';show('v-pkg');poll();1" >/dev/null; agent-browser wait 900 >/dev/null 2>&1
  click ".brand"
  check "$T guard: tapping home with unsaved work asks first" "$(waitexp "document.getElementById('leave').open&&document.body.dataset.view==='pkg'")" "true"
  click "#leave-stay"; check "$T guard: Stay keeps the work" "$(waitexp "!document.getElementById('leave').open&&document.body.dataset.view==='pkg'")" "true"
  click ".brand"; waitexp "document.getElementById('leave').open" >/dev/null; click "#leave-go"
  check "$T guard: Leave goes home" "$(waitexp "document.body.dataset.view==='home'")" "true"
done; done
# ---- reduced motion: nothing animates
agent-browser set viewport 390 844 >/dev/null 2>&1; agent-browser open "http://127.0.0.1:$PORT/#/" >/dev/null 2>&1
agent-browser set media dark reduced-motion >/dev/null 2>&1 || agent-browser set media reduced-motion >/dev/null 2>&1
agent-browser eval "location.reload();1" >/dev/null 2>&1; agent-browser wait "#h-home" >/dev/null 2>&1; agent-browser wait 700 >/dev/null 2>&1
check "reduced motion: no element is animating" "$(ev "[...document.querySelectorAll('*')].filter(e=>getComputedStyle(e).animationName!=='none').length")" "0"
ev "try{localStorage.setItem('nury-theme','dark')}catch(e){};1" >/dev/null
[ $FAIL = 0 ] && echo "ALL PASS" || { echo "SOME FAILED"; exit 1; }
