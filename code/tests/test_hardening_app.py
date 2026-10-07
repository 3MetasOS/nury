"""Hardening tests, app part (CODE_REVIEW.md): the HTTP layer, input limits, the approval gate's stage check, file rights,
the export and the session call budget. No network: a fake client stands in for Gloo, and the
server runs on 127.0.0.1 with a random port inside the test."""
import http.client
import json
import os
import random
import re
import shutil
import socket
import sys
import tempfile
import threading
import time
import unittest
import zipfile
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonet  # noqa: E402,F401
from app import network_api, server  # noqa: E402
from nury import casefile as cf  # noqa: E402
from nury import gloo_client, guardrails, privacy  # noqa: E402
from nury.engine import run_scripted  # noqa: E402
from nury.privacy import PrivacyClient  # noqa: E402
from test_core import CANNED, FakeClient  # noqa: E402

JSON = {"Content-Type": "application/json"}


class Live(unittest.TestCase):
    """A real server on a random local port. Subclasses use self.call(...)."""

    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.H)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def call(self, method, path, body=None, headers=None, host=None, raw=None):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        h = dict(headers or {})
        if host is not None:
            c.putrequest(method, path, skip_host=True)
            c.putheader("Host", host)
            for k, v in h.items():
                c.putheader(k, v)
            data = raw if raw is not None else (json.dumps(body).encode() if body is not None else b"")
            c.putheader("Content-Length", str(len(data)))
            c.endheaders(data)
        else:
            data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
            c.request(method, path, body=data, headers=h)
        r = c.getresponse()
        text = r.read()
        c.close()
        try:
            return r.status, json.loads(text), r
        except ValueError:
            return r.status, text, r


class Guard(Live):
    def test_a_cross_site_text_plain_post_is_refused(self):
        st, j, _ = self.call("POST", "/api/network", {"name": "Evil", "kind": "other", "phone": "3035550199"},
                             {"Content-Type": "text/plain", "Origin": "http://evil.example"})
        self.assertEqual(st, 403)                                     # the origin is checked first
        st, j, _ = self.call("POST", "/api/network", {"name": "Evil"}, {"Content-Type": "text/plain"})
        self.assertEqual(st, 415)                                     # and without an Origin the body type still has to be JSON

    def test_another_origin_or_host_is_refused_on_reads_too(self):
        self.assertEqual(self.call("GET", "/api/privacy", headers={"Origin": "http://evil.example"})[0], 403)
        self.assertEqual(self.call("GET", "/api/cases", host="attacker.example:8080")[0], 403)      # DNS rebinding
        self.assertEqual(self.call("GET", "/api/cases", host=f"127.0.0.1:{self.port}")[0], 200)
        self.assertEqual(self.call("GET", "/api/privacy", headers={"Origin": f"http://localhost:{self.port}"}, host=f"localhost:{self.port}")[0], 200)
        self.assertEqual(self.call("GET", "/api/privacy", headers={"Origin": "null"})[0], 403)

    def test_a_put_and_a_delete_need_the_same_checks(self):
        self.assertEqual(self.call("DELETE", "/api/network/n-1", headers={"Origin": "http://evil.example", **JSON})[0], 403)
        self.assertEqual(self.call("PUT", "/api/network/n-1", {"name": "x"}, {"Content-Type": "text/plain"})[0], 415)

    def test_every_response_carries_the_security_headers(self):
        for path in ("/api/privacy", "/", "/final.css", "/nope"):
            st, _, r = self.call("GET", path)
            for k in ("X-Content-Type-Options", "X-Frame-Options", "Referrer-Policy", "Content-Security-Policy"):
                self.assertTrue(r.getheader(k), (path, k))
            self.assertEqual(r.getheader("X-Frame-Options"), "DENY")
            self.assertIn("frame-ancestors 'none'", r.getheader("Content-Security-Policy"))

    def test_the_app_pages_only_use_things_the_policy_allows(self):
        """The policy allows own scripts, styles, fonts and data: or blob: images. No page may pull anything from another site."""
        for f in (server.STATIC / "index.html", server.STATIC / "network.html", server.STATIC / "observability.html"):
            t = f.read_text(encoding="utf-8")
            self.assertFalse(re.search(r"""(?:src|href)=["']https?://""", t.replace('rel="noopener"', "")) and "<script src=\"http" in t, f.name)
            self.assertNotRegex(t, r"""<script[^>]+src=["']https?://""")
            self.assertNotRegex(t, r"""<link[^>]+href=["']https?://""")


