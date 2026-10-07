"""Playbook loader. A crisis is a folder under code/playbooks/, not engine code.

    playbook.json  stages.json  prompts/  sources/  outcomes.json

The engine owns the safety floor. A playbook can add checks and sources.
It cannot remove the floor, and the loader refuses a disclaimer that drops it.
"""

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from . import checks as checks_lib
from . import skills as skills_lib

PLAYBOOKS_DIR = Path(__file__).resolve().parent.parent / "playbooks"
LANG_NAME = {"es": "Spanish", "en": "English"}
OUTCOMES = ("package_complete", "stopped_by_pastor", "escalated", "blocked")


class PlaybookError(Exception):
    pass


@dataclass
class Stage:
    id: str
    title: str
    audience: str                                  # "pastor" (English) or "family" (family language)
    prompt: str                                    # prompt text, read from prompts/
    deps: list = field(default_factory=list)       # earlier stage ids it consumes
    sources: list = field(default_factory=list)    # source names (kept for the eval adapter)
    source_specs: list = field(default_factory=list)
    checks: list = field(default_factory=list)     # [{"name", ...params}]
    input: dict = field(default_factory=dict)
    when: Optional[dict] = None                    # run only if this matches triage fields
    variants: list = field(default_factory=list)   # [{"when", "prompt"}] first match swaps the prompt
    prompt_file: str = ""
    skills: list = field(default_factory=list)     # Skill objects, loaded from code/skills/
    jev: list = field(default_factory=list)        # Jev classifier questions for this stage's draft (see nury/jev_gate.py)
    scripture: bool = False                        # pastoral stage: the model picks a verse id, the engine inserts the text
    summary: str = ""                              # one plain line for the pastor's screen. Display only: never in a prompt, check or audit


@dataclass
class Playbook:
    id: str
    title: str
    description: str
    languages: list
    default_family_language: str
    disclaimer: dict
    draft_label: dict
    stages: list
    outcomes: dict
    dir: Path
    boundary: dict = field(default_factory=dict)       # domain words the engine's rules template fills in
    extra_banned: list = field(default_factory=list)   # [{"pattern", "why"}] added to the floor
    sources: dict = field(default_factory=dict)    # name -> loaded JSON
    pending_sources: list = field(default_factory=list)  # source ids not yet approved (dev flag only)

    @property
    def registry(self):
        return {s.id: s for s in self.stages}


def allow_pending():
    """Dev only: run a playbook whose sources are not all approved. Never for the demo or the eval."""
    return os.environ.get("NURY_ALLOW_PENDING") == "1"


def list_playbooks(root: Optional[Path] = None):
    """[{id, title, description, status}] in display order, for GET /api/playbooks.

    status is "live" or "soon". A playbook marked soon, or whose vetted sources are not all
    approved yet, is listed as soon. The engine refuses to run a soon entry."""
    out = []
    for d in (root or PLAYBOOKS_DIR).iterdir():
        f = d / "playbook.json"
        if not f.is_file():
            continue
        j = json.loads(f.read_text(encoding="utf-8"))
        status = "soon"
        if j.get("status", "live") == "live":
            try:
                load_playbook(j["id"], root)
                status = "live"
            except PlaybookError:
                status = "soon"
        out.append((j.get("order", 99), {"id": j["id"], "title": j["title"],
                                         "description": j["description"], "status": status}))
    return [e for _, e in sorted(out, key=lambda x: (x[0], x[1]["id"]))]


def _approvals(d):
    f = d / "sources" / "approvals.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.is_file() else None


def _apply_approvals(sources, approvals, pb_id):
    """Drop rejected entries. Refuse to load while any used entry is still pending."""
    pending = set()
    for name, data in sources.items():
        for key, val in list(data.items()):
            if isinstance(val, list):
                keep = []
                for e in val:
                    sid = e.get("source_id") if isinstance(e, dict) else None
                    st = approvals.get(sid, "pending") if sid else "approved"
                    if st == "rejected":
                        continue
                    if st != "approved":
                        pending.add(sid)
                    keep.append(e)
                data[key] = keep
    if pending and not allow_pending():
        raise PlaybookError(f"{pb_id}: sources pending approval: {sorted(pending)}")
    return sorted(pending)


