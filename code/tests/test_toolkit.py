"""The read-only tools (nury.toolkit, nury.cli, nury.mcp_server): same verdicts as the engine, no key read, no file written,
no network, inputs capped, and an MCP handshake that works."""
import builtins
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonet  # noqa: E402,F401
from nury import cli, mcp_server, toolkit  # noqa: E402
from nury.engine import UNSAFE_SUFFIX, run_scripted  # noqa: E402
from test_core import CANNED, FakeClient  # noqa: E402

GOOD = "- Tiene derecho a guardar silencio. (ACLU Know Your Rights)\nPor favor hable con un abogado de inmigración."
BAD = "- Tiene derecho a guardar silencio. (ACLU Know Your Rights)\nUsted se declarará culpable. Su caso será ganado.\nPor favor hable con un abogado."


def cats(res):
    return sorted({v["category"] for v in res["violations"]})


class Verdicts(unittest.TestCase):
    def test_a_good_draft_passes_and_a_bad_one_gets_the_engines_categories(self):
        self.assertTrue(toolkit.check_draft("detention", "rights", "es", GOOD)["ok"])
        # the engine rejects the first draft of the rights stage when the unsafe suffix is added; the tools must agree
        st, rs, au = run_scripted("Maria Lopez was detained in Aurora.", client=FakeClient(CANNED), fault_injection={"stage": "rights", "times": 1, "draft_suffix": UNSAFE_SUFFIX})
        rights = [r for r in rs if r.stage_id == "rights"][0]
        first = rights.attempts[0]
        self.assertTrue(first["violations"])
        mine = toolkit.check_draft("detention", "rights", "es", first["text"])
        self.assertFalse(mine["ok"])
        engine_cats = sorted({v["category"] if isinstance(v, dict) else v for v in first["violations"]})
        self.assertEqual(cats(mine), engine_cats)
        self.assertTrue(toolkit.check_draft("detention", "rights", "es", rights.attempts[-1]["text"])["ok"])

    def test_every_stage_of_both_playbooks_accepts_its_own_approved_text(self):
        st, rs, au = run_scripted("Maria Lopez was detained in Aurora.", client=FakeClient(CANNED))
        for r in rs:
            if r.stage_id in ("rights", "checklist"):
                res = toolkit.check_draft("detention", r.stage_id, "es", r.draft)
                self.assertTrue(res["ok"], (r.stage_id, res["violations"]))

    def test_the_named_checks_run_are_the_stages_own(self):
        res = toolkit.check_draft("detention", "checklist", "es", "DO TONIGHT\n1. Llame.\nDO NOT DO\n1. No firme.\nGATHER THESE DOCUMENTS\n- IDs")
        self.assertIn("required_headings", res["named_checks"])
        self.assertTrue(res["not_checked"])

    def test_refusals_are_plain_and_inputs_are_capped(self):
        for args in (("nope", "rights", "es", GOOD), ("detention", "nope", "es", GOOD), ("detention", "rights", "fr", GOOD),
                     ("detention", "rights", "es", ""), ("detention", "rights", "es", "x" * (toolkit.MAX_CHARS + 1)), ("detention", "rights", "es", None)):
            with self.assertRaises(toolkit.ToolError):
                toolkit.check_draft(*args)

    def test_rules_and_scorecards(self):
        names = {r["name"] for r in toolkit.describe_rules()}
        self.assertTrue({"banned_phrases", "cited_bullets", "jev_assumes_facts"} <= names)
        self.assertEqual(toolkit.explain("cited_bullets")["kind"], "check")
        with self.assertRaises(toolkit.ToolError):
            toolkit.explain("nope")
        for which in ("detention", "hospital", "attacker"):
            s = toolkit.scorecard_summary(which)
            self.assertGreater(s["scenarios"], 0)
            self.assertIn("note", s)
        with self.assertRaises(toolkit.ToolError):
            toolkit.scorecard_summary("../../etc")


class Safe(unittest.TestCase):
    def run_all(self):
        out = io.StringIO()
        toolkit.list_playbooks(), toolkit.describe_rules(), toolkit.explain("banned_phrases"), toolkit.scorecard_summary("hospital")
        toolkit.check_draft("detention", "rights", "es", GOOD)
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(GOOD)
        self.addCleanup(os.unlink, f.name)
        cli.main(["check", "--playbook", "detention", "--stage", "rights", "--lang", "es", "--file", f.name], out)
        cli.main(["rules"], out)
        mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "check_draft", "arguments": {"playbook": "detention", "stage": "rights", "lang": "es", "text": GOOD}}})

    def test_no_key_is_read(self):
        seen = []

        class Rec(dict):
            def get(self, k, d=None):
                seen.append(k)
                return super().get(k, d)

            def __getitem__(self, k):
                seen.append(k)
                return super().__getitem__(k)
        env = Rec(os.environ)
        keys = ("GLOO_API_KEY", "JEV_API_KEY", "YVP_APP_KEY", "ELEVENLABS_API_KEY")
        env.update({k: "sentinel-" + k.lower() for k in keys})
        with mock.patch.object(os, "environ", env):
            self.run_all()
        for k in keys:
            self.assertNotIn(k, seen)

    def test_no_file_is_written_and_nothing_leaves_the_machine(self):
        real_open = builtins.open

        def guarded(file, mode="r", *a, **k):
            if any(c in mode for c in "wax+") and not str(file).startswith(("/dev/null",)):
                raise AssertionError(f"tried to write {file}")
            return real_open(file, mode, *a, **k)
        with mock.patch.object(builtins, "open", guarded):
            self.run_all()                      # nonet already raises on any connection to another machine

    def test_no_module_of_the_tools_imports_a_client(self):
        for m in (toolkit, cli, mcp_server):
            src = Path(m.__file__).read_text(encoding="utf-8")
            for bad in ("gloo_client", "GlooClient", "requests", "urllib.request", "subprocess", "socket"):
                self.assertNotIn(bad, src.replace("no network", ""), (m.__name__, bad))


