"""Scripture for the pastoral message. The model picks a verse id. The engine inserts the exact text.

The model never writes Scripture. It returns three labelled parts:

    VERSE: <an id from the approved list, or NONE>
    WHY: <at most two short sentences on why this verse may matter to this family>
    MESSAGE: <the pastoral message>

The engine checks the id, then builds the draft: the message, the verse block copied
from the vetted bank, and the why-lines. The verse block is quoted source text, so the
wording checks run on Nury's own sentences only. A separate check proves the block
equals the source verbatim.

The bank is data: playbooks/<id>/sources/scripture.json plus the church's own file
network/scripture.json. A verse ships only when its approval is "approved".
"""

import json
import re
from pathlib import Path
from typing import Optional

from . import guardrails as g

DEFAULT_CAP = 52          # words in a verse block (text only)
CHURCH_FILE = "scripture.json"
SCRIPTURE_NOTE = "The verse is Scripture, quoted exactly. The rest is a draft; edit it."
BLOCK_RE = re.compile(r"«(?P<text>.*?)»[ \t]*\n— (?P<ref>[^\n]+)", re.S)


class ScriptureError(Exception):
    pass


def _words(t):
    return len(t.split())


def _check_verse(v, cap, church):
    where = f"verse {v.get('id', '?')!r}"
    for k in ("id", "themes"):
        if not v.get(k):
            raise ScriptureError(f"{where}: missing {k}")
    langs = [lg for lg in ("es", "en") if v.get(f"text_{lg}") and v.get(f"reference_{lg}")]
    if not langs:
        raise ScriptureError(f"{where}: needs a reference and exact text in at least one language")
    if church:
        if not str(v["id"]).startswith("church-"):
            raise ScriptureError(f"{where}: a church verse id starts with 'church-'")
        if not v.get("source_url") or not v.get("license"):
            raise ScriptureError(f"{where}: a church verse needs source_url and license")
        for lg in langs:
            if not v.get(f"translation_{lg}"):
                raise ScriptureError(f"{where}: needs translation_{lg}")
    else:
        for lg in langs:
            if not v.get(f"source_url_{lg}"):
                raise ScriptureError(f"{where}: needs source_url_{lg}")
    for lg in langs:
        if _words(v[f"text_{lg}"]) > cap:
            raise ScriptureError(f"{where}: text_{lg} is over the {cap}-word cap")
    return langs


def load_bank(pb_dir: Path, church_root: Optional[str] = None, church: bool = True) -> dict:
    """{"cap", "verses": [verse + "translation_es/en" + "origin"]}. Only approved verses.

    The playbook file lists every verse. approvals.json decides which ship: only "approved".
    A pending or rejected verse is left out, so nothing ships unapproved.
    The church file is the pastor's own list. It is read only when `church` is True."""
    f = Path(pb_dir) / "sources" / "scripture.json"
    if not f.is_file():
        return {"cap": DEFAULT_CAP, "verses": []}
    d = json.loads(f.read_text(encoding="utf-8"))
    if d.get("tradition", "none") != "none":
        raise ScriptureError("tradition other than 'none' is not built")
    cap = int(d.get("max_block_words", DEFAULT_CAP))
    af = Path(pb_dir) / "sources" / "approvals.json"
    approvals = json.loads(af.read_text(encoding="utf-8")) if af.is_file() else {}
    tr = d.get("translations", {})
    out = []
    for v in d.get("verses", []):
        _check_verse(v, cap, church=False)
        if approvals.get(v.get("source_id")) != "approved":
            continue
        v = dict(v, origin="playbook", translation_es=tr.get("es", {}).get("name", ""),
                 translation_en=tr.get("en", {}).get("name", ""))
        out.append(v)
    if church:
        root = church_root
        if root is None:
            from . import network
            root = network.DEFAULT_ROOT
        cf = Path(root) / CHURCH_FILE
        if cf.is_file():
            for v in json.loads(cf.read_text(encoding="utf-8")).get("verses", []):
                _check_verse(v, cap, church=True)
                if v.get("approved") is True:
                    out.append(dict(v, origin="church"))
    ids = [v["id"] for v in out]
    if len(ids) != len(set(ids)):
        raise ScriptureError("duplicate verse ids")
    return {"cap": cap, "verses": out}


