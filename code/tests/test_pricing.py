"""Prices as data, and cost on each stage. No network."""
import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonet  # noqa: E402,F401
from nury import pricing  # noqa: E402
from nury.audit import AuditLog  # noqa: E402
from nury.engine import CaseState, run_stage  # noqa: E402
from test_core import FakeClient  # noqa: E402


class Priced(FakeClient):
    def ask(self, user_input, instructions=None, **kw):
        t, meta = super().ask(user_input, instructions=instructions, **kw)
        return t, dict(meta, model="gloo-anthropic-claude-sonnet-4.6", input_tokens=1000, output_tokens=200)


class Pricing(unittest.TestCase):
    def setUp(self):
        for k in ("NURY_PRICE_IN", "NURY_PRICE_OUT"):
            os.environ.pop(k, None)

    def test_the_file_has_the_run_model_with_a_source_and_a_date_and_jev_is_not_quoted(self):
        t = json.loads((Path(pricing.__file__).parent / "pricing.json").read_text())
        m = t["models"]["gloo-anthropic-claude-sonnet-4.6"]
        self.assertEqual((m["input"], m["output"], t["per_tokens"], m["as_of"]), (3.0, 15.0, 1000000, "2026-10-06"))
        self.assertIn("Gloo", m["source"])
        self.assertIsNone(t["classifiers"]["jev"]["price"])
        self.assertEqual(pricing.jev_status(), "unknown, not quoted")

    def test_cost_is_tokens_times_the_table(self):
        self.assertEqual(pricing.cost_usd("gloo-anthropic-claude-sonnet-4.6", 1000, 200), round((1000 * 3 + 200 * 15) / 1e6, 6))
        self.assertEqual(pricing.cost_usd("gloo-anthropic-claude-sonnet-4.6", 0, 0), 0.0)

    def test_an_unknown_model_has_no_cost_and_nothing_is_guessed(self):
        for m in ("fake", None, "", "gpt-x"):
            self.assertIsNone(pricing.cost_usd(m, 1000, 200))

    def test_the_environment_override_still_wins(self):
        os.environ["NURY_PRICE_IN"], os.environ["NURY_PRICE_OUT"] = "1.0", "2.0"
        try:
            self.assertEqual(pricing.cost_usd("fake", 1000000, 1000000), 3.0)
            self.assertEqual(pricing.cost_usd("gloo-anthropic-claude-sonnet-4.6", 1000000, 0), 1.0)
        finally:
            os.environ.pop("NURY_PRICE_IN"), os.environ.pop("NURY_PRICE_OUT")

    def test_a_stage_gets_a_cost_from_the_table_and_the_model_is_recorded(self):
        st = CaseState("intake", "es")
        rec = run_stage("triage", st, client=Priced(), audit=AuditLog())
        self.assertEqual(rec.metrics["model"], "gloo-anthropic-claude-sonnet-4.6")
        self.assertEqual(rec.metrics["cost_usd"], round((rec.metrics["input_tokens"] * 3 + rec.metrics["output_tokens"] * 15) / 1e6, 6))
        self.assertGreater(rec.metrics["cost_usd"], 0)

    def test_a_stage_on_an_unpriced_model_keeps_cost_null_as_before(self):
        rec = run_stage("triage", CaseState("intake", "es"), client=FakeClient(), audit=AuditLog())
        self.assertEqual((rec.metrics["model"], rec.metrics["cost_usd"]), ("fake", None))

    def test_every_model_entry_is_complete(self):
        for name, m in pricing.table()["models"].items():
            self.assertTrue(m["source"] and m["as_of"] and m["input"] > 0 and m["output"] > 0, name)


if __name__ == "__main__":
    unittest.main()
