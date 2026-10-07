"""The new-playbook scaffold. No network."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonet  # noqa: E402,F401
import new_playbook as npb  # noqa: E402
from nury import playbook as pbm  # noqa: E402


class Scaffold(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_the_scaffold_validates_has_every_file_and_cannot_run(self):
        dest = npb.build("house_fire", "House fire", self.root)
        for f in ("playbook.json", "stages.json", "outcomes.json", "sources/approvals.json"):
            self.assertTrue((dest / f).is_file(), f)
        self.assertEqual(sorted(p.name for p in (dest / "prompts").iterdir()), ["checklist.txt", "info.txt", "pastoral.txt", "resources.txt", "triage.txt"])
        self.assertEqual(npb.validate("house_fire", self.root), ["triage", "info", "resources", "checklist", "pastoral"])
        with self.assertRaises(pbm.PlaybookError) as cm:
            pbm.load_playbook("house_fire", self.root)
        self.assertIn("coming soon", str(cm.exception))
        listed = {e["id"]: e["status"] for e in pbm.list_playbooks(self.root)}
        self.assertEqual(listed["house_fire"], "soon")

    def test_nothing_is_approved_and_every_value_is_a_todo(self):
        import json
        dest = npb.build("house_fire", "House fire", self.root)
        self.assertEqual(json.loads((dest / "sources/approvals.json").read_text()), {})
        pj = json.loads((dest / "playbook.json").read_text())
        self.assertEqual(pj["status"], "soon")
        self.assertIn("TODO", pj["boundary"]["domain"])
        for p in (dest / "prompts").iterdir():
            self.assertIn("TODO", p.read_text())
        for f in (dest / "sources").glob("*.json"):
            self.assertNotIn("ACLU", f.read_text())
            self.assertNotIn("hospital", f.read_text().lower())

    def test_it_refuses_an_existing_folder_and_a_bad_id_and_changes_nothing(self):
        npb.build("house_fire", "House fire", self.root)
        before = sorted(str(p) for p in self.root.rglob("*"))
        for pid in ("house_fire", "House", "a", "../x", "9lives"):
            with self.assertRaises(SystemExit):
                npb.build(pid, "x", self.root)
        self.assertEqual(sorted(str(p) for p in self.root.rglob("*")), before)

    def test_validation_catches_a_broken_playbook(self):
        dest = npb.build("house_fire", "House fire", self.root)
        (dest / "prompts" / "triage.txt").unlink()
        with self.assertRaises(Exception):
            npb.validate("house_fire", self.root)

    def test_the_real_playbooks_are_untouched(self):
        npb.build("house_fire", "House fire", self.root)
        self.assertFalse((pbm.PLAYBOOKS_DIR / "house_fire").exists())


if __name__ == "__main__":
    unittest.main()
