import importlib.util
import unittest
from pathlib import Path

import nonet  # noqa: F401
from nury import readability as rd
from nury.engine import run_scripted
from test_core import CANNED, FakeClient, HCANNED, HFake

NINJA = Path(__file__).resolve().parents[2] / "documents" / "product" / "readability_check.py"
EN = "Call a lawyer today. Keep your papers in one place. Write down the names of the people you talk to."
ES = "Llame a un abogado hoy. Guarde sus papeles en un solo lugar. Anote los nombres de las personas con quienes hable."


def ninja():
    spec = importlib.util.spec_from_file_location("readability_check", NINJA)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Readability(unittest.TestCase):
    def test_numbers_match_hack_ninjas_script(self):
        n = ninja()
        for text, lang in ((EN, "en"), (ES, "es"), ("The petitioner shall adjudicate the jurisdictional ramifications.", "en")):
            got = rd.of_draft(text, lang)
            want = n.measure(text, lang)
            for k, v in want.items():
                self.assertEqual(got[k], v, (lang, k))

    def test_target_flag_and_plain_text_meets_it(self):
        self.assertTrue(rd.of_draft(EN, "en")["meets_target"])
        self.assertTrue(rd.of_draft(ES, "es")["meets_target"])
        self.assertFalse(rd.of_draft("The petitioner shall adjudicate the jurisdictional ramifications notwithstanding.", "en")["meets_target"])

    def test_bad_input_never_raises(self):
        self.assertIsInstance(rd.of_draft("", "en"), dict)
        self.assertIsInstance(rd.of_draft(None, "xx"), dict)

    def test_family_stages_log_one_advisory_event_and_the_pastor_stage_none(self):
        for fake, canned, pb, ids in ((FakeClient, CANNED, "detention", ["rights", "attorney", "checklist", "pastoral"]),
                                      (HFake, HCANNED, "hospital", ["info", "resources", "checklist", "pastoral"])):
            st, rs, au = run_scripted("intake", client=fake(canned), playbook=pb)
            ev = [e for e in au.events if e["kind"] == "readability"]
            self.assertEqual([e["stage"] for e in ev], ids)
            self.assertTrue(all(e["advisory"] is True and e["lang"] == "es" and "szigriszt" in e for e in ev))
            self.assertEqual(st.outcome["outcome"], "package_complete")          # advisory: it changes no result


if __name__ == "__main__":
    unittest.main()