class Cli(unittest.TestCase):
    def run_cli(self, argv, stdin=None):
        out = io.StringIO()
        with mock.patch.object(sys, "stdin", io.StringIO(stdin or "")):
            code = cli.main(argv, out)
        return code, out.getvalue()

    def test_exit_codes_and_stdin(self):
        c, o = self.run_cli(["check", "--playbook", "detention", "--stage", "rights", "--lang", "es", "--file", "-"], GOOD)
        self.assertEqual((c, json.loads(o)["ok"]), (0, True))
        c, o = self.run_cli(["check", "--playbook", "detention", "--stage", "rights", "--lang", "es", "--file", "-"], BAD)
        self.assertEqual((c, json.loads(o)["ok"]), (1, False))
        c, o = self.run_cli(["check", "--playbook", "nope", "--stage", "rights", "--lang", "es", "--file", "-"], GOOD)
        self.assertEqual(c, 2)
        self.assertIn("error", json.loads(o))
        c, o = self.run_cli(["check", "--playbook", "detention", "--stage", "rights", "--lang", "es", "--file", "/no/such/file"])
        self.assertEqual(c, 2)
        self.assertEqual(self.run_cli(["nope"])[0], 2)

    def test_lists(self):
        c, o = self.run_cli(["playbooks"])
        self.assertEqual({p["id"] for p in json.loads(o)} >= {"detention", "hospital"}, True)
        c, o = self.run_cli(["rules"])
        self.assertIn("cited_bullets", o)
        c, o = self.run_cli(["score", "--set", "attacker"])
        self.assertEqual(json.loads(o)["set"], "attacker")


class Mcp(unittest.TestCase):
    def talk(self, *lines):
        out = io.StringIO()
        mcp_server.main(io.StringIO("".join(l if l.endswith("\n") else l + "\n" for l in lines)), out)
        return [json.loads(x) for x in out.getvalue().splitlines()]

    def test_handshake_tools_and_a_check(self):
        msgs = self.talk(
            json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}}}),
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
            json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
            json.dumps({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "check_draft", "arguments": {"playbook": "detention", "stage": "rights", "lang": "es", "text": BAD}}}),
            json.dumps({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "check_draft", "arguments": {"playbook": "detention", "stage": "rights", "lang": "es"}}}),
            json.dumps({"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "nope", "arguments": {}}}),
            json.dumps({"jsonrpc": "2.0", "id": 6, "method": "nope"}),
            json.dumps({"jsonrpc": "2.0", "id": 7, "method": "ping"}))
        by = {m["id"]: m for m in msgs}
        self.assertEqual(len(msgs), 7)                                 # the notification got no reply
        self.assertEqual(by[1]["result"]["protocolVersion"], "2024-11-05")
        self.assertIn("tools", by[1]["result"]["capabilities"])
        self.assertEqual({t["name"] for t in by[2]["result"]["tools"]}, {"list_playbooks", "describe_rules", "check_draft", "get_scorecard_summary"})
        r3 = by[3]["result"]
        self.assertFalse(r3["isError"])
        self.assertFalse(json.loads(r3["content"][0]["text"])["ok"])
        self.assertTrue(by[4]["result"]["isError"])                    # no text: a plain refusal, not a crash
        self.assertTrue(by[5]["result"]["isError"])
        self.assertEqual(by[6]["error"]["code"], -32601)
        self.assertEqual(by[7]["result"], {})

    def test_bad_input_gets_an_error_not_a_crash(self):
        msgs = self.talk("{not json", json.dumps([1, 2]), json.dumps({"jsonrpc": "2.0", "id": 9, "method": "tools/list"}))
        self.assertEqual(msgs[0]["error"]["code"], -32700)
        self.assertEqual(msgs[1]["error"]["code"], -32600)
        self.assertEqual(msgs[2]["id"], 9)
        big = self.talk("x" * (mcp_server.MAX_LINE + 10), json.dumps({"jsonrpc": "2.0", "id": 10, "method": "ping"}))
        self.assertEqual(big[0]["error"]["code"], -32600)
        self.assertEqual(big[1]["id"], 10)                             # the next message still works

    def test_the_server_runs_as_a_process(self):
        import subprocess
        p = subprocess.run([sys.executable, "-m", "nury.mcp_server"], input=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}) + "\n",
                           capture_output=True, text=True, cwd=str(Path(__file__).resolve().parent.parent), env={**os.environ, "GLOO_API_KEY": "", "JEV_API_KEY": ""}, timeout=30)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(len(json.loads(p.stdout)["result"]["tools"]), 4)


if __name__ == "__main__":
    unittest.main()
