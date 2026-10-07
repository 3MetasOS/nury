"""The church network: contacts the PASTOR has vetted. Saved by the app in network/ on the server that runs it (gitignored like cases/). There is no sign-in yet, so everyone who can reach the app shares one network.

Nury lists these first, under "People our church has worked with", labeled as the church's own.
It never endorses, ranks, or invents a contact. It never alters an entry: names, phones and links
reach the family exactly as the pastor saved them.

    network/network.json          {"entries": [...]}   the pastor's real network (never committed)
    network_demo/DEMO_NETWORK_FAKE.json                 fictional contacts for demos and evals;
                                                        loaded only when NURY_DEMO_NETWORK=1
Entry fields: id, name, kind, services, languages, city, state, phone, url, note, last_used, tags,
              nationwide (optional). The pastor's `note` stays on the pastor's screen. It is never put in a prompt.
"""

import json
import os
import re
import uuid
from datetime import date
from pathlib import Path
from typing import Optional

KINDS = ("pro_bono_immigration_attorney", "legal_aid", "medicare_medicaid_help", "social_services", "interpreter", "other")
FIELDS = ("id", "name", "kind", "services", "languages", "city", "state", "phone", "url", "note", "last_used", "tags", "nationwide")
DEFAULT_ROOT = "network"
DEMO_FILE = Path(__file__).resolve().parent.parent / "network_demo" / "DEMO_NETWORK_FAKE.json"

STATES = {"alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA", "colorado": "CO",
          "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
          "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS", "kentucky": "KY", "louisiana": "LA",
          "maine": "ME", "maryland": "MD", "massachusetts": "MA", "michigan": "MI", "minnesota": "MN",
          "mississippi": "MS", "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
          "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY", "north carolina": "NC",
          "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
          "rhode island": "RI", "south carolina": "SC", "south dakota": "SD", "tennessee": "TN", "texas": "TX",
          "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
          "wisconsin": "WI", "wyoming": "WY", "district of columbia": "DC"}
_ABBR = set(STATES.values())
_PHONE = re.compile(r"^[\d\s().+\-]{7,25}$")


class NetworkError(Exception):
    pass


