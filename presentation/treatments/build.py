"""Render TREATMENTS.md, frames/*.svg and Juan's canvas from data.py.
Usage: python3 presentation/treatments/build.py   (writes the canvas to ~/.aimaestro/agents/<id>/canvas/nury-treatments.html)"""
import os, sys, json, html, datetime
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import data as D

esc = html.escape
def mm(s): return f"{int(s)//60}:{int(s)%60:02d}"
def musts_map(rows):
    out = {}
    for t0, t1, *_rest in [(r[0], r[1]) + tuple(r[2:]) for r in rows]:
        pass
    for r in rows:
        for tag in r[7]: out.setdefault(tag, []).append(f"{mm(r[0])} to {mm(r[1])}")
    return out
def eric_lines(rows):
    return [(mm(r[0]), x.strip()) for r in rows for x in r[3].split('|') if x.strip()]

# ---- frames to files
(HERE / "frames").mkdir(exist_ok=True)
FR = {}
for t in D.TREATMENTS:
    FR[t["id"]] = []
    for i, (t0, svg) in enumerate(t["frames"]()):
        p = HERE / "frames" / f"{t['id']}{i+1}_{t0:02d}s.svg"; p.write_text(svg); FR[t["id"]].append((t0, svg))

PERSONA = ("Pastor Elias, 58. Pastor of a church of about forty in a storefront in Aurora, Colorado. No lawyer on speed dial. Seen only as a silhouette and as hands. "
           "In his hand: a phone. On the table: a cold mug and a worn notebook, under one lamp. His want: to give Maria something true and useful before she hangs up. His clock: it is 2:07 AM. "
           "The family: Maria, her children (8 and 11), and Jose, who was detained last evening. Seen only as silhouettes in a lit window and a few pairs of shoes by a door. All synthetic. No real people, no faces, no agency imagery.")

# ---- TREATMENTS.md
md = ["# Three treatments for the 90-second film (Juan's creative reset)", "",
 "Status: **for Juan to choose.** Written by hack-ninja, 2026-10-06. Nothing existing is thrown away: the app footage, the dictionary card, the tech beat, the end card, the memorial card and Eric's voice are assets in all three. Further polish on them is on hold until Juan picks.", "",
 "## Shared persona (synthetic)", PERSONA, "",
 "## What I researched, and what it changed", "| Source | What it says (verbatim) | How I used it |", "|---|---|---|"]
for s in D.SOURCES: md.append(f"| [{s[2]}]({s[3].split(' and ')[0]}) | {s[1]} | {s[4]} |")
md += ["", "**The honest tension.** The hackathon guide I read says \"Production quality does not affect your judging score,\" and Y Combinator's guide says to say what you do early and keep slides light. A cinematic film is a bet against that advice. The bet is only safe if the real app run stays clear in every frame. Every treatment below keeps it.", "",
 "**Our own limit on agitation.** Problem, agitate, solve works by making the problem felt. We agitate through time and consequence (the clock, the call) and never by showing a family in distress.", "",
 "## My recommendation", "My recommendation: **A, with one plain line borrowed from C** (the entry's second sense, \"An AI crisis response agent\", is already on screen in the first 22 seconds). A gives the most feeling and the clearest arc, and its build is moderate. If time or hack-video's hours run short, **fall back to C**, the safest build and the clearest first ten seconds. I would not pick B for this deadline: it needs hands we do not have, and it withholds the name for 43 seconds against the advice I read. If Juan loves B, we can still borrow its sound idea (no music until the lantern) inside A.", "", "## Hard rules all three keep", "At most 90 s. Eric (ElevenLabs, disclosed) is the narrator, and every line is 8 words or fewer. The memorial is last and is text only, with no synthetic voice. No real people, no real children, no agency imagery or names, no stock photos of detainees. Humanitarian, never political. Technical claims from `documents/TECH_CLAIMS.md`, VERIFIED rows only, and the Jev disclosure caption verbatim. No unlicensed music: the pad, the ticks and the foley are synthesized.", ""]
for t in D.TREATMENTS:
    md += [f"## Treatment {t['id']}: {t['title']}", "", f"**Concept.** {t['concept']}", "", f"**Story spine.** {t['spine']}", "", f"**What makes it different.** {t['difference']}", "",
           "| Time | Picture | Eric (8 words or fewer) | Sound | On-screen type | Asset |", "|---|---|---|---|---|---|"]
    for r in t["rows"]:
        md.append(f"| {mm(r[0])} to {mm(r[1])} | {r[2]} | {r[3].replace('|', ' / ') or '(none)'} | {r[4]} | {r[5]} | {r[6]} |")
    mp = musts_map(t["rows"])
    md += ["", "**Where the six musts land**"] + [f"- {name}: {', '.join(mp[k])}" for k, name in D.MUSTS]
    md += ["", f"**Sound design.** {t['sound']}", "", f"**Type.** {t['type_style']}", "", f"**Feasibility (my estimate, not measured).** {t['feasible']}", "", f"**Risks.** {t['risks']}", "", f"**The live pitch tonight.** {t['pitch']}", "", f"**{t['pick']}**", ""]
