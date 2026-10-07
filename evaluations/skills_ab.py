"""Skills before/after: the same scenarios with the Nury skills OFF and ON. Live Gloo calls.

    python3 evaluations/skills_ab.py --dry-run          # plan and cost estimate, no calls
    python3 evaluations/skills_ab.py --fake             # script smoke test with a fake model, no calls
    python3 evaluations/skills_ab.py                    # live: 7 scenarios x 2 modes x 3 repeats = 42 pipelines, about $3

Each arm is repeated at least 3 times (--repeat; fewer is refused unless --allow-single) with the order of the arms alternated,
and the summary compares the difference between arms with the spread INSIDE an arm. Jev scores drifted by up to 0.12 between two
passes of the same drafts and the model varies too, so one pass per arm cannot show a small effect. This script has NOT been run live.

Writes evaluations/results/skills_ab/runs.json and summary.md. Privacy is ON for both modes (the final
configuration). Keys come from the environment. Nothing here prints them.
Measures (all deterministic, no judge): tokens, dollars, latency, attempts, self-corrections, stock-phrase
hits, em and en dashes, words, and the two checklist tips that no vetted point states.
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "code"))
sys.path.insert(0, str(HERE.parent / "code" / "tests"))
os.environ.setdefault("NURY_PRICE_IN", "3.00")
os.environ.setdefault("NURY_PRICE_OUT", "15.00")

from nury import checks as ck  # noqa: E402
from nury.engine import get_playbook, run_scripted  # noqa: E402
from nury.privacy import make_client  # noqa: E402

SCENARIOS = ["01", "09", "13", "14", "20", "h01", "h07"]
OUT = HERE / "results" / "skills_ab"
TIPS = re.compile(r"memori[cz]e|memorice|copias|copies|redes sociales|social media", re.I)
SKILL_STAGES = ("attorney", "resources", "checklist", "pastoral")
_NS = type("N", (), {})()


def load(sid):
    import glob
    p = glob.glob(str(HERE / "scenarios" / f"{sid}-*.yaml"))[0]
    return yaml.safe_load(open(p))


def decisions(sc, ids):
    out = {}
    for k, act in (sc.get("pastor_actions") or {}).items():
        sid = ids[int(k) - 1]
        if isinstance(act, dict) and "edit" in act:
            out[sid] = ("edit", act["edit"])
        elif act in ("reject", "stop"):
            out[sid] = "stop"
    return out


def text_metrics(st):
    texts = {k: v for k, v in st.approved.items() if k in SKILL_STAGES}
    blob = "\n".join(texts.values())
    stock = ck.no_stock_phrases({}, blob, _NS)
    return {"words": len(blob.split()), "stock_phrase_hits": len(stock),
            "dashes": blob.count("—") + blob.count("–"),
            "unsourced_tip_lines": sum(1 for l in texts.get("checklist", "").splitlines() if TIPS.search(l))}


def run_one(sc, skills, fake):
    pb = get_playbook(sc.get("playbook", "detention"))
    ids = [s.id for s in pb.stages]
    if fake:
        from test_core import CANNED, HCANNED, FakeClient, HFake
        client = HFake(HCANNED) if pb.id == "hospital" else FakeClient(CANNED)
    else:
        client = make_client(intake=sc["intake"])
        client.allow_playbook(pb)
    t0 = time.time()
    st, rs, au = run_scripted(sc["intake"], sc.get("output_language", "es"), decisions(sc, ids), client=client,
                              playbook=pb.id, skills=skills)
    tin = sum(r.metrics["input_tokens"] for r in rs)
    tout = sum(r.metrics["output_tokens"] for r in rs)
    cost = round((tin * float(os.environ["NURY_PRICE_IN"]) + tout * float(os.environ["NURY_PRICE_OUT"])) / 1e6, 4)
    return {"scenario": sc["id"], "playbook": pb.id, "skills": "on" if skills else "off", "outcome": st.outcome["outcome"],
            "stages": [{"id": r.stage_id, "status": r.status, "attempts": r.metrics["attempts"], "categories": r.reason_categories} for r in rs],
            "attempts": sum(r.metrics["attempts"] for r in rs), "self_corrections": sum(r.metrics["self_corrections"] for r in rs),
            "tokens_in": tin, "tokens_out": tout, "cost_usd": cost, "latency_s": round(time.time() - t0, 1),
            "skill_events": len(au.of_kind("skill_applied")), **text_metrics(st)}


METRICS = [("stock_phrase_hits", "stock phrases"), ("dashes", "dashes"), ("unsourced_tip_lines", "unsourced tip lines"), ("words", "words"),
           ("attempts", "stage attempts"), ("self_corrections", "self-corrections"), ("tokens_in", "tokens in"), ("tokens_out", "tokens out"),
           ("cost_usd", "cost $"), ("latency_s", "seconds")]


def _mean(v):
    return sum(v) / len(v) if v else 0.0


def summarize(runs):
    """Per metric: the mean with skills off and on, the difference, and the spread INSIDE an arm (max minus min across repeats of
    the same scenario, averaged). A difference no larger than that spread is within noise and is not evidence."""
    scen = sorted({r["scenario"] for r in runs})
    reps = max((r.get("repeat", 0) for r in runs), default=0) + 1
    rows = ["| metric | skills off | skills on | on minus off | spread inside one arm | reading |", "|---|---|---|---|---|---|"]
    for key, label in METRICS:
        off_m, on_m, spreads = [], [], []
        for sc in scen:
            o = [r[key] for r in runs if r["scenario"] == sc and r["skills"] == "off"]
            n = [r[key] for r in runs if r["scenario"] == sc and r["skills"] == "on"]
            if o and n:
                off_m.append(_mean(o))
                on_m.append(_mean(n))
                spreads += [max(o) - min(o), max(n) - min(n)]
        d, sp = _mean(on_m) - _mean(off_m), _mean(spreads)
        reading = "within noise" if abs(d) <= sp + 1e-9 else "outside the noise: read the drafts before believing it"
        rows.append(f"| {label} | {round(_mean(off_m), 3)} | {round(_mean(on_m), 3)} | {round(d, 3)} | {round(sp, 3)} | {reading} |")
    incomplete = {m: sum(1 for r in runs if r["skills"] == m and r["outcome"] != "package_complete") for m in ("off", "on")}
    total = {m: sum(r["cost_usd"] for r in runs if r["skills"] == m) for m in ("off", "on")}
    head = (f"Scenarios: {len(scen)}. Repeats per arm: {reps}. Pipelines: {len(runs)}. "
            f"Not complete: off {incomplete['off']}, on {incomplete['on']}. Total cost: off ${round(total['off'], 3)}, on ${round(total['on'], 3)}.\n\n")
    return head + "\n".join(rows) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fake", action="store_true")
    ap.add_argument("--only", nargs="*", default=SCENARIOS)
    ap.add_argument("--repeat", type=int, default=3, help="repeats of each arm; at least 3, because Jev and the model both drift")
    ap.add_argument("--allow-single", action="store_true", help="allow fewer than 3 repeats (a smoke test, never a result)")
    a = ap.parse_args(argv)
    if a.repeat < 3 and not a.allow_single:
        print("Refused: repeat each arm at least 3 times. One pass per arm cannot tell an effect from noise. (--allow-single for a smoke test.)")
        return 2
    scs = [load(s) for s in a.only]
    if a.dry_run:
        n = len(scs) * 2 * a.repeat
        print(f"{n} pipelines ({len(scs)} scenarios x skills off/on x {a.repeat} repeats, order alternated), privacy ON, about {n * 5} Gloo calls.")
        print(f"Estimate: about {n * 14000} input and {n * 2200} output tokens = about ${n * (14000 * 3 + 2200 * 15) / 1e6:.2f} at $3 and $15 per 1M.")
        for s in scs:
            print(" ", s["id"], s.get("playbook"), "-", s.get("title"))
        return
    runs = []
    for rep in range(a.repeat):
        for sc in scs:
            for flag in ((False, True) if rep % 2 == 0 else (True, False)):      # alternate the order so time of day does not favor one arm
                r = run_one(sc, flag, a.fake)
                r["repeat"] = rep
                runs.append(r)
                print(r["scenario"], r["skills"], f"rep{rep}", r["outcome"], f"attempts={r['attempts']}", f"${r['cost_usd']}", f"{r['latency_s']}s", flush=True)
    out = OUT if not a.fake else OUT / "fake-selftest"
    out.mkdir(parents=True, exist_ok=True)
    (out / "runs.json").write_text(json.dumps(runs, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "summary.md").write_text("# Skills off vs on\n\n" + ("**FAKE MODEL SELF-TEST. Not a result.**\n\n" if a.fake else "")
                                    + summarize(runs) + "\n", encoding="utf-8")
    print((out / "summary.md").read_text())
    return 0


if __name__ == "__main__":
    sys.exit(main())
