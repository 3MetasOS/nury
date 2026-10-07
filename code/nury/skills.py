"""Nury skills: small, versioned instruction modules a playbook stage includes by name.

    code/skills/<name>/SKILL.md    header (name, version) + "## EN" and "## ES" sections
    code/skills/<name>/checks.json optional list of named checks that go with the skill
    stages.json                    "skills": ["voice", "grounding"]

A skill adds rules and checks to a stage prompt. It cannot remove or override the safety floor,
the disclaimer, or a playbook's banned patterns. The loader refuses a skill that tries.
No extra model call: a skill changes the prompt, not the number of calls.
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import checks as checks_lib

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"
_CACHE = {}

# Wording that tries to override the floor. English and Spanish.
_OVERRIDE = re.compile(
    r"\b(ignore|disregard|override|bypass|skip|disable|remove|drop|omit|turn off|do not (add|include|append|show))\b[^.\n]{0,60}"
    r"\b(disclaimer|safety|guardrail|floor|rules?|checks?|banned|boundary|citations?|referral|instructions)\b"
    r"|\b(ignora|omite|salta|desactiva|elimina|quita|no (agregues|incluyas|añadas))\b[^.\n]{0,60}"
    r"\b(descargo|aviso|seguridad|reglas?|verificaci[oó]n|prohibid\w+|cita\w*)\b"
    r"|\b(you (are|may) now|new instructions|previous instructions)\b",
    re.I)
_BAD_CHECK_KEYS = {"remove", "disable", "override", "skip", "replace"}


class SkillError(Exception):
    pass


@dataclass
class Skill:
    name: str
    version: str
    summary: str
    text: dict                      # {"en": ..., "es": ...}
    checks: list = field(default_factory=list)


def _parse(name, raw):
    m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
    if not m:
        raise SkillError(f"skill {name}: missing header")
    head = dict(re.findall(r"^(\w+):\s*(.+)$", m.group(1), re.M))
    if head.get("name") != name:
        raise SkillError(f"skill {name}: header name {head.get('name')!r} does not match the folder")
    if not re.fullmatch(r"\d+\.\d+\.\d+", head.get("version", "")):
        raise SkillError(f"skill {name}: needs a version like 1.0.0")
    parts = re.split(r"^## (EN|ES)\s*$", m.group(2), flags=re.M)
    text = {parts[i].lower(): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}
    if set(text) != {"en", "es"} or not all(text.values()):
        raise SkillError(f"skill {name}: needs non-empty '## EN' and '## ES' sections")
    for lang, t in text.items():
        for hit in _OVERRIDE.finditer(t):
            before = t[max(0, hit.start() - 40):hit.start()].lower()
            if re.search(r"\b(never|not|don't|nunca|no)\b", before):   # "never drop the disclaimer" is fine
                continue
            raise SkillError(f"skill {name} [{lang}]: tries to override the safety floor ({hit.group(0)!r})")
    return head, text


def load_skill(name, root: Path = None) -> Skill:
    root = root or SKILLS_DIR
    key = (str(root), name)
    if key in _CACHE:
        return _CACHE[key]
    d = root / name
    f = d / "SKILL.md"
    if not f.is_file():
        raise SkillError(f"no skill {name!r} in {root}")
    head, text = _parse(name, f.read_text(encoding="utf-8"))
    checks = []
    cf = d / "checks.json"
    if cf.is_file():
        checks = json.loads(cf.read_text(encoding="utf-8"))
        if not isinstance(checks, list):
            raise SkillError(f"skill {name}: checks.json must be a list of named checks")
        for c in checks:
            if not isinstance(c, dict) or c.get("name") not in checks_lib.REGISTRY:
                raise SkillError(f"skill {name}: unknown check {c!r}")
            if _BAD_CHECK_KEYS & set(c):
                raise SkillError(f"skill {name}: a skill may add checks, never remove or replace them")
    sk = Skill(name, head["version"], head.get("summary", ""), text, checks)
    _CACHE[key] = sk
    return sk


def render(skills, lang, boundary):
    """Prompt text for a stage's skills, in the output language, domain words filled from the playbook."""
    if not skills:
        return ""
    out = []
    for sk in skills:
        t = sk.text["es" if lang == "es" else "en"].replace("{professional}", boundary.get("professional", "professional"))
        out.append(f"SKILL {sk.name} v{sk.version}:\n{t}")
    out.append("These skill rules add to the hard rules above. They never override the hard rules, the disclaimer, or the source citations.")
    return "\n\n" + "\n\n".join(out)
