"""Rebuild Juan's review canvas (reading copy) from the repo files.
Usage: python3 presentation/build_canvas.py <thumbs_dir>
<thumbs_dir> holds s0.jpg ... sN.jpg: one 640 px JPEG per default-visible slide, in order.
Writes ~/.aimaestro/agents/<id>/canvas/nury-review.html. The repo files stay the source.
"""
import json, sys, re, base64, datetime, os
from pathlib import Path
HERE = Path(__file__).resolve().parent
D = Path(sys.argv[1]); AID = "65e84d35-4fab-4ceb-991a-a5c9833f12a9"
rd = lambda f: (HERE / f).read_text()
desc, pitch, fin = rd('description.txt'), rd('PITCH_SCRIPT.md'), rd('FINALIST_SCRIPT.md')
name = rd('NAME_ENTRY.md'); img = (HERE.parent / 'branding/IMAGES.md').read_text(); notes_sub = rd('SUBMISSION_NOTES.md')
deck = rd('deck.html')
tags = re.findall(r'<section class="slide[^>]*>', deck)
secs = re.findall(r'<section class="slide[^>]*>(.*?)</section>', deck, re.S)
slides = []
for i, (tg, body) in enumerate(zip(tags, secs)):
    n = re.search(r'<aside class="notes">(.*?)</aside>', body, re.S)
    b2 = re.sub(r'<aside.*?</aside>|<svg.*?</svg>|<img[^>]*>', '', body, flags=re.S)
    t = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', b2)).strip()
    h = re.search(r'<h[12][^>]*>(.*?)</h[12]>', body, re.S)
    title = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', h.group(1))).strip() if h else 'Nury'
    g = re.search(r'data-gated="([\w-]+)"', tg)
    slides.append({"n": i + 1, "title": title, "text": t[:400], "notes": re.sub(r'\s+', ' ', n.group(1)) if n else '',
                   "backup": 'backup' in tg, "gated": g.group(1) if g else None})
vis = [s for s in slides if not s["gated"]]
for k, s in enumerate(vis):
    f = D / f"s{k}.jpg"
    if f.exists(): s["thumb"] = "data:image/jpeg;base64," + base64.b64encode(f.read_bytes()).decode()
gated = sorted({s["gated"] for s in slides if s["gated"]})
data = {"generatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "DECK V2 for Juan's 18:00 read, Oct 7", "wordCount": len(desc.split()),
        "description": desc, "pitch": pitch, "finalist": fin, "name": name, "images": img, "submission": notes_sub, "slides": slides,
        "open": ["Proof numbers (deck slide 9 and the description's scorecard sentence): placeholders until a real final scorecard exists. Cut rule: Oct 7 16:00 MDT.",
                 "Selector screenshot (deck slide 4): a dashed slot, waiting for hack-artisans to ship the selector.",
                 "Hidden until Sensei confirms in writing: " + ", ".join(gated) + ". Press g in the deck to see them.",
                 "Approved by Juan: the name entry (slide 2). Locked, not edited: the Jev line, the brand line, the voice-over lines, the memorial text."],
        "source": "Repo files in presentation/ and branding/ are the source. This page is a reading copy."}
html = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Nury review pack</title>
<style>:root{--ink:#0d1015;--s:#131824;--t:#ece7dc;--m:#a0a0a0;--a:#e8a33d;--ln:#263044}*{box-sizing:border-box;overflow-wrap:anywhere}
body{margin:0;background:var(--ink);color:var(--t);font:16px/1.5 system-ui,sans-serif;padding:20px;max-width:860px;margin-inline:auto}
h1,h2{font-family:Georgia,serif;margin:.2em 0}h2{margin-top:1.6em;border-top:1px solid var(--ln);padding-top:.8em}h3{margin:.2em 0;font-size:16px}
pre{white-space:pre-wrap;background:var(--s);padding:14px;border-radius:10px;font:15px/1.5 system-ui,sans-serif}.m{color:var(--m);font-size:14px}
.sl{background:var(--s);border-radius:10px;padding:10px;margin:10px 0;border:1px solid var(--ln)}.sl img{width:100%;height:auto;border-radius:6px;display:block}
.tag{display:inline-block;font-size:12px;border:1px solid var(--ln);border-radius:99px;padding:1px 8px;margin-right:6px;color:var(--m)}.g{border-color:var(--a);color:var(--a)}
details{margin-top:6px}summary{cursor:pointer;color:var(--m)}button{font:inherit;padding:10px 16px;border-radius:8px;border:0;margin-right:8px;cursor:pointer}
.ok{background:var(--a);color:#0d1015}.no{background:var(--ln);color:var(--t)}textarea{width:100%;min-height:70px;background:var(--s);color:var(--t);border:1px solid var(--ln);border-radius:8px;padding:8px;font:inherit}
:focus-visible{outline:2px solid var(--a);outline-offset:2px}</style></head><body>
<h1>Nury review pack</h1><p class="m" id="meta"></p>
<h2>Still open</h2><ul id="open"></ul>
<h2>250-word description <span class="m" id="wc"></span></h2><pre id="desc"></pre>
<h2>Deck v2</h2><p class="m">Open presentation/deck.html and use arrow keys. n shows notes, g shows hidden slides, b jumps to backup.</p><div id="slides"></div>
<h2>The name entry (approved)</h2><pre id="name"></pre>
<h2>3-minute pitch script</h2><pre id="pitch"></pre>
<h2>90-second finalist script</h2><pre id="fin"></pre>
<h2>Submission notes</h2><pre id="sub"></pre>
<h2>Image credits</h2><pre id="img"></pre>
<h2>Your call</h2><textarea id="note" placeholder="What to change (optional)"></textarea><p><button class="ok" id="a">Approve</button><button class="no" id="c">Request changes</button></p><p class="m" id="src"></p>
<script type="application/json" id="page-data">''' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + '''</script>
<script>const D=JSON.parse(document.getElementById('page-data').textContent);const $=i=>document.getElementById(i);const esc=s=>String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
$('meta').textContent=D.status+' · generated '+D.generatedAt;$('wc').textContent='('+D.wordCount+' words, limit 250)';
$('open').innerHTML=D.open.map(x=>'<li>'+esc(x)+'</li>').join('');$('desc').textContent=D.description;
$('slides').innerHTML=D.slides.map(s=>'<div class="sl"><h3>'+s.n+'. '+esc(s.title)+'</h3><div>'+(s.backup?'<span class="tag">backup</span>':'<span class="tag">talk</span>')+(s.gated?'<span class="tag g">hidden until confirmed: '+esc(s.gated)+'</span>':'')+'</div>'+(s.thumb?'<img alt="Slide '+s.n+'" src="'+s.thumb+'">':'<p class="m">'+esc(s.text)+'</p>')+(s.notes?'<details><summary>Speaker notes</summary><p class="m">'+esc(s.notes)+'</p></details>':'')+'</div>').join('');
$('name').textContent=D.name;$('pitch').textContent=D.pitch;$('fin').textContent=D.finalist;$('sub').textContent=D.submission;$('img').textContent=D.images;$('src').textContent=D.source;
function go(v){maestro.send('submit','review-decision',{decision:v,note:$('note').value.slice(0,500)});$('a').disabled=$('c').disabled=true}
$('a').onclick=()=>go('approve');$('c').onclick=()=>go('changes');</script></body></html>'''
out = Path(os.path.expanduser(f'~/.aimaestro/agents/{AID}/canvas/nury-review.html')); out.write_text(html)
print(out, len(html), len(slides), len(vis))
