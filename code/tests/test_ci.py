"""CI definition and the key scanner. No network."""
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonet  # noqa: E402,F401
import scan_keys as sk  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
CI = REPO / ".github" / "workflows" / "ci.yml"


class Scanner(unittest.TestCase):
    def test_it_finds_a_literal_key_a_secret_and_a_bearer_token_and_never_prints_the_value(self):
        text = "\n".join(["GLOO_API_KEY=abcdef0123456789abcdef", "x = 'sk-" + "a1b2c3d4e5f6g7h8i9j0k1l2" + "'",
                          "Authorization: Bearer " + "q1w2e3r4t5y6u7i8o9p0a1s2d3f4", "JEV_API_KEY: 'zzzzzzzzzzzzzzzzzzzz1'"])
        kinds = [k for _, k in sk.scan_text(text)]
        self.assertEqual(sorted(kinds), sorted(["a key name assigned a literal value", "an sk- style secret", "a Bearer token", "a key name assigned a literal value"]))
        self.assertNotIn("abcdef0123", str(sk.scan_text(text)))

    def test_placeholders_and_environment_reads_are_allowed(self):
        ok = ["GLOO_API_KEY=your-key-here", 'os.environ["GLOO_API_KEY"]', "JEV_API_KEY=<set>", "NURY: test-jev-key-not-real", "GLOO_API_KEY=${GLOO_API_KEY}",
              'GLOO_API_KEY="test-key-not-real"', "export YVP_APP_KEY=example-value-123456", "Bearer test-jev-key-not-real-xxxxxxxx"]
        for line in ok:
            self.assertEqual(sk.scan_text(line), [], line)

    def test_only_tracked_files_are_scanned_and_the_real_repository_is_clean(self):
        self.assertEqual(sk.scan(), [])
        d = Path(tempfile.mkdtemp())
        try:
            subprocess.run(["git", "init", "-q"], cwd=d, check=True)
            (d / ".gitignore").write_text(".env\n")
            (d / ".env").write_text("GLOO_API_KEY=realrealrealrealreal1\n")                  # ignored, never scanned
            (d / "a.txt").write_text("fine\n")
            subprocess.run(["git", "add", ".gitignore", "a.txt"], cwd=d, check=True)
            self.assertEqual(sk.scan(d), [])
            (d / "leak.txt").write_text("JEV_API_KEY=realrealrealrealreal2\n")
            subprocess.run(["git", "add", "leak.txt"], cwd=d, check=True)
            self.assertEqual([(r, n) for r, n, _ in sk.scan(d)], [("leak.txt", 1)])
        finally:
            shutil.rmtree(d)

    def test_the_one_allowed_fixture_is_named_with_its_reason(self):
        for (f, kind), why in sk.ALLOW.items():
            self.assertTrue((REPO / f).is_file(), f)
            self.assertTrue(why)


class Workflow(unittest.TestCase):
    def setUp(self):
        self.text = CI.read_text()

    def test_every_action_is_pinned_to_a_commit_with_its_version_in_a_comment(self):
        uses = re.findall(r"uses:\s*(\S+)\s*(#.*)?", self.text)
        self.assertGreaterEqual(len(uses), 4)
        for ref, comment in uses:
            self.assertRegex(ref, r"^[\w.\-]+/[\w.\-]+@[0-9a-f]{40}$", ref)
            self.assertRegex(comment or "", r"# v\d", ref)

    def test_runners_and_python_are_pinned_not_latest(self):
        self.assertNotIn("latest", self.text)
        self.assertEqual(set(re.findall(r"runs-on:\s*(\S+)", self.text)), {"ubuntu-24.04"})
        self.assertIn('python-version: "3.12"', self.text)

    def test_it_runs_the_offline_tests_and_the_key_scan_and_uses_no_secret_or_key(self):
        for needle in ("code/test.sh", "pytest -q evaluations/tests", "code/tools/scan_keys.py", "permissions:\n  contents: read"):
            self.assertIn(needle, self.text)
        for banned in ("secrets.", "GLOO_API_KEY", "JEV_API_KEY", "YVP_APP_KEY", "NURY_FEEDBACK", "--live"):
            self.assertNotIn(banned, self.text)

    def test_it_is_valid_yaml_with_the_two_jobs(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML is not installed")
        d = yaml.safe_load(self.text)
        self.assertEqual(sorted(d["jobs"]), ["key-scan", "tests"])
        self.assertIn("pull_request", d[True] if True in d else d["on"])


if __name__ == "__main__":
    unittest.main()
