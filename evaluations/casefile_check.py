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
            except Exception as e:
                problems = [f"save failed: {type(e).__name__}: {str(e)[:100]}"]
        out.append({"id": sc["id"], "pass": not problems, "problems": problems, "rejected_drafts": len(rejected)})
        print(f"{sc['id']:<34} {'PASS' if not problems else 'FAIL'} {problems}", flush=True)
    d = HERE / "results"
    d.mkdir(exist_ok=True)
    (d / "casefile.json").write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    run_live()
