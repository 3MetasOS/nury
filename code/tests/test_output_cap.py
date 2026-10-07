"""The reply of every stage but the checklist is capped at 1,500 tokens (the longest measured reply of the others is 652;
the checklist reached 1,092, so it has no cap). The cap travels as max_output_tokens, which Gloo accepted and enforced on
a live call on 2026-10-07 (cap 60, 60 tokens came back)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonet  # noqa: E402,F401
from nury import playbook as pbm  # noqa: E402
from nury.engine import get_playbook, run_scripted  # noqa: E402
from test_core import CANNED, HCANNED, FakeClient, HFake  # noqa: E402


class Recording:
    def __init__(self, inner):
        self.inner, self.kw = inner, []

    def ask(self, user_input, instructions=None, **kw):
        self.kw.append(kw)
        return self.inner.ask(user_input, instructions=instructions, **kw)

    def __getattr__(self, name):
        return getattr(self.inner, name)


class OutputCap(unittest.TestCase):
    def test_the_caps_in_the_playbooks(self):
        for pid in ("detention", "hospital"):
            caps = {s.id: s.max_output_tokens for s in get_playbook(pid).stages}
            self.assertIsNone(caps["checklist"], pid)
            self.assertEqual({k: v for k, v in caps.items() if k != "checklist"}, {k: 1500 for k in caps if k != "checklist"}, pid)

    def test_the_engine_sends_the_cap_only_for_capped_stages(self):
        for pid, fake, canned in (("detention", FakeClient, CANNED), ("hospital", HFake, HCANNED)):
            rec = Recording(fake(canned))
            run_scripted("intake", client=rec, playbook=pid)
            ids = [s.id for s in get_playbook(pid).stages]
            self.assertEqual(len(rec.kw), len(ids))
            for sid, kw in zip(ids, rec.kw):
                self.assertEqual(kw, {} if sid == "checklist" else {"max_output_tokens": 1500}, (pid, sid))

    def test_a_bad_cap_is_refused_when_the_playbook_loads(self):
        for bad in (0, 50, 9000, "1500", True, 1500.5):
            with self.assertRaises(pbm.PlaybookError):
                pbm._cap({"id": "x", "max_output_tokens": bad})
        self.assertIsNone(pbm._cap({"id": "x"}))
        self.assertEqual(pbm._cap({"id": "x", "max_output_tokens": 1000}), 1000)


if __name__ == "__main__":
    unittest.main()
