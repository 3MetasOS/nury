(()=>{const n=h=>h.replace(/ aria-current="page"/g,'').replace(/ data-noted="1"/g,'').replace(/<span class="hnote"[\s\S]*?<\/span><\/span>/g,'').replace(/(Hide|Show) the hand-written notes/g,'NOTES').replace(/ aria-pressed="(true|false)"/g,'').replace(/ rv-in| rv(?=[" ])/g,'').replace(/ style="[^"]*"/g,'').replace(/ hidden=""/g,'').replace(/<span id="fm-checks">[^<]*<\/span>/g,'').replace(/<div class="fb" id="fm-build"[\s\S]*?<\/div>/g,'').replace(/aria-label="(Day|Night) mode[^"]*"/g,'').replace(/<svg class="i"[^>]*><use href="\/icons\.svg#i-(sun|moon)"><\/use><\/svg>/g,'ICON');
const hs=document.querySelectorAll('header.top'),fs=document.querySelectorAll('footer.sitefoot');
if(hs.length!==1||fs.length!==1)return 'count:'+hs.length+'/'+fs.length;
const s=n(hs[0].outerHTML)+n(fs[0].outerHTML);let x=0;for(let i=0;i<s.length;i++)x=(x*31+s.charCodeAt(i))|0;
return x+':'+Math.round(hs[0].getBoundingClientRect().height)+':'+s.length})()
