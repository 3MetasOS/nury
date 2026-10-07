"""Replay mode: the app with no key. Recorded model words, live checks. No network, no key."""
import http.client
import json
import os
import sys
import threading
import time
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonet  # noqa: E402,F401
from app import server  # noqa: E402
from nury import gloo_client, replay  # noqa: E402
from nury.engine import UNSAFE_SUFFIX  # noqa: E402
from nury.privacy import make_client  # noqa: E402

JSON = {"Content-Type": "application/json"}


class ReplayOn(unittest.TestCase):
    def setUp(self):
        os.environ["NURY_REPLAY"] = "1"
        self.addCleanup(os.environ.__setitem__, "NURY_REPLAY", "0")
        self.sessions = []

    def tearDown(self):
        for s in self.sessions:
            s.abandon()
            s.thread.join(timeout=10)

    def start(self, pid, demo=False, protected=None):
        s = server.Session(pid, replay.sample_intake(pid), replay.packs()[pid]["language"], demo, protected)
        self.sessions.append(s)
        return s

    def drive(self, s, edits=None):
        """Approve every gate (or edit where asked) until the run ends. Returns the stages seen at the gate."""
        edits, seen = edits or {}, []
        for _ in range(400):
            if s.done:
                break
            w = s.waiting
            if w is not None:
                seen.append(w.stage_id)
                if w.stage_id in edits:
                    s.decide("edit", edits[w.stage_id], stage=w.stage_id)
                else:
                    s.decide("approve", stage=w.stage_id)
                time.sleep(0.02)
            else:
                time.sleep(0.02)
        self.assertTrue(s.done)
        return seen

    def test_a_full_run_of_each_playbook_completes_with_recorded_words_and_live_checks(self):
        for pid in ("detention", "hospital"):
            s = self.start(pid)
            seen = self.drive(s)
            v = s.view()
            self.assertEqual(seen, [st.id for st in s.pb.stages], pid)
            self.assertTrue(v["done"] and not v["halted"] and not v["error"], (pid, v["halted"], v["error"]))
            self.assertTrue(v["replay"])
            self.assertEqual(v["replay_banner"], replay.BANNER)
            self.assertEqual(sorted(v["package"]), sorted(st.id for st in s.pb.stages))
            kinds = [e["kind"] for e in v["log"]]
            self.assertIn("check", kinds)                               # the checks ran live
            self.assertEqual(kinds.count("jev_recorded"), len(s.pb.stages))
            self.assertTrue(all(e["label"] == "recorded" for e in v["log"] if e["kind"] == "jev_recorded"))
            self.assertFalse(any(e["kind"] == "jev_gate" for e in v["log"]))     # no live Jev call without a key

    def test_a_rejected_and_regenerated_draft_is_in_the_audit(self):
        for pid in ("detention", "hospital"):
            s = self.start(pid, demo=True)
            self.drive(s)
            stage2 = s.pb.stages[1].id
            ev = [e for e in s.audit.events if e.get("stage") == stage2]
            kinds = [e["kind"] for e in ev]
            self.assertIn("fault_injected", kinds)
            self.assertIn("draft_rejected", kinds)
            checks = [e for e in ev if e["kind"] == "check"]
            self.assertEqual([c["passed"] for c in checks], [False, True], pid)      # rejected by the live checks, then the recorded regeneration passes
            self.assertTrue([e for e in ev if e["kind"] == "draft_rejected"][0]["visible_to_pastor"] is False)
            log = s.view()["log"]
            self.assertTrue(all("draft" not in e for e in log))                      # the rejected text never reaches the browser
            self.assertNotIn(UNSAFE_SUFFIX.strip()[:30], json.dumps(log))

    def test_an_edit_is_carried_forward_and_the_later_stages_stay_recorded(self):
        s = self.start("detention")
        seen_inputs = []
        real = replay.ReplayClient.ask

        def spy(self_, user_input, instructions=None, **kw):
            seen_inputs.append((replay.task_line(instructions), user_input))
            return real(self_, user_input, instructions, **kw)
        edit = "- EDITADO por el pastor (ACLU Know Your Rights)\nPor favor hablen con un abogado de inmigración."
        with mock.patch.object(replay.ReplayClient, "ask", spy):
            self.drive(s, edits={"rights": edit})
        v = s.view()
        self.assertIn("EDITADO por el pastor", s.state.approved["rights"])
        self.assertEqual(v["replay_note"], replay.EDIT_NOTE)
        self.assertTrue(any("EDITADO por el pastor" in u for _, u in seen_inputs if u), "later stages are given the edited text as context")
        later = s.state.results["attorney"].attempts[-1]["text"]
        self.assertEqual(later, replay.packs()["detention"]["stages"]["attorney"]["attempts"][0]["text"])      # but they say what was recorded
        self.assertTrue(v["done"])

    def test_the_recorded_attempts_run_out_gracefully(self):
        c = replay.ReplayClient()
        c.use_playbook("detention", "es")
        task = replay.packs()["detention"]["stages"]["triage"]["task"]
        a, _ = c.ask("x", instructions="boundary\n" + task + "\nmore")
        b, _ = c.ask("x", instructions="boundary\n" + task + "\nmore")
        self.assertEqual(a, b)                                            # past the last recording: the last words again, not a crash
        with self.assertRaises(RuntimeError):
            c.ask("x", instructions="Task: something nobody recorded")
        with self.assertRaises(RuntimeError):
            replay.ReplayClient().use_playbook("detention", "en")         # a language that was not recorded


