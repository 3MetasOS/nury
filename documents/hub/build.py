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
:root{--bg:#f6f1e7;--card:#ece3d0;--ink:#0d1015;--mute:#5b564c;--amber:#b8680f;--amber-text:#8a4b04;--line:#d8cdb6;--serif:Fraunces,Georgia,serif;--mono:ui-monospace,SFMono-Regular,Menlo,monospace}
*{box-sizing:border-box}
body{margin:0 auto;background:var(--bg);color:var(--ink);font:17px/1.65 Inter,system-ui,-apple-system,sans-serif;padding:40px 28px 80px;max-width:820px}
h1,h2,h3{font-family:var(--serif);line-height:1.12;text-wrap:balance;letter-spacing:-.01em}
h1{font-size:clamp(34px,5vw,52px);margin:.1em 0 .5em;font-weight:600}
h2{font-size:clamp(22px,2.8vw,30px);margin:2em 0 .5em;color:var(--ink);font-weight:600;padding-top:.6em;border-top:1px solid var(--line)}
h3{font-size:19px;margin:1.5em 0 .4em;color:var(--amber-text);font-weight:600}
p,li{max-width:68ch}
a{color:var(--amber-text);text-underline-offset:3px}
code{background:var(--card);border:1px solid var(--line);border-radius:5px;padding:1px 5px;font:.86em var(--mono)}
pre{background:#0d1015;color:#ece7dc;border-radius:10px;padding:14px;overflow:auto}pre code{background:none;border:0;padding:0;color:inherit}
table{border-collapse:collapse;width:100%;display:block;overflow-x:auto;font-size:14.5px}th,td{border-bottom:1px solid var(--line);padding:8px 12px 8px 0;text-align:left;vertical-align:top}th{font:600 12px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--amber-text)}
blockquote{border-left:3px solid var(--amber);margin:1.2em 0;padding:.2em 1.1em;color:var(--mute)}
hr{border:0;border-top:1px solid var(--line);margin:2em 0}img,svg{max-width:100%}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:10px 0}
.pill{display:inline-block;font:600 12px var(--mono);letter-spacing:.06em;border:1px solid var(--amber);border-radius:99px;padding:2px 10px;color:var(--amber-text);margin-right:6px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}
dl dt{color:var(--amber-text);font-weight:600;margin-top:.8em}dl dd{margin:.1em 0 0 0}
::selection{background:var(--amber);color:var(--bg)}
"""


def wrap(title, body):
    return ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<link href='https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&display=swap' rel='stylesheet'><title>{title}</title><style>{PAGE_CSS}</style></head><body>{body}</body></html>")


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
            f"<div class='card' style='background:#0d1015'><b>Lockup on ink</b><br><div style='max-width:360px'>{svg('logo-lockup-stacked.svg')}</div></div>"
            f"<div class='card' style='background:#f6f1e7;color:#111'><b>Lockup on paper</b><br><div style='max-width:360px'>{svg('logo-lockup-stacked-light.svg')}</div></div></div>"
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
<p><b>An AI Crisis Response Agent.</b> Nury helps a pastor who takes a panicked call from a family in crisis. The pastor types what the family said. Nury works through stages, one at a time. After every stage the pastor decides: <b>Approve, Edit or Stop</b>. Nothing reaches the family except through the pastor.</p>
<div class='card'><b>Who it is for.</b> Churches and the pastors who answer the call, often on a phone, often at 2 AM. Flagship demo: a family member detained in an immigration raid. A second playbook runs hospital emergencies.</div>
<h2>What Nury will never do</h2>
<ul><li>Give legal or medical advice, or predict how a case or an illness will turn out.</li><li>Claim to be a pastor, a lawyer, a counselor or a clinician.</li><li>Send anything to the family. There is no send path.</li><li>Search the open web while it runs, or use a source nobody vetted.</li><li>Send names, phones, addresses or ID numbers to a language model.</li></ul>
<h2>The pastor's journey</h2>
<ol><li><b>Pick the crisis</b> on the selector (detention and hospital are live; sudden death and house fire are coming soon).</li><li><b>Intake.</b> Type the call. Confirm which names to protect.</li><li><b>Stages with gates.</b> Triage, rights or information brief, attorney or hospital resources, family checklist, pastoral message. Each ends with Approve, Edit or Stop.</li><li><b>Package.</b> Copy or download. The pastor gives it to the family.</li><li><b>Case file.</b> Save a set of linked pages and a next-steps map.</li><li><b>Something changed.</b> Reopen the case, say what happened, and draft again as version 2.</li></ol>
<h2>Concepts, in plain words</h2>
<dl>
<dt>Playbook</dt><dd>One crisis as a folder: stages, prompts, vetted sources, outcomes. A new crisis is a new folder; the engine does not change.</dd>
<dt>Engine</dt><dd>Runs the stages, chains approved text forward, runs the correction loop, runs the gates, writes the audit log. It knows nothing about any one crisis.</dd>
<dt>Safety floor</dt><dd>The rules no playbook can remove: no advice, no predictions, no identity claims, vetted links and phones only, a disclaimer on every output.</dd>
<dt>Correction loop</dt><dd>Each draft is checked. If it fails, Nury rewrites it, up to 3 attempts in all, then hands over. The pastor never sees an unsafe draft.</dd>
<dt>Gate</dt><dd>The Approve / Edit / Stop step after every stage. Edits flow into later stages.</dd>
<dt>Skills</dt><dd>Small versioned instruction modules a stage includes by name (voice, grounding). They can add rules, never remove the floor.</dd>
<dt>Privacy layer</dt><dd>Replaces names, phones, emails, addresses, birth dates and IDs with tokens before anything reaches Gloo, and restores them in Nury when the answer comes back.</dd>
<dt>Church network</dt><dd>The pastor's own list of contacts they have worked with. Listed first, labeled as the church's own, never endorsed by Nury.</dd>
<dt>Official list</dt><dd>The U.S. Department of Justice list of legal service providers, approved by Juan. Listed does not mean recommended.</dd>
<dt>Case file</dt><dd>A saved set of linked pages, a log of every gate, and a next-steps map. Approved text only.</dd>
<dt>Evals</dt><dd>Four layers: deterministic checks, Jev yes/no and score judges, a cross-vendor red-team panel, and a human review by Juan.</dd>
</dl>
<h2>How the pieces run</h2>
<p><b>At run time:</b> Gloo (guarded Responses endpoint, Claude Sonnet 4.6) writes drafts. Nury's own code checks them. <b>At test time:</b> Jev and the red-team panel judge the runs. Both keys live in the server's environment file, which git ignores.</p>
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
    ("Overview", "Product (original brief; positioning superseded)", "md", "documents/prework/PRODUCT.md"),
    ("Overview", "Judging notes", "md", "documents/prework/JUDGING.md"),
    ("Overview", "Features: built vs not built", "md", "documents/FEATURES.md"),
    ("Overview", "Technical claims (verified)", "md", "documents/TECH_CLAIMS.md"),
    ("Overview", "Who Gloo's customers are", "md", "documents/GLOO_CUSTOMERS.md"),
    ("Overview", "Case management standards", "md", "documents/STANDARDS_ALIGNMENT.md"),
    ("Overview", "Standards page text (for the app)", "md", "documents/product/STANDARDS_PAGE.md"),
    ("Overview", "Plain-language samples (before and after)", "md", "documents/product/PLAIN_LANGUAGE_SAMPLES.md"),
    ("Architecture", "How this was built (page content)", "md", "documents/product/HOW_IT_WAS_BUILT.md"),
    ("Architecture", "How the engine thinks (walkthrough)", "md", "documents/product/ENGINE_WALKTHROUGH.md"),
    ("Architecture", "Technical reference (for engineers)", "md", "documents/product/TECHNICAL_REFERENCE.md"),
    ("Evidence", "Claims and consistency audit", "md", "documents/product/CLAIMS_AUDIT.md"),
    ("Architecture", "How to add a rule", "md", "documents/product/ADD_A_RULE.md"),
    ("Architecture", "Pi review (what to learn from it)", "md", "documents/product/PI_REVIEW.md"),
    ("Architecture", "The learning loop", "md", "documents/product/LEARNING_LOOP.md"),
    ("Architecture", "Observability", "md", "documents/product/OBSERVABILITY.md"),
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
    ("Presentation", "Script review: pace and spacing", "md", "presentation/SCRIPT_REVIEW.md"),
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
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
@font-face{font-family:"Gochi Hand";src:url(data:font/woff2;base64,d09GMgABAAAAAEzAAA4AAAAAgqAAAExoAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGiIbDBxYBmAAgSwRCAqB7GyBzAMLgzIAATYCJAOGYAQgBYQ2B4NkG5BvsxEVbBwAIJTNi6I8svqIpJM0afJ/OuBEhsAl7VSf2whCMzYatU1dEgfdHZ0KLWnSI4htope9TfVqx0Zv/HZx0MG5aTP+f6pes8fq3+cYP6xwLmw+A9ypET0l/4c/9e9DASetzxuU05/iK52UQalTnGxOM6l2CqUdVCosUnNiJgb+n7/3c92z97l/rAF9mknT1rRz7RYrlSCA1SQUClgoNvP2AM2tg0XfttstohgbY8CojVUzYtAjShCpEEFQERPzrbf6fX3jQ//VD/2w/lvf/9aPCILcPUTwCkEtkrJb4EGQejUKPtSmRb7JtxJZk8qaCGnO5WcOX/iKxZoiM0OkQsTrMsDK6y4BAhh+cnu9W++t4IljkXaqL3snl2GitneNkV++6OFfDIiY/L1Ota6ZrGvnAIECxB8CyK84ba1H5CAY8CuwNfDP/9XaaL5Vlg9RC8gsxwfDrKGr74q2gAXYgLSobnoI3k1oQUK30UIIXHxozrS50JLH5J8dsPsJ17iXkfMTbqq9PF2u/QHmmdsR9jtGOQdsp74dAEkgB4zCABkzoSf1LAsPKISZnh7LWTX//1XV9VNyK/SWk8mjvXkY086ebQTeBT8+3gdI8H+JEQFSBXKlXGjKlXID3SimkXRpW1pflamXLcdTPGVaMuxDbCxVXLT7MqwhiOTx7DJcec7mbxXqyEGC+NREptXdPeVry2YbPYCNmwZJNnnSFuDlz2IOi2FjPv7VLCAAoA4v5ihggMAwaaOMcvEY46CrsOqrCYYLsmQJyJFHIcdAGXCAJGKQxVdBvkagGHSMX4EyNu1GRkEdFGEMb2GPtvPsEdgIhg2MJBQAFLi9es5odc3ABnEnq5eEqxE4xE8s+Yl3p9jwL6T13UnstwCKhGhrQHQuLRR/qz+VBLoLYKq+nkpXxCELWVsQXtf+MneRD+PYVZKaqpk1TDIlWZKsSfYkF5IH6W7kzLRC7tsYejCNZEwyp6n3YvJHEYSfpJw4+PP71cHLv/aK5e+9PWtiJwCBF4iKPtWHzSs5wSPlxDTneJmj3JssFgOgtudPoVAXWZBeYY8e5z60i++M7XEgqfgaYRQivRjg+sIRgcqOHNwYFhE8cs/jXQp4fj+eGw8tf5Hdq1GuTif9c/OjgJBXJxbPITCV+OWeEzsxzKP//0iUCWUECoGEdh5URoe06u4iNpPCYkAmb72PFzLTqjRybiYnHWYbKLo2qJKdxeXmadmT3RmMKVbAmxYJCKB0dlp+R8hhyWqP5qw2sUwGGtfCTGOm57BtcCSbZqEwdRSvqMoihPTMejjXUW4wlFSH6mrBWjWTkoUt7YDaQLCbS6FI4TwtTaEySWEXhwNDdsjexHWkp+sEkFzjpIywMqVBsgDS0RdUQXADg0KByEKoiM5axI7I6UoeJKLR2Fw2G1bIWQW4kRrKQmeiPzMUTBuMOvjHJeILlHRlSHJ1zCzaQ4zHW40DZB1SZ2MsEQgJnGKJjJ8iteBBwBeG97rGEHav+LGbTYIwNB8Tffj3J33x20zKi6NpgVDW3JsLFCMxmiQmH+P3FESBnPb8yDsUhwTK00qHiuor/hRVrwfmUJW7KgklrZpeHRRGmzQMR3LyY7ZJ8rjvDsY4UpEH8uz+Wd2xEKf6/dXPykPc+nt8QmC55mFGN/yZ71HQidmYZpepqdZBnT1fySFBDPQkn+HBteQV5nH4YnkvdzXRsD8Gd+FAakW8RUV557Kvsu67cxleVDECRtXrbP4FNWrJY94xW49KmNGVA2nsMmV4gsRwEjKy/nRAJQIHHMMkw4REQqcJCeeAxvHEC8GfDj7Gq+WcCtykclfK+rfaOILMRiEPipkMRsHUH5plMCTLQ0F23N35HRWVH6fbXLuIMPkkIbH7/gtWxHShzUzFH6lSB1T026uINJDGKEo4SYGcQ9YAA/a0dXfylr6dlszQXsOow0MenHaPN0TJu4srrSnLBJt3JqRsvQJGK6tEQM17YBEMoucVSUmm9u56GZRt1C3QKyyG4lQF80jx/jjB9UUAkJS6VRIO3dsLNgLaberOYDIkwKe32FCEoHBFhhGeyRWLfDkS0OMVA/d8/uFdVkyLu6MynPkCIrF9wgNIHN3IePItjiEJCDKswbPAkgekpcSF+8uoaoEzT7ZnTEuy1LTASU2E5KbLS7ez0bRxYZkO0d9DAQfvf7+3PsRR00kfqwK9czoP8CrvGE+qFWu1XJ0S8aVppgkunDUKBTExT2SGtDVqbw25IgrKYr4G0rbRSEEMI8vGOggaB5OJV/jiU4LcLGxBm8h+3aMnz9LgRY47nHe48pFCups2p+6afGbVLjDHk/fh9qmQIPs2un8hZqpEuOCv1KGtaQ7Kzf07Xs9jwLh+RgaK3uWgyEgaGVQUgnu/aub9pFF4E5vMhFVuwHAZc19zDEWR7CW1fCQxVq8HrugKrEMsQ/WzwCaLx5wy+RjNIQGR9IwjXyJA9s9iczA0yyNAAXcTsvV+9PKRfdKQrNbhcJxwTNzVCX/DoUToujW3qkoRWe/pmSnNPrRoqflBkefvort3tvDQOTJOo2THnrRxHEJ0OLzn6ZTn6St8JDklrxm2+BKbxLfLtcE590zxjOOcajhyHYqhbvdJs161nBrOahbOi0GmcthomseagfftX8CeJHyI43DvhkwgyxstH+F8Rr4fWxYQJxgkDKNNSzPQnejomMn+R6Aq3vDhBcZuU7GYmIBdLG/O8d4uyv31m4yBLiOSAbKCvy5hAnlKHk97JMUcHCBfM2e1ZdHHmZLL3bFEXlfv9IAVsPMxxgooyFTczPNxSpGL2aWlzxC4xeioHWgnmcLzO6nA/5MGOtvJ9C18h+gunHdSgeLdxZfNAn8OPEE++i2V87Int+pCnFripBCtFoyDC95eteGgzYJYXRm+gh/k+6G3LaCU9ixe6XLJlA77ju2jbhP9PR8Ar+oup32F4PgUh5fJmAcJQ/ifS0UR7L3Oy1niKEnhk16yI9XSTVjaTRspb8W03J538LAlj3lFqiPJEq20yr3qLWJeh2SVcMwxFzGhaH3hcx4dIyn+FEH+TxDZ20hcqrrbypypmpKr2znnDIFk2zCeFVQrUCaxtYh2hicDuyLzhiNe3b+lq8V9Lt8/ExZBx3A9mF1mfhbxsSgvdr+uczLniNyKsOCRrWqQHJ35Xw/my54YeNj8AboFRnoopqqu+3ciHW+1cBV8xnXlPqK/L3Ldl5xGXnmOza76LwFsIotKhWcNoV8xPcsQZDEB2tBCyFZH/1OGm1HWtB9CM+8mCgr2wQytHvLqtJp879vMgNCykcY9nHed0kxY1hKnzudEii/FcYFzeXmyxqHb3NfMLebBUbXdKNIXVZeDdqJ8zEw/3vZsiFVtc0gZprpleVZI3EEYj45c60T5iUo1VC1rBu0DN+XRU9+tpiaxxfHx8/nHFDyuJt4P8M5MsykJhvlrQ7Hq2D+TVebhtBpg/FKLyL8Y5TPe9vzf2Kcn86zQoBaMdfohnSzeyIqZ2yzEyKEiiEBzpVAX0nmqrCk2Yd78Y9VystiK85LbgY7Nb4yqNAlN4iXQZIpF7ZX0c1G16oYYtYYsg0lCxIXWxTQHi/yy/oZl0lYrE4m2R6vS+YYxMGph6WuAM7EXlX9dE75psMd1UCiPBlMOSgz4iVYnzpzREPlIaF6BHcrSW1ujfhWdxi3vGWMi46Rav8OPYC8HFHmPADfBG+0mWhDoS18npoY9o69zlFIbwASbB7GIBkAPfyMAdTv76LePGI+QOmsvqm+KtDB1kSYRxkhzdnFqSIK8tUUKo3Q1Nkml0iv3JN1wQ209Fi3NQkEJv3w1pZfTapA/0o9g5Lwm1EGvNjVabXQAGc7hdDLkxM+Hs/lC/SgN2NyI4o2hq5tV2JPPIITWCy+UY45Y+82u4uOhid3zYPP6s1Vge1PkiBVcO2Ipg/2BnqJxOWpW6fdhEqaFHVPsEspUi7YnHHjYmG+8qlWsxYCHKGfLAGTEeKEWs0KWDywu7CCtGY/O4A/m3il/ogd8qD9qsdvghElEFhVLFXdn4mIRJsopwuL3XGIBGLBkc86dpxP2wBWKg5Z40bm6qjdNxt4KWmskNKSLmmXd9MSH9ECsUCkjLUEDggQDHTEOMU9NmQ84pHvepLiNP1Nr0aQfeWVvpeMG5V28eNEbe9gBonB0NFywwk2HZfo98gXGNEktIDPeNRQfR2JqL4ud3cqC0cT7OpcCNzcGWd3FcNTSbL3nKjoXInAK6s+N7ZxEgcY8PHs416KDDTzgUHB8KEM+T/T6AKubzKBvgk41CX80Oh+S8Qg+6F/h0kxv59oz4+WJbrkLXFpnzznqT99XcbERfOePj096Kx6GAXe+P8Qzeb9SE10o7c+BM9V8ui0Nu6Bw7t8i0k0RoZ9arMr2vzxRLiCNwVfcjarZZeU6ZEHhK4LS+OWpwRF06yOyuBDkOIakAnnbf9bTwHUMwFbVqLspzaPDbZ7O0uTUXvKqLJbc52vgJ3josnwYpDka63EsZV5FPKNkfpqeno7AAsl0wt+mUMUjREHLb4ZD0P3NJIOkN2eEtvRo8U+jA1mGbUnX9ha24JXG2E70B7yD0aJPwJ0Er4HKHeeKleXGpsXh8dhRS1YwY+YzHfC4bTkMANs3/wgUQxrt2oym8lgjdiQGN8kqIjlZhreOObLo1slsrWbclXEr8WZf9rtca7hg6SZTrrTgi5s1HeaITj32uBxgiRfkKyYcfpNk86/vBw0b7qyyjdykTm+tnEizfHkStB6H7+9Fc+JDnjt9S7Z4N+5KZ4RcMid71O9ATI5qY2yIMZxxnqDfgKUM9gqpYKingR5aSUprdEdyFhSPYt7F3mDTJzEAaR63bES0MOOhTsUpbicTxijJCmojSasZ6UBVGnGOJTLKFSOIKV5CCJrMGeaTwM6vB0kbe7ewghm06GHa3zwodRcT1Us3a9d+9VryLeLwUhg0lvd5P6Y3bwObGmNdrK8WDQzQfoMHN4wmsToC6hSLZexIkARu0Tn7Ye8M+MEaQ/Qa7+6EgxfCzYbZcgQINIo3Wmtlt3tlvh41aN7SsSsExueKrc0LZ1PL1NMz1/l7i44tJsYpNxwtHXcBbdYnHNJNytwSyuanyJTQTNOtueF3xn/D+Z4Ck5KtJycC7ixMecbg73xywg6CABtLUHPkKojiyzQ91FV0vqrlBFIszS2atNUx21SDRu99UsTTDr+zCex1LpSM0ikb4lCO6ImZwq1MJxqJD3aCJkWY/JjI2IeWjjFEXyBDtHf0GU46iBOn9cQgp5AeJ/1sNHpUQjgVF+tlXzc1uIfDcooxp8XY0S4wDp2QtMtlG7bDCqwk/W8WYYlb8UKfsL/amVLVPGSWt7FDYl0aQ4Yld/PAig/3oCBHOysK1JyWt1QNMlAUlnh1HqryGjgR9T0JqjRSm1sG+yuog28bHnLwXFPiLU2JlnWSER7ZjRoieiiGI3hAciu5dcvT6x5lgzM052JO9ol6vAuyLEYT0vz8SUE9K6zRCpJasaimvNrbRPqBeGw/0y/CDuOsWLgSS/7xDiV4hE7/1+lr/ar1b3hbOELJCxTereEwsMsgmcREddoHky4oa34KvDPh9TDCk/Hq6mHUbWc4AorJZmmb7dLeZHWN1IR+dU3s7EhP89re4G6rI4by9IzEVhQ922d5oiqvhE6BPQjLvDY/gNH8m/9LcMPs2QcUnP/o513RmAqeZaahDTYaToVvtfqYwGzcTsf08nfeY4irQBp82ihGDJH15ombXscU0l/613cM6jDpnvNTaUuD5EsSHNgQY4tG0m1W6P8FoP/m/qqTkooJp5MtAe39oJZMtqNHBY0ot95q5NvjXAx2FNjR+c68cEKFHHyJHnfAupcbz2m1lo8DtenWSbpfsnkQy4lg0UbWO8Ah4b5iWQ3DGxosnuf9kW7Q8G/mSGU8aEuh6PCEiNK2wi8nMHQ365G0zopRID6fgbh3zHqalMV4SyDTt25lIPxD9nX0navR93mN+hVmBIbTeNHyMjiJXSUlbrfqpWpCFuIzE0vU6GBgoCcrhPfpmOqjz2PMq3q3Vxq9UQgcfJvddPfHRBM83Okgqu5pINAKYHovyz7BvlvriIA45Cjuje+4jOkhV2pGCrs0dfGqnjrlbnrK5vxpXamzNxRBq7HUyNsodT8CuceAyl6pEnfMxgIZ+69zH8bx8HtWDKOJQeqds2t6cdhu1pXVqxvRgDqreowIDbIilT6hENxeP1F1cKTm7PP9ubGy8Ut26RQ0tfTqjClg7wto/G1u+Zkn3iVHDqNkQ02Y5Z9j2xQHBn29JZlws0gUa7GVa69o+4Ptwg5T8cfshEseo/2g7Q4tzzE4ELsgSaAAkxnunKl90f8Zqmxbw+RFqN3aOMqpkgewavEq4iavllQjPvwAbFutg5IHTF/0EDr7a/uKp96YCa0Tv2emVJNIOKjY6Pb4osXDahGJd7T/HrwbzJZQEJpuykPblxV51Tp8eXjgmUfQNbzmTNcI+3kZ4prz6qxqwuIzSzV3wApoHYQw5xjylH7K0eNZi5AfK3qeC1qhVOD+VGV8DU83ZQj8Oh5oULnawbnuMlSlWr8MbjrGmMm4yK3avUe5ORC8MgPZ9baBrkM4Ym2NhKvAEEpv2lH3M8ALW5jWUBemLy7tgectIWcaKcz4sruiySv8TkNMk7ugEqeDnT3SZ3oVvgz6QNronG0aKwjl5I5ixRF5vZTnxQ2rMYmrxWkmBagO1wV9LqksVHkH5FpxgWu4eQGH8XlFr2Q2mCKEXheDSobFZ6qcaBSsz2f6UjEEGp3er3RaXcpnnpVFoLqwlGn3ueLagnEMMm1r1OzVALDcyM1zofQWV4OKmhOGADESiqqAX5WrFQIS9NXQNVnyGDJr3tfFkeV92j2ZOAe07Gzl5DwsT6AI7RcieHbt8Ma4sIqB0S/L+Oax70rXLgDVeEQeWtNqztFMShXSi1NEOh880JLwSUd6KDoQviaWNRYQGnW3VuTO1Lp+V4nh49BoWD7zMlXJZRLTe/iSRmbtmctdYm/5O1ax1dvvki9HCWkp3IOXzOgpmdYQvrcBJuUMj1wHpb9kEmGDMvIfXaMZl6lJpgVR/0CsPT0q6NdiymXacbYi7UezgJBfaeSG6HF0n7tsYPtSDNxocwKkcQY+9XwTyzh/xbUV1BOS2RJlCCcpuJvjOSV0HfZFwVpV9BFXZJ5sHJ3HbOtbMqO3EIm3npssSm3eKcM9TCRTfEJJdBwPqu1sh6GoXMH5a2VNMDW2ErjNZM3mzJTBhM3GsywBE1OvQXrBfdCxK0uQ6+ZsDLkiz/Rjp/Nh+ro6pF8hkSiz5BdH6iUeRniUgURWcw2nBIw7Zllb0Hw9c6jZKCFwXU0P/y9Db6PwxtZoZJ4Yx6XW9vhstJRvIOtKZLswbE9tJLm7S8lMqJRkkhKLOPyegpUOpXMvL5FYd6cwzrka6QeMfTd+ecFj97KM1zSY6UajCtNbpfnUWk3pnCWWlJLxRgpptvC8ONm3qzpd0dhJujyodDRZh+yDsiOLwDrFNLK1vdOCkHVMZkxOSrHBK52ZdotsL5w8unRrWTJhXYigu/J92GAEs4g7WfdoP/dyyuMYUFZjO8zsIRO8XNc4pu69lshz3qb9piUCuJI00docuVXme9Vk7wxm29PcGAASwXhp7DLgeRnA+K44gQwAlAisb5bnkDIGPWys4ootpx6GDhL5kCgGC8LUo6XmnKVH1XzmcovpL5Km//8bxtrV283DYmwkwYpgN7W/4+2cnQoDBR8kW6/XV7T6sVf09sXo05b1B+S/W61aRHCcxODi9Se7a7omowFluoU4IFs7Yc2WCnG97MJsMeuSLsZlZSKddaoPFUJiHecKlIhGnRYQkdcF6OrOI1jdyxATJshnBgpxRrluDt3cq7OdlIBCRgQorCg5xpFq46qL+7EfDURXxe6OxuifpQJMDyXxI74hSX8jhw66hKJrVfwQHq5ZWRW3K0zVYu5BTDPFAHnguxG2v+DuCgyo4xme5UAftYZ/iXGVeL0dNl+0Q3HCBi8Dc75wHa4fwReFK9iaooxszk+RSqb2I0BZ9V7VJy6EUY+XvIJl8x/ozWbD61WoM2rmMJbwGnmePsIxGz5J6pj7fLKDTVuZKXY63AQhsLBwDQ3N5J1+XiU5tzotpfjOIuDgFeTICJbwPtnIHIRQGPjN846sfB00zuPn/u/r+gIQ5LPv1H4SQDBaYAL7BpsXQ/B0lyIIWSqd6d/nYw0i4FSYEX1dA/BGNoLbZnaIOD+IMOtsmACfiUu8+t4XnDzCJ8W9xdV1uR1We25DtX2R2IKD5jGnwG39x8Wcj0WED1qSDm+ZujmbUY04x8Re7aHvHTdeAzMNiXmS8KUuV9xpdKnT84J12QPS5Zj9nXdOg5D7uxwavHQmdvXXTSTWedofqHmx+yIE6PS9qzgMnONg0Y5pJjUmXxS6p+6uJVBBMK1oWFngajE7SsVd1mDm4urKEZMjt1UfKtYtcsA+aU+s4OTiUutjjHSc40UT0wDVZx8Z8uUfUoVReDyhihaEVeZSRZ5DVG3hTBw6rqhJR6MyUOhfCDur+fqMaonboWm0p97QGWNZii5o4yrhN/e/5EvbWjP5IOqb6bwsJNrIY0EkPgkSXq6BRul/sngPZIxX5we4hDcW6IEsWdc3fIHuj3+/kb/59szXEPHcS43s7KyFsoQzK1lgNzUeHhrHYQJKv2pRjtvUk4gMaZ15feIKe1ZDkU2b9AeTueUZqegfjvsCKb8j0AtEKWhCJoVqVjUjsPoqUYCqoJesrSJS/39AnabIizDurRM9Fy5yeKHID1zGe97F/VPC/wjU+/8c3vExBTyldhDsJXYA3N1g/OvqUyL5Wh4mb2A9NAwuw671eHDrWetUc/9zG+v+JVPX/vY8SKRe33Ci4JDyEu2V+g1SJVBzYdb5zMvVgm2v04sLpjZNd3/7vet/JOFZ2suE7M1aBGEqds+V9WjedwxM7EwOGXp+fwae+oCA7Vp5ooFC+8v1DUh6OO1rPIxHb/y+5D0Q2qPajiMa1upwOFzTwe9g6iNe4a8EMNv6B47QAeLG1i8mkDfmNZPYb0qFDSB+bM/TJFpZfO53PPGN11qsWNRZoHS9iM9Ba+nbvy10JRA8+cvMbHxXjuQC/WvUFMqahvueMcL0rqZ43QWUVKczlUqeHxWS0SwsVUX//H07FsV/Q2RE1KebjTmDSOD7YQI/lt5VOGJvLihiE/ORw0S8Kpw77tjLro6X0aBaVQTorOEV6FUeZSnmTCW+Fl+CYclXZVt7CR8f8uGiOB/mRSBC5YtrfSxNUUYWJzVSwdR9BFDxxK6fahBXcvhmS0+H11xxm12Bi7XACBysu+0stoi0/wCPojrDF2fnLkQ6el70b5gsOdloV48E2zvKpwo2SSLtxwuGe4v2ZgJNjtyh1opV5khWncblVTXkbNm6f6VvSlnvyqoGZhRPC8H3CwNC+EWPtTK/Jqtc/5/yd6oEzWx48IhnmNJB6iUuwtUj3WS3k1DegxQ6pPhlXCxvafV9OvycXW8zAdSP2rd/h3Fbd3ypYr511OuuzljEd7jG1DVBy0JX3L6zbcP0jD3nyBSWEIYbkc9TGvBF2BwsPNZzSwiXontwy4izuGl0FuOTtBEmb7b+TkdsQVVDU7BN35Epu479RVIUyQK2XkqeRgvp9gSKieDv21f2+Gl/QZG895YXFDu70pC/sah3GAt/ABn+z+PCano9Ma10Tp0MmDtsctjT8ymBeqM94jUlWE2ZMdd4X8kmbcQ9IWlx+hooNjofzVsisqGc8MfPnE6+yFc5yCmH1emKwFshnkriYwCW/xqodUJc1digtOfwJh6DvOP0Rrp1r/tCxm0MZYQP2ltXvwwEf7wEXvGig0QvY1oi4/wwcePFjPKJfbnF6+SUDWR6q3YjbMbKkXmKmUiqZKbsdLIL3juPh2wUFIfefPNTzesqNgVCi2w1lzeSQPFPwMPdaMmZ6XKmAMv+9nQ0dQpZEFiHcmFMPNrfbvYjWRvty4JNNdYeV6hwcX/lIWNr5Wn1mpLEVLni7r0PX+ZS3alpKC79nMiSHaxI76Zb2ruL8qzxql3ln1ats3bomjD8trVO91dzjAfUxnLAQFv8JE/077L375G5n/w4xTVEDbkRcUsWe8VI4G8c6Vy5/oWsDmsnP241llsd1vZG71KFd8X74Z0ry57sqLOdG1lzsqzT3qoavM764IqFYepglJ79Hgut+qARyvT61cDp1ZJiKb1F8GlPFHUQFcvIoELC8LVXvkpQWwidqAzGPBz28OjbFLwkVx1MiUELcV3MRk2DuATnSI2BBnl/N6H1MwMLP/pamxXMXEEncpazU/zILan+VI+XLG28gkYUpDoJ5axxdmY7ogrpRACix0TvWnlP0N0TVKNVQSzDtqJgVaA6vnx54qi2LLMLalVUWR1RZUuhXTs5kAqB+3zX2KGCjlb7DN9Tc//gu4elBBQh9vnzfL8LGiBiqAPfSA/n0CymcDSjkW3Ma6S7VR0KodDtv834uXMbg3IbkJuicMmBUk7+2BwejdZxfdJiMpDrX0/6BwT/bmxakIZvQd9ui2MOoKJku4twJEZA2VAewuYdotQ4IpxqIwkYJG4s61ReWW6/utZvbcn35XUlo+OZS4SDJN3I6zYSI93887MUjkbjx8pB3p1PasEK0a+anIQrJndT7cJ3AfbqlRKY/t9wMQxRv/cEXPH8Ut9qCq3tvbAqIvXxjug4+BAYp6L2FBd3GKymmvRYQbZfJxXFLRXuqmBFMAZMpBi1CCxMjVxMP5wSgA4RCL1qZFwMnSRW0F4quE9A69AQBx5F7sI8ii9G4WNyGBGXQGWox/HHsXuRAI4G0Wn8tjiNRv3OExxHkUePprXXhER4RM92/r8xSrshYKw2xvKno890T7etHJoGEMFQIUDK1y9gtO717HRalsyjhba8fGpHxSbLgmTeipgvc6apZ0NVtYBOUwPPHOHQnns6KugsLLLzPGqtzPegRJA++cxuYPjMuvqiU2MzZyLd+kpOxJQf+AgdbTidLC2vT5ZZ0odjfZ3tg9HRtGx9Cc+WofDo6D/vpIoJObLizQ6WKL9MmeXltNpKC8ZbE9NZc8IZQmboFPOUeW/xWL9vW7LOeXho9Z6F54PPq+riu4U+ae9naGYe2iNC8280m1/WtfV9r/m49NrSTY+V3VtW77iwZP+Fuc+bqFnbW54XnihcX9s2bt1hiq74Z41sbhTmufgeo7Mw0yGyc3nqgnVjQIGEmiJEkaBUj4OQbNhSghX3qXbDXpZH5Aqu+nPmG6bgakcgUDMwdqhs4OZNOEdaz0eTlUomF01/q2Oew5LNVb67kgR9dsfgqJ822roVI8jvKEOE/Ud1B6j2AsqnkJSP5jMdR+NMHlrIukl+5G8ce4NV1quFsSi5En9hCHvGWA+STm8t6QRul5MvmFql57VrseiPsYrNfHFXhaVPPyoagowVk9pij6LGZNIMysuyUTjTpk59zGtMZoWsva2BtbK4fSnjjhFL3ZjyuYh/9uLhcibClZkTUg984YMi5BhOwa/eMSfU8wPyCorKspC57NV9FwiEWaIHDNZCN/Bo2S+rK0V+PagRX+TZCUpVlAAIQ9uya83uauVir79ofLB6T0ada5RVpU6I2JQODh3O0N5i8fVO2K2Klc5tbbyVPbriU++BqarTHf3RG6u2PV3RYQjDm1MFLD/leTbn4c53ANLPK1Q09Yw6FoKd5F1gcilgfF52bXDDXPEjoXDb6tMLviycbLkvX6a+nUs69/wZfA5+CppiDbKrDhGomASOD6PKK1aS68iD4AZMFWgthRcSc8NrZZ35tpjO17vy5UXUKLD7V8SVj+8geY8qOcLCA68RRaleEW7vSzvotD2abzLoF/wYHKWOsJy+j3tYtFtsI5vJ9KXPSMgc3XgD77rmVckNbjPpzm1QTaV1ncGzmmgTvDnJGK+GRuNdD6OYKL7o1Sc8lCSjh93FqmW8fegwmr7s+zC7hBLDScnZRalu1JyNSHgIwmVpV5n832QGdlF93Y6C5wWN/c8Jtjq6OiWh88D3d2m8aJDOWHuBS1LciosGGX7SAP0q83H80ZRa3r+fa0HKTFjKjqYvANpT61F+/HNEIpNte2xmUS5VXYorI5bhtKyPWAvw+vE6+gTGje65cp+AoCEmmVE4QvIw05yGQuaBADmm3EkPzXEEfkSI4IXWaQU0+GIKGZr/NSmiUCn7WS1Xx0iA0BYffIrGXvTURxTGtV35LnVKPnXrv8FWiPwjmaK5sjxzpXwlZG89rhuLOBY5AqUrN7e+mj+4C2l7uq9lT32d+XzbgR1rvzssORxUdtKLFn/nbLOtY1LS78e5NbRGQnpohtWgGQEu/0rY8S7Vdn8zxNy55C06hzhzCAwT/HhXTbn2sU8h+B0GeKTsmpBjOpeVejX2mQyxhOgml4ChizpXOZ0iUApE0q+qnmd0wQuglgnXJtg5i7WnJrfRDSlV6VmpfXKa+paLZiiQZ6NGCjQpYQ0tdezuAE4OP+h6pOszmEjhM5AS1VkFJe8bDqKNmWB/grlCAND+hyDBbydZhksRygzjG9LbqBeqTW6jU6jjnYB17C/hnQDeRm3M3PcXk3+FSdocxlbj67E1KDXTn6uq5JqMXZJq8y0eQw+VEYsQyTIYgsoYE9C+mjrz9mTXSmtpYLV2LNTS5ZtWbY7KH5cIF6/socWsGxu7p+0+u7u+qk+eKn/k86tDqI/pQD77jNLkCBZW5AbzDTJBPGtX1ofWVSIXZIbl/0zRTRP8FdoV5kFtJZ8JAUep4QKnzZSTuxyMa06aTlqPCkOLOsmk3077YPWPU8+V5OaJ0nDYk4szFoydmZpY6spjrf+WBZQ6XnhfIh/h0ElFEvQk4x/6HfImLiT4/QTLcDHCfZvVgtzJXAGrYtgYLopVsL9GeIm0gQJ4fpTwCgGwvy4mLpX7SoZK43GdXHbTXVq51T6yvwFHKiM3YOdKTPjGTKgAfYNt0g7NHJZRnFdrO3LNtYOWmVJTjcn5G40mup7XpataUle2niPMtWd3Zc6bdqcfYPhKbUSqjX2Kzvtm0ssMiToUQ4omaRFg+ajBVOArMJU6oyMvh5ciC2P70eOoCUR/SoNEMLD1moLvURW7aiobG9taavqv2Yw2iYAHWByJA8xl0uWtgeUg842t75PFGW7FIvZqyhr0pDZGHFXFQxq7uUfT7x2s6WnuaL4noYAPAM3FrvO+6Rnfhe48eKGwF4uff2IzqKmL7iq4pmifumlfPxo6tXAs+eaxHQ8rtIJw5lhzySZd7cFDhw5GjTMVtePmQNk6c0tdzgwQ6hUj2zFLcOsIa/AzLkyQ6xEJxGK82GhR1OaVNMw+Uf9v5o7uZ9Jny0KD7kjVuj1D7yXGWXI5G+1Hx9ARYXZhRnpUgXBIdiUNk1yP9LNn9pHxKC+uDt9WkbafKClnVCsSJnf2MWD3bDHFoPJdVJxGM3kcJxxmOE/Q6Mu5sEvUEtoz1r3TGq4Z0jqLOUNBq3ZhvGbEE6La0SiKlIxiMVxSgpBKKTxm+pHaBnHVetfShh35x3nl7o2i1fbFdTUTlu3VIekSW2tVdIwkRGBSkal+SphSQghzC1xkZwk6H+vGOjnToL3MAfKX3St7dFP588DCX7No6aywFGtwt6nfy+g2N9EjmcYKZ7qivDAS85TmxtOplyH61x3yD+29qrgGbrv9ipZcamNtytxu3pz+czMWu5yAYKHSJqdrydkv3tjwEy4L62Ce8ycNp9QgOnOp+zByCmn5Bw7J5kF3Lx39y4EfKo0NefWOoMNg50Mn39IqFcXEGD3CBTjZedaWuuCYxg5voVYzNNZYXXQsuiQyFq2LWos1KpXTkVWhTfIbQL04nOoE7/NwlR+8H+SrK6E0tmznIzRad2VOn3M43JeobLB05XrtXa2+xbK8/HFen7nJ76vWLMhlNzD+YGNNK66/BFBsCrEvPWUnbjuEcbhpTYK3GvupD5UD9E2PbL1gB4sIDzkirJxW/Pfp2Iopxr+ZVqkEDWnQcTV2nYxNXwfjUVlv36BTOT9EuMfVJagT3BS71AigHmUV99qljSIUE4W3kVZ5a0QHSkY3uHttSb0tKuqy2ThjumHrAOEuQzk3t5clXy0vcs2a1wkeifX4n1o5c9k7OPlSYsVO19sTCfhx4OqEwVEyXNgmK5dBX226TpbtPKCL5rZ4+4N9wQ537DKDb4iopoQHWEepj1YZbrPo1Gevs+TERmghs/dMH6dDOZg56Kots1qUcU3cFUv4qgrLgFS9IZuTdDhJQOXjXUZCKzTGWiFcqhwwVhyQsvWU+3VfLSumYIUsPW3MqyHFUqZyTj2AGelvnGMkTRbaone6qFi7VZBeXxiKGDP0nkB6H3u2oAi3ZADGo3JeuCmnZOLtJ4ljBTP5Dxee2NpYVfFEh7f/PYj6nj7eVhNoVptLJiqrtxa+oHmT8xauGpihleih9hMYLaNX4PXsVMaUNWjW0njBgYmSfJ8E3H7j8StS4ty7vsz1HZ6sZb9jGQRDdfO5zPIjcvrjf87JSMOLrTXtzxkblAE0u6ev4tOzveUakeCrtFcE3POrzMseYlnf9qIBTFVCLQO337i8W0o8cndVW+pHwzNikBsvr/0qDd98QYJPI8fE407YIwmolfP/ZJLpuIdPcNBkpXAw/0veAIONJh6cW73DRAVmH0gnhWgdsxR0elN9KfMpPon9R/m2Xd/dAGlH5499hSgI2tB8ZgnZEwimbEOEAwOptYQAXbJmdrG3gUTrm5XuuUGjIvF/7fWi1oAe3CdpbNpBeYDxdDaiBzW0nDiJ60DxhMOrisKiXYdJdPBqKf58apI3fyWE0sNYEcMB3n+Vx9i2gdVfSv0MHqo5irfjzD7w2zttKDpKKPQbA1bvSQSZOMH4CAkcjTuz+Pfq9l0tIW2GvHqP4lnhHoEn9XBqO/JW5zjhgKaxVONL8WxAljotWRm+qVsIr1cJxNqBuTpDyjzqOP4CNq7IymihAVTbBG1M949F5CzW3YZxCLglVoFj3273mHs7Miz8nCs1iJ8A1FTkyOK9X7dhSM6nI27yfC/R5t81RjgoaH2APUSpIzPb5J26jfCc2GJwjC7ZpbJ1/qHS4dvLGXRI8l/AU+wqy5/p/wRN27JLGZZGeL6501z8m99nUoksoV+bMJXnxB47yJXGRQlLtbsiGAsC2w1qBA6mxXamcf7zb5+r07gAUf8+sV7XBylKtFG3N2FJiKJcIvIxLJX28uJQsNJns+lSXgV07I6sZnEoNy2eQVf8M8lIFaVSUhERxFrvdC4d88pWElPJ4x126cq5+vDAJGs8jieuahj/cLwrI8ZfLggbXXlbWzfOLtvSvCNXXkH94GwxAZtQb5EqarT13upqT1Jbp5C4RMVXTgKjD6Av02+kfc4koZni31Yx89t2wgsYa+hHcAkVifDs/HPXA1P2uh7LjsoS87qa1klrsPYJbyR/BZ508kcrJ5IKqcIyl8NamwNxkdQnC4KZAaWPIfL649ECbpshWKQBuLQcc5LvN+ltEgbrg2I6s/hYkVw23wkXG1e3b2g0FPGluxjECcWroNjmas4el+ZGpvPqOs1bq5ush9tG1zmB7+8asQx+Vq69oDCjkIWqRg+glhe1cDdm1HvS9OzVPPgIn/Ot3QUpilc0iVsNGGyE4y3r7y2e1QajM+a62szJQH3k6OzEOV+rpob4dU9OwugMGqr55SQXmfD42UPbh6T0vKTUaZdXWtJ5QbmHD1h97l3nUXb/8OA1UHD39+6CEe0UwxZbo1oYCHSQi1Z9RJX3SUAazXFLSNagBc66nqHorM7jn9TUBSzNuWqh40yJsKRSAk9TOd02WQldr62kJIRx3VOCT8qo5IoSLk9dynQpnmUyedQApgpfQwJS7JMXJJTwBQFRXodsOKPHrhfe0a+3VmQdvk1itz24zcKNlnTmetSt3Hl0C+UxsjJM8BD/ZkN4IVR6w/wxjlu0in2fns95lz7Oo6coL3LY9VKci3QI+wrih/VyNyQQnyQBChoxvRR0UQQE3E8DvWLFef5C43/dhafXLbGOZ7RGi5J68u9vsSHao12D+QXKu/JtAiq4uGbir4ltniFNWdDQYSvUjUY7u6umizbIdpeu/PRE9ACdgcRvdpDL8DrPtKE5kt+clVvmAhDs5ztXs3IUq0lDxE3Eq5jl4Co0bkrsjw/WFXdosv1D8fg2/d0V8sd23JUYphW1rEPaxVafJPTIn8V/D+bvLeNkXuOjTgryRACrEgBT/8nCzPLZdOlrpsoaK3YBdhg9iRqPpnQc/yDrHPEH8BniOLC3lCPIwjgyb/CU4ld5oyLJe7HQP7Bb8iTrLeIXg4t5x5yt3bq4sYPVrKrMcuatE5AHRAMU2qovI196uPjPgcspBV6W5mcLNzVaydJ+AKylleNeBW9TroEHcUMs1VM5bHX5S7osVCW6DzOPqgV3oAlTJSeeOp8wXzJnp9d64yU+ryu9SCL02lYWXLNOcMwoiFHwtpcqqaF2CvpUnWn1JtXBayg0C5Qef+Q9iV4MpIz0mZ9xsXIGH4SICc5V1mX6ecpO7LBUduVbokw6LVcQJmg7WKc4x1mP0kYJYeC4Bj0j+Eh0mNVKoj3/tIFOXRWyzfhK8ITb+feK1ghrl26UrYoMo1BHQkxbYaUz28MW5zckgk9mc6ArFrsmR75bTZwTvCvdpAlxSM3aJsNj9BWl13QZ3XSEHVrKHRQ3yf0jNHaaS7aE/kQ3DYYFcvk7XPbb/5YBaJqSvHNLmEuO/EOMomwZTWjcWu/rc7a2SOXZmEL1DoeKZdrg7XSN3cvbavnavCcjzuHobOqVijeoGzwug0VWw8begonUfYQIUBegjrCpVzKviJhreo9PuCYMY+yc+iPu8VHvgdrq4IGpsce8ybq9hQOL7NtvbtVUiP229JrcPG1rMNimze8e6B2yKxa6orV6gNSgdKns5CHF7xO9WMxOlrXEl13GTU8e9o5Muh5r6fRfWDbzpH+hWJ9hegUIyr9me2vhcyaPmWN8qDjOWOD83Y6bwPuqD2624Rm2VrnPrUzm+ZQTzprqTIshqLJ4+a2AtfBIQkj49duYNCBahiJv0J+D4B9VDvFcrpsXVpM2lDEpquqh1xeO+8fVFT5TS74za6yufaJsdf4GkdPbQP7j9i2QdsI1Rib0LW0msrBJcJyycqJSipi3d8QZXqoVK/pXJSx1OsEpiZ22QJlxkHFwRyGb+S4NW8947r9vTLW8Sk/5qKZGGUKLm1Ha4l3aMU+gKr2oygks+lo+qHSyq8ldqKH8KHF7kfaHXMITq2Qp2HLxBdN59xP60omjRPK+NalMRU4bq9dRhyKICbU5s2WJRWqnMkL6e4gNfTT+HQWCWw8AsLDJsUYyYAk4RJTzvQ8g1mF3elxpFK3lsX8KZzbmtjkaI+Eaw0J7trLKZ2+W5oem0mpi5h5noiDi1AiZxOG5LjJnyUypIFpkjlWPJdZWjCVjC+0WXUXI1iYFCPh05tMutmrFgxChmvciubFaTZC50FFMFO1F8hjrv7JRyadUz0Hlj+PLsS8qESwEoQzeCg5iwyTZ7f+CKkUGjBpgf0cZnJMhehD3u7j/H9lCZSaEhLwTXub6VbJysrmFiSLQyVW8LfCCS4DMd3lsPmwszsltFa0tycD45xbTRdW5gWKH/bSTPfnChfbe2GxRw3DWoSYFohTTQOzDOHSpCsmlw+sgCAxSGsBeQFGC1M4o3mP6nBoDrpOQADtaqEsYj5JqimOx/Kn8kfbO1bFH0w5GKkyJQt12zddiRi4jA14obTfUZnraOZBSB9w8/mjgqKfneRc48i6Tj6YvMU6sSI+r872SZI6NX5L3uoi8Z1UKg79O18KZdiQ9x8emDgSqw8MWk3P8Tyz+z9WOxPZATeuBRX238lVPBggNf1jU2nqVkBDkzat+9p5qSubP2uYqTQQ0ielCOgH0x+AL4zjqGxchGmGyWBUcOYmGYKTDv3KJU/lIHZE2lOoiM1fV+fXLx/Kd25I4bHLY7/M4TTYen5lH5zfwxX1Le4XpjeLG3GT0e4gGI78sa44G/FoZp2nXLQKYXav9QRJvwbtqsbyv8kuqNgE/c/KGrF3NNXOuPcpTCedoYQRro64svF+2oyOepw1ozj+6gIp0E2dRTv65gVaB5Ke7RGeGjmjDPqAgizHDyFI9RccxYBZimzEhMq1npFbA+YQnR3QiRoGJlM5iCJogoC3XZB4q8OvviV9WbiMSGvhPUMkHCxz+UEFI4xVIKKqsTnaN0M+mg+us+2FpU1ZNG6uHtgifNj7VUKuBfTqfI/yvhEh11CM35TQ3mmdL24Pnly8/F2qv2Zs92OCcCcnI3m0/U9hfFbUS8U1tCyh6VdSVWyPJtLVp/GFVZ5FFUeUoqlEAgwVf88CL/10S8Ld9vc4StVdrrG5OlUkDhZkhKKSWjAY2usZZ8uKvehAKMTPML2bGZN78RQ2hcVUB30N4eJANindceoFEvAhUM/iNizeQOYwQt4QR5VvSSk8Xg9Ql34uCZjU1xAhSQyrJN9v9DJEPwPH+UQUMduEfUgBd/N2xh2V8e4nCf+Y1Ie/Y12unQzPE3AOZbAzEdT3kgYBn3yASX/Oi85v8OHFGjNITEzoh8uut7gXSr9ceIRDI78z/Shak+GTlNKWhXdAirxAIWfPmO0Tiv+9kE1lHbYIwRWZqFtbKS4RilZ0L3P1E7yLw6E9fWEqeTp++A2c+eUERnQrWtiOurWBpHBlZ2YeluA2wqvW661LOCRbI5Ww4uoQNlVOB3vqfjb74d1wGUckf+HG2OI0Vyr+Jf+Q+6eBMCYl/2gkLnMF2zVxxlXFXxdBYwI+f2nCptoh1/6XzX5L9wI+mYCGC2f3/vfdFqVughNxNFYpOkpLXJJTawwKiohbZe0aPm1Cezhwq9NLXvwExWFseZ1Me/ua1mkvEw9gScA+F5iUUE8MEFu1vPlTynPkjHK94jl00QBen+2BFsTZz/TyQl1Ch8e8D6eJQ5N7TIPlf7fvnuOLXYsVmJuFzO8NvxNvxKE5LJH7/WVCw59mVQvKN+88Or8NT0M5ou0Fc/hmKSkmdG+XIXmYvZirevHTpuyYYczrmonhsC2JnMPSSYOQon/rLuXkCU0JywlRsUPk+6OqUK9UOj6mOZ5H/9u4hYWlTZVVGgl4kawBeuGnSIjAwNXLRoC9LuTI2gfp0dTtLbZXTaHmb1yt2IYUFxWR0RFwMvVGBuiqePUpoJ/kW6Sq74XUO60i6vCh1HDHJHoSRZayzfM3gBKZT7ak9lKKp7RhDNikbk/afTPQbLiDTy7G0VYYH0my0AwWjDF1WWWVZf+loSX9JZTyrWG31lHVnr+Da0TMIVLnz3dwKVyRiKTdk+WK9GavYdoLJjnaSNkcYRPfid99dxuQ9+vh3Ygh5/CcyDRkuagq1lTcmw22GLquB4/vinbx7VCJ0PDTj8doWNLvHpLkFY4LerMawr1bTaeU0c/9mE1L3Za58Rah7Eay66jU5VdtAuZn8OUSK3JkMXze4iGVoIzxDcAKUR29Aa08V//vfCQLtp4dfjq6fj746WsQYzqjORROeeOFJspBQktWftkK8hRZc+6l3z/LSK8OV6Qcq1i7u2x47q7tY3uTYNd51Omdh79H8nu7snXWthcd6R/YUJbsuOKZHfUcFbObK+1SbUgE+FmWnS5/eN0gkPHpzI5lMOB+CWcteANmmrNK6wimpP75a3xLN6Sp0mEYTtQPZDuGS7dMw5f+nInR4NfANINldpouyv40ooO9nf6Am00rl1NalV2U4tprH1M+4GbKC2iq4PFR6rDRWWpsIpKe1hZvbqnrdAyrw27dHPhtSghw726G1WdRfMHBcas7yDmDRpfvvk0l3l/5OYqKeJgkY1w/L91+hcFd6EVTS9uv+ErvXYwgohNpIYdTnZ2Hv3acQX5n+g8S03M3j0a+dp599HuKMZqdQiUfufvVGoPjgQbZUHS0M+/1A0Z2/IphidAO2p5p9sfMKjTiTfoOjwEbxMWyxCh5mhlL2YE6QLkILSL+8lmYySLmbyXfof9Mn0ZIiEoOzQkG1Jsr35EfDpyw4lQD6jnnlq4NMwQcSnEb63a8Xr1STKdefyJtUkr8dugmm1r/RynyT+qaT8VfsNIpBJ9aQiYw9bDJckEVqVFxh18EqNONExB03457CpaILx8rGfyTgz33oUB2voFJeYqoS7LWfA7g1UiFfk+aXVzE9iBJkFaoU6UOw0zQ5ottWTghZg2rGJlHlSACRigzkTbcl12bFy7eYuyttI26Xe2S4cl9mVWyZtiaW0dPrVqid3ox6vkXx+xeHhaVN1TUZlfQieSNQ+sllnVHIXkmeqM4QIsolFO3BPZDxXXmEvlVvO1ZCcgcvpy5hXMbOr1RTU8Ph1BexcyyAIkIfk2CdZ1PfvppGKBsOzntkZXCGJcn3ZmuiGTmGjmBDfeIXT+o8wYP5RMLH8uh1hlz8wDB+HDOKnJQsL+JSDauEIyXt1e6knqr5ZCXDwANgGzC5F8WTRnKRdETB/6/37UURYrEHs7/A1C0Tv9GNQe6vzzN4l1PmjoI08h9fbpGW57cJglmaUDr/D0tmiSQ6Fcq1VFbk9QnzLUlWND3Hc5/OxQiTAn7zKd+BzlvZG2CzXaBgZOpO96D2ookNZ6++A2hs75NfTbHrvLZQZWjxyxAV+xiSyBVFLQlvIuou1iqhaV09Ob1rs7PHXjjV3pXdKAn/RsDXEgLwLG2COrRK+toT70qDdhSeLnwv9yneF9D6TLe3V1SfnmHIFqIimBjKz5bTq+g7o/2d9mlv2LysOjmZFdjxb+YT9Q2zJXm1CovRiBdTBSKuBxN04WcIa3DrMEuQ7UA/YqVCIcplM3BE8tauNG2xSiYPuWxJda7ABZ8ZZUAb8yQ43FJ0Az1LCR6vfNbrG4eERAeA2VX2Ngv89yCJQmUtcGndSrtwBHmeqPz31heVjllSMaEC11AueT6bHxdjSqFj9JIYTFr6zS1g+C5OiAVtfX6W8LeArlpazYoS2YEpY31ZVl+R3drfVL48I+Af11dETF2NDt5V6c8iyXtWN0sdCObb5Y9++yXwY/Ko2OPwDLQz/WWBvSrhSTz2JJEeVaQN22JePxNHkKtY+gdI7nUd8gzSWH4BPlfDz4GizQeAZeBlnu7gDiqNQq4rFSsyoxZLCbcpLZoxXBJboMrObpQHHIY6n2SWzW/evFmIAZmbLTWRYIO1XdUJG0uOZ6/uTzw+XMgbtXSHaxtdQwqn/C6Dmlh1LpNgINgq3uaLnroAZr0A48XPA75LWpWDiqH200A2ra/xu1febP/6g92/ZscIKEuVILJXgsLaT2oqc08jiR//wMGaygdu2benao2bJG0iFF6hao/vgYgHhV7jASpkT/VnPObcTFGqNnObxWg2XdIS66ciYqhb6kcKXieBP1nRpta+vfbn8D2Wi4rrdOwWknnfB3RKxtfcxoIr4vozYhTWHoZ2qcLML02vGUS3GPRLVTerSCCZjJqPsZwUpsJEJlW9xQsCjUleml7xMIBdSk/Qi0pxVMxAXr8tBTIeRDj+P1rOv5nUE7wLNvnQDPmq7Oxe0umNGymnf/taRHr6MBP7xp0KJnho9J/RQyDxs6+6vnlIRlm/a6aRVv9jIu4kkQ4qLfascyAJ/s4FUUHUI0iQQpgsezqxnEwJ/akDQf/WUys4RNyf208B4k9O7ZNSzjNs5LJa3XUHZ6kQuawYeOFKHnCnf2Y0Bt5kvsO+wzwO9pPzPncfRkwi2YVp1F2yzbDEi5PW7kjvjua35VRXzqytPGmOEzZ9zE5pTveYC0UW8DXRmWdeotNuMlrZ8F0HzSFoofCUjRFBBRHY5UIFAuTDV5v+Dkp5jbkZc0OPnLR7yRuky3P7K8qGjJHcTlVxyLjIo2VV/HQVj10GCo0JUcCS59cWMxKacOa2ttEdwea8PgVZ9y8VvHjpk8f5XKwr3aG6Ogr7VXp2wuwMazI591hCDnhvWi3g3Wyb/UcgEhbYBAJVq4EWwUYBH2cIiwc5dBlQlcJ+yKE96L6MF9x9cUH+iG6a5Wzca7XaZBDlF5fvhD+Z1SQM5aUlsnN1iZCtXTvMmwR/tj9Bk92t9DG0aR75CSSDs3+gS8R7JeK5VN4RWV1kCj6EsOhZW/amjEDeiCzpzm9zWsyRKcu74n2Y5FmQT/KJS6jSqoMFeesTXA/LrrjDIW+gZ7eRouwUmDFRdM1s3+ISUkYb8GxlMVwkOcEiPE0lF6FKcDVE4Gqe7IMbw0Tiau8bTPJ76NKxqwModBH1BDPtzZdhiPA0PXc9zPR8uMZc036yItfT+gSaksImHS17k6P18H7FY1ceWSEPpM0W9/fUzjjmpYGCPnFFUWbS7nDWLSyY47tlLtR1DZx5FKR8qqW57ToIte+1WSjxbymFvvL0hXs3yJj/Kt5OgzwoH9wKfPDgOtbImSN80c3l+v5xqd52PA56ApdTl9Av4+ZXqqHYOgoTEPr/ZMwuT8afiM0HBbhbWPtWwjOWPsFFJgmNwsNTm005BYVHqXin1ZO1FYUmnKN5UhenEa7QvzwfI6IlNBEeUYrZiJhKXWTOSm2BbKqw3O2wVis0GCT1yaD7kaA90/DSVLUXqjZ/zcL1jZA5lNPM+rP0/XNkBq9CeI6eBIzVTlUp5ukFsn0mrP5pofcOeykejV3OMy8epWN1zDLQ6UmvRxiPHyOcJnFoPb7b7JXL6JPUhXiZdEKEMSZ6r4jbkbe5LVRnHOKgwxTvRgiFtQ/Sf+KMBgrRAmYc9Pjsy5FrqBskAf7fdMYN+hoha20JncLS2fq7lkU26H3VR4qWLA5cGGjIPF+/e9n0nprzGcKcClRIZUPZuEgHPYDlLTgXX7bK/0Sy3LgkGm9VWSKrvYvGQweBxkX3vuCS7zBOPQPyv3ab+dXvyrM4GGT8vVmPc4enYod6Vb2ZS9H6eHl+xRgHBxZ5/MdcZXkj0kNSfZY5PJX1rmgfNipP4BWVQLKqAxsuPWSMSy+LSYQjKIp8WoLCwjDWnwviTHiKz5aVUGdmV/HsOdLy3G1fKQt1lYQGUkYb8WxZDHZKXmMRnjk+hw9FBH9Mgyjv971HpHyEfvHeGI3nY4WVAdMLdhol9lU6CJZd/v2j8xAllfg6QHi8HYP9aAvIzF7q5rhoL9NyGuVeuzqRYdIlAo5mhTW7RurMV8TTwSb6d5XLWZzO+gZh1mMmbiHtZ/o7u4ihkvWVi+jDih9f+P9q8qkV1jUPP0HRCo/b9eJtWIb8W2BFRq6N6M60hwYVEpub69/w8E5aHQVo9f14igBgg+WJ8nvB9ef8nLRZ+LSsVcUnbup4HRTi5upNSL/HQ5bamUbREuD9jobQR+3ttjxHy2kU+rI10XSVxP1Zgm8x10p9edpYmkbkfLyUA2S3HBOfsUYAr1+iPcpPdWxR6nqI1OUX4A8xYxj5o0mAIds3vM8YmN7mxqTyX3+klYHm3Ppv8FEhtBonrsKX8A9oJIpQdqDAPZrtGF6EwvaDnAfZ9JoXOSQCWqcZ9dxVMj9Cpc0ES1GIxtaaYaBKkyFFYCGqq/EjBidzPd9ft3i0cp0pcmXQ3yp6nvW47kOOu6dY4qpEnMVVovBJIwXh1pqa0C/hmpAYCMuUVyMuYBtQ+F4xwgOfSwaR2zABRKbjXHjQUMz8OJMMXXvwCh2Wfr2Eznrsc8inyylaMFi6N6NuwXn9fLxtgOuxp+ZzpskIHEQtav6EQRUDBB0KZVF67u48cbzYGDEO+olPUkRjuhzWKekS8nhn6FJsQ5ruz5JevVMvhX9rVSFV9alYVI/PIlFk4fIHvEu2Xy7Bd1Nm6dsJIQGegmEXDbsiPcBVoSz7w4bvhx6FwA4/KQa2FVK090CaGdG3lLjzsFMksx170AFqoA6Agq6WQpYIY8sezv8ySdYddyuUj+ifZacUuAds2aiKFfXVPSHkq2s5EI3ZO/ZgK4TT8pFaOQeGVCSXsFrOwt1TDJmyDzxHF0A5htMogy3nDG2pyJPFB2pJOG0Zo17Oyb9SkScr1qaVfRV5FJpW9SA9lP0k5/BWKpJLEHuy6Kf+CqflHdFyDvulIk8WVJNbz8WXVAKP4gm0L0Q2xqa/FwRSkVwCX85C6inmPl5nKp77jXFDC/yNEWZDf/UhqciTBTeR7zSfTpbfKUpEEBXEO1sUJS8pRnrr/PHHDL2/whAritF196bQk8U1an867d+fbDTOTV2RE+s0ZhgADu4RlCDhcaBijkouRt9y4IQSj2xKtgepKkEq8ADWOSLJOoNbIOho9Sg4CUUIiyI/p+3C36FdAHd0VYsJzo+QqsXoDnE9wmuJHTLQS/w41vY/SQt9ajseARlkH69Yy7BIa2v3e2AWmTz64HU0CewWwLtshVP47dr3gcm3Z5TMyMbZ/ggSiIdcaiLVsn6U0usJUWDAhOzJjoSaUJd1KjCh9D/Hyb9wTYYZLQKm+vwtjd+Sr+B+g1Vk5nUgMHtp3Ybux/NTCLEA+kFUzHLflNZCV8vtnU1m8sfZxgAJxENOXoxUy/wxpdcTgh+BmQ+qb3NU5Zq+tRXQWq6W1loUzolWbhvQCtPwZRR/35W0lcCBT+A1ZofMdsDLxbJ1GaqHTC654G8kIQCJw+Gn7157a7n9V7bYgDCw+xtqzEV6rGpqmd1vWeVOAjhjxwiqmBNx6ig9q8AFh6J1mDIxniDkMFkMVBlcRYerYtYpi3PtIGnlXNAKueUBL9q3KiFkPUK/QvEKYOnqisdr7BwLVa55otcE2yF/1IWFKWyyZnDklEH7wTQqdzSKHuWTVgylfQoDrij3Vs846XosbJQX3otdOyfRv3CySd62OuxwMlvGawLtjr6DUUbfEtjxeDQVpgehmhVp+7DaKyGrFlfpp9D5uJqdydkL2e5ZVG38einuVQ6vDrKpyiNUKk42y6CY8H0SK1NRROshXM4/JmNW7Egdj6634Dya8ardy6z6sysJsej7bFEvTDugisnywV041yj69QFCHkkWH2dFQp6rsTMFFJOhiEWiiM7DKQBuzWdcUij+q1ltt6F4NDFuvvUXVput/kAXk9BmsE5+WG3FgS6GkBBTT+JCXZI2RBCsTfkzljbET7NxMPLbICV0oVme6BxUv7n7XJq0uW2zvJls0wn03SZmrTZhshRwGazIb7xOJgfCp0YtXao4qpSyNEssh0thRRDbsBG7PUuW7zYpaxLsJrgMVuQ3mpPJgfCpKSu1JhBYKWZhs1hwuBRWBBEuNeSzRZphrBpZN8tRxZhwEoiPSPezDPaH3AoldbsXtqqXVAJe9lvrGee6FnERBAbV/RjMohbRthA7L4/UFFQO3ZRNkAkOQvAjiDEpSRkCM3VxFfb+YC4UAX26Q1HQhOZQDLZwonu8WqjCxuAoC0WTMCMw6kMtWH8JXMTKYN6nUa92CfX3Ypo+1NmibgW1Wswj3II8kr4qaLPvlbRQE71izSY04EDJisoE3GuAui3mIkZp0pdkI7eo9nPFFjUbKNOoIlYi+9qib0whyrBpejkbNpn1xNiubTVyyMmLjIwLt45XE1EZkbrGGWGdRh3otcGCkoxLXEDdLtQroZaKG4uSVYai4dO0aXrd/0Fpjdati2H/sLolJPKj9hfRpvQf99kkD2oeZ5w7mkjYp3ZVMVD3krF5SYiUIptjzpZIFdZUHqhF4sSFjnFnO25TsHDwCIhIQGQUVBAaGB0DEwsbBxcPn4CQiJiElIycgpKKmoaWjv6FDc4+e5lkMMtkkSVbDqtcefIVKGRjV8TBycXNw8vHLyAoJCwiKqZYXIlSZcolVKhUpVqNWnXqJZ1QIky4Fhmei5AgVp5beGJMCZXqg4/iZYoiNOe9fLd99skXxe7p0uE+P43WY3pVgOu69evRq88Lgd4wYNADQX6QbMyIUcG+9kY0lnYLdOm00B7H9Vi04XfjAf0GDfnKWaNGjFls3JOKXDFh0jWvvdVoXLkKE2ZNqlSlVh2RajXEIt3Rqk1zNcRl/AM3OaeumlTxB2cBAA==) format("woff2")}
:root{--bg:#f6f1e7;--nav:#0d1015;--ink:#ece7dc;--mute:#a9a59b;--amber:#e8a33d;--line:#262b34;--mono:ui-monospace,SFMono-Regular,Menlo,monospace}
*{box-sizing:border-box}html,body{height:100%;margin:0}
body{background:var(--bg);color:#0d1015;font:15px/1.5 Inter,system-ui,-apple-system,sans-serif;display:flex}
nav{width:300px;flex:none;background:var(--nav);color:var(--ink);display:flex;flex-direction:column;height:100%}
.brand{padding:22px 20px 14px}
.brand .mark{display:flex;gap:12px;align-items:center}
.brand b{font:600 28px Fraunces,Georgia,serif;letter-spacing:-.01em}
.brand small{display:block;color:var(--mute);font:600 11px var(--mono);letter-spacing:.12em;text-transform:uppercase;margin-top:8px}
.hand{font:26px "Gochi Hand","Bradley Hand",cursive;color:var(--ink);margin:10px 20px 4px;transform:rotate(-2deg);display:inline-block}
.hand span{background:linear-gradient(transparent 58%,rgba(232,163,61,.55) 58% 90%,transparent 90%);padding:0 .2em}
.search{padding:10px 16px 12px}
.search input{width:100%;background:#161a21;color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:10px 12px;font:inherit}
.menu{overflow:auto;flex:1;padding:4px 0 24px}
.grp{padding:20px 20px 6px;font:600 11px var(--mono);letter-spacing:.16em;text-transform:uppercase;color:var(--amber)}
.menu a{display:block;padding:9px 20px;color:var(--ink);text-decoration:none;border-left:3px solid transparent;min-height:40px}
.menu a:hover{background:#161a21}.menu a.on{background:#161a21;border-left-color:var(--amber);color:#fff}
main{flex:1;min-width:0;height:100%;display:flex;flex-direction:column}
.bar{display:none;align-items:center;gap:10px;padding:8px 12px;border-bottom:1px solid #d8cdb6;background:var(--bg)}
.bar button{background:#b8680f;color:#fff;border:0;border-radius:8px;padding:9px 13px;font-weight:600;min-height:44px}
.bar span{font:600 18px Fraunces,Georgia,serif}
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
  <div><b>Nury</b></div></div>
  <small>An AI Crisis Response Agent</small></div>
 <div class="hand"><span>start anywhere</span></div>
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
