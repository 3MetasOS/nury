"""The Observability page and its data: numbers and labels only, never text or names; the smoke run is guarded.
Offline: no model call, no subprocess. Run: python3 -m pytest evaluations/tests -q"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
from app import evals_api  # noqa: E402

STATIC = ROOT / "code" / "app" / "static"
NAMES = ["Maria", "Carlos", "Jose", "Lopez", "Rosa", "Hernandez", "Garcia", "Martinez", "Aurora", "Denver"]
BAD_KEYS = {"text", "draft", "name", "names", "summary", "intake", "message", "prompt", "case", "case_id", "id"}


def _walk(x, path=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from _walk(v, path + "/" + str(k))
            yield ("key", k, path)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from _walk(v, path + f"[{i}]")
    else:
        yield ("val", x, path)


def _check_no_text(d, allow_long=("/source", "/smoke/note")):
    for kind, v, path in _walk(d):
        if kind == "key":
            assert v not in BAD_KEYS, f"key {v!r} at {path}: ops data carries no text or ids"
        elif isinstance(v, str):
            if any(path.endswith(a) for a in allow_long):
                continue
            assert len(v) <= 64, f"{path}: a long string ({len(v)} chars) is text, not a label"
            for n in NAMES:
                assert n.lower() not in v.lower(), f"{path} contains {n}"


def test_ops_data_has_numbers_and_labels_only():
    d = evals_api.ops()
    assert {"source", "headline", "latency_by_stage", "cost_series", "rejections_by_category", "jev_by_question", "provider_mix", "runs"} <= set(d)
    _check_no_text(d)
    assert len(d["runs"]) <= 50
    for r in d["runs"]:
        assert set(r) == {"t", "crisis", "stages", "attempts", "cost", "latency_s", "outcome"}


def test_stub_is_labelled_and_the_ledger_view_is_used_when_it_has_packages(monkeypatch):
    from app import ops_api
    monkeypatch.setattr(ops_api, "handle", lambda m, p: (200, "application/json", json.dumps({"source": "ledger", "headline": {"packages": 3}}).encode()))
    assert evals_api.ops()["source"] == "ledger"
    monkeypatch.setattr(ops_api, "handle", lambda m, p: (200, "application/json", json.dumps({"source": "ledger", "headline": {"packages": 0}}).encode()))
    assert "stub" in evals_api.ops()["source"]


def test_evals_summary_has_numbers_and_no_text():
    e = evals_api.evals()
    _check_no_text(e)
    assert e["sets"] and all(s["scenarios"] >= 1 for s in e["sets"])
    assert e["smoke"]["scenarios"] == 3 and e["smoke"]["estimate_usd"] > 0


class _FakeThread:
    def __init__(self, target=None, daemon=None):
        self.target = target

    def start(self):
        pass                         # never runs the worker: no subprocess, no live call


def _reset():
    evals_api.STATE.update({"running": False, "started": None, "progress": "", "result": None, "error": None})


def test_smoke_run_is_off_by_default(monkeypatch):
    _reset()
    monkeypatch.delenv("NURY_ALLOW_EVAL_RUN", raising=False)
    assert evals_api.start_smoke({"confirm": True, "estimate_usd": evals_api.evals()["smoke"]["estimate_usd"]})[0] == 403
    assert evals_api.evals()["smoke"]["enabled"] is False


def test_smoke_run_needs_the_shown_estimate_confirmed(monkeypatch):
    _reset()
    monkeypatch.setenv("NURY_ALLOW_EVAL_RUN", "1")
    monkeypatch.setattr(evals_api.threading, "Thread", _FakeThread)
    assert evals_api.start_smoke({})[0] == 400
    assert evals_api.start_smoke({"confirm": True})[0] == 400
    assert evals_api.start_smoke({"confirm": True, "estimate_usd": 0.01})[0] == 400
    assert evals_api.start_smoke({"confirm": "yes", "estimate_usd": evals_api.evals()["smoke"]["estimate_usd"]})[0] == 400


def test_smoke_run_never_runs_beside_another_live_job(monkeypatch):
    _reset()
    monkeypatch.setenv("NURY_ALLOW_EVAL_RUN", "1")
    monkeypatch.setattr(evals_api.threading, "Thread", _FakeThread)
    ok = {"confirm": True, "estimate_usd": evals_api.evals()["smoke"]["estimate_usd"]}
    monkeypatch.setattr(evals_api, "_other_live_job", lambda: True)
    assert evals_api.start_smoke(ok)[0] == 409
    monkeypatch.setattr(evals_api, "_other_live_job", lambda: False)
    assert evals_api.start_smoke(ok)[0] == 202
    assert evals_api.start_smoke(ok)[0] == 409, "a second start while one is running is refused"
    _reset()


def test_observability_page_is_in_the_shell_and_never_writes_html_from_data():
    s = (STATIC / "observability.html").read_text(encoding="utf-8")
    assert '<script src="/shell.js"></script>' in s and '<link rel="stylesheet" href="/shell.css">' in s and "<header" not in s
    assert 'data-nav="ops"' in s
    assert "innerHTML" not in s and "insertAdjacentHTML" not in s, "data goes in with textContent only"
    assert "No alerts, no retention policy, no per-church separation yet." in s
    shell = (STATIC / "shell.js").read_text(encoding="utf-8")
    assert 'href="/observability"' in shell and 'id="ops-link"' in shell


def test_the_ledger_module_and_this_module_do_not_share_a_name():
    """hack-jedi's app/ops_api.py serves the ledger view; app/evals_api.py holds the evaluation extras and the stub."""
    assert (ROOT / "code" / "app" / "ops_api.py").is_file() and (ROOT / "code" / "app" / "evals_api.py").is_file()
    assert not hasattr(sys.modules["app.evals_api"], "handle")
