"""Build presentation/submission_form.html from SUBMISSION_FORM.md: every field in its own box with a Copy button.
Usage: python3 presentation/build_submission_html.py   (no network, standard library only)"""
import html, re, pathlib
root = pathlib.Path(__file__).parent
src = (root / "SUBMISSION_FORM.md").read_text(encoding="utf-8")
REPO = "https://github.com/3MetasOS/nury"
src = (src.replace("[REPO URL]/blob/main/BUILD_LOG.md", REPO + "/blob/main/BUILD_LOG.md")
          .replace("[REPO URL]", REPO)
          .replace("[APP URL]/about (or the README if the app is not hosted: there is no hosting)", REPO + "#readme"))
cards, title, body, level = [], None, [], 0
def flush():
    global title, body
    if title is not None and any(l.strip() for l in body):
        cards.append((title, "\n".join(body).strip(), level))
    title, body = None, []
for line in src.splitlines():
    m = re.match(r"^(#{1,3})\s+(.*)", line)
    if m and len(m.group(1)) >= 2:
        flush(); title, level = m.group(2), len(m.group(1))
    elif title is not None:
        body.append(line)
flush()
def clean(t):  # plain text for pasting: drop markdown bold and backticks
    t = re.sub(r"\*\*(.*?)\*\*", r"\1", t); t = t.replace("`", "")
    return t
out = []
for t, b, lv in cards:
    b = clean(b)
    sub = [l for l in b.split("\n")]
    out.append(f'<section class="card"><h{lv}>{html.escape(t)}</h{lv}>')
    items = [l[2:] for l in sub if l.startswith("- ")]
    if items and len(items) == len([l for l in sub if l.strip()]):
        for it in items:
            out.append(f'<div class="f"><pre>{html.escape(it)}</pre><button>Copy</button></div>')
    else:
        out.append(f'<div class="f"><pre>{html.escape(b)}</pre><button>Copy</button></div>')
    out.append("</section>")
page = f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nury: submission form, copy and paste</title>
<style>
:root{{--bg:#f7f3ea;--ink:#0d1112;--mut:#5a5546;--card:#fffdf7;--line:#e6dcc6;--amb:#b8680f}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 Inter,system-ui,sans-serif;padding:32px 20px}}
main{{max-width:900px;margin:auto}}h1{{font:600 34px/1.1 Fraunces,Georgia,serif;margin:0 0 6px}}p.s{{color:var(--mut);margin:0 0 24px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:18px 20px;margin:0 0 16px}}
h2,h3{{font:600 20px/1.2 Fraunces,Georgia,serif;margin:0 0 10px}}h3{{font-size:17px}}
.f{{display:flex;gap:12px;align-items:flex-start;margin:0 0 10px}}pre{{flex:1;margin:0;white-space:pre-wrap;word-wrap:break-word;font:15px/1.5 Inter,system-ui,sans-serif;background:#f3ecd9;border-radius:10px;padding:10px 12px}}
button{{flex:none;border:0;border-radius:10px;padding:10px 16px;font-weight:600;background:var(--amb);color:#fff;cursor:pointer;min-height:40px}}button.ok{{background:#2a7a4a}}
</style><main><h1>Nury: submission form</h1><p class="s">Each box is one field. Press Copy, paste into the form. Built from SUBMISSION_FORM.md. The repository link is already filled. Check the 'Fields I could not confirm' box first.</p>
{''.join(out)}
<script>document.querySelectorAll('.f button').forEach(function(b){{b.onclick=function(){{var t=b.previousElementSibling.innerText;
function done(){{b.textContent='Copied';b.className='ok';setTimeout(function(){{b.textContent='Copy';b.className=''}},1400)}}
if(navigator.clipboard&&window.isSecureContext){{navigator.clipboard.writeText(t).then(done)}}else{{var a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();document.execCommand('copy');a.remove();done()}}}}}})</script></main></html>"""
(root / "submission_form.html").write_text(page, encoding="utf-8")
print("wrote", root / "submission_form.html", len(cards), "boxes")
