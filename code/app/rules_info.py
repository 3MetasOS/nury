"""Plain-words data for the 'How this was built' page: the rules table and the playbook detail.
Reads the live registry and the playbook files. Nothing here is a model call. Stdlib only."""
import inspect
import json
import re

from nury import checks
from nury.playbook import PLAYBOOKS_DIR, list_playbooks

# Named checks that carry no docstring of their own get a plain sentence here. A test fails if a registry check has neither.
PLAIN = {
    "required_labels": "The draft must carry every label the stage names (for example SITUATION, PEOPLE, LOCATION), so nothing is skipped.",
    "numbered_after": "A list must follow a marker with the right number of items (triage ends with three numbered missing facts).",
    "cited_bullets": "Every point in the brief ends with a citation to a vetted source. A point with no source is rejected.",
    "ends_with_referral": "The brief must end by urging the family to speak with a qualified person (an attorney, or the care team).",
    "vetted_links_present": "The links the stage must hand over (hotlines, official lists) are all present and match the vetted sources.",
    "required_headings": "The checklist must carry its three headings, in order, so the family can find each part.",
    "max_words": "The message stays under its word limit (120 words for the pastoral message).",
}

# The safety floor is code in guardrails and the engine. It is not a named check, and no playbook or skill can remove it.
FLOOR = [
    ("banned_patterns", "Banned patterns, English and Spanish: no outcome prediction, no promised outcome, no advice to plead, sign, file or apply, no legal strategy, no claim to be a lawyer, counselor, therapist, doctor or pastor."),
    ("disclaimer", "The disclaimer is on every output. A playbook with a weaker disclaimer is refused when it loads."),
    ("family_language", "The draft is in the family's language, and the checker confirms it."),
    ("vetted_contacts", "Every link, phone number, web address and email comes from the vetted sources or from text the pastor already approved."),
    ("no_send_path", "Nury has no way to email, text or post. Nothing reaches the family except through the pastor."),
]


def _first_sentence(text):
    """The docstring's first paragraph, as one line, capped. Short first sentences keep the next one so the meaning survives."""
    para = (text or "").strip().split("\n\n")[0]
    return " ".join(para.split())[:320]


def _usage():
    """check name -> ["Detention: 2. Rights brief", ...] read from every playbook's stages.json."""
    use = {}
    for p in list_playbooks():
        f = PLAYBOOKS_DIR / p["id"] / "stages.json"
        if not f.is_file():
            continue
        for st in json.loads(f.read_text(encoding="utf-8")):
            for c in st.get("checks", []):
                use.setdefault(c["name"], []).append(f'{p["title"]}: {st["title"]}')
    return use


def rules():
    """Every rule, from nury.rules.describe_all(): the safety floor, the named checks and the Jev questions. Read-only."""
    from nury import rules as R
    out = []
    for r in R.describe_all():
        st = [f'{x["playbook"]}: {x["stage"]}' if isinstance(x, dict) else str(x) for x in r.get("stages", [])]
        out.append({"name": r["name"], "kind": r["kind"], "explanation": r["explanation"], "where": r.get("where", ""),
                    "stages": st or ["Every stage" if r["kind"] == "floor" else "Not named in a stage file"]})
    n = lambda k: sum(1 for r in out if r["kind"] == k)
    return {"rules": out, "count_floor": n("floor"), "count_named": n("check"), "count_jev": n("classifier")}


def playbook_detail(pid):
    f = PLAYBOOKS_DIR / pid / "stages.json"
    if not re.fullmatch(r"[a-z0-9-]+", pid or "") or not f.is_file():
        return None
    stages = []
    for st in json.loads(f.read_text(encoding="utf-8")):
        stages.append({"id": st["id"], "title": st["title"], "summary": st.get("summary", ""), "audience": st.get("audience", ""),
                       "prompt": st.get("prompt", ""), "sources": st.get("sources", []), "deps": st.get("deps", []),
                       "checks": [c["name"] for c in st.get("checks", [])], "jev": st.get("jev", [])})
    pj = PLAYBOOKS_DIR / pid / "playbook.json"
    meta = json.loads(pj.read_text(encoding="utf-8")) if pj.is_file() else {}
    outc = PLAYBOOKS_DIR / pid / "outcomes.json"
    outcomes = json.loads(outc.read_text(encoding="utf-8")) if outc.is_file() else {}
    return {"id": pid, "title": meta.get("title", pid), "languages": meta.get("languages", []), "stages": stages,
            "outcomes": sorted(outcomes) if isinstance(outcomes, dict) else [], "sources": sorted(p.name for p in (PLAYBOOKS_DIR / pid / "sources").glob("*") if p.is_file())}