def _validate_disclaimer(d):
    """Safety floor: every disclaimer says Nury is an AI assistant, not a pastor or a professional, and gives no advice."""
    must = {"en": ("ai assistant", "pastor", r"\bnot an? \w+", r"\badvice\b"),
            "es": ("asistente de ia", "pastor", r"\bno (es|soy) ", r"asesoramiento|consejo")}
    for lang, needles in must.items():
        t = d.get(lang, "").lower()
        missing = [n for n in needles if not re.search(n, t)]
        if missing:
            raise PlaybookError(f"disclaimer[{lang}] is missing required wording: {missing}")


def load_playbook(playbook_id, root: Optional[Path] = None, skills_root: Optional[Path] = None) -> Playbook:
    d = (root or PLAYBOOKS_DIR) / playbook_id
    if not (d / "playbook.json").is_file():
        raise PlaybookError(f"no playbook {playbook_id!r} in {d.parent}")
    pj = json.loads((d / "playbook.json").read_text(encoding="utf-8"))
    if pj.get("status", "live") != "live":
        raise PlaybookError(f"{playbook_id!r} is coming soon and cannot run")
    _validate_disclaimer(pj["disclaimer"])
    need = ("who", "domain", "professional", "professional_kind")
    if any(k not in pj.get("boundary", {}) for k in need):
        raise PlaybookError(f"playbook.json needs boundary fields {need}")
    stages = []
    for sj in json.loads((d / "stages.json").read_text(encoding="utf-8")):
        for c in sj.get("checks", []):
            if c["name"] not in checks_lib.REGISTRY:
                raise PlaybookError(f"stage {sj['id']}: unknown check {c['name']!r}")
        specs = sj.get("sources", [])
        stages.append(Stage(
            id=sj["id"], title=sj["title"], audience=sj["audience"],
            prompt=(d / sj["prompt"]).read_text(encoding="utf-8").strip(),
            prompt_file=sj["prompt"], deps=sj.get("deps", []), sources=[s["name"] for s in specs],
            source_specs=specs, checks=sj.get("checks", []), input=sj.get("input", {"from": "intake"}),
            when=sj.get("when"),
            skills=_load_skills(sj, skills_root),
            summary=_summary(sj), scripture=bool(sj.get("scripture", False)), jev=_jev(sj),
            variants=[{"when": v["when"], "prompt": (d / v["prompt"]).read_text(encoding="utf-8").strip()}
                      for v in sj.get("variants", [])]))
    for s in stages:
        if s.scripture and not any(sp.get("dynamic") == "scripture" for sp in s.source_specs):
            raise PlaybookError(f"stage {s.id}: scripture needs a dynamic source with dynamic 'scripture'")
    if not stages or stages[0].id != "triage":
        raise PlaybookError("stage 1 of every playbook is triage")
    ids = [s.id for s in stages]
    for s in stages:
        bad = [x for x in s.deps if x not in ids[:ids.index(s.id)]]
        if bad:
            raise PlaybookError(f"stage {s.id}: deps must be earlier stages, got {bad}")
    outcomes = json.loads((d / "outcomes.json").read_text(encoding="utf-8"))
    missing = [o for o in OUTCOMES if o not in outcomes]
    if missing:
        raise PlaybookError(f"outcomes.json is missing {missing}")
    sources = {}
    for s in stages:
        for spec in s.source_specs:
            if spec.get("dynamic"):               # filled at run time (church network, official list)
                continue
            sources[spec["name"]] = json.loads((d / "sources" / spec["file"]).read_text(encoding="utf-8"))
    approvals = _approvals(d)
    pending = _apply_approvals(sources, approvals, pj["id"]) if approvals is not None else []
    pb = Playbook(pj["id"], pj["title"], pj["description"], pj["languages"],
                    pj.get("default_family_language", "es"), pj["disclaimer"], pj["draft_label"],
                    stages, outcomes, d, pj["boundary"], pj.get("extra_banned", []), sources)
    pb.pending_sources = pending
    return pb


def _jev(sj):
    from . import jev_gate
    qs = sj.get("jev", [])
    bad = [q for q in qs if q not in jev_gate.QUESTIONS]
    if bad:
        raise PlaybookError(f"stage {sj['id']}: unknown Jev question {bad}")
    return list(qs)


