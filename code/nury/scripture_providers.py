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
- The docs we could read give no cache rule and no rate limit. So Nury caches nothing, and a 429 or any
  error means "unavailable". Check the Platform terms again when the app key is issued.
"""

import os
from typing import Optional

import requests

YV_BASE = "https://api.youversion.com"


class ProviderUnavailable(Exception):
    pass


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
        p = self._get(f"/v1/bibles/{bible}/passages/{usfm}", format="text")
        meta = self._get(f"/v1/bibles/{bible}")
        text = " ".join(str(p.get("content", "")).split())
        name = meta.get("abbreviation") or meta.get("localized_abbreviation") or meta.get("title") or ""
        copyright_ = " ".join(str(meta.get("copyright", "")).split())
        if not text or "<" in text:
            raise ProviderUnavailable("youversion gave no plain text")
        if not name or not copyright_:
            raise ProviderUnavailable("youversion gave no version name or copyright, so it cannot be shown")
        if len(text.split()) > self.cap:
            raise ProviderUnavailable("youversion text is over the word cap")
        return {"id": entry["id"], "reference": p.get("reference") or entry["reference"], "text": text,
                "translation": name, "copyright": copyright_, "themes_text": entry.get("themes_text", ""),
                "origin": "playbook", "source": "youversion"}


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
