"""Build static/how-it-was-built.html from documents/product/HOW_IT_WAS_BUILT.md.
Run from code/:  python3 -m app.build_docs
Needs python-markdown at BUILD time only. The server stays dependency-free: it serves the committed output.
Two live markers stay live: <!--LIVE:RULES--> and <!--LIVE:PLAYBOOKS--> are filled in the browser from /api/rules and /api/playbook/<id>.
<!--LIVE:SCORECARD--> is dropped: the page quotes no pass rate (the source says so)."""
import html
import json
import re
from pathlib import Path

import markdown

from app import htmlsafe

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


def _box(x, y, w, h, title, sub, cls=""):
    return (f'<g class="bx {cls}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/><text x="{x + 14}" y="{y + 24}" class="bt">{html.escape(title)}</text>'
            f'<text x="{x + 14}" y="{y + 43}" class="bs">{html.escape(sub)}</text></g>')


def _arrow(x, y1, y2):
    return f'<path d="M{x} {y1} V{y2 - 6}" class="ba"/><path d="M{x - 5} {y2 - 12} L{x} {y2 - 5} L{x + 5} {y2 - 12}" class="ba"/>'


def arch_svg():
    """The architecture in one picture: pastor -> privacy layer -> Claude via Gloo -> named rules -> Jev -> (up to 3 tries) -> pastor gate -> audit. Vertical, readable at 390 px."""
    steps = [("The pastor", "Types what the family said. Picks the names to hide.", ""), ("Privacy layer", "Names, phones, emails, addresses and dates become tokens.", ""),
             ("Claude Sonnet 4.6, through Gloo", "Writes the draft from the vetted sources only.", "hi"), ("Named rules", "Plain code: the stage's rules and the safety floor.", ""),
             ("Jev gate", "Classifies the draft with yes or no questions.", ""), ("The pastor's gate", "Approve, Edit or Stop. Only a draft that passed is shown.", "hi"),
             ("Audit log", "Every check and every gate, with reasons only.", "")]
    W, BH, GAP = 560, 56, 30
    H = len(steps) * (BH + GAP) - GAP + 8
    out = [f'<svg class="adg" viewBox="0 0 {W} {H}" role="img" aria-label="Architecture: the pastor, the privacy layer, Claude through Gloo, named rules, the Jev gate, then the pastor\'s gate and the audit log. A draft that fails a rule or Jev goes back to Claude with the reasons, up to three tries, then the work goes to the pastor.">']
    for i, (t, sub, cls) in enumerate(steps):
        y = 4 + i * (BH + GAP)
        out.append(_box(20, y, 400, BH, t, sub, cls))
        if i < len(steps) - 1:
            out.append(_arrow(220, y + BH, y + BH + GAP))
    # the retry loop: from Jev (index 4) back up to Claude (index 2)
    y_j, y_c = 4 + 4 * (BH + GAP) + BH / 2, 4 + 2 * (BH + GAP) + BH / 2
    out.append(f'<path d="M420 {y_j} C 520 {y_j}, 520 {y_c}, 426 {y_c}" class="bl"/><path d="M434 {y_c - 6} L424 {y_c} L434 {y_c + 6}" class="bl"/>')
    out.append(f'<text x="446" y="{(y_j + y_c) / 2 - 6}" class="bh">fails? back with</text><text x="446" y="{(y_j + y_c) / 2 + 14}" class="bh">the reasons,</text><text x="446" y="{(y_j + y_c) / 2 + 34}" class="bh">3 tries</text>')
    out.append("</svg>")
    return "".join(out)


def loop_svg():
    """The self-improvement loop: feedback -> report -> candidate -> test -> a person approves -> release. A person decides; nothing applies itself."""
    steps = [("Feedback", "What the pastor changed, without names."), ("Report", "Counts by crisis and stage."), ("Candidate", "A proposed prompt line, rule, question or scenario."),
             ("Test", "Run against the evaluation set; no regression allowed."), ("A person approves", "Written in the candidate's review file."), ("Release", "A normal commit. Nothing applies itself.")]
    W, BH, GAP = 560, 52, 26
    H = len(steps) * (BH + GAP) - GAP + 8
    out = [f'<svg class="adg" viewBox="0 0 {W} {H}" role="img" aria-label="The self-improvement loop: feedback, report, candidate, test, a person approves, release. Nothing changes without a person approving it.">']
    for i, (t, sub) in enumerate(steps):
        y = 4 + i * (BH + GAP)
        out.append(_box(20, y, 400, BH, t, sub, "hi" if t == "A person approves" else ""))
        if i < len(steps) - 1:
            out.append(_arrow(220, y + BH, y + BH + GAP))
    out.append("</svg>")
    return "".join(out)


