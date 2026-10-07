(()=>{const notes=[...document.querySelectorAll('.hnote')].filter(n=>n.getBoundingClientRect().width>0);
const R=e=>{const r=e.getBoundingClientRect();return{l:r.left,r:r.right,t:r.top,b:r.bottom}};
const bad=[];for(const n of notes){const a=R(n.querySelector('.hn-t'));
 for(const e of document.querySelectorAll('main p,main h1,main h2,main h3,main button,main a,main label,main li,main span.t,.sitefoot p,.sitefoot a,.sitefoot button,.sitefoot nav a')){
  if(n.contains(e)||e.contains(n)||e.closest('.hnote'))continue;const d=e.closest('details');if(d&&!d.open&&!e.closest('summary'))continue;const r=R(e);if(r.r-r.l<2||r.b-r.t<2)continue;
  if(!e.textContent.trim())continue;if(getComputedStyle(e).visibility==='hidden')continue;
  const w=Math.min(a.r,r.r)-Math.max(a.l,r.l),h=Math.min(a.b,r.b)-Math.max(a.t,r.t);if(w>3&&h>3)bad.push((n.textContent||'').slice(0,24)+' x '+(e.textContent||'').trim().slice(0,24))}}
return JSON.stringify({notes:notes.length,bad:bad.slice(0,4)})})()
