"""Build scorecard.md and results.json from runs.json."""
import json
from collections import defaultdict
from pathlib import Path

CATS = ["safety", "language", "role", "workflow", "adversarial", "network"]


def build(runs_path, out_dir):
    d = json.loads(Path(runs_path).read_text())
    runs = d["runs"]
    pbid = d.get("playbook", "detention")
    hrf = Path(runs_path).parent / "human_review.json"
    hr = json.loads(hrf.read_text()) if hrf.exists() else {}
    for r in runs:
        r["final"] = r["status"]
        if r["status"] == "review":
            keys = [f"{pbid}:{r['id']}:{j['name']}" for j in r["jev"] if j["verdict"] == "review"]
            got = [hr.get(k) for k in keys]
            if keys and all(got):
                r["final"] = "human_fail" if any(g["verdict"] == "fail" for g in got) else "human_pass"
                r["human"] = [{"question": k.split(":")[-1], **g} for k, g in zip(keys, got)]
            else:
                r["final"] = "awaiting"
        elif r["status"] == "error":
            r["final"] = "fail"
    by = defaultdict(list)
    for r in runs:
        by[r["category"]].append(r)
    n = len(runs) or 1
    passed = sum(r["status"] == "pass" for r in runs)
    m = [r["metrics"] for r in runs]
    agg = {
        "agent": d["agent"], "jev_used": d["jev"], "scenarios": len(runs),
        "judge_pass": sum(r["final"] == "pass" for r in runs),
        "human_pass": sum(r["final"] == "human_pass" for r in runs),
        "fail_by_judges": sum(r["final"] == "fail" for r in runs),
        "fail_by_human": sum(r["final"] == "human_fail" for r in runs),
        "awaiting_human_review": sum(r["final"] == "awaiting" for r in runs),
        "by_category": {c: {k: sum(r["final"] == f for r in by[c]) for k, f in
                            (("judge_pass", "pass"), ("human_pass", "human_pass"), ("fail", "fail"),
                             ("human_fail", "human_fail"), ("awaiting", "awaiting"))} for c in CATS if by[c]},
        "mean_corrections": round(sum(x["corrections"] for x in m) / n, 2),
        "total_retries": sum(x["retries"] for x in m),
        "escalations": sum(x["escalated"] for x in m),
        "mean_latency_s": round(sum(x["latency_s"] for x in m) / n, 2),
        "tokens_in": sum(x["tokens_in"] for x in m), "tokens_out": sum(x["tokens_out"] for x in m),
        "total_cost_usd": (None if any(x["cost_usd"] is None for x in m) else round(sum(x["cost_usd"] for x in m), 4)),
        "mean_cost_usd": (None if any(x["cost_usd"] is None for x in m) else round(sum(x["cost_usd"] for x in m) / n, 5)),
    }
    slim = [{k: v for k, v in r.items() if k != "trajectory"} for r in runs]
    out = Path(out_dir)
    (out / "results.json").write_text(json.dumps({"aggregate": agg, "runs": slim}, indent=1, ensure_ascii=False))
    L = (["MOCK SELF-TEST, NOT A RESULT", ""] if d["agent"] == "mock" else []) + [f"# Nury Evaluation Scorecard: {d.get('playbook', 'detention')} playbook", "",
         f"Agent: `{agg['agent']}`. Jev judges: {'on' if agg['jev_used'] else 'off (deterministic only)'}.",
         (f"Privacy layer: {'on' if d.get('privacy') else 'off'} (names, phones, emails, addresses, dates and ID numbers are replaced by tokens before anything reaches the model)." if d.get("privacy") is not None else "Privacy layer: not recorded."),
         (f"Model: `{d['pricing']['model']}`. Price: ${d['pricing']['usd_per_1m_in']} per 1M input tokens, ${d['pricing']['usd_per_1m_out']} per 1M output tokens (Gloo /platform/v2/models). Cache pricing not used." if d.get("pricing") and d["pricing"].get("usd_per_1m_in") else "Model and price: not recorded."), "",
         "## Summary", "",
         f"- Scenarios run: {agg['scenarios']}. Passed by the judges: {agg['judge_pass']}. Passed after human review: {agg['human_pass']}. "
         f"Failed: {agg['fail_by_judges'] + agg['fail_by_human']} ({agg['fail_by_judges']} by judges, {agg['fail_by_human']} by human review). "
         f"Sent to human review and still waiting: {agg['awaiting_human_review']}.",
         (f"- Passed in total after review: {agg['judge_pass'] + agg['human_pass']} of {agg['scenarios']}." if agg['awaiting_human_review'] == 0 else "- No total is quoted until every review item is decided."),
         f"- Corrections per run (mean): {agg['mean_corrections']}. Retries: {agg['total_retries']}. Escalations: {agg['escalations']}.",
         f"- Latency per run (mean): {agg['mean_latency_s']} s. Tokens: {agg['tokens_in']} in / {agg['tokens_out']} out. Cost: {('$%s total, $%s per run' % (agg['total_cost_usd'], agg['mean_cost_usd'])) if agg['total_cost_usd'] is not None else 'not measured (token rates not set)'}.", "",
         "## By category", "", "| Category | Runs | Judge pass | Human pass | Fail | Awaiting review |", "|---|---|---|---|---|---|"]
    for c, v in agg["by_category"].items():
        L.append(f"| {c} | {len(by[c])} | {v['judge_pass']} | {v['human_pass']} | {v['fail'] + v['human_fail']} | {v['awaiting']} |")
    L += ["", "## Per scenario", "", "| # | Scenario | Category | Result | Corrections | Retries | Escalated | Latency s | Tokens | Cost $ |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in runs:
        x = r["metrics"]
        L.append(f"| {r['number']} | {r['id']} | {r['category']} | {r['final']} | {x['corrections']} | {x['retries']} | {'yes' if x['escalated'] else 'no'} | {x['latency_s']} | {x['tokens_in']+x['tokens_out']} | {x['cost_usd']} |")
    L += ["", "## Failures and review items", ""]
    bad = [r for r in runs if r["final"] not in ("pass", "human_pass")]
    if not bad:
        L.append("None.")
    for r in bad:
        L.append(f"### {r['number']} {r['id']} ({r['final']})")
        for h in r.get("human", []):
            L.append(f"- Human review `{h['question']}`: {h['verdict']}" + (f". Note: {h['note']}" if h.get("note") else ""))
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
