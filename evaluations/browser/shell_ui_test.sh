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
  agent-browser eval "location.reload();1" >/dev/null 2>&1; agent-browser wait 1500 >/dev/null 2>&1
  REF=$(ev "$SIG")
  for P in "#/" "#/cases" "#/case/$CASE" "#/crisis/detention"; do open "http://127.0.0.1:$PORT/$P"; check "$T one shell: $P has the same header and footer HTML as Home" "$(ev "$SIG")" "$REF"; done
  TAG="$(cat $HERE/taglinecheck.js)"
  for P in "#/" "#/cases" "#/crisis/detention" network how-it-was-built observability self-improvement build-log; do open "http://127.0.0.1:$PORT/$P"; check "$T brand: on /$P the tagline is never in the header and always below a logo, in its own row" "$(ev "$TAG")" "\"ok\""; done
  for P in network how-it-was-built observability self-improvement build-log; do open "http://127.0.0.1:$PORT/$P"; check "$T one shell: /$P has the same header and footer HTML as Home" "$(ev "$SIG")" "$REF"; done
  open "http://127.0.0.1:$PORT/#/"
  read -r -d '' J <<'JS'
(()=>{const h=document.querySelector('header.top');const l=[...h.querySelectorAll('a')].map(a=>a.textContent.trim()||'mark');return /^Nury/.test(l[0])&&JSON.stringify(l.slice(1))==='["Home","Cases","Network"]'&&h.querySelectorAll('button').length===1&&!!h.querySelector('#theme')})()
JS
  check "$T header: the mark, Home, Cases, Network and the Day/Night switch, nothing else" "$(ev "$J")" "true"
  read -r -d '' J <<'JS'
(()=>{const h=document.querySelector('header.top');const hb=h.getBoundingClientRect(),b=document.getElementById('theme').getBoundingClientRect();return Math.round(b.height)===36&&Math.round(b.width)===36&&(b.top-hb.top)>=12&&(hb.bottom-b.bottom)>=12&&Math.abs((b.top+b.height/2)-(hb.top+(hb.height-1)/2))<=2})()
JS
  check "$T header: the Day/Night switch is a 36 px control, centred, with at least 12 px of air above and below" "$(ev "$J")" "true"
  check "$T header: at least 12 px of padding above the content of the bar" "$(ev "parseFloat(getComputedStyle(document.querySelector('header.top .wrap')).paddingTop)>=12")" "true"
  read -r -d '' J <<'JS'
(()=>{const vis=e=>e.getBoundingClientRect().height>0&&getComputedStyle(e).display!=='none';const T='An AI Crisis Response Agent';const h=document.querySelector('header.top .brand .tg'),f=document.querySelector('footer.sitefoot .lockup .tg');return !!h&&!!f&&h.textContent===T&&f.textContent===T&&[...document.querySelectorAll('main .lockup, main .brand, #final-body .lockup')].filter(vis).length===0})()
JS
  check "$T logo: the lockup is in the header and in the footer, and in no page body" "$(ev "$J")" "true"
  check "$T header: no link to a page for judges" "$(ev "![...document.querySelectorAll('header.top a')].some(a=>/how-it-was-built|observability|improvement/.test(a.getAttribute('href')))")" "true"
  read -r -d '' J <<'JS'
(()=>{const f=document.querySelector('footer.sitefoot');return /For judges and reviewers/.test(f.textContent)&&JSON.stringify([...f.querySelectorAll('.fnav a')].map(a=>a.textContent.trim()))==='["How this was built","Observability","Self-improvement","What did not work","Economics","The pattern","Standards we use"]'&&!/Improvement\b/.test(f.textContent.replace(/Self-improvement/g,''))})()
JS
  check "$T footer: 'For judges and reviewers' with the three pages, Self-improvement named so" "$(ev "$J")" "true"
  read -r -d '' J <<'JS'
(()=>{window.scrollTo(0,document.body.scrollHeight);const f=document.querySelector('footer.sitefoot').getBoundingClientRect(),t=document.querySelector('.tabs').getBoundingClientRect();return f.bottom<=innerHeight+1&&(innerWidth>=960||f.bottom<=t.top+1)})()
JS
  check "$T footer: reachable and visible at the end of the page, above the phone tab bar" "$(ev "$J")" "true"
  # notes
  check "$T notes: every note is aria-hidden decoration and sits in the normal flow" "$(ev "[...document.querySelectorAll('.hnote')].every(n=>n.getAttribute('aria-hidden')==='true'&&getComputedStyle(n).position!=='absolute')")" "true"
  agent-browser eval "document.getElementById('hero-btn').click();1" >/dev/null 2>&1; agent-browser wait 600 >/dev/null 2>&1
  read -r -d '' J <<'JS'