def build(out=None):
    md = SRC.read_text(encoding="utf-8")
    md = re.sub(r"## Contents\n.*?(?=\n## 1\.)", "", md, count=1, flags=re.S)       # the page builds its own contents
    short = ""
    ms = re.search(r"<!--\s*in-short\s*-->(.*?)<!--\s*/in-short\s*-->", md, re.S)
    if ms:                                                   # the 'In short' block is a card above the contents, not part of the article
        inner = re.sub(r"(?mi)^(#{1,6} .*|\*\*in short\*\*)\n", "", ms.group(1).strip() + "\n").strip()
        short = '<aside class="inshort" aria-labelledby="inshort-l"><p class="mono" id="inshort-l">In short</p>' + markdown.markdown(inner, extensions=["sane_lists"]) + "</aside>"
        md = md[:ms.start()] + md[ms.end():]
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
    # diagrams: the architecture after the text version of the pipeline, the loop after the learning-loop heading
    if '<details class="astext">' in body:
        i = body.index('<details class="astext">'); j = body.index("</details>", i) + len("</details>")
        body = body[:j] + f'<figure class="fig"><figcaption class="mono">The architecture in one picture</figcaption>{arch_svg()}</figure>' + body[j:]
    mm = re.search(r'<h3 id="[^"]*learning-loop[^"]*">.*?</h3>\s*(<p>.*?</p>)', body, re.S)
    if mm:
        body = body[:mm.end()] + f'<figure class="fig"><figcaption class="mono">The loop, with a person in control</figcaption>{loop_svg()}</figure>' + body[mm.end():]
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    body = re.sub(r"<h1[^>]*>.*?</h1>", "", body, count=1, flags=re.S)
    tocs = "".join(f'<li><a href="#{i}">{html.escape(n)}</a></li>' for i, n, _ in toc)
    page = TEMPLATE.replace("@@INSHORT@@", short).replace("@@TOC@@", tocs).replace("@@BODY@@", body).replace("@@NOTE@@", html.escape(NOTE)).replace("@@DISCLOSE@@", html.escape(DISCLOSE))
    assert 'data-live="rules"' in page and 'data-live="playbooks"' in page, "live markers lost"
    Path(out or OUT).write_text(page, encoding="utf-8")
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


def build_log(out=None):
    text = LOG_SRC.read_text(encoding="utf-8")
    hits = scan_log(text)
    if hits:
        raise SystemExit(f"BUILD_LOG.md looks like it holds a secret or personal data; not published: {hits[:5]}")
    parts = re.split(r"(?m)^## (\d+)\. (.+)$", text)
    entries = []
    for i in range(1, len(parts), 3):
        num, title, body = int(parts[i]), parts[i + 1].strip(), parts[i + 2]
        html_body = htmlsafe.clean(markdown.markdown(body.strip(), extensions=["tables", "fenced_code", "sane_lists"]))   # BUILD_LOG.md is pasted text: keep only document markup
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
    Path(out or LOG_OUT).write_text(page, encoding="utf-8")
    return len(page), len(entries)


STD_SRC = ROOT / "documents" / "product" / "STANDARDS_PAGE.md"
STD_OUT = Path(__file__).resolve().parent / "static" / "standards.html"


def functions_diagram(md):
    """Inline SVG from the six-functions table: function -> where it lives in Nury -> how far it goes. Vertical, readable at 390 px. The table below it is the text alternative."""
    import textwrap
    m = re.search(r"## The six case-management functions.*?\n(\|.*?)(?=\n\n|\Z)", md, re.S)
    rows = []
    for line in (m.group(1).splitlines() if m else []):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3 and not set("".join(cells)) <= set("-: ") and cells[0] != "Function":
            rows.append(cells)
    if not rows:
        return ""
    W, RH = 600, 92
    out = [f'<svg class="fdiag" viewBox="0 0 {W} {RH * len(rows) + 8}" role="img" aria-label="The six case management functions and where Nury covers them: ' +
           "; ".join(f"{html.escape(a)}: {html.escape(c.split('.')[0])}" for a, b, c in rows) + '">']
    for i, (fn, where, how) in enumerate(rows):
        y = i * RH + 8
        kind = "yes" if how.startswith("Yes") else "partly" if how.startswith("Partly") else "barely" if how.startswith("Barely") else "no"
        label = {"yes": "Yes", "partly": "Partly", "barely": "Barely", "no": "Not built"}[kind]
        short = textwrap.wrap(where.split(". ")[0].rstrip("."), 30)[:3]
        out.append(f'<g class="fr {kind}">')
        out.append(f'<rect x="4" y="{y}" width="150" height="56" rx="6" class="fbox"/><text x="16" y="{y + 34}" class="ffn">{html.escape(fn)}</text>')
        out.append(f'<path d="M154 {y + 28} C 178 {y + 24}, 188 {y + 32}, 214 {y + 28} M206 {y + 22} L214 {y + 28} L205 {y + 34}" class="farrow"/>')
        out.append(f'<rect x="218" y="{y}" width="248" height="56" rx="6" class="fbox2"/>')
        for k, ln in enumerate(short):
            out.append(f'<text x="230" y="{y + 22 + k * 15}" class="fwh">{html.escape(ln)}</text>')
        out.append(f'<rect x="480" y="{y + 12}" width="110" height="32" rx="16" class="fpill"/><text x="535" y="{y + 33}" text-anchor="middle" class="fst">{label}</text>')
        out.append("</g>")
    out.append("</svg>")
    return "".join(out)


