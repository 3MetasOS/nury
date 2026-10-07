#!/usr/bin/env python3
"""Case-file checks. Offline function check_case_dir() plus a live runner for 3 scenarios.

  python3 evaluations/casefile_check.py            # runs scenarios_casefile/*.yaml live, saves to a temp root

A saved case folder must contain: only approved or edited text, no rejected-draft text, no key, only vetted
links and phones, and (when edited) the pastor's text. The log must hold categories only.
"""
import json, os, re, sys, tempfile
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from judges.deterministic import load_allowlist  # noqa: E402

URL = re.compile(r"https?://[^\s)>\]\"']+|\b(?:www\.)?[a-z0-9\-]+\.(?:org|com|gov|net|edu|info|us|mx)\b(?:/[^\s)>\]\"']*)?", re.I)
PHONE = re.compile(r"(?:\+?1[\s.\-]?)?\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}")
SECRET = re.compile(r"Bearer\s+\S{12,}|sk-[A-Za-z0-9]{20,}|api[_-]?key\s*[:=]\s*\S{8,}", re.I)
FILE_LIKE = re.compile(r"\.(md|svg|json|txt|zip)$", re.I)


def read_all(d):
    return {p.name: p.read_text(encoding="utf-8", errors="replace") for p in Path(d).iterdir() if p.is_file()}


def check_case_dir(d, playbook, rejected_snippets=(), secrets=(), edit_marker=None):
    """Return a list of problems (empty = clean)."""
    files = read_all(d)
    domains, phones = load_allowlist(playbook)
    bad = []
    for name, text in files.items():
        for snip in rejected_snippets:
            if snip and snip in text:
                bad.append(f"{name}: contains rejected-draft text {snip[:40]!r}")
        for sec in secrets:
            if sec and sec in text:
                bad.append(f"{name}: contains a key value")
        if SECRET.search(text):
            bad.append(f"{name}: looks like a key or bearer token")
        scan = re.sub(r'xmlns(?::\w+)?="[^"]*"', "", text)   # XML namespace ids are not links
        for u in URL.findall(scan):
            if FILE_LIKE.search(u):
                continue
            host = urlparse(u if "//" in u else "//" + u).netloc.lower().removeprefix("www.")
            if host and host not in domains:
                bad.append(f"{name}: unvetted link {u}")
        for p in PHONE.findall(text):
            d10 = re.sub(r"\D", "", p)[-10:]
            if not any(d10 == v[-10:] for v in phones):
                bad.append(f"{name}: unvetted phone {p}")
    if "log.md" in files and re.search(r"matched\s+'", files["log.md"]):
        bad.append("log.md: quotes a matched phrase (categories only)")
    if edit_marker:
        page = next((t for n, t in files.items() if re.match(r"0\d-", n) and edit_marker in t), None)
        if page is None:
            bad.append("edited text is not in any stage page")
        if "index.md" in files and "edit" not in files["index.md"].lower():
            bad.append("index.md does not say the case was edited")
    return bad


USAGE = []   # [(label, tokens_in, tokens_out)] per pipeline, for the cost log
P_IN, P_OUT = 3.00, 15.00   # gloo-anthropic-claude-sonnet-4.6, USD per 1M tokens (Gloo /platform/v2/models)


def note_usage(label, results):
    USAGE.append((label, sum(r.metrics.get("input_tokens", 0) for r in results), sum(r.metrics.get("output_tokens", 0) for r in results)))


def tree_hash(d):
    import hashlib
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(d).iterdir()) if p.is_file()}


