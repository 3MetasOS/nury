"""Build static/how-it-was-built.html from documents/product/HOW_IT_WAS_BUILT.md.
Run from code/:  python3 -m app.build_docs
Needs python-markdown at BUILD time only. The server stays dependency-free: it serves the committed output.
Two live markers stay live: <!--LIVE:RULES--> and <!--LIVE:PLAYBOOKS--> are filled in the browser from /api/rules and /api/playbook/<id>.
<!--LIVE:SCORECARD--> is dropped: the page quotes no pass rate (the source says so)."""
import html
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "documents" / "product" / "HOW_IT_WAS_BUILT.md"
OUT = Path(__file__).resolve().parent / "static" / "how-it-was-built.html"
DISCLOSE = "The Jev decision API from TypeSafe is used as typed judges in our evaluation harness and as a run-time draft classifier; disclosed as third-party technology per the rules."
NOTE = "Nury saves approved cases, with the names you typed, so you can come back to them. There is no sign-in yet: anyone who can open this app can open the saved cases. Nury sends nothing to the family. Share only what the family has agreed to share."
STATUS = {"BUILT, live": "built-live", "BUILT, offline": "built-off", "IN PROGRESS": "inprog", "PLANNED": "planned", "NOT BUILT": "notbuilt"}

FLOW = [("Intake", "The pastor types what the family said."), ("Protect names", "The pastor picks which names to hide. Names become tokens."),
        ("Write", "Claude Sonnet 4.6, through Gloo AI Studio's guarded endpoint."), ("Named checks", "Plain code: the stage's rules and the safety floor."),
        ("Jev gate", "Jev classifies the draft with yes or no questions. IN PROGRESS."), ("Try again", "A failure sends back the reasons, never the draft. Up to 3 tries, then the work goes to the pastor."),
        ("Approval gate", "The pastor sees only a draft that passed. Approve, Edit or Stop."), ("Package", "Every approved stage. The pastor shares it by hand."), ("Save a case", "Optional. Linked pages, a next-steps map, versions.")]


def slug(value, sep="-"):
    v = re.sub(r"[^a-z0-9]+", sep, value.lower()).strip(sep)
    return v or "section"


def flow_html():
    li = "".join(f'<li><b>{html.escape(t)}</b><span>{html.escape(d)}</span></li>' for t, d in FLOW)
    return f'<ol class="pipe" aria-label="The pipeline, step by step">{li}</ol>'


def build():
    md = SRC.read_text(encoding="utf-8")
    md = re.sub(r"## Contents\n.*?(?=\n## 1\.)", "", md, count=1, flags=re.S)       # the page builds its own contents
    md = md.replace("<!--LIVE:RULES-->", '\n<div class="live" data-live="rules" markdown="0"></div>\n')
    md = md.replace("<!--LIVE:PLAYBOOKS-->", '\n<div class="live" data-live="playbooks" markdown="0"></div>\n')
    md = md.replace("<!--LIVE:SCORECARD-->", "")
    m = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists", "md_in_html"],
                          extension_configs={"toc": {"slugify": slug, "permalink": False, "toc_depth": "2-3"}})
    body = m.convert(md)
    toc = [(t["id"], t["name"], t.get("children", [])) for t in m.toc_tokens[0]["children"]] if m.toc_tokens and m.toc_tokens[0].get("level") == 1 else [(t["id"], t["name"], t.get("children", [])) for t in m.toc_tokens]
    # headings get a deep-link anchor
    body = re.sub(r'<h([23]) id="([^"]+)">(.*?)</h\1>', lambda x: f'<h{x.group(1)} id="{x.group(2)}">{x.group(3)}<a class="anc" href="#{x.group(2)}" aria-label="Link to this section">#</a></h{x.group(1)}>', body)
    # keyboard-reachable scroll regions for tables and code
    body = body.replace("<table>", '<div class="tw" tabindex="0" role="region" aria-label="Table, scrolls sideways if needed"><table>').replace("</table>", "</table></div>")
    body = body.replace("<pre>", '<pre tabindex="0">')
    # status labels become badges (text stays, so screen readers read it)
    parts = re.split(r"(<pre.*?</pre>|<code>.*?</code>)", body, flags=re.S)           # never inside a code block
    for label, cls in STATUS.items():
        parts = [x if i % 2 else re.sub(rf'(?<![\w>])({re.escape(label)})(?![\w])', rf'<span class="st st-{cls}">\1</span>', x) for i, x in enumerate(parts)]
    body = "".join(parts)
    # the first diagram gets a real flow and the text version folds under it
    body = body.replace('<h3 id="the-pipeline">', '<h3 id="the-pipeline">', 1)
    body = re.sub(r'(<h3 id="the-pipeline">.*?</h3>)\s*(<pre[^>]*>.*?</pre>)', lambda x: x.group(1) + flow_html() + '<details class="astext"><summary>The same pipeline as text</summary>' + x.group(2) + '</details>', body, count=1, flags=re.S)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    body = re.sub(r"<h1[^>]*>.*?</h1>", "", body, count=1, flags=re.S)
    tocs = "".join(f'<li><a href="#{i}">{html.escape(n)}</a></li>' for i, n, _ in toc)
    page = TEMPLATE.replace("@@TOC@@", tocs).replace("@@BODY@@", body).replace("@@NOTE@@", html.escape(NOTE)).replace("@@DISCLOSE@@", html.escape(DISCLOSE))
    assert 'data-live="rules"' in page and 'data-live="playbooks"' in page, "live markers lost"
    OUT.write_text(page, encoding="utf-8")
    return len(page), len(toc)


