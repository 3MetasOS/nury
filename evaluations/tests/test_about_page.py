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
