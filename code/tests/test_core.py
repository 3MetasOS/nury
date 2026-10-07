"""Core tests. No network: a fake client stands in for Gloo.   Run: cd code && python3 -m unittest -v"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from nury import playbook as pbm  # noqa: E402
from nury.audit import AuditLog  # noqa: E402
from nury.engine import (UNSAFE_SUFFIX, CaseState, GateDecision, compute_outcome, get_playbook,  # noqa: E402
                         run_pipeline, run_scripted, run_stage)

TRIAGE = ("SITUATION: Carlos was detained in Aurora.\nPEOPLE: Maria, Carlos\nLOCATION: Aurora, CO\n"
          "FAMILY LANGUAGE: es\nURGENCY: High — kids at home\nMISSING FACTS:\n1. Where is he?\n2. Any case number?\n3. Any court date?")
RIGHTS = ("- Tiene derecho a guardar silencio. (ACLU Know Your Rights)\n"
          "- No firme nada sin hablar con un abogado. (ACLU Know Your Rights)\n"
          "Hable con un abogado de inmigración lo antes posible.")
ATTY = ("Recursos: https://www.immigrationadvocates.org/nonprofit/legaldirectory/ "
        "https://www.ailalawyer.com/ https://www.aclu.org/know-your-rights/immigrants-rights https://nipnlg.org/")
CHECK = "DO TONIGHT\n1. Busque papeles.\nDO NOT DO\n1. No firme.\nGATHER THESE DOCUMENTS\n1. Identificación."
PAST = "María, la iglesia está con ustedes. No están solos. Estamos buscando ayuda."
CANNED = {"triage": TRIAGE, "rights": RIGHTS, "attorney": ATTY, "checklist": CHECK, "pastoral": PAST}
ORDER = ["triage", "rights", "attorney", "checklist", "pastoral"]


class FakeClient:
    """Answers by stage. Spots the stage from the prompt text."""
    def __init__(self, canned=None):
        self.canned, self.inputs, self.calls = canned or CANNED, [], 0

    def ask(self, user_input, instructions=None, **kw):
        self.calls += 1
        self.inputs.append(user_input)
        key = ("triage" if "structured case" in instructions else "rights" if "rights brief" in instructions
               else "attorney" if "scannable list" in instructions
               else "pastoral" if "pastoral message" in instructions else "checklist")
        return self.canned[key], {"latency_s": 0.01, "input_tokens": 10, "output_tokens": 5, "model": "fake"}


class Core(unittest.TestCase):
    def test_full_run_complete(self):
        st, rs, au = run_scripted("intake", client=FakeClient())
        self.assertEqual([r.status for r in rs], ["approved"] * 5)
        self.assertEqual(st.outcome["outcome"], "package_complete")
        self.assertTrue(all("asistente de IA" in v for k, v in st.approved.items() if k != "triage"))
        self.assertIn("AI assistant", st.approved["triage"])

    def test_edit_flows_to_later_stages(self):
        c = FakeClient()
        st, rs, _ = run_scripted("intake", decisions={"rights": ("edit", "- EDITADO (ACLU Know Your Rights)")}, client=c)
        self.assertEqual(rs[1].status, "edited")
        self.assertTrue(any("EDITADO" in i for i in c.inputs[2:]))           # later stages read the edit
        self.assertIn("asistente de IA", st.approved["rights"])               # disclaimer re-appended
        self.assertIn("EDITADO", rs[2].input_context["rights"])

    def test_reject_once_then_pass(self):
        st, rs, au = run_scripted("intake", client=FakeClient(),
                                  fault_injection={"stage": "rights", "times": 1, "draft_suffix": UNSAFE_SUFFIX})
        r = rs[1]
        self.assertEqual((r.status, r.metrics["attempts"], r.metrics["retries"]), ("approved", 2, 1))
        self.assertEqual(r.reason_categories, ["banned_phrase"])
        self.assertNotIn("guarantee", r.shown_text)
        self.assertEqual(au.of_kind("draft_rejected")[0]["visible_to_pastor"], False)

    def test_escalation_and_gate_never_sees_unsafe(self):
        seen = []
        def gate(res):
            seen.append(res)
            return GateDecision("approve")
        st = CaseState("intake")
        rs = run_pipeline("detention", st, gate, FakeClient(), AuditLog(),
                          fault_injection={"stage": "rights", "times": 3, "draft_suffix": UNSAFE_SUFFIX})
        self.assertEqual(rs[-1].status, "escalated")
        self.assertEqual(rs[-1].metrics["attempts"], 3)
        self.assertEqual([s.stage_id for s in seen], ["triage"])               # rights never reached the gate
        self.assertTrue(all(s.attempts == [] for s in seen))
        self.assertEqual(st.outcome["outcome"], "escalated")
        self.assertIn("sources_list", st.outcome["package"])
        self.assertIn("vetted sources", st.outcome["message"])

    def test_stop(self):
        st, rs, _ = run_scripted("intake", decisions={"attorney": "stop"}, client=FakeClient())
        self.assertEqual(rs[-1].status, "stopped")
        self.assertEqual(len(rs), 3)
        self.assertEqual(st.outcome["outcome"], "stopped_by_pastor")
        self.assertEqual(st.outcome["message"], "I'll handle this manually.")

    def test_old_call_style_still_works(self):
        st = CaseState("intake")
        rs = run_pipeline(st, lambda r: GateDecision("approve"), FakeClient(), AuditLog(), stages=["triage"])
        self.assertEqual(rs[0].status, "approved")

    def test_floor_blocks_unvetted_link_phone_and_pastor_byline(self):
        bad = dict(CANNED, attorney=ATTY + " Llame al 555-123-4567 o visite https://evil.example.com",
                   pastoral=PAST + "\nPreparada por el pastor")
        for stage, cat in (("attorney", "ungrounded_claim"), ("pastoral", "banned_phrase")):
            st = CaseState("intake")
            st.approved["triage"], st.approved["rights"], st.approved["checklist"] = TRIAGE, RIGHTS, CHECK
            r = run_stage(stage, st, client=FakeClient(bad))
            self.assertEqual(r.status, "escalated")
            self.assertIn(cat, r.reason_categories)

    def test_triage_agency_names_flagged(self):
        bad = dict(CANNED, triage=TRIAGE.replace("Any case number?", "Was he taken by, for example, ICE?"))
        r = run_stage("triage", CaseState("intake"), client=FakeClient(bad))
        self.assertEqual(r.status, "escalated")
        self.assertIn("agency_name", r.reason_categories)
        ok = run_stage("triage", CaseState("intake"), client=FakeClient())
        self.assertEqual(ok.status, "approved")

    def test_agency_names_flagged_on_checklist_and_pastoral_not_on_rights_or_attorney(self):
        for stage, key, bad_text in (("checklist", "checklist", CHECK + "\n1. No hable con ICE."),
                                      ("pastoral", "pastoral", PAST + " ICE no puede separarlos.")):
            st = CaseState("intake")
            st.approved.update(triage=TRIAGE, rights=RIGHTS, attorney=ATTY, checklist=CHECK)
            r = run_stage(stage, st, client=FakeClient(dict(CANNED, **{key: bad_text})))
            self.assertEqual(r.status, "escalated", stage)
            self.assertIn("agency_name", r.reason_categories)
        # rights and attorney may name agencies that appear in vetted sources: no false escalation
        for stage, key, text in (("rights", "rights", RIGHTS + " (ICE)"), ("attorney", "attorney", ATTY + " ICE")):
            st = CaseState("intake")
            st.approved.update(triage=TRIAGE, rights=RIGHTS)
            r = run_stage(stage, st, client=FakeClient(dict(CANNED, **{key: text})))
            self.assertNotIn("agency_name", r.reason_categories, stage)

    def test_forced_rejection_env_targets_stage_2(self):
        import os
        os.environ["NURY_FORCE_REJECTION"] = "1"
        try:
            st, rs, _ = run_scripted("intake", client=FakeClient())
        finally:
            del os.environ["NURY_FORCE_REJECTION"]
        self.assertEqual([r.metrics["attempts"] for r in rs], [1, 2, 1, 1, 1])

    def test_language_check(self):
        bad = dict(CANNED, pastoral="Dios está con ustedes. As the Psalm says, God is our refuge and the strength of those who hurt.")
        st = CaseState("intake")
        r = run_stage("pastoral", st, client=FakeClient(bad))
        self.assertIn("language", r.reason_categories)


class Playbooks(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.src = pbm.PLAYBOOKS_DIR / "detention"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _copy(self, name="detention"):
        dst = self.tmp / name
        shutil.copytree(self.src, dst)
        return dst

    def test_when_condition_skips_stage(self):
        d = self._copy()
        sj = json.loads((d / "stages.json").read_text())
        next(s for s in sj if s["id"] == "checklist")["when"] = {"field": "triage.urgency", "in": ["low"]}
        (d / "stages.json").write_text(json.dumps(sj))
        pb = pbm.load_playbook("detention", self.tmp)
        st, rs, au = run_scripted("intake", client=FakeClient(), playbook=pb)
        self.assertEqual([r.status for r in rs], ["approved", "approved", "approved", "skipped", "approved"])
        self.assertEqual(st.outcome["outcome"], "package_complete")
        self.assertTrue(au.of_kind("stage_skipped"))

    def test_prompt_variant_by_field(self):
        d = self._copy()
        (d / "prompts" / "checklist_urgent.txt").write_text("Task: URGENT checklist in {{lang_name}}.\n{{vetted_points}}\nchecklist")
        sj = json.loads((d / "stages.json").read_text())
        next(s for s in sj if s["id"] == "checklist")["variants"] = [
            {"when": {"field": "urgency", "in": ["high"]}, "prompt": "prompts/checklist_urgent.txt"}]
        (d / "stages.json").write_text(json.dumps(sj))
        pb = pbm.load_playbook("detention", self.tmp)
        text = pbm.render_prompt(pb.registry["checklist"], pb, "es", None, {"urgency": "High — kids"})
        self.assertIn("URGENT", text)
        self.assertNotIn("URGENT", pbm.render_prompt(pb.registry["checklist"], pb, "es", None, {"urgency": "low"}))

    def test_second_playbook_zero_engine_changes(self):
        d = self.tmp / "hospital"
        (d / "prompts").mkdir(parents=True)
        (d / "sources").mkdir()
        shutil.copy(self.src / "outcomes.json", d)
        pj = json.loads((self.src / "playbook.json").read_text())
        pj.update(id="hospital", title="Hospital emergency", description="A family member is in the hospital.",
                  disclaimer={"en": "Nury is an AI assistant, not a doctor, nurse, or pastor. This is general information, not medical advice. Please ask the hospital care team.",
                              "es": "Nury es un asistente de IA, no es médico, enfermero ni pastor. Esto es información general, no consejo médico. Por favor pregunte al equipo del hospital."},
                  boundary={"who": "a family with a loved one in the hospital", "domain": "medical",
                            "professional": "hospital care team", "professional_kind": "doctor"})
        (d / "playbook.json").write_text(json.dumps(pj))
        (d / "prompts" / "triage.txt").write_text("Task: turn the pastor's raw intake into a structured case. Write in English for the pastor. Use the labels SITUATION, PEOPLE, LOCATION, FAMILY LANGUAGE, URGENCY, MISSING FACTS (exactly 3). Facts only.")
        (d / "prompts" / "note.txt").write_text("Task: write a short note in {{lang_name}} from {{vetted_points}}")
        (d / "sources" / "facts.json").write_text(json.dumps({"items": [{"t": "Visiting hours", "es": "Hay visitas."}]}))
        (d / "stages.json").write_text(json.dumps([
            {**json.loads((self.src / "stages.json").read_text())[0],
             "checks": [c for c in json.loads((self.src / "stages.json").read_text())[0]["checks"] if c["name"] != "no_agency_names"]},
            {"id": "note", "title": "2. Note", "audience": "family", "prompt": "prompts/note.txt",
             "input": {"from": "context"}, "deps": ["triage"],
             "sources": [{"name": "facts", "file": "facts.json", "var": "vetted_points",
                          "groups": [{"list": "items", "line": "- {t}: {es}"}]}],
             "checks": [{"name": "max_words", "limit": 50}]}]))
        pb = pbm.load_playbook("hospital", self.tmp)
        seen = []
        class C(FakeClient):
            def ask(self, u, instructions=None, **kw):
                seen.append(instructions)
                t = TRIAGE if "structured case" in instructions else "Hay visitas. Hable con un abogado."
                return t, {"latency_s": 0, "input_tokens": 1, "output_tokens": 1, "model": "f"}
        st, rs, _ = run_scripted("intake", client=C(), playbook=pb)
        self.assertEqual([r.status for r in rs], ["approved", "approved"])
        self.assertEqual(st.outcome["outcome"], "package_complete")
        everything = "\n".join(seen) + json.dumps(pb.disclaimer) + pb.title + pb.description
        self.assertNotIn("immigra", everything.lower())
        self.assertNotIn("legal", "\n".join(seen).lower().replace("legal aid", ""))
        self.assertIn("medical", seen[0])
        self.assertIn("hospital care team", seen[0])
        self.assertNotIn("immigra", rs[1].shown_text.lower())

    def test_playbook_cannot_drop_disclaimer_floor(self):
        d = self._copy()
        pj = json.loads((d / "playbook.json").read_text())
        pj["disclaimer"]["en"] = "This is info."
        (d / "playbook.json").write_text(json.dumps(pj))
        with self.assertRaises(pbm.PlaybookError):
            pbm.load_playbook("detention", self.tmp)

    def test_loader_lists_and_validates(self):
        self.assertIn("detention", [p["id"] for p in pbm.list_playbooks()])
        self.assertEqual([s.id for s in get_playbook().stages], ORDER)


if __name__ == "__main__":
    unittest.main()
