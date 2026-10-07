"""The app's feedback, ledger and Improvement wiring. Offline: an in-process server on a random localhost port, a fake session, temp dirs.
No model call: a real Session would start the pipeline, so these tests insert a stand-in. Run: python3 -m pytest evaluations/tests -q"""
import json
import sys
import threading
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "code" / "tests"))
import nonet  # noqa: E402,F401  (keeps the Gloo client and the Jev gate off the network)
from app import server  # noqa: E402
from nury import feedback  # noqa: E402


@pytest.fixture
def srv(monkeypatch, tmp_path):
    monkeypatch.setenv("NURY_FEEDBACK_DIR", str(tmp_path / "fb"))
    monkeypatch.setenv("NURY_LEDGER_DIR", str(tmp_path / "ledger"))
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.H)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"
    server.SESSIONS["fake0001"] = SimpleNamespace(pb=SimpleNamespace(id="detention"), language="es", rec=SimpleNamespace(run_id="r-test"))
    yield base, tmp_path
    server.SESSIONS.pop("fake0001", None)
    httpd.shutdown()


def get(base, path):
    return json.loads(urllib.request.urlopen(base + path, timeout=10).read())


def post(base, path, body):
    r = urllib.request.Request(base + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=10).read())


def test_consent_sentence_is_offered_only_when_capture_is_on(srv, monkeypatch):
    base, _ = srv
    monkeypatch.delenv("NURY_FEEDBACK", raising=False)
    f = get(base, "/api/features")
    assert f["feedback"] is False and f["consent_sentence"] == "" and f["chips"] == []
    monkeypatch.setenv("NURY_FEEDBACK", "on")
    f = get(base, "/api/features")
    assert f["feedback"] is True and f["consent_sentence"] == feedback.CONSENT_SENTENCE
    assert [c["slug"] for c in f["chips"]] == list(feedback.CHIPS)
    monkeypatch.setenv("NURY_FEEDBACK", "counts")      # strict mode: the same sentence is still true
    assert get(base, "/api/features")["consent_sentence"] == feedback.CONSENT_SENTENCE
    assert feedback.CONSENT_SENTENCE == "Nury also records what you change, without names, to improve its drafts; a person reviews every change before it is used."


def test_chip_post_is_off_by_default_and_ignores_bad_input(srv, monkeypatch):
    base, tmp = srv
    monkeypatch.delenv("NURY_FEEDBACK", raising=False)
    assert post(base, "/api/feedback", {"session": "fake0001", "stage": "pastoral", "chip": "too_long"}) == {"ok": False}
    monkeypatch.setenv("NURY_FEEDBACK", "on")
    assert post(base, "/api/feedback", {"session": "nope", "stage": "pastoral", "chip": "too_long"}) == {"ok": False}
    assert post(base, "/api/feedback", {"session": "fake0001", "stage": "pastoral", "chip": "<script>"}) == {"ok": False}
    assert not (tmp / "fb").exists() or not list((tmp / "fb").glob("*")), "nothing is written for refused input"


def test_chip_post_records_a_slug_and_never_returns_the_file(srv, monkeypatch):
    base, tmp = srv
    monkeypatch.setenv("NURY_FEEDBACK", "on")
    assert post(base, "/api/feedback", {"session": "fake0001", "stage": "pastoral", "chip": "too_long"}) == {"ok": True}
    lines = [json.loads(l) for f in (tmp / "fb").glob("*") for l in f.read_text().splitlines()]
    assert lines and lines[0].get("reason_chip") == "too_long" and lines[0].get("stage") == "pastoral"
    assert lines[0].get("run") == "r-test" and lines[0].get("playbook") == "detention"
    for path in ("/api/improvement", "/api/ops", "/api/evals"):
        assert "r-test" not in json.dumps(get(base, path)), f"{path} must not return feedback lines"


def test_progress_has_a_real_jev_phase():
    s = server.Session.progress
    src = Path(server.__file__).read_text(encoding="utf-8")
    assert '"jev_gate_start"' in src and 'phase = "checking_jev"' in src
    assert 'Checking the draft with Jev' in (ROOT / "code/app/static/index.html").read_text(encoding="utf-8")
    assert callable(s)


def test_improvement_api_returns_metadata_and_aggregates_only(srv):
    base, _ = srv
    d = get(base, "/api/improvement")
    assert d["synthetic"] is True and "synthetic" in d["source"]
    assert d["candidates"] and all(c["status"] in ("proposed", "tested", "approved", "released", "rejected") for c in d["candidates"])
    blob = json.dumps(d)
    for banned in ("Maria", "Carlos", "Jose", "Lopez", '"draft"', '"intake"'):
        assert banned not in blob
    for c in d["candidates"]:
        assert set(c) >= {"id", "title", "type", "status", "evidence", "why", "approved", "test"}
        assert c["approved"] is False or c["approved_by"]


def test_session_records_to_the_ledger_and_closes_it(monkeypatch, tmp_path):
    """The Session wiring: a Recorder per run, stage_done after each stage, finish at the end. Source check; a live run is not made here."""
    src = Path(server.__file__).read_text(encoding="utf-8")
    assert "ledger.Recorder(self.pb.id, language)" in src and "self.rec.stage_done(r, self.audit.events)" in src and "self.rec.finish(" in src
    assert "feedback.record_gate(" in src and "self.client" in src.split("feedback.record_gate(")[1][:200]
