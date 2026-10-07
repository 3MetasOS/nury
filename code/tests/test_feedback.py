"""The feedback capture: off by default, no names ever, whole drafts never. No network."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonet  # noqa: E402,F401
from nury import feedback as fb  # noqa: E402
from nury.privacy import PrivacyClient  # noqa: E402

CANARIES = ["Zorana", "Quimbley", "Thaddeus", "Ottilie", "555-0142", "canarymail", "Larkspur", "A123456789", "Brunhilda", "Vandersloot"]
PROTECTED = ["Zorana Quimbley", "Thaddeus Quimbley", "Ottilie"]
DRAFT = ("Zorana, la iglesia está con ustedes y con Thaddeus. Sabemos que hay mucho miedo esta noche. "
         "Si quieren orar juntos, pueden llamarme al (303) 555-0142. Estamos pensando en Ottilie y en toda la familia. "
         "No están solos.\n\n«Dios es nuestro amparo y fortaleza.»\n— Salmo 46:1, Reina-Valera 1909\n\n"
         "Este salmo habla de que Dios está presente.\n\nNury es un asistente de IA, no es abogado, pastor, consejero ni terapeuta.")
FINAL = ("Zorana, la iglesia está con ustedes. Sabemos que hay mucho miedo esta noche. No están solos. "
         "Escriba a zorana.q@canarymail.org si lo prefiere. Hable con Brunhilda Vandersloot, que vive en 4821 Larkspur Avenue.\n\n"
         "«Dios es nuestra fuerza.»\n— Salmo 46:1, Reina-Valera 1909\n\n"
         "Este salmo habla de que Dios está presente.\n\nNury es un asistente de IA, no es abogado, pastor, consejero ni terapeuta.")


def client():
    return PrivacyClient(None, PROTECTED)


def events(stage="pastoral"):
    return [{"kind": "draft_rejected", "stage": stage, "attempt": 1, "visible_to_pastor": False, "reason_categories": ["banned_phrase", "jev_promises_action"]},
            {"kind": "jev_gate", "stage": stage, "attempt": 2, "question": "promises_action", "probability": 0.34, "decision": "uncertain"},
            {"kind": "jev_gate", "stage": "triage", "attempt": 1, "question": "assumes_facts", "probability": 0.1, "decision": "pass"}]


class Base(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        nonet.scrub()

    def tearDown(self):
        shutil.rmtree(self.root)
        os.environ.pop("NURY_FEEDBACK", None)

    def on(self, m="on"):
        os.environ["NURY_FEEDBACK"] = m

    def lines(self):
        out = []
        for f in sorted(Path(self.root).glob("feedback-*.jsonl")):
            out += [json.loads(x) for x in f.read_text().splitlines()]
        return out

    def blob(self):
        return "".join(f.read_text() for f in Path(self.root).glob("feedback-*.jsonl"))


class Switch(Base):
    def test_it_is_off_by_default_and_writes_nothing(self):
        self.assertEqual(fb.mode(), "off")
        self.assertFalse(fb.record_gate("pastoral", "edit", DRAFT, FINAL, client(), [], root=self.root))
        self.assertFalse(fb.record_chip("pastoral", "too_long", root=self.root))
        self.assertFalse(fb.record_outcome("detention", "unknown", root=self.root))
        self.assertEqual(list(Path(self.root).iterdir()), [])

    def test_modes(self):
        for v, want in (("on", "sentences"), ("counts", "counts"), ("off", "off"), ("nonsense", "off"), ("", "off")):
            os.environ["NURY_FEEDBACK"] = v
            self.assertEqual(fb.mode(), want, v)

    def test_the_approved_consent_sentence_and_the_chips(self):
        self.assertEqual(fb.CONSENT_SENTENCE, "Nury also records what you change, without names, to improve its drafts; a person reviews every change before it is used.")
        self.assertEqual(fb.CHIPS, ("good_as_is", "too_long", "not_my_voice", "wrong_tone", "inaccurate"))
        self.assertEqual([fb.CHIP_LABELS[c] for c in fb.CHIPS], ["Good as is", "Too long", "Not my voice", "Wrong tone", "Inaccurate"])


class Sentences(Base):
    def test_an_edit_stores_only_changed_sentences_with_tokens_and_the_counts_and_events(self):
        self.on()
        self.assertTrue(fb.record_gate("pastoral", "edit", DRAFT, FINAL, client(), events(), playbook="detention", language="es",
                                       run_id="abc123", reason_chip="too_long", outcome_label="did not go as hoped", root=self.root))
        (ln,) = self.lines()
        self.assertEqual((ln["type"], ln["mode"], ln["action"], ln["stage"], ln["playbook"], ln["reason_chip"], ln["revision_result"]),
                         ("gate", "sentences", "edit", "pastoral", "detention", "too_long", "did_not_go_as_hoped"))
        self.assertEqual(ln["rule_categories"], {"banned_phrase": 1, "jev_promises_action": 1})
        self.assertEqual(ln["jev"], {"promises_action": {"decisions": {"uncertain": 1}, "probs": [0.34]}})
        self.assertIn("verse_changed", ln["tags"])
        self.assertTrue(ln["counts"]["removed"] + ln["counts"]["replaced"] >= 1)
        self.assertTrue(ln["diff"]["removed"] or ln["diff"]["replaced"])
        blob = self.blob()
        self.assertNotIn("Dios es nuestro amparo", blob)         # the verse is never stored, only the tag
        self.assertNotIn("Nury es un asistente", blob)           # the disclaimer is not a change
        self.assertNotIn("Este salmo habla", blob)               # an unchanged sentence is never stored
        self.assertTrue(all(s.count("[") == s.count("]") for s in ln["diff"]["removed"]))

    def test_no_canary_name_phone_email_address_or_id_reaches_the_file_in_either_mode(self):
        for m in ("on", "counts"):
            self.on(m)
            fb.record_gate("pastoral", "edit", DRAFT, FINAL, client(), events(), playbook="detention", language="es", root=self.root)
        blob = self.blob()
        self.assertGreaterEqual(len(self.lines()), 2)
        for c in CANARIES:
            self.assertFalse(c.lower() in blob.lower(), f"LEAK of {c!r}")

    def test_a_sentence_with_a_name_the_pastor_typed_that_nobody_protected_is_dropped_and_counted(self):
        self.on()
        draft = "La iglesia está con ustedes. Llame cuando quiera."
        final = "La iglesia está con ustedes. Hable con Brunhilda Vandersloot, que conoce su caso."
        fb.record_gate("pastoral", "edit", draft, final, client(), [], root=self.root)
        (ln,) = self.lines()
        self.assertGreaterEqual(ln["dropped_unsafe"], 1)
        self.assertFalse("brunhilda" in self.blob().lower())
        self.assertEqual(ln["diff"]["added"] + [p["to"] for p in ln["diff"]["replaced"]], [])

    def test_a_phone_or_email_in_an_added_sentence_is_tokenized_before_it_can_be_stored(self):
        self.on()
        fb.record_gate("pastoral", "edit", "Estamos con ustedes.", "Estamos con ustedes. Llame al (720) 555-0199.", client(), [], root=self.root)
        blob = self.blob()
        self.assertNotIn("555-0199", blob)

    def test_approve_and_stop_store_no_diff(self):
        self.on()
        fb.record_gate("triage", "approve", DRAFT, DRAFT, client(), [], root=self.root)
        fb.record_gate("rights", "stop", DRAFT, None, client(), [], root=self.root)
        a, s = self.lines()
        self.assertEqual((a["action"], a["counts"], a["tags"], "diff" in a), ("approve", None, [], False))
        self.assertEqual((s["action"], s["counts"]), ("stop", None))

    def test_without_a_pseudonymizer_sentence_mode_degrades_to_counts(self):
        self.on()
        fb.record_gate("pastoral", "edit", DRAFT, FINAL, None, [], root=self.root)
        (ln,) = self.lines()
        self.assertEqual((ln["mode"], ln["degraded"], "diff" in ln), ("counts", True, False))
        self.assertFalse("zorana" in self.blob().lower())


class Counts(Base):
    def test_counts_mode_stores_no_sentence_at_all(self):
        self.on("counts")
        fb.record_gate("pastoral", "edit", DRAFT, FINAL, client(), events(), playbook="detention", language="es", root=self.root)
        (ln,) = self.lines()
        self.assertEqual(ln["mode"], "counts")
        self.assertNotIn("diff", ln)
        self.assertIn("counts", ln)
        for tok in self.blob().replace('"', " ").replace(",", " ").split():
            self.assertLess(len(tok), 60)
        for v in json.dumps(ln).split('"'):
            self.assertFalse(" " in v.strip() and len(v.split()) > 2, v)      # no sentence-like string


class Small(Base):
    def test_chips_and_outcomes(self):
        self.on()
        self.assertTrue(fb.record_chip("pastoral", "not_my_voice", playbook="hospital", language="es", root=self.root))
        self.assertFalse(fb.record_chip("pastoral", "I did not like it", root=self.root))
        self.assertTrue(fb.record_outcome("detention", "went as hoped", language="es", root=self.root))
        self.assertTrue(fb.record_outcome("detention", "did_not_go_as_hoped", root=self.root))
        self.assertFalse(fb.record_outcome("detention", "my note about the family", root=self.root))
        c, o1, o2 = self.lines()
        self.assertEqual((c["type"], c["reason_chip"]), ("chip", "not_my_voice"))
        self.assertEqual((o1["revision_result"], o2["revision_result"]), ("went_as_hoped", "did_not_go_as_hoped"))
        self.assertNotIn("note", self.blob())

    def test_an_invalid_chip_or_action_is_not_stored_as_given(self):
        self.on()
        fb.record_gate("pastoral", "approve", DRAFT, DRAFT, client(), [], reason_chip="free text from the pastor", root=self.root)
        self.assertIsNone(self.lines()[0]["reason_chip"])
        self.assertFalse(fb.record_gate("pastoral", "delete", DRAFT, DRAFT, client(), [], root=self.root))

    def test_it_never_raises_and_the_file_is_append_only(self):
        self.on()
        self.assertFalse(fb.record_gate("pastoral", "edit", DRAFT, FINAL, client(), [], root="/dev/null/nope"))
        fb.record_gate("triage", "approve", DRAFT, DRAFT, client(), [], root=self.root)
        first = self.blob()
        fb.record_gate("rights", "approve", DRAFT, DRAFT, client(), [], root=self.root)
        self.assertTrue(self.blob().startswith(first))

    def test_retention_prunes_old_daily_files_only(self):
        self.on()
        fb.record_gate("triage", "approve", DRAFT, DRAFT, client(), [], root=self.root)
        old = (datetime.now(timezone.utc) - timedelta(days=40)).strftime("%Y%m%d")
        (Path(self.root) / f"feedback-{old}.jsonl").write_text("{}\n")
        gone = fb.prune(30, root=self.root)
        self.assertEqual(gone, [f"feedback-{old}.jsonl"])
        self.assertEqual(len(self.lines()), 1)

    def test_read_all_filters_by_time(self):
        self.on()
        fb.record_gate("triage", "approve", DRAFT, DRAFT, client(), [], root=self.root)
        self.assertEqual(len(fb.read_all(self.root)), 1)
        self.assertEqual(len(fb.read_all(self.root, since=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat())), 0)


if __name__ == "__main__":
    unittest.main()
