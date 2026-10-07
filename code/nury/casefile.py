"""Case file writer and next-steps map.

After the pastor approves a package, save it as a local folder of linked markdown pages
plus one SVG map. Built with no model call, from approved text and the audit log only.

    cases/<id>/
      index.md          one screen: summary, status, next step, links
      01-<stage>.md ... one page per stage, as approved or edited by the pastor
      people.md         from the triage PEOPLE field
      documents.md      from the checklist's documents / bring list
      timeline.md       gates in time order
      log.md            each gate, action, time; edits flagged; skills applied; categories only
      nextsteps.svg     lanes: Tonight, This week, Questions still open, Who to call
      case.json         small manifest

Rules: local only, approved content only, no rejected draft text anywhere (only categories),
no keys, steps and questions only (no outcomes), links in the map only from vetted sources.
"""

import html
import json
import os
import re
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from . import guardrails as g
from .engine import get_playbook

DEFAULT_ROOT = "cases"
OK_STATUS = ("approved", "edited")
SECRET_ENV = ("GLOO_API_KEY", "JEV_API_KEY")


class CaseError(Exception):
    pass


# ---------- text helpers ----------

_LABEL = re.compile(r"^\s*([A-Z][A-Z ]{2,}):\s*(.*)$")


def _clean(line):
    line = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", line.strip())
    return re.sub(r"[*_`#]+", "", line).strip()


def triage_sections(text):
    """{'PEOPLE': [lines], ...} from the triage 'LABEL: value' structure. Stops at the disclaimer."""
    out, cur = {}, None
    for line in text.splitlines():
        m = _LABEL.match(line)
        if m and m.group(1).strip() in ("SITUATION", "PEOPLE", "LOCATION", "FAMILY LANGUAGE", "URGENCY", "MISSING FACTS"):
            cur = m.group(1).strip()
            out[cur] = [m.group(2).strip()] if m.group(2).strip() else []
        elif cur and line.strip():
            if line.strip().startswith(("Nury is", "Nury es")):
                cur = None
            else:
                out[cur].append(line.strip())
    return {k: [_clean(x) for x in v if _clean(x)] for k, v in out.items()}


def checklist_sections(text):
    """{'DO TONIGHT': [items], 'DO NOT DO': [...], 'GATHER...': [...]} by heading lines."""
    out, cur = {}, None
    for line in text.splitlines():
        s = line.strip()
        if not s or set(s) <= set("-—_* "):
            continue
        if s.startswith(("Nury is", "Nury es")):
            cur = None
            continue
        m = re.match(r"^(?:#+\s*)?\**\s*(DO TONIGHT|DO NOT DO|GATHER THESE DOCUMENTS|WHAT TO BRING AND ASK)\b", s)
        if m:
            cur = m.group(1)
            out[cur] = []
        elif cur:
            c = _clean(s)
            if c and not c.endswith(":"):
                out[cur].append(c)
            elif c:
                out[cur].append(c)
    return out


def _short(s, n=170):
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1].rsplit(" ", 1)[0] + "…"


# ---------- who to call: vetted entries found in the approved resources text ----------

def _resource_stage_id(pb):
    for s in pb.stages:
        for spec in s.source_specs:
            if "national" in pb.sources.get(spec["name"], {}):
                return s.id, spec["name"]
    return None, None


def _digits(s):
    return re.sub(r"\D", "", s)


def who_to_call(pb, state):
    """[{name, phone, url}] for vetted entries whose link or phone appears in the approved resources text."""
    sid, src = _resource_stage_id(pb)
    if not sid or sid not in state.approved:
        return []
    text = state.approved[sid]
    norm = g._norm_url
    out = []
    data = pb.sources[src]
    for e in data.get("national", []) + data.get("local", []):
        url, phone = e.get("url", ""), e.get("phone", "")
        hit = (url and norm(url) in norm(text)) or (phone and len(_digits(phone)) >= 3 and re.search(r"(?<!\d)" + re.escape(phone) + r"(?!\d)", text))
        if hit and (url or phone):
            out.append({"name": e["name"], "phone": phone, "url": url})
    return out


# ---------- the map ----------

W, PAD, CHARS = 400, 16, 46


