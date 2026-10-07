"""Skills before/after: the same scenarios with the Nury skills OFF and ON. Live Gloo calls.

    python3 evaluations/skills_ab.py --dry-run          # plan and cost estimate, no calls
    python3 evaluations/skills_ab.py --fake             # script smoke test with a fake model, no calls
    python3 evaluations/skills_ab.py                    # live: 7 scenarios x 2 modes = 14 pipelines

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


def summarize(runs):
    rows = []
    for mode in ("off", "on"):
        r = [x for x in runs if x["skills"] == mode]
        n = max(len(r), 1)
        rows.append((mode, len(r), sum(x["stock_phrase_hits"] for x in r), sum(x["dashes"] for x in r), sum(x["unsourced_tip_lines"] for x in r),
                     round(sum(x["words"] for x in r) / n), sum(x["attempts"] for x in r), sum(x["self_corrections"] for x in r),
                     sum(1 for x in r if x["outcome"] != "package_complete"), round(sum(x["tokens_in"] for x in r) / n),
                     round(sum(x["tokens_out"] for x in r) / n), round(sum(x["cost_usd"] for x in r), 3), round(sum(x["latency_s"] for x in r) / n, 1)))
    head = "| skills | runs | stock phrases | dashes | unsourced tip lines | avg words | stage attempts | self-corrections | not complete | avg tokens in | avg tokens out | total $ | avg s |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
    return head + "\n".join("| " + " | ".join(str(c) for c in row) + " |" for row in rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fake", action="store_true")
    ap.add_argument("--only", nargs="*", default=SCENARIOS)
    a = ap.parse_args()
    scs = [load(s) for s in a.only]
    if a.dry_run:
        n = len(scs) * 2
        print(f"{n} pipelines ({len(scs)} scenarios x skills off/on), privacy ON, about {n * 5} Gloo calls.")
        print(f"Estimate: about {n * 14000} input and {n * 2200} output tokens = about ${n * (14000 * 3 + 2200 * 15) / 1e6:.2f} at $3 and $15 per 1M.")
        for s in scs:
            print(" ", s["id"], s.get("playbook"), "-", s.get("title"))
        return
    runs = []
    for sc in scs:
        for flag in (False, True):
            r = run_one(sc, flag, a.fake)
            runs.append(r)
            print(r["scenario"], r["skills"], r["outcome"], f"attempts={r['attempts']}", f"${r['cost_usd']}", f"{r['latency_s']}s", flush=True)
    out = OUT if not a.fake else OUT / "fake-selftest"
    out.mkdir(parents=True, exist_ok=True)
    (out / "runs.json").write_text(json.dumps(runs, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "summary.md").write_text("# Skills off vs on\n\n" + ("**FAKE MODEL SELF-TEST. Not a result.**\n\n" if a.fake else "")
                                    + summarize(runs) + "\n", encoding="utf-8")
    print((out / "summary.md").read_text())


if __name__ == "__main__":
    main()