class Selection(unittest.TestCase):
    def test_on_off_and_the_default(self):
        self.assertTrue(replay.active({"NURY_REPLAY": "1"}))
        self.assertTrue(replay.active({"NURY_REPLAY": "1", "GLOO_API_KEY": "present"}))      # asked for on purpose
        self.assertFalse(replay.active({"NURY_REPLAY": "0"}))
        self.assertTrue(replay.active({}))                                # no key: on
        self.assertTrue(replay.active({"GLOO_API_KEY": "  "}))
        self.assertFalse(replay.active({"GLOO_API_KEY": "present"}))      # a key is present: off, the scored behavior

    def test_with_a_key_and_no_switch_the_real_client_is_built(self):
        env = {"GLOO_API_KEY": "present-key", "NURY_REPLAY": ""}
        with mock.patch.dict(os.environ, env), mock.patch.object(gloo_client, "load_env", lambda: None):
            c = make_client(enabled=False)
        self.assertIsInstance(c, gloo_client.GlooClient)
        self.assertNotIsInstance(c, replay.ReplayClient)

    def test_with_no_key_and_no_switch_the_recorded_client_is_built(self):
        with mock.patch.dict(os.environ, {"GLOO_API_KEY": "", "NURY_REPLAY": ""}), mock.patch.object(gloo_client, "load_env", lambda: None):
            c = make_client(enabled=False)
        self.assertIsInstance(c, replay.ReplayClient)


class Http(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.H)
        cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def setUp(self):
        os.environ["NURY_REPLAY"] = "1"
        self.addCleanup(os.environ.__setitem__, "NURY_REPLAY", "0")

    def post(self, body):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        c.request("POST", "/api/run", json.dumps(body), JSON)
        r = c.getresponse()
        out = json.loads(r.read())
        c.close()
        return r.status, out

    def test_a_typed_intake_is_refused_and_the_sample_is_accepted(self):
        st, j = self.post({"intake": "My own words about a family I know.", "playbook": "detention", "language": "es"})
        self.assertEqual(st, 400)
        self.assertEqual(j["error"], replay.REFUSAL)
        self.assertTrue(j["replay"])
        st, j = self.post({"intake": replay.sample_intake("detention") + " (changed)", "playbook": "detention", "language": "es"})
        self.assertEqual(st, 400)
        st, j = self.post({"intake": replay.sample_intake("detention"), "playbook": "detention", "language": "en"})
        self.assertEqual(st, 400)                                          # only the recorded language
        st, j = self.post({"intake": replay.sample_intake("detention"), "playbook": "detention", "language": "es"})
        self.assertEqual(st, 200)
        s = server.SESSIONS.pop(j["id"])
        s.abandon()
        s.thread.join(timeout=10)

    def test_the_sample_text_is_the_playbooks_own_demo_intake(self):
        for p in server.playbooks():
            if p["status"] == "live":
                self.assertEqual(" ".join(p["demo_intake"].split()), " ".join(replay.sample_intake(p["id"]).split()), p["id"])

    def test_features_say_replay_so_the_page_can_show_its_banner(self):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        c.request("GET", "/api/features")
        j = json.loads(c.getresponse().read())
        self.assertTrue(j["replay"])
        self.assertEqual(j["replay_banner"], replay.BANNER)
        os.environ["NURY_REPLAY"] = "0"
        c.request("GET", "/api/features")
        j = json.loads(c.getresponse().read())
        self.assertFalse(j["replay"])
        c.close()


class Packs(unittest.TestCase):
    def test_every_pack_is_whole_and_holds_no_secret_or_real_person(self):
        packs = replay.packs()
        self.assertEqual(set(packs), {"detention", "hospital"})
        for pid, p in packs.items():
            self.assertTrue(p["intake"] and p["language"] and p["model"])
            from nury.engine import get_playbook
            self.assertEqual(list(p["stages"]), [s.id for s in get_playbook(pid).stages])
            for sid, st in p["stages"].items():
                self.assertTrue(st["task"].startswith("Task:"))
                self.assertGreaterEqual(len(st["attempts"]), 1)
            blob = json.dumps(p)
            for bad in ("GLOO_API_KEY", "JEV_API_KEY", "Bearer ", "@gmail", "@hotmail"):
                self.assertNotIn(bad, blob)


if __name__ == "__main__":
    unittest.main()