def _wrap(text, n=CHARS):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) > n:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines or [""]


def lanes_for(pb, state):
    tri = triage_sections(state.approved.get("triage", ""))
    chk = checklist_sections(state.approved.get("checklist", ""))
    tonight = chk.get("DO TONIGHT", [])
    week = chk.get("GATHER THESE DOCUMENTS", []) or chk.get("WHAT TO BRING AND ASK", [])
    questions = tri.get("MISSING FACTS", [])
    calls = [f"{c['name']}" + (f": {c['phone']}" if c["phone"] else "") + (f"  {c['url']}" if c["url"] else "") for c in who_to_call(pb, state)]
    return [("Tonight", tonight), ("This week", week), ("Questions still open", questions), ("Who to call", calls)]


def nextsteps_svg(pb, state, case_title="Next steps"):
    lanes = lanes_for(pb, state)
    y, parts = 82, []
    for name, items in lanes:
        parts.append(f'<text class="lane" x="{PAD}" y="{y}">{html.escape(name)}</text>')
        y += 10
        if not items:
            parts.append(f'<text class="mut" x="{PAD + 12}" y="{y + 14}">Nothing listed.</text>')
            y += 30
        for it in items[:9]:
            lines = _wrap(_short(it))[:5]
            parts.append(f'<circle class="dot" cx="{PAD + 5}" cy="{y + 9}" r="2.5"/>')
            for j, ln in enumerate(lines):
                parts.append(f'<text class="t" x="{PAD + 16}" y="{y + 14 + j * 16}">{html.escape(ln)}</text>')
            y += 8 + 16 * len(lines)
        y += 22
    h = y
    style = ("<style>.bg{fill:#0d1015}.t{font:500 12.5px -apple-system,Segoe UI,Roboto,sans-serif;fill:#ece7dc}"
             ".mut{font:400 12.5px -apple-system,Segoe UI,Roboto,sans-serif;fill:#a79f8d}"
             ".lane{font:700 14px Georgia,serif;fill:#e8a33d}.dot{fill:#e8a33d}"
             ".ttl{font:600 16px Georgia,serif;fill:#ece7dc}.rule{stroke:rgba(236,231,220,.14);stroke-width:1}</style>")
    head = (f'<text class="ttl" x="{PAD}" y="28">{html.escape(case_title)}</text>'
            f'<text class="mut" x="{PAD}" y="44">Steps and questions from the approved package.</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" role="img" aria-label="{html.escape(case_title)}">'
            f'<title>{html.escape(case_title)}</title>{style}<rect class="bg" width="{W}" height="{h}"/>{head}{"".join(parts)}</svg>')


# ---------- pages ----------

def _ts(e):
    return e["ts"].replace("T", " ").replace("+00:00", " UTC")


def _stage_pages(pb, state):
    pages = {}
    stages = [s for s in pb.stages if s.id in state.approved]
    for i, s in enumerate(stages, 1):
        r = state.results.get(s.id)
        edited = bool(r and r.status == "edited")
        prev = f"[Previous]({i - 1:02d}-{stages[i - 2].id}.md) · " if i > 1 else ""
        nxt = f" · [Next]({i + 1:02d}-{stages[i].id}.md)" if i < len(stages) else ""
        body = [f"# {s.title}", "", f"Status: {'edited by the pastor' if edited else 'approved by the pastor'}",
                "", state.approved[s.id].strip(), "", "---", f"{prev}[Index](index.md){nxt}", ""]
        pages[f"{i:02d}-{s.id}.md"] = "\n".join(body)
    return pages, stages


def _people_md(state):
    tri = triage_sections(state.approved.get("triage", ""))
    people = tri.get("PEOPLE", [])
    lines = ["# People", "", "From the approved triage.", ""] + ([f"- {p}" for p in people] or ["- Not stated."])
    for k in ("LOCATION", "FAMILY LANGUAGE"):
        if tri.get(k):
            lines += ["", f"{k.title()}: {' '.join(tri[k])}"]
    return "\n".join(lines + ["", "[Index](index.md)", ""])


