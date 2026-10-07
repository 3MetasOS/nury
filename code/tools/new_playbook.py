"""Scaffold a new crisis (a playbook). Creates code/playbooks/<id>/ from a template, status "soon", so it cannot run.

    cd code && python3 tools/new_playbook.py <id> "<Title>"            # e.g. house_fire "House fire"
    cd code && python3 tools/new_playbook.py <id> "<Title>" --root DIR  # another playbooks folder (tests)

The template has the same five-stage shape as the hospital playbook, with every domain word, prompt and source
left as TODO. The script then runs the loader's own validation on a copy with status "live" (and pending sources
allowed, because a new playbook has none approved yet) and prints what is left to do. Nothing here approves a
source or flips the status: a person does that.
"""
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from nury import playbook as pbm  # noqa: E402

BASE = "hospital"
GENERIC_DISCLAIMER = {
    "en": "Nury is an AI assistant, not a pastor, lawyer, doctor, counselor, or therapist. This is general information, not advice. TODO: name the professional the family should see.",
    "es": "Nury es un asistente de IA, no es pastor, abogado, médico, consejero ni terapeuta. Esta es información general, no asesoramiento. TODO: nombre al profesional con quien debe hablar la familia.",
}
GENERIC_JEV = {"triage": ["assumes_facts"], "pastoral": ["claims_pastoral_office", "claims_counselor", "promises_action"]}


def _blank(v):
    if isinstance(v, list):
        return []
    if isinstance(v, dict):
        return {k: _blank(x) for k, x in v.items()}
    return "TODO" if isinstance(v, str) else v


def build(pid, title, root):
    root = Path(root)
    dest = root / pid
    if not re.fullmatch(r"[a-z][a-z0-9_]{2,30}", pid):
        raise SystemExit("id must be lowercase letters, digits and underscores, 3 to 31 characters, starting with a letter")
    if dest.exists():
        raise SystemExit(f"{dest} already exists; nothing was changed")
    src = pbm.PLAYBOOKS_DIR / BASE
    (dest / "prompts").mkdir(parents=True)
    (dest / "sources").mkdir()

    pj = json.loads((src / "playbook.json").read_text(encoding="utf-8"))
    pj.update(id=pid, title=title, description="TODO: one sentence on what this crisis is.", status="soon", order=90,
              disclaimer=GENERIC_DISCLAIMER, extra_banned=[],
              boundary={"who": "TODO the people the family is", "domain": "TODO domain", "professional": "TODO professional", "professional_kind": "TODO kind"},
              intake={"placeholder": "TODO: what the pastor should say about this crisis.", "demo": "TODO: a synthetic example intake. Fictional people only."})
    (dest / "playbook.json").write_text(json.dumps(pj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    stages = json.loads((src / "stages.json").read_text(encoding="utf-8"))
    files = {}
    for st in stages:
        st["summary"] = "TODO: one plain line, at most 140 characters, no promises."
        st["jev"] = GENERIC_JEV.get(st["id"], ["assumes_facts"])
        for i, spec in enumerate(st.get("sources", [])):
            if spec.get("dynamic"):
                continue
            new = f"{spec['name']}.json"
            files[spec["file"]] = new
            spec["file"] = new
        vars_ = [sp["var"] for sp in st.get("sources", [])] + ["lang_name"]
        (dest / st["prompt"]).write_text(
            f"TODO: write the {st['id']} prompt. Model it on code/playbooks/detention/prompts/{st['id'] if st['id'] in ('triage','checklist','pastoral') else 'rights'}.txt and {BASE}/prompts/{st['id']}.txt.\n"
            f"Variables this stage fills: {', '.join('{{' + v + '}}' for v in vars_)}. Every one must appear in the prompt.\n"
            + ("The pastoral stage also asks for the VERSE / WHY / MESSAGE labels: copy them from the hospital pastoral prompt.\n" if st["id"] == "pastoral" else ""),
            encoding="utf-8")
    (dest / "stages.json").write_text(json.dumps(stages, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for old, new in files.items():
        d = json.loads((src / "sources" / old).read_text(encoding="utf-8"))
        (dest / "sources" / new).write_text(json.dumps(_blank(d), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (dest / "sources" / "approvals.json").write_text("{}\n", encoding="utf-8")
    shutil.copy(src / "outcomes.json", dest / "outcomes.json")
    return dest


def validate(pid, root):
    """Run the loader on a copy with status live. Pending sources are allowed: a new playbook has none approved."""
    tmp = Path(tempfile.mkdtemp())
    try:
        shutil.copytree(Path(root) / pid, tmp / pid)
        f = tmp / pid / "playbook.json"
        j = json.loads(f.read_text(encoding="utf-8"))
        j["status"] = "live"
        f.write_text(json.dumps(j), encoding="utf-8")
        old = os.environ.get("NURY_ALLOW_PENDING")
        os.environ["NURY_ALLOW_PENDING"] = "1"
        try:
            pb = pbm.load_playbook(pid, tmp)
        finally:
            if old is None:
                os.environ.pop("NURY_ALLOW_PENDING", None)
            else:
                os.environ["NURY_ALLOW_PENDING"] = old
        return [s.id for s in pb.stages]
    finally:
        shutil.rmtree(tmp)


NEXT = """Next steps (the playbook is status "soon": it cannot run and shows as a coming-soon card):
 1. playbook.json: description, boundary words (who, domain, professional), disclaimer, intake placeholder and demo (fictional only), extra_banned patterns for this domain.
 2. prompts/: write each stage prompt. Use the variables listed in each stub.
 3. sources/: add vetted points and contacts, each with a source and a source_id. Nothing is vetted until a person approves it in sources/approvals.json ("approved"). A pending source blocks the playbook.
 4. stages.json: write each summary; set the checks; set the Jev questions for the domain (add the advice and outcome questions for this crisis in code/nury/jev_gate.py and evaluations/judges/jev_judges.py, same wording, and a test).
 5. evaluations/scenarios/: write the scenarios (a happy path, the unsafe asks, a vague intake, a prompt injection) and the pass criteria.
 6. code/tests/: copy the playbook tests, add one for each rule you wrote; run them.
 7. Run it once live with the Jev gate on and read the drafts. Then set "status": "live" in playbook.json.
"""

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = pbm.PLAYBOOKS_DIR
    if "--root" in sys.argv:
        root = Path(sys.argv[sys.argv.index("--root") + 1])
        args = [a for a in args if a != str(root)]
    if len(args) != 2:
        raise SystemExit(__doc__)
    pid, title = args
    dest = build(pid, title, root)
    print(f"Created {dest}")
    print("Loader validation (on a copy with status live): OK, stages =", validate(pid, root))
    print(NEXT)
