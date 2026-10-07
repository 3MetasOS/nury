"""Official list (U.S. Department of Justice, as Juan approved it). No network."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from nury import officiallist as ol  # noqa: E402
from nury.engine import CaseState, run_stage  # noqa: E402
from test_core import ATTY, CANNED, FakeClient, RIGHTS, official_lines  # noqa: E402

TRI_CO = ("SITUATION: x\nPEOPLE:\n- Maria\nLOCATION: Aurora, Colorado\nFAMILY LANGUAGE: es\nURGENCY: High\nMISSING FACTS:\n1. a\n2. b\n3. c")
HELD_PHONES = ["(719) 866-6515", "(970) 233-3219", "(970) 439-0595", "(303) 399-4500", "(970) 413-4303", "(970) 893-9034", "(303) 795-3968"]
SRC = ol.SRC


def state(loc="Aurora, Colorado"):
    st = CaseState("intake")
    st.approved.update(triage=TRI_CO.replace("Aurora, Colorado", loc), rights=RIGHTS)
    return st


class Official(unittest.TestCase):
    def test_built_file_has_only_approved_and_no_held_details(self):
        d = json.loads((SRC / "official_list.json").read_text())
        ap = json.loads((SRC / "approvals.json").read_text())
        self.assertEqual(len(d["entries"]), 18)
        self.assertEqual(len(d["held_names"]), 7)
        txt = json.dumps(d)
        for ph in HELD_PHONES:
            self.assertNotIn(ph, txt)
        for e in d["entries"]:
            self.assertEqual(ap[e["id"]], "approved")
            self.assertNotRegex(json.dumps(e).lower(), r"\bfree\b")        # never labeled free
        self.assertEqual(ol.build(), d)                                    # the file is exactly what the build makes
        self.assertIn("Listed does not mean recommended", d["label"])
        self.assertIn("10/04/26", d["as_of"])

    def test_select_is_state_bound_detention_first_and_skips_asylum_only(self):
        d = json.loads((SRC / "official_list.json").read_text())
        got = ol.select(d, "CO")["entries"]
        self.assertEqual({e["id"] for e in got[:2]}, {"rmian", "aba-detention-hotline"})
        self.assertNotIn("colorado-asylum-center", [e["id"] for e in ol.select(d, "CO", 50)["entries"]])
        self.assertEqual(ol.select(d, "AZ")["entries"], [])                # only Colorado was read
        self.assertEqual(ol.select(d, "")["entries"], [])

    def test_aba_entry_uses_the_family_route_not_the_military_hotline(self):
        d = json.loads((SRC / "official_list.json").read_text())
        aba = [e for e in d["entries"] if e["id"] == "aba-detention-hotline"][0]
        self.assertEqual(aba["email"], "immcenter@americanbar.org")
        self.assertEqual(aba["phones"], [])
        self.assertNotIn("855", json.dumps(aba))

    def test_approved_entries_pass_with_the_caveat(self):
        st = state()
        r = run_stage("attorney", st, client=FakeClient())
        self.assertEqual((r.status, r.metrics["attempts"]), ("approved", 1))
        self.assertIn("Rocky Mountain Immigrant Advocacy Network", st.approved["attorney"])
        self.assertIn("no significa", st.approved["attorney"])

    def test_held_entry_named_in_a_draft_is_rejected(self):
        for held in ("Alianza NORCO", "Littleton Immigrant Resources Center", "Catholic Charities of Central Colorado"):
            bad = dict(CANNED, attorney=ATTY + f"\n- {held}: llame pronto")
            r = run_stage("attorney", state(), client=FakeClient(bad))
            self.assertEqual(r.status, "escalated", held)
            self.assertIn("ungrounded_claim", r.reason_categories, held)

    def test_held_phone_is_rejected_by_the_floor(self):
        bad = dict(CANNED, attorney=ATTY + "\n- Un lugar: (970) 893-9034")
        r = run_stage("attorney", state(), client=FakeClient(bad))
        self.assertEqual(r.status, "escalated")

    def test_free_label_missing_entry_and_missing_caveat_are_rejected(self):
        class Tweak(FakeClient):
            def __init__(self, fn):
                super().__init__()
                self.fn = fn

            def ask(self, u, instructions=None, **kw):
                t, m = super().ask(u, instructions=instructions, **kw)
                return self.fn(t), m
        cases = {
            "free": lambda t: t.replace("- Rocky Mountain Immigrant Advocacy Network", "- Rocky Mountain Immigrant Advocacy Network (servicios gratis)"),
            "caveat": lambda t: t.replace("Estar en la lista no significa que sea recomendado.", ""),
            "dropped": lambda t: "\n".join(l for l in t.splitlines() if "ABA Commission" not in l and "855" not in l),
        }
        for name, fn in cases.items():
            r = run_stage("attorney", state(), client=Tweak(fn))
            self.assertEqual(r.status, "escalated", name)
            self.assertTrue({"ungrounded_claim", "missing_vetted_entry"} & set(r.reason_categories), name)

    def test_other_state_has_no_official_section_and_may_not_invent_one(self):
        st = state("Mesa, Arizona")
        r = run_stage("attorney", st, client=FakeClient())
        self.assertEqual(r.status, "approved")
        self.assertEqual(st.sources_used["attorney"]["official_list"]["entries"], [])
        self.assertEqual(official_lines("OFFICIAL LIST (U.S. Department of Justice; may be empty):\n(none)\n\nNATIONAL LIST:"), "")

    def test_listed_does_not_mean_recommended_is_allowed_but_endorsing_is_not(self):
        from nury import checks as ck
        ns = type("N", (), {})()
        self.assertEqual(ck.no_endorsement_words({}, "Listed by the U.S. Department of Justice. Listed does not mean recommended.", ns), [])
        self.assertEqual(ck.no_endorsement_words({}, "Estar en la lista no significa que sea recomendado.", ns), [])
        self.assertTrue(ck.no_endorsement_words({}, "Es una organización altamente recomendada.", ns))
        self.assertTrue(ck.no_endorsement_words({}, "This is the best lawyer.", ns))

    def test_language_check_ignores_vetted_english_names(self):
        from nury import guardrails as g
        t = "Llame a Catholic Charities and Community Services of the Archdiocese hoy."
        self.assertTrue(g.language_reasons(t, "es"))
        self.assertEqual(g.language_reasons(t, "es", ["Catholic Charities and Community Services of the Archdiocese"]), [])


if __name__ == "__main__":
    unittest.main()
