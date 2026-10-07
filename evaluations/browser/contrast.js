(()=>{function parse(c){const m=c.match(/rgba?\(([^)]+)\)/);if(!m)return null;const p=m[1].split(",").map(x=>parseFloat(x));return{r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1}}
function lum(c){const f=v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)};return 0.2126*f(c.r)+0.7152*f(c.g)+0.0722*f(c.b)}
function blend(top,bot){const a=top.a;return{r:top.r*a+bot.r*(1-a),g:top.g*a+bot.g*(1-a),b:top.b*a+bot.b*(1-a),a:1}}
function bgOf(el){const chain=[];for(let e=el;e;e=e.parentElement){const c=parse(getComputedStyle(e).backgroundColor);if(c&&c.a>0)chain.push(c);if(c&&c.a===1)break}
 let base={r:255,g:255,b:255,a:1};chain.reverse().forEach(c=>{base=blend(c,base)});return base}
const bad=[];const seen=new Set();
document.querySelectorAll("body *").forEach(el=>{
 if(!el.offsetParent&&getComputedStyle(el).position!=="fixed")return;
 const own=[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim().length>1);if(!own)return;
 const cs=getComputedStyle(el);if(cs.visibility==="hidden"||el.closest("[disabled]")||el.disabled)return;
 const fg=parse(cs.color);if(!fg)return;const bg=bgOf(el);const f=blend(fg,bg);
 const l1=lum(f),l2=lum(bg);const ratio=(Math.max(l1,l2)+0.05)/(Math.min(l1,l2)+0.05);
 const size=parseFloat(cs.fontSize),bold=parseInt(cs.fontWeight)>=700;const large=size>=24||(size>=18.66&&bold);
 const need=large?3:4.5;if(ratio<need){const k=el.tagName+"."+el.className+"|"+el.textContent.trim().slice(0,28);if(!seen.has(k)){seen.add(k);bad.push([k,+ratio.toFixed(2),need])}}});
return JSON.stringify(bad.slice(0,12))})()