def _documents_md(state):
    chk = checklist_sections(state.approved.get("checklist", ""))
    key = "GATHER THESE DOCUMENTS" if "GATHER THESE DOCUMENTS" in chk else "WHAT TO BRING AND ASK"
    items = chk.get(key, [])
    lines = ["# Documents", "", f"From the approved checklist ({key.lower()}). Tick them off on paper.", ""]
    lines += [f"- [ ] {x}" for x in items] or ["- Nothing listed."]
    return "\n".join(lines + ["", "[Index](index.md)", ""])


def _timeline_md(audit):
    ev = audit.events
    rows = []
    if ev:
        rows.append(f"- {_ts(ev[0])}  Case opened")
    for e in ev:
        if e["kind"] == "gate":
            rows.append(f"- {_ts(e)}  {e['stage']}: pastor chose {e['action']}")
        elif e["kind"] == "outcome":
            rows.append(f"- {_ts(e)}  Outcome: {e['outcome']}")
    return "\n".join(["# Timeline", ""] + rows + ["", "[Index](index.md)", ""])


def _log_md(audit):
    """Gates, edits, skills, rejection categories. Never draft text, never reason text."""
    rows = []
    for e in audit.events:
        k = e["kind"]
        if k == "gate":
            rows.append(f"- {_ts(e)}  gate  stage={e['stage']}  action={e['action']}")
        elif k == "edit_check":
            cats = sorted({(w.get('category') if isinstance(w, dict) else 'violation') for w in e.get("warnings", [])})
            rows.append(f"- {_ts(e)}  EDITED by the pastor  stage={e['stage']}  warnings={cats or 'none'}")
        elif k == "skill_applied":
            rows.append(f"- {_ts(e)}  skill  {e['name']} v{e['version']}  stage={e['stage']}")
        elif k == "draft_rejected":
            rows.append(f"- {_ts(e)}  draft rejected (not saved)  stage={e['stage']}  attempt={e['attempt']}  categories={e.get('reason_categories', [])}")
        elif k == "escalated":
            rows.append(f"- {_ts(e)}  escalated  stage={e['stage']}  categories={sorted(set(e.get('reason_categories', [])))}")
        elif k == "outcome":
            rows.append(f"- {_ts(e)}  outcome  {e['outcome']}")
    return "\n".join(["# Log", "", "Each gate, edit, skill, and rejected draft (categories only).", ""] + rows + ["", "[Index](index.md)", ""])


def _index_md(pb, state, case_id, created, stages, svg_name="nextsteps.svg"):
    tri = triage_sections(state.approved.get("triage", ""))
    chk = checklist_sections(state.approved.get("checklist", ""))
    edited = [s.title for s in stages if (state.results.get(s.id) and state.results[s.id].status == "edited")]
    status = "Package complete" + (f", edited by the pastor: {', '.join(edited)}" if edited else "")
    nxt = (chk.get("DO TONIGHT") or ["See the checklist."])[0]
    lines = [f"# {pb.title}", "", f"Case {case_id}  ·  saved {created}  ·  {pb.id}", "",
             f"Status: {status}", "", f"Situation: {' '.join(tri.get('SITUATION', [])) or 'See triage.'}", "",
             f"Next step: {nxt}", "", f"![Next-steps map]({svg_name})", "", "## Pages", ""]
    for i, s in enumerate(stages, 1):
        lines.append(f"- [{s.title}]({i:02d}-{s.id}.md)")
    lines += ["- [People](people.md)", "- [Documents](documents.md)", "- [Timeline](timeline.md)", "- [Log](log.md)",
              f"- [Next-steps map]({svg_name})", "", "---",
              pb.disclaimer["en"], "", "Nothing here is sent anywhere. The pastor shares it.", ""]
    return "\n".join(lines)


# ---------- guards ----------

def _guard(files, state, audit, results_attempts=True):
    blob = "\n".join(files.values())
    rejected = [e["draft"] for e in audit.events if e["kind"] == "draft_rejected" and e.get("draft")]
    if results_attempts:
        for r in state.results.values():
            for a in getattr(r, "attempts", []):
                if a.get("violations") and a.get("text"):
                    rejected.append(a["text"])
    for t in rejected:
        probe = t.strip()
        if len(probe) >= 20 and probe in blob:
            raise CaseError("a rejected draft would be written into the case file; refusing")
    for name in SECRET_ENV:
        v = os.environ.get(name, "")
        if len(v) >= 8 and v in blob:
            raise CaseError(f"{name} value found in case content; refusing")
    if re.search(r"\b(GLOO|JEV)_API_KEY\s*=", blob):
        raise CaseError("key assignment found in case content; refusing")


