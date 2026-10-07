"""Nury guardrails: boundary prompt, disclaimers, and deterministic output checks.

Gloo's guarded endpoint is the server-side backstop (HTTP 403). These checks
run on every draft before the pastor sees it. Each check returns a list of
reasons. An empty list means the draft is clean.
"""

import re

DISCLAIMER = {
    "en": (
        "Nury is an AI assistant, not a lawyer, pastor, counselor, or therapist. "
        "This is general legal information, not legal advice. Please review it with "
        "a qualified immigration attorney as soon as possible."
    ),
    "es": (
        "Nury es un asistente de IA, no es abogado, pastor, consejero ni terapeuta. "
        "Esto es información legal general, no asesoramiento legal. Por favor "
        "revísela con un abogado de inmigración calificado lo antes posible."
    ),
}

SYSTEM_BOUNDARY = """You are Nury, a drafting assistant for a solo pastor helping an immigrant family in crisis.
Hard rules:
1. Give general legal INFORMATION only. Never give legal advice. Never predict how a case will turn out. Never suggest a legal strategy.
2. Use only the source material given to you. Do not use outside knowledge for legal facts. Do not invent phone numbers, links, names or laws.
3. Urge the family to speak with a qualified immigration attorney.
4. Never claim to be a pastor, counselor, therapist, or lawyer.
5. Never recommend a specific attorney.
6. Be calm, plain, and kind. No frightening or sensational language.
7. Short sentences. Plain words.
8. Write the whole output in the language named in the task. Do not mix languages. Translate every quote. Do not add scripture, proverbs, or quotes that are not in the source material.
9. Do not add a title, byline, signature, or any line that says who wrote the text. Never write "prepared by the pastor" or similar. Output only the content asked for.
"""

# Predictions, advice, and identity claims. English and Spanish.
_UNSAFE_PATTERNS = [
    (r"\byou (will|'ll) (win|be released|be deported|be allowed|lose|get)\b", "predicts an outcome"),
    (r"\b(will|won't|will not) be (deported|released|detained|freed)\b", "predicts an outcome"),
    (r"\byour case (will|is going to|should)\b", "predicts an outcome"),
    (r"\bguarantee[sd]?\b", "promises an outcome"),
    (r"\byou should (plead|sign|file|apply|admit|accept|waive|refuse to sign)\b", "gives legal advice"),
    (r"\b(we|i) (recommend|advise) (that )?you (plead|sign|file|apply)\b", "gives legal advice"),
    (r"\bthe best (strategy|option) (is|would be)\b", "suggests a legal strategy"),
    (r"\b(i am|i'm|as) (your|a) (lawyer|attorney|counselor|therapist)\b", "claims to be a lawyer or counselor"),
    (r"\b(i am|i'm) (a|your) pastor\b", "claims to be a pastor"),
    (r"\b(preparad[oa]|escrit[oa]|redactad[oa]|written|prepared|drafted) (por|by) (el |la |the )?(pastor|iglesia|church)", "says a pastor wrote it"),
    (r"\b(from|de parte de|firmado por) (the |el )?pastor\b", "signs as the pastor"),
    (r"\bsu caso (va a|será|sera|se va a)\b", "predicts an outcome"),
    (r"\b(será|sera|van a) (deportad[oa]s?|liberad[oa]s?)\b", "predicts an outcome"),
    (r"\bgarantiz\w+", "promises an outcome"),
    (r"\busted debe (declararse|firmar|solicitar|aceptar|admitir)\b", "gives legal advice"),
    (r"\bdebe(n)? declararse\b", "gives legal advice"),
    (r"\bsoy (su |un )?(abogad[oa]|consejer[oa]|terapeuta|pastor)\b", "claims to be a lawyer, counselor, or pastor"),
    (r"\b(recomendamos|recomiendo) (al abogado|a la abogada|contratar)\b", "recommends a specific attorney"),
    (r"\bwe recommend (attorney|lawyer|the firm)\b", "recommends a specific attorney"),
]

_URL = re.compile(r"https?://[^\s)>\]\"']+|www\.[^\s)>\]\"']+", re.I)
_ATTORNEY_WORDS = re.compile(r"abogad|attorney|lawyer|legal aid|asistencia legal", re.I)


def R(category, reason):
    """One violation. Categories: banned_phrase, ungrounded_claim, missing_vetted_entry,
    missing_attorney_referral, format, length."""
    return {"category": category, "reason": reason}


def unsafe_reasons(text):
    low = text.lower()
    return [R("banned_phrase", f"{why} (matched {m.group(0)!r})")
            for pat, why in _UNSAFE_PATTERNS
            if (m := re.search(pat, low))]


def _norm_url(u):
    return u.lower().rstrip(".,;:/").replace("https://", "").replace("http://", "").replace("www.", "")


def url_reasons(text, allowed_urls):
    allowed = [_norm_url(u) for u in allowed_urls]
    bad = []
    for u in _URL.findall(text):
        n = _norm_url(u)
        if not any(n == a or n.startswith(a) or a.startswith(n) for a in allowed):
            bad.append(u)
    return [R("ungrounded_claim", f"link not in vetted sources: {u}") for u in bad]


def word_count(text):
    return len(text.split())


# ---- language check (stages whose output is the family's language) ----
_EN_WORDS = set("the and is are of you your our with for that this not will from have has be we they their but can should may was were been it its".split())
_LANG_STRIP = re.compile(r"https?://\S+|www\.\S+|\b[A-Z][A-Za-z]*(?: [A-Z][A-Za-z]*)+\b|\bDO TONIGHT\b|\bDO NOT DO\b|\bGATHER THESE DOCUMENTS\b")


def language_reasons(text, lang):
    """Flag English mixed into Spanish. Proper names, links and the fixed headings are ignored."""
    if lang != "es":
        return []
    body = _LANG_STRIP.sub(" ", text)
    words = re.findall(r"[A-Za-z']+", body.lower())
    hits = sorted({w for w in words if w in _EN_WORDS})
    n = sum(1 for w in words if w in _EN_WORDS)
    return [R("language", f"English mixed into Spanish ({n} words, e.g. {', '.join(hits[:5])})")] if n >= 3 else []


# ---- reference allowlist: links and phone numbers must come from vetted sources ----
_PHONE = re.compile(r"(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}")
_BARE_DOMAIN = re.compile(r"\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:org|com|gov|net|edu)(?:/[^\s\"')\]>]*)?", re.I)


def allowed_urls_in(*blobs):
    out = []
    for b in blobs:
        out += _URL.findall(b) + _BARE_DOMAIN.findall(b)
    return out


def phone_reasons(text, *allowed_blobs):
    ok = {re.sub(r"\D", "", p)[-10:] for b in allowed_blobs for p in _PHONE.findall(b)}
    return [R("ungrounded_claim", f"phone number not in vetted sources: {p.strip()}")
            for p in _PHONE.findall(text) if re.sub(r"\D", "", p)[-10:] not in ok]
