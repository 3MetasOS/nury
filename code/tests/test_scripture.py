"""Scripture in the pastoral message. No network. The model picks an id; the app inserts the exact text."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nury import checks as ck  # noqa: E402
from nury import playbook as pbm  # noqa: E402
from nury import scripture as scr  # noqa: E402
from nury import scripture_providers as scrp  # noqa: E402
from nury.audit import AuditLog  # noqa: E402
from nury.engine import CaseState, GateDecision, run_stage  # noqa: E402
from test_core import CANNED, TRIAGE, FakeClient  # noqa: E402

WHY = "Dios está cerca de quienes tienen miedo."
MSG = "María, la iglesia está con ustedes. No están solos."


class Pastoral(FakeClient):
    """A model that answers the pastoral stage with the text you give it."""
    def __init__(self, reply):
        super().__init__(CANNED)
        self.reply = reply
        self.last = ""

    def ask(self, user_input, instructions=None, **kw):
        self.last = instructions
        if "pastoral message" in instructions:
            r = self.reply(instructions, user_input) if callable(self.reply) else self.reply
            return r, {"latency_s": 0.01, "input_tokens": 10, "output_tokens": 5, "model": "fake"}
        return super().ask(user_input, instructions=instructions, **kw)


def reply(verse, why=WHY, msg=MSG):
    return f"VERSE: {verse}\nWHY: {why}\nMESSAGE: {msg}"


class Base(unittest.TestCase):
    PB = "detention"
    approve = "all"

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(pbm.PLAYBOOKS_DIR, self.tmp, dirs_exist_ok=True)
        self.src = self.tmp / self.PB / "sources"
        self.set_approvals(self.approve)
        self.pb = pbm.load_playbook(self.PB, self.tmp)
        self.root = self.tmp / "church"
        self.root.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def set_approvals(self, which):
        a = json.loads((self.src / "approvals.json").read_text())
        ids = [v["source_id"] for v in json.loads((self.src / "scripture.json").read_text())["verses"]]
        for i in ids:
            a[i] = "approved" if which == "all" or i in which else "pending"
        (self.src / "approvals.json").write_text(json.dumps(a))

    def state(self):
        st = CaseState("intake", "es")
        st.approved["triage"] = TRIAGE
        return st

    def run_past(self, client, **kw):
        st = self.state()
        au = AuditLog()
        rec = run_stage("pastoral", st, client=client, audit=au, playbook=self.pb, **kw)
        return rec, st, au

    def verse(self, vid, lang="es"):
        return next(e for e in scr.for_language(scr.load_bank(self.pb.dir, church=False), lang) if e["id"] == vid)


class Bank(Base):
    approve = ["scr-psa46-1", "scr-psa23-4"]

    def test_only_approved_verses_are_offered(self):
        ids = [e["id"] for e in scr.for_language(scr.load_bank(self.pb.dir, church=False), "es")]
        self.assertEqual(sorted(ids), ["psa23_4", "psa46_1"])

    def test_nothing_approved_means_no_verse_and_the_stage_still_runs(self):
        self.set_approvals([])
        pb = pbm.load_playbook("detention", self.tmp)
        self.pb = pb
        c = Pastoral(reply("NONE", "", MSG))
        rec, _, _ = self.run_past(c)
        self.assertEqual(rec.status, "approved")
        self.assertIsNone(rec.scripture)
        self.assertIn("(none)", c.last)
        self.assertNotIn("psa46_1", c.last)
        rec2, _, _ = self.run_past(Pastoral(reply("psa46_1")))      # an unapproved id is not allowed
        self.assertEqual(rec2.status, "escalated")

    def test_the_dev_flag_shows_pending_verses_but_never_rejected_ones(self):
        import os
        a = json.loads((self.src / "approvals.json").read_text())
        a["scr-psa34-18"] = "rejected"
        (self.src / "approvals.json").write_text(json.dumps(a))
        os.environ["NURY_ALLOW_PENDING"] = "1"
        try:
            ids = [e["id"] for e in scr.for_language(scr.load_bank(self.pb.dir, church=False), "es")]
        finally:
            del os.environ["NURY_ALLOW_PENDING"]
        self.assertIn("psa23_4", ids)
        self.assertNotIn("psa34_18", ids)
        self.assertEqual([e["id"] for e in scr.for_language(scr.load_bank(self.pb.dir, church=False), "es")], ["psa46_1", "psa23_4"])

    def test_the_real_bank_fits_the_cap_has_sources_and_a_license(self):
        for pid, n in (("detention", 10), ("hospital", 12)):
            d = json.loads((pbm.PLAYBOOKS_DIR / pid / "sources" / "scripture.json").read_text())
            self.assertEqual(len(d["verses"]), n)
            self.assertEqual(d["tradition"], "none")
            self.assertEqual(d["max_block_words"], 52)
            for lg in ("es", "en"):
                self.assertTrue(d["translations"][lg]["license"].lower().startswith("public domain"))
                self.assertTrue(d["translations"][lg]["license_page"].startswith("https://"))
            for v in d["verses"]:
                self.assertTrue(v["source_url_es"] and v["source_url_en"], v["id"])
                self.assertLessEqual(max(len(v["text_es"].split()), len(v["text_en"].split())), 52, v["id"])
                self.assertEqual(v["source_id"], "scr-" + v["id"].replace("_", "-"))
            a = json.loads((pbm.PLAYBOOKS_DIR / pid / "sources" / "approvals.json").read_text())
            self.assertTrue(all(v["source_id"] in a for v in d["verses"]))

    def test_tradition_other_than_none_and_text_over_the_cap_are_refused(self):
        f = self.src / "scripture.json"
        d = json.loads(f.read_text())
        d["tradition"] = "other"
        f.write_text(json.dumps(d))
        with self.assertRaises(scr.ScriptureError):
            scr.load_bank(self.pb.dir, church=False)
        d["tradition"] = "none"
        d["verses"][0]["text_es"] = "palabra " * 53
        f.write_text(json.dumps(d))
        with self.assertRaises(scr.ScriptureError):
            scr.load_bank(self.pb.dir, church=False)


class Church(Base):
    approve = ["scr-psa46-1"]

    def put(self, **over):
        v = {"id": "church-1", "themes": ["comfort"], "reference_es": "Salmo 91:1", "text_es": "Texto exacto de la fuente.",
             "translation_es": "Reina-Valera 1909", "source_url": "https://ebible.org/spaRV1909/PSA091.htm",
             "license": "Public domain", "approved": True}
        v.update(over)
        (self.root / "scripture.json").write_text(json.dumps({"verses": [v]}))

    def test_church_verse_with_source_and_license_is_offered(self):
        self.put()
        ids = [e["id"] for e in scr.for_language(scr.load_bank(self.pb.dir, str(self.root)), "es")]
        self.assertEqual(ids, ["psa46_1", "church-1"])
        self.assertEqual(scr.list_verses(self.pb, "es", str(self.root))[1]["reference"], "Salmo 91:1")

    def test_church_verse_without_source_or_license_or_translation_is_refused(self):
        for bad in ({"source_url": ""}, {"license": ""}, {"translation_es": ""}, {"id": "mine"}, {"themes": []}):
            self.put(**bad)
            with self.assertRaises(scr.ScriptureError, msg=bad):
                scr.load_bank(self.pb.dir, str(self.root))

    def test_church_verse_is_ignored_until_approved(self):
        self.put(approved=False)
        ids = [e["id"] for e in scr.for_language(scr.load_bank(self.pb.dir, str(self.root)), "es")]
        self.assertEqual(ids, ["psa46_1"])


class Engine(Base):
    def test_the_engine_inserts_the_exact_text_and_reference(self):
        rec, _, au = self.run_past(Pastoral(reply("psa46_1")))
        v = self.verse("psa46_1")
        self.assertEqual(rec.status, "approved")
        self.assertIn(f"«{v['text']}»\n— {v['reference']}, {v['translation']}", rec.draft)
        self.assertEqual(rec.scripture["id"], "psa46_1")
        self.assertEqual(rec.note, scr.SCRIPTURE_NOTE)
        self.assertTrue(rec.draft.index(MSG) < rec.draft.index("«") < rec.draft.index(WHY))
        self.assertEqual([e["verse"] for e in au.events if e["kind"] == "scripture"], ["psa46_1"])
        self.assertEqual(ck.verse_block_verbatim({}, rec.draft, SimpleNamespace(scripture={"x": v})), [])

    def test_english_family_gets_the_english_translation(self):
        st = self.state()
        st.language = "en"
        st.approved["triage"] = TRIAGE.replace("FAMILY LANGUAGE: es", "FAMILY LANGUAGE: en")
        c = Pastoral(reply("psa46_1", "God is near to people who are afraid.", "Maria, the church is with you. You are not alone."))
        rec = run_stage("pastoral", st, client=c, playbook=self.pb)
        self.assertEqual(rec.status, "approved", rec.attempts)
        self.assertIn("a very present help in trouble", rec.draft)
        self.assertIn("World English Bible", rec.draft)

    def test_different_cases_can_get_different_verses_and_none_is_allowed(self):
        def pick(ins, inp):
            return reply("psa23_4") if "hospital" in inp else reply("NONE", "", MSG) if "calm" in inp else reply("psa46_1")
        got = []
        for text in ("detained, scared", "hospital bedside", "calm, only checking"):
            st = self.state()
            st.approved["triage"] = TRIAGE
            st.approved["checklist"] = text
            r = run_stage("pastoral", st, client=Pastoral(lambda i, u: pick(i, u)), playbook=self.pb)
            got.append(r.scripture["id"] if r.scripture else None)
        self.assertEqual(got, ["psa46_1", "psa23_4", None])
        self.assertTrue(len(set(got)) == 3)

    def test_the_prompt_lists_every_approved_verse_with_themes_and_no_id_is_forced(self):
        c = Pastoral(reply("NONE", "", MSG))
        rec, _, _ = self.run_past(c)
        self.assertEqual(rec.status, "approved")
        for vid in ("psa46_1", "rom8_38_39", "psa34_18"):
            self.assertIn(vid, c.last)
        self.assertIn("themes: presence, comfort", c.last)
        self.assertIsNone(rec.scripture)
        self.assertNotIn("«", rec.draft)

    def test_model_written_scripture_is_rejected_and_regenerated(self):
        seq = iter([reply("psa46_1", "Como dice el Salmo 46:1, Dios es nuestro amparo.", MSG), reply("psa46_1")])
        rec, _, au = self.run_past(Pastoral(lambda i, u: next(seq)))
        self.assertEqual(rec.status, "approved")
        self.assertEqual(rec.attempts[0]["violations"][0]["category"], "invented_scripture")
        self.assertEqual(rec.metrics["attempts"], 2)
        quote = self.verse("psa46_1")["text"]
        rec2, _, _ = self.run_past(Pastoral(reply("psa46_1", WHY, MSG + " " + quote)))
        self.assertEqual(rec2.status, "escalated")

    def test_bad_format_unknown_id_and_why_with_none_are_rejected(self):
        for bad in ("Solo un mensaje sin etiquetas.", reply("jer29_11"), reply("NONE", WHY, MSG),
                    reply("psa46_1", "", MSG), reply("psa46_1", "Uno. Dos. Tres.", MSG), reply("psa46_1", WHY, "")):
            rec, _, _ = self.run_past(Pastoral(bad))
            self.assertEqual(rec.status, "escalated", bad)
            self.assertIsNone(rec.draft)

    def test_providence_claims_in_the_why_lines_are_rejected(self):
        for why in ("Dios lo liberará de esto.", "Todo pasa por algo.", "Es la voluntad de Dios.",
                    "Dios tiene un plan para ustedes.", "Dios está probando su fe."):
            rec, _, _ = self.run_past(Pastoral(reply("psa46_1", why)))
            self.assertEqual(rec.status, "escalated", why)
            self.assertIn("providence_claim", rec.reason_categories)

    def test_the_why_lines_still_face_the_promise_check_but_the_verse_does_not(self):
        rec, _, _ = self.run_past(Pastoral(reply("isa41_10", "Pronto vamos a visitarlos.")))
        self.assertEqual(rec.status, "escalated")
        self.assertIn("unauthorized_promise", rec.reason_categories)
        # Isaiah 41:10 says 'I will help you'. That is the verse's own text, quoted, so it is not checked as a promise.
        ok, _, _ = self.run_past(Pastoral(reply("isa41_10")))
        self.assertEqual(ok.status, "approved")
        self.assertIn("ayudaré", ok.draft)

    def test_the_word_cap_counts_nury_sentences_not_the_verse_block(self):
        rec, _, _ = self.run_past(Pastoral(reply("rom8_38_39")))
        self.assertEqual(rec.status, "approved")
        long = "La iglesia está con ustedes. " * 25
        rec2, _, _ = self.run_past(Pastoral(reply("psa46_1", WHY, long)))
        self.assertEqual(rec2.status, "escalated")
        self.assertIn("length", rec2.reason_categories)

    def test_pastor_edits_of_the_verse_are_flagged_and_other_edits_are_not(self):
        rec, _, au = self.run_past(Pastoral(reply("psa46_1")), gate=lambda r: GateDecision("edit", r.draft.replace("amparo", "refugio")))
        warns = [e for e in au.events if e["kind"] == "edit_check"][0]["warnings"]
        self.assertEqual([w["category"] for w in warns], ["scripture_altered"])
        rec2, _, au2 = self.run_past(Pastoral(reply("psa46_1")), gate=lambda r: GateDecision("edit", r.draft.replace("No están solos.", "Aquí estamos.")))
        self.assertEqual([e for e in au2.events if e["kind"] == "edit_check"][0]["warnings"], [])

    def test_swap_replaces_the_verse_with_exact_text_and_leaves_the_why_alone(self):
        rec, _, _ = self.run_past(Pastoral(reply("psa46_1")))
        new = self.verse("psa23_4")
        out = scr.swap_verse(rec.draft, new)
        self.assertIn(f"«{new['text']}»\n— {new['reference']}, {new['translation']}", out)
        self.assertNotIn(self.verse("psa46_1")["text"], out)
        self.assertIn(WHY, out)
        self.assertIn(MSG, out)
        self.assertEqual(scr.swap_verse(out, None).count("«"), 0)
        plain = scr.swap_verse(MSG, new)
        self.assertTrue(plain.startswith(MSG) and plain.count("«") == 1)

    def test_a_prompt_is_byte_identical_whatever_the_model_chose(self):
        a, b = Pastoral(reply("psa46_1")), Pastoral(reply("NONE", "", MSG))
        self.run_past(a)
        self.run_past(b)
        self.assertEqual(a.last, b.last)


class HospitalBank(Base):
    PB = "hospital"

    def test_hospital_offers_its_twelve_verses_and_inserts_one(self):
        ids = [e["id"] for e in scr.for_language(scr.load_bank(self.pb.dir, church=False), "es")]
        self.assertEqual(len(ids), 12)
        self.assertIn("psa121_1_2", ids)
        st = CaseState("intake", "es")
        st.approved["triage"] = TRIAGE
        from test_core import HCANNED, HFake
        c = HFake(dict(HCANNED, pastoral=reply("2co1_3_4")))
        rec = run_stage("pastoral", st, client=c, playbook=self.pb)
        self.assertEqual(rec.status, "approved", rec.attempts)
        self.assertIn("Padre de misericordias", rec.draft)


class StubHTTP:
    """Stands in for requests. Records every call. mode: ok | 429 | 403 | boom | nocopyright | long | html."""
    def __init__(self, mode="ok"):
        self.mode, self.calls = mode, []

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append({"url": url, "params": params, "headers": headers, "timeout": timeout})
        mode = self.mode
        if mode == "boom":
            raise TimeoutError("slow")
        code = {"429": 429, "403": 403}.get(mode, 200)
        body = {}
        if "/passages/" in url:
            body = {"id": url.rsplit("/", 1)[1], "reference": "Salmos 46:1",
                    "content": ("palabra " * 60 if mode == "long" else "<b>x</b>" if mode == "html" else "Dios es nuestro refugio y fortaleza, nuestro pronto auxilio en las tribulaciones.")}
        else:
            body = {"id": 7, "abbreviation": "RVR60", "copyright": "" if mode == "nocopyright" else "Sociedades Biblicas Unidas 1960"}

        class R:
            status_code = code
            def json(self_):
                return body
        return R()


class Providers(Base):
    def go(self, http, verse="psa46_1", intake="intake", lang="es", providers="yv"):
        chain = [scrp.YouVersionProvider("KEY123", {"es": "7", "en": "9"}, http=http), scrp.BankProvider()] if providers == "yv" else None
        st = CaseState(intake, lang)
        st.approved["triage"] = TRIAGE
        au = AuditLog()
        rec = run_stage("pastoral", st, client=Pastoral(reply(verse)), audit=au, playbook=self.pb, scripture_providers=chain)
        return rec, au

    def test_no_key_means_bank_only_and_a_key_adds_youversion_first(self):
        self.assertEqual([p.name for p in scrp.default_chain(env={})], ["bank"])
        self.assertEqual([p.name for p in scrp.default_chain(env={"YVP_APP_KEY": "k", "YVP_BIBLE_ES": "7"})], ["youversion", "bank"])
        self.assertEqual(scrp.default_chain(env={"YVP_APP_KEY": "k", "YVP_BIBLE_ES": "7"})[0].bibles, {"es": "7"})

    def test_youversion_text_is_inserted_with_version_and_copyright_and_checked_against_what_it_returned(self):
        http = StubHTTP()
        rec, au = self.go(http)
        self.assertEqual(rec.status, "approved", rec.attempts)
        self.assertIn("«Dios es nuestro refugio y fortaleza, nuestro pronto auxilio en las tribulaciones.»", rec.draft)
        self.assertIn("— Salmos 46:1, RVR60. Sociedades Biblicas Unidas 1960", rec.draft)
        self.assertNotIn(self.verse("psa46_1")["text"], rec.draft)
        self.assertEqual([e["provider"] for e in au.events if e["kind"] == "scripture"], ["youversion"])
        self.assertEqual(http.calls[0]["headers"]["X-YVP-App-Key"], "KEY123")
        self.assertTrue(http.calls[0]["url"].endswith("/v1/bibles/7/passages/PSA.46.1"))

    def test_any_failure_falls_back_to_the_bank_and_is_logged(self):
        for mode in ("429", "403", "boom", "nocopyright", "long", "html"):
            rec, au = self.go(StubHTTP(mode))
            self.assertEqual(rec.status, "approved", mode)
            self.assertIn(self.verse("psa46_1")["text"], rec.draft, mode)
            self.assertEqual([e["provider"] for e in au.events if e["kind"] == "scripture"], ["bank"], mode)
            fb = [e for e in au.events if e["kind"] == "scripture_fallback"]
            self.assertEqual(len(fb), 1, mode)
            self.assertIn("youversion", fb[0]["reasons"][0])

    def test_a_language_with_no_chosen_version_uses_the_bank(self):
        http = StubHTTP()
        chain = [scrp.YouVersionProvider("K", {"en": "9"}, http=http), scrp.BankProvider()]
        st = CaseState("intake", "es")
        st.approved["triage"] = TRIAGE
        rec = run_stage("pastoral", st, client=Pastoral(reply("psa46_1")), playbook=self.pb, scripture_providers=chain)
        self.assertIn(self.verse("psa46_1")["text"], rec.draft)
        self.assertEqual(http.calls, [])

    def test_only_a_passage_id_and_a_version_leave_the_app_never_names_or_case_text(self):
        http = StubHTTP()
        self.go(http, intake="Pastor, soy Maria Lopez, mi esposo Carlos fue detenido en Mesa. Mi telefono es 303-555-0100.")
        self.assertEqual(len(http.calls), 2)
        for c in http.calls:
            blob = json.dumps(c, ensure_ascii=False)
            for secret in ("Maria", "Lopez", "Carlos", "Mesa", "303", "detenido"):
                self.assertNotIn(secret, blob)
            self.assertEqual(sorted(c["headers"]), ["Accept", "X-YVP-App-Key"])
            self.assertTrue(c["url"].startswith("https://api.youversion.com/v1/bibles/7"))
        self.assertEqual(http.calls[0]["params"], {"format": "text"})

    def test_nothing_is_cached(self):
        http = StubHTTP()
        self.go(http)
        self.go(http)
        self.assertEqual(len(http.calls), 4)

    def test_a_church_verse_is_never_sent_to_youversion(self):
        Church.put(self)
        http = StubHTTP()
        chain = [scrp.YouVersionProvider("K", {"es": "7"}, http=http), scrp.BankProvider()]
        entry = [e for e in scr.for_language(scr.load_bank(self.pb.dir, str(self.root)), "es") if e["id"] == "church-1"][0]
        passage, notes = scrp.fetch(entry, "es", chain)
        self.assertEqual(passage["source"], "bank")
        self.assertEqual(http.calls, [])

    def test_a_changed_word_after_the_fetch_is_caught_against_what_the_provider_returned(self):
        http = StubHTTP()
        rec, au = self.go(http)
        bad = rec.draft.replace("refugio", "amparo")
        ctx = SimpleNamespace(scripture={"psa46_1": {"text": "Dios es nuestro refugio y fortaleza, nuestro pronto auxilio en las tribulaciones.",
                                                     "reference": "Salmos 46:1", "translation": "RVR60",
                                                     "copyright": "Sociedades Biblicas Unidas 1960"}}, scripture_cap=52)
        self.assertEqual(ck.verse_block_verbatim({}, rec.draft, ctx), [])
        self.assertEqual(ck.verse_block_verbatim({}, bad, ctx)[0]["category"], "scripture_altered")

    def test_every_bank_verse_has_a_passage_id_for_youversion(self):
        for pid in ("detention", "hospital"):
            for v in json.loads((pbm.PLAYBOOKS_DIR / pid / "sources" / "scripture.json").read_text())["verses"]:
                self.assertRegex(v["usfm"], r"^[1-3A-Z]{3}\.\d+\.\d+(-\d+)?$", v["id"])


class Checks(unittest.TestCase):
    def test_no_providence_claims_catches_both_languages_and_allows_presence(self):
        c = SimpleNamespace(scripture={})
        for t in ("God will heal him.", "God will free your son.", "Everything happens for a reason.", "It is God's plan.",
                  "God is punishing us.", "Dios lo sanará.", "Dios los traerá de vuelta.", "Todo sucede por algo.",
                  "Es la voluntad de Dios.", "Eso es un castigo de Dios."):
            self.assertTrue(ck.no_providence_claims({}, t, c), t)
        for t in ("God is with you.", "Dios está con ustedes.", "Dios los acompaña en esta noche difícil.",
                  "You are not alone, and God is near to the brokenhearted."):
            self.assertEqual(ck.no_providence_claims({}, t, c), [], t)

    def test_verse_block_verbatim_rejects_a_changed_word_a_wrong_reference_and_two_blocks(self):
        v = {"id": "a", "reference": "Salmo 46:1", "text": "Dios es nuestro amparo y fortaleza.", "translation": "Reina-Valera 1909"}
        c = SimpleNamespace(scripture={"a": v}, scripture_cap=52)
        good = scr.block(v)
        self.assertEqual(ck.verse_block_verbatim({}, "Hola.\n\n" + good, c), [])
        self.assertEqual(ck.verse_block_verbatim({}, "Hola.", c), [])
        for bad in (good.replace("amparo", "refugio"), good.replace("46:1", "46:2"), good + "\n\n" + good):
            self.assertEqual(ck.verse_block_verbatim({}, bad, c)[0]["category"], "scripture_altered")


if __name__ == "__main__":
    unittest.main()