TEMPLATE = (Path(__file__).resolve().parent / "docs_template.html").read_text(encoding="utf-8") if (Path(__file__).resolve().parent / "docs_template.html").is_file() else ""

LOG_SRC = ROOT / "BUILD_LOG.md"
LOG_OUT = Path(__file__).resolve().parent / "static" / "build-log.html"
# anything that looks like a secret, a personal address or a phone number stops the build, and is reported
LEAKS = {"email": re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), "phone": re.compile(r"\(?\b\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b"),
         "key assignment": re.compile(r"\b(?:GLOO|JEV|YVP)_[A-Z_]*(?:KEY|TOKEN)\s*=\s*\S+"), "sk key": re.compile(r"\bsk-[A-Za-z0-9]{10,}"),
         "bearer": re.compile(r"Bearer\s+[A-Za-z0-9._-]{10,}"), "40-char hex": re.compile(r"\b[0-9a-f]{40}\b")}
ALLOWED_LEAKS = {"x@invented.org"}   # an invented example address in an entry about test data


def scan_log(text):
    hits = []
    for name, rx in LEAKS.items():
        for m in rx.finditer(text):
            if m.group(0) not in ALLOWED_LEAKS:
                hits.append((name, m.group(0)[:40]))
    return hits


def build_log():
    text = LOG_SRC.read_text(encoding="utf-8")
    hits = scan_log(text)
    if hits:
        raise SystemExit(f"BUILD_LOG.md looks like it holds a secret or personal data; not published: {hits[:5]}")
    parts = re.split(r"(?m)^## (\d+)\. (.+)$", text)
    entries = []
    for i in range(1, len(parts), 3):
        num, title, body = int(parts[i]), parts[i + 1].strip(), parts[i + 2]
        html_body = markdown.markdown(body.strip(), extensions=["tables", "fenced_code", "sane_lists"])
        html_body = html_body.replace("<table>", '<div class="tw" tabindex="0" role="region" aria-label="Table, scrolls sideways if needed"><table>').replace("</table>", "</table></div>").replace("<pre>", '<pre tabindex="0">')
        m = re.match(r"(\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2})?(?: [A-Z]{3})?)\s+\u2014\s+(.*)$", title)
        when, what = (m.group(1), m.group(2)) if m else ("", title)
        entries.append((num, when, what, html_body))
    entries.sort(key=lambda e: -e[0])
    seen = {}
    ids = []
    for n, *_ in entries:               # BUILD_LOG.md can hold two entries with one number (parallel edits): keep every id unique
        seen[n] = seen.get(n, 0) + 1
        ids.append(f"e{n}" if seen[n] == 1 else f"e{n}-{seen[n]}")
    items = "".join(
        f'<details class="ent" id="{ids[i]}"><summary><span class="num mono">#{n}</span><span class="when mono">{html.escape(w)}</span><span class="what">{html.escape(t)}</span></summary><div class="eb">{b}</div></details>\n'
        for i, (n, w, t, b) in enumerate(entries))
    first = next((e for e in entries if e[0] == 1), None)
    tpl = (Path(__file__).resolve().parent / "log_template.html").read_text(encoding="utf-8")
    page = tpl.replace("@@ENTRIES@@", items).replace("@@COUNT@@", str(len(entries))).replace("@@FIRST@@", html.escape(first[1] if first else ""))
    LOG_OUT.write_text(page, encoding="utf-8")
    return len(page), len(entries)


if __name__ == "__main__":
    n, t = build()
    print(f"wrote {OUT} ({n} bytes, {t} sections)")
    n, e = build_log()
    print(f"wrote {LOG_OUT} ({n} bytes, {e} entries)")