class Limits(Live):
    def test_body_and_length_limits(self):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        c.putrequest("POST", "/api/propose-terms")
        c.putheader("Content-Type", "application/json")
        c.putheader("Content-Length", str(server.MAX_BODY + 1))
        c.endheaders()
        self.assertEqual(c.getresponse().status, 413)                # refused before a byte of the body is read
        c.close()
        for bad in ("-5", "abc"):
            c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
            c.putrequest("POST", "/api/propose-terms")
            c.putheader("Content-Type", "application/json")
            c.putheader("Content-Length", bad)
            c.endheaders()
            self.assertEqual(c.getresponse().status, 400, bad)
            c.close()

    def test_an_intake_is_capped_and_a_long_token_is_fast(self):
        st, j, _ = self.call("POST", "/api/propose-terms", {"intake": "a" * (server.MAX_INTAKE + 1)}, JSON)
        self.assertEqual(st, 400)
        t0 = time.time()
        st, j, _ = self.call("POST", "/api/propose-terms", {"intake": "x" * server.MAX_INTAKE}, JSON)
        self.assertEqual(st, 200)
        self.assertLess(time.time() - t0, 3.0)                        # the strict bound is in test_hardening_core.py

    def test_a_stalled_client_gets_a_408_instead_of_holding_a_thread(self):
        old = server.H.timeout
        server.H.timeout = 1
        try:
            s = socket.create_connection(("127.0.0.1", self.port), timeout=6)
            s.sendall(b"POST /api/propose-terms HTTP/1.1\r\nHost: 127.0.0.1:%d\r\nContent-Type: application/json\r\nContent-Length: 50\r\n\r\n{\"in" % self.port)
            data = s.recv(4096)
            s.close()
            self.assertIn(b" 408 ", data.split(b"\r\n")[0] + b" ")
        finally:
            server.H.timeout = old

    def test_language_and_protected_names_are_checked(self):
        st, j, _ = self.call("POST", "/api/run", {"intake": "x", "playbook": "detention", "language": "fr"}, JSON)
        self.assertEqual(st, 400)
        st, j, _ = self.call("POST", "/api/run", {"intake": "x", "playbook": "detention", "language": "es",
                                                  "protected": [{"term": "n%d" % i} for i in range(server.MAX_PROTECTED + 1)]}, JSON)
        self.assertEqual(st, 400)

    def test_a_json_list_to_the_network_api_is_a_400_not_a_dropped_connection(self):
        with tempfile.TemporaryDirectory() as d:
            os.environ["NURY_NETWORK_DIR"] = d
            try:
                for path in ("/api/network/home", "/api/network", "/api/network/import"):
                    st, j, _ = self.call("POST", path, [1], JSON)
                    self.assertEqual(st, 400, path)
                st, body = network_api.handle("POST", "/api/network", b"[1]")[:2]
                self.assertEqual(st, 400)
                Path(d, "network.json").write_text("{not json", encoding="utf-8")        # a damaged file is a plain answer too
                self.assertEqual(self.call("GET", "/api/network")[0], 500)
            finally:
                del os.environ["NURY_NETWORK_DIR"]