def for_language(bank, lang):
    """Approved verses that have text in `lang`, as plain dicts the engine and the prompt use."""
    out = []
    for v in bank["verses"]:
        if v.get(f"text_{lang}") and v.get(f"reference_{lang}"):
            out.append({"id": v["id"], "reference": v[f"reference_{lang}"], "text": v[f"text_{lang}"],
                        "translation": v.get(f"translation_{lang}", ""),
                        "themes_text": ", ".join(v["themes"]), "origin": v.get("origin", "playbook")})
    return out


def source_for(pb, lang, church_root=None, church=True):
    """Dynamic source for the pastoral prompt: {"entries": [...]}, empty when nothing is approved."""
    return {"entries": for_language(load_bank(pb.dir, church_root, church), lang)}


def list_verses(pb, lang, church_root=None, church=True):
    """For the pastoral gate selector: id, reference, first words, translation."""
    return [{"id": e["id"], "reference": e["reference"], "first_words": " ".join(e["text"].split()[:6]) + " ...",
             "translation": e["translation"], "origin": e["origin"]}
            for e in for_language(load_bank(pb.dir, church_root, church), lang)]


def block(v):
    """The verse block, exactly as the source gives it."""
    ref = f"{v['reference']}, {v['translation']}" if v.get("translation") else v["reference"]
    return f"«{v['text']}»\n— {ref}"


def block_line(v):
    return block(v).split("\n", 1)[1]


def parse_output(text, verses):
    """Model output -> (parts, violations). `verses` is {id: verse}. parts: verse (dict or None), why, message, own."""
    m = re.match(r"\s*VERSE\s*:[ \t]*(?P<v>[^\n]*)\n\s*WHY\s*:[ \t]*(?P<w>.*?)\n[ \t]*MESSAGE\s*:\s*(?P<m>.*)\Z",
                 text.strip(), re.S | re.I)
    if not m:
        return None, [g.R("format", "use exactly the labels VERSE:, WHY: and MESSAGE:, in that order")]
    raw = m.group("v").strip().strip("`'\"[]<>* ")
    why, msg = m.group("w").strip(), m.group("m").strip()
    out = []
    verse = None
    if raw.upper() != "NONE":
        verse = next((v for k, v in verses.items() if k.lower() == raw.lower()), None)
        if verse is None:
            out.append(g.R("ungrounded_claim", "VERSE must be an id from the approved list, or NONE"))
    if not msg:
        out.append(g.R("format", "MESSAGE is empty"))
    if verse is None and why and not out:
        out.append(g.R("format", "WHY must be empty when VERSE is NONE"))
    if verse is not None:
        sentences = [s for s in re.split(r"(?<=[.!?])\s+", why) if s.strip()]
        if not why:
            out.append(g.R("format", "WHY is empty. Give one or two short sentences"))
        elif len(sentences) > 2 or _words(why) > 45:
            out.append(g.R("format", "WHY is at most two short sentences"))
    if out:
        return None, out
    return {"verse": verse, "why": why if verse else "", "message": msg,
            "own": (why + "\n" + msg).strip() if verse else msg}, []


def assemble(parts):
    """The draft the pastor sees: message, then the verse block, then the why-lines."""
    segs = [parts["message"]]
    if parts["verse"]:
        segs.append(block(parts["verse"]))
        if parts["why"]:
            segs.append(parts["why"])
    return "\n\n".join(segs)


def strip_block(text):
    """Nury's own sentences: the text with the verse block removed."""
    return re.sub(r"\n{3,}", "\n\n", BLOCK_RE.sub("", text)).strip()


def swap_verse(text, verse):
    """Pastor swaps the verse at the gate. `verse` is one entry from for_language(), or None to remove.

    Works on the draft text (without the disclaimer). The block is always the exact source text.
    The why-lines are left alone: they change only if the pastor asks Nury for a redraft."""
    new = block(verse) if verse else ""
    if BLOCK_RE.search(text):
        return re.sub(r"\n{3,}", "\n\n", BLOCK_RE.sub(lambda _m: new, text, count=1)).strip()
    if not verse:
        return text
    parts = text.strip().split("\n\n", 1)
    return parts[0] + "\n\n" + new + (("\n\n" + parts[1]) if len(parts) > 1 else "")
