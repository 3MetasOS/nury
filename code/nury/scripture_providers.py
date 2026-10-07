"""Where the exact verse text comes from. The bank is the default and the fallback. YouVersion is a second step.

    get_passage(entry, lang) -> {id, reference, text, translation, copyright, source}

The model proposes a verse id from the approved list. The engine asks a provider for the exact text.
The text the engine inserts is the text the provider returned. A provider that cannot give the exact
text, with its version name and copyright, raises ProviderUnavailable, and the engine falls back to the bank.

Privacy: the only thing a provider sends out is a passage id such as PSA.46.1 and a Bible version id.
Never a name, never case text.

YouVersion rules, as far as the public developer docs state them (read 2026-10-06):
- GET /v1/bibles/{bible_id}/passages/{passage_id}, header X-YVP-App-Key, Accept: application/json.
- The version name or abbreviation and the copyright must be shown with the text.
- Availability depends on the app key and the licenses it accepted: a version that is not available is an error.
- The docs we could read give no cache rule and no rate limit. Responses carry Cache-Control hints
  (passages: public, max-age=86400). Nury still caches nothing, and a 429 or any error means "unavailable".
- The three versions Juan chose from (BSB 3034, VBL 3291, RVES 147) sit under the license "Public Domain and
  Creative Commons" (GET /v1/licenses). That agreement is one line; it states no cache or rate rule.

Superscriptions. The plain-text format puts a Psalm's title before verse 1 and no option removes it. The HTML
format marks the title as its own element (class "d"). Rule: ask for HTML, drop elements with a title or heading
class (d, s1..s4, ms, mr, r, sp), drop verse numbers and notes, keep the text of verse classes (p, q1..q4, m ...).
Any class we do not know means "unavailable" and the bank is used. The text inserted is the result of that rule,
and the verbatim check compares with it. The raw HTML length and the dropped classes go in the audit log.

Attribution. The version name or abbreviation and the copyright are shown with every verse. The provider's
copyright text is shown as returned, except that lines with an email address are removed and a second,
repeated copyright block is cut. Public domain versions show "Public Domain".
"""

import os
import re
from html.parser import HTMLParser
from typing import Optional

import requests

YV_BASE = "https://api.youversion.com"


class ProviderUnavailable(Exception):
    pass


_DROP_DIV = {"d", "s", "s1", "s2", "s3", "s4", "ms", "ms1", "ms2", "mr", "r", "sp", "h", "cl", "cd", "qa"}
_KEEP_DIV = {"p", "m", "pm", "pmo", "pmc", "pi", "pi1", "pi2", "mi", "nb", "b", "q", "q1", "q2", "q3", "q4", "qr", "qc", "qm",
             "qm1", "qm2", "li", "li1", "li2", "ph", "ph1", "ph2", "lh", "lf"}
_DROP_SPAN = {"yv-vlbl", "yv-n", "f", "fr", "fq", "fk", "x"}
_KEEP_SPAN = {"yv-v", "nd", "wj", "add", "tl", "qt", "sc", "bd", "it", "em", "sig", "w", "ord", "pn", "k"}


