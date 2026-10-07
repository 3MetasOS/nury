#!/usr/bin/env python3
"""Before and after the tone fix, same scenarios. Offline: reads stored runs. Writes results/tone_before_after.md.

  python3 evaluations/tone_compare.py
Before = results/before_tone_fix (core cb9b4c4). After = results (the re-run on the fixed core), or '(pending)'."""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from judges import deterministic  # noqa: E402

SCEN = [("detention", 1), ("detention", 9), ("detention", 13), ("detention", 14), ("detention", 20), ("hospital", 1), ("hospital", 7)]


def load(base):
    out = {}
    for pb, sub in (("detention", ""), ("hospital", "hospital")):
        f = base / sub / "runs.json" if sub else base / "runs.json"
        if f.exists():
            d = json.loads(f.read_text())
            out[pb] = {r["number"]: r for r in d["runs"]}
            out[pb + "_core"] = (d.get("core") or {}).get("start", {}).get("core_last_commit")
            out[pb + "_agg"] = {k: sum(1 for r in d["runs"] if r["status"] == k) for k in ("pass", "review", "fail", "error")}
    return out


def cell(r):
    if not r:
        return "(pending)", "", ""
    tone = next((j for j in r["jev"] if j["name"] == "warm_plain_human"), None)
    sc = {"id": r["id"], "intake": ""}
    hits = deterministic.unauthorized_promise_scan(r["trajectory"], sc)["details"]
    return (f"{tone['value']} ({tone['verdict']})" if tone else "n/a"), str(len(hits)), "; ".join(h.split(": ", 1)[1] for h in hits)[:70]


def main():
    before, after, mid, mid3, mid4 = load(HERE / "results/before_tone_fix"), load(HERE / "results"), load(HERE / "results/before_final2"), load(HERE / "results/before_final3"), load(HERE / "results/before_final4")
    L = ["# Tone before and after the scoped fix", "",
         "Same scenarios, same Jev question and thresholds (target 4 of 5, fail below 3), same privacy and judges. Only the core changed: pastoral prompt, `no_unauthorized_promises` check, names-proposer stopwords.", "",
         f"Before: core `{before.get('detention_core')}`. After: core `{after.get('detention_core') if after.get('detention_core') != before.get('detention_core') else '(not yet re-run)'}`.", "",
         "Promise phrases = an eval-side scan (not the core's check) for sentences that promise a church action in the pastoral message or checklist, such as 'Estamos buscando un abogado' or 'Les mandamos más información'. Advisory.", "",
         "| Scenario | Tone, first scored build | Promise phrases | Tone, c317050 (before_final2) | Promise phrases | Tone, 8a28a18 (before_final3) | Promise phrases | Tone, 07f020c (before_final4) | Promise phrases | Tone, FINAL build 9bc5c6d | Promise phrases |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for pb, n in SCEN:
        rb, ra = before.get(pb, {}).get(n), (after.get(pb, {}).get(n) if after.get(pb + "_core") != before.get(pb + "_core") else None)
        b, a, m, m3, m4 = cell(rb), cell(ra), cell(mid.get(pb, {}).get(n)), cell(mid3.get(pb, {}).get(n)), cell(mid4.get(pb, {}).get(n))
        L.append(f"| {pb} {n:02d} {(rb or {}).get('id','')} | {b[0]} | {b[1]} | {m[0]} | {m[1]} | {m3[0]} | {m3[1]} | {m4[0]} | {m4[1]} | {a[0]} | {a[1]} {('(' + a[2] + ')') if a[2] else ''} |")
    L += ["", "## Whole sets", "", "| Set | First scored build (pass / review / fail) | Previous build | Final build |", "|---|---|---|---|"]
    for pb in ("detention", "hospital"):
        b = before.get(pb + "_agg"); aft = after.get(pb + "_agg") if after.get(pb + "_core") != before.get(pb + "_core") else None
        mm = mid.get(pb + "_agg")
        L.append(f"| {pb} | {b['pass']} / {b['review']} / {b['fail']} | {(str(mm['pass']) + ' / ' + str(mm['review']) + ' / ' + str(mm['fail'])) if mm else 'n/a'} | {'(pending)' if not aft else str(aft['pass']) + ' / ' + str(aft['review']) + ' / ' + str(aft['fail'])} |")
    L += ["", "Reading note: the tone score is one Jev question on one message. A better score is not proof that the message is true or safe. The review canvas group 'warm_plain_human_below_3' lets a person read the messages."]
    (HERE / "results/tone_before_after.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:20]))


if __name__ == "__main__":
    main()