class Sessions(Live):
    def setUp(self):
        self._mc = server.make_client
        server.make_client = lambda protected=None, intake=None: FakeClient(CANNED)
        self._ids = []

    def tearDown(self):
        server.make_client = self._mc
        for sid in self._ids:
            s = server.SESSIONS.pop(sid, None)
            if s:
                s.abandon()
                s.thread.join(timeout=5)

    def start(self):
        s = server.Session("detention", "Maria Lopez was detained in Aurora.", "es", False, [])
        server.SESSIONS[s.id] = s
        self._ids.append(s.id)
        for _ in range(200):
            if s.waiting is not None:
                return s
            time.sleep(0.05)
        self.fail("no draft reached the gate")

    def test_a_decision_must_name_the_stage_the_pastor_saw(self):
        s = self.start()
        url = f"/api/session/{s.id}/decision"
        self.assertEqual(self.call("POST", url, {"action": "approve"}, JSON)[0], 400)                          # no stage
        st, j, _ = self.call("POST", url, {"action": "approve", "stage": "rights"}, JSON)                     # the NEXT draft, not the one waiting
        self.assertEqual((st, j["ok"]), (409, False))
        self.assertEqual(s.waiting.stage_id, "triage")                                                       # nothing was approved
        st, j, _ = self.call("POST", url, {"action": "approve", "stage": "triage"}, JSON)
        self.assertEqual((st, j["ok"]), (200, True))
        for _ in range(100):                                                                                 # the second click of a double click
            if s.waiting is None or s.waiting.stage_id != "triage":
                break
            time.sleep(0.05)
        st, j, _ = self.call("POST", url, {"action": "approve", "stage": "triage"}, JSON)
        self.assertEqual((st, j["ok"]), (409, False))
        self.assertNotIn("rights", {k for k, v in s.state.approved.items()})

    def test_session_start_errors_are_a_500_in_plain_words(self):
        def boom(protected=None, intake=None):
            raise RuntimeError("Set GLOO_API_KEY in the environment.")
        server.make_client = boom
        st, j, _ = self.call("POST", "/api/run", {"intake": "x", "playbook": "detention", "language": "es"}, JSON)
        self.assertEqual(st, 500)
        self.assertNotIn("GLOO", json.dumps(j))

    def test_only_a_few_runs_may_write_at_once(self):
        old = server.MAX_BUSY
        server.MAX_BUSY = 1
        fake = SimpleNamespace(done=False, waiting=None, created=time.time())
        server.SESSIONS["busy-test"] = fake
        try:
            st, j, _ = self.call("POST", "/api/run", {"intake": "x", "playbook": "detention", "language": "es"}, JSON)
            self.assertEqual(st, 429)
            fake.waiting = object()                                    # waiting at a gate costs nothing
            self.assertEqual(server.busy_count(), 0)
        finally:
            server.MAX_BUSY = old
            server.SESSIONS.pop("busy-test", None)

    def test_old_sessions_are_dropped_and_a_run_left_at_a_gate_is_stopped(self):
        s = self.start()
        server.purge_sessions(now=time.time() + server.SESSION_TTL_S + 5)
        self.assertNotIn(s.id, server.SESSIONS)
        s.thread.join(timeout=10)
        self.assertFalse(s.thread.is_alive())                          # the worker ended, it does not wait forever


class Files(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def saved(self):
        st, rs, au = run_scripted("Maria Lopez was detained in Aurora.", client=FakeClient(CANNED))
        pc = PrivacyClient(FakeClient(CANNED), protected=[{"term": "Maria Lopez"}])
        return cf.save_case(st, au, playbook="detention", root=self.tmp, privacy=pc)

    def test_case_files_are_owner_only(self):
        r = self.saved()
        d = Path(r["path"])
        self.assertEqual(oct(d.stat().st_mode & 0o777), "0o700")
        for f in d.iterdir():
            self.assertEqual(oct(f.stat().st_mode & 0o777), "0o600", f.name)
        self.assertTrue((d / "privacy-map.json").is_file())
        cf.set_follow_up(r["id"], True, self.tmp)
        self.assertEqual(oct((d / "case.json").stat().st_mode & 0o777), "0o600")

    def test_the_export_leaves_out_the_privacy_map_unless_asked_and_is_owner_only(self):
        r = self.saved()
        z = cf.export_zip(r["id"], self.tmp)
        names = {n.split("/")[1] for n in zipfile.ZipFile(z).namelist()}
        self.assertNotIn("privacy-map.json", names)
        self.assertIn("intake.md", names)
        self.assertEqual(oct(Path(z).stat().st_mode & 0o777), "0o600")
        z2 = cf.export_zip(r["id"], self.tmp, include_privacy_map=True)
        self.assertIn("privacy-map.json", {n.split("/")[1] for n in zipfile.ZipFile(z2).namelist()})

    def test_the_server_deletes_the_zip_after_sending_it(self):
        r = self.saved()
        old = server.CASES_ROOT
        server.CASES_ROOT = self.tmp
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.H)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        try:
            c = http.client.HTTPConnection("127.0.0.1", httpd.server_address[1], timeout=10)
            c.request("GET", f"/api/case/{r['id']}/export")
            resp = c.getresponse()
            body = resp.read()
            self.assertEqual(resp.status, 200)
            self.assertTrue(body.startswith(b"PK"))
            c.close()
            self.assertEqual([p.name for p in Path(self.tmp).iterdir()], [r["id"]])        # no zip left on the server
        finally:
            httpd.shutdown()
            server.CASES_ROOT = old


@unittest.skipUnless(hasattr(gloo_client, "CallBudgetExceeded"), "needs the core part of the hardening patch")
class SessionBudget(unittest.TestCase):
    def test_the_session_sets_the_budget_on_the_real_client(self):
        c = gloo_client.GlooClient(api_key="k")
        pc = PrivacyClient(c)
        mc = server.make_client
        server.make_client = lambda protected=None, intake=None: pc
        try:
            s = server.Session("detention", "x", "es", False, [])
            s.abandon()
            s.thread.join(timeout=10)
        finally:
            server.make_client = mc
        self.assertEqual(c.max_calls, server.RUN_CALL_BUDGET)




if __name__ == "__main__":
    unittest.main()
