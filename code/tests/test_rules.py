"""The rules registry (metadata only). No network."""
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonet  # noqa: E402,F401
from nury import checks, jev_gate, rules  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


class Rules(unittest.TestCase):
    def setUp(self):
        self.all = rules.describe_all()

    def test_every_named_check_and_jev_question_is_described_and_nothing_else_is_missing(self):
        names = {e["name"] for e in self.all}
        self.assertTrue(set(checks.REGISTRY) <= names)
        self.assertTrue({"jev_" + q for q in jev_gate.QUESTIONS} <= names)
        self.assertEqual(len(names), len(self.all))
        self.assertEqual(sorted(rules.CHECKS), sorted(checks.REGISTRY))

    def test_every_entry_has_a_plain_short_explanation_a_kind_and_a_real_file(self):
        for e in self.all:
            self.assertIn(e["kind"], ("floor", "check", "classifier"))
            self.assertTrue(10 < len(e["explanation"]) < 520, e["name"])
            self.assertTrue((ROOT / e["where"]).is_file(), e["name"])
            self.assertNotRegex(e["explanation"], r"[—–]", e["name"])

    def test_every_check_a_stage_uses_is_in_the_registry_and_says_where(self):
        used = {e["name"]: e for e in self.all if e["stages"]}
        self.assertIn("triage_facts_only", used)
        self.assertEqual({s["stage"] for s in used["no_providence_claims"]["stages"]}, {"pastoral"})
        self.assertEqual(sorted(used["jev_gives_medical_advice"]["playbooks"]), ["hospital"])
        self.assertEqual(sorted(used["jev_gives_legal_advice"]["playbooks"]), ["detention"])
        self.assertEqual(sorted(used["no_agency_names"]["playbooks"]), ["detention"])
        self.assertFalse([e["name"] for e in self.all if e["kind"] == "check" and not e["stages"]])

    def test_floor_rules_are_listed_and_describing_changes_nothing(self):
        floor = [e["name"] for e in self.all if e["kind"] == "floor"]
        for n in ("banned_phrases", "three_attempts_then_the_pastor", "no_send_path", "tokens_not_names", "disclaimer_on_every_output"):
            self.assertIn(n, floor)
        before = dict(checks.REGISTRY)
        rules.describe_all()
        self.assertEqual(before, checks.REGISTRY)


if __name__ == "__main__":
    unittest.main()
