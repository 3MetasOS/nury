#!/usr/bin/env python3
"""Build the Nury hub: one self-contained HTML file with a side menu that links
every artifact (architecture, concepts, evidence, presentation, video, canvases).

Run:  python3 documents/hub/build.py
Out:  documents/hub/index.html   (open it in a browser, or copy it to a canvas folder)

Reading copy only. The repo files stay the source. Re-run to refresh.
"""
import glob
import json
import os
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "index.html"
CANVAS_ROOT = Path.home() / ".aimaestro" / "agents"

PAGE_CSS = """
:root{--bg:#0f1115;--card:#171a21;--ink:#e9e6df;--mute:#9a978f;--amber:#e8a33d;--line:#262a33}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 system-ui,-apple-system,sans-serif;padding:22px 20px 60px;max-width:880px;margin:auto}
h1,h2,h3{font-family:Georgia,'Fraunces',serif;line-height:1.25}
h1{font-size:28px;margin:.2em 0 .6em}h2{font-size:21px;margin:1.6em 0 .5em;color:var(--amber)}h3{font-size:17px;margin:1.3em 0 .4em}
a{color:var(--amber)}code{background:#0c0e12;border:1px solid var(--line);border-radius:5px;padding:1px 5px;font-size:.88em}
pre{background:#0c0e12;border:1px solid var(--line);border-radius:8px;padding:12px;overflow:auto}pre code{border:0;padding:0}
table{border-collapse:collapse;width:100%;display:block;overflow-x:auto;font-size:14px}th,td{border:1px solid var(--line);padding:6px 9px;text-align:left;vertical-align:top}th{background:var(--card)}
blockquote{border-left:3px solid var(--amber);margin:1em 0;padding:.2em 1em;color:var(--mute)}
hr{border:0;border-top:1px solid var(--line);margin:2em 0}img,svg{max-width:100%}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:10px 0}
.pill{display:inline-block;font-size:12px;border:1px solid var(--line);border-radius:99px;padding:1px 9px;color:var(--mute);margin-right:6px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px}
dl dt{color:var(--amber);font-weight:600;margin-top:.8em}dl dd{margin:.1em 0 0 0;color:var(--ink)}
"""


def wrap(title, body):
    return ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{title}</title><style>{PAGE_CSS}</style></head><body>{body}</body></html>")


def md_page(path, title=None):
    p = ROOT / path
    if not p.exists():
        return None
    text = p.read_text(encoding="utf-8", errors="replace")
    html = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists", "toc"])
    return wrap(title or p.name, f"<p class='pill'>{path}</p>{html}")


def txt_page(path, title=None):
    p = ROOT / path
    if not p.exists():
        return None
    text = p.read_text(encoding="utf-8", errors="replace")
    esc = text.replace("&", "&amp;").replace("<", "&lt;")
    return wrap(title or p.name, f"<p class='pill'>{path}</p><pre style='white-space:pre-wrap'>{esc}</pre>")


def html_file(path):
    p = Path(path) if os.path.isabs(str(path)) else ROOT / path
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8", errors="replace")


def brand_page():
    b = ROOT / "branding"
    def svg(n):
        f = b / n
        return f.read_text(encoding="utf-8") if f.exists() else ""
    if not (b / "logo-mark.svg").exists():
        return None
    body = ("<h1>Nury logo</h1><p>Outline lantern. Chosen by Juan. Pure SVG.</p>"
            "<div class='grid'>"
            f"<div class='card' style='background:#0d1015'><b>Lockup on ink</b><br><div style='max-width:360px'>{svg('logo-lockup.svg')}</div></div>"
            f"<div class='card' style='background:#f6f1e7;color:#111'><b>Lockup on paper</b><br><div style='max-width:360px'>{svg('logo-lockup-light.svg')}</div></div></div>"
            "<h2>Mark</h2><div class='grid'>"
            f"<div class='card'><div style='width:96px'>{svg('logo-mark.svg')}</div><p class='pill'>logo-mark.svg</p></div>"
            f"<div class='card'><div style='width:32px'>{svg('logo-mark-small.svg')}</div><p class='pill'>logo-mark-small.svg, for 24 px and under</p></div>"
            f"<div class='card'><div style='width:32px'>{svg('favicon.svg')}</div><p class='pill'>favicon.svg</p></div></div>")
    return wrap("Logo", body)


def canvas_file(name):
    hits = sorted(glob.glob(str(CANVAS_ROOT / "*" / "canvas" / name)))
    return Path(hits[0]).read_text(encoding="utf-8", errors="replace") if hits else None


