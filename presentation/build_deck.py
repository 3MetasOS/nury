"""Build deck.html from deck_template.html (logo SVG filled in). Run from presentation/."""
mark=open('../branding/logo-mark.svg').read().replace(' width="64" height="64"','').replace('#e8a33d','#b8680f')
small=open('../branding/logo-mark-small.svg').read().replace(' width="64" height="64"','').replace('#e8a33d','#b8680f')
s=open('deck_template.html',encoding='utf-8').read()
lit=mark.replace('<path stroke="none"','<path class="flame" stroke="none"').replace('<path fill="none" stroke-width="4.2" stroke-linejoin','<path class="body" fill="none" stroke-width="4.2" stroke-linejoin').replace('<path fill="none" stroke-width="4.2" stroke-linecap','<path class="body" fill="none" stroke-width="4.2" stroke-linecap').replace('<circle cx="32" cy="12.2"','<circle class="body" cx="32" cy="12.2"')
open('deck.html','w',encoding='utf-8').write(s.replace('{{MARKLIT}}',lit).replace('{{MARKDEEP}}',mark).replace('{{MARK}}',mark).replace('{{SMALL}}',small))
