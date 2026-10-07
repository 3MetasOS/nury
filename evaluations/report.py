"""Build scorecard.md and results.json from runs.json."""
import json
from collections import defaultdict
from pathlib import Path

CATS = ["safety", "language", "role", "workflow", "adversarial", "network", "privacy"]


def gate_lines(runs, jev_used):
    """Run-time Jev gate and Scripture, counted from the stored trajectories. Empty when the run did not carry the fields."""
    stages = [st for r in runs for st in (r.get("trajectory") or {}).get("stages", [])]
    if not any("jev_calls" in st for st in stages):
        return []
    calls = sum(st.get("jev_calls", 0) for st in stages)
    ms = sum(st.get("jev_ms", 0) for st in stages)
    rejects, esc = {}, []
    regen = 0
    for r in runs:
        for st in (r.get("trajectory") or {}).get("stages", []):
            for a in st.get("attempts", []):
                cats = [v for v in a.get("violations", []) if str(v).startswith("jev_")]
                if cats:
                    regen += 1
                    for v in cats:
                        q = str(v).split(":")[0]
                        rejects[q] = rejects.get(q, 0) + 1
            if st.get("escalated") and any(str(v).startswith("jev_") for a in st.get("attempts", [])[-1:] for v in a.get("violations", [])):
                esc.append(f"{r.get('id')} stage {st.get('n')}")
    prov = {}
    for r in runs:
        for e in (r.get("trajectory") or {}).get("scripture", []):
            prov[e.get("provider")] = prov.get(e.get("provider"), 0) + 1
    fb = sum(len((r.get("trajectory") or {}).get("scripture_fallbacks", [])) for r in runs)
    out = [f"Run-time Jev gate: {calls} Jev calls, {round(ms / 1000, 1)} s of Jev time in all. Drafts rejected by a Jev question: {regen}"
           + (f" ({', '.join(f'{q} {n}' for q, n in sorted(rejects.items()))})" if rejects else "") + ". "
           + ("Escalations caused by a Jev question: " + ", ".join(esc) + "." if esc else "No escalation was caused by a Jev question."),
           "Scripture: " + (", ".join(f"{n} from {p}" for p, n in sorted(prov.items(), key=lambda x: str(x[0]))) if prov else "no verse block recorded")
           + f". Provider fallbacks logged: {fb}.",
           "Independence: the Jev judges that score a run are no longer independent of the run-time gate, because Jev also classifies each draft while it is written. "
           "The deterministic judges, the red team of three other makers and human review stay independent of it."]
    tbl = {}
    for st in stages:
        for g in st.get("jev_gate", []):
            q = g.get("question")
            if not q or q == "*":
                continue
            e = tbl.setdefault(q, {"pass": 0, "uncertain": 0, "reject": 0, "unavailable": 0, "p": []})
            e[g.get("decision") if g.get("decision") in e else "unavailable"] += 1
            if isinstance(g.get("probability"), (int, float)):
                e["p"].append(g["probability"])
    rows = []
    if tbl:
        rows = ["", "Jev gate decisions by question (every draft checked, including regenerations):", "",
                "| Question | pass | uncertain | reject | unavailable | probability range |", "|---|---|---|---|---|---|"]
        for q, e in sorted(tbl.items()):
            pr = f"{min(e['p']):.2f} to {max(e['p']):.2f}" if e["p"] else "n/a"
            rows.append(f"| `{q}` | {e['pass']} | {e['uncertain']} | {e['reject']} | {e['unavailable']} | {pr} |")
        rows.append("")
    note = Path(__file__).parent / "scorecard_final_note.md"
    extra = ["- " + l for l in note.read_text(encoding="utf-8").splitlines() if l.strip()] if note.is_file() else []
    return ["- " + x for x in out] + extra + rows + [""]


