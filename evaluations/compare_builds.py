#!/usr/bin/env python3
"""Compare two builds of every scored set: c317050 (results/before_final2) against the current results. Offline: reads stored runs.
  python3 evaluations/compare_builds.py      -> results/build_comparison.md (report.py puts it in the main scorecard)
A column says which core commit it was run on. The network and case-file sets in before_final2 were last run on an earlier build, and the table says so."""
import glob
import json
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
SETS = [("Detention (20)", "runs.json"), ("Hospital (8)", "hospital/runs.json"), ("Attacker (18)", "attacker/runs.json"), ("Network (3)", "network/runs.json")]


def load(base, rel):
    f = base / rel
    if not f.exists():
        return None
    d = json.loads(f.read_text())
    runs = d["runs"]
    rf = f.with_name("results.json")           # the judged records (final, jev) live in results.json; the trajectories in runs.json
    judged = {r["id"]: r for r in json.loads(rf.read_text())["runs"]} if rf.exists() else {}
    for r in runs:
        r.update({k: v for k, v in judged.get(r["id"], {}).items() if k in ("final", "jev")})
    core = ((d.get("core") or {}).get("start") or {}).get("core_last_commit", "?").split()[0]
    pf = {"pass": 0, "fail": 0, "awaiting": 0}
    for r in runs:
        k = r["final"]
        pf["pass" if k in ("pass", "human_pass") else "awaiting" if k in ("awaiting", "review") else "fail"] += 1
    tone = [j["value"] for r in runs for j in r.get("jev", []) if j["name"] == "warm_plain_human" and isinstance(j.get("value"), (int, float))]
    cost = sum(sum((s.get("cost_usd") or 0) for s in r["trajectory"]["stages"]) for r in runs)
    lat = [r["trajectory"].get("latency_s") or 0 for r in runs]
    esc = sum(1 for r in runs if r["trajectory"].get("escalated"))
    return {"core": core, "n": len(runs), **pf, "esc": esc, "tone": (min(tone), max(tone)) if tone else None, "cost": cost, "lat": st.mean(lat) if lat else 0,
            "audit": base / (rel.rsplit("/", 1)[0] + "/audit" if "/" in rel else "audit")}


def reading(audit_dir):
    es, en = [], []
    for f in glob.glob(str(audit_dir) + "/*.json"):
        for e in json.loads(Path(f).read_text()):
            if e.get("kind") == "readability":
                (es if e.get("lang") == "es" else en).append(e.get("szigriszt") if e.get("lang") == "es" else e.get("fk_grade"))
    f = lambda xs: round(st.median([x for x in xs if x is not None]), 1) if xs else None
    return (f(es), len(es)), (f(en), len(en))


def cell(x, audit=False):
    if not x:
        return "not run"
    t = f"{x['tone'][0]:.2f} to {x['tone'][1]:.2f}" if x["tone"] else "n/a"
    r = ""
    if audit:
        (m_es, n_es), (m_en, n_en) = reading(x["audit"])
        r = ", ".join(x for x in ((f"ES INFLESZ {m_es} ({n_es})" if n_es else ""), (f"EN grade {m_en} ({n_en})" if n_en else "")) if x) or "not recorded"
    return [f"`{x['core']}`", f"{x['pass']} / {x['fail']} / {x['awaiting']}", str(x["esc"]), t, f"${x['cost']:.2f}", f"{x['lat']:.0f} s", r or "not recorded"]


def main():
    cur, old = HERE / "results", HERE / "results/before_final2"
    rows = ["# Build comparison: c317050 against the final build", "",
            "Pass / fail / awaiting review are judge results, not human verdicts. Tone range is the Jev warm, plain and human score (target 4, fail below 3). Reading level is advisory and was first recorded in the final build. A column names the core commit it ran on.", "",
            "| Set | Build | Core | Pass / fail / awaiting | Escalations | Tone range | Cost | Mean time per run | Reading level |", "|---|---|---|---|---|---|---|---|---|"]
    for name, rel in SETS:
        for label, base, audit in (("before", old, False), ("final", cur, True)):
            x = load(base, rel)
            c = cell(x, audit)
            rows.append(f"| {name} | {label} | " + (" | ".join(c) if isinstance(c, list) else f"{c} | | | | | | ") + " |")
    cf = []
    for label, base in (("before", old), ("final", cur)):
        f = base / "casefile.json"
        if f.exists():
            d = json.loads(f.read_text()); ok = sum(1 for c in d["checks"] if c["pass"])
            cf.append(f"| Case-file (5) | {label} | n/a | {ok} / {len(d['checks']) - ok} / 0 | n/a | n/a | ${d.get('cost_usd', 0):.2f} | n/a | n/a |")
    rows += cf
    rows += ["", "`b47cc92` is c317050 plus a change to rule descriptions only (disclosed in the scorecard note); the hospital and attacker rows marked before ran on it. The network and case-file rows marked before were last run on an earlier build than c317050 (see the Core column); only detention, hospital and attacker were re-run on c317050.", ""]
    (HERE / "results/build_comparison.md").write_text("\n".join(rows) + "\n")
    print("\n".join(rows[4:]))


if __name__ == "__main__":
    main()
