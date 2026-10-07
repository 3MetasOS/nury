"""Church network tests. No network calls."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from nury import casefile as cf  # noqa: E402
from nury import network as net  # noqa: E402
from nury import playbook as pbm  # noqa: E402
from nury.engine import CaseState, run_scripted, run_stage  # noqa: E402
from nury.privacy import PrivacyClient  # noqa: E402
from test_core import ATTY, CANNED, CHECK, HCANNED, HFake, FakeClient, HINFO, HRES, HTRIAGE  # noqa: E402

TRI_AURORA = ("SITUATION: Carlos was detained.\nPEOPLE:\n- Maria\nLOCATION: Aurora, Colorado\nFAMILY LANGUAGE: es\n"
              "URGENCY: High\nMISSING FACTS:\n1. a\n2. b\n3. c")
CHURCH = ("Personas con quienes ha trabajado nuestra iglesia\n- Demo Legal Aid (fictional): consultas gratis de inmigración (303) 555-0101 https://demo-legal-aid.example.org/\n")


def demo_on():
    os.environ["NURY_DEMO_NETWORK"] = "1"


def demo_off():
    os.environ.pop("NURY_DEMO_NETWORK", None)


class Store(unittest.TestCase):
    def setUp(self):
        demo_off()
        self.root = Path(tempfile.mkdtemp())

    def tearDown(self):
        demo_off()
        shutil.rmtree(self.root)

    def good(self, **kw):
        e = {"name": "Test Legal Aid", "kind": "legal_aid", "languages": ["es"], "city": "Aurora", "state": "Colorado",
             "phone": "(303) 555-0111", "services": "Free consults", "note": "The pastor's own words", "last_used": "2026-09-01"}
        e.update(kw)
        return e

    def test_crud_validate_import_export(self):
        n = net.load_network(self.root)
        a = n.add(self.good())
        self.assertEqual(a["state"], "CO")
        self.assertEqual(len(n.list()), 1)
        n.update(a["id"], {"phone": "(303) 555-0122"})
        self.assertEqual(n.get(a["id"])["phone"], "(303) 555-0122")
        n.mark_used(a["id"], "2026-10-07")
        self.assertEqual(n.get(a["id"])["last_used"], "2026-10-07")
        for bad in ({"name": ""}, {"kind": "best_lawyer"}, {"url": "ftp://x", "phone": ""}, {"phone": "", "url": ""},
                    {"state": "Narnia"}, {"languages": ["fr"]}, {"last_used": "yesterday"}):
            with self.assertRaises(net.NetworkError):
                n.add(self.good(**bad))
        dest = self.root / "out.json"
        n.export_json(dest)
        n2 = net.load_network(self.root / "other")
        self.assertEqual(n2.import_json(dest), 1)
        self.assertEqual(n2.import_json(dest), 0)                      # merge, no duplicates
        (self.root / "bad.json").write_text(json.dumps({"entries": [self.good(), {"name": "x"}]}))
        with self.assertRaises(net.NetworkError):
            n2.import_json(self.root / "bad.json")                       # one bad entry refuses all
        n.delete(a["id"])
        self.assertEqual(n.list(), [])
        with self.assertRaises(net.NetworkError):
            n.delete("nope")

    def test_demo_network_is_gated_fictional_and_read_only(self):
        self.assertEqual(net.load_network(self.root).list(), [])          # a real run never loads the demo
        demo_on()
        n = net.load_network(self.root)
        self.assertTrue(n.fictional)
        names = [e["name"] for e in n.list()]
        self.assertTrue(names and all("(fictional)" in x for x in names))
        self.assertTrue(json.loads(net.DEMO_FILE.read_text())["fictional"])
        for e in n.list():
            self.assertRegex(e["phone"], r"555-01\d\d")
        with self.assertRaises(net.NetworkError):
            n.add(self.good())
        with self.assertRaises(net.NetworkError):                          # fictional contacts cannot enter a real network
            net.Network(self.root, demo=False).import_json(net.DEMO_FILE)

    def test_matching_is_deterministic_and_local(self):
        demo_on()
        E = net.load_network().list()
        legal = ["pro_bono_immigration_attorney", "legal_aid"]
        self.assertEqual([e["id"] for e in net.match(E, "CO", "Aurora", "es", legal)], ["demo-aurora-legal"])
        self.assertEqual([e["id"] for e in net.match(E, "Arizona", "Mesa", "es", legal)], ["demo-mesa-clinic"])
        self.assertEqual(net.match(E, "AZ", "Mesa", "en", legal), [])                     # language must fit
        self.assertEqual(net.match(E, "TX", "", "es", legal), [])                         # wrong place, not listed
        self.assertEqual([e["id"] for e in net.match(E, "", "", "es", ["interpreter"])], ["demo-national-interpreters"])
        self.assertEqual(net.parse_location("Aurora, Colorado"), ("Aurora", "CO"))
        self.assertEqual(net.parse_location("Mesa, AZ"), ("Mesa", "AZ"))
        self.assertEqual(net.match(E, "CO", "Aurora", "es", ["medicare_medicaid_help"])[0]["id"], "demo-aurora-medicare")


class Home(unittest.TestCase):
    def tearDown(self):
        demo_off()

    def test_home_state_fills_in_when_the_case_has_no_state(self):
        root = Path(tempfile.mkdtemp())
        try:
            n = net.load_network(root, demo=False)
            n.add({"name": "Local Aid", "kind": "legal_aid", "languages": ["es"], "city": "Aurora", "state": "CO", "phone": "(303) 555-0111"})
            self.assertEqual(n.home, ("", ""))
            n.set_home("Aurora", "Colorado")
            self.assertEqual(n.home, ("Aurora", "CO"))
            self.assertEqual(len(n.list()), 1)                                  # set_home keeps the entries
            n.add({"name": "Second", "kind": "legal_aid", "phone": "(303) 555-0112"})
            self.assertEqual(n.home, ("Aurora", "CO"))                           # and add keeps the home
            os.environ["NURY_DEMO_NETWORK"] = "1"
            self.assertEqual(net.load_network().home, ("Aurora", "CO"))
            spec = {"kinds": ["pro_bono_immigration_attorney"], "limit": 5}
            got = net.source_for(spec, None, {"location": "outside his workplace"}, "es", root)["entries"]
            self.assertEqual([e["id"] for e in got], ["demo-aurora-legal"])      # no state in the case: the church's home state
            got = net.source_for(spec, None, {"location": "Mesa, Arizona"}, "es", root)["entries"]
            self.assertEqual([e["id"] for e in got], ["demo-mesa-clinic"])       # an explicit state wins
        finally:
            shutil.rmtree(root)


class Stages(unittest.TestCase):
    def setUp(self):
        demo_on()

    def tearDown(self):
        demo_off()

    def _state(self):
        st = CaseState("intake")
        st.approved.update(triage=TRI_AURORA, rights=CANNED["rights"])
        return st

    def test_prompt_lists_church_contacts_without_the_pastors_note(self):
        pb = pbm.load_playbook("detention")
        from nury.engine import dynamic_source
        fields = pbm.parse_fields(TRI_AURORA)
        dyn = {"church_network": dynamic_source(pb.registry["attorney"].source_specs[1], pb, self._state(), fields, "es")}
        text = pbm.render_prompt(pb.registry["attorney"], pb, "es", None, fields, None, dyn)
        self.assertIn("People our church has worked with", text)
        self.assertIn("Demo Legal Aid (fictional)", text)
        self.assertIn("(303) 555-0101", text)
        self.assertNotIn("The pastor's note would go here", text)
        self.assertNotIn("Demo Border Law Clinic", text)                    # wrong state
        self.assertNotIn("recommend a specific attorney", text.lower())

    def test_listed_exactly_passes_dropped_changed_invented_ranked_fail(self):
        good = dict(CANNED, attorney=ATTY + "\n" + CHURCH)
        r = run_stage("attorney", self._state(), client=FakeClient(good))
        self.assertEqual((r.status, r.metrics["attempts"]), ("approved", 1))
        for label, text, cat in (
            ("dropped", ATTY, "missing_vetted_entry"),
            ("renamed", ATTY + "\n- Legal Help Center: Free consultations (303) 555-0101", "ungrounded_claim"),
            ("invented title", ATTY + "\n" + CHURCH + "\n- Abogado Juan Pérez ayuda gratis", "ungrounded_claim"),
            ("ranked", ATTY + "\n" + CHURCH + "\nEs el mejor abogado de la ciudad", "endorsement"),
            ("ranked en", ATTY + "\n" + CHURCH + "\nEs una clínica altamente recomendada", "endorsement"),
            ("invented phone", ATTY + "\n" + CHURCH + "\n- Otro Lugar: (303) 555-0999", "ungrounded_claim"),
        ):
            r = run_stage("attorney", self._state(), client=FakeClient(dict(CANNED, attorney=text)))
            self.assertEqual(r.status, "escalated", label)
            self.assertIn(cat, r.reason_categories, label)

    def test_no_network_means_stage_still_works(self):
        demo_off()
        st = self._state()
        r = run_stage("attorney", st, client=FakeClient())
        self.assertEqual(r.status, "approved")
        self.assertEqual(st.sources_used["attorney"]["church_network"]["entries"], [])

    def test_hospital_resources_use_network(self):
        st = CaseState("intake")
        st.approved.update(triage=HTRIAGE.replace("LOCATION: Aurora, CO", "LOCATION: Aurora, Colorado"), info=HINFO)
        text = HRES + "\n- Demo Medicare Helpers (fictional): Help (303) 555-0103 https://demo-medicare-help.example.org/\n" \
                      "- Demo Interpreter Line (fictional): intérpretes por teléfono (800) 555-0104"
        r = run_stage("resources", st, client=HFake(dict(HCANNED, resources=text)), playbook="hospital")
        self.assertEqual(r.status, "approved")
        ids = [x["id"] for x in st.sources_used["resources"]["church_network"]["entries"]]
        self.assertEqual(sorted(ids), ["demo-aurora-medicare", "demo-national-interpreters"])
        r2 = run_stage("resources", st, client=HFake(dict(HCANNED, resources=HRES)), playbook="hospital")
        self.assertEqual(r2.status, "escalated")                             # dropped the church contacts
        self.assertNotIn("immigra", pbm.render_prompt(pbm.load_playbook("hospital").registry["resources"],
                                                     pbm.load_playbook("hospital"), "es", None, {"location": "Aurora, Colorado"}).lower())

    def test_network_phones_and_links_survive_privacy_and_the_family_phone_does_not(self):
        seen = []

        class Spy:
            def ask(self, user_input, instructions=None, **kw):
                seen.append(user_input)
                return "ok", {"latency_s": 0, "input_tokens": 0, "output_tokens": 0}
        entries = net.load_network().list()
        pc = PrivacyClient(Spy(), ["Maria"])
        pc.allow_network(entries)
        pc.ask("Maria dice: llame a Demo Legal Aid (fictional) al (303) 555-0101 o vea https://demo-legal-aid.example.org/. "
               "Su propio número es (720) 555-0177.")
        body = seen[0]
        self.assertIn("(303) 555-0101", body)
        self.assertIn("https://demo-legal-aid.example.org/", body)
        self.assertIn("Demo Legal Aid (fictional)", body)
        self.assertNotIn("(720) 555-0177", body)
        self.assertNotIn("Maria", body)

    def test_allow_playbook_keeps_official_and_network_details_but_not_the_family_phone(self):
        seen = []

        class Spy:
            def ask(self, user_input, instructions=None, **kw):
                seen.append(user_input)
                return "ok", {}
        pb = pbm.load_playbook("detention")
        pc = PrivacyClient(Spy(), ["Maria"])
        pc.allow_playbook(pb)
        pc.ask("Llame a RMIAN (303) 433-2812 o al (303) 555-0101. El número de Maria es (720) 555-0177. immcenter@americanbar.org")
        body = seen[0]
        self.assertIn("(303) 433-2812", body)
        self.assertIn("(303) 555-0101", body)
        self.assertIn("immcenter@americanbar.org", body)
        self.assertNotIn("(720) 555-0177", body)

    def test_full_run_case_file_marks_church_contacts(self):
        canned = dict(CANNED, triage=TRI_AURORA, attorney=ATTY + "\n" + CHURCH)
        st, rs, au = run_scripted("intake", client=FakeClient(canned))
        self.assertEqual(rs[2].status, "approved")
        self.assertTrue(au.of_kind("dynamic_source"))
        root = Path(tempfile.mkdtemp())
        try:
            out = cf.save_case(st, au, "detention", root)
            svg = (Path(out["path"]) / "nextsteps.svg").read_text()
            self.assertIn("Church: Demo Legal Aid (fictional)", svg)
            self.assertNotIn("The pastor's note", svg)
        finally:
            shutil.rmtree(root)

    def test_official_list_hook_empty_until_a_file_exists_then_matches_state(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(pbm.PLAYBOOKS_DIR, tmp, dirs_exist_ok=True)
            (tmp / "detention" / "sources" / "official_list.json").unlink()
            from nury.engine import dynamic_source
            pb = pbm.load_playbook("detention", tmp)
            spec = {"name": "official_list", "dynamic": "official_list", "limit": 5}
            fields = {"location": "Aurora, Colorado"}
            self.assertEqual(dynamic_source(spec, pb, CaseState("x"), fields, "es")["entries"], [])
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
