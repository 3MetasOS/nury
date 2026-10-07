#!/usr/bin/env python3
"""Record one human review decision and rebuild the scorecard.

  python3 evaluations/record_review.py <playbook>:<scenario>:<question> <pass|fail> [note]

Writes results/human_review.json (detention) or results/<playbook>/human_review.json, then rebuilds
that playbook's scorecard.md and results.json. The review canvas sends the same key.
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import report  # noqa: E402


def main(key, verdict, note=""):
    if verdict not in ("pass", "fail"):
        sys.exit("verdict must be pass or fail")
    playbook = key.split(":")[0]
    d = HERE / "results" if playbook == "detention" else HERE / "results" / playbook
    f = d / "human_review.json"
    data = json.loads(f.read_text()) if f.exists() else {}
    data[key] = {"verdict": verdict, "note": note}
    f.write_text(json.dumps(data, indent=1, ensure_ascii=False))
    report.build(d / "runs.json", d)
    print(f"recorded {key} = {verdict}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
