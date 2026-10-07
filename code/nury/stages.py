"""Stage registry: five stages. Each = prompt + vetted source file + guardrail set.

A stage never reads the open web. Its only facts come from its source files
and from earlier approved (or edited) stage text.
"""

import json
import re
from typing import Callable
from dataclasses import dataclass, field
from pathlib import Path

from . import guardrails as g

DATA_DIR = Path(__file__).parent / "data"
LANG_NAME = {"es": "Spanish", "en": "English"}


def load_source(name):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


@dataclass
class Stage:
    id: str
    title: str
    audience: str                      # "pastor" (English) or "family" (family language)
    sources: list = field(default_factory=list)   # vetted source files in data/
    deps: list = field(default_factory=list)      # earlier stage ids it consumes
    build: Callable = None               # (state, data) -> (instructions, input)
    checks: Callable = None              # (text, state, data) -> [reasons]


def _prior(state, ids):
    parts = [f"[{i.upper()} — approved text]\n{state.approved[i]}" for i in ids if i in state.approved]
    return "\n\n".join(parts)


def _src_names(data):
    names = set()
    for e in data.get("rights", {}).get("entries", []):
        names.add(e["source"].split(" (")[0].strip())
    return names


def _norm(u):
    return g._norm_url(u)


def _allowed_urls(data):
    urls = []
    for e in data.get("rights", {}).get("entries", []):
        urls += re.findall(r"\(([a-z0-9.\-/]+)\)", e["source"])
    for e in data.get("attorneys", {}).get("national", []) + data.get("attorneys", {}).get("local", []):
        if e.get("url"):
            urls.append(e["url"])
    return urls


# ---------- 1. triage ----------
def _build_triage(state, data):
    ins = g.SYSTEM_BOUNDARY + (
        "\nTask: turn the pastor's raw intake into a structured case. Write in English for the pastor. "
        "Use exactly these labels, one per line:\n"
        "SITUATION: (1-2 factual sentences)\nPEOPLE: \nLOCATION: \nFAMILY LANGUAGE: (es or en)\n"
        "URGENCY: (high/medium/low) — one-line reason\n"
        "MISSING FACTS: exactly 3 numbered facts to ask the family\n"
        "Facts only. No advice. No prediction. Do not add facts the pastor did not give."
    )
    return ins, state.intake


def _check_triage(text, state, data):
    out = []
    for label in ("SITUATION", "PEOPLE", "LOCATION", "FAMILY LANGUAGE", "URGENCY", "MISSING FACTS"):
        if label not in text.upper():
            out.append(g.R("format", f"missing label {label}"))
    tail = text.upper().split("MISSING FACTS", 1)[-1]
    if len(re.findall(r"^\s*\d[.)]", tail, re.M)) != 3:
        out.append(g.R("format", "MISSING FACTS must list exactly 3 numbered items"))
    return out


# ---------- 2. rights brief ----------
def _build_rights(state, data):
    lang = LANG_NAME[state.language]
    key = "summary_es" if state.language == "es" else "summary_en"
    bullets = "\n".join(f"- {e['topic']}: {e[key]} (source: {e['source'].split(' (')[0]})"
                        for e in data["rights"]["entries"])
    ins = g.SYSTEM_BOUNDARY + (
        f"\nTask: write a plain-language rights brief in {lang} for the family. "
        "Use ONLY the points below. Make one bullet per point, starting with '- '. "
        "End every bullet with its source name in parentheses, for example (ACLU Know Your Rights). "
        "After the bullets, add one closing sentence that urges the family to speak with an immigration attorney. "
        "Output only the bullets and that sentence. No headings, notes to the pastor, or separators. "
        "Do not add any point that is not listed.\n\nVETTED POINTS:\n" + bullets
    )
    return ins, "Case summary for context only:\n" + _prior(state, ["triage"])


def _check_rights(text, state, data):
    out = []
    names = _src_names(data)
    lines = [l for l in text.splitlines()
             if re.match(r"\s*[-•*]\s+\w", l) and not l.strip().startswith("**")]
    if not lines:
        out.append(g.R("format", "no bullet points found"))
    for l in lines:
        if not any(n.lower() in l.lower() for n in names):
            out.append(g.R("ungrounded_claim", f"bullet without a source citation: {l.strip()[:60]!r}"))
    if not g._ATTORNEY_WORDS.search(text[-400:]):
        out.append(g.R("missing_attorney_referral", "must end by urging an attorney"))
    return out


