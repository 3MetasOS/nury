"""Live check of the Scripture work. Live Gloo calls; with --yv also live YouVersion calls. Logs tokens and dollars.

    cd code && python3 tools/scripture_live.py bank 01 10 14 h01 h03      # verse text from the bank
    cd code && python3 tools/scripture_live.py yv 01 h01                  # verse text from YouVersion (needs YVP_* in .env)

Prints the pastoral message, the verse chosen, attempts, the audit provider lines, and the raw model text of the
pastoral stage (before names are put back). Keys are read from the environment or the repo-root .env and never printed.
"""
import glob
import json
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

from nury import gloo_client  # noqa: E402,F401  (loads the repo-root .env)
from nury.engine import get_playbook, run_scripted  # noqa: E402
from nury.privacy import make_client  # noqa: E402


def scenario(pat):
    f = glob.glob(str(HERE.parents[1] / "evaluations" / "scenarios" / f"{pat}-*.yaml"))[0]
    t = open(f).read()
    m = re.search(r"^intake:\s*(.*?)^output_language", t, re.S | re.M)
    lang = re.search(r"^output_language:\s*(\w+)", t, re.M).group(1)
    return " ".join(l.strip() for l in m.group(1).splitlines()), lang


def run(pat, mode):
    I, lang = scenario(pat)
    pb = "hospital" if pat.startswith("h") else "detention"
    if mode == "bank":
        os.environ.pop("YVP_APP_KEY", None)
    c = make_client(intake=I)
    c.allow_playbook(get_playbook(pb))
    raw = []
    orig = c.inner.ask

    def ask(user_input, instructions=None, **kw):
        t, meta = orig(user_input, instructions=instructions, **kw)
        if "pastoral message" in (instructions or ""):
            raw.append(t)
        return t, meta
    c.inner.ask = ask
    t0 = time.time()
    st, rs, au = run_scripted(I, lang, playbook=pb, client=c)
    tin, tout = sum(r.metrics["input_tokens"] for r in rs), sum(r.metrics["output_tokens"] for r in rs)
    usd = round((tin * 3.0 + tout * 15.0) / 1e6, 4)
    past = [r for r in rs if r.stage_id == "pastoral"][0]
    print(f"\n===== {pat} ({pb}, family language {lang}, mode {mode}) outcome={st.outcome['outcome']} "
          f"attempts={[r.metrics['attempts'] for r in rs]} tokens={tin}/{tout} usd={usd} s={round(time.time() - t0)}")
    print("pastoral status:", past.status, "| verse:", past.scripture, "| note:", bool(past.note))
    print("--- pastoral text the pastor sees ---\n" + (past.draft or "(none)"))
    print("--- raw model text(s) of the pastoral stage, before names are restored ---")
    for i, t in enumerate(raw, 1):
        print(f"[call {i}]\n{t}")
    for r in rs:
        for a in r.attempts:
            if a["violations"]:
                print(f"rejected attempt: stage={r.stage_id} n={a['n']} categories={sorted({v['category'] for v in a['violations']})}")
    for e in au.events:
        if e["kind"] in ("scripture", "scripture_fallback"):
            print("audit:", json.dumps({k: v for k, v in e.items() if k != "ts"}, ensure_ascii=False))
    return usd


if __name__ == "__main__":
    mode, pats = sys.argv[1], sys.argv[2:]
    total = 0.0
    for p in pats:
        total += run(p, mode)
    print(f"\nTOTAL usd (Gloo, est.) = {round(total, 4)}")