def _summary(sj):
    """Optional display line for a stage. Plain text only, 140 characters at most. Never used by the engine."""
    t = sj.get("summary", "")
    if t == "":
        return ""
    if not isinstance(t, str) or len(t) > 140 or re.search(r"<[^>]*>|&\w+;|&#\d+;", t):
        raise PlaybookError(f"stage {sj['id']}: summary must be plain text of 140 characters or fewer, no HTML")
    return t.strip()


def _load_skills(sj, skills_root):
    out = []
    for name in sj.get("skills", []):
        try:
            out.append(skills_lib.load_skill(name, skills_root))
        except skills_lib.SkillError as e:
            raise PlaybookError(f"stage {sj['id']}: {e}")
    return out


# ---------- prompt and source rendering ----------

class _Safe(dict):
    def __missing__(self, k):
        return ""


def _fmt(line, entry, lang):
    vals = _Safe({k: v for k, v in entry.items() if isinstance(v, str)})
    for k, v in list(vals.items()):
        vals[k + "_short"] = v.split(" (")[0].strip()
    return line.replace("{lang}", lang).format_map(vals)


def render_sources(stage, pb, lang, dynamic=None):
    """{var: text} for each source spec, built only from the vetted JSON (and the run's dynamic sources)."""
    out = {}
    for spec in stage.source_specs:
        data, lines = (dynamic or {}).get(spec["name"]) or pb.sources.get(spec["name"], {}), []
        for grp in spec["groups"]:
            items = data.get(grp["list"], [])
            lines += [_fmt(grp["line"], e, lang) for e in items]
            if not items and grp.get("empty"):
                lines.append(grp["empty"])
        out[spec["var"]] = "\n".join(lines)
    return out


def render_prompt(stage, pb, lang, state, fields, skills=None, dynamic=None):
    """Instructions text for a stage: the playbook prompt with its variables filled in."""
    prompt = stage.prompt
    for v in stage.variants:
        if when_matches(v["when"], fields):
            prompt = v["prompt"]
            break
    vars_ = {"lang_name": LANG_NAME[lang], **render_sources(stage, pb, lang, dynamic)}
    for k, v in vars_.items():
        prompt = prompt.replace("{{" + k + "}}", v)
    prompt += skills_lib.render(stage.skills if skills is None else skills, lang, pb.boundary)
    left = re.findall(r"\{\{(\w+)\}\}", prompt)
    if left:
        raise PlaybookError(f"stage {stage.id}: unfilled prompt variables {left}")
    return prompt


def build_input(stage, state):
    if stage.input.get("from") == "intake":
        return state.intake
    ctx = "\n\n".join(f"[{d.upper()} — approved text]\n{state.approved[d]}"
                      for d in stage.deps if d in state.approved)
    return stage.input.get("prefix", "") + ctx


# ---------- paths: plain field matches on triage output ----------

def parse_fields(text):
    """'LABEL: value' lines -> {'label': 'value'} (lowercase, underscores). Used for `when`."""
    fields = {}
    for m in re.finditer(r"^\W*([A-Z][A-Z _]+?)\s*:\s*(.+)$", text or "", re.M):
        fields[re.sub(r"\s+", "_", m.group(1).strip().lower())] = m.group(2).strip()
    return fields


def when_matches(cond, fields):
    """cond: {"field": "urgency", "in": ["high"]} | {"equals": "x"} | {"matches": "regex"}.
    Also {"all": [cond, ...]} and {"any": [cond, ...]}. A missing field never matches."""
    if not cond:
        return True
    if "all" in cond:
        return all(when_matches(c, fields) for c in cond["all"])
    if "any" in cond:
        return any(when_matches(c, fields) for c in cond["any"])
    val = fields.get(cond["field"].split(".")[-1])
    if val is None:
        return False
    v = val.lower()
    if "equals" in cond:
        return v == str(cond["equals"]).lower()
    if "in" in cond:
        return any(v.startswith(str(x).lower()) or v == str(x).lower() for x in cond["in"])
    if "matches" in cond:
        return re.search(cond["matches"], v, re.I) is not None
    raise PlaybookError(f"bad condition {cond}")
