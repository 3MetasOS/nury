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
  read -r -d '' J <<'JS'
(()=>{const e=document.activeElement;const s=getComputedStyle(e);return e!==document.body&&s.outlineStyle!=='none'&&parseFloat(s.outlineWidth)>=2})()
JS
  check "$T keyboard: focus ring visible on a focused control" "$(ev "$J")" "true"
  # ---- crisis detail
  click "#picks a.pk"
  check "$T crisis: hash and view" "$(ev "location.hash+'|'+document.body.dataset.view")" '"#/crisis/detention|crisis"'
  check "$T crisis: five stages from the playbook, drawn as a path diagram" "$(ev "document.querySelectorAll('#crisis-page .st').length===5&&document.querySelectorAll('#crisis-page svg.dgm .dg-node.on').length===5")" "true"
  check "$T crisis: 911 line, never list, time note" "$(ev "/call 911 first/.test(document.body.innerText)&&/What Nury will never do/.test(document.body.innerText)&&/about a minute/i.test(document.body.innerText)")" "true"
  read -r -d '' J <<'JS'
(()=>{const b=[...document.querySelectorAll('[data-begin]')].find(x=>x.getBoundingClientRect().height>0&&getComputedStyle(x).display!=='none');if(!b)return false;const r=b.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight&&r.height>=56})()
JS
  check "$T crisis: Begin button reachable without scrolling" "$(ev "$J")" "true"
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
  click "#f-status button[data-v=v2]"; check "$T cases: Updated filter pressed" "$(ev "document.querySelector('#f-status button[data-v=v2]').getAttribute('aria-pressed')")" '"true"'
  click "#clear"
  check "$T cases: no sideways scroll" "$(ov)" "true"
  check "$T cases: contrast scan clean" "$(scan)" '"[]"'
  agent-browser screenshot $SHOTS/cases-$T.png >/dev/null 2>&1
  # ---- open a case, then back to cases
  click "#rows a.lrow"
  check "$T case: viewer opens by route" "$(ev "/^#\/case\//.test(location.hash)&&document.body.dataset.view==='case'")" "true"
  check "$T case: viewer wording (Read-only, no storage claims)" "$(ev "/Read-only\./.test(document.body.innerText)&&!/computer|stays here|local/i.test(document.body.innerText)")" "true"
  read -r -d '' J <<'JS'
(()=>{const c=document.querySelector('#v-case [data-consent]');return !!c&&c.textContent.trim()==='Nury saves approved cases, with the names you typed, so you can come back to them. There is no sign-in yet: anyone who can open this app can open the saved cases. Nury sends nothing to the family. Share only what the family has agreed to share.'&&c.getBoundingClientRect().top<innerHeight})()
JS
  check "$T case: the consent note is at the top, exact text" "$(ev "$J")" "true"
  check "$T case: contrast scan clean" "$(scan)" '"[]"'
  click "#back-case"; check "$T case: back returns to cases" "$(view)" '"cases"'
  # ---- theme toggle in the shared header (persists across a reload)
  agent-browser eval "location.hash='#/';1" >/dev/null 2>&1; agent-browser wait "#h-home" >/dev/null 2>&1; agent-browser wait 500 >/dev/null 2>&1
  OTHER=light; [ $TH = light ] && OTHER=dark
  click "#theme"; check "$T theme: the header toggle switches to $OTHER" "$(ev "document.documentElement.dataset.theme")" "\"$OTHER\""
  check "$T theme: toggle label names the mode and the switch" "$(ev "/Switch to/.test(document.getElementById('theme').getAttribute('aria-label'))")" "true"
  agent-browser eval "location.reload();1" >/dev/null 2>&1; agent-browser wait "#h-home" >/dev/null 2>&1; agent-browser wait 700 >/dev/null 2>&1
  check "$T theme: the choice survives a reload" "$(ev "document.documentElement.dataset.theme")" "\"$OTHER\""
  click "#theme"; check "$T theme: toggling back restores $TH" "$(ev "document.documentElement.dataset.theme")" "\"$TH\""
  # ---- the crisis chooser (hero button opens it; it never scrolls the page)
  agent-browser eval "window.scrollTo(0,0);1" >/dev/null 2>&1
  click "#hero-btn"
  read -r -d '' J <<'JS'
(()=>{const d=document.getElementById('chooser');return d.open&&d.getAttribute('aria-modal')==='true'&&document.getElementById('chooser-t').textContent==='A family needs help'})()
JS
  check "$T chooser: hero button opens a modal titled 'A family needs help'" "$(ev "$J")" "true"
  check "$T chooser: the page did not scroll" "$(ev "scrollY===0")" "true"
  read -r -d '' J <<'JS'
