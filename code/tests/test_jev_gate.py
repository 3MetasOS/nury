"""Jev as a run-time classifier gate. No network: requests.post is replaced by a stub."""
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonet  # noqa: E402,F401
import requests  # noqa: E402
from nury import jev_gate  # noqa: E402
from nury.audit import AuditLog  # noqa: E402
from nury.engine import CaseState, run_scripted, run_stage  # noqa: E402
from test_core import CANNED, TRIAGE, FakeClient  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PAST = "VERSE: NONE\nWHY:\nMESSAGE: María, la iglesia está con ustedes. No están solos."


class Jev:
    """Stub for the Jev API. `probs` maps a question to the probability of yes (default 0.1). `mode` can break it."""
    def __init__(self, probs=None, mode="ok", default=0.1):
        self.probs, self.mode, self.default, self.bodies, self.headers, self.calls = probs or {}, mode, default, [], [], 0

    def __call__(self, url, json=None, headers=None, timeout=None):
        self.calls += 1
        self.bodies.append(json)
        self.headers.append((url, headers, timeout))
        if self.mode == "timeout":
            raise requests.exceptions.Timeout("slow")
        outer = self

        class R:
            status_code = 500 if outer.mode == "500" else 200

            def json(self_):
                if outer.mode == "garbage":
                    return {"nope": 1}
                return {"answers": {q: {"type": "noul", "noul": outer.probs.get(q, outer.default)} for q in json["questions"]},
                        "usage": {"total_tokens": 7}}
        return R()


def gate_on():
    os.environ.update(NURY_JEV_GATE="on", JEV_API_KEY="test-jev-key-not-real")


