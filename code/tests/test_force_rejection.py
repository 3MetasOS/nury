"""The demo hook NURY_FORCE_REJECTION: '1' (one rejection after triage, as before) or 'stage:times' pairs (times 1 or 2: the third try
always passes). Test and demo only. No prompt, rule, check, gate or threshold is involved: the live checks reject the injected draft."""
import os
import sys
import threading
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonet  # noqa: E402,F401
from app import server  # noqa: E402
from nury.engine import forced_rejections, get_playbook, run_scripted  # noqa: E402
from test_core import CANNED, HCANNED, FakeClient, HFake  # noqa: E402


class Env:
    def __init__(self, value):
        self.value = value

    def __enter__(self):
        self.old = os.environ.get("NURY_FORCE_REJECTION")
        os.environ["NURY_FORCE_REJECTION"] = self.value

    def __exit__(self, *a):
        if self.old is None:
            os.environ.pop("NURY_FORCE_REJECTION", None)
        else:
            os.environ["NURY_FORCE_REJECTION"] = self.old


class Parser(unittest.TestCase):
    def setUp(self):
        self.det, self.hos = get_playbook("detention"), get_playbook("hospital")

    def test_one_is_the_old_behavior_and_empty_does_nothing(self):
        self.assertEqual(forced_rejections("1", self.det), {"rights": 1})
        self.assertEqual(forced_rejections("1", self.hos), {"info": 1})
        for v in ("", None, "  "):
            self.assertEqual(forced_rejections(v, self.det), {})

    def test_stage_times_pairs(self):
        self.assertEqual(forced_rejections("rights:2,checklist:1", self.det), {"rights": 2, "checklist": 1})
        self.assertEqual(forced_rejections(" rights : 2 , pastoral ", self.det), {"rights": 2, "pastoral": 1})        # spaces and a missing count (1)
        self.assertEqual(forced_rejections("info:2,resources:1", self.hos), {"info": 2, "resources": 1})

    def test_times_are_cut_to_two_and_zero_is_ignored_so_a_case_is_never_stopped(self):
        self.assertEqual(forced_rejections("rights:9,attorney:3", self.det), {"rights": 2, "attorney": 2})
        self.assertEqual(forced_rejections("rights:0,attorney:-1", self.det), {})

    def test_unknown_stages_and_bad_pairs_are_ignored_with_a_log_line(self):
        with self.assertLogs("nury", level="WARNING") as cm:
            out = forced_rejections("info:2,rights:1,nope:x,rights:two", self.det)
        self.assertEqual(out, {"rights": 1})                      # info is a hospital stage; 'rights:two' is not a number
        log = "\n".join(cm.output)
        self.assertIn("stage 'info' is not in playbook detention", log)
        self.assertIn("is not stage:times", log)


class FullRuns(unittest.TestCase):
    def attempts(self, fake, canned, pid, value):
        with Env(value):
            st, rs, au = run_scripted("Maria Lopez was detained in Aurora.", client=fake(canned), playbook=pid)
        return st, rs, au, {r.stage_id: r.metrics["attempts"] for r in rs}

    def test_two_forced_rejections_then_the_case_completes_in_detention(self):
        st, rs, au, att = self.attempts(FakeClient, CANNED, "detention", "rights:2,checklist:1")
        self.assertEqual(att, {"triage": 1, "rights": 3, "attorney": 1, "checklist": 2, "pastoral": 1})
        self.assertEqual(st.outcome["outcome"], "package_complete")
        inj = [(e["stage"], e["attempt"]) for e in au.events if e["kind"] == "fault_injected"]
        self.assertEqual(inj, [("rights", 1), ("rights", 2), ("checklist", 1)])
        rej = [(e["stage"], e["attempt"]) for e in au.events if e["kind"] == "draft_rejected"]
        self.assertEqual(rej, inj)                                  # the live checks refused each injected draft
        self.assertTrue(all(e["visible_to_pastor"] is False for e in au.events if e["kind"] == "draft_rejected"))

    def test_the_same_in_hospital_and_the_old_value_still_means_one(self):
        st, rs, au, att = self.attempts(HFake, HCANNED, "hospital", "info:2,pastoral:1")
        self.assertEqual(att, {"triage": 1, "info": 3, "resources": 1, "checklist": 1, "pastoral": 2})
        self.assertEqual(st.outcome["outcome"], "package_complete")
        st, rs, au, att = self.attempts(FakeClient, CANNED, "detention", "1")
        self.assertEqual(att["rights"], 2)
        self.assertEqual(sum(1 for e in au.events if e["kind"] == "fault_injected"), 1)

    def test_a_value_that_names_no_stage_changes_nothing(self):
        with self.assertLogs("nury", level="WARNING"):
            st, rs, au, att = self.attempts(FakeClient, CANNED, "detention", "nope:2")
        self.assertEqual(set(att.values()), {1})

    def test_unset_does_nothing(self):
        os.environ.pop("NURY_FORCE_REJECTION", None)
        st, rs, au = run_scripted("x", client=FakeClient(CANNED), playbook="detention")
        self.assertEqual({r.metrics["attempts"] for r in rs}, {1})


class SlowFake(FakeClient):
    def ask(self, *a, **k):
        time.sleep(0.25)
        return super().ask(*a, **k)


class Strip(unittest.TestCase):
    def test_the_screen_strip_counts_the_tries_two_of_three_then_three_of_three(self):
        old = server.make_client
        server.make_client = lambda protected=None, intake=None: SlowFake(CANNED)
        try:
            with Env("rights:2"):
                s = server.Session("detention", "Maria Lopez was detained in Aurora.", "es", False, [])
                seen, logs = [], []
                for _ in range(600):
                    v = s.view()
                    if v["strip"] and v["strip"] not in seen:
                        seen.append(v["strip"])
                    if s.waiting is not None:
                        s.decide("approve", stage=s.waiting.stage_id)
                    if s.done:
                        break
                    time.sleep(0.02)
        finally:
            server.make_client = old
            s.abandon()
        self.assertIn("Draft rejected by guardrail. Regenerating (2 of 3).", seen)
        self.assertIn("Draft rejected by guardrail. Regenerating (3 of 3).", seen)
        self.assertTrue(s.done)
        self.assertEqual(s.state.results["rights"].metrics["attempts"], 3)


if __name__ == "__main__":
    unittest.main()
