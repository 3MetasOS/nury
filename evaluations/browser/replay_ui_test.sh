#!/usr/bin/env bash
# Real-click test of replay mode: the banner on and off, the sample intake in place of typing, the refusal text from the API, the recorded Jev label,
# the replay note, and 'Recorded run' on the final page and its print PDF. PORT = a normal app (keys present, replay off). PORT3 = an app started with NURY_REPLAY=1.
# No model call is made: the refused request never reaches the model, and the pages use stubbed sessions.
PORT=${PORT:-8099}; PORT3=${PORT3:-8096}; HERE="$(cd "$(dirname "$0")" && pwd)"; FAIL=0; SHOTS=${SHOTS:-/tmp/nury_shots}; mkdir -p "$SHOTS" /tmp/dl
ev(){ agent-browser eval "$1" 2>&1 | tail -1; }
check(){ if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1 (got $2, want $3)"; FAIL=1; fi; }
click(){ agent-browser click "$1" >/dev/null 2>&1; agent-browser wait 500 >/dev/null 2>&1; }
open(){ agent-browser open "about:blank" >/dev/null 2>&1; agent-browser open "$1" >/dev/null 2>&1; agent-browser wait 1700 >/dev/null 2>&1; }
scan(){ ev "$(cat $HERE/contrast.js)"; }
BAN="Recorded run. The words were written by the model earlier; the checks run live. Add a Gloo key to run your own."
STUB="$(cat $HERE/finalstub.js | tr '\n' ' ')"
ES=$(curl -s localhost:$PORT/api/cases | python3 -c "
import sys,json,urllib.request
for c in json.load(sys.stdin)['cases']:
    if json.load(urllib.request.urlopen('http://localhost:$PORT/api/case/'+c['id']))['meta']['language']=='es': print(c['id']); break")
for TH in dark light; do for W in 390 1280; do H=800; [ $W = 390 ] && H=844; T="$TH-$W"
 agent-browser set viewport $W $H >/dev/null 2>&1
 open "http://127.0.0.1:$PORT/#/"; ev "try{localStorage.setItem('nury-theme','$TH')}catch(e){};1" >/dev/null; agent-browser eval "location.reload();1" >/dev/null 2>&1; agent-browser wait 1500 >/dev/null 2>&1
 check "$T replay OFF: no banner, typing allowed, the demo button keeps its name" "$(ev "(()=>{const b=document.getElementById('replay-banner');return b.hidden&&b.textContent===''})()")" "true"
 ev "location.hash='#/crisis/detention';1" >/dev/null; agent-browser wait 800 >/dev/null 2>&1; ev "(()=>{const b=[...document.querySelectorAll('[data-begin]')].find(x=>x.getBoundingClientRect().height>0);b.click();return 1})()" >/dev/null; agent-browser wait 700 >/dev/null 2>&1
 check "$T replay OFF: the intake box is editable and says 'Use demo intake'" "$(ev "!document.getElementById('intake').readOnly&&document.getElementById('btn-demo').textContent==='Use demo intake'")" "true"
 open "http://127.0.0.1:$PORT3/#/"; agent-browser eval "location.reload();1" >/dev/null 2>&1; agent-browser wait 1500 >/dev/null 2>&1
 check "$T replay ON: a calm banner with the server's exact sentence is at the top of Home" "$(ev "(()=>{const b=document.getElementById('replay-banner');return !b.hidden&&b.textContent===\"$BAN\"&&b.getBoundingClientRect().top<200})()")" "true"
 check "$T replay ON: the features say so" "$(ev "(async()=>{const f=await (await fetch('/api/features')).json();return f.replay===true&&f.replay_banner===\"$BAN\"})()")" "true"
 check "$T replay ON: contrast scan clean on Home" "$(scan)" '"[]"'
 ev "location.hash='#/crisis/detention';1" >/dev/null; agent-browser wait 800 >/dev/null 2>&1; ev "(()=>{const b=[...document.querySelectorAll('[data-begin]')].find(x=>x.getBoundingClientRect().height>0);b.click();return 1})()" >/dev/null; agent-browser wait 700 >/dev/null 2>&1
 read -r -d '' J <<'JS'
(()=>{const b=document.getElementById('replay-banner'),d=document.getElementById('btn-demo');return !b.hidden&&document.getElementById('intake').readOnly&&d.textContent==='Use the sample intake'&&d.classList.contains('primary')&&d.getBoundingClientRect().height>=44&&d.getBoundingClientRect().bottom<innerHeight&&d.compareDocumentPosition(document.getElementById('intake'))&Node.DOCUMENT_POSITION_FOLLOWING>0})()
JS
 check "$T replay ON: the banner stays on the intake; the box is read-only; the visible path is 'Use the sample intake'" "$(ev "$J")" "true"
 ev "document.getElementById('btn-demo').scrollIntoView({block:'center'});1" >/dev/null; click "#btn-demo"
 check "$T replay ON: one tap fills the sample intake and ticks the demo box" "$(ev "document.getElementById('intake').value.length>80&&document.getElementById('demo').checked")" "true"
 agent-browser screenshot $SHOTS/replay-intake-$T.png >/dev/null 2>&1
 read -r -d '' J <<'JS'
(async()=>{const r=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({playbook:'detention',intake:'My own typed intake that is not the sample.',language:'es'})});const b=await r.json();return JSON.stringify([r.status,b.error,b.replay])})()
JS
 check "$T replay ON: a typed intake is refused by the API with the plain text, before any model call" "$(ev "$J")" '"[400,\"This is a recorded run. Add a Gloo key to run your own.\",true]"'
 # the screens that show a run: banner, replay note, the recorded Jev label
 ev "(()=>{window.__realApi=window.__realApi||api;window.api=async(p,b)=>{if(p.startsWith('/api/session/'))return{id:'x',playbook:{id:'detention',title:'Immigration detention or raid'},replay:true,replay_banner:'x',replay_note:'Your edit is carried forward as you wrote it. The later stages are the recorded ones, so they do not react to it.',stages:[{id:'triage',title:'1. Triage',status:'working'}],gate:null,log:[{ts:'2026-10-07T00:00:00.000+00:00',kind:'jev_recorded',stage:'triage',label:'recorded',scores:[{attempt:1,question:'assumes_facts',probability:0.12,decision:'pass'}]}],strip:null,halted:null,error:null,sources_list:[],done:false,package:null,map_svg:null,progress:{phase:'writing',stage:'triage',attempt:1,elapsed_s:2}};return await window.__realApi(p,b)};sid='x';show('v-pipe');poll();return 1})()" >/dev/null; agent-browser wait 1400 >/dev/null 2>&1
 read -r -d '' J <<'JS'
(()=>{const n=document.getElementById('replay-note'),l=document.getElementById('log').textContent;return !document.getElementById('replay-banner').hidden&&!n.hidden&&/carried forward as you wrote it/.test(n.textContent)&&/RECORDED \(not a live Jev check\).*assumes_facts 0.12 pass/.test(l)&&!/jev_gate/.test(l)})()
JS
 check "$T replay ON: the run page shows the banner, the replay note, and Jev's scores under a 'recorded' label, not as a live check" "$(ev "$J")" "true"
 # the final page in a recorded run
 open "http://127.0.0.1:$PORT3/#/"
 ev "(async()=>{$STUB; await window.__finalStub('$ES',{addVerse:true}); const a=window.api; window.api=async(p,b)=>{const r=await a(p,b); if(p.startsWith('/api/session/')&&!p.endsWith('/save')){r.replay=true;r.replay_banner='x'} return r}; return 1})()" >/dev/null; ev "sid='x';show('v-pkg');poll();1" >/dev/null; agent-browser wait 1500 >/dev/null 2>&1
 check "$T replay ON: the final page keeps its content and adds 'Recorded run' to the key facts and a footer line" "$(ev "(()=>{const k=document.querySelector('.keyfacts').textContent;return /Recorded run/.test(k)&&!!document.querySelector('.fp-rec')&&/Recorded run/.test(document.getElementById('final-body').textContent)&&document.querySelectorAll('#final-body section.fp-sec').length===4&&!document.getElementById('replay-banner').hidden})()")" "true"
 rm -f /tmp/dl/replay-$T.pdf; agent-browser pdf /tmp/dl/replay-$T.pdf >/dev/null 2>&1
 PR=$(python3 - "/tmp/dl/replay-$T.pdf" <<'PY'
import sys,subprocess
t=' '.join(subprocess.run(['pdftotext','-layout',sys.argv[1],'-'],capture_output=True,text=True).stdout.split()).lower()
print('ok' if ('recorded run' in t or 'ejecución grabada' in t) else 'bad: no recorded-run line in the printout')
PY
)
 check "$T replay ON: the print view says it was a recorded run" "$PR" "ok"
 agent-browser screenshot $SHOTS/replay-final-$T.png >/dev/null 2>&1
done; done
ev "try{localStorage.setItem('nury-theme','dark')}catch(e){};1" >/dev/null
[ $FAIL = 0 ] && echo "ALL PASS" || { echo "SOME FAILED"; exit 1; }