# ---------- 3. attorney resources ----------
def _build_attorney(state, data):
    d = data["attorneys"]
    lines = [f"- NATIONAL: {e['name']}: {e['description']} — {e['url']}" for e in d["national"]]
    lines += [f"- LOCAL (church-vetted): {e['name']} ({e.get('area','')}): {e.get('phone','')} {e.get('url','')}"
              for e in d.get("local", [])]
    if not d.get("local"):
        lines.append("(No church-vetted local entries yet. Say the pastor can add them.)")
    lang = LANG_NAME[state.language]
    ins = g.SYSTEM_BOUNDARY + (
        f"\nTask: format the list below as a clean, scannable list in {lang}. National first, then local. "
        "Copy names and links exactly. Add one line on what to have ready before calling "
        "(names, dates, paperwork). Do not recommend any one attorney. Do not add entries.\n\nLIST:\n"
        + "\n".join(lines)
    )
    return ins, "Case context:\n" + _prior(state, ["triage", "rights"])


def _check_attorney(text, state, data):
    out = g.url_reasons(text, _allowed_urls(data))
    for e in data["attorneys"]["national"] + data["attorneys"].get("local", []):
        if e.get("url") and _norm(e["url"]) not in _norm(text):
            out.append(g.R("missing_vetted_entry", f"missing vetted link: {e['url']}"))
    return out


# ---------- 4. family checklist ----------
def _build_checklist(state, data):
    lang = LANG_NAME[state.language]
    key = "summary_es" if state.language == "es" else "summary_en"
    pts = "\n".join(f"- {e['topic']}: {e[key]}" for e in data["rights"]["entries"])
    ins = g.SYSTEM_BOUNDARY + (
        f"\nTask: write a tonight-only checklist in {lang}. Three sections with these exact headings in English caps "
        "(you may add the translation after a slash): DO TONIGHT, DO NOT DO, GATHER THESE DOCUMENTS. "
        "DO TONIGHT: 5-7 concrete steps. DO NOT DO: 4-5 items. GATHER THESE DOCUMENTS: IDs, paperwork, contact numbers. "
        "Base 'DO NOT DO' only on the vetted points below. General information only.\n\nVETTED POINTS:\n" + pts
    )
    return ins, "Approved context:\n" + _prior(state, ["triage", "rights", "attorney"])


def _check_checklist(text, state, data):
    up = text.upper()
    out = [g.R("format", f"missing section {h}") for h in ("DO TONIGHT", "DO NOT DO", "GATHER THESE DOCUMENTS") if h not in up]
    return out + g.url_reasons(text, _allowed_urls(data))


# ---------- 5. pastoral message ----------
def _build_pastoral(state, data):
    lang = LANG_NAME[state.language]
    ins = g.SYSTEM_BOUNDARY + (
        f"\nTask: draft a short pastoral message in {lang} for the pastor to send the family. "
        "Under 120 words. Warm, steady, hopeful. Acknowledge their fear. Say the church is with them. "
        "Say practical help is being arranged (an attorney search and a checklist). "
        "No legal claims. No promises about outcomes. Write it as words the pastor can say; do not sign it."
    )
    return ins, "Approved context:\n" + _prior(state, ["triage", "rights", "checklist"])


def _check_pastoral(text, state, data):
    n = g.word_count(text)
    return [g.R("length", f"too long: {n} words (limit 119)")] if n >= 120 else []


STAGES = [
    Stage("triage", "1. Triage", "pastor", [], [], _build_triage, _check_triage),
    Stage("rights", "2. Rights brief", "family", ["rights"], ["triage"], _build_rights, _check_rights),
    Stage("attorney", "3. Attorney resources", "family", ["attorneys"], ["triage", "rights"], _build_attorney, _check_attorney),
    Stage("checklist", "4. Family checklist", "family", ["rights"], ["triage", "rights", "attorney"], _build_checklist, _check_checklist),
    Stage("pastoral", "5. Pastoral message", "family", [], ["triage", "rights", "checklist"], _build_pastoral, _check_pastoral),
]
REGISTRY = {s.id: s for s in STAGES}
SOURCE_FILES = {"rights": "know_your_rights.json", "attorneys": "attorney_directory.json"}