def _norm(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", s or "") if unicodedata.category(c) != "Mn").casefold().strip()


def state_abbr(s):
    """'Colorado' -> 'CO', 'co' -> 'CO', '' -> ''."""
    s = (s or "").strip()
    if s.upper() in _ABBR:
        return s.upper()
    return STATES.get(_norm(s), "")


def parse_location(text):
    """(city, state_abbr) from a triage LOCATION value such as 'Aurora, Colorado' or 'Mesa, AZ'."""
    text = text or ""
    low = _norm(text)
    st = ""
    for name in sorted(STATES, key=len, reverse=True):
        if re.search(r"(?<!\w)" + re.escape(name) + r"(?!\w)", low):
            st = STATES[name]
            break
    if not st:
        m = re.search(r",\s*([A-Z]{2})\b", text)
        if m and m.group(1) in _ABBR:
            st = m.group(1)
    city = ""
    m = re.match(r"\s*([^,;(]+?)\s*(?:,|\(|;|$)", text)
    if m and _norm(m.group(1)) not in STATES and m.group(1).strip().upper() not in _ABBR:
        city = m.group(1).strip()
    return city, st


def validate(entry):
    """Returns the cleaned entry or raises NetworkError. Never invents data."""
    e = {k: entry.get(k) for k in FIELDS if k in entry}
    name = (e.get("name") or "").strip()
    if not name:
        raise NetworkError("name is required")
    kind = e.get("kind") or "other"
    if kind not in KINDS:
        raise NetworkError(f"kind must be one of {KINDS}")
    langs = [str(x).lower() for x in (e.get("languages") or [])]
    if any(l not in ("es", "en") for l in langs):
        raise NetworkError("languages must be es or en")
    st = state_abbr(e.get("state") or "")
    if (e.get("state") or "") and not st:
        raise NetworkError("state must be a US state name or two-letter code")
    phone = (e.get("phone") or "").strip()
    if phone and not _PHONE.match(phone):
        raise NetworkError("phone looks wrong")
    url = (e.get("url") or "").strip()
    if url and not re.match(r"^https?://[^\s]+$", url):
        raise NetworkError("url must start with http:// or https://")
    if not phone and not url:
        raise NetworkError("add a phone or a link so the family can reach the contact")
    lu = (e.get("last_used") or "").strip()
    if lu and not re.match(r"^\d{4}-\d{2}-\d{2}$", lu):
        raise NetworkError("last_used must look like 2026-10-07")
    return {"id": e.get("id") or f"n-{uuid.uuid4().hex[:8]}", "name": name, "kind": kind,
            "services": (e.get("services") or "").strip()[:200], "languages": langs,
            "city": (e.get("city") or "").strip(), "state": st, "phone": phone, "url": url,
            "note": (e.get("note") or "").strip()[:500], "last_used": lu,
            "tags": [str(t).strip() for t in (e.get("tags") or []) if str(t).strip()],
            "nationwide": bool(e.get("nationwide"))}


class Network:
    """Read and write the pastor's network. One JSON file; a write replaces it whole."""

    def __init__(self, root=DEFAULT_ROOT, demo: Optional[bool] = None):
        self.demo = demo_enabled(demo)
        self.path = DEMO_FILE if self.demo else Path(root) / "network.json"
        self.fictional = self.demo

    @property
    def home(self):
        """The church's own city and state. Used when the case does not say where the family is:
        the pastor's families are mostly local. ('', '') if the pastor has not set it."""
        if not self.path.is_file():
            return ("", "")
        h = json.loads(self.path.read_text(encoding="utf-8")).get("home") or {}
        return ((h.get("city") or "").strip(), state_abbr(h.get("state") or ""))

    def set_home(self, city, state):
        st = state_abbr(state)
        if not st:
            raise NetworkError("state must be a US state name or two-letter code")
        items = self._read()
        self._write(items, {"city": (city or "").strip(), "state": st})

    def _read(self):
        if not self.path.is_file():
            return []
        j = json.loads(self.path.read_text(encoding="utf-8"))
        return [validate(e) for e in j.get("entries", [])]

    def _write(self, entries, home=None):
        if self.demo:
            raise NetworkError("the fictional demo network is read only")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        h = home or ({"city": self.home[0], "state": self.home[1]} if self.home[1] else None)
        data = ({"home": h} if h else {}) | {"entries": entries}
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def list(self):
        return self._read()

    def get(self, entry_id):
        for e in self._read():
            if e["id"] == entry_id:
                return e
        raise NetworkError(f"no entry {entry_id!r}")

    def add(self, entry):
        e = validate(entry)
        items = self._read()
        if any(x["id"] == e["id"] for x in items):
            raise NetworkError(f"id {e['id']!r} already exists")
        self._write(items + [e])
        return e

    def update(self, entry_id, fields):
        items = self._read()
        for i, x in enumerate(items):
            if x["id"] == entry_id:
                items[i] = validate({**x, **fields, "id": entry_id})
                self._write(items)
                return items[i]
        raise NetworkError(f"no entry {entry_id!r}")

    def delete(self, entry_id):
        items = self._read()
        keep = [x for x in items if x["id"] != entry_id]
        if len(keep) == len(items):
            raise NetworkError(f"no entry {entry_id!r}")
        self._write(keep)

    def mark_used(self, entry_id, when: Optional[str] = None):
        return self.update(entry_id, {"last_used": when or date.today().isoformat()})

    def export_json(self, dest):
        Path(dest).write_text(json.dumps({"entries": self._read()}, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(dest)

    def import_json(self, src, merge=True):
        """Validates every entry first; one bad entry refuses the whole import. Returns the count added."""
        j = json.loads(Path(src).read_text(encoding="utf-8"))
        if j.get("fictional"):
            raise NetworkError("refusing to import fictional demo contacts into a real network")
        new = [validate(e) for e in j.get("entries", [])]
        have = self._read() if merge else []
        ids = {x["id"] for x in have}
        add = [e for e in new if e["id"] not in ids]
        self._write(have + add)
        return len(add)


def demo_enabled(flag=None):
    if flag is not None:
        return bool(flag)
    return os.environ.get("NURY_DEMO_NETWORK") == "1"


def load_network(root=DEFAULT_ROOT, demo: Optional[bool] = None):
    return Network(root, demo)


# ---------- matching: deterministic, no model ----------

def match(entries, state="", city="", language="", kinds=None, limit=5):
    """Entries that fit the case, best fit first. State and language must fit when known.
    With no known state only nationwide entries are listed (a local contact in the wrong place does not help)."""
    st = state_abbr(state)
    out = []
    for e in entries:
        if kinds and e["kind"] not in kinds:
            continue
        if language and e["languages"] and language not in e["languages"]:
            continue
        local = bool(st) and e["state"] == st
        if not (local or e["nationwide"]):
            continue
        score = (2 if city and _norm(e["city"]) == _norm(city) else 0) + (1 if local else 0)
        out.append((score, e["last_used"] or "", e))
    out.sort(key=lambda t: (-t[0], t[1] == "", _neg(t[1]), t[2]["name"].lower()))
    return [e for _, _, e in out[:limit]]


def _neg(s):
    return tuple(-ord(c) for c in s)


def source_for(spec, state, fields, lang, root=DEFAULT_ROOT):
    """The dynamic 'church_network' source for one stage: {'entries': [...], 'fictional': bool}.
    Only the fields that reach a prompt (name, services, phone, url). The pastor's note stays in the app and is never put in a prompt."""
    net = load_network(root)
    city, st = parse_location(fields.get("location", ""))
    hc, hs = net.home
    if not st and hs:                      # the case does not say which state: use the church's own
        st, city = hs, city or hc
    got = match(net.list(), st, city, lang, spec.get("kinds"), spec.get("limit", 5))
    return {"fictional": net.fictional,
            "entries": [{"id": e["id"], "name": e["name"], "services": e["services"], "phone": e["phone"],
                         "url": e["url"], "kind": e["kind"], "city": e["city"], "state": e["state"]} for e in got]}


def literals(entries):
    """Phones, links, emails of entries: the privacy layer must not tokenize or break these."""
    out = []
    for e in entries:
        out += [x for x in (e.get("phone"), e.get("url")) if x]
        out += [x for x in e.get("phones", []) if x]
    return out