def build_standards():
    text = STD_SRC.read_text(encoding="utf-8")
    body_md = text.split("\n---\n", 1)[1] if "\n---\n" in text else text
    body_md = re.sub(r"## Closing line for the page\n+", "", body_md)
    m = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"], extension_configs={"toc": {"slugify": slug, "permalink": False, "toc_depth": "2-3"}})
    body = m.convert(body_md)
    toc = [(t["id"], t["name"]) for t in m.toc_tokens]
    body = re.sub(r'<h([23]) id="([^"]+)">(.*?)</h\1>', lambda x: f'<h{x.group(1)} id="{x.group(2)}">{x.group(3)}<a class="anc" href="#{x.group(2)}" aria-label="Link to this section">#</a></h{x.group(1)}>', body)
    body = body.replace("<table>", '<div class="tw" tabindex="0" role="region" aria-label="Table, scrolls sideways if needed"><table>').replace("</table>", "</table></div>")
    diag = functions_diagram(body_md)
    marker = '<h2 id="the-six-case-management-functions-and-the-five-stages">'
    if diag and marker in body:
        i = body.index(marker); j = body.index("</p>", i) + 4
        body = body[:j] + f'<figure class="fig">{diag}<figcaption>Where each function lives in Nury. The table below says the same in words.</figcaption></figure>' + body[j:]
    tocs = "".join(f'<li><a href="#{i}">{html.escape(n)}</a></li>' for i, n in toc)
    tpl = (Path(__file__).resolve().parent / "standards_template.html").read_text(encoding="utf-8")
    page = tpl.replace("@@TITLE@@", "Case management standards").replace("@@DESC@@", "The case management and trauma-informed standards that informed Nury, what it does and does not do, and what we could not verify.").replace("@@TOC@@", tocs).replace("@@BODY@@", body)
    STD_OUT.write_text(page, encoding="utf-8")
    return len(page), len(toc)


SIMPLE_DOCS = [("WHAT_DID_NOT_WORK.md", "what-did-not-work.html", "What did not work", "What we tried that did not work, what happened, what we changed, and what we do not know."),
               ("ECONOMICS.md", "economics.html", "Economics", "What a Nury package costs, where the time goes, and what could break the economics."),
               ("PATTERN.md", "pattern.html", "The pattern", "The approve-gated stage pipeline for high-stakes drafting, and when to reuse it.")]


def build_simple(src_name, out_name, title, desc):
    """A static document page in the shared shell, rendered from documents/product/<src_name>. The page keeps its 'Not known' lines and every number as written."""
    text = (ROOT / "documents" / "product" / src_name).read_text(encoding="utf-8")
    text = re.sub(r"(?m)^# .*\n", "", text, count=1)
    text = re.sub(r"(?m)^Written 20\d\d-.*\n", "", text)
    m = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"], extension_configs={"toc": {"slugify": slug, "permalink": False, "toc_depth": "2-3"}})
    body = m.convert(text)
    toc = [(t["id"], t["name"]) for t in m.toc_tokens]
    body = re.sub(r'<h([23]) id="([^"]+)">(.*?)</h\1>', lambda x: f'<h{x.group(1)} id="{x.group(2)}">{x.group(3)}<a class="anc" href="#{x.group(2)}" aria-label="Link to this section">#</a></h{x.group(1)}>', body)
    body = body.replace("<table>", '<div class="tw" tabindex="0" role="region" aria-label="Table, scrolls sideways if needed"><table>').replace("</table>", "</table></div>")
    tocs = "".join(f'<li><a href="#{i}">{html.escape(n)}</a></li>' for i, n in toc)
    tpl = (Path(__file__).resolve().parent / "standards_template.html").read_text(encoding="utf-8")
    page = (tpl.replace("@@TITLE@@", html.escape(title)).replace("@@DESC@@", html.escape(desc)).replace("@@TOC@@", tocs).replace("@@BODY@@", body))
    (Path(__file__).resolve().parent / "static" / out_name).write_text(page, encoding="utf-8")
    return len(page)


