"""Robustness fixes from CODE_REVIEW.md: single-pass prompt rendering (COR-02), a damaged case does not hide the others
(COR-03), a lost save race is a plain error (COR-04), the church network file is written whole and by one writer at a
time (COR-05), failures that must not stop a run are logged by class only (QA-03), tests cannot leave this machine."""
import json
import os
import re
import shutil
import socket
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonet  # noqa: E402,F401
from app import network_api, server  # noqa: E402
from nury import casefile as cf  # noqa: E402
from nury import log, network, playbook as pbm  # noqa: E402
from nury.audit import AuditLog  # noqa: E402
from nury.engine import get_playbook, run_scripted  # noqa: E402
from test_core import CANNED, FakeClient  # noqa: E402

GOOD = {"name": "Ayuda Legal", "kind": "legal_aid", "services": "x", "languages": ["es"], "city": "Denver", "state": "CO", "phone": "(303) 555-0100"}


def old_render(stage, pb, lang, fields, dynamic=None):
    """The renderer as it was before COR-02 (sequential replace, check after), for the equality test."""
    prompt = stage.prompt
    vars_ = {"lang_name": pbm.LANG_NAME[lang], **pbm.render_sources(stage, pb, lang, dynamic)}
    for k, v in vars_.items():
        prompt = prompt.replace("{{" + k + "}}", v)
    prompt += pbm.skills_lib.render(stage.skills, lang, pb.boundary)
    left = re.findall(r"\{\{(\w+)\}\}", prompt)
    if left:
        raise pbm.PlaybookError(f"unfilled {left}")
    return prompt


class Render(unittest.TestCase):
    def test_the_single_pass_renderer_gives_the_same_text_as_before_for_every_stage(self):
        n = 0
        for pid in ("detention", "hospital"):
            pb = get_playbook(pid)
            for s in pb.stages:
                for lang in pb.languages:
                    self.assertEqual(pbm.render_prompt(s, pb, lang, None, {}), old_render(s, pb, lang, {}), (pid, s.id, lang))
                    n += 1
        self.assertGreaterEqual(n, 16)

    def test_a_contact_name_with_braces_is_only_text(self):
        pb = get_playbook("detention")
        st = pb.registry["attorney"]
        entry = {"id": "n-1", "name": "Ayuda {{vetted_points}} {{nope}} Legal", "services": "", "phone": "(303) 555-0100", "url": "", "kind": "legal_aid", "city": "", "state": "CO"}
        text = pbm.render_prompt(st, pb, "es", None, {}, dynamic={"church_network": {"entries": [entry], "fictional": False}})
        self.assertIn("Ayuda {{vetted_points}} {{nope}} Legal", text)          # the name is copied exactly, not expanded, not an error

    def test_an_unknown_variable_in_the_template_is_still_refused(self):
        pb = get_playbook("detention")
        st = pb.registry["rights"]
        bad = type(st)(**{**st.__dict__, "prompt": st.prompt + "\n{{surprise}}"})
        with self.assertRaises(pbm.PlaybookError):
            pbm.render_prompt(bad, pb, "es", None, {})


class Cases(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def save(self, **kw):
        st, rs, au = run_scripted("Maria Lopez was detained in Aurora.", client=FakeClient(CANNED))
        return cf.save_case(st, au, playbook="detention", root=self.tmp, **kw)

    def test_one_damaged_case_does_not_hide_the_others(self):
        good = self.save()
        bad = self.save()
        (Path(bad["path"]) / "case.json").write_text('{"id": "x", "pla', encoding="utf-8")        # a crash while writing
        ids = [c["id"] for c in cf.list_cases(self.tmp)]
        self.assertEqual(ids, [good["id"]])
        old = server.CASES_ROOT
        server.CASES_ROOT = self.tmp
        try:
            self.assertEqual([c["id"] for c in server.cases_overview()], [good["id"]])
        finally:
            server.CASES_ROOT = old

    def test_a_lost_save_race_is_a_case_error(self):
        with mock.patch.object(Path, "mkdir", side_effect=FileExistsError):
            with self.assertRaises(cf.CaseError):
                self.save()

    def test_case_json_is_written_whole_and_leaves_no_temporary_file(self):
        r = self.save()
        cf.set_follow_up(r["id"], True, self.tmp)
        self.assertEqual(sorted(p.name for p in Path(r["path"]).iterdir() if p.name.endswith(".tmp")), [])
        self.assertTrue(json.loads((Path(r["path"]) / "case.json").read_text(encoding="utf-8"))["needs_follow_up"])


class NetworkFile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_thirty_adds_at_once_all_arrive_and_the_file_is_whole(self):
        errs = []

        def add(i):
            try:
                network.load_network(self.tmp, demo=False).add({**GOOD, "name": f"Contact {i}"})
            except Exception as e:           # noqa: BLE001
                errs.append(e)
        ts = [threading.Thread(target=add, args=(i,)) for i in range(30)]
        [t.start() for t in ts]
        [t.join() for t in ts]
        self.assertEqual(errs, [])
        j = json.loads((Path(self.tmp) / "network.json").read_text(encoding="utf-8"))
        self.assertEqual(len(j["entries"]), 30)
        self.assertEqual([p.name for p in Path(self.tmp).iterdir()], ["network.json"])          # no temporary file left

    def test_imports_use_files_of_their_own_and_leave_nothing_behind(self):
        os.environ["NURY_NETWORK_DIR"] = self.tmp
        try:
            st, _, body = network_api.handle("POST", "/api/network/import", json.dumps({"entries": [GOOD]}).encode())
            self.assertEqual(st, 200)
            self.assertEqual(json.loads(body)["added"], 1)
            self.assertEqual(sorted(p.name for p in Path(self.tmp).iterdir()), ["network.json"])
        finally:
            del os.environ["NURY_NETWORK_DIR"]


class Logging(unittest.TestCase):
    def test_a_failed_side_job_is_logged_by_class_never_by_message(self):
        with self.assertLogs("nury", level="WARNING") as cm:
            log.note("somewhere", ValueError("Maria Lopez 303-555-0100"))
        out = "\n".join(cm.output)
        self.assertIn("somewhere failed: ValueError", out)
        self.assertNotIn("Maria", out)
        self.assertNotIn("555", out)

    def test_a_subscriber_that_fails_is_logged_and_the_run_goes_on(self):
        au = AuditLog()

        def boom(e):
            raise RuntimeError("private text")
        au.subscribe(boom)
        with self.assertLogs("nury", level="WARNING") as cm:
            au.log("stage_start", stage="triage")
        self.assertIn("audit.subscriber failed: RuntimeError", "\n".join(cm.output))
        self.assertNotIn("private", "\n".join(cm.output))
        self.assertEqual(len(au.events), 1)


class NetworkGuard(unittest.TestCase):
    def test_a_test_cannot_reach_another_machine(self):
        s = socket.socket()
        self.addCleanup(s.close)
        with self.assertRaises(OSError) as cm:
            s.connect(("93.184.216.34", 80))
        self.assertIn("must not reach the network", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
