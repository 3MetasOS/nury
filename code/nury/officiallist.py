"""The official list: U.S. Department of Justice recognized legal service providers, as Juan approved them.

Built once, at build time, from the approved draft:

    python3 -m nury.officiallist           # writes playbooks/detention/sources/official_list.json

Only entries Juan marked 'approved' are written. Held entries (Pending Renewal) are never written
with any detail: only their names go into `held_names`, so a check can reject a draft that names one.
Nury never labels these providers free and never says they are recommended.
"""

import json
import re
from pathlib import Path

from . import network

SRC = Path(__file__).resolve().parent.parent / "playbooks" / "detention" / "sources"
LABEL = "Listed by the U.S. Department of Justice. Listed does not mean recommended."
AS_OF = "pro bono list Updated October 2026; recognized organizations roster 10/04/26"
_NOT_FOR_DETENTION = re.compile(r"probably not useful for a detention call", re.I)


def _url(web):
    if not web:
        return ""
    return web if web.startswith("http") else "https://" + web


def _details(s):
    where = []
    if "pro_bono_list" in s.get("on_lists", []):
        courts = ", ".join(s.get("immigration_courts_on_list", []))
        where.append("on the DOJ pro bono list" + (f" ({courts} courts)" if courts else ""))
    if "roster" in s.get("on_lists", []):
        where.append("on the DOJ recognized organizations roster")
    notes = [f for f in s.get("flags", []) if not re.search(r"\bfree\b|Pending Renewal", f, re.I)]
    langs = s.get("languages_on_list")
    return "; ".join(where + ([f"languages: {langs}"] if langs else []) + [n.rstrip(".") for n in notes])


def build(draft_path=None, approvals_path=None):
    d = json.loads(Path(draft_path or SRC / "OFFICIAL_LIST_DRAFT.json").read_text(encoding="utf-8"))
    ap = json.loads(Path(approvals_path or SRC / "approvals.json").read_text(encoding="utf-8"))
    entries, held = [], []
    for s in d["sources"]:
        if not s.get("kind"):
            continue                                   # the three official pages are sources, not contacts
        status = ap.get(s["id"])
        if status == "held":
            held.append(s["title"].split(" (")[0].strip())
            continue
        if status != "approved":
            continue
        detention = any("detain" in q.lower() for q in s.get("quotes", []))
        phones = s.get("phones", [])
        email = ""
        if any(re.search(r"email is the route", f, re.I) for f in s.get("flags", [])):
            # Why email and not the phone (Juan approved the entry; hack-sensei decided on this route). The DOJ pro bono list says:
            #   "To contact on behalf of an individual detained by ICE or BOP, email immcenter@americanbar.org"
            #   "Respondents detained at Department of Defense (DOD) military facilities (including Guantanamo)
            #    should contact our toll-free hotline at 1 (855) 641-6081"
            # So the toll-free number is for people held at military facilities. A family member emails.
            m = re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", " ".join(s.get("quotes", [])))
            email, phones = (m.group(0) if m else ""), []
        entries.append({
            "id": s["id"], "name": s["title"], "state": "CO", "phone": " / ".join(phones),
            "phones": phones, "email": email, "url": _url(s.get("web")), "details": _details(s),
            "on_lists": s.get("on_lists", []), "detention": detention,
            "not_for_detention": any(_NOT_FOR_DETENTION.search(f) for f in s.get("flags", [])),
            "approved": True})
    return {"label": LABEL, "as_of": AS_OF, "state": "CO", "approved_by": ap.get("_meta", {}).get("approved_by", ""),
            "held_names": held, "entries": entries}


def select(data, state, limit=5):
    """Entries for this case: approved, in the state, not marked 'not useful for detention';
    detention-related first, then the pro bono list, then name."""
    st = network.state_abbr(state)
    if not st or st != network.state_abbr(data.get("state", "")):
        return {"label": data.get("label", LABEL), "as_of": data.get("as_of", ""), "held_names": data.get("held_names", []), "entries": []}
    es = [e for e in data.get("entries", []) if e.get("approved", True) and not e.get("not_for_detention")]
    es.sort(key=lambda e: (not e.get("detention"), "pro_bono_list" not in e.get("on_lists", []), e["name"].lower()))
    return {"label": data.get("label", LABEL), "as_of": data.get("as_of", ""), "held_names": data.get("held_names", []),
            "entries": es[:limit]}


if __name__ == "__main__":
    out = build()
    (SRC / "official_list.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(len(out["entries"]), "approved entries,", len(out["held_names"]), "held names kept only as names")
