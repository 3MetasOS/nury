"""Hardening tests, core part (CODE_REVIEW.md): the exact linear email scanner, the per-run call budget and the optional
output-token cap in the Gloo client. No network: requests.post is replaced."""
import os
import random
import re
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonet  # noqa: E402,F401
from nury import gloo_client, guardrails, privacy  # noqa: E402
from test_core import CANNED  # noqa: E402


class _Resp:
    status_code = 200
    text = "{}"
    headers = {}

    def raise_for_status(self):
        pass

    def json(self):
        return {"output": [], "usage": {"input_tokens": 1, "output_tokens": 1}}


class Budget(unittest.TestCase):
    def setUp(self):
        self.sent = []
        self._post = gloo_client.requests.post
        gloo_client.requests.post = lambda url, json=None, **kw: (self.sent.append(json), _Resp())[1]
        self.addCleanup(setattr, gloo_client.requests, "post", self._post)

    def test_a_run_cannot_make_more_calls_than_its_budget(self):
        c = gloo_client.GlooClient(api_key="k")
        c.max_calls = 2
        c.respond("a")
        c.respond("b")
        with self.assertRaises(gloo_client.CallBudgetExceeded):
            c.respond("c")
        self.assertEqual(c.calls, 2)

    def test_max_output_tokens_is_sent_only_when_asked(self):
        c = gloo_client.GlooClient(api_key="k")
        c.respond("a")
        self.assertNotIn("max_output_tokens", self.sent[-1])
        os.environ["NURY_MAX_OUTPUT_TOKENS"] = "1500"
        try:
            c.respond("a")
        finally:
            del os.environ["NURY_MAX_OUTPUT_TOKENS"]
        self.assertEqual(self.sent[-1]["max_output_tokens"], 1500)


OLD_EMAIL = re.compile(r"[\w.+\-]+@[\w\-]+(?:\.[\w\-]+)+")
OLD_EMAIL_IN_TEXT = re.compile(r"[\w.+\-]+@([\w\-]+(?:\.[\w\-]+)+)")


class EmailRegex(unittest.TestCase):
    def corpus(self):
        out = ["", "a@b.co", "maria.lopez+iglesia@example.org llamó", "@a@b.com", "x.y@z.w.v", "..@a.b", "a@b", "a@@b.com", "me@x.com,you@y.org",
               "ñandú@correo.mx y José@Correo.com", "foo-bar_baz@sub-domain.example.co.uk.", "no email here", "a" * 200 + "@x.com", "x@" + "y" * 50]
        for pb in ("detention", "hospital"):
            root = Path(__file__).resolve().parents[1] / "playbooks" / pb
            for f in list(root.rglob("*.json")) + list(root.rglob("*.txt")):
                out.append(f.read_text(encoding="utf-8"))
        for texts in list(CANNED.values()):
            out.append(texts if isinstance(texts, str) else str(texts))
        rnd = random.Random(7)
        alpha = ["a", "B", "1", "_", "-", ".", "+", "@", " ", "\n", "é", "ñ", "x.y", "@z.co"]
        out += ["".join(rnd.choice(alpha) for _ in range(rnd.randint(0, 40))) for _ in range(20000)]
        return out

    def test_the_linear_regex_matches_exactly_what_the_old_one_matched(self):
        n = 0
        for t in self.corpus():
            self.assertEqual([m.group(0) for m in privacy._EMAIL.finditer(t)], [m.group(0) for m in OLD_EMAIL.finditer(t)], t[:60])
            self.assertEqual([(m.group(0), m.group(1)) for m in guardrails._EMAIL_IN_TEXT.finditer(t)],
                             [(m.group(0), m.group(1)) for m in OLD_EMAIL_IN_TEXT.finditer(t)], t[:60])
            n += 1
        self.assertGreater(n, 20000)

    def test_a_long_unbroken_token_is_scanned_in_linear_time(self):
        for rx in (privacy._EMAIL, guardrails._EMAIL_IN_TEXT):
            for t in ("x" * 200_000, "1" * 200_000, "a." * 100_000, "a@" * 50_000):
                t0 = time.time()
                rx.findall(t)
                self.assertLess(time.time() - t0, 1.0, (rx.pattern[:20], t[:6]))

    def test_the_whole_pseudonymizer_and_the_email_check_stay_fast_on_a_long_token(self):
        t0 = time.time()
        privacy.propose_terms("x" * 20_000)
        guardrails.email_reasons("x" * 20_000, "", "")
        self.assertLess(time.time() - t0, 2.0)




if __name__ == "__main__":
    unittest.main()