(()=>{const d=document.getElementById('chooser');const l=[...d.querySelectorAll('a.pk')],s=[...d.querySelectorAll('.pk.soon')];return l.length===2&&l.every(a=>a.querySelector('svg use')&&a.getBoundingClientRect().height>=56)&&s.length===2&&s.every(e=>e.tagName==='DIV'&&e.tabIndex<0&&/Coming soon/.test(e.textContent))})()
JS
  check "$T chooser: two live crises as links with icons, two coming soon that are not links" "$(ev "$J")" "true"
  check "$T chooser: a clear Close button" "$(ev "[...document.querySelectorAll('#chooser button')].some(b=>b.textContent.trim()==='Close'&&b.getBoundingClientRect().height>=44)")" "true"
  read -r -d '' J <<'JS'
(()=>{const r=document.getElementById('chooser').getBoundingClientRect();return innerWidth<640?Math.abs(r.bottom-innerHeight)<2:(r.top>0&&r.bottom<innerHeight)})()
JS
  check "$T chooser: sits as a bottom sheet on phone, a centred modal on laptop" "$(ev "$J")" "true"
  for i in 1 2 3 4 5 6 7 8 9 10 11 12; do agent-browser press Tab >/dev/null 2>&1; done
  check "$T chooser: focus stays trapped inside after 12 Tab presses" "$(ev "document.getElementById('chooser').contains(document.activeElement)")" "true"
  check "$T chooser: contrast scan clean" "$(scan)" '"[]"'
  agent-browser screenshot $SHOTS/chooser-$T.png >/dev/null 2>&1
  agent-browser press Escape >/dev/null 2>&1; agent-browser wait 300 >/dev/null 2>&1
  check "$T chooser: Escape closes and focus returns to the hero button" "$(ev "!document.getElementById('chooser').open&&document.activeElement.id==='hero-btn'")" "true"
  click "#hero-btn"; click "#chooser button[data-close]"
  check "$T chooser: Close closes and focus returns to the hero button" "$(ev "!document.getElementById('chooser').open&&document.activeElement.id==='hero-btn'")" "true"
  click "#hero-btn"; click "#chooser a.pk"
  check "$T chooser: choosing Detention closes it and opens the crisis page" "$(ev "!document.getElementById('chooser').open&&location.hash==='#/crisis/detention'&&document.body.dataset.view==='crisis'")" "true"
  agent-browser eval "location.hash='#/';1" >/dev/null 2>&1; agent-browser wait 500 >/dev/null 2>&1
  # ---- one shared header on every page
  SIG="$(cat $HERE/shellsig.js)"
  HOMESIG=$(ev "$SIG")
  agent-browser open "http://127.0.0.1:$PORT/network" >/dev/null 2>&1; agent-browser wait "#h-net" >/dev/null 2>&1; agent-browser wait 800 >/dev/null 2>&1
  check "$T shell: Network has the same header as Home" "$(ev "$SIG")" "$HOMESIG"
  check "$T shell: Network marks its own tab" "$(ev "document.querySelector('.tabs a[aria-current=page]').dataset.nav")" '"network"'
  check "$T shell: Network keeps its content and has no sideways scroll" "$(ev "!!document.getElementById('h-net')&&document.documentElement.scrollWidth<=innerWidth")" "true"
  check "$T shell: Network contrast clean" "$(scan)" '"[]"'
  agent-browser screenshot $SHOTS/network-$T.png >/dev/null 2>&1
  click "#theme"; check "$T shell: the toggle works on Network too" "$(ev "document.documentElement.dataset.theme")" "\"$OTHER\""; click "#theme"
  click ".tabs a[data-nav=cases]"; agent-browser wait "#h-cases" >/dev/null 2>&1; agent-browser wait 800 >/dev/null 2>&1
  check "$T shell: from Network the Cases tab lands on Cases with the same header" "$(ev "document.body.dataset.view==='cases'")|$(ev "$SIG")" "true|$HOMESIG"
  check "$T shell: Cases has the same header as Home" "$(ev "$SIG")" "$HOMESIG"
  click "#rows a.lrow"; agent-browser wait 600 >/dev/null 2>&1
  check "$T shell: the case viewer has the same header" "$(ev "$SIG")" "$HOMESIG"
  agent-browser eval "location.hash='#/crisis/detention';1" >/dev/null 2>&1; agent-browser wait 700 >/dev/null 2>&1
  check "$T shell: the crisis page has the same header" "$(ev "$SIG")" "$HOMESIG"
  # ---- How this was built: a full page, not a popup
  agent-browser eval "location.href='/#/';1" >/dev/null 2>&1; agent-browser wait "#h-home" >/dev/null 2>&1; agent-browser wait 700 >/dev/null 2>&1
  check "$T how: there is no About popup anywhere" "$(ev "!document.getElementById('about')&&!document.querySelector('[data-about]')")" "true"
  click ".fnav a[data-nav=how]"; agent-browser wait "#doc" >/dev/null 2>&1; agent-browser wait 1500 >/dev/null 2>&1
  check "$T how: the header link opens /how-it-was-built" "$(ev "location.pathname")" '"/how-it-was-built"'
  check "$T how: same shared header as every page, link marked current" "$(ev "$SIG")|$(ev "document.querySelector('.fnav a[data-nav=how]').getAttribute('aria-current')")" "$HOMESIG|\"page\""
  read -r -d '' J <<'JS'
