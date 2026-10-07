"""Candidate improvements: the review file format and its checks.

A candidate is a proposed change to Nury, written by the learning report or by a person. It is NEVER applied by any
script outside a temporary copy. It becomes real only through a human approval recorded in its file and a normal release.

    candidates/<id>.md

    ---
    id: c-0001-pastoral-length          (must equal the file name)
    type: prompt_line                   prompt_line | new_rule | new_jev_question | new_scenario
    status: proposed                    proposed -> tested -> approved -> released   (or rejected at any point)
    created: 2026-10-07
    synthetic: true                     true when the evidence came from synthetic scenarios, never a real pastor
    evidence: {"stage": "pastoral", "edits": 7}
    approved_by: null                   a person's name; required from status approved on
    approved_date: null                 YYYY-MM-DD; required from status approved on
    test_result: null                   path to the saved before and after table; required from status tested on
    release_commit: null                required for released
    ---
    # Title
    ## Why
    ## Draft change
    ```json change
    {"kind": "append", "file": "code/playbooks/detention/prompts/pastoral.txt", "text": "Keep it under 90 words.\n"}
    ```

Change kinds: append (add text to a file), replace (old -> new in a file), json_append (add a value to a list in a JSON file,
`key` may be dotted), add_file (a new file). A candidate with no change block can be proposed but cannot be tested.
"""
import json
import re
import sys
from pathlib import Path

TYPES = ("prompt_line", "new_rule", "new_jev_question", "new_scenario")
STATUSES = ("proposed", "tested", "approved", "released", "rejected")
ORDER = {s: i for i, s in enumerate(("proposed", "tested", "approved", "released"))}
KINDS = ("append", "replace", "json_append", "add_file")
FIELDS = ("id", "type", "status", "created", "synthetic", "evidence", "approved_by", "approved_date", "test_result", "release_commit")
_BLOCK = re.compile(r"```json change\n(.*?)\n```", re.S)
_DATE = re.compile(r"\d{4}-\d\d-\d\d")


class CandidateError(ValueError):
    pass


def parse(text):
    m = re.match(r"---\n(.*?)\n---\n(.*)\Z", text, re.S)
    if not m:
        raise CandidateError("no front matter")
    meta = {}
    for ln in m.group(1).splitlines():
        if not ln.strip():
            continue
        k, _, v = ln.partition(":")
        v = v.strip()
        try:
            meta[k.strip()] = json.loads(v)
        except ValueError:
            meta[k.strip()] = v
    return meta, m.group(2), [json.loads(b) for b in _BLOCK.findall(m.group(2))]


def check(meta, changes, name=None):
    """A list of problems. Empty means the file is well formed."""
    p = []
    for f in FIELDS:
        if f not in meta:
            p.append(f"missing field {f}")
    if p:
        return p
    if name and meta["id"] != name:
        p.append("id must equal the file name")
    if meta["type"] not in TYPES:
        p.append(f"type must be one of {TYPES}")
    if meta["status"] not in STATUSES:
        p.append(f"status must be one of {STATUSES}")
    if not isinstance(meta["synthetic"], bool):
        p.append("synthetic must be true or false")
    if not _DATE.fullmatch(str(meta["created"])):
        p.append("created must be YYYY-MM-DD")
    if not isinstance(meta["evidence"], dict) or not meta["evidence"]:
        p.append("evidence must be a non-empty object of counts")
    st = meta["status"]
    rank = ORDER.get(st, -1)
    if rank >= ORDER["tested"] and not meta["test_result"]:
        p.append("a tested candidate needs test_result (the saved before and after table)")
    if rank >= ORDER["tested"] and not changes:
        p.append("a tested candidate needs a change block")
    if rank >= ORDER["approved"]:
        if not meta["approved_by"] or not isinstance(meta["approved_by"], str) or meta["approved_by"].lower() in ("nury", "auto", "bot", "script"):
            p.append("approved needs approved_by: the name of a person")
        if not _DATE.fullmatch(str(meta["approved_date"] or "")):
            p.append("approved needs approved_date YYYY-MM-DD")
    if st == "released" and not meta["release_commit"]:
        p.append("released needs release_commit")
    if st in ("proposed", "tested", "rejected") and (meta["approved_by"] or meta["approved_date"]) and st != "rejected":
        p.append("approved_by and approved_date belong to approved or released candidates only")
    for c in changes:
        if c.get("kind") not in KINDS:
            p.append(f"change kind must be one of {KINDS}")
        elif not c.get("file") or c["file"].startswith("/") or ".." in Path(c["file"]).parts:
            p.append("change file must be a relative path inside the repository")
        elif c["kind"] == "append" and "text" not in c:
            p.append("append needs text")
        elif c["kind"] == "replace" and ("old" not in c or "new" not in c):
            p.append("replace needs old and new")
        elif c["kind"] == "json_append" and ("key" not in c or "value" not in c):
            p.append("json_append needs key and value")
        elif c["kind"] == "add_file" and "content" not in c:
            p.append("add_file needs content")
        elif c["file"].startswith(".git") or c["file"].startswith(".env"):
            p.append("a change may not touch .git or .env")
    if meta["type"] == "new_jev_question" and changes:
        p.append("a new Jev question changes shared wording and the eval harness: write it by hand, not as a change block")
    return p


def load(path):
    path = Path(path)
    meta, body, changes = parse(path.read_text(encoding="utf-8"))
    return meta, body, changes, check(meta, changes, path.stem)


def render(meta, title, why, changes, extra=""):
    fm = "\n".join(f"{k}: {json.dumps(meta[k], ensure_ascii=False)}" for k in FIELDS)
    blocks = "\n\n".join("```json change\n" + json.dumps(c, ensure_ascii=False, indent=1) + "\n```" for c in changes) or \
        "_No change block yet. A person writes the change before this can be tested._"
    return f"---\n{fm}\n---\n# {title}\n\n## Why\n\n{why}\n\n## Draft change\n\n{blocks}\n{extra}"


def new_meta(cid, ctype, evidence, created, synthetic):
    return {"id": cid, "type": ctype, "status": "proposed", "created": created, "synthetic": synthetic, "evidence": evidence,
            "approved_by": None, "approved_date": None, "test_result": None, "release_commit": None}


def check_dir(folder):
    out = {}
    for f in sorted(Path(folder).glob("*.md")):
        if f.name.upper() == "README.MD":
            continue
        try:
            out[f.name] = load(f)[3]
        except Exception as e:
            out[f.name] = [f"unreadable: {type(e).__name__}"]
    return out


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parents[2] / "candidates")
    res = check_dir(folder)
    bad = {k: v for k, v in res.items() if v}
    for k, v in res.items():
        print(("OK   " if not v else "FAIL ") + k, "; ".join(v))
    sys.exit(1 if bad else 0)
