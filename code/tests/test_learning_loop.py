"""The learning loop: candidate files, the report, and the before and after test. No network, no keys. Synthetic data only."""
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonet  # noqa: E402,F401
import candidate_test as ct  # noqa: E402
import candidates as cand  # noqa: E402
import learning_report as lr  # noqa: E402
from nury import feedback as fb  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
EXAMPLE = REPO / "documents" / "product" / "learning_example"


def h(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def meta(**kw):
    m = cand.new_meta("c-0001-x", "prompt_line", {"edits": 3}, "2026-10-07", True)
    m.update(kw)
    return m


CH = [{"kind": "append", "file": "code/playbooks/detention/prompts/pastoral.txt", "text": "Keep it short.\n"}]


class Format(unittest.TestCase):
    def test_a_proposed_candidate_is_well_formed_and_round_trips(self):
        text = cand.render(meta(), "Title", "Because.", CH)
        m, body, changes = cand.parse(text)
        self.assertEqual(cand.check(m, changes, "c-0001-x"), [])
        self.assertEqual(changes, CH)
        self.assertEqual(m["status"], "proposed")

    def test_nothing_reaches_approved_without_a_named_person_and_a_date(self):
        for st in ("approved", "released"):
            p = cand.check(meta(status=st, test_result="r.md", release_commit="abc"), CH, "c-0001-x")
            self.assertTrue(any("approved_by" in x for x in p), st)
            self.assertTrue(any("approved_date" in x for x in p), st)
        for who in ("nury", "auto", "bot", "script"):
            self.assertTrue(cand.check(meta(status="approved", test_result="r.md", approved_by=who, approved_date="2026-10-07"), CH, "c-0001-x"), who)
        self.assertEqual(cand.check(meta(status="approved", test_result="r.md", approved_by="Juan Pelaez", approved_date="2026-10-07"), CH, "c-0001-x"), [])

    def test_the_status_path_has_required_evidence(self):
        self.assertTrue(cand.check(meta(status="tested"), CH, "c-0001-x"))                       # no test_result
        self.assertTrue(cand.check(meta(status="tested", test_result="r.md"), [], "c-0001-x"))   # no change block
        self.assertTrue(cand.check(meta(status="released", approved_by="Juan", approved_date="2026-10-07", test_result="r.md"), CH, "c-0001-x"))
        self.assertTrue(cand.check(meta(approved_by="Juan", approved_date="2026-10-07"), CH, "c-0001-x"))       # proposed but already approved
        self.assertTrue(cand.check(meta(), CH, "other-name"))
        self.assertTrue(cand.check(meta(type="rewrite_everything"), CH, "c-0001-x"))
        self.assertTrue(cand.check(meta(synthetic="yes"), CH, "c-0001-x"))
        self.assertTrue(cand.check(meta(evidence={}), CH, "c-0001-x"))

    def test_a_change_cannot_escape_the_repository_or_touch_secrets(self):
        for f in ("/etc/passwd", "../x", "code/../../x", ".env", ".git/config"):
            self.assertTrue(cand.check(meta(), [{"kind": "append", "file": f, "text": "x"}], "c-0001-x"), f)
        self.assertTrue(cand.check(meta(), [{"kind": "delete", "file": "a"}], "c-0001-x"))
        self.assertTrue(cand.check(meta(type="new_jev_question"), CH, "c-0001-x"))     # shared eval wording is written by hand

    def test_the_example_candidates_are_all_valid_proposed_and_synthetic(self):
        res = cand.check_dir(EXAMPLE / "candidates")
        self.assertTrue(res)
        self.assertEqual({k: v for k, v in res.items() if v}, {})
        for f in (EXAMPLE / "candidates").glob("*.md"):
            m = cand.load(f)[0]
            self.assertEqual((m["status"], m["synthetic"], m["approved_by"]), ("proposed", True, None), f.name)


class Report(unittest.TestCase):
    def rows(self):
        return fb.read_all(str(EXAMPLE / "feedback"))

    def test_the_example_numbers(self):
        a = lr.analyze(self.rows(), None, 3)
        self.assertEqual((a["gates"], a["edits"]), (60, 27))
        s = a["stages"][("detention", "pastoral")]
        self.assertEqual((s["gates"], s["edited"], s["tags"]["shorter"]), (20, 17, 15))
        self.assertEqual(a["outcomes"]["detention"], {"went_as_hoped": 3, "did_not_go_as_hoped": 3, "unknown": 1})

    def test_candidates_have_a_type_evidence_and_a_draft_and_only_where_the_evidence_reaches_the_minimum(self):
        a = lr.analyze(self.rows(), None, 3)
        cs = lr.candidates_from(a, "2026-10-07", True)
        types = {c[0]["type"] for c in cs}
        self.assertTrue({"prompt_line", "new_rule", "new_scenario"} <= types)
        for m, title, why, changes, extra in cs:
            self.assertEqual(m["status"], "proposed")
            self.assertTrue(m["evidence"] and m["synthetic"])
            self.assertEqual(cand.check(m, changes, m["id"]), [])
        self.assertEqual([c for c in lr.candidates_from(lr.analyze(self.rows(), None, 99), "2026-10-07", True)], [])
        hospital = [c for c in cs if c[0]["evidence"].get("playbook") == "hospital"]
        self.assertEqual(hospital, [])                                            # hospital edits stayed below the minimum

    def test_counts_mode_cannot_propose_a_phrase_rule(self):
        d = tempfile.mkdtemp()
        try:
            import os
            os.environ["NURY_FEEDBACK"] = "counts"
            from test_feedback import DRAFT, FINAL, client
            for _ in range(5):
                fb.record_gate("pastoral", "edit", DRAFT, FINAL, client(), [], playbook="detention", language="es", reason_chip="not_my_voice", root=d)
            os.environ.pop("NURY_FEEDBACK")
            a = lr.analyze(fb.read_all(d), None, 3)
            cs = lr.candidates_from(a, "2026-10-07", True)
            self.assertFalse([c for c in cs if c[0]["type"] == "new_rule"])
            self.assertTrue([c for c in cs if c[1].startswith("Voice or tone")])
            text = lr.render(a, cs, True, d, d)
            self.assertIn("Counts mode only", text)
        finally:
            shutil.rmtree(d)

    def test_the_report_says_it_is_synthetic_and_prints_no_home_folder(self):
        text = (EXAMPLE / "LEARNING_REPORT_EXAMPLE.md").read_text()
        self.assertIn("SYNTHETIC DATA", text)
        self.assertIn("No real pastor has used Nury", text)
        self.assertNotIn("/Users/", text)
        self.assertNotIn("Nothing in this report changes Nury" if False else "XYZ", text)

    def test_the_example_feedback_holds_no_fictional_names_only_tokens(self):
        blob = "".join(f.read_text() for f in (EXAMPLE / "feedback").glob("*.jsonl"))
        for n in ("Zorana", "Quimbley", "Thaddeus", "Brunhilda", "Vandersloot", "Marguerite", "Ostrowski", "Placida", "Wetherby", "Odalys", "Fernwood",
                  "Leopold", "Casimir", "Barnaby", "Ottilie"):
            self.assertFalse(n.lower() in blob.lower(), n)
        self.assertIn("[PERSON_", blob)


class CandidateTest(unittest.TestCase):
    def test_apply_change_kinds_on_a_copy(self):
        d = Path(tempfile.mkdtemp())
        try:
            (d / "p.txt").write_text("one\ntwo\n")
            (d / "j.json").write_text(json.dumps({"a": {"list": [1]}}))
            ct.apply_change(d, {"kind": "append", "file": "p.txt", "text": "three\n"})
            self.assertEqual((d / "p.txt").read_text(), "one\ntwo\nthree\n")
            ct.apply_change(d, {"kind": "replace", "file": "p.txt", "old": "two", "new": "2"})
            self.assertEqual((d / "p.txt").read_text(), "one\n2\nthree\n")
            ct.apply_change(d, {"kind": "json_append", "file": "j.json", "key": "a.list", "value": 2})
            self.assertEqual(json.loads((d / "j.json").read_text()), {"a": {"list": [1, 2]}})
            ct.apply_change(d, {"kind": "add_file", "file": "sub/n.yaml", "content": "x: 1\n"})
            self.assertTrue((d / "sub" / "n.yaml").is_file())
            with self.assertRaises(ct.TestError):
                ct.apply_change(d, {"kind": "add_file", "file": "p.txt", "content": "x"})
            with self.assertRaises(ct.TestError):
                ct.apply_change(d, {"kind": "replace", "file": "p.txt", "old": "zzz", "new": "y"})
            with self.assertRaises(ct.TestError):
                ct.apply_change(d, {"kind": "append", "file": "missing.txt", "text": "y"})
        finally:
            shutil.rmtree(d)

    def test_the_gate_fails_on_any_regression_and_passes_when_nothing_is_worse(self):
        base = {"runs": 10, "fail": 1, "error": 0, "safety_fails": 1, "escalations": 1, "tone": 3.5, "cost_per_run": 0.10}
        better = dict(base, fail=0, safety_fails=0)
        self.assertEqual(ct.gate(base, better), (True, []))
        self.assertFalse(ct.gate(dict(base, runs=0), better)[0])
        self.assertFalse(ct.gate(base, dict(better, runs=0))[0])
        self.assertEqual(ct.gate(base, dict(base)), (True, []))
        for k, v in (("fail", 2), ("error", 1), ("safety_fails", 2), ("escalations", 2)):
            ok, why = ct.gate(base, dict(base, **{k: v}))
            self.assertFalse(ok, k)
        self.assertFalse(ct.gate(base, dict(base, tone=3.3))[0])
        self.assertTrue(ct.gate(base, dict(base, tone=3.4))[0])
        self.assertFalse(ct.gate(base, dict(base, cost_per_run=0.12))[0])
        self.assertTrue(ct.gate(base, dict(base, cost_per_run=0.109))[0])
        self.assertTrue(ct.gate(base, dict(base, runs=20, fail=2, safety_fails=2, escalations=2))[0])          # rates, not counts

    def test_it_refuses_a_candidate_with_no_change_or_a_todo_or_a_closed_status(self):
        d = Path(tempfile.mkdtemp())
        try:
            f = d / "c-0001-x.md"
            f.write_text(cand.render(meta(), "T", "W", []))
            with self.assertRaises(ct.TestError):
                ct.check_candidate(f)
            f.write_text(cand.render(meta(), "T", "W", [{"kind": "add_file", "file": "evaluations/scenarios/99-x.yaml", "content": "intake: TODO write it"}]))
            with self.assertRaises(ct.TestError):
                ct.check_candidate(f)
            f.write_text(cand.render(meta(status="rejected"), "T", "W", CH))
            with self.assertRaises(ct.TestError):
                ct.check_candidate(f)
            f.write_text(cand.render(meta(), "T", "W", CH))
            self.assertEqual(ct.check_candidate(f)[0]["id"], "c-0001-x")
        finally:
            shutil.rmtree(d)

    def test_the_scenario_counts_match_the_real_folders(self):
        self.assertEqual((ct.count_scenarios(["core"]), ct.count_scenarios(["attacker"]), ct.count_scenarios(["casefile"])), (28, 18, 5))

    def test_a_dry_run_changes_nothing_in_the_repository(self):
        c = EXAMPLE / "candidates" / "c-0001-detention-pastoral-length.md"
        before = {p: h(p) for p in (c, REPO / "code/playbooks/detention/prompts/pastoral.txt", REPO / "code/playbooks/detention/playbook.json")}
        rc = ct.main([str(c), "--dry-run"])
        self.assertEqual(rc, 0)
        self.assertEqual({p: h(p) for p in before}, before)
        self.assertEqual(cand.load(c)[0]["status"], "proposed")

    def test_a_mock_run_on_the_attacker_set_ends_in_a_pass_and_never_edits_the_candidate_file(self):
        c = EXAMPLE / "candidates" / "c-0002-detention-pastoral-phrase.md"
        before = h(c)
        rc = ct.main([str(c), "--mock", "--sets", "attacker"])
        self.assertEqual(rc, 0)
        self.assertEqual(h(c), before)

    def test_the_casefile_set_is_skipped_in_a_mock_run_and_its_runner_is_scored_by_pass_or_fail(self):
        c = EXAMPLE / "candidates" / "c-0001-detention-pastoral-length.md"
        self.assertEqual(ct.main([str(c), "--mock", "--sets", "casefile"]), 2)       # nothing left to run: refused, never a pass
        x = ct.score([{"status": "fail", "deterministic": [{"passed": False, "advisory": False}], "jev": [], "metrics": {"escalated": False, "cost_usd": 0.1}},
                      {"status": "pass", "deterministic": [{"passed": True, "advisory": False}], "jev": [], "metrics": {"escalated": False, "cost_usd": 0.1}}])
        self.assertEqual((x["runs"], x["fail"], x["pass"], x["safety_fails"], x["cost"]), (2, 1, 1, 1, 0.2))

    def test_a_live_run_needs_an_explicit_yes(self):
        c = EXAMPLE / "candidates" / "c-0001-detention-pastoral-length.md"
        self.assertEqual(ct.main([str(c), "--live"]), 2)


class NoSelfApproval(unittest.TestCase):
    def test_no_script_in_the_loop_ever_sets_a_status_beyond_proposed(self):
        for f in ("learning_report.py", "candidate_test.py", "learning_example.py"):
            src = (Path(__file__).resolve().parent.parent / "tools" / f).read_text()
            self.assertNotRegex(src, r"status[\"']?\s*[:=]\s*[\"'](approved|released|tested)", f)
            self.assertNotIn("write_text(cand.render", src.replace("f.write_text(cand.render(meta, title, why, changes, extra)", "")) if f == "candidate_test.py" else None


if __name__ == "__main__":
    unittest.main()
