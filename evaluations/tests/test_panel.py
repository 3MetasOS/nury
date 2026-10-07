"""Panel logic that needs no model. Run: python3 -m pytest evaluations/tests -q"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "code"))
from judges import redteam_panel as rp


def rev(model, *quotes, error=None):
    return {"model": model, "error": error, "findings": [{"stage": "checklist", "quote": q, "category": "advice", "quote_verified": True} for q in quotes]}


def test_two_reviewers_quoting_the_same_sentence_is_corroborated():
    r = [rev("a", "No hable con nadie antes de hablar con un abogado."), rev("b", "No hable con nadie antes de hablar con un abogado"), rev("c")]
    c = rp.corroborate(r)
    assert len(c) == 1 and sorted(c[0]["reviewers"]) == ["a", "b"]


def test_single_reviewer_finding_is_not_corroborated_and_advisory_does_not_force_review():
    r = [rev("gloo-openai-gpt-5.4", "Llame a un abogado ahora."), rev("gloo-meta-llama-4-maverick"), rev("gloo-google-gemini-3.1-pro")]
    assert rp.corroborate(r) == []
    assert rp.needs_human(r, []) is False


def test_unverified_quotes_never_corroborate():
    r = [rev("a", "texto inventado uno"), rev("b", "texto inventado uno")]
    for x in r:
        x["findings"][0]["quote_verified"] = False
    assert rp.corroborate(r) == []


def test_all_reviewers_failing_goes_to_a_human():
    r = [rev("a", error="x"), rev("b", error="y"), rev("c", error="z")]
    assert rp.needs_human(r, []) is True


def test_gating_reviewer_finding_forces_review(monkeypatch):
    monkeypatch.setitem(rp.ROLES, "a", "gating")
    assert rp.needs_human([rev("a", "algo")], []) is True


def test_lenient_parser_survives_unescaped_quotes_and_still_flags_fake_quotes():
    t = '{"findings":[{"stage":"checklist","quote":"No hable con "nadie" antes.","category":"advice","reason":"x"}]}'
    f = rp._json(t)["findings"]
    assert f[0]["quote"] == 'No hable con "nadie" antes.' and f[0]["category"] == "advice"
    assert rp._json('{"findings": []}') == {"findings": []}
