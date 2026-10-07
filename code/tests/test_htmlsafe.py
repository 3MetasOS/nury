"""SEC-21: text pasted into BUILD_LOG.md cannot run in a reader's browser."""
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonet  # noqa: E402,F401

try:
    import markdown  # noqa: F401
    from app import build_docs as bd
    HAVE = True
except ImportError:          # markdown is a docs-build dependency (requirements-dev.txt)
    HAVE = False
from app import htmlsafe  # noqa: E402

HOSTILE = ('<p>a <script>alert(1)</script>b <img src=x onerror=alert(1)> <a href="javascript:alert(1)" onclick="x()">l</a> '
           '<a href="https://example.org/a" onmouseover="x()">ok</a> <iframe src="http://evil"></iframe> <svg onload="x()"></svg></p>')


class Sanitizer(unittest.TestCase):
    def test_nothing_that_runs_survives(self):
        out = htmlsafe.clean(HOSTILE)
        for bad in ("<script", "alert(1)</", "<img", "javascript:", "onclick", "onmouseover", "<iframe", "<svg", "onload"):
            self.assertNotIn(bad, out.lower().replace("&lt;img src=x onerror=alert(1)&gt;", ""), bad)
        self.assertIn('<a href="https://example.org/a" rel="noopener noreferrer">ok</a>', out)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", out)           # an unknown tag is shown as plain text

    def test_ordinary_markup_and_angle_text_are_kept(self):
        src = '<h3>T</h3><table><thead><tr><th style="text-align: left;">A</th></tr></thead><tbody><tr><td>x &amp; y</td></tr></tbody></table><pre><code class="language-py">a &lt; b</code></pre><p>jev_&lt;question&gt;</p>'
        self.assertEqual(htmlsafe.clean(src), src)
        self.assertEqual(htmlsafe.clean("<p>jev_<question></p>"), "<p>jev_&lt;question&gt;</p>")


@unittest.skipUnless(HAVE, "needs Markdown (code/requirements-dev.txt)")
class BuiltLog(unittest.TestCase):
    def test_a_script_tag_pasted_into_an_entry_stays_inert_in_the_built_page(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "BUILD_LOG.md"
            src.write_text("# Log\n\n## 1. 2026-10-07 — A test entry\n\nHello <script>alert('x')</script> and <img src=x onerror=alert(2)>.\n\n- item <b onclick=\"y()\">bold</b>\n", encoding="utf-8")
            out = Path(d) / "build-log.html"
            old = (bd.LOG_SRC, bd.LOG_OUT)
            bd.LOG_SRC, bd.LOG_OUT = src, out
            try:
                bd.build_log()
            finally:
                bd.LOG_SRC, bd.LOG_OUT = old
            page = out.read_text(encoding="utf-8")
            body = page[page.index('class="ent"'):]
            self.assertNotIn("alert('x')", body)
            self.assertNotRegex(body, r"<img[^>]*onerror")
            self.assertNotIn("onclick", body)
            self.assertIn("&lt;img src=x onerror=alert(2)&gt;", body)
            tpl = (Path(bd.__file__).parent / 'log_template.html').read_text(encoding='utf-8')
            self.assertEqual(len(re.findall(r'<script', page)), len(re.findall(r'<script', tpl)))      # only the template's own scripts


if __name__ == "__main__":
    unittest.main()