def revise_and_check(sc, saved, root, ids, secrets, cf, run_scripted):
    """Save v2 beside v1 with the same helpers the app uses. v1 must stay byte-identical."""
    sys.path.insert(0, str(HERE.parent / "code"))
    import app.server as srv
    srv.CASES_ROOT = root
    v1_dir, v1_before = Path(saved["path"]), tree_hash(saved["path"])
    rv = dict(sc["revise"], case_id=saved["id"])
    intake, meta = srv.revision_intake(saved["id"], rv["step"], rv["result"], rv["note"])
    state2, results2, audit2 = run_scripted(intake, sc["output_language"], {}, playbook=sc["playbook"])
    note_usage(sc["id"] + " (v2)", results2)
    new_id = srv.next_version_id(saved["id"])
    r2 = cf.save_case(state2, audit2, playbook=sc["playbook"], root=root, case_id=new_id)
    d2 = Path(r2["path"])
    srv.write_changes(d2, new_id, rv, ids)
    bad = []
    if not new_id.endswith("-v2"):
        bad.append(f"v2 id is {new_id}")
    if tree_hash(v1_dir) != v1_before:
        bad.append("v1 files changed after saving v2")
    ch = (d2 / "changes.md").read_text(encoding="utf-8") if (d2 / "changes.md").exists() else ""
    if rv["note"].strip() not in ch:
        bad.append("changes.md does not hold the pastor's words")
    if "does not predict" not in ch:
        bad.append("changes.md lacks the no-prediction line")
    bad += [f"v2: {p}" for p in check_case_dir(d2, sc["playbook"], [], secrets)]
    t1 = (v1_dir / "01-triage.md").read_text(encoding="utf-8")
    t2 = (d2 / "01-triage.md").read_text(encoding="utf-8")
    if t1 == t2:
        bad.append("v2 triage is identical to v1: the update did not change the case summary")
    return bad


def run_live():
    import yaml
    sys.path.insert(0, str(HERE.parent / "code"))
    from nury import casefile as cf
    from nury.engine import UNSAFE_SUFFIX, get_playbook, run_scripted
    from nury.gloo_client import load_env
    load_env()
    secrets = [os.environ.get("GLOO_API_KEY", ""), os.environ.get("JEV_API_KEY", "")]
    out = []
    for f in sorted((HERE / "scenarios_casefile").glob("*.yaml")):
        sc = yaml.safe_load(f.read_text())
        pb = get_playbook(sc["playbook"])
        ids = [s.id for s in pb.stages]
        fi = sc.get("fault_injection")
        fi = {"stage": ids[fi["stage"] - 1], "times": fi["times"], "draft_suffix": UNSAFE_SUFFIX} if fi else None
        dec = {}
        for k, a in sc["pastor_actions"].items():
            dec[ids[int(k) - 1]] = ("edit", a["edit"]) if isinstance(a, dict) else a
        state, results, audit = run_scripted(sc["intake"], sc["output_language"], dec, fault_injection=fi, playbook=sc["playbook"])
        note_usage(sc["id"] + " (v1)", results)
        rejected = [a["text"] for r in results for a in r.attempts if a.get("violations") and a.get("text")]
        snippets = [UNSAFE_SUFFIX.strip()] if fi else []
        with tempfile.TemporaryDirectory() as root:
            try:
                saved = cf.save_case(state, audit, playbook=sc["playbook"], root=root)
                problems = check_case_dir(saved["path"], sc["playbook"], snippets, secrets, sc.get("edit_marker"))
                if len(list(Path(saved["path"]).glob("0*-*.md"))) != len(ids):
                    problems.append("stage page count does not match the playbook")
                if fi and not rejected:
                    problems.append("fault was not injected: no rejected draft to test against")
                if sc.get("revise"):
                    problems += revise_and_check(sc, saved, root, ids, secrets, cf, run_scripted)
            except Exception as e:
                problems = [f"save failed: {type(e).__name__}: {str(e)[:100]}"]
        out.append({"id": sc["id"], "pass": not problems, "problems": problems, "rejected_drafts": len(rejected)})
        print(f"{sc['id']:<34} {'PASS' if not problems else 'FAIL'} {problems}", flush=True)
    d = HERE / "results"
    d.mkdir(exist_ok=True)
    tot_i, tot_o = sum(u[1] for u in USAGE), sum(u[2] for u in USAGE)
    for label, ti, to in USAGE:
        print(f"  {label:<40} in {ti:>6} out {to:>5}  ${ti * P_IN / 1e6 + to * P_OUT / 1e6:.4f}")
    cost = tot_i * P_IN / 1e6 + tot_o * P_OUT / 1e6
    print(f"TOTAL in {tot_i} out {tot_o} cost ${cost:.4f}")
    (d / "casefile.json").write_text(json.dumps({"checks": out, "usage": [{"run": u[0], "in": u[1], "out": u[2]} for u in USAGE],
                                                  "tokens_in": tot_i, "tokens_out": tot_o, "cost_usd": round(cost, 4)}, indent=1))
    return out


if __name__ == "__main__":
    run_live()
