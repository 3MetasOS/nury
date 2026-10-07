(()=>{const disc="Nury is an AI assistant, not a lawyer, pastor, counselor, or therapist. This is general legal information, not legal advice.";
const mk=(id,t,s)=>({id,title:t,status:s});
window.__phase=window.__phase||"ready";window.__fbCalls=[];window.__realApi=window.__realApi||api;
window.api=async(p,b)=>{
 if(p==="/api/feedback"){window.__fbCalls.push(b);return{ok:true}}
 if(p.startsWith("/api/session/")){const ready=window.__phase==="ready";
  return{id:"x",playbook:{id:"detention",title:"Immigration detention or raid"},
   stages:[mk("triage","1. Triage","approved"),mk("rights","2. Rights brief","approved"),mk("attorney","3. Attorney resources","approved"),mk("checklist","4. Family checklist","approved"),mk("pastoral","5. Pastoral message",ready?"waiting":"working")],
   gate:ready?{id:"pastoral",title:"5. Pastoral message",draft:"Estamos con ustedes esta noche. Si quieren orar juntos, llámenme.",disclaimer:disc,metrics:{attempts:1,self_corrections:0,latency_s:3}}:null,
   log:[],strip:null,halted:null,error:null,sources_list:[],done:false,package:null,map_svg:null,progress:{phase:window.__phase,stage:"pastoral",attempt:1,elapsed_s:4}}}
 return await window.__realApi(p,b)};
})();
