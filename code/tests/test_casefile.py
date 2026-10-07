"""Case file tests. No network. Run: cd code && python3 -m unittest discover -s tests"""
import json
import os
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from nury import casefile as cf  # noqa: E402
from nury.engine import UNSAFE_SUFFIX, CaseState, run_scripted  # noqa: E402
from test_core import (CANNED, HCANNED, HFake, FakeClient, ATTY, CHECK)  # noqa: E402

DCHK = ("DO TONIGHT\n1. Llame a un abogado de inmigración calificado.\n2. Pregúntele al abogado cómo averiguar dónde está.\n"
        "DO NOT DO\n1. No firme nada sin hablar con un abogado.\nGATHER THESE DOCUMENTS\n- Identificaciones de la familia\n- Papeles de inmigración")
DTRI = ("SITUATION: Carlos was detained in Aurora.\nPEOPLE:\n- Maria (wife)\n- Carlos (detained)\n- Two children, 8 and 11\n"
        "LOCATION: Aurora, CO\nFAMILY LANGUAGE: es\nURGENCY: High, kids at home\nMISSING FACTS:\n1. Where is he held?\n2. Any case number?\n3. Any court date?")


class Cases(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.root)

    def _run(self, **kw):
        return run_scripted("intake", **kw)

    def _all_text(self, d):
        return "\n".join(p.read_text(encoding="utf-8") for p in Path(d).iterdir() if p.is_file())

    def test_detention_case_layout_and_links(self):
        canned = dict(CANNED, triage=DTRI, checklist=DCHK, attorney=ATTY)
        st, rs, au = self._run(client=FakeClient(canned))
        out = cf.save_case(st, au, "detention", self.root)
        d = Path(out["path"])
        names = sorted(p.name for p in d.iterdir())
        for n in ("index.md", "01-triage.md", "02-rights.md", "03-attorney.md", "04-checklist.md", "05-pastoral.md",
                  "people.md", "documents.md", "timeline.md", "log.md", "nextsteps.svg", "case.json"):
            self.assertIn(n, names)
        idx = (d / "index.md").read_text()
        self.assertIn("Package complete", idx)
        self.assertIn("Next step: Llame a un abogado", idx)
        self.assertIn("![Next-steps map](nextsteps.svg)", idx)
        # every relative link resolves
        import re
        for p in d.glob("*.md"):
            for target in re.findall(r"\]\(([^)#]+)\)", p.read_text()):
                if not target.startswith("http"):
                    self.assertTrue((d / target).is_file(), f"{p.name} -> {target}")
        self.assertEqual((d / "intake.md").read_text().split("\n")[4], "intake")                  # the original words, saved
        self.assertIn("[Intake](intake.md)", idx)
        self.assertIn("Maria (wife)", (d / "people.md").read_text())
        self.assertIn("- [ ] Identificaciones de la familia", (d / "documents.md").read_text())
        self.assertIn("approved by the pastor", (d / "01-triage.md").read_text())

    def test_map_is_svg_390_with_four_lanes_and_vetted_links_only(self):
        canned = dict(CANNED, triage=DTRI, checklist=DCHK, attorney=ATTY)
        st, rs, au = self._run(client=FakeClient(canned))
        d = Path(cf.save_case(st, au, "detention", self.root)["path"])
        svg = (d / "nextsteps.svg").read_text()
        root = ET.fromstring(svg)
        self.assertEqual(root.attrib["viewBox"].split()[2], "400")
        for lane in ("Tonight", "This week", "Questions still open", "Who to call"):
            self.assertIn(lane, svg)
        self.assertIn("Where is he held?", svg)                   # open question from triage
        import re
        urls = re.findall(r"https?://[^\s<\"]+", svg.replace('xmlns="http://www.w3.org/2000/svg"', ""))
        self.assertTrue(urls)
        allowed = g_allowed("detention")
        for u in urls:
            self.assertTrue(any(cf.g._norm_url(u) == cf.g._norm_url(a) for a in allowed), u)
        self.assertNotRegex(svg.lower(), r"\b(will be|va a ser|serán|will win|released|liberad)")   # no outcomes

    def test_svg_escapes_text(self):
        canned = dict(CANNED, triage=DTRI.replace("Where is he held?", "<script>alert(1)</script> & more"), checklist=DCHK, attorney=ATTY)
        st, rs, au = self._run(client=FakeClient(canned))
        d = Path(cf.save_case(st, au, "detention", self.root)["path"])
        svg = (d / "nextsteps.svg").read_text()
        self.assertNotIn("<script>", svg)
        ET.fromstring(svg)                                         # still well formed

    def test_rejected_draft_never_in_case_folder_or_zip(self):
        canned = dict(CANNED, triage=DTRI, checklist=DCHK, attorney=ATTY)
        st, rs, au = self._run(client=FakeClient(canned),
                               fault_injection={"stage": "rights", "times": 1, "draft_suffix": UNSAFE_SUFFIX})
        self.assertEqual(rs[1].metrics["attempts"], 2)
        rejected = au.of_kind("draft_rejected")[0]["draft"]
        out = cf.save_case(st, au, "detention", self.root)
        text = self._all_text(out["path"])
        self.assertNotIn(rejected, text)
        for bad in ("Garantizamos", "garantizamos", "Su caso va a ser ganado", UNSAFE_SUFFIX.strip()):
            self.assertNotIn(bad, text)
        self.assertIn("draft rejected (not saved)", text)           # the log says it happened
        self.assertIn("banned_phrase", text)                        # categories only
        z = cf.export_zip(out["id"], self.root)
        with zipfile.ZipFile(z) as zf:
            blob = "\n".join(zf.read(n).decode() for n in zf.namelist())
        self.assertNotIn(rejected, blob)
        self.assertNotIn("Garantizamos", blob)

    def test_refuses_unapproved_stage(self):
        st, rs, au = self._run(client=FakeClient(), decisions={"attorney": "stop"})
        with self.assertRaises(cf.CaseError):
            cf.save_case(st, au, "detention", self.root)
        st2, rs2, au2 = self._run(client=FakeClient(), fault_injection={"stage": "rights", "times": 3, "draft_suffix": UNSAFE_SUFFIX})
        with self.assertRaises(cf.CaseError):
            cf.save_case(st2, au2, "detention", self.root)
        self.assertEqual(list(self.root.iterdir()), [])             # nothing was written

    def test_edits_are_flagged_and_kept(self):
        st, rs, au = self._run(client=FakeClient(), decisions={"rights": ("edit", "- EDITADO (ACLU Know Your Rights)")})
        out = cf.save_case(st, au, "detention", self.root)
        d = Path(out["path"])
        self.assertIn("edited by the pastor", (d / "02-rights.md").read_text())
        self.assertIn("EDITADO", (d / "02-rights.md").read_text())
        self.assertIn("EDITED by the pastor", (d / "log.md").read_text())
        self.assertIn("edited by the pastor: 2. Rights brief", (d / "index.md").read_text())

    def test_no_keys_in_case_and_leak_is_refused(self):
        os.environ["GLOO_API_KEY"] = "sk-test-secret-123456"
        try:
            st, rs, au = self._run(client=FakeClient())
            out = cf.save_case(st, au, "detention", self.root)
            self.assertNotIn("sk-test-secret-123456", self._all_text(out["path"]))
            leaky = dict(CANNED, pastoral=CANNED["pastoral"] + " sk-test-secret-123456")
            st2, rs2, au2 = self._run(client=FakeClient(leaky))
            with self.assertRaises(cf.CaseError):
                cf.save_case(st2, au2, "detention", self.root)
        finally:
            del os.environ["GLOO_API_KEY"]

    def test_hospital_case_has_no_immigration_words(self):
        st, rs, au = run_scripted("intake", client=HFake(HCANNED), playbook="hospital")
        out = cf.save_case(st, au, "hospital", self.root)
        text = self._all_text(out["path"])
        self.assertNotIn("immigra", text.lower())
        d = Path(out["path"])
        self.assertTrue((d / "02-info.md").is_file())
        self.assertIn("988", (d / "nextsteps.svg").read_text())      # vetted resource whose link is in the approved text
        self.assertIn("Una lista de preguntas", (d / "documents.md").read_text())

    def test_list_load_export(self):
        st, rs, au = self._run(client=FakeClient())
        a = cf.save_case(st, au, "detention", self.root, case_id="one")
        lst = cf.list_cases(self.root)
        self.assertEqual([c["id"] for c in lst], ["one"])
        loaded = cf.load_case("one", self.root)
        self.assertEqual(loaded["meta"]["playbook"], "detention")
        self.assertIn("index.md", loaded["pages"])
        self.assertTrue(loaded["svg"].startswith("<svg"))
        z = cf.export_zip("one", self.root)
        with zipfile.ZipFile(z) as zf:
            self.assertIn("one/index.md", zf.namelist())
        with self.assertRaises(cf.CaseError):
            cf.load_case("../etc", self.root)
        with self.assertRaises(cf.CaseError):
            cf.save_case(st, au, "detention", self.root, case_id="one")      # no overwrite
        self.assertEqual(cf.list_cases(self.root / "nope"), [])


def g_allowed(pbid):
    from nury.engine import get_playbook
    pb = get_playbook(pbid)
    return cf.g.allowed_urls_in(json.dumps(pb.sources))


if __name__ == "__main__":
    unittest.main()