if __name__ == "__main__":
    n, t = build()
    print(f"wrote {OUT} ({n} bytes, {t} sections)")
    n, e = build_log()
    print(f"wrote {LOG_OUT} ({n} bytes, {e} entries)")
    n, t = build_standards()
    print(f"wrote {STD_OUT} ({n} bytes, {t} sections)")
    for a, b, c, d in SIMPLE_DOCS:
        print(f"wrote {b} ({build_simple(a, b, c, d)} bytes)")


ABOUT_SRC = ROOT / "documents" / "product" / "ABOUT_PAGE.md"
ABOUT_OUT = Path(__file__).resolve().parent / "static" / "about.html"
ABOUT_DATA = Path(__file__).resolve().parent / "about_data.json"


def _about_sections(text):
    """Sections of ABOUT_PAGE.md by '## ' heading. 'How it was made' is a list of '- **Label.** text' blocks; the others are prose."""
    out = {}
    for m in re.finditer(r"(?ms)^## (.+?)\n(.*?)(?=^## |\Z)", text):
        out[m.group(1).strip().lower()] = m.group(2).strip()
    return out


def build_about(out=None, src=None, data=None):
    """The About page in the shared shell. Sections come from documents/product/ABOUT_PAGE.md (ninja): What Nury is, How it was made (blocks,
    each '**Label.** text'), Where it came from, Credits. The memorial text and its flag come from about_data.json, verbatim, in the place of the
    'MEMORIAL BLOCK' line. Until the source exists, a short text from the project's own docs stands in."""
    d = json.loads(Path(data or ABOUT_DATA).read_text(encoding="utf-8"))
    src = Path(src or ABOUT_SRC)
    sec = _about_sections(src.read_text(encoding="utf-8")) if src.is_file() else {}
    def md(t):
        return htmlsafe.clean(markdown.markdown(t.strip(), extensions=["sane_lists"]))
    def inline(t):
        h = md(t)
        return re.sub(r"^<p>(.*)</p>$", r"\1", h.strip(), flags=re.S)
    parts = []
    parts.append(f'<section class="sec" aria-labelledby="a-what"><h2 id="a-what">What Nury is</h2>{md(sec.get("what nury is") or d["fallback"]["what"])}</section>')
    def blocks_of(text):
        bl, rest = [], []
        for para in re.split(r"\n{2,}", text or ""):
            m = re.match(r"^\*\*(.+?)\.?\*\*\s*(.*)$", para.strip(), re.S)
            if m:
                bl.append((m.group(1).strip().rstrip("."), m.group(2).strip()))
            elif para.strip():
                rest.append(para.strip())
        return bl, rest
    def grid(bl):
        return '<div class="blocks">' + "".join(f'<div class="blk"><p class="mono">{html.escape(a)}</p><p>{inline(b)}</p></div>' for a, b in bl) + "</div>"
    grow, grow_rest = blocks_of(sec.get("built to grow"))
    if grow:
        parts.append(f'<section class="sec" aria-labelledby="a-grow"><h2 id="a-grow">Built to grow</h2>{grid(grow)}{md(chr(10).join(grow_rest)) if grow_rest else ""}</section>')
    blocks, _rest = blocks_of(sec.get("how it was made"))
    if blocks:
        parts.append(f'<section class="sec" aria-labelledby="a-how"><h2 id="a-how">How it was made</h2>{grid(blocks)}</section>')
    parts.append(f'<section class="sec" aria-labelledby="a-where"><h2 id="a-where">Where it came from</h2>{md(sec.get("where it came from") or d["fallback"]["origin"])}</section>')
    if sec.get("credits"):
        parts.append(f'<section class="sec credits" aria-labelledby="a-cred"><h2 id="a-cred">Credits</h2>{md(sec["credits"])}</section>')
    mem = d.get("memorial") or {}
    memorial = ""
    if mem.get("visible"):
        lines = "".join(f"<p>{html.escape(l)}</p>" for l in mem.get("lines", []))
        memorial = ('<!-- Memorial: Juan\'s words, verbatim. Pending his final OK (about_data.json memorial.visible). -->'
                    '<section class="memorial" aria-label="In memory">'
                    '<svg class="lant" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><use href="/icons.svg#i-mark"/></svg>'
                    f'<blockquote>{lines}</blockquote>'
                    '<figure id="mem-photo"><img alt="Nury Pel\u00e1ez"></figure></section>')
    page = Path(__file__).resolve().parent.joinpath("about_template.html").read_text(encoding="utf-8").replace("@@SECTIONS@@", "".join(parts)).replace("@@MEMORIAL@@", memorial)
    Path(out or ABOUT_OUT).write_text(page, encoding="utf-8")
    return len(page)