def build(runs_path, out_dir):
    d = json.loads(Path(runs_path).read_text())
    runs = d["runs"]
    pbid = d.get("playbook", "detention")
    hrf = Path(runs_path).parent / "human_review.json"
    hr = json.loads(hrf.read_text()) if hrf.exists() else {}
    rtf = Path(runs_path).parent / "redteam.json"
    rt = json.loads(rtf.read_text()) if rtf.exists() else None
    panel = {x["id"]: x for x in (rt or {}).get("results", [])}
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
        pe = panel.get(r["id"])
        if pe:
            r["panel"] = {"corroborated": pe.get("corroborated", []), "needs_human": pe.get("needs_human", False),
                          "findings": {x["model"]: len(x["findings"]) for x in pe["reviewers"]},
                          "errors": [x["model"] for x in pe["reviewers"] if x["error"]]}
            # A corroborated panel finding does NOT change the scenario's status: nearly every scenario has one, and the panel
            # reviewers are advisory (validation/PANEL_VALIDATION.md). Findings go to the human canvas and to the column below.
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
         (lambda h: f"Build id (repo head when this scorecard was built): `{h}`." if h else "Build id: not available.")(__import__("subprocess").run(["git", "rev-parse", "--short", "HEAD"], cwd=Path(__file__).resolve().parent.parent, capture_output=True, text=True).stdout.strip()),
         (lambda c: (f"Core (code/nury and code/playbooks): last commit `{c['start']['core_last_commit']}`"
                     + (", uncommitted changes at start" if c["start"]["core_dirty"] else ", clean at start")
                     + ("; CHANGED during the run" if c["start"]["core_last_commit"] != c["end"]["core_last_commit"] else "; unchanged during the run")
                     + f". Repo head at start `{c['start']['repo_head']}`.") if c else "Core commit: not recorded.")(d.get("core")),
         (f"Privacy layer: {'on' if d.get('privacy') else 'off'} (names, phones, emails, addresses, dates and ID numbers are replaced by tokens before anything reaches the model)." if d.get("privacy") is not None else "Privacy layer: not recorded."),
         (f"Model: `{d['pricing']['model']}`. Price: ${d['pricing']['usd_per_1m_in']} per 1M input tokens, ${d['pricing']['usd_per_1m_out']} per 1M output tokens (Gloo /platform/v2/models). Cache pricing not used." if d.get("pricing") and d["pricing"].get("usd_per_1m_in") else "Model and price: not recorded."), "",
         *gate_lines(runs, d.get("jev_used")),
         "## Summary", "",
         f"- Scenarios run: {agg['scenarios']}. Passed by the judges: {agg['judge_pass']}. Passed after human review: {agg['human_pass']}. "
         f"Failed: {agg['fail_by_judges'] + agg['fail_by_human']} ({agg['fail_by_judges']} by judges, {agg['fail_by_human']} by human review). "
         f"Sent to human review and still waiting: {agg['awaiting_human_review']}.",
         (f"- Passed in total after review: {agg['judge_pass'] + agg['human_pass']} of {agg['scenarios']}." if agg['awaiting_human_review'] == 0 else "- No total is quoted until every review item is decided."),
         f"- Corrections per run (mean): {agg['mean_corrections']}. Retries: {agg['total_retries']}. Escalations: {agg['escalations']}.",
         f"- Latency per run (mean): {agg['mean_latency_s']} s. Tokens: {agg['tokens_in']} in / {agg['tokens_out']} out. Cost: {('$%s total, $%s per run' % (agg['total_cost_usd'], agg['mean_cost_usd'])) if agg['total_cost_usd'] is not None else 'not measured (token rates not set)'}.", "",
         *(["## Red-team panel (pre-release audit on build 00fe7b1, not re-run on the final build)", "",
            f"- Reviewers (not Claude, same Gloo endpoint): {', '.join('`'+m+'`' for m in rt['reviewers'])}. Prompt `{rt['version']}`. Prices per 1M tokens in/out: " + "; ".join(f"{m.split('gloo-')[1]} ${p['in']}/${p['out']}" for m, p in rt.get('prices_usd_per_1m', {}).items()) + f". Cost of this panel run: ${rt.get('total_cost_usd')}.",
            f"- Scenarios with a corroborated finding (two reviewers quoted the same sentence): {sum(1 for x in rt['results'] if x['corroborated'])} of {len(rt['results'])}. Sent to the human canvas: {sum(1 for x in rt['results'] if x['needs_human'])}.",
            "- All reviewers are advisory (see `validation/PANEL_VALIDATION.md`): they catch injected problems but also flag safe text. Panel findings never change a scenario's result. Corroborated ones are in the review canvas group `red_team_corroborated` and summarized in `results/panel_digest.md`. Unanimous none would be extra evidence, not a pass.", ""] if rt else []),
         "## By category", "", "| Category | Runs | Judge pass | Human pass | Fail | Awaiting review |", "|---|---|---|---|---|---|"]
    for c, v in agg["by_category"].items():
        L.append(f"| {c} | {len(by[c])} | {v['judge_pass']} | {v['human_pass']} | {v['fail'] + v['human_fail']} | {v['awaiting']} |")
    L += ["", "## Per scenario", "", "| # | Scenario | Category | Result | Red-team panel | Corrections | Retries | Escalated | Latency s | Tokens | Cost $ |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in runs:
        x = r["metrics"]
        pn = r.get("panel")
        pcell = "-" if not pn else (f"{len(pn['corroborated'])} corroborated" + (" (to human)" if pn["needs_human"] else "") + "; findings " + "/".join(str(v) for v in pn["findings"].values()))
        L.append(f"| {r['number']} | {r['id']} | {r['category']} | {r['final']} | {pcell} | {x['corrections']} | {x['retries']} | {'yes' if x['escalated'] else 'no'} | {x['latency_s']} | {x['tokens_in']+x['tokens_out']} | {x['cost_usd']} |")
    notes = Path(__file__).parent / "scorecard_notes.md"
    if notes.exists():
        L += ["", "## Notes on the build", "", notes.read_text().strip(), ""]
    cmpf = Path(__file__).parent / "results" / "build_comparison.md"
    if cmpf.exists() and Path(out_dir).resolve() == (Path(__file__).parent / "results").resolve():
        L += ["", cmpf.read_text(encoding="utf-8").replace("# Build comparison", "## Build comparison", 1), ""]
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
            hk = hr.get(f"{pbid}:{r['id']}:{j['name']}_below_3") if j["verdict"] == "fail" else None
            if hk:   # a person read the message; this is a record and does not change the judge's result
                L.append(f"- Human reading of the {j['name']} fail: {hk['verdict']}" + (f". Note: {hk['note']}" if hk.get("note") else ""))
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
    L += ["", "The Jev decision API from TypeSafe is used as typed judges in our evaluation harness and as a run-time draft classifier; disclosed as third-party technology per the rules."]
    (out / "scorecard.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    import sys
    build(sys.argv[1], Path(sys.argv[1]).parent)
