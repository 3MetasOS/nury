"""The bounded retry in the Gloo client. No network: requests.post is a script, and sleeping is recorded, not done."""
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonet  # noqa: E402,F401
import requests  # noqa: E402
from nury import gloo_client as gc  # noqa: E402
from nury.audit import AuditLog  # noqa: E402
from nury.engine import CaseState, run_stage  # noqa: E402


class Resp:
    def __init__(self, status, body="", headers=None):
        self.status_code, self.text, self.headers = status, body, headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"{self.status_code}", response=self)

    def json(self):
        return {"output": [{"type": "message", "content": [{"type": "output_text", "text": "hola"}]}], "usage": {"input_tokens": 5, "output_tokens": 2}}


class Script:
    """Replays a list of outcomes: a Resp to return or an exception to raise."""
    def __init__(self, *steps):
        self.steps, self.calls = list(steps), 0

    def __call__(self, *a, **k):
        self.calls += 1
        s = self.steps.pop(0)
        if isinstance(s, Exception):
            raise s
        return s


class Retry(unittest.TestCase):
    def setUp(self):
        self.slept = []
        self.p = mock.patch.object(gc, "_sleep", lambda s: self.slept.append(s))
        self.p.start()
        self.c = gc.GlooClient(api_key="test-key-not-real")

    def tearDown(self):
        self.p.stop()

    def go(self, *steps):
        sc = Script(*steps)
        with mock.patch.object(gc.requests, "post", sc):
            try:
                return self.c.ask("x"), sc, None
            except Exception as e:
                return None, sc, e

    def test_a_429_then_success_retries_once_with_a_one_second_backoff(self):
        r, sc, e = self.go(Resp(429), Resp(200))
        self.assertEqual((r[0], r[1]["http_retries"], sc.calls, self.slept), ("hola", 1, 2, [1.0]))

    def test_5xx_codes_are_retried_with_backoff_one_then_two_seconds(self):
        for code in (500, 502, 503, 504):
            self.slept.clear()
            r, sc, e = self.go(Resp(code), Resp(code), Resp(200))
            self.assertEqual((r[0], r[1]["http_retries"], sc.calls, self.slept), ("hola", 2, 3, [1.0, 2.0]), code)

    def test_after_three_tries_the_last_error_is_raised_as_before(self):
        r, sc, e = self.go(Resp(503), Resp(503), Resp(503))
        self.assertIsInstance(e, requests.exceptions.HTTPError)
        self.assertEqual((sc.calls, self.slept), (3, [1.0, 2.0]))

    def test_dropped_connections_and_timeouts_are_retried(self):
        r, sc, e = self.go(requests.exceptions.ConnectionError("reset"), requests.exceptions.Timeout("slow"), Resp(200))
        self.assertEqual((r[0], sc.calls), ("hola", 3))
        r, sc, e = self.go(*[requests.exceptions.Timeout("slow")] * 3)
        self.assertIsInstance(e, requests.exceptions.Timeout)
        self.assertEqual(sc.calls, 3)

    def test_402_and_403_and_other_4xx_are_never_retried(self):
        r, sc, e = self.go(Resp(402, "INSUFFICIENT_CREDIT"))
        self.assertIsInstance(e, requests.exceptions.HTTPError)
        self.assertEqual((sc.calls, self.slept), (1, []))
        r, sc, e = self.go(Resp(403, "blocked by guardrail"))
        self.assertIsInstance(e, gc.GuardrailBlock)
        self.assertEqual(sc.calls, 1)
        for code in (400, 401, 404, 422):
            r, sc, e = self.go(Resp(code))
            self.assertEqual(sc.calls, 1, code)

    def test_a_429_about_quota_or_billing_is_not_retried(self):
        for body in ('{"error":"insufficient_quota"}', "Quota exceeded for this key", "billing hard limit reached"):
            r, sc, e = self.go(Resp(429, body))
            self.assertEqual(sc.calls, 1, body)
            self.assertIsInstance(e, requests.exceptions.HTTPError)

    def test_retry_after_is_honored_up_to_ten_seconds(self):
        self.go(Resp(429, headers={"Retry-After": "3"}), Resp(200))
        self.assertEqual(self.slept, [3.0])
        self.slept.clear()
        self.go(Resp(429, headers={"Retry-After": "120"}), Resp(200))
        self.assertEqual(self.slept, [10.0])
        self.slept.clear()
        self.go(Resp(429, headers={"Retry-After": "soon"}), Resp(200))
        self.assertEqual(self.slept, [1.0])

    def test_a_clean_call_has_no_retries_and_the_meta_says_zero(self):
        r, sc, e = self.go(Resp(200))
        self.assertEqual((r[1]["http_retries"], sc.calls, self.slept), (0, 1, []))

    def test_the_status_rule_itself(self):
        self.assertTrue(all(gc.retryable_status(c) for c in (429, 500, 502, 503, 504)))
        self.assertFalse(any(gc.retryable_status(c) for c in (200, 400, 401, 402, 403, 404, 501)))
        self.assertFalse(gc.retryable_status(429, "insufficient_quota"))

    def test_the_engine_error_path_is_unchanged_when_the_tries_run_out(self):
        st = CaseState("intake", "es")
        au = AuditLog()
        with mock.patch.object(gc.requests, "post", Script(Resp(503), Resp(503), Resp(503))):
            rec = run_stage("triage", st, client=self.c, audit=au)
        self.assertEqual(rec.status, "error")
        self.assertIn("Gloo call failed", rec.message)
        self.assertEqual([e["kind"] for e in au.events if e["kind"] == "error"], ["error"])

    def test_a_retried_call_succeeds_inside_a_stage_and_is_not_counted_as_a_draft_attempt(self):
        st = CaseState("Pastor, Carlos fue detenido hoy.", "es")
        good = Resp(200)
        good.json = lambda: {"output": [{"type": "message", "content": [{"type": "output_text", "text":
            "SITUATION: Carlos was detained.\nPEOPLE: Carlos\nLOCATION: not stated\nFAMILY LANGUAGE: es\nURGENCY: high: detained today\nMISSING FACTS:\n1. Where?\n2. Who called?\n3. Children?"}]}],
            "usage": {"input_tokens": 5, "output_tokens": 2}}
        with mock.patch.object(gc.requests, "post", Script(Resp(502), good)):
            rec = run_stage("triage", st, client=self.c, audit=AuditLog())
        self.assertEqual((rec.status, rec.metrics["attempts"]), ("approved", 1))


if __name__ == "__main__":
    unittest.main()