(()=>{const t=document.body.innerText;return /An AI Crisis Response Agent/.test(document.querySelector('header.top').textContent)&&!!document.querySelector('[data-consent]')&&document.querySelector('[data-disclose]').textContent==='The Jev decision API from TypeSafe is used as typed judges in our evaluation harness and as a run-time draft classifier; disclosed as third-party technology per the rules.'&&!/solo pastor|local computer/i.test(t)})()
JS
  check "$T how: tagline, consent note and disclosure line are on the page" "$(ev "$J")" "true"
  read -r -d '' J <<'JS'
(()=>{const a=[...document.querySelectorAll('#toc a')];return a.length>=8&&a.every(x=>document.getElementById(x.getAttribute('href').slice(1)))})()
JS
  check "$T how: contents lists all sections and each link has a target" "$(ev "$J")" "true"
  read -r -d '' J <<'JS'
(async()=>{const d=await (await fetch('/api/rules')).json();const rows=[...document.querySelectorAll('[data-live=rules] tbody tr')].map(r=>r.id.replace('rule-',''));return d.rules.length>=25&&d.rules.every(r=>rows.includes(r.name))&&rows.length===d.rules.length})()
JS
  check "$T how: the live rules table lists every check the app reports" "$(ev "$J")" "true"
  read -r -d '' J <<'JS'
(()=>{const p=[...document.querySelectorAll('[data-live=playbooks] details.pbk')];const live=p.filter(d=>d.querySelectorAll('.stg h4').length>=5);return live.length===2&&p.length===4})()
JS
  check "$T how: the live playbook list shows both live playbooks with their five stages" "$(ev "$J")" "true"
  check "$T how: no sideways scroll on the page (tables scroll inside their own box)" "$(ov)" "true"
  check "$T how: tables and code blocks are keyboard-reachable" "$(ev "[...document.querySelectorAll('.tw,pre')].every(e=>e.tabIndex===0)")" "true"
  check "$T how: contrast scan clean" "$(scan)" '"[]"'
  if [ $W -lt 960 ]; then
    check "$T how: contents is collapsed on phone and opens on tap" "$(ev "!document.getElementById('toc').open")" "true"
    click "#toc summary"; check "$T how: tapping Contents opens it" "$(ev "document.getElementById('toc').open")" "true"
    click "#toc li:nth-child(3) a"; check "$T how: choosing a section closes Contents and lands on it" "$(ev "!document.getElementById('toc').open&&/^#/.test(location.hash)&&document.getElementById(location.hash.slice(1)).getBoundingClientRect().top<innerHeight")" "true"
  else
    read -r -d '' J <<'JS'
(()=>{const t=document.getElementById('toc');window.scrollTo(0,1800);return t.open&&getComputedStyle(t).position==='sticky'&&t.getBoundingClientRect().top<200})()
JS
    check "$T how: contents is open and sticky on laptop" "$(ev "$J")" "true"
  fi
  agent-browser eval "location.href='/how-it-was-built#5-how-people-add-rules';1" >/dev/null 2>&1; agent-browser wait 1800 >/dev/null 2>&1
  check "$T how: a deep link lands on its section" "$(ev "document.getElementById('5-how-people-add-rules').getBoundingClientRect().top<innerHeight*0.5")" "true"
  agent-browser screenshot $SHOTS/how-$T.png >/dev/null 2>&1
  agent-browser eval "location.href='/#/';1" >/dev/null 2>&1; agent-browser wait "#h-home" >/dev/null 2>&1; agent-browser wait 700 >/dev/null 2>&1
  check "$T how: the footer links to the page" "$(ev "document.querySelector('footer a[href=\"/how-it-was-built\"]').getAttribute('href')")" '"/how-it-was-built"'
  # ---- follow-up flag (a plain mark set by the pastor; no dates, no reminders)
  agent-browser eval "location.hash='#/cases';1" >/dev/null 2>&1; agent-browser wait "#h-cases" >/dev/null 2>&1; agent-browser wait 700 >/dev/null 2>&1
  click "#rows a.lrow"; agent-browser wait 700 >/dev/null 2>&1
  CASEHASH=$(ev "location.hash" | tr -d '"')
  # ---- case detail: width, tab bar, in-place tabs, deep link
  read -r -d '' J <<'JS'