START_HERE = wrap("Start here", """
<h1>Nury</h1>
<p><b>The crisis-response agent for solo pastors.</b> Nury helps a pastor who takes a panicked call from a family in crisis. The pastor types what the family said. Nury works through stages, one at a time. After every stage the pastor decides: <b>Approve, Edit or Stop</b>. Nothing reaches the family except through the pastor.</p>
<div class='card'><b>Who it is for.</b> A solo pastor with no staff and no lawyer on the line, on a phone, often at 2 AM. Flagship demo: a family member detained in an immigration raid. A second playbook runs hospital emergencies.</div>
<h2>What Nury will never do</h2>
<ul><li>Give legal or medical advice, or predict how a case or an illness will turn out.</li><li>Claim to be a pastor, a lawyer, a counselor or a clinician.</li><li>Send anything to the family. There is no send path.</li><li>Search the open web while it runs, or use a source nobody vetted.</li><li>Send names, phones, addresses or ID numbers to a language model.</li></ul>
<h2>The pastor's journey</h2>
<ol><li><b>Pick the crisis</b> on the selector (detention and hospital are live; sudden death and house fire are coming soon).</li><li><b>Intake.</b> Type the call. Confirm which names to protect.</li><li><b>Stages with gates.</b> Triage, rights or information brief, attorney or hospital resources, family checklist, pastoral message. Each ends with Approve, Edit or Stop.</li><li><b>Package.</b> Copy or download. The pastor gives it to the family.</li><li><b>Case file.</b> Save a local folder of linked pages and a next-steps map.</li><li><b>Something changed.</b> Reopen the case, say what happened, and draft again as version 2.</li></ol>
<h2>Concepts, in plain words</h2>
<dl>
<dt>Playbook</dt><dd>One crisis as a folder: stages, prompts, vetted sources, outcomes. A new crisis is a new folder; the engine does not change.</dd>
<dt>Engine</dt><dd>Runs the stages, chains approved text forward, runs the correction loop, runs the gates, writes the audit log. It knows nothing about any one crisis.</dd>
<dt>Safety floor</dt><dd>The rules no playbook can remove: no advice, no predictions, no identity claims, vetted links and phones only, a disclaimer on every output.</dd>
<dt>Correction loop</dt><dd>Each draft is checked. If it fails, Nury rewrites it, up to 3 attempts in all, then hands over. The pastor never sees an unsafe draft.</dd>
<dt>Gate</dt><dd>The Approve / Edit / Stop step after every stage. Edits flow into later stages.</dd>
<dt>Skills</dt><dd>Small versioned instruction modules a stage includes by name (voice, grounding). They can add rules, never remove the floor.</dd>
<dt>Privacy layer</dt><dd>Replaces names, phones, emails, addresses, birth dates and IDs with tokens before anything reaches Gloo, and restores them on the pastor's computer.</dd>
<dt>Church network</dt><dd>The pastor's own list of contacts they have worked with. Listed first, labeled as the church's own, never endorsed by Nury.</dd>
<dt>Official list</dt><dd>The U.S. Department of Justice list of legal service providers, approved by Juan. Listed does not mean recommended.</dd>
<dt>Case file</dt><dd>A local folder of linked pages, a log of every gate, and a next-steps map. Approved text only.</dd>
<dt>Evals</dt><dd>Four layers: deterministic checks, Jev yes/no and score judges, a cross-vendor red-team panel, and a human review by Juan.</dd>
</dl>
<h2>How the pieces run</h2>
<p><b>At run time:</b> Gloo (guarded Responses endpoint, Claude Sonnet 4.6) writes drafts. Nury's own code checks them. <b>At test time:</b> Jev and the red-team panel judge the runs. Both keys sit in a local <code>.env</code> that git ignores.</p>
<h2>The crew</h2>
<div class='grid'>
<div class='card'><b>hack-sensei</b><br>Coordinator. Owns CLAUDE.md and BUILD_LOG.</div>
<div class='card'><b>hack-jedi</b><br>Architecture: engine, playbooks, privacy, network, case file.</div>
<div class='card'><b>hack-artisans</b><br>App, eval harness, scorecards.</div>
<div class='card'><b>hack-ninja</b><br>Description, deck, scripts, research, logo.</div>
<div class='card'><b>hack-video</b><br>The 90-second demo video.</div>
</div>
<h2>Deadlines (MDT)</h2>
<p>Oct 7 21:00 submission (hard stop). Prelim pitch 21:00 to 23:00. Top 25 at midnight. Oct 8 09:00 finalist video. Finals in person.</p>
""")


