#!/usr/bin/env bash
# Real-click test of the ONE shared header and footer, and of the hand-written notes. 390 and 1280 px, Night and Day. No model call.
PORT=${PORT:-8099}; PORT2=${PORT2:-8098}; HERE="$(cd "$(dirname "$0")" && pwd)"; FAIL=0; SHOTS=${SHOTS:-/tmp/nury_shots}; mkdir -p "$SHOTS"
ev(){ agent-browser eval "$1" 2>&1 | tail -1; }
check(){ if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1 (got $2, want $3)"; FAIL=1; fi; }
click(){ agent-browser click "$1" >/dev/null 2>&1; agent-browser wait 500 >/dev/null 2>&1; }
open(){ agent-browser open "$1" >/dev/null 2>&1; agent-browser wait 1600 >/dev/null 2>&1; }
SIG="$(cat $HERE/shellsig.js)"; OVL="$(cat $HERE/notesoverlap.js)"
CASE=$(curl -s localhost:$PORT/api/cases | python3 -c "import sys,json;print(json.load(sys.stdin)['cases'][0]['id'])")
for TH in dark light; do for W in 390 1280; do H=800; [ $W = 390 ] && H=844; T="$TH-$W"
  agent-browser set viewport $W $H >/dev/null 2>&1
  open "http://127.0.0.1:$PORT/#/"; ev "try{localStorage.setItem('nury-theme','$TH');localStorage.removeItem('nury-notes')}catch(e){};1" >/dev/null; open "http://127.0.0.1:$PORT/#/"
  REF=$(ev "$SIG")
  for P in "#/" "#/cases" "#/case/$CASE" "#/crisis/detention"; do open "http://127.0.0.1:$PORT/$P"; check "$T one shell: $P has the same header and footer HTML as Home" "$(ev "$SIG")" "$REF"; done
  for P in network how-it-was-built observability self-improvement; do open "http://127.0.0.1:$PORT/$P"; check "$T one shell: /$P has the same header and footer HTML as Home" "$(ev "$SIG")" "$REF"; done
  open "http://127.0.0.1:$PORT/#/"
  read -r -d '' J <<'JS'
(()=>{const h=document.querySelector('header.top');const l=[...h.querySelectorAll('a')].map(a=>a.textContent.trim()||'mark');return /^Nury/.test(l[0])&&JSON.stringify(l.slice(1))==='["Home","Cases","Network"]'&&h.querySelectorAll('button').length===1&&!!h.querySelector('#theme')})()
JS
  check "$T header: the mark, Home, Cases, Network and the Day/Night switch, nothing else" "$(ev "$J")" "true"
  check "$T header: no link to a page for judges" "$(ev "![...document.querySelectorAll('header.top a')].some(a=>/how-it-was-built|observability|improvement/.test(a.getAttribute('href')))")" "true"
  read -r -d '' J <<'JS'
(()=>{const f=document.querySelector('footer.sitefoot');return /For judges and reviewers/.test(f.textContent)&&JSON.stringify([...f.querySelectorAll('.fnav a')].map(a=>a.textContent.trim()))==='["How this was built","Observability","Self-improvement"]'&&!/Improvement\b/.test(f.textContent.replace(/Self-improvement/g,''))})()
JS
  check "$T footer: 'For judges and reviewers' with the three pages, Self-improvement named so" "$(ev "$J")" "true"
  read -r -d '' J <<'JS'
(()=>{window.scrollTo(0,document.body.scrollHeight);const f=document.querySelector('footer.sitefoot').getBoundingClientRect(),t=document.querySelector('.tabs').getBoundingClientRect();return f.bottom<=innerHeight+1&&(innerWidth>=960||f.bottom<=t.top+1)})()
JS
  check "$T footer: reachable and visible at the end of the page, above the phone tab bar" "$(ev "$J")" "true"
  # notes
  check "$T notes: every note is aria-hidden decoration and sits in the normal flow" "$(ev "[...document.querySelectorAll('.hnote')].every(n=>n.getAttribute('aria-hidden')==='true'&&getComputedStyle(n).position!=='absolute')")" "true"
  read -r -d '' J <<'JS'
(()=>{const n=document.querySelector('#picks').previousElementSibling;const s=getComputedStyle(n);const rot=s.transform!=='none';return /Gochi/.test(s.fontFamily)&&(innerWidth>=640?rot:!rot)})()
JS
  check "$T notes: the home screen shows its note in Gochi Hand, rotated on laptop and a plain caption on phone" "$(ev "$J")" "true"
  check "$T notes: fonts load from this server (Gochi Hand)" "$(ev "document.fonts.check('20px \"Gochi Hand\"')")" "true"
  window_check=$(ev "window.scrollTo(0,0);$OVL")
  check "$T notes: on Home, no note overlaps any text" "$(ev "JSON.parse($OVL).bad.length")" "0"
  open "http://127.0.0.1:$PORT/network"; check "$T notes: Network shows its note and nothing overlaps" "$(ev "JSON.parse($OVL).notes>=1&&JSON.parse($OVL).bad.length===0")" "true"
  open "http://127.0.0.1:$PORT/#/crisis/detention"; ev "(()=>{const b=[...document.querySelectorAll('[data-begin]')].find(x=>x.getBoundingClientRect().height>0);b.click();return 1})()" >/dev/null; agent-browser wait 700 >/dev/null 2>&1
  check "$T notes: Intake shows its note by Begin and nothing overlaps" "$(ev "JSON.parse($OVL).notes>=1&&JSON.parse($OVL).bad.length===0")" "true"
  open "http://127.0.0.1:$PORT2/#/"; ev "$(cat $HERE/gatestub.js)" >/dev/null; ev "window.__phase='ready';sid='x';show('v-pipe');poll();1" >/dev/null; agent-browser wait 1300 >/dev/null 2>&1
  check "$T notes: the gate shows its notes (three on laptop, one caption on phone) and nothing overlaps" "$(ev "(()=>{const o=JSON.parse($OVL);return o.bad.length===0&&(innerWidth>=640?o.notes>=4:o.notes>=2)})()")" "true"
  check "$T notes: the gate buttons keep their own labels (the notes add nothing the labels lack)" "$(ev "JSON.stringify([...document.querySelectorAll('#g-btns .btn')].map(b=>b.textContent.trim()))==='[\"Approve\",\"Edit\",\"Stop\"]'")" "true"
  agent-browser screenshot $SHOTS/gate-notes-$T.png >/dev/null 2>&1
  # hide notes: remembered across a reload
  open "http://127.0.0.1:$PORT/#/"; ev "document.getElementById('notes-toggle').scrollIntoView();1" >/dev/null; click "#notes-toggle"
  check "$T notes: Hide notes hides every note" "$(ev "[...document.querySelectorAll('.hnote')].every(n=>getComputedStyle(n).display==='none')&&document.getElementById('notes-toggle').getAttribute('aria-pressed')==='true'")" "true"
  agent-browser eval "location.reload();1" >/dev/null 2>&1; agent-browser wait 1500 >/dev/null 2>&1
  check "$T notes: the choice is remembered after a reload, and the label says so" "$(ev "document.documentElement.dataset.notes==='off'&&/Show the hand-written notes/.test(document.getElementById('notes-toggle').textContent)")" "true"
  click "#notes-toggle"; check "$T notes: Show notes brings them back" "$(ev "document.documentElement.dataset.notes==='on'&&[...document.querySelectorAll('.hnote')].some(n=>getComputedStyle(n).display!=='none')")" "true"
done; done
ev "try{localStorage.setItem('nury-theme','dark');localStorage.removeItem('nury-notes')}catch(e){};1" >/dev/null
[ $FAIL = 0 ] && echo "ALL PASS" || { echo "SOME FAILED"; exit 1; }
