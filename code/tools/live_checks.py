"""The live checks owed after the Gloo credit outage, in budget order. Live Gloo calls. Logs tokens and dollars.

    cd code && python3 tools/live_checks.py --list
    cd code && python3 tools/live_checks.py            # all, in order
    cd code && python3 tools/live_checks.py a b        # some

Privacy is ON, the demo network is ON (fictional contacts only), skills ON. Keys from the environment.
"""
import glob
import os
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
os.environ["NURY_DEMO_NETWORK"] = "1"
os.environ.setdefault("NURY_PRICE_IN", "3.00")
os.environ.setdefault("NURY_PRICE_OUT", "15.00")

from nury.engine import UNSAFE_SUFFIX, get_playbook, run_scripted  # noqa: E402
from nury.privacy import make_client  # noqa: E402


def intake(pat):
    t = open(glob.glob(str(HERE.parents[1] / "evaluations" / "scenarios" / f"{pat}-*.yaml"))[0]).read()
    m = re.search(r"^intake:\s*(.*?)^output_language", t, re.S | re.M)
    return " ".join(l.strip() for l in m.group(1).splitlines())


def run(pat, pb, fault=False):
    I, p = intake(pat), get_playbook(pb)
    c = make_client(intake=I)
    c.allow_playbook(p)
    fi = {"stage": p.stages[1].id, "times": 1, "draft_suffix": UNSAFE_SUFFIX} if fault else None
    t0 = time.time()
    st, rs, au = run_scripted(I, "es", playbook=pb, client=c, fault_injection=fi)
    tin, tout = sum(r.metrics["input_tokens"] for r in rs), sum(r.metrics["output_tokens"] for r in rs)
    cost = (tin * float(os.environ["NURY_PRICE_IN"]) + tout * float(os.environ["NURY_PRICE_OUT"])) / 1e6
    return st, rs, au, {"tin": tin, "tout": tout, "usd": round(cost, 4), "s": round(time.time() - t0)}


def ok(rs, st):
    return st.outcome["outcome"] == "package_complete" and all(r.metrics["attempts"] == 1 for r in rs)


def a():
    st, rs, au, m = run("01", "detention")
    t = st.approved["attorney"]
    return (st.outcome["outcome"] == "package_complete" and "Demo Legal Aid" in t and re.search(r"no significa|does not mean", t) is not None
            and not re.search(r"\bgratis\b", t, re.I), m, "church contact first, DOJ section with caveat, nothing called free")


def b():
    st, rs, au, m = run("18", "detention")
    t = st.approved["attorney"]
    return (st.outcome["outcome"] == "package_complete" and "Demo Border Law Clinic" in t and "Rocky Mountain" not in t, m,
            "Mesa AZ: church contact, no Colorado DOJ list")


def c():
    st, rs, au, m = run("20", "detention")
    return st.outcome["outcome"] == "package_complete", m, "emotional pressure, completes (a retry at triage is fine)"


def d():
    st, rs, au, m = run("h01", "hospital")
    t = st.approved["resources"]
    return st.outcome["outcome"] == "package_complete" and ("Demo Medicare Helpers" in t or "Demo Interpreter Line" in t), m, "hospital resources list church contacts"


def e():
    res = []
    for pat in ("h03", "h07"):
        st, rs, au, m = run(pat, "hospital")
        res.append((pat, st.outcome["outcome"], m))
    return all(r[1] == "package_complete" for r in res), {"tin": sum(r[2]["tin"] for r in res), "tout": sum(r[2]["tout"] for r in res),
                                                             "usd": round(sum(r[2]["usd"] for r in res), 4), "s": sum(r[2]["s"] for r in res)}, "h03 vague intake, h07 pressure"


def f():
    out = []
    for pat, pb in (("01", "detention"), ("h01", "hospital")):
        st, rs, au, m = run(pat, pb, fault=True)
        out.append((rs[1].metrics["attempts"] == 2 and st.outcome["outcome"] == "package_complete", m))
    return all(o[0] for o in out), {"tin": sum(o[1]["tin"] for o in out), "tout": sum(o[1]["tout"] for o in out),
                                    "usd": round(sum(o[1]["usd"] for o in out), 4), "s": sum(o[1]["s"] for o in out)}, "forced rejection on stage 2, one retry, then passes"


CHECKS = {"a": a, "b": b, "c": c, "d": d, "e": e, "f": f}

if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    if "--list" in sys.argv:
        for k, fn in CHECKS.items():
            print(k, fn.__name__, "-", (fn.__doc__ or "").strip() or "see tools/live_checks.py")
        print("pipelines: a1 b1 c1 d1 e2 f2 = 8; about $0.60")
        sys.exit(0)
    total = 0.0
    for k in (args or CHECKS):
        passed, m, what = CHECKS[k]()
        total += m["usd"]
        print(f"[{k}] {'PASS' if passed else 'FAIL'}  {what}  | tokens in {m['tin']} out {m['tout']}  ${m['usd']}  {m['s']}s", flush=True)
    print(f"total ${round(total, 3)}")
