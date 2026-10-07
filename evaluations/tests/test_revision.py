"""Revision helpers in the app server. Offline: no model, no network. Run: python3 -m pytest evaluations/tests -q"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "code"))
import app.server as srv


def test_base_id_and_version_order(monkeypatch):
    ids = ["detention-1-ab-v3", "detention-1-ab", "detention-1-ab-v2", "hospital-9-cd"]
    monkeypatch.setattr(srv.cf, "list_cases", lambda root: [{"id": i} for i in ids])
    assert srv.base_id("detention-1-ab-v2") == "detention-1-ab"
    assert srv.versions_of("detention-1-ab-v2") == ["detention-1-ab", "detention-1-ab-v2", "detention-1-ab-v3"]
    assert srv.next_version_id("detention-1-ab") == "detention-1-ab-v4"
    assert srv.next_version_id("hospital-9-cd") == "hospital-9-cd-v2"


def test_diff_marks_added_and_removed_lines():
    d = srv.diff_pages("a\nb\nc", "a\nB\nc")
    assert [x["t"] for x in d if x["t"] != "same"] == ["del", "add"]
    assert srv.diff_pages("same", "same") == [{"t": "same", "x": "same"}]


def test_original_intake_prefers_intake_page_and_drops_headers():
    assert srv.original_intake({"intake.md": "# Intake\n\nMaria called at 2 AM.\n"}) == "Maria called at 2 AM."


def test_original_intake_fallback_cuts_page_footer():
    pages = {"01-triage.md": "# 1. Triage\n\nSITUATION: x\n\n---\n[Index](index.md) · [Next](02-rights.md)\n\nNury is an AI assistant."}
    out = srv.original_intake(pages)
    assert out == "SITUATION: x" and "Index" not in out and "AI assistant" not in out


def test_revision_intake_appends_a_record_not_a_prediction(monkeypatch):
    monkeypatch.setattr(srv.cf, "load_case", lambda cid, root: {"pages": {"intake.md": "# Intake\n\nOriginal words."}, "meta": {"playbook": "detention"}})
    text, meta = srv.revision_intake("c1", "Call the attorney", "not_hoped", "The lawyer could not take it.")
    assert text.startswith("Original words.\n\nUPDATE FROM THE PASTOR")
    assert "did not go as hoped" in text and "The lawyer could not take it." in text
    assert text.count("UPDATE FROM THE PASTOR") == 1   # one dated record; everything in it is the pastor's own words
    assert meta["playbook"] == "detention"


def test_unknown_result_label_is_unknown(monkeypatch):
    monkeypatch.setattr(srv.cf, "load_case", lambda cid, root: {"pages": {"intake.md": "# Intake\n\nx"}, "meta": {}})
    text, _ = srv.revision_intake("c1", "", "bogus", "n")
    assert "Result: unknown" in text and "Step: not named" in text


def test_original_intake_reads_save_case_format():
    page = "# Intake\n\nWhat the pastor typed, exactly. A later update is added below it, never over it.\n\nMaria called at 2:07 AM.\n\n[Index](index.md)\n"
    assert srv.original_intake({"intake.md": page}) == "Maria called at 2:07 AM."
