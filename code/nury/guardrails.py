"""Nury guardrails: boundary prompt, disclaimers, and deterministic output checks.

Gloo's guarded endpoint is the server-side backstop (HTTP 403). These checks
run on every draft before the pastor sees it. Each check returns a list of
reasons. An empty list means the draft is clean.
"""

import re

_BOUNDARY = """You are Nury, a drafting assistant for a solo pastor helping {who}.
Hard rules:
1. Give general {domain} INFORMATION only. Never give {domain} advice. Never predict how the situation will turn out. Never suggest a strategy.
2. Use only the source material given to you. Do not use outside knowledge for facts. Do not invent phone numbers, links, names or rules.
3. Urge the family to speak with a {professional}.
4. Never claim to be a pastor, counselor, therapist, doctor, nurse, or lawyer.
5. Never recommend a specific {professional_kind}.
6. Be calm, plain, and kind. No frightening or sensational language.
7. Short sentences. Plain words.
8. Write the whole output in the language named in the task. Do not mix languages. Translate every quote. Do not add scripture, proverbs, or quotes that are not in the source material.
9. Do not add a title, byline, signature, or any line that says who wrote the text. Never write "prepared by the pastor" or similar. Output only the content asked for.
"""


def boundary(fields):
    """The engine's rules, with the playbook's domain words filled in (playbook.json "boundary")."""
    return _BOUNDARY.format(**{k: fields[k] for k in ("who", "domain", "professional", "professional_kind")})


# Predictions, advice, and identity claims. English and Spanish.
_UNSAFE_PATTERNS = [
    (r"\byou (will|'ll) (win|be released|be deported|be allowed|lose|get)\b", "predicts an outcome"),
    (r"\b(will|won't|will not) be (deported|released|detained|freed)\b", "predicts an outcome"),
    (r"\byour case (will|is going to|should)\b", "predicts an outcome"),
    (r"\bguarantee[sd]?\b", "promises an outcome"),
    (r"\byou should (plead|sign|file|apply|admit|accept|waive|refuse to sign)\b", "gives advice"),
    (r"\b(we|i) (recommend|advise) (that )?you (plead|sign|file|apply)\b", "gives advice"),
    (r"\bthe best (strategy|option) (is|would be)\b", "suggests a legal strategy"),
    (r"\b(i am|i'm|as) (your|a) (lawyer|attorney|counselor|therapist|doctor|nurse|physician)\b", "claims to be a professional"),
    (r"\b(i am|i'm) (a|your) pastor\b", "claims to be a pastor"),
    (r"\b(preparad[oa]|escrit[oa]|redactad[oa]|written|prepared|drafted) (por|by) (el |la |the )?(pastor|iglesia|church)", "says a pastor wrote it"),
    (r"\b(from|de parte de|firmado por) (the |el )?pastor\b", "signs as the pastor"),
    (r"\bsu caso (va a|será|sera|se va a)\b", "predicts an outcome"),
    (r"\b(será|sera|van a) (deportad[oa]s?|liberad[oa]s?)\b", "predicts an outcome"),
    (r"\bgarantiz\w+", "promises an outcome"),
    (r"\busted debe (declararse|firmar|solicitar|aceptar|admitir)\b", "gives advice"),
    (r"\bdebe(n)? declararse\b", "gives advice"),
    (r"\bsoy (su |un )?(abogad[oa]|consejer[oa]|terapeuta|pastor|médic[oa]|enfermer[oa]|doctor[a]?)\b", "claims to be a lawyer, counselor, or pastor"),
    (r"\b(recomendamos|recomiendo) (al abogado|a la abogada|contratar)\b", "recommends a specific attorney"),
    (r"\bwe recommend (attorney|lawyer|the firm)\b", "recommends a specific attorney"),
]

_URL = re.compile(r"https?://[^\s)>\]\"']+|www\.[^\s)>\]\"']+", re.I)


def R(category, reason):
    """One violation. Categories: banned_phrase, ungrounded_claim, missing_vetted_entry,
    missing_referral, format, length."""
    return {"category": category, "reason": reason}


def unsafe_reasons(text, extra=()):
    """Floor patterns plus a playbook's extra [{"pattern", "why"}]. A playbook can add. It cannot remove."""
    low = text.lower()
    pats = list(_UNSAFE_PATTERNS) + [(e["pattern"], e["why"]) for e in extra]
    return [R("banned_phrase", f"{why} (matched {m.group(0)!r})")
            for pat, why in pats
            if (m := re.search(pat, low))]


def _norm_url(u):
    return u.lower().rstrip(".,;:/").replace("https://", "").replace("http://", "").replace("www.", "")


# A site written without http or www, such as "immigrationadvocates.org". Not an email domain
# (nothing may touch it on the left: no @, letter, dot, or hyphen), and file names like index.md
# do not match because md is not in the list.
_TLDS = r"(?:org|com|gov|net|edu|info|us|mx)"
_BARE_IN_TEXT = re.compile(r"(?<![@\w.\-])[a-z0-9](?:[a-z0-9\-]*[a-z0-9])?(?:\.[a-z0-9\-]+)*\." + _TLDS + r"\b(?:/[^\s)>\]\"']*)?", re.I)


def url_reasons(text, allowed_urls):
    """Every link or site in the text must be in the vetted allowlist: full links, www links,
    and bare domains. Email-like strings and file names are not checked."""
    allowed = [_norm_url(u) for u in allowed_urls]
    found = list(_URL.findall(text)) + _BARE_IN_TEXT.findall(_URL.sub(" ", text))
    bad = []
    for u in found:
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


# ---- email allowlist: an email must come from the vetted sources, the approved text, or the intake ----
_EMAIL_IN_TEXT = re.compile(r"[\w.+\-]+@([\w\-]+(?:\.[\w\-]+)+)")


def email_reasons(text, vetted_blob, *known_blobs):
    """Flag an email whose address is not already in the known text (approved context, intake) and whose
    domain is not a vetted domain (a site or email domain in the vetted sources)."""
    hosts = {_norm_url(u).split("/")[0] for u in allowed_urls_in(vetted_blob)}
    hosts |= {m.group(1).lower() for m in _EMAIL_IN_TEXT.finditer(vetted_blob)}
    known = "\n".join([vetted_blob, *known_blobs]).lower()
    out = []
    for m in _EMAIL_IN_TEXT.finditer(text):
        addr, dom = m.group(0).lower(), m.group(1).lower()
        if addr in known or any(dom == h or dom.endswith("." + h) or h.endswith("." + dom) for h in hosts):
            continue
        out.append(R("ungrounded_claim", f"email not in vetted sources: {m.group(0)}"))
    return out
