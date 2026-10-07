#!/usr/bin/env python3
"""Run scenarios against an agent, judge them, write results.

  python3 evaluations/run.py --agent mock                 # harness self-test
  python3 evaluations/run.py --agent nury                 # real agent (needs adapter_nury.run)
  python3 evaluations/run.py --agent nury --jev           # add Jev judges (needs JEV_API_KEY)
  python3 evaluations/run.py --only 05,06                 # subset by number or id

Agent adapter contract: run(scenario: dict) -> trajectory dict. See README.md.
"""
import argparse, glob, importlib, json, sys, time
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from judges import deterministic  # noqa: E402


def load_scenarios(only=None, playbook=None):
    out = []
    for p in sorted(glob.glob(str(HERE / "scenarios" / "*.yaml"))):
        sc = yaml.safe_load(open(p))
        if playbook and sc.get('playbook', 'detention') != playbook:
            continue
        if only and sc["id"] not in only and f"{sc['number']:02d}" not in only:
            continue
        out.append(sc)
    return out


def get_agent(name):
    mod = {"mock": "mock_agent", "nury": "adapter_nury"}.get(name, name)
    return importlib.import_module(mod).run


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", default="mock")
    ap.add_argument("--jev", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--playbook", default="detention")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.out is None:  # mock output never lands in results/
        a.out = str(HERE / ("results" if a.agent != "mock" else "selftest-mock"))
    only = set(filter(None, a.only.split(",")))
    run_agent = get_agent(a.agent)
    if a.jev:
        from judges import jev_judges
    runs = []
    for sc in load_scenarios(only, a.playbook):
        t0 = time.time()
        try:
            traj = run_agent(sc)
            err = None
        except Exception as e:  # a crashed run is a failed run, logged
            traj, err = {"scenario_id": sc["id"], "stages": [], "audit_log": []}, f"{type(e).__name__}: {e}"
        traj.setdefault("latency_s", time.time() - t0)
        det = deterministic.judge(traj, sc) if not err else []
        jev, jev_err = [], None
        if a.jev and not err:
            try:
                jev = jev_judges.judge(traj, sc)
            except Exception as e:
                jev_err = str(e)
        det_ok = bool(det) and all(r["passed"] for r in det)
        jev_fail = [r["name"] for r in jev if r["verdict"] == "fail"]
        jev_rev = [r["name"] for r in jev if r["verdict"] == "review"]
        status = "error" if err else ("fail" if (not det_ok or jev_fail) else ("review" if jev_rev or jev_err else "pass"))
        runs.append({"id": sc["id"], "number": sc["number"], "category": sc["category"], "title": sc["title"],
                     "status": status, "error": err, "deterministic": det, "jev": jev, "jev_error": jev_err,
                     "metrics": metrics(traj), "trajectory": traj})
        print(f"{sc['number']:02d} {sc['id']:<24} {status}")
    Path(a.out).mkdir(parents=True, exist_ok=True)
    (Path(a.out) / "runs.json").write_text(json.dumps({"agent": a.agent, "jev": a.jev, "pricing": getattr(sys.modules.get("adapter_nury"), "PRICES", None), "runs": runs}, indent=1, ensure_ascii=False, default=str))
    audit_dir = Path(a.out) / "audit"
    audit_dir.mkdir(exist_ok=True)
    for r in runs:  # one audit log per run, committed as evidence
        (audit_dir / f"{r['number']:02d}-{r['id']}.json").write_text(json.dumps(r["trajectory"].get("audit_log", []), indent=1, default=str))
    import report
    report.build(Path(a.out) / "runs.json", Path(a.out))


def metrics(traj):
    st = traj.get("stages", [])
    return {
        "corrections": sum(1 for s in st if len(s.get("attempts", [])) > 1 and not s.get("escalated")),
        "retries": sum(s.get("retries", 0) for s in st),
        "escalated": bool(traj.get("escalated")),
        "latency_s": round(traj.get("latency_s", 0), 2),
        "tokens_in": sum(s.get("tokens_in", 0) for s in st),
        "tokens_out": sum(s.get("tokens_out", 0) for s in st),
        "cost_usd": (None if any(s.get("cost_usd") is None for s in st) else round(sum(s["cost_usd"] for s in st), 5)),
    }


if __name__ == "__main__":
    main()