(()=>{const n=document.querySelector('#chooser .hnote');if(!n)return false;const s=getComputedStyle(n);const rot=s.transform!=='none';return /Gochi/.test(s.fontFamily)&&(innerWidth>=640?rot:!rot)&&/sounds like your call/.test(n.textContent)})()
JS
  check "$T notes: the crisis chooser shows its note in Gochi Hand, rotated on laptop and a plain caption on phone" "$(ev "$J")" "true"
  agent-browser eval "document.getElementById('chooser').close();1" >/dev/null 2>&1
  check "$T notes: fonts load from this server (Gochi Hand)" "$(ev "document.fonts.check('20px \"Gochi Hand\"')")" "true"
  window_check=$(ev "window.scrollTo(0,0);$OVL")
  check "$T notes: on Home, no note overlaps any text" "$(ev "JSON.parse($OVL).bad.length")" "0"
  open "http://127.0.0.1:$PORT/network"; check "$T notes: Network shows its note and nothing overlaps" "$(ev "JSON.parse($OVL).notes>=1&&JSON.parse($OVL).bad.length===0")" "true"
  open "http://127.0.0.1:$PORT/#/crisis/detention"; ev "(()=>{const b=[...document.querySelectorAll('[data-begin]')].find(x=>x.getBoundingClientRect().height>0);b.click();return 1})()" >/dev/null; agent-browser wait 700 >/dev/null 2>&1
  check "$T notes: Intake shows its note by Begin and nothing overlaps" "$(ev "JSON.parse($OVL).notes>=1&&JSON.parse($OVL).bad.length===0")" "true"
  open "http://127.0.0.1:$PORT2/#/"; ev "$(cat $HERE/gatestub.js)" >/dev/null; ev "window.__phase='ready';sid='x';show('v-pipe');poll();1" >/dev/null; agent-browser wait 1300 >/dev/null 2>&1
  check "$T notes: the gate shows its notes (one by Approve, one by the chips, plus the footer note) and nothing overlaps" "$(ev "(()=>{const o=JSON.parse($OVL);return o.bad.length===0&&o.notes>=3})()")" "true"
  check "$T notes: the gate buttons keep their own labels (the notes add nothing the labels lack)" "$(ev "JSON.stringify([...document.querySelectorAll('#g-btns .btn')].map(b=>b.textContent.trim()))==='[\"Approve\",\"Edit\",\"Stop\"]'")" "true"
  agent-browser screenshot $SHOTS/gate-notes-$T.png >/dev/null 2>&1
  # no toggle, no hidden copies: the notes are always shown, one text per note
  open "http://127.0.0.1:$PORT/#/"
  read -r -d '' J <<'JS'
(()=>{const rules=[...document.styleSheets].flatMap(ss=>{try{return [...ss.cssRules]}catch(e){return []}}).flatMap(r=>r.cssRules?(/print/.test(r.conditionText||'')?[]:[...r.cssRules]):[r]);const hid=rules.filter(r=>r.selectorText&&/hnote/.test(r.selectorText)&&!/hn-a/.test(r.selectorText)&&r.style&&r.style.display==='none');const t=[...document.querySelectorAll('.hnote')].map(n=>n.textContent);return !document.getElementById('notes-toggle')&&!document.documentElement.dataset.notes&&hid.length===0&&new Set(t).size===t.length})()
JS
  check "$T notes: there is no Hide notes control, no display:none variant and no duplicate note text" "$(ev "$J")" "true"
  read -r -d '' J <<'JS'
(()=>{const f=document.querySelector('.sitefoot'),p=f.querySelector('.prov'),d=f.querySelector('.fine');return /Built in Boulder, Colorado, during the Gloo AI Hackathon, October 6 to 8, 2026\./.test(p.textContent)&&p.querySelector('a').getAttribute('href')==='/build-log'&&/See the build log/.test(p.textContent)&&p.getBoundingClientRect().bottom<=d.getBoundingClientRect().top+1})()
JS
  check "$T footer: the provenance line sits above the disclaimer and links to the build log" "$(ev "$J")" "true"
done; done
ev "try{localStorage.setItem('nury-theme','dark');localStorage.removeItem('nury-notes')}catch(e){};1" >/dev/null
[ $FAIL = 0 ] && echo "ALL PASS" || { echo "SOME FAILED"; exit 1; }