class _Verse(HTMLParser):
    """HTML -> (verse text, dropped classes). Unknown classes set .unknown."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.out, self.dropped, self.unknown = [], [], set(), set()

    def handle_starttag(self, tag, attrs):
        if tag in ("div", "span", "p"):
            cls = (dict(attrs).get("class") or "").split()
            self.stack.append((tag, cls[0] if cls else ""))
            if tag != "span":
                self.out.append(" ")

    def handle_endtag(self, tag):
        if tag in ("div", "span", "p") and self.stack:
            self.stack.pop()
            if tag != "span":
                self.out.append(" ")

    def handle_data(self, data):
        if not data.strip():
            self.out.append(" ")
            return
        for tag, cls in self.stack:
            if (tag == "div" and cls in _DROP_DIV) or (tag == "span" and cls in _DROP_SPAN):
                if cls != "yv-vlbl":                      # a verse number is not a trim
                    self.dropped.add(cls)
                return
        for tag, cls in reversed(self.stack):
            if tag == "span" and cls:
                if cls not in _KEEP_SPAN:
                    self.unknown.add(cls)
                    return
            if tag == "div" and cls:
                if cls not in _KEEP_DIV:
                    self.unknown.add(cls)
                    return
                break
        else:
            self.unknown.add("(no class)")
            return
        self.out.append(data)


def verse_from_html(html):
    """(text, dropped classes). Raises ProviderUnavailable on a class we do not know."""
    p = _Verse()
    p.feed(html or "")
    if p.unknown:
        raise ProviderUnavailable(f"youversion html has classes we do not handle: {sorted(p.unknown)}")
    return " ".join("".join(p.out).split()), sorted(p.dropped)


def attribution(copyright_text):
    """The copyright to show. Lines with an email are removed. A second copyright block is cut."""
    lines, seen = [], 0
    for ln in str(copyright_text or "").splitlines():
        ln = ln.strip()
        if not ln or re.search(r"\S+@\S+", ln):
            continue
        if "©" in ln:
            seen += 1
            if seen > 1:
                break
        lines.append(ln)
    return " ".join(lines)


class BankProvider:
    """The verified bank: public-domain text, exact, works offline. The entry already holds the text."""
    name = "bank"

    def get_passage(self, entry, lang):
        if not entry.get("text") or not entry.get("reference"):
            raise ProviderUnavailable("bank entry has no text")
        return {"id": entry["id"], "reference": entry["reference"], "text": entry["text"],
                "translation": entry.get("translation", ""), "copyright": entry.get("copyright", ""),
                "themes_text": entry.get("themes_text", ""), "origin": entry.get("origin", "playbook"), "source": "bank"}


class YouVersionProvider:
    """YouVersion Platform. Only used when YVP_APP_KEY is set and a Bible id is set for the language."""
    name = "youversion"

    def __init__(self, app_key, bibles, http=None, timeout=4.0, cap=52):
        self.app_key, self.bibles, self.http, self.timeout, self.cap = app_key, bibles, http or requests, timeout, cap

    def _get(self, path, **params):
        try:
            r = self.http.get(YV_BASE + path, params=params or None, timeout=self.timeout,
                              headers={"X-YVP-App-Key": self.app_key, "Accept": "application/json"})
        except Exception as e:
            raise ProviderUnavailable(f"youversion request failed: {type(e).__name__}")
        if r.status_code != 200:
            raise ProviderUnavailable(f"youversion http {r.status_code}")
        try:
            return r.json()
        except Exception:
            raise ProviderUnavailable("youversion sent no JSON")

    def get_passage(self, entry, lang):
        bible, usfm = self.bibles.get(lang), entry.get("usfm")
        if not bible or not usfm or entry.get("origin") == "church":
            raise ProviderUnavailable("no YouVersion version or passage id for this verse")
        p = self._get(f"/v1/bibles/{bible}/passages/{usfm}", format="html")
        meta = self._get(f"/v1/bibles/{bible}")
        raw = str(p.get("content", ""))
        text, dropped = verse_from_html(raw)
        name = meta.get("abbreviation") or meta.get("localized_abbreviation") or meta.get("title") or ""
        copyright_ = attribution(meta.get("copyright"))
        if not text:
            raise ProviderUnavailable("youversion gave no verse text")
        if not name or not copyright_:
            raise ProviderUnavailable("youversion gave no version name or copyright, so it cannot be shown")
        if len(text.split()) > self.cap:
            raise ProviderUnavailable("youversion text is over the word cap")
        return {"id": entry["id"], "reference": p.get("reference") or entry["reference"], "text": text,
                "translation": name, "copyright": copyright_, "themes_text": entry.get("themes_text", ""),
                "origin": "playbook", "source": "youversion",
                "raw_chars": len(raw), "dropped": dropped}


def default_chain(cap=52, env=None):
    """[YouVersion, bank] when YVP_APP_KEY is set, else [bank]. Bible ids: YVP_BIBLE_ES, YVP_BIBLE_EN."""
    env = os.environ if env is None else env
    chain = []
    key = env.get("YVP_APP_KEY")
    if key:
        bibles = {lg: env[f"YVP_BIBLE_{lg.upper()}"] for lg in ("es", "en") if env.get(f"YVP_BIBLE_{lg.upper()}")}
        chain.append(YouVersionProvider(key, bibles, cap=cap))
    chain.append(BankProvider())
    return chain


def fetch(entry, lang, chain: Optional[list] = None):
    """(passage, notes). Tries each provider in order. The bank is last and is the fallback."""
    notes = []
    for prov in chain or [BankProvider()]:
        try:
            return prov.get_passage(entry, lang), notes
        except ProviderUnavailable as e:
            notes.append(f"{prov.name}: {e}")
    raise ProviderUnavailable("; ".join(notes) or "no provider")
