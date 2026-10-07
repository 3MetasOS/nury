"""Run one scenario live and save its audit file, then print a timed trace of the events.

    cd code && python3 tools/trace_run.py 01 ../documents/product/trace_detention_01.jsonl

Live Gloo and Jev calls (about 9 cents of Gloo). Privacy is ON. The audit file holds categories, ids, probabilities and
timings. It holds no draft text except `draft_rejected`, and a check below refuses to write a file that contains a protected name.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
os.environ["NURY_DEMO_NETWORK"] = "1"

from nury import gloo_client  # noqa: E402,F401
from nury.audit import AuditLog  # noqa: E402
from nury.engine import get_playbook, run_scripted  # noqa: E402
from nury.privacy import make_client  # noqa: E402
from scripture_live import scenario  # noqa: E402

if __name__ == "__main__":
    pat, out = sys.argv[1], Path(sys.argv[2])
    I, lang = scenario(pat)
    pb = "hospital" if pat.startswith("h") else "detention"
    c = make_client(intake=I)
    c.allow_playbook(get_playbook(pb))
    out.unlink(missing_ok=True)
    au = AuditLog(path=str(out))
    st, rs, _ = run_scripted(I, lang, playbook=pb, client=c, audit=au)
    names = [v for v in c.map().values() if len(v) > 2]
    blob = out.read_text(encoding="utf-8")
    leaked = [n for n in names if n.lower() in blob.lower()]
    if leaked:
        out.unlink()
        raise SystemExit(f"refusing to keep the audit: it contains {leaked}")
    ev = [json.loads(x) for x in blob.splitlines()]
    t0 = datetime.fromisoformat(ev[0]["ts"])
    print("outcome:", st.outcome["outcome"], "| events:", len(ev), "| protected terms:", len(names), "| none found in the file")
    for e in ev:
        ms = round((datetime.fromisoformat(e["ts"]) - t0).total_seconds() * 1000)
        rest = {k: v for k, v in e.items() if k not in ("ts", "kind", "stage")}
        print(f"+{ms:>6} ms  {e['kind']:<18} {e.get('stage', ''):<10} {json.dumps(rest, ensure_ascii=False)[:150]}")
