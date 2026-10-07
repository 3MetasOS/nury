#!/usr/bin/env python3
"""Re-run the Jev judges on stored trajectories. No Gloo calls, no agent cost.
Use it to re-check verdict stability or to apply a changed question. Needs JEV_API_KEY.

  python3 evaluations/rejudge.py evaluations/results/runs.json
"""
import json, sys
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from judges import jev_judges  # noqa: E402
import report  # noqa: E402
from run import status_of  # noqa: E402


def main(path):
    path = Path(path)
    d = json.loads(path.read_text())
    scs = {}
    for f in (HERE / "scenarios").glob("*.yaml"):
        sc = yaml.safe_load(f.read_text())
        scs[sc["id"]] = sc
    for r in d["runs"]:
        try:
            r["jev"], r["jev_error"] = jev_judges.judge(r["trajectory"], scs[r["id"]]), None
        except Exception as e:
            r["jev"], r["jev_error"] = [], str(e)
        r["status"] = status_of(r["deterministic"], r["jev"], r["jev_error"], r["error"])
        print(f"{r['number']:02d} {r['id']:<24} {r['status']}")
    d["jev"] = True
    path.write_text(json.dumps(d, indent=1, ensure_ascii=False, default=str))
    report.build(path, path.parent)


if __name__ == "__main__":
    main(sys.argv[1])
