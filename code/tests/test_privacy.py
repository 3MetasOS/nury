"""Privacy layer tests, including the LEAK TEST: capture the exact request body at the HTTP boundary."""
import json
import os
import re
import shutil
import sys
import tempfile
import unicodedata
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonet  # noqa: E402,F401
from nury import casefile as cf  # noqa: E402
from nury import gloo_client  # noqa: E402
from nury.engine import UNSAFE_SUFFIX, CaseState, GateDecision, approve_all, run_pipeline, scripted_gate  # noqa: E402
from nury.audit import AuditLog  # noqa: E402
from nury.privacy import PrivacyClient, Pseudonymizer, make_client, propose_terms  # noqa: E402
from test_core import ATTY, CHECK, HINFO, HPAST, HRES, HCHK, RIGHTS  # noqa: E402

CANARIES = ["Zorana", "Quimbley", "Thaddeus", "Ottilie", "(303) 555-0142", "555-0142", "zorana.q@canarymail.org", "canarymail",
            "4821 Larkspur", "Larkspur", "03/14/1985", "A123456789", "EAC2190012345", "Brunhilda", "Vandersloot"]
INTAKE = ("Zorana Quimbley called at 2:07 AM from (303) 555-0142, email zorana.q@canarymail.org, speaking Spanish. "
          "Her husband Thaddeus Quimbley, born on 03/14/1985, A-number A123456789, case number EAC2190012345, was taken "
          "from 4821 Larkspur Avenue, Apt 3B, Aurora, Colorado. They have a daughter, Ottilie, 8. She wants to know what to do tonight.")
HINTAKE = ("Zorana Quimbley called at 11 PM from (303) 555-0142. Her father Thaddeus Quimbley, born on 03/14/1985, was taken by "
           "ambulance to the emergency room. Their daughter Ottilie is 8. Email zorana.q@canarymail.org. She lives at 4821 Larkspur Avenue.")
PROTECTED = ["Zorana Quimbley", "Thaddeus Quimbley", "Ottilie"]