# (group, label, kind, source)  kind: md | txt | html_repo | canvas | raw
MENU = [
    ("Overview", "Start here", "raw", START_HERE),
    ("Overview", "README", "md", "README.md"),
    ("Overview", "Product (locked)", "md", "documents/prework/PRODUCT.md"),
    ("Overview", "Judging notes", "md", "documents/prework/JUDGING.md"),
    ("Overview", "Features: built vs not built", "md", "documents/FEATURES.md"),
    ("Overview", "Technical claims (verified)", "md", "documents/TECH_CLAIMS.md"),
    ("Overview", "Who Gloo's customers are", "md", "documents/GLOO_CUSTOMERS.md"),
    ("Architecture", "Architecture decisions", "md", "documents/ARCHITECTURE.md"),
    ("Architecture", "Diagrams (10 tabs)", "html_repo", "documents/architecture/diagrams.html"),
    ("Architecture", "Diagrams notes", "md", "documents/architecture/README.md"),
    ("Architecture", "Case file sample", "canvas", "case-file-sample.html"),
    ("Build", "Build log", "md", "BUILD_LOG.md"),
    ("Build", "Crew rules (CLAUDE.md)", "md", "CLAUDE.md"),
    ("Build", "Core interface", "md", "code/INTERFACE.md"),
    ("Build", "Prompt notes (v1 vs shipped)", "md", "code/playbooks/detention/PROMPT_NOTES.md"),
    ("Build", "Prompt notes (canvas)", "canvas", "prompt-notes.html"),
    ("Evidence", "Detention scorecard (interim)", "md", "evaluations/results/scorecard.md"),
    ("Evidence", "Hospital scorecard (interim)", "md", "evaluations/results/hospital/scorecard.md"),
    ("Evidence", "Failure log", "md", "evaluations/FAILURE_LOG.md"),
    ("Evidence", "Judge validation", "md", "evaluations/validation/JUDGE_VALIDATION.md"),
    ("Evidence", "Panel validation", "md", "evaluations/validation/PANEL_VALIDATION.md"),
    ("Evidence", "Eval design", "md", "documents/prework/EVAL_DESIGN.md"),
    ("Evidence", "Eval README", "md", "evaluations/README.md"),
    ("Evidence", "Live cost log", "md", "evaluations/LIVE_COST_LOG.md"),
    ("Evidence", "Live checks plan", "md", "evaluations/LIVE_CHECKS_OWED.md"),
    ("Sources", "Hospital sources (canvas)", "canvas", "hospital-sources.html"),
    ("Sources", "Official list (canvas)", "canvas", "official-list-review.html"),
    ("Presentation", "250-word description", "txt", "presentation/description.txt"),
    ("Presentation", "Deck", "html_repo", "presentation/deck.html"),
    ("Presentation", "Pitch script (3 min)", "md", "presentation/PITCH_SCRIPT.md"),
    ("Presentation", "Finalist script (90 s)", "md", "presentation/FINALIST_SCRIPT.md"),
    ("Presentation", "Shared demo", "md", "presentation/SHARED_DEMO.md"),
    ("Presentation", "Creative brief (v3)", "md", "presentation/CREATIVE_BRIEF.md"),
    ("Presentation", "The name entry (Nury)", "md", "presentation/NAME_ENTRY.md"),
    ("Presentation", "Memorial (draft)", "md", "presentation/MEMORIAL.md"),
    ("Presentation", "Tech story", "md", "presentation/TECH_STORY.md"),
    ("Presentation", "Review (canvas)", "canvas", "nury-review.html"),
    ("Video", "Storyboard", "md", "video/STORYBOARD.md"),
    ("Video", "Storyboard (canvas)", "canvas", "storyboard.html"),
    ("Video", "Remotion vs ffmpeg", "canvas", "remotion-vs-ffmpeg.html"),
    ("Brand", "Brand kit", "md", "branding/BRAND.md"),
    ("Brand", "Logo and lockups", "brand", None),
    ("Project", "Status (canvas)", "canvas", "status.html"),
]


def build():
    pages = []
    missing = []
    for group, label, kind, src in MENU:
        if kind == "raw":
            html = src
        elif kind == "brand":
            html = brand_page()
        elif kind == "md":
            html = md_page(src, label)
        elif kind == "txt":
            html = txt_page(src, label)
        elif kind == "html_repo":
            html = html_file(src)
        elif kind == "canvas":
            html = canvas_file(src)
            if html:
                html = ("<div style='position:sticky;top:0;z-index:9;background:#171a21;color:#9a978f;font:13px system-ui;"
                        "padding:6px 12px;border-bottom:1px solid #262a33'>Reading copy. Buttons work in the agent's Canvas tab.</div>") + html
        else:
            html = None
        if not html:
            missing.append(f"{group} / {label} ({src if kind != 'raw' else ''})")
            continue
        pages.append({"id": f"p{len(pages)}", "group": group, "label": label, "html": html})
    data = json.dumps(pages).replace("</", "<\\/")
    logo = (ROOT / "branding" / "logo-mark.svg").read_text(encoding="utf-8") if (ROOT / "branding" / "logo-mark.svg").exists() else ""
    logo = logo.replace('width="64" height="64"', 'width="34" height="34"', 1)
    shell = SHELL.replace("__DATA__", data).replace("__LOGO__", logo)
    OUT.write_text(shell, encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB), {len(pages)} pages")
    if missing:
        print("skipped (not found):")
        for m in missing:
            print("  -", m)