md += ["## Deadlines, said plainly", "The prelim pitch is tonight (Oct 7, 21:00 to 23:00 MDT) and the finalist film is due Oct 8, 09:00, only if we make the top 25. So the film has until the morning and the pitch does not. hack-video is the one builder for the film and hack-artisans is full. The hours above are my estimates and assume Eric's new lines are generated once, a few lines at a time. I have not built any of these.", ""]
(HERE.parent / "TREATMENTS.md").write_text("\n".join(md))

# ---- canvas
def tbl(t):
    rows = "".join(f"<tr><td>{mm(r[0])}&ndash;{mm(r[1])}</td><td>{esc(r[2])}</td><td>{esc(r[3].replace('|',' / ')) or '<span class=m>(none)</span>'}</td><td>{esc(r[4])}</td><td>{esc(r[5])}</td><td class=m>{esc(r[6])}</td></tr>" for r in t["rows"])
    return f"<div class=tw><table><tr><th>Time</th><th>Picture</th><th>Eric</th><th>Sound</th><th>On-screen type</th><th>Asset</th></tr>{rows}</table></div>"
def sec(t):
    mp = musts_map(t["rows"]); fr = "".join(f"<figure><div class=fr>{svg}</div></figure>" for _, svg in FR[t["id"]])
    musts = "".join(f"<li><b>{esc(name)}</b>: {esc(', '.join(mp[k]))}</li>" for k, name in D.MUSTS)
    el = "".join(f"<li><span class=m>{tc}</span> {esc(x)}</li>" for tc, x in eric_lines(t["rows"]))
    return (f"<section class=tr id=t{t['id']}><h2>{t['id']}. {esc(t['title'])}</h2><p class=lead>{esc(t['concept'])}</p>"
            f"<p><b>Story spine.</b> {esc(t['spine'])}</p><p><b>Different because:</b> {esc(t['difference'])}</p>"
            f"<h3>Storyboard frames</h3><div class=frs>{fr}</div><p class=m>Flat sketches, not the film. Silhouettes only. Time shown bottom left.</p>"
            f"<h3>Beat sheet, to the second</h3>{tbl(t)}<div class=two><div><h3>Where the six musts land</h3><ul>{musts}</ul></div><div><h3>Eric's lines ({len(eric_lines(t['rows']))})</h3><ul>{el}</ul></div></div>"
            f"<p><b>Sound design.</b> {esc(t['sound'])}</p><p><b>Type.</b> {esc(t['type_style'])}</p><p><b>Feasibility.</b> {esc(t['feasible'])}</p><p><b>Risks.</b> {esc(t['risks'])}</p><p><b>The live pitch tonight.</b> {esc(t['pitch'])}</p>"
            f"<p class=pick>{esc(t['pick'])}</p><button class=ok data-pick='{t['id']}'>Pick {t['id']}</button></section>")
src = "".join(f"<tr><td><a href='{esc(s[3].split(' and ')[0])}'>{esc(s[2])}</a></td><td>{esc(s[1])}</td><td>{esc(s[4])}</td></tr>" for s in D.SOURCES)
cmp = ("<div class=tw><table><tr><th></th><th>A. From night to light</th><th>B. His hands</th><th>C. The clock</th></tr>"
 "<tr><td>Structure</td><td>Light: ink, amber, paper</td><td>Point of view: hands only</td><td>Clarity first, then a clock</td></tr>"
 "<tr><td>\"This is Nury\" lands</td><td>0:15, as the release</td><td>0:43, earned after the turn</td><td>0:03, up front</td></tr>"
 "<tr><td>Turn lands</td><td>0:37</td><td>0:33</td><td>0:32</td></tr>"
 "<tr><td>Sound</td><td>Tick, then a warm pad</td><td>Foley only, no music until the lantern</td><td>A tick bed that slows and stops</td></tr>"
 "<tr><td>Build estimate (hack-video)</td><td>6 to 8 h</td><td>9 to 12 h, highest risk</td><td>4 to 6 h, lowest risk</td></tr>"
 "<tr><td>Strongest at</td><td>Feeling and arc</td><td>Distinctiveness</td><td>Clarity and tension</td></tr></table></div>")
page = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Nury: three treatments</title>
<style>:root{--ink:#0d1015;--s:#131824;--t:#ece7dc;--m:#a0a0a0;--a:#e8a33d;--ln:#263044}*{box-sizing:border-box;overflow-wrap:anywhere}
body{margin:0;background:var(--ink);color:var(--t);font:16px/1.5 system-ui,sans-serif;padding:20px;max-width:980px;margin-inline:auto}
h1,h2{font-family:Georgia,serif;margin:.2em 0}h2{margin-top:1.2em}h3{margin:1em 0 .3em;font-size:15px;color:var(--a);letter-spacing:.02em}
.m{color:var(--m);font-size:13px}.lead{font-size:18px}.box{background:var(--s);border:1px solid var(--ln);border-radius:10px;padding:12px 14px;margin:10px 0}
.tr{border-top:2px solid var(--ln);margin-top:28px;padding-top:6px}.frs{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:10px}
.fr{border-radius:8px;overflow:hidden;border:1px solid var(--ln)}.fr svg{display:block;width:100%;height:auto}figure{margin:0}
.tw{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:13px}th,td{border-bottom:1px solid var(--ln);padding:6px 8px;text-align:left;vertical-align:top}th{color:var(--a)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:700px){.two{grid-template-columns:1fr}}
button{font:inherit;padding:10px 16px;border-radius:8px;border:0;margin:6px 8px 0 0;cursor:pointer}.ok{background:var(--a);color:#0d1015}.no{background:var(--ln);color:var(--t)}
.pick{color:var(--a)}textarea{width:100%;min-height:70px;background:var(--s);color:var(--t);border:1px solid var(--ln);border-radius:8px;padding:8px;font:inherit}a{color:var(--a)}
:focus-visible{outline:2px solid var(--a);outline-offset:2px}</style></head><body>
<h1>Three treatments for the 90-second film</h1><p class="m">Draft for Juan. Written by hack-ninja, @@DATE@@. Source file: presentation/TREATMENTS.md. Nothing existing is thrown away; polish on it is on hold until you pick.</p>
<div class="box"><b>Hard rules all three keep.</b> At most 90 s. Eric is the narrator and every line is 8 words or fewer. The memorial is last, text only, no synthetic voice. No real people, children or agency imagery. Humanitarian, never political. Technical claims from VERIFIED rows only, plus the Jev disclosure caption verbatim. Every sound is synthesized or licensed.</div>
<h2>The persona (synthetic, shared)</h2><div class="box">@@PERSONA@@</div>
<h2>My recommendation</h2><div class="box">My recommendation: A, with one plain line borrowed from C (the entry's second sense, "An AI crisis response agent", is already on screen in the first 22 seconds). A gives the most feeling and the clearest arc, and its build is moderate. If time or hack-video's hours run short, fall back to C, the safest build and the clearest first ten seconds. I would not pick B for this deadline: it needs hands we do not have, and it withholds the name for 43 seconds against the advice I read. If Juan loves B, we can still borrow its sound idea (no music until the lantern) inside A.</div><h2>Side by side</h2>@@CMP@@
<h2>What I researched, and what it changed</h2><div class="tw"><table><tr><th>Source</th><th>Verbatim</th><th>How I used it</th></tr>@@SRC@@</table></div>
<div class="box"><b>The honest tension.</b> The hackathon guide says "Production quality does not affect your judging score," and Y Combinator's guide says to say what you do early. A cinematic film is a bet against that. It is only safe if the real app run stays clear in every frame, and all three keep it. <b>Our own limit:</b> we build tension with time and consequence, never by showing a family in distress.</div>
<div class="box"><b>Deadlines, said plainly.</b> The prelim pitch is tonight (Oct 7, 21:00 to 23:00 MDT). The finalist film is due Oct 8, 09:00, only if we make the top 25. hack-video is the one builder for the film, and hack-artisans is full. The hours are my estimates, not measurements, and I have built none of these.</div>
@@SECS@@
<h2>Your call</h2><textarea id="note" placeholder="What to change, or what to borrow from another treatment (optional)"></textarea>
<p><button class="ok" data-pick="A">Pick A</button><button class="ok" data-pick="B">Pick B</button><button class="ok" data-pick="C">Pick C</button><button class="no" data-pick="MIX">Mix, see my note</button></p><p class="m" id="done"></p>
<script>document.querySelectorAll('button[data-pick]').forEach(b=>b.onclick=()=>{try{maestro.send('submit','treatment-choice',{pick:b.dataset.pick,note:document.getElementById('note').value.slice(0,600)})}catch(e){}document.getElementById('done').textContent='Sent: '+b.dataset.pick;document.querySelectorAll('button[data-pick]').forEach(x=>x.disabled=true)})</script></body></html>'''
page = (page.replace('@@DATE@@', datetime.date.today().isoformat()).replace('@@PERSONA@@', esc(PERSONA)).replace('@@CMP@@', cmp).replace('@@SRC@@', src).replace('@@SECS@@', ''.join(sec(t) for t in D.TREATMENTS)))
AID = "65e84d35-4fab-4ceb-991a-a5c9833f12a9"
out = Path(os.path.expanduser(f"~/.aimaestro/agents/{AID}/canvas/nury-treatments.html")); out.write_text(page)
print("wrote", out, len(page), "and TREATMENTS.md,", sum(len(v) for v in FR.values()), "frames")
