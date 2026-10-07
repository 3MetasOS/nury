"""The page must not repeat an id, and every id its script uses must exist once.
A repeated id (b-save) made getElementById return the wrong button, so the Package screen's Save did nothing for a real click.
Offline. Run: python3 -m pytest evaluations/tests -q"""
import re
from collections import Counter
from pathlib import Path

STATIC = Path(__file__).resolve().parents[2] / "code" / "app" / "static"


def parts(name):
    s = (STATIC / name).read_text(encoding="utf-8")
    html = re.sub(r"<script>.*?</script>", "", s, flags=re.S)
    js = "\n".join(re.findall(r"<script>(.*?)</script>", s, re.S))
    return html, js


def test_no_duplicate_ids_in_any_page():
    for f in STATIC.glob("*.html"):
        html, _ = parts(f.name)
        dup = [k for k, v in Counter(re.findall(r'\bid="([^"]+)"', html)).items() if v > 1]
        assert not dup, f"{f.name}: duplicate ids {dup}"


def test_every_id_used_by_the_script_exists():
    for f in STATIC.glob("*.html"):
        html, js = parts(f.name)
        ids = set(re.findall(r'\bid="([^"]+)"', html))
        used = set(re.findall(r'\$\("([^"]+)"\)', js)) | set(re.findall(r'getElementById\("([^"]+)"\)', js))
        missing = sorted(u for u in used if u not in ids)
        assert not missing, f"{f.name}: script uses ids that are not in the page: {missing}"


def test_save_buttons_have_different_ids():
    html, _ = parts("index.html")
    assert 'id="b-save"' in html and 'id="b-edit-save"' in html
