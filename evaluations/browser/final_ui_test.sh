#!/usr/bin/env bash
# Real-click test of the final package page and of Download (txt) and the case zip. Uses REAL saved cases (their approved text) as the finished session. No model call.
PORT=${PORT:-8099}; HERE="$(cd "$(dirname "$0")" && pwd)"; FAIL=0; SHOTS=${SHOTS:-/tmp/nury_shots}; mkdir -p "$SHOTS" /tmp/dl
ev(){ agent-browser eval "$1" 2>&1 | tail -1; }
check(){ if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1 (got $2, want $3)"; FAIL=1; fi; }
click(){ agent-browser click "$1" >/dev/null 2>&1; agent-browser wait 400 >/dev/null 2>&1; }
scan(){ ev "$(cat $HERE/contrast.js)"; }
ovl(){ ev "$(cat $HERE/notesoverlap.js)"; }
STUB="$(cat $HERE/finalstub.js | tr '\n' ' ')"
CASES=$(curl -s localhost:$PORT/api/cases | python3 -c "
import sys,json,urllib.request
cs=json.load(sys.stdin)['cases'];out={}
for c in cs:
    d=json.load(urllib.request.urlopen('http://localhost:$PORT/api/case/'+c['id']))
    m=d['meta']
    out.setdefault(m['language'],c['id'])
print(out.get('es',''),out.get('en',''))")
ES=${CASES% *}; EN=${CASES#* }
load(){ agent-browser open "about:blank" >/dev/null 2>&1; agent-browser open "http://127.0.0.1:$PORT/#/" >/dev/null 2>&1; agent-browser wait 1400 >/dev/null 2>&1
  ev "(async()=>{$STUB; return await window.__finalStub('$1',$2)})()" >/dev/null; ev "sid='x';show('v-pkg');poll();1" >/dev/null; agent-browser wait 1400 >/dev/null 2>&1; }
for TH in dark light; do for W in 390 1280; do H=800; [ $W = 390 ] && H=844; T="$TH-$W"
 agent-browser set viewport $W $H >/dev/null 2>&1
 for LANG in es en; do CASE=$ES; [ $LANG = en ] && CASE=$EN; [ -z "$CASE" ] && continue; TT="$T/$LANG"
  agent-browser open "http://127.0.0.1:$PORT/#/" >/dev/null 2>&1; ev "try{localStorage.setItem('nury-theme','$TH');localStorage.removeItem('nury-pastor');localStorage.removeItem('nury-notes')}catch(e){};1" >/dev/null
  load "$CASE" "{edited:['pastoral'],addVerse:true}"
  check "$TT final: the four sections are on the page in order, each with a heading" "$(ev "JSON.stringify([...document.querySelectorAll('#final-body section.fp-sec')].map(s=>s.id))")" '"[\"fp-1\",\"fp-2\",\"fp-3\",\"fp-4\"]"'
  check "$TT final: headline is the case's own situation sentence plus the fixed line" "$(ev "/Here is what the family can do tonight\.\$/.test(document.getElementById('fp-h1').textContent)&&document.getElementById('fp-h1').textContent.length>50")" "true"
  check "$TT final: key facts show case, date, family language and a name field" "$(ev "(()=>{const k=document.querySelector('.keyfacts').textContent;return /Case/.test(k)&&/Date/.test(k)&&/Family language/.test(k)&&!!document.getElementById('kf-pastor')})()")" "true"
  check "$TT final: the disclaimer is on the page, visible" "$(ev "(()=>{const d=document.querySelector('.fp-disc');return !!d&&d.textContent.length>40&&d.getBoundingClientRect().height>0})()")" "true"
  read -r -d '' J <<'JS'
(()=>{const st=window.__stubStages.find(x=>x.id==='pastoral').final.split('\n');const vt=st.find(l=>/^«.+»\s*$/.test(l.trim())).trim();const vr=st[st.indexOf(st.find(l=>l.trim()===vt))+1].trim();
return document.querySelector('.verse .vt').textContent===vt&&document.querySelector('.verse .vr').textContent===vr&&/word for word/.test(document.querySelector('.vsrc').textContent)})()
JS
  check "$TT final: the verse and its reference are verbatim as the engine inserted them, with how it was chosen" "$(ev "$J")" "true"
  check "$TT final: the pastor's edit is marked as the pastor's" "$(ev "[...document.querySelectorAll('.edmark')].length===1&&document.querySelector('#fp-3 .edmark')!==null")" "true"
  read -r -d '' J <<'JS'
(()=>{const c=[...document.querySelectorAll('#fp-4 .rc')];const calls=[...document.querySelectorAll('#fp-4 a.call[href^="tel:"]')];const more=document.querySelector('#fp-4 details.more');
const shown=document.querySelectorAll('#fp-4 > ul.cards > li').length;
return c.length>=1&&shown<=5&&(c.length<=5||!!more)&&calls.every(a=>/^(Call|Llamar) (1-)?\d{3}-\d{3}-\d{4}$/.test(a.textContent.trim()))&&[...document.querySelectorAll('.rtag')].every(t=>/church|iglesia|official|oficial|national|nacional/i.test(t.textContent))&&c.every(x=>x.querySelector('.rn').textContent.length>2)})()
JS
  check "$TT final: resources are cards (at most 5 shown, the rest behind a 'more'), big tap-to-call with a formatted number, labelled by source" "$(ev "$J")" "true"
  check "$TT final: a big call button is at least 56 px tall" "$(ev "[...document.querySelectorAll('#fp-4 a.call')].filter(a=>a.getBoundingClientRect().height>0).every(a=>a.getBoundingClientRect().height>=56||a.classList.contains('alt'))")" "true"
  check "$TT final: DO NOT is a separate box and the documents are a checklist" "$(ev "!!document.querySelector('#fp-2 .donot')&&document.querySelectorAll('#fp-2 .ck input[type=checkbox]').length>=3&&document.querySelectorAll('#fp-2 .todo li').length>=3")" "true"
  check "$TT final: no outcome or prediction text on the page (outcomes.json holds run outcomes only)" "$(ev "!document.getElementById('fp-outcomes')&&!/probab|odds|will be (deported|released)|serán deportad|será liberad/i.test(document.getElementById('final').textContent)")" "true"
  read -r -d '' J <<'JS'
(()=>{const n=[...document.querySelectorAll('#final-body .hnote')];return n.length===2&&n.every(x=>x.getAttribute('aria-hidden')==='true')&&/before you call/.test(n[0].textContent)&&/for them, from you/.test(n[1].textContent)})()
JS
  check "$TT final: the two hand-written notes are by section 1 and section 3, decoration only" "$(ev "$J")" "true"
  check "$TT final: no note overlaps text" "$(ev "JSON.parse($(cat $HERE/notesoverlap.js)).bad.length")" "0"
  check "$TT final: the tagline is below the logo (never beside) and not in the header" "$(ev "$(cat $HERE/taglinecheck.js)")" "\"ok\""
  check "$TT final: no sideways scroll" "$(ev "document.documentElement.scrollWidth<=innerWidth")" "true"
  check "$TT final: contrast scan clean" "$(scan)" '"[]"'
  # the pastor's name: real typing, printed on the family copy, remembered
  agent-browser click "#kf-pastor" >/dev/null 2>&1; agent-browser type "#kf-pastor" "Ana Torres" >/dev/null 2>&1; agent-browser wait 300 >/dev/null 2>&1
  check "$TT final: typing the pastor's name updates the closing line" "$(ev "/Ana Torres/.test(document.getElementById('fp-foot').textContent)&&localStorage.getItem('nury-pastor')==='Ana Torres'")" "true"
  agent-browser screenshot --full $SHOTS/final-$LANG-$T.png >/dev/null 2>&1
  # PRINT: a real PDF of the page, read back as text
  rm -f /tmp/dl/print-$LANG-$T.pdf; agent-browser pdf /tmp/dl/print-$LANG-$T.pdf >/dev/null 2>&1
  PR=$(python3 - "/tmp/dl/print-$LANG-$T.pdf" "$LANG" <<'PY'
import sys,subprocess
t=' '.join(subprocess.run(['pdftotext','-layout',sys.argv[1],'-'],capture_output=True,text=True).stdout.split())
tl=t.lower()
info=subprocess.run(['pdfinfo',sys.argv[1]],capture_output=True,text=True).stdout
pages=int([l for l in info.splitlines() if l.startswith('Pages:')][0].split()[1])
lang=sys.argv[2]
bad=[]
for w in ('Hide the hand-written notes','For judges and reviewers','Observability','Copy all','Download','Save to case file','Audit log','Every stage as approved','Case summary for you'):
    if w.lower() in tl: bad.append('has '+w)
if 'an ai crisis response agent' not in tl: bad.append('no tagline below the logo')
for w in ('Ana Torres','Here is what the family can do tonight' if lang=='en' else 'Información para la familia'):
    if w.lower() not in tl: bad.append('missing '+w)
if lang=='es':
    for w in ('Lo que está pasando','Qué hacer ahora','Apoyo espiritual','Recursos','Preparado por','Esta noche'):
        if w.lower() not in tl: bad.append('missing '+w)
    for w in ('What is happening','What to do next','Prepared by','TONIGHT','GATHER THESE'):
        if w.lower() in tl: bad.append('English label printed: '+w)
if '«' not in t and lang=='en': bad.append('no verse')
if pages>4: bad.append(f'{pages} pages')
print('ok pages=%d'%pages if not bad else 'bad '+'; '.join(bad)+f' pages={pages}')
PY
)
  case "$PR" in ok*) PRS=ok;; *) PRS="$PR";; esac
  check "$TT print: the PDF has the family copy only (no header, footer, buttons), the pastor's name, the right headings, at most 4 pages [$PR]" "$PRS" "ok"
  # EXPORT MENU: one button with five items, no Download and no separate Print button
  agent-browser click "#b-export" >/dev/null 2>&1; agent-browser wait 400 >/dev/null 2>&1
  check "$TT export: one Export menu with the three downloads, a separator and the two print items; no Download or Print button" "$(ev "(()=>{const m=document.getElementById('b-export-menu');return !m.hidden&&[...m.querySelectorAll('[role=menuitem]')].map(b=>b.textContent).join('|')==='Family copy (PDF)|Pastor copy (PDF)|Both in a zip|Print family copy|Print pastor copy'&&!document.getElementById('b-download')&&!document.getElementById('b-print')&&!!m.querySelector('[role=separator]')})()")" "true"
  agent-browser press Escape >/dev/null 2>&1
 done
 ZC="${ES:-$EN}"
 # case zip: real click on the saved-case export
 if [ -n "$ZC" ]; then
  open_case(){ agent-browser open "about:blank" >/dev/null 2>&1; agent-browser open "http://127.0.0.1:$PORT/#/case/$ZC" >/dev/null 2>&1; agent-browser wait 1800 >/dev/null 2>&1; }
  open_case; agent-browser click "#case-export" >/dev/null 2>&1; agent-browser wait 400 >/dev/null 2>&1
  check "$T export: the case Export button opens a menu with the five items" "$(ev "[...document.querySelectorAll('#case-export-menu [role=menuitem]')].length===5&&!document.getElementById('case-export-menu').hidden")" "true"
  agent-browser press Escape >/dev/null 2>&1
  rm -f /tmp/dl/case-$T.zip; curl -s -o /tmp/dl/case-$T.zip "localhost:$PORT/api/case/$ZC/export"
  HDR=$(curl -s -D - -o /dev/null "localhost:$PORT/api/case/$ZC/export" | tr -d '\r' | grep -i content-disposition)
  check "$T zip: the server names it after the case id" "$HDR" "Content-Disposition: attachment; filename=\"$ZC.zip\""
  ZR=$(python3 - "$ZC" "/tmp/dl/case-$T.zip" <<'PY'
import sys,zipfile
cid,path=sys.argv[1:3]
z=zipfile.ZipFile(path); bad=z.testzip(); names=z.namelist()
want={f'{cid}/Family copy.pdf',f'{cid}/Pastor copy.pdf',f'{cid}/records/case.json'}
pdfs_ok=all(z.read(n).startswith(b'%PDF') for n in names if n.endswith('.pdf'))
print('ok' if bad is None and set(names)==want and pdfs_ok and not any(n.endswith('.md') or 'privacy-map' in n for n in names) else f'bad {bad} {names}')
PY
)
  check "$T zip: a valid zip with the two PDFs and records/case.json only (no markdown, no token map)" "$ZR" "ok"
 fi
done; done
ev "try{localStorage.setItem('nury-theme','dark');localStorage.removeItem('nury-pastor')}catch(e){};1" >/dev/null
[ $FAIL = 0 ] && echo "ALL PASS" || { echo "SOME FAILED"; exit 1; }
