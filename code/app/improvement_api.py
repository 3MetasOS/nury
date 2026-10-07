"""GET /api/improvement: the reviewer's view of the learning loop. Reads the latest learning report and the candidate review files.
Nothing here changes Nury. It returns no feedback line, no draft and no name: only the report's aggregate tables and the candidates' metadata.
Until a real report exists it shows the SYNTHETIC example and says so."""
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from nury import log

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "tools"))
sys.path.insert(0, str(ROOT / "code"))

REAL_REPORT = ROOT / "documents" / "product" / "LEARNING_REPORT.md"
EXAMPLE_DIR = ROOT / "documents" / "product" / "learning_example"
REAL_CANDIDATES = ROOT / "candidates"


def _iso(p):
    return datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat(timespec="seconds")


def _tables(md):
    """{heading: {header:[...], rows:[[...]]}} for every pipe table under a '## ' heading."""
    out, head, cur = {}, None, None
    for line in md.splitlines():
        if line.startswith("## "):
            head, cur = line[3:].strip(), None
        elif line.startswith("|") and head:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cur is None:
                cur = {"header": cells, "rows": []}
                out[head] = cur
            elif not set("".join(cells)) <= set("-: "):
                cur["rows"].append(cells)
        else:
            cur = None if not line.startswith("|") else cur
    return out


def _test_view(rel, base):
    if not rel:
        return None
    f = (base / rel) if not Path(rel).is_absolute() else Path(rel)
    try:
        f = f.resolve()
        if ROOT not in f.parents or not f.is_file():
            return None
        t = f.read_text(encoding="utf-8")
    except Exception:
        return None
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in t.splitlines() if l.startswith("|") and not set(l) <= set("|-: ")]
    gate = next((l.split(":", 1)[1].strip() for l in t.splitlines() if l.startswith("NO-REGRESSION GATE")), None)
    return {"table": rows, "gate": gate, "mock": "MOCK AGENT" in t}


def view():
    import candidates as C
    synthetic_example = not REAL_REPORT.is_file()
    report_path = EXAMPLE_DIR / "LEARNING_REPORT_EXAMPLE.md" if synthetic_example else REAL_REPORT
    cand_dir = REAL_CANDIDATES if any(REAL_CANDIDATES.glob("c-*.md")) else EXAMPLE_DIR / "candidates"
    d = {"source": "synthetic example (no real pastor has used Nury)" if synthetic_example else "learning report", "synthetic": synthetic_example,
         "report": None, "candidates": [], "feedback_mode": "off"}
    try:
        from nury import feedback
        d["feedback_mode"] = feedback.mode()
    except Exception as e:
        log.note("improvement_api.feedback_mode", e)
    if report_path.is_file():
        md = report_path.read_text(encoding="utf-8")
        tb = _tables(md)
        d["report"] = {"updated": _iso(report_path), "tables": [{"title": k, **v} for k, v in tb.items() if not k.startswith("Candidate")]}
    for f in sorted(cand_dir.glob("c-*.md")):
        try:
            meta, body, _changes, _w = C.load(f)
        except Exception as e:
            log.note("improvement_api.candidate_load", e)
            continue
        title = next((l[2:].strip() for l in body.splitlines() if l.startswith("# ")), meta.get("id"))
        why = ""
        m = re.search(r"## Why\s+(.*?)(?=\n## |\Z)", body, re.S)
        if m:
            why = " ".join(m.group(1).split())[:600]
        ev = meta.get("evidence") or {}
        d["candidates"].append({"id": meta.get("id"), "title": title, "type": meta.get("type"), "status": meta.get("status"), "created": meta.get("created"),
                                "synthetic": bool(meta.get("synthetic")), "evidence": {k: v for k, v in ev.items() if isinstance(v, (int, float, str)) and k not in ("text",)},
                                "why": why, "approved": bool(meta.get("approved_by")), "approved_by": meta.get("approved_by"), "approved_date": meta.get("approved_date"),
                                "test": _test_view(meta.get("test_result"), ROOT)})
    return d
