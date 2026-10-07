#!/usr/bin/env bash
# Real-click test of the diagrams (drawn from data) and the document pages (Standards, What did not work, Economics, The pattern). No model call.
PORT=${PORT:-8099}; HERE="$(cd "$(dirname "$0")" && pwd)"; FAIL=0; SHOTS=${SHOTS:-/tmp/nury_shots}; mkdir -p "$SHOTS"
ev(){ agent-browser eval "$1" 2>&1 | tail -1; }
check(){ if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1 (got $2, want $3)"; FAIL=1; fi; }
open(){ agent-browser open "$1" >/dev/null 2>&1; agent-browser wait 1700 >/dev/null 2>&1; }
scan(){ ev "$(cat $HERE/contrast.js)"; }
SIG="$(cat $HERE/shellsig.js)"
CASE=$(curl -s localhost:$PORT/api/cases | python3 -c "import sys,json;print(json.load(sys.stdin)['cases'][0]['id'])")
for TH in dark light; do for W in 390 1280; do H=800; [ $W = 390 ] && H=844; T="$TH-$W"
 agent-browser set viewport $W $H >/dev/null 2>&1
 open "http://127.0.0.1:$PORT/#/"; ev "try{localStorage.setItem('nury-theme','$TH')}catch(e){};1" >/dev/null; agent-browser eval "location.reload();1" >/dev/null 2>&1; agent-browser wait 1500 >/dev/null 2>&1
 REF=$(ev "$SIG")
 for PB in detention hospital; do
  open "http://127.0.0.1:$PORT/#/crisis/$PB"
  read -r -d '' J <<'JS'
(async()=>{const pbs=(await (await fetch('/api/playbooks')).json()).playbooks;const p=pbs.find(x=>x.id===location.hash.split('/')[2]);const svg=document.querySelector('#crisis-page figure.dfig svg.dgm');if(!svg||!p)return 'missing';
const nodes=svg.querySelectorAll('.dg-node.on').length,gates=svg.querySelectorAll('.dg-gate').length,lab=svg.getAttribute('aria-label');
const titles=p.stages.every(s=>lab.includes(s.title.replace(/^\d+\.\s*/,'')));
const sc=svg.getBoundingClientRect().width/svg.viewBox.baseVal.width;const fs=parseFloat(getComputedStyle(svg.querySelector('.dg-desc')).fontSize)*sc;
return JSON.stringify([nodes===p.stages.length,gates===p.stages.length,titles,svg.getAttribute('role')==='img',fs>=8.5,document.documentElement.scrollWidth<=innerWidth])})()
JS
  check "$T crisis($PB): the path diagram is drawn from the playbook's stages: one node and one gate per stage, a text alternative, readable size, no sideways scroll" "$(ev "$J")" '"[true,true,true,true,true,true]"'
  check "$T crisis($PB): contrast scan clean" "$(scan)" '"[]"'
 done
 agent-browser screenshot --full $SHOTS/diagram-crisis-$T.png >/dev/null 2>&1
 open "http://127.0.0.1:$PORT/#/case/$CASE"
 read -r -d '' J <<'JS'
(()=>{const f=document.getElementById('case-strip');const svg=f&&f.querySelector('svg.strip');if(!svg||f.classList.contains('hidden'))return 'missing';const n=svg.querySelectorAll('.dg-node').length;const states=[...svg.querySelectorAll('.dg-node')].map(c=>c.getAttribute('class').split(' ')[1]);
return JSON.stringify([n===5,states.every(s=>['approved','edited','stopped','pending'].includes(s)),/Stages of this case/.test(svg.getAttribute('aria-label')),document.documentElement.scrollWidth<=innerWidth])})()
JS
 check "$T case: the saved case shows its stages as a progress strip with a text alternative" "$(ev "$J")" '"[true,true,true,true]"'
 open "http://127.0.0.1:$PORT/network"
 read -r -d '' J <<'JS'
(()=>{const svg=document.querySelector('main svg.adg');if(!svg)return 'missing';const r=svg.getBoundingClientRect();const t=[...svg.querySelectorAll('.bh')].every(x=>x.getBoundingClientRect().right<=r.right+1);return JSON.stringify([/How a contact becomes part of your network/.test(svg.getAttribute('aria-label')),svg.querySelectorAll('.bx').length===4,t,document.documentElement.scrollWidth<=innerWidth])})()
JS
 check "$T network: how a contact becomes yours is drawn, the hand aside is not clipped" "$(ev "$J")" '"[true,true,true,true]"'
 open "http://127.0.0.1:$PORT/how-it-was-built"
 check "$T how: the architecture and the learning loop are drawn, each with a text alternative" "$(ev "(()=>{const f=[...document.querySelectorAll('svg.adg')];return f.length===2&&f.every(s=>s.getAttribute('role')==='img'&&s.getAttribute('aria-label').length>80)&&/Claude through Gloo/.test(f[0].getAttribute('aria-label'))&&/Nothing changes without a person approving it/.test(f[1].getAttribute('aria-label'))})()")" "true"
 open "http://127.0.0.1:$PORT/standards"
 check "$T standards: the six case management functions are drawn and the table says the same in words" "$(ev "document.querySelectorAll('svg.fdiag .fr').length===6&&document.querySelectorAll('.tw table').length>=3&&/informed by/i.test(document.body.textContent)&&!/is compliant with|are certified|has been certified|meets the standards/i.test(document.body.textContent)")" "true"
 check "$T standards: no sideways scroll, contrast clean" "$(ev "document.documentElement.scrollWidth<=innerWidth")|$(scan)" 'true|"[]"'
 open "http://127.0.0.1:$PORT/what-did-not-work"
 check "$T what-did-not-work: 15 items, each with its Not known line" "$(ev "document.querySelectorAll('#doc li strong').length>=60&&[...document.querySelectorAll('#doc h3')].length>=15&&(document.getElementById('doc').textContent.match(/Not known\./g)||[]).length>=15")" "true"
 for P in standards what-did-not-work economics pattern; do open "http://127.0.0.1:$PORT/$P"; check "$T $P: the same header and footer HTML as Home, no sideways scroll" "$(ev "$SIG")|$(ev "document.documentElement.scrollWidth<=innerWidth")" "$REF|true"; done
 open "http://127.0.0.1:$PORT/economics"; check "$T economics: contrast clean" "$(scan)" '"[]"'
 open "http://127.0.0.1:$PORT/pattern"; check "$T pattern: contrast clean" "$(scan)" '"[]"'
 agent-browser screenshot --full $SHOTS/standards-$T.png >/dev/null 2>&1
done; done
ev "try{localStorage.setItem('nury-theme','dark')}catch(e){};1" >/dev/null
[ $FAIL = 0 ] && echo "ALL PASS" || { echo "SOME FAILED"; exit 1; }
