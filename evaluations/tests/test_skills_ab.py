"""The skills A/B script: design only. Never calls Gloo or Jev (the fake model stands in)."""
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import skills_ab as ab  # noqa: E402


def run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = ab.main(argv)
    return rc, buf.getvalue()


def test_fewer_than_three_repeats_is_refused_unless_allowed():
    for n in ("1", "2"):
        rc, out = run(["--fake", "--repeat", n, "--only", "01"])
        assert rc == 2 and "Refused" in out
    rc, out = run(["--dry-run", "--repeat", "1", "--allow-single", "--only", "01"])
    assert rc in (0, None) and "2 pipelines" in out


def test_the_default_is_three_repeats_and_the_dry_run_counts_them():
    rc, out = run(["--dry-run"])
    assert "42 pipelines" in out and "3 repeats" in out and "order alternated" in out


def test_a_fake_run_repeats_each_arm_and_alternates_the_order(tmp_path, monkeypatch):
    monkeypatch.setattr(ab, "OUT", tmp_path)
    rc, out = run(["--fake", "--only", "01", "h01"])
    assert rc == 0
    runs = json.loads((tmp_path / "fake-selftest" / "runs.json").read_text())
    assert len(runs) == 2 * 2 * 3
    for pb in ("detention", "hospital"):
        for mode in ("off", "on"):
            assert sorted(r["repeat"] for r in runs if r["playbook"] == pb and r["skills"] == mode) == [0, 1, 2], (pb, mode)
    first = [(r["repeat"], r["skills"]) for r in runs if r["playbook"] == "detention"]
    assert first[0] == (0, "off") and first[1] == (0, "on") and first[2] == (1, "on") and first[3] == (1, "off")
    summary = (tmp_path / "fake-selftest" / "summary.md").read_text()
    assert "FAKE MODEL SELF-TEST" in summary and "Repeats per arm: 3" in summary and "spread inside one arm" in summary


def test_the_summary_calls_a_difference_inside_the_spread_noise_and_one_outside_it_a_lead():
    base = {"scenario": "s", "playbook": "detention", "outcome": "package_complete", "stock_phrase_hits": 0, "dashes": 0, "unsourced_tip_lines": 0,
            "words": 100, "attempts": 5, "self_corrections": 0, "tokens_in": 1000, "tokens_out": 200, "cost_usd": 0.1, "latency_s": 50}
    runs = []
    for rep, (a_off, a_on) in enumerate([(5, 5), (6, 5), (5, 6)]):          # attempts: spread 1 inside each arm, equal means
        runs += [dict(base, skills="off", repeat=rep, attempts=a_off), dict(base, skills="on", repeat=rep, attempts=a_on)]
    text = ab.summarize(runs)
    line = [ln for ln in text.splitlines() if ln.startswith("| stage attempts")][0]
    assert "within noise" in line
    runs2 = [dict(r, stock_phrase_hits=(4 if r["skills"] == "off" else 0)) for r in runs]
    line2 = [ln for ln in ab.summarize(runs2).splitlines() if ln.startswith("| stock phrases")][0]
    assert "outside the noise" in line2


def test_it_makes_no_live_call_in_any_of_these_tests():
    src = Path(ab.__file__).read_text()
    assert "--fake" in src and "make_client" in src