class Gate(unittest.TestCase):
    def tearDown(self):
        nonet.scrub()

    def pastoral(self, jev, canned=None):
        gate_on()
        st = CaseState("intake", "es")
        st.approved["triage"] = TRIAGE
        au = AuditLog()
        with mock.patch.object(requests, "post", jev):
            rec = run_stage("pastoral", st, client=FakeClient(dict(CANNED, pastoral=PAST)), audit=au)
        return rec, au, st

    def test_a_probability_of_point_six_rejects_with_a_jev_category_and_the_loop_regenerates(self):
        class Flip(Jev):
            def __call__(s, url, json=None, headers=None, timeout=None):
                s.default = 0.6 if s.calls == 0 else 0.1          # first draft rejected, regenerated draft passes
                return super().__call__(url, json=json, headers=headers, timeout=timeout)
        rec, au, _ = self.pastoral(Flip())
        self.assertEqual(rec.status, "approved")
        self.assertEqual(rec.metrics["attempts"], 2)
        self.assertEqual(sorted({v["category"] for v in rec.attempts[0]["violations"]}),
                         ["jev_claims_counselor", "jev_claims_pastoral_office", "jev_predicts_outcome", "jev_promises_action"])
        rej = [e for e in au.events if e["kind"] == "jev_gate" and e["decision"] == "reject"]
        self.assertEqual(len(rej), 4)
        self.assertTrue(all(e["attempt"] == 1 and e["stage"] == "pastoral" and e["probability"] == 0.6 for e in rej))
        self.assertEqual(rec.metrics["jev_calls"], 2)
        self.assertGreaterEqual(rec.metrics["jev_ms"], 0)

    def test_a_reject_always_escalates_after_three_attempts(self):
        rec, au, _ = self.pastoral(Jev(default=0.9))
        self.assertEqual(rec.status, "escalated")
        self.assertIsNone(rec.draft)
        self.assertEqual(rec.metrics["attempts"], 3)

    def test_the_line_is_point_five_exactly(self):
        for p, want in ((0.49, "approved"), (0.50, "escalated"), (0.51, "escalated")):
            rec, _, _ = self.pastoral(Jev(probs={"promises_action": p}))
            self.assertEqual(rec.status, want, p)
        self.assertEqual([jev_gate.decide(x) for x in (0.0, 0.29, 0.30, 0.49, 0.5, 1.0)],
                         ["pass", "pass", "uncertain", "uncertain", "reject", "reject"])

    def test_assumes_facts_rejects_at_point_six_and_every_other_question_at_point_five(self):
        self.assertEqual(jev_gate.line("assumes_facts"), 0.60)
        for q in jev_gate.QUESTIONS:
            if q != "assumes_facts":
                self.assertEqual(jev_gate.line(q), 0.50, q)
        self.assertEqual([jev_gate.decide(0.55, "assumes_facts"), jev_gate.decide(0.55, "gives_legal_advice"),
                          jev_gate.decide(0.59, "assumes_facts"), jev_gate.decide(0.60, "assumes_facts"),
                          jev_gate.decide(0.29, "assumes_facts"), jev_gate.decide(0.30, "assumes_facts")],
                         ["uncertain", "reject", "uncertain", "reject", "pass", "uncertain"])

    def test_in_a_run_0_55_passes_triage_and_rejects_a_legal_advice_draft(self):
        gate_on()
        st = CaseState("intake", "es")
        with mock.patch.object(requests, "post", Jev(probs={"assumes_facts": 0.55})):
            rec = run_stage("triage", st, client=FakeClient(), audit=AuditLog())
        self.assertEqual(rec.status, "approved")
        st.approved.update(triage=TRIAGE)
        au = AuditLog()
        with mock.patch.object(requests, "post", Jev(probs={"gives_legal_advice": 0.55})):
            rec2 = run_stage("rights", st, client=FakeClient(), audit=au)
        self.assertEqual(rec2.status, "escalated")
        self.assertIn("jev_gives_legal_advice", rec2.reason_categories)

    def test_point_two_passes_and_point_four_passes_but_is_logged_uncertain(self):
        rec, au, _ = self.pastoral(Jev(probs={"promises_action": 0.4}, default=0.2))
        self.assertEqual(rec.status, "approved")
        dec = {e["question"]: e["decision"] for e in au.events if e["kind"] == "jev_gate"}
        self.assertEqual(dec["promises_action"], "uncertain")
        self.assertEqual({v for k, v in dec.items() if k != "promises_action"}, {"pass"})

    def test_unavailable_fails_open_logs_why_and_later_stages_skip_the_gate(self):
        gate_on()
        for mode in ("timeout", "500", "garbage"):
            jev = Jev(mode=mode)
            with mock.patch.object(requests, "post", jev):
                st, rs, au = run_scripted("intake", client=FakeClient())
            self.assertEqual(st.outcome["outcome"], "package_complete", mode)
            ev = [e for e in au.events if e["kind"] == "jev_gate"]
            self.assertEqual(ev[0]["decision"], "unavailable", mode)
            self.assertTrue(ev[0]["reason"], mode)
            self.assertEqual({e["decision"] for e in ev[1:]}, {"skipped"}, mode)
            self.assertEqual(jev.calls, 1, mode)                       # one failed call, then the run stops asking
            self.assertTrue(all(r.status == "approved" for r in rs), mode)

    def test_the_timeout_is_eight_seconds_and_the_key_goes_in_the_header_only(self):
        jev = Jev()
        self.pastoral(jev)
        url, headers, timeout = jev.headers[0]
        self.assertEqual(timeout, 8.0)
        self.assertEqual(url, "https://api.typesafe.ai/v1/systemone")
        self.assertEqual(headers["Authorization"], "Bearer test-jev-key-not-real")
        self.assertNotIn("test-jev-key-not-real", str(jev.bodies))

    def test_the_default_is_on_only_when_a_key_exists_and_the_switch_wins(self):
        self.assertFalse(jev_gate.enabled({}))
        self.assertTrue(jev_gate.enabled({"JEV_API_KEY": "k"}))
        self.assertFalse(jev_gate.enabled({"JEV_API_KEY": "k", "NURY_JEV_GATE": "off"}))
        self.assertTrue(jev_gate.enabled({"NURY_JEV_GATE": "on"}))
        jev = Jev()
        os.environ["NURY_JEV_GATE"] = "off"
        os.environ["JEV_API_KEY"] = "k"
        st = CaseState("intake", "es")
        st.approved["triage"] = TRIAGE
        with mock.patch.object(requests, "post", jev):
            run_stage("pastoral", st, client=FakeClient(dict(CANNED, pastoral=PAST)))
        self.assertEqual(jev.calls, 0)

    def test_one_batched_call_per_attempt_with_the_stage_questions(self):
        jev = Jev()
        gate_on()
        with mock.patch.object(requests, "post", jev):
            st, rs, au = run_scripted("intake", client=FakeClient())
        self.assertEqual(jev.calls, 5)
        self.assertEqual([sorted(b["questions"]) for b in jev.bodies],
                         [["assumes_facts"], ["assumes_facts", "gives_legal_advice", "predicts_outcome"], ["assumes_facts"],
                          ["gives_legal_advice"], ["claims_counselor", "claims_pastoral_office", "predicts_outcome", "promises_action"]])
        self.assertEqual(sum(r.metrics["jev_calls"] for r in rs), 5)
        self.assertTrue(all(e["kind"] != "jev_gate" or {"stage", "attempt", "question", "probability", "decision"} <= set(e) for e in au.events))

    def test_a_draft_the_floor_rejects_never_reaches_jev(self):
        jev = Jev()
        gate_on()
        st = CaseState("intake", "es")
        st.approved["triage"] = TRIAGE
        with mock.patch.object(requests, "post", jev):
            rec = run_stage("pastoral", st, client=FakeClient(dict(CANNED, pastoral=PAST + " Su caso va a ser ganado.")))
        self.assertEqual(rec.status, "escalated")
        self.assertEqual(jev.calls, 0)

    def test_hospital_asks_the_medical_questions(self):
        from test_core import HCANNED, HFake
        jev = Jev()
        gate_on()
        with mock.patch.object(requests, "post", jev):
            st, rs, au = run_scripted("intake", client=HFake(HCANNED), playbook="hospital")
        asked = {q for b in jev.bodies for q in b["questions"]}
        self.assertTrue({"gives_medical_advice", "predicts_medical_outcome", "assumes_facts", "claims_pastoral_office", "promises_action"} <= asked)
        self.assertFalse(asked & {"gives_legal_advice", "predicts_outcome"})


class Wording(unittest.TestCase):
    def test_the_gate_asks_the_same_questions_the_eval_judges_were_validated_on(self):
        sys.path.insert(0, str(ROOT / "evaluations"))
        from judges import jev_judges as ej
        for q, text in jev_gate.QUESTIONS.items():
            self.assertEqual(text, ej.NOUL[q], q)
            self.assertEqual(jev_gate.CRITERIA.get(q), ej.NOUL_CRITERIA.get(q), q)

    def test_every_stage_question_has_a_reason_and_a_definition(self):
        from nury.engine import get_playbook
        for pid in ("detention", "hospital"):
            pb = get_playbook(pid)
            for s in pb.stages:
                self.assertTrue(s.jev, (pid, s.id))
                for q in s.jev:
                    self.assertIn(q, jev_gate.REASONS)
                    self.assertIn(q, jev_gate.QUESTIONS)

    def test_the_loader_refuses_an_unknown_question(self):
        from nury import playbook as pbm
        with self.assertRaises(pbm.PlaybookError):
            pbm._jev({"id": "x", "jev": ["nope"]})


if __name__ == "__main__":
    unittest.main()
