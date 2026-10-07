"""The run ledger: what is recorded, and the proof that text never is. No network."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonet  # noqa: E402,F401
from app import ops_api  # noqa: E402
from nury import ledger  # noqa: E402
from nury.audit import AuditLog  # noqa: E402
from nury.engine import UNSAFE_SUFFIX, CaseState, run_pipeline, run_scripted  # noqa: E402
from test_core import FakeClient  # noqa: E402

CANARIES = ["Zorana", "Quimbley", "Thaddeus", "Ottilie", "555-0142", "canarymail", "Larkspur", "A123456789"]
INTAKE = ("Zorana Quimbley called from (303) 555-0142, email zorana.q@canarymail.org. Her husband Thaddeus Quimbley, "
          "A-number A123456789, was taken from 4821 Larkspur Avenue. Their daughter Ottilie is 8.")


def metrics(**kw):
    m = {"attempts": 1, "retries": 0, "self_corrections": 0, "latency_s": 4.0, "input_tokens": 1000, "output_tokens": 200,
         "cost_usd": 0.01, "skills": [{"name": "voice", "version": "1.0.0"}], "jev_ms": 150, "jev_calls": 1}
    m.update(kw)
    return m


def rec(stage="triage", status="approved", cats=(), escalated=False, **kw):
    return SimpleNamespace(stage_id=stage, status=status, reason_categories=list(cats), escalated=escalated, metrics=metrics(**kw))


def jev(stage, q, p, dec, attempt=1):
    return {"kind": "jev_gate", "stage": stage, "attempt": attempt, "question": q, "probability": p, "decision": dec}


class Base(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root)

    def lines(self):
        f = Path(self.root) / ledger.FILE
        return [json.loads(x) for x in f.read_text().splitlines()] if f.is_file() else []


class Lines(Base):
    def test_a_stage_line_has_the_fields_and_no_text(self):
        events = [jev("triage", "assumes_facts", 0.33, "uncertain"), {"kind": "scripture", "stage": "triage", "verse": "psa46_1", "provider": "youversion"}]
        r = ledger.Recorder("detention", "es", self.root)
        self.assertTrue(r.stage_done(rec(cats=["banned_phrase", "banned_phrase", "jev_assumes_facts"], attempts=3), events, duration_ms=5200))
        self.assertTrue(r.finish({"outcome": "package_complete", "failed_stage": None}))
        s, run = self.lines()
        self.assertEqual((s["type"], s["playbook"], s["stage"], s["language"], s["attempts"], s["escalated"]), ("stage", "detention", "triage", "es", 3, False))
        self.assertEqual(s["rule_categories"], {"banned_phrase": 2, "jev_assumes_facts": 1})
        self.assertEqual(s["jev"]["assumes_facts"], {"decisions": {"uncertain": 1}, "max_probability": 0.33, "last_probability": 0.33, "probs": [0.33]})
        self.assertEqual((s["tokens_in"], s["tokens_out"], s["cost_usd"], s["latency_s"], s["jev_ms"], s["duration_ms"]), (1000, 200, 0.01, 4.0, 150, 5200))
        self.assertEqual((s["skills"], s["scripture_provider"]), (["voice@1.0.0"], "youversion"))
        self.assertTrue(s["ts"].endswith("+00:00"))
        self.assertEqual((run["type"], run["outcome"], run["stages"], run["cost_usd"], run["run"]), ("run", "package_complete", 1, 0.01, s["run"]))
        self.assertGreaterEqual(run["duration_ms"], 0)

    def test_the_run_id_is_random_and_not_derived_from_the_case(self):
        a, b = ledger.new_run_id(), ledger.new_run_id()
        self.assertNotEqual(a, b)
        self.assertRegex(a, r"^[0-9a-f]{12}$")

    def test_unavailable_and_skipped_jev_decisions_are_counted(self):
        r = ledger.Recorder("detention", "es", self.root)
        r.stage_done(rec(), [{"kind": "jev_gate", "stage": "triage", "attempt": 1, "question": "*", "probability": None, "decision": "unavailable", "reason": "Timeout: slow"}])
        self.assertEqual(self.lines()[0]["jev"], {"*": {"decisions": {"unavailable": 1}, "max_probability": 0.0, "last_probability": None, "probs": []}})

    def test_a_string_that_is_not_a_slug_stops_the_write_and_nothing_is_written(self):
        r = ledger.Recorder("detention", "es", self.root)
        self.assertFalse(r.stage_done(rec(cats=["Zorana called from 303"]), []))
        self.assertFalse(r.stage_done(rec(stage="triage for Maria Lopez"), []))
        self.assertEqual(self.lines(), [])
        with self.assertRaises(ledger.LedgerError):
            ledger._write({"type": "stage", "note": "Zorana Quimbley"}, self.root)
        with self.assertRaises(ledger.LedgerError):
            ledger._write({"type": "stage", "nested": {"text": "a draft sentence"}}, self.root)
        self.assertEqual(self.lines(), [])

    def test_the_ledger_is_append_only(self):
        r = ledger.Recorder("detention", "es", self.root)
        r.stage_done(rec(), [])
        first = (Path(self.root) / ledger.FILE).read_bytes()
        r.stage_done(rec(stage="rights"), [])
        r.finish({"outcome": "package_complete", "failed_stage": None})
        again = (Path(self.root) / ledger.FILE).read_bytes()
        self.assertTrue(again.startswith(first))
        self.assertEqual(len(self.lines()), 3)

    def test_a_ledger_failure_never_breaks_a_run(self):
        r = ledger.Recorder("detention", "es", "/dev/null/not-a-folder")
        self.assertFalse(r.stage_done(rec(), []))
        self.assertFalse(r.finish({"outcome": "package_complete", "failed_stage": None}))


class Leak(Base):
    def test_no_canary_name_phone_email_or_id_reaches_the_ledger_across_a_real_run_with_a_rejection(self):
        st = CaseState(INTAKE, "es")
        au = AuditLog()
        results = run_pipeline("detention", st, client=FakeClient(), audit=au,
                               fault_injection={"stage": "rights", "times": 1, "draft_suffix": UNSAFE_SUFFIX + " Zorana Quimbley will be freed. Call 555-0142."})
        self.assertTrue(any(e["kind"] == "draft_rejected" for e in au.events))     # the audit holds the rejected text, the ledger must not
        rid = ledger.record_run("detention", "es", st, results, au.events, root=self.root)
        self.assertIsNotNone(rid)
        blob = (Path(self.root) / ledger.FILE).read_text()
        for c in CANARIES:
            self.assertFalse(c.lower() in blob.lower(), f"LEAK of {c!r}")
        for ln in blob.splitlines():
            self.assertNotIn(" ", ln.replace(": ", "").replace(", ", ""))        # no sentence-like value anywhere
        rows = self.lines()
        self.assertEqual(len([r for r in rows if r["type"] == "stage"]), 5)
        rights = [r for r in rows if r["type"] == "stage" and r["stage"] == "rights"][0]
        self.assertEqual(rights["attempts"], 2)
        self.assertIn("banned_phrase", rights["rule_categories"])

    def test_the_stage_line_for_an_escalation_carries_categories_only(self):
        st = CaseState(INTAKE, "es")
        au = AuditLog()
        results = run_pipeline("detention", st, client=FakeClient(), audit=au,
                               fault_injection={"stage": "rights", "times": 3, "draft_suffix": UNSAFE_SUFFIX + " Thaddeus Quimbley"})
        ledger.record_run("detention", "es", st, results, au.events, root=self.root)
        rows = self.lines()
        run = [r for r in rows if r["type"] == "run"][0]
        self.assertEqual((run["outcome"], run["failed_stage"]), ("escalated", "rights"))
        self.assertTrue([r for r in rows if r["type"] == "stage" and r["escalated"]])
        self.assertFalse("thaddeus" in json.dumps(rows).lower())


class Summary(Base):
    def seed(self):
        for i, (outcome, att) in enumerate([("package_complete", 1), ("package_complete", 2), ("escalated", 3)]):
            r = ledger.Recorder("detention", "es", self.root)
            ev = [jev("triage", "assumes_facts", 0.2 + 0.2 * i, "pass" if i == 0 else "uncertain" if i == 1 else "reject"),
                  {"kind": "scripture", "stage": "pastoral", "verse": "x", "provider": "youversion" if i < 2 else "bank"}]
            r.stage_done(rec("triage", status="escalated" if outcome == "escalated" else "approved", attempts=att, cats=["banned_phrase"] * (att - 1), latency_s=2.0 + i, cost_usd=0.02, escalated=outcome == "escalated"), ev)
            r.stage_done(rec("pastoral", latency_s=5.0, cost_usd=0.03), ev)
            r.finish({"outcome": outcome, "failed_stage": "triage" if outcome == "escalated" else None})

    def test_totals(self):
        self.seed()
        s = ledger.summarize(root=self.root)
        self.assertEqual((s["runs"], s["stages"], s["packages"]), (3, 6, 2))
        self.assertEqual(s["cost_per_package_usd"], 0.05)
        self.assertEqual(s["attempts_distribution"], {"1": 4, "2": 1, "3": 1})
        self.assertEqual(s["escalation_rate_runs"], round(1 / 3, 4))
        self.assertEqual(s["escalation_rate_stages"], round(1 / 6, 4))
        self.assertEqual(s["rejections_by_category"], {"banned_phrase": 2})            # stages where the category fired
        self.assertEqual(s["rejection_rate_by_category"], {"banned_phrase": round(2 / 6, 4)})
        self.assertEqual(s["jev_by_question"]["assumes_facts"]["reject"], 1)
        self.assertEqual(s["scripture_provider_mix"], {"bank": 1, "youversion": 2})
        lat = s["latency_s_by_stage"]["triage"]
        self.assertEqual((lat["n"], lat["p50"], lat["p95"]), (3, 3.15, 4.15))      # 2.15, 3.15, 4.15 including 150 ms of Jev

    def test_since_filters_by_time(self):
        self.seed()
        self.assertEqual(ledger.summarize(since=3600, root=self.root)["runs"], 3)
        future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(timespec="milliseconds")
        self.assertEqual(ledger.summarize(since=future, root=self.root)["runs"], 0)
        self.assertEqual(ledger.summarize(since=timedelta(seconds=3600), root=self.root)["runs"], 3)

    def test_empty_ledger_is_fine(self):
        s = ledger.summarize(root=self.root)
        self.assertEqual((s["runs"], s["cost_per_package_usd"], s["escalation_rate_runs"]), (0, None, None))


class View(Base):
    def test_the_ops_view_has_exactly_the_agreed_shape_and_numbers(self):
        Summary.seed(self)
        v = ledger.ops_view(root=self.root)
        self.assertEqual(sorted(v), ["cost_series", "generated", "headline", "jev_by_question", "latency_by_stage", "provider_mix",
                                     "rejections_by_category", "runs", "source"])
        self.assertEqual(sorted(v["headline"]), ["cost_avg", "cost_p95", "escalation_rate", "latency_p50_s", "latency_p95_s", "packages", "rejection_rate"])
        h = v["headline"]
        self.assertEqual((h["packages"], h["cost_avg"], h["cost_p95"], h["escalation_rate"]), (2, 0.05, 0.05, round(1 / 3, 4)))
        # six stages wrote 1 + 2 + 3 + 3 = 9 drafts... attempts: triage 1,2,3 and pastoral 1,1,1 = 9 written; accepted 5 (the escalated one has none)
        self.assertEqual(h["rejection_rate"], round(4 / 9, 4))
        self.assertEqual(v["rejections_by_category"], {"banned_phrase": 3})
        self.assertEqual(v["jev_by_question"]["assumes_facts"]["reject"], 1)
        self.assertEqual(len(v["jev_by_question"]["assumes_facts"]["probs"]), 3)
        self.assertEqual(v["provider_mix"], {"youversion": 2, "bank": 1, "none": 0})
        self.assertEqual([x["outcome"] for x in v["runs"]], ["escalated", "complete", "complete"])
        self.assertEqual(sorted(v["runs"][0]), ["attempts", "cost", "crisis", "latency_s", "outcome", "stages", "t"])
        self.assertEqual(len(v["cost_series"]), 2)
        self.assertLessEqual(v["cost_series"][0]["t"], v["cost_series"][1]["t"])
        self.assertEqual(sorted(v["latency_by_stage"][0]), ["n", "p50", "p95", "stage"])

    def test_the_view_holds_no_text_and_an_empty_ledger_is_fine(self):
        Summary.seed(self)
        blob = json.dumps(ledger.ops_view(root=self.root))
        self.assertNotRegex(blob, r"[A-Z][a-z]+ [a-z]+ [a-z]+")
        e = ledger.ops_view(root=self.root + "/none")
        self.assertEqual((e["headline"]["packages"], e["headline"]["cost_avg"], e["runs"]), (0, None, []))


class OpsApi(Base):
    def test_get_returns_the_summary_and_nothing_else_is_allowed(self):
        os.environ["NURY_LEDGER_DIR"] = self.root
        try:
            Summary.seed(self)
            status, ctype, body = ops_api.handle("GET", "/api/ops?since=3600")
            self.assertEqual((status, ctype.split(";")[0]), (200, "application/json"))
            v = json.loads(body)
            self.assertEqual((v["source"], v["headline"]["packages"], len(v["runs"])), ("ledger", 2, 3))
            for m in ("POST", "PUT", "DELETE"):
                self.assertEqual(ops_api.handle(m, "/api/ops")[0], 405)
            self.assertEqual(ops_api.handle("GET", "/api/ops?since=yesterday")[0], 400)
        finally:
            os.environ.pop("NURY_LEDGER_DIR", None)


if __name__ == "__main__":
    unittest.main()
