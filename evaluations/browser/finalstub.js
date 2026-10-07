/* Test helper: builds a finished-session state from a REAL saved case (its approved pages), so the final page is tested on real text.
   usage: await window.__finalStub('<case id>')  then  sid='x';show('v-pkg');poll()  */
window.__finalStub=async(caseId,opts)=>{opts=opts||{};
 const d=await (await fetch('/api/case/'+caseId)).json();
 const map=[['01-triage.md','triage','1. Triage'],['02-rights.md','rights','2. Rights brief'],['03-attorney.md','attorney','3. Attorney resources'],['04-checklist.md','checklist','4. Family checklist'],['05-pastoral.md','pastoral','5. Pastoral message']];
 const strip=t=>{let x=t.replace(/^#[^\n]*\n+/,'').replace(/^Status:[^\n]*\n+/,'');x=x.split(/\n---\n\[Previous\]|\n---\n\[Index\]/)[0].replace(/\n---\s*$/,'');
   const m=x.match(/\n\n(Nury (?:is an AI assistant|es un asistente)[^\n]*)\s*$/);const dis=m?m[1]:'Nury is an AI assistant, not a lawyer, pastor, counselor, or therapist. This is general legal information, not legal advice.';
   if(m)x=x.slice(0,m.index);return {final:x.trim(),dis}};
 const edited=(opts.edited||d.meta.edited||[]);
 const stages=map.map(([f,id,title])=>{const s=strip(d.pages[f]||'');if(id==='pastoral'&&opts.addVerse&&!/«.+»/.test(s.final)){const es=d.meta.language==='es';s.final=s.final.replace(/\n+$/,'')+'\n\n'+(es?'«Dios es nuestro refugio y fortaleza, nuestro pronto auxilio en las tribulaciones.»\n— Salmo 46:1, RVR1960. Dominio público':'«God is our refuge and strength, an ever-present help in times of trouble.»\n— Psalm 46:1, BSB. Public Domain')+'\n\nEste versículo habla de refugio.'}return{id,title,status:edited.includes(id)?'edited':'approved',final:s.final,disclaimer:s.dis,metrics:{attempts:1}}});
 window.__stubStages=stages;window.__realApi=window.__realApi||api;
 window.__saveCalls=[];
 window.api=async(p,b)=>{
  if(p.startsWith('/api/session/')&&p.endsWith('/save'))return{id:caseId+'-v9',path:'code/cases/x'};
  if(p.startsWith('/api/session/'))return{id:'x',playbook:{id:'detention',title:d.meta.title},language:d.meta.language,stages,log:[{kind:'scripture',provider:window.__provider||'youversion',verse:'psa46_1',ts:'2026-10-07T00:00:00.000'}],strip:null,halted:null,error:null,sources_list:[],done:true,package:{},map_svg:d.svg,progress:{phase:'idle'}};
  return await window.__realApi(p,b)};
 return stages.length};