def _check_saveable(pb, state):
    missing, bad = [], []
    for s in pb.stages:
        r = state.results.get(s.id)
        if r is None:
            missing.append(s.id)
        elif r.status == "skipped":
            continue
        elif r.status not in OK_STATUS or s.id not in state.approved:
            bad.append(f"{s.id}={r.status}")
    if missing or bad:
        raise CaseError(f"cannot save: every stage must be approved or edited (missing {missing}, not approved {bad})")


# ---------- public API ----------

def save_case(state, audit, playbook=None, root=DEFAULT_ROOT, case_id: Optional[str] = None) -> dict:
    """Write cases/<id>/. Returns {id, path, files}. Refuses unless every stage is approved or edited."""
    pb = get_playbook(playbook)
    _check_saveable(pb, state)
    now = datetime.now(timezone.utc)
    cid = case_id or f"{pb.id}-{now:%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:4]}"
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,80}", cid):
        raise CaseError("bad case id")
    created = f"{now:%Y-%m-%d %H:%M} UTC"
    pages, stages = _stage_pages(pb, state)
    svg = nextsteps_svg(pb, state, pb.title)
    files = {"index.md": _index_md(pb, state, cid, created, stages), **pages,
             "people.md": _people_md(state), "documents.md": _documents_md(state),
             "timeline.md": _timeline_md(audit), "log.md": _log_md(audit), "nextsteps.svg": svg}
    manifest = {"id": cid, "playbook": pb.id, "title": pb.title, "created": created, "language": state.language,
                "status": "complete", "edited": [s.id for s in stages if state.results.get(s.id) and state.results[s.id].status == "edited"],
                "files": sorted(list(files) + ["case.json"])}
    files_all = dict(files)
    _guard(files_all, state, audit)
    d = Path(root) / cid
    if d.exists():
        raise CaseError(f"case {cid} already exists")
    d.mkdir(parents=True)
    for name, text in files.items():
        (d / name).write_text(text, encoding="utf-8")
    (d / "case.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"id": cid, "path": str(d), "files": manifest["files"]}


def list_cases(root=DEFAULT_ROOT):
    """[{id, playbook, title, created, status, path}] newest first."""
    out = []
    r = Path(root)
    if not r.is_dir():
        return out
    for d in r.iterdir():
        f = d / "case.json"
        if f.is_file():
            m = json.loads(f.read_text(encoding="utf-8"))
            out.append({"id": m["id"], "playbook": m["playbook"], "title": m["title"], "created": m["created"],
                        "status": m["status"], "path": str(d)})
    return sorted(out, key=lambda c: c["created"], reverse=True)


def _case_dir(case_id, root):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,80}", case_id or ""):
        raise CaseError("bad case id")
    d = Path(root) / case_id
    if not (d / "case.json").is_file():
        raise CaseError(f"no case {case_id!r}")
    return d


def load_case(case_id, root=DEFAULT_ROOT) -> dict:
    """{meta, pages: {name: text}, svg}."""
    d = _case_dir(case_id, root)
    meta = json.loads((d / "case.json").read_text(encoding="utf-8"))
    pages = {p.name: p.read_text(encoding="utf-8") for p in sorted(d.glob("*.md"))}
    return {"meta": meta, "pages": pages, "svg": (d / "nextsteps.svg").read_text(encoding="utf-8")}


def export_zip(case_id, root=DEFAULT_ROOT, dest=None) -> str:
    """Zip the case folder. Returns the zip path (default: <root>/<id>.zip)."""
    d = _case_dir(case_id, root)
    dest = Path(dest) if dest else Path(root) / f"{case_id}.zip"
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(d.iterdir()):
            if p.is_file():
                z.write(p, f"{case_id}/{p.name}")
    return str(dest)
