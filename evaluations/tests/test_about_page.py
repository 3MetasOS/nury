"""The About page: built from ABOUT_PAGE.md, with Juan's memorial verbatim and a photo slot that shows only when the file exists. Offline."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "code"
sys.path.insert(0, str(ROOT))
from app import build_docs  # noqa: E402

STATIC = ROOT / "app" / "static"
LINES = ["Nury is named for my aunt, Nury Peláez.", "She served her church for 83 years, in the small things and the big ones,",
         "always with a smile, always with Jesus in her heart.", "She passed away a month ago. This is for her."]


def test_the_memorial_is_juans_words_verbatim_and_flagged_as_pending():
    d = json.loads((ROOT / "app" / "about_data.json").read_text(encoding="utf-8"))
    assert d["memorial"]["lines"] == LINES and d["memorial"]["pending_juan_ok"] is True and d["memorial"]["visible"] is True
    page = (STATIC / "about.html").read_text(encoding="utf-8")
    for l in LINES:
        assert f"<p>{l}</p>" in page
    assert "Pending his final OK" in page


def test_the_photo_slot_has_no_image_unless_the_file_exists():
    page = (STATIC / "about.html").read_text(encoding="utf-8")
    assert '<figure id="mem-photo"><img alt="Nury Pel' in page            # the image has no src until the script finds the file
    assert "img src=" not in page and "display:none" in page and 'i.src="/memorial/nury.jpg"' in page


def test_the_page_is_current_with_its_source(tmp_path):
    out = tmp_path / "about.html"
    build_docs.build_about(out=out)
    assert out.read_text(encoding="utf-8") == (STATIC / "about.html").read_text(encoding="utf-8"), "about.html is stale: run python3 -m app.build_docs"


def test_sections_come_from_the_source_and_the_blocks_are_label_plus_text():
    page = (STATIC / "about.html").read_text(encoding="utf-8")
    for h in ("What Nury is", "How it was made", "Where it came from", "Credits"):
        assert f">{h}</h2>" in page
    assert page.count('class="blk"') >= 6 and "Writer" in page and "MEMORIAL BLOCK" not in page


def test_the_footer_links_to_about_twice():
    js = (STATIC / "shell.js").read_text(encoding="utf-8")
    assert '<a class="fabout" href="/about"' in js and ">About</a>" in js and "More about how it was made" in js and 'href="/about"' in js


def test_the_saved_cases_notice_lives_only_in_the_app_page_and_not_on_document_pages():
    for f in list(STATIC.glob("*.html")) + [ROOT / "app" / n for n in ("docs_template.html", "log_template.html", "standards_template.html", "about_template.html")]:
        if f.name == "index.html":
            continue
        assert "data-consent" not in f.read_text(encoding="utf-8"), f.name


DOC_PAGES = {"how-it-was-built.html", "build-log.html", "standards.html", "economics.html", "pattern.html", "what-did-not-work.html",
             "run-your-own.html", "self-improvement.html", "improve.html"}


def _visible_html(s):
    import re
    s = re.sub(r"(?s)<(script|style|code|pre)\b.*?</\1>|<!--.*?-->", " ", s)
    return re.sub(r"<[^>]+>", " ", s)


def test_no_page_says_package_in_visible_text():
    """'Package' is an internal word: the app says 'case'. App pages and the text inside their scripts are scanned; document pages that quote code are not."""
    import re
    word = re.compile(r"\b[Pp]ackages?\b")
    bad = []
    for f in sorted(STATIC.glob("*.html")):
        s = f.read_text(encoding="utf-8")
        if f.name not in DOC_PAGES and word.search(_visible_html(s)):
            bad.append(f.name)
        scripts = re.findall(r"(?s)<script\b[^>]*>(.*?)</script>", s) if f.name not in DOC_PAGES else []
        for js in scripts:
            for lit in re.findall(r'"((?:[^"\\\n]|\\.)*)"|`((?:[^`\\]|\\.)*)`', re.sub(r"(?m)^\s*//.*$|/\*.*?\*/", "", js, flags=re.S)):
                if word.search(lit[0] or lit[1]):
                    bad.append(f"{f.name}: {(lit[0] or lit[1])[:50]}")
    for n in ("diagrams.js", "shell.js", "final.js", "case-print.js"):
        js = re.sub(r"(?m)^\s*//.*$|/\*.*?\*/", "", (STATIC / n).read_text(encoding="utf-8"), flags=re.S)
        js = re.sub(r"(?m)\s//.*$", "", js)
        for lit in re.findall(r'"((?:[^"\\\n]|\\.)*)"|`((?:[^`\\]|\\.)*)`', js):
            if word.search(lit[0] or lit[1]):
                bad.append(f"{n}: {(lit[0] or lit[1])[:50]}")
    assert not bad, bad


def test_what_did_not_work_page_is_cards_with_filters_and_anchors(tmp_path):
    import re
    page = (STATIC / "what-did-not-work.html").read_text(encoding="utf-8")
    n = page.count('class="item"')
    assert n >= 10 and page.count('class="row nk"') == n, "each item has a distinct Not known row"
    assert all(f'id="item-{i}"' in page for i in range(1, n + 1)), "anchors #item-1 ..."
    assert page.count('class="fchip"') == 4 and "All" in page and "The product" in page and "The evaluation" in page and ">Us<" in page
    assert 'aria-expanded="false"' in page and "Written 20" not in page
    assert page.count('class="badge"') == n and 'data-note="what we tried that failed, and what we do not know yet"' in page
    out = tmp_path / "w.html"
    build_docs.build_wdnw(out=out)
    assert out.read_text(encoding="utf-8") == page, "what-did-not-work.html is stale: run python3 -m app.build_docs"


def test_pattern_page_is_cards_with_a_sequence_and_the_honest_list(tmp_path):
    page = (STATIC / "pattern.html").read_text(encoding="utf-8")
    assert 'data-note="the part you can reuse"' in page and 'class="pull"' in page and "Written 20" not in page
    assert page.count('class="stn"') == 5 and all(f'id="part-{i}"' in page and f'href="#part-{i}"' in page for i in range(1, 6))
    assert page.count('class="card nope"') >= 5 and page.count('class="card idea"') == 3 and "Idea, not built" in page
    assert "Use it when" in page and "Do not use it when" in page and page.count('class="chip"') >= 10
    out = tmp_path / "p.html"
    build_docs.build_pattern(out=out)
    assert out.read_text(encoding="utf-8") == page, "pattern.html is stale: run python3 -m app.build_docs"