def fold(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").casefold()


class FakeHTTP:
    """Stands in for requests.post. Records the exact JSON body. Replies like a model that copies tokens."""
    def __init__(self, hospital=False, mangle=False, unknown_first=False):
        self.bodies, self.hospital, self.mangle, self.unknown_first, self.unknown_done = [], hospital, mangle, unknown_first, False

    def __call__(self, url, json=None, headers=None, timeout=None):
        self.bodies.append(json)
        ins, inp = json["instructions"], json["input"]
        toks = re.findall(r"\[PERSON_\d+\]", inp)
        t1 = toks[0] if toks else "la familia"
        if self.mangle and toks:
            t1 = t1.replace("_", " ")                                                  # [PERSON 1]
        key = ("triage" if "structured case" in ins else "rights" if "rights brief" in ins else "info" if "information brief" in ins
               else "attorney" if "scannable list" in ins and not self.hospital else "resources" if "scannable list" in ins
               else "pastoral" if "pastoral message" in ins else "checklist")
        texts = {
            "triage": f"SITUATION: {t1} called about a family member.\nPEOPLE:\n- {t1} (caller)\nLOCATION: Aurora\nFAMILY LANGUAGE: es\nURGENCY: High, urgent\nMISSING FACTS:\n1. Where?\n2. Who?\n3. When?",
            "rights": RIGHTS, "info": HINFO, "attorney": ATTY, "resources": HRES,
            "checklist": (CHECK if not self.hospital else HCHK),
            "pastoral": f"Querida {t1}, la iglesia está con ustedes. No están solos. Estamos orando por ustedes."}
        text = texts[key]
        if key == "pastoral" and "VERSE:" in ins:
            text = "VERSE: NONE\nWHY:\nMESSAGE: " + text
        if self.unknown_first and not self.unknown_done and key == "pastoral":
            self.unknown_done = True
            text = "VERSE: NONE\nWHY:\nMESSAGE: Querida [PERSON_99], estamos con ustedes. No están solos."
        class R:
            status_code = 200
            def raise_for_status(self): pass
            def json(self_):
                return {"output": [{"type": "message", "content": [{"type": "output_text", "text": text}]}],
                        "usage": {"input_tokens": 10, "output_tokens": 5}}
        return R()


def run(playbook, intake, http, protected=PROTECTED, decisions=None, fault=None, tmp=None):
    os.environ.setdefault("GLOO_API_KEY", "test-key-not-real")
    with mock.patch.object(gloo_client.requests, "post", http):
        pc = PrivacyClient(gloo_client.GlooClient(api_key="test-key-not-real"), protected)
        st, au = CaseState(intake), AuditLog()
        gate = pc.wrap_gate(scripted_gate(decisions or {}))
        rs = run_pipeline(playbook, st, gate, pc, au, fault_injection=fault)
    return st, rs, au, pc


class Leak(unittest.TestCase):
    def _assert_no_leak(self, http):
        self.assertGreaterEqual(len(http.bodies), 5)
        for b in http.bodies:
            body = fold(json.dumps(b, ensure_ascii=False))
            for c in CANARIES:
                self.assertNotIn(fold(c), body, f"LEAK of {c!r} in an outbound body")
        self.assertTrue(any("[person_1]" in fold(json.dumps(b)) for b in http.bodies))     # tokens really went out

    def test_detention_all_stages_correction_loop_and_edit_with_new_name(self):
        http = FakeHTTP()
        edit = "- EDITADO. Hable con Brunhilda Vandersloot en la iglesia. (ACLU Know Your Rights)"
        st, rs, au, pc = run("detention", INTAKE, http, decisions={"rights": ("edit", edit)},
                             fault={"stage": "rights", "times": 1, "draft_suffix": UNSAFE_SUFFIX})
        self.assertEqual([r.status for r in rs], ["approved", "edited", "approved", "approved", "approved"])
        self.assertEqual(rs[1].metrics["attempts"], 2)                      # the loop ran, and still no leak
        self._assert_no_leak(http)
        # detokenized: the pastor sees real names
        self.assertIn("Zorana Quimbley", st.approved["triage"])
        self.assertIn("Zorana Quimbley", rs[4].shown_text)
        self.assertIn("Brunhilda Vandersloot", st.approved["rights"])        # the edit is kept in the saved case
        self.assertTrue(any(e["event"] == "edit_name_protected" for e in pc.events))
        self.assertIn("Brunhilda Vandersloot", pc.map().values())

    def test_hospital_all_stages_with_forced_rejection(self):
        http = FakeHTTP(hospital=True)
        st, rs, au, pc = run("hospital", HINTAKE, http, fault={"stage": "info", "times": 1, "draft_suffix": UNSAFE_SUFFIX})
        self.assertEqual([r.status for r in rs], ["approved"] * 5)
        self.assertEqual(rs[1].metrics["attempts"], 2)
        self._assert_no_leak(http)
        self.assertIn("Zorana Quimbley", rs[4].shown_text)

    def test_case_file_keeps_real_names_and_the_map_with_the_case(self):
        http = FakeHTTP()
        st, rs, au, pc = run("detention", INTAKE, http)
        root = Path(tempfile.mkdtemp())
        try:
            out = cf.save_case(st, au, "detention", root, privacy=pc)
            d = Path(out["path"])
            pages = "\n".join(p.read_text() for p in d.glob("*.md"))
            self.assertIn("Zorana Quimbley", pages)
            self.assertNotRegex(pages, r"\[PERSON_\d+\]")
            m = json.loads((d / "privacy-map.json").read_text())
            self.assertEqual(m["map"]["[PERSON_1]"], pc.map()["[PERSON_1]"])
            self.assertIn("privacy-map.json", out["files"])
        finally:
            shutil.rmtree(root)

    def test_mangled_tokens_are_repaired(self):
        http = FakeHTTP(mangle=True)
        st, rs, au, pc = run("detention", INTAKE, http)
        self.assertEqual([r.status for r in rs], ["approved"] * 5)
        self.assertNotRegex(st.approved["triage"] + st.approved["pastoral"], r"PERSON[ _]\d")
        self.assertIn("Zorana", st.approved["pastoral"])

    def test_unknown_token_triggers_a_new_call_then_is_clean(self):
        http = FakeHTTP(unknown_first=True)
        st, rs, au, pc = run("detention", INTAKE, http)
        self.assertEqual(rs[4].status, "approved")
        self.assertNotIn("[PERSON_99]", st.approved["pastoral"])
        self.assertTrue(any(e["event"] == "unknown_token" for e in pc.events))
        self._assert_no_leak(http)

    def test_unknown_token_that_never_resolves_becomes_a_visible_gap(self):
        class Always(FakeHTTP):
            def __call__(self, url, json=None, headers=None, timeout=None):
                r = super().__call__(url, json=json, headers=headers, timeout=timeout)
                return r
        http = Always(unknown_first=False)
        orig = http.__call__
        def bad(url, json=None, headers=None, timeout=None):
            r = orig(url, json=json, headers=headers, timeout=timeout)
            if "pastoral message" in json["instructions"]:
                class R2(r.__class__):
                    def json(self_):
                        return {"output": [{"type": "message", "content": [{"type": "output_text", "text": "Querida [PERSON_77], no están solos."}]}], "usage": {}}
                return R2()
            return r
        os.environ.setdefault("GLOO_API_KEY", "x")
        with mock.patch.object(gloo_client.requests, "post", bad):
            pc = PrivacyClient(gloo_client.GlooClient(api_key="x"), PROTECTED)
            text, meta = pc.ask("hola Zorana Quimbley", instructions="Task: draft a short pastoral message in Spanish")
        self.assertNotIn("PERSON_77", text)
        self.assertIn("[?]", text)
        self.assertEqual(meta["privacy"]["extra_calls"], 2)


class Units(unittest.TestCase):
    def test_roundtrip_and_stable_tokens(self):
        ps = Pseudonymizer(PROTECTED)
        a = ps.pseudonymize(INTAKE)
        for c in CANARIES[:-2]:
            self.assertNotIn(c, a)
        self.assertEqual(ps.detokenize(a)[0], INTAKE)
        self.assertEqual(ps.pseudonymize("Zorana Quimbley"), ps.pseudonymize("zorana quimbley"))      # stable, case blind
        self.assertIn("Aurora, Colorado", a)                                                           # city and state stay

    def test_accents_and_spanish_forms(self):
        ps = Pseudonymizer(["María José"])
        out = ps.pseudonymize("Llamó Maria Jose y luego MARÍA JOSÉ. Nació el 14 de marzo de 1985. Vive en Calle Larkspur 4821.")
        self.assertNotRegex(out, r"(?i)mar[ií]a")
        self.assertNotIn("1985", out)
        self.assertNotIn("Larkspur", out)

    def test_vetted_numbers_and_files_untouched_in_instructions(self):
        pc = PrivacyClient(None, PROTECTED)
        text = "Llame al 988 o vea index.md. Use 8.11 y 2:07. Ayuda: info@parroquia.org"
        self.assertEqual(pc.ps.pseudonymize(text, patterns=False), text)
        self.assertEqual(pc.ps.pseudonymize("Llame al 988 y a las 2:07 con 8 y 11", names=False), "Llame al 988 y a las 2:07 con 8 y 11")

    def test_propose_terms(self):
        c = {x["term"]: x for x in propose_terms(INTAKE)}
        self.assertTrue(c["Zorana Quimbley"]["suggested"] and c["Thaddeus Quimbley"]["suggested"] and c["Ottilie"]["suggested"])
        self.assertFalse(c["Aurora"]["suggested"])
        self.assertFalse(c["Colorado"]["suggested"])
        self.assertNotIn("Spanish", c)
        self.assertNotIn("What", c)
        self.assertNotIn("Larkspur", " ".join(c))                     # addresses are patterns, not names

    def test_propose_terms_skips_sentence_openers_but_keeps_names(self):
        text = ("Write exactly that. Please call me. Esto es urgente. Llame al pastor. Maria called at 2:07 AM. "
                "Her husband Jose was detained. Maria is afraid. Sra. Ruiz lives nearby. Pedro dijo que viene.")
        c = {x["term"]: x for x in propose_terms(text)}
        for word in ("Write", "Please", "Esto", "Llame"):
            self.assertNotIn(word, c, word)
        for name in ("Maria", "Jose", "Ruiz", "Pedro"):
            self.assertTrue(c[name]["suggested"], name)
        demo = ("Maria called at 2:07 AM, very upset, speaking Spanish. Her husband Jose was detained by immigration officers "
                "outside his workplace in Aurora. Maria is afraid to leave the house tomorrow. She wants to know what to do tonight.")
        d = {x["term"] for x in propose_terms(demo) if x["suggested"]}
        self.assertEqual(d, {"Maria", "Jose"})

    def test_off_switch_returns_plain_client(self):
        class Plain:
            def ask(self, *a, **k): return "x", {}
        p = Plain()
        os.environ["NURY_PRIVACY"] = "off"
        try:
            self.assertIs(make_client(p, PROTECTED), p)
        finally:
            del os.environ["NURY_PRIVACY"]
        self.assertIsInstance(make_client(p, PROTECTED), PrivacyClient)
        self.assertIs(make_client(p, PROTECTED, enabled=False), p)
        pc = PrivacyClient(p, PROTECTED, enabled=False)
        self.assertEqual(pc.ask("Zorana"), ("x", {}))


if __name__ == "__main__":
    unittest.main()
