"""Audit subscribe hook and monotonic event times. No network."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonet  # noqa: E402,F401
from nury.audit import AuditLog  # noqa: E402
from nury.engine import run_scripted  # noqa: E402
from test_core import FakeClient  # noqa: E402


class Hooks(unittest.TestCase):
    def test_a_subscriber_sees_every_event_in_order_and_can_unsubscribe(self):
        au, seen = AuditLog(), []
        off = au.subscribe(seen.append)
        au.log("a", x=1)
        au.log("b")
        off()
        au.log("c")
        self.assertEqual([e["kind"] for e in seen], ["a", "b"])
        self.assertEqual([e["kind"] for e in au.events], ["a", "b", "c"])
        off()                                             # twice is fine

    def test_a_subscriber_that_raises_never_breaks_the_log_or_the_others(self):
        au, seen = AuditLog(), []

        def boom(e):
            raise RuntimeError("bad subscriber")
        au.subscribe(boom)
        au.subscribe(seen.append)
        self.assertEqual(au.log("a")["kind"], "a")
        self.assertEqual(len(seen), 1)

    def test_every_event_has_a_monotonic_time_that_never_goes_backwards(self):
        au = AuditLog()
        for i in range(20):
            au.log("e", i=i)
        t = [e["t_ms"] for e in au.events]
        self.assertEqual(t, sorted(t))
        self.assertTrue(all(isinstance(x, float) and x >= 0 for x in t))

    def test_the_file_carries_t_ms_too_and_a_run_has_it_on_every_event(self):
        p = tempfile.mktemp(suffix=".jsonl")
        au = AuditLog(path=p)
        st, rs, au2 = run_scripted("intake", client=FakeClient(), audit=au)
        rows = [json.loads(x) for x in Path(p).read_text().splitlines()]
        self.assertTrue(rows and all("t_ms" in r and "ts" in r for r in rows))
        Path(p).unlink()

    def test_a_subscriber_can_follow_a_whole_run_as_progress_and_it_changes_nothing(self):
        phases = []
        au = AuditLog()
        au.subscribe(lambda e: phases.append(e["kind"]) if e["kind"] in ("gloo_call", "check", "gate") else None)
        st, rs, _ = run_scripted("intake", client=FakeClient(), audit=au)
        self.assertEqual(st.outcome["outcome"], "package_complete")
        self.assertEqual(phases.count("gate"), 5)
        st2, rs2, _ = run_scripted("intake", client=FakeClient(), audit=AuditLog())
        self.assertEqual([r.status for r in rs], [r.status for r in rs2])


if __name__ == "__main__":
    unittest.main()