(()=>{const L=s=>{const r=document.querySelector(s).getBoundingClientRect();return[Math.round(r.left),Math.round(r.right)]};const w=innerWidth>=960?[104,1176]:[16,374];const same=(a,b)=>a[0]===b[0]&&a[1]===b[1];
return same(L('#v-case .chd'),w)&&same(L('.ctabs'),w)&&same(L('.aboutsaved'),w)&&same(L('.casehd'),w)&&L('#case-card')[0]===w[0]&&L('#case-card')[1]===w[1]&&document.documentElement.scrollWidth<=innerWidth})()
JS
  check "$T case detail: header, tab bar and notice use the Cases content width, panel starts at the same left edge" "$(ev "$J")" "true"
  check "$T case detail: the actions are small (36 px) and the notice is the last block before the footer" "$(ev "[...document.querySelectorAll('.chd-a .btn.sm:not(.hidden)')].every(b=>Math.round(b.getBoundingClientRect().height)===36)&&document.querySelector('.aboutsaved').getBoundingClientRect().top>document.querySelector('#case-card').getBoundingClientRect().bottom-1&&!document.querySelector('#v-case .consent:not(.aboutsaved .consent)')")" "true"
  check "$T case detail: Overview is full-width cards: the sequence with arrows first (44 px nodes, 14 px / 12 px text, five links), then Next steps as live text lanes, no old title" "$(waitexp "(()=>{const c=[...document.querySelectorAll('#case-page .ovc')];const w=innerWidth>=960?[104,1176]:[16,374];const ok=c.length>=3&&c.every(e=>{const r=e.getBoundingClientRect();return Math.round(r.left)===w[0]&&Math.round(r.right)===w[1]});return ok&&c[0].querySelector('h3').textContent==='How this case went'&&c[1].querySelector('h3').textContent==='Next steps'&&c[1].querySelectorAll('.lane li').length>3&&c[0].querySelectorAll('a.stn').length===5&&c[0].querySelectorAll('svg.arr').length>=5&&Math.round(c[0].querySelector('.nd').getBoundingClientRect().width)===44&&getComputedStyle(c[0].querySelector('.nm')).fontSize==='14px'&&getComputedStyle(c[0].querySelector('.stt')).fontSize==='12px'&&!document.getElementById('case-page').textContent.includes('Immigration detention')&&!document.querySelector('.crail')})()")" "true"
  ev "window.scrollTo(0,200);1" >/dev/null; SY0=$(ev "Math.round(scrollY)")
  click "#case-chips .chip:nth-child(3)"
  check "$T case detail: clicking a tab keeps the scroll position, changes the hash and does not reload" "$(waitexp "Math.abs(scrollY-$SY0)<=2&&/\/rights$/.test(location.hash)&&document.querySelector('#case-chips .chip.on').dataset.p.includes('rights')&&document.body.dataset.view==='case'")" "true"
  agent-browser press ArrowRight >/dev/null 2>&1; agent-browser wait 300 >/dev/null 2>&1
  check "$T case detail: arrow keys move to the next tab (roving focus), End jumps to the last, Home to the first" "$(ev "(()=>{const on=()=>document.querySelector('#case-chips .chip.on').textContent;const a=on()==='attorney';return a})()")" "true"
  agent-browser press End >/dev/null 2>&1; agent-browser wait 300 >/dev/null 2>&1; E1=$(ev "document.querySelector('#case-chips .chip.on').textContent"); agent-browser press Home >/dev/null 2>&1; agent-browser wait 300 >/dev/null 2>&1
  check "$T case detail: End selects log and Home selects Overview" "$E1:$(ev "document.querySelector('#case-chips .chip.on').textContent")" '"log":"Overview"'
  agent-browser eval "location.hash='$CASEHASH/checklist';1" >/dev/null 2>&1; agent-browser wait 900 >/dev/null 2>&1; agent-browser eval "location.reload();1" >/dev/null 2>&1; agent-browser wait 1800 >/dev/null 2>&1
  check "$T case detail: a deep link and a refresh keep the tab" "$(waitexp "document.querySelector('#case-chips .chip.on')&&document.querySelector('#case-chips .chip.on').dataset.p.includes('checklist')")" "true"
  agent-browser eval "location.hash='$CASEHASH';1" >/dev/null 2>&1; agent-browser wait 900 >/dev/null 2>&1
  check "$T follow-up: toggle is offered in the case viewer" "$(ev "!document.getElementById('case-follow').classList.contains('hidden')")" "true"
  P="document.getElementById('case-follow').getAttribute('aria-pressed')"
  click "#case-follow"
  check "$T follow-up: a single click only opens the dialog, focus starts on Cancel, nothing changed yet" "$(waitexp "document.getElementById('confirm').open&&document.activeElement.id==='confirm-no'&&/Mark this case as needs follow-up\?/.test(document.getElementById('confirm-t').textContent)&&/moves to the top of your list/.test(document.getElementById('confirm-b').textContent)&&document.getElementById('confirm-ok').textContent==='Mark as needs follow-up'&&$P==='false'")" "true"
  click "#confirm-no"
  check "$T follow-up: Cancel changes nothing" "$(waitexp "!document.getElementById('confirm').open&&$P==='false'")" "true"
  click "#case-follow"; waitexp "document.getElementById('confirm').open" >/dev/null; ev "document.getElementById('confirm').dispatchEvent(new Event('cancel',{cancelable:true}));document.getElementById('confirm').close();1" >/dev/null
  check "$T follow-up: Escape (cancel) changes nothing" "$(waitexp "!document.getElementById('confirm').open&&$P==='false'")" "true"
  click "#case-follow"; waitexp "document.getElementById('confirm').open" >/dev/null; click "#confirm-ok"
  check "$T follow-up: Confirm marks it and a toast with Undo appears" "$(waitexp "$P==='true'&&!document.getElementById('toast').hidden&&/Marked as needs follow-up\./.test(document.getElementById('toast-t').textContent)&&!document.getElementById('toast-undo').hidden")" "true"
  click "#toast-undo"
  check "$T follow-up: Undo restores it and the toast goes" "$(waitexp "$P==='false'&&document.getElementById('toast').hidden")" "true"
  click "#case-follow"; waitexp "document.getElementById('confirm').open" >/dev/null; click "#confirm-ok"; waitexp "$P==='true'" >/dev/null
  agent-browser eval "location.hash='#/cases/follow';1" >/dev/null 2>&1; agent-browser wait 900 >/dev/null 2>&1
  check "$T follow-up: Cases filter 'Needs follow-up' lists it with the chip" "$(ev "document.querySelectorAll('#rows li').length>=1&&!!document.querySelector('#rows .s-follow')")" "true"
  agent-browser eval "location.hash='#/';1" >/dev/null 2>&1; agent-browser wait 800 >/dev/null 2>&1
  check "$T follow-up: Home shows the marked case first with the chip" "$(ev "!!document.querySelector('#cont-list li:first-child .s-follow')")" "true"
  agent-browser eval "location.hash='$CASEHASH';1" >/dev/null 2>&1; agent-browser wait 800 >/dev/null 2>&1
  click "#case-follow"
  check "$T follow-up: clearing asks first, with the clear wording" "$(waitexp "document.getElementById('confirm').open&&/Clear the follow-up flag\?/.test(document.getElementById('confirm-t').textContent)&&document.getElementById('confirm-ok').textContent==='Clear follow-up'&&$P==='true'")" "true"
  click "#confirm-ok"
  check "$T follow-up: confirming clears it, with a toast" "$(waitexp "$P==='false'&&/Follow-up cleared\./.test(document.getElementById('toast-t').textContent)")" "true"
  # ---- 'Something changed' asks before it drafts again (only the Cancel path runs: Confirm would call the model)
  click "#b-changed"; ev "document.getElementById('rv-note').value='A test note';1" >/dev/null; click "#rv-go"
  check "$T changed: Record asks first, with the updated-draft wording, and Cancel sends nothing" "$(waitexp "document.getElementById('confirm').open&&/Record what changed\?/.test(document.getElementById('confirm-t').textContent)&&/keeps the first draft/.test(document.getElementById('confirm-b').textContent)&&document.getElementById('confirm-ok').textContent==='Record and draft again'&&document.activeElement.id==='confirm-no'")" "true"
  click "#confirm-no"; check "$T changed: Cancel closes it and nothing was drafted" "$(waitexp "!document.getElementById('confirm').open&&document.body.dataset.view!=='pipe'")" "true"
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
