(()=>{const T='An AI Crisis Response Agent';const out=[];
const hs=document.querySelector('header.top');if(!hs||!hs.textContent.includes(T))out.push('tagline missing from the header');
for(const e of document.querySelectorAll('body *')){if(e.children.length)continue;if((e.textContent||'').trim()!==T)continue;if(getComputedStyle(e).display==='none')continue;
  const lk=e.closest('.lockup,.brand');if(!lk){out.push('tagline outside a lockup');continue}const mark=lk.querySelector('.lk');const a=e.getBoundingClientRect(),b=mark.getBoundingClientRect();const ic=mark.querySelector('.i').getBoundingClientRect();if(Math.abs(a.left-ic.left)>2)out.push('tagline not left-aligned with the mark');if(e.scrollWidth>e.clientWidth+1||a.right>innerWidth)out.push('tagline clipped');
 if(a.top<b.bottom-1)out.push('tagline not below the logo');if(getComputedStyle(e).display!=='block')out.push('tagline not block');}
return out.length?out.join('; '):'ok'})()