SHELL = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nury hub</title>
<style>
:root{--bg:#0f1115;--card:#171a21;--ink:#e9e6df;--mute:#9a978f;--amber:#e8a33d;--line:#262a33}
*{box-sizing:border-box}html,body{height:100%;margin:0}
body{background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,sans-serif;display:flex}
nav{width:290px;flex:none;background:var(--card);border-right:1px solid var(--line);display:flex;flex-direction:column;height:100%}
.brand{padding:16px 16px 10px;border-bottom:1px solid var(--line)}
.brand .mark{display:flex;gap:10px;align-items:center}
.brand b{font:600 24px Georgia,'Fraunces',serif;color:var(--ink);letter-spacing:.01em}
.brand small{display:block;color:var(--mute);font-size:12px;margin-top:4px}
.search{padding:10px 12px;border-bottom:1px solid var(--line)}
.search input{width:100%;background:#0c0e12;color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:9px 10px;font:inherit}
.menu{overflow:auto;flex:1;padding:6px 0 20px}
.grp{padding:14px 16px 4px;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--amber)}
.menu a{display:block;padding:9px 16px;color:var(--ink);text-decoration:none;border-left:3px solid transparent;min-height:40px}
.menu a:hover{background:#1d212a}.menu a.on{background:#1d212a;border-left-color:var(--amber);color:#fff}
main{flex:1;min-width:0;height:100%;display:flex;flex-direction:column}
.bar{display:none;align-items:center;gap:10px;padding:8px 12px;border-bottom:1px solid var(--line);background:var(--card)}
.bar button{background:var(--amber);color:#1a1405;border:0;border-radius:8px;padding:9px 13px;font-weight:600;min-height:44px}
.bar span{font:600 16px Georgia,serif}
iframe{flex:1;width:100%;border:0;background:var(--bg)}
a:focus-visible,button:focus-visible,input:focus-visible{outline:2px solid var(--amber);outline-offset:2px}
@media(max-width:820px){
 nav{position:fixed;inset:0 20% 0 0;z-index:20;transform:translateX(-100%);transition:transform .2s}
 nav.open{transform:none;box-shadow:0 0 0 100vmax rgba(0,0,0,.55)}
 .bar{display:flex}
}
@media(prefers-reduced-motion:reduce){nav{transition:none}}
</style></head><body>
<nav id="nav" aria-label="Nury hub menu">
 <div class="brand"><div class="mark">
  __LOGO__
  <div><b>Nury</b><small>the crisis-response agent for solo pastors</small></div></div></div>
 <div class="search"><input id="q" type="search" placeholder="Search the menu" aria-label="Search the menu"></div>
 <div class="menu" id="menu"></div>
</nav>
<main>
 <div class="bar"><button id="open" aria-label="Open menu">Menu</button><span id="cur">Nury</span></div>
 <iframe id="view" title="Content"></iframe>
</main>
<script type="application/json" id="data">__DATA__</script>
<script>
const PAGES = JSON.parse(document.getElementById('data').textContent);
const menu = document.getElementById('menu'), view = document.getElementById('view'), nav = document.getElementById('nav');
const cur = document.getElementById('cur');
function render(filter){
  const f=(filter||'').toLowerCase(); menu.innerHTML=''; let g='';
  PAGES.forEach(p=>{
    if(f && !(p.label+' '+p.group).toLowerCase().includes(f)) return;
    if(p.group!==g){g=p.group; const h=document.createElement('div'); h.className='grp'; h.textContent=g; menu.appendChild(h);}
    const a=document.createElement('a'); a.href='#'+p.id; a.textContent=p.label; a.dataset.id=p.id; menu.appendChild(a);
  });
  mark();
}
function mark(){ const id=(location.hash||'#p0').slice(1); menu.querySelectorAll('a').forEach(a=>a.classList.toggle('on',a.dataset.id===id)); }
function show(){
  const id=(location.hash||'#p0').slice(1); const p=PAGES.find(x=>x.id===id)||PAGES[0];
  view.srcdoc=p.html; cur.textContent=p.label; document.title=p.label+' - Nury hub'; mark(); nav.classList.remove('open');
}
document.getElementById('q').addEventListener('input',e=>render(e.target.value));
document.getElementById('open').addEventListener('click',()=>nav.classList.toggle('open'));
window.addEventListener('hashchange',show);
render(''); show();
</script></body></html>
"""

if __name__ == "__main__":
    build()
