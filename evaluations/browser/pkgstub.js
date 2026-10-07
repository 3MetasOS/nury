(()=>{const long="- Tiene derecho a guardar silencio. (ACLU Know Your Rights)\n- No firme ningún documento sin hablar primero con un abogado. (ACLU Know Your Rights)";
const tri="SITUATION: Jose was detained by immigration officers in Aurora yesterday evening.\nPEOPLE: Jose (detained); Maria (wife); two children, 8 and 11\nLOCATION: Aurora\nFAMILY LANGUAGE: es\nURGENCY: High\nMISSING FACTS:\n1. Which facility?\n2. Any papers signed?\n3. Does the family have an attorney?";
const disc="Nury is an AI assistant, not a lawyer, pastor, counselor, or therapist. This is general legal information, not legal advice.";
const big=Array(6).fill(long).join("\n");
const st=(id,t)=>({id,title:t,status:"approved",final:id==="triage"?tri:big,disclaimer:disc,metrics:{attempts:1}});
window.__realApi=window.__realApi||api;
window.__saveCalls=[];
window.api=async(p,b)=>{
 if(p.startsWith("/api/session/")&&p.endsWith("/save")){window.__saveCalls.push(p);return window.__saveReply||{id:"detention-20261007-120000-abcd",path:"code/cases/detention-20261007-120000-abcd"}}
 if(p.startsWith("/api/session/")){return{id:"x",playbook:{id:"detention",title:"Immigration detention or raid"},stages:[st("triage","1. Triage"),st("rights","2. Rights brief"),st("attorney","3. Attorney resources"),st("checklist","4. Family checklist"),st("pastoral","5. Pastoral message")],log:[],strip:null,halted:null,error:null,sources_list:[],done:true,package:{},map_svg:null,progress:{phase:"idle"}}}
 return await window.__realApi(p,b)};
})();
