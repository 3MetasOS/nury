"""Build scorecard.md and results.json from runs.json."""
import json
from collections import defaultdict
from pathlib import Path

CATS = ["safety", "language", "role", "workflow", "adversarial"]


def build(runs_path, out_dir):
    d = json.loads(Path(runs_path).read_text())
    runs = d["runs"]
    by = defaultdict(list)
    for r in runs:
        by[r["category"]].append(r)
    n = len(runs) or 1
    passed = sum(r["status"] == "pass" for r in runs)
    m = [r["metrics"] for r in runs]
    agg = {
        "agent": d["agent"], "jev_used": d["jev"], "scenarios": len(runs),
        "pass": passed, "fail": sum(r["status"] in ("fail", "error") for r in runs),
        "human_review": sum(r["status"] == "review" for r in runs),
        "pass_rate": round(passed / n, 3),
        "pass_rate_by_category": {c: round(sum(r["status"] == "pass" for r in by[c]) / len(by[c]), 3) for c in CATS if by[c]},
        "mean_corrections": round(sum(x["corrections"] for x in m) / n, 2),
        "total_retries": sum(x["retries"] for x in m),
        "escalations": sum(x["escalated"] for x in m),
        "mean_latency_s": round(sum(x["latency_s"] for x in m) / n, 2),
        "tokens_in": sum(x["tokens_in"] for x in m), "tokens_out": sum(x["tokens_out"] for x in m),
        "total_cost_usd": round(sum(x["cost_usd"] for x in m), 4),
    }
    slim = [{k: v for k, v in r.items() if k != "trajectory"} for r in runs]
    out = Path(out_dir)
    (out / "results.json").write_text(json.dumps({"aggregate": agg, "runs": slim}, indent=1, ensure_ascii=False))
    L = (["MOCK SELF-TEST, NOT A RESULT", ""] if d["agent"] == "mock" else []) + ["# Nury Evaluation Scorecard", "",
         f"Agent: `{agg['agent']}`. Jev judges: {'on' if agg['jev_used'] else 'off (deterministic only)'}.", "",
         "## Summary", "",
         f"- Pass rate: **{agg['pass']}/{agg['scenarios']} ({agg['pass_rate']:.0%})**. Fail: {agg['fail']}. Human review: {agg['human_review']}.",
         f"- Corrections per run (mean): {agg['mean_corrections']}. Retries: {agg['total_retries']}. Escalations: {agg['escalations']}.",
         f"- Latency per run (mean): {agg['mean_latency_s']} s. Tokens: {agg['tokens_in']} in / {agg['tokens_out']} out. Cost: ${agg['total_cost_usd']}.", "",
         "## Pass rate by category", "", "| Category | Pass rate | Runs |", "|---|---|---|"]
    for c, v in agg["pass_rate_by_category"].items():
        L.append(f"| {c} | {v:.0%} | {len(by[c])} |")
    L += ["", "## Per scenario", "", "| # | Scenario | Category | Result | Corrections | Retries | Escalated | Latency s | Tokens | Cost $ |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in runs:
        x = r["metrics"]
        L.append(f"| {r['number']} | {r['id']} | {r['category']} | {r['status']} | {x['corrections']} | {x['retries']} | {'yes' if x['escalated'] else 'no'} | {x['latency_s']} | {x['tokens_in']+x['tokens_out']} | {x['cost_usd']} |")
    L += ["", "## Failures and review items", ""]
    bad = [r for r in runs if r["status"] != "pass"]
    if not bad:
        L.append("None.")
    for r in bad:
        L.append(f"### {r['number']} {r['id']} ({r['status']})")
        if r["error"]:
            L.append(f"- Run error: {r['error']}")
        for c in r["deterministic"]:
            if not c["passed"]:
                L.append(f"- `{c['name']}`: " + "; ".join(c["details"]))
        for j in r["jev"]:
            if j["verdict"] != "accept":
                L.append(f"- Jev `{j['name']}` ({j['kind']}) = {j['value']} -> {j['verdict']}")
        if r["jev_error"]:
            L.append(f"- Jev error: {r['jev_error']}")
        L.append("")
    L += ["## Failure-mode log (what broke -> what changed)", "",
          "Hand-maintained in `evaluations/FAILURE_LOG.md`. Add a row per failure after each fix.", ""]
    fl = Path(__file__).parent / "FAILURE_LOG.md"
    if fl.exists():
        L.append(fl.read_text())
    L += ["", "Evaluation harness uses the Jev decision API (my prior project) as typed judges; disclosed as prior technology per the rules."]
    (out / "scorecard.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    import sys
    build(sys.argv[1], Path(sys.argv[1]).parent)
