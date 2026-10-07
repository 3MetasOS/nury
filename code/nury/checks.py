"""Named stage checks. A playbook lists them by name in stages.json.

They add to the safety floor (guardrails.py + the engine). They never replace it.
Each check: (params, text, ctx) -> list of violations. ctx has .state, .data, .fields, .lang.
"""

import re

from . import guardrails as g


def _norm(u):
    return g._norm_url(u)


def required_labels(p, text, ctx):
    up = text.upper()
    return [g.R("format", f"missing label {l}") for l in p["labels"] if l.upper() not in up]


def numbered_after(p, text, ctx):
    tail = text.upper().split(p["marker"].upper(), 1)[-1]
    n = len(re.findall(r"^\s*\d[.)]", tail, re.M))
    return [] if n == p["count"] else [g.R("format", f"{p['marker']} must list exactly {p['count']} numbered items")]


def cited_bullets(p, text, ctx):
    entries = ctx.data[p["source"]][p["list"]]
    names = {e[p["field"]].split(" (")[0].strip() for e in entries}
    lines = [l for l in text.splitlines()
             if re.match(r"\s*[-•*]\s+\w", l) and not l.strip().startswith("**")]
    out = [] if lines else [g.R("format", "no bullet points found")]
    for l in lines:
        if not any(n.lower() in l.lower() for n in names):
            out.append(g.R("ungrounded_claim", f"bullet without a source citation: {l.strip()[:60]!r}"))
    return out


def ends_with_referral(p, text, ctx):
    ok = re.search(p["pattern"], text[-p.get("tail", 400):], re.I)
    return [] if ok else [g.R("missing_referral", p.get("reason", "must end by urging the family to see a professional"))]


def vetted_links_present(p, text, ctx):
    out = []
    for lst in p["lists"]:
        for e in ctx.data[p["source"]].get(lst, []):
            if e.get(p["field"]) and _norm(e[p["field"]]) not in _norm(text):
                out.append(g.R("missing_vetted_entry", f"missing vetted link: {e[p['field']]}"))
    return out


def required_headings(p, text, ctx):
    up = text.upper()
    return [g.R("format", f"missing section {h}") for h in p["headings"] if h.upper() not in up]


def max_words(p, text, ctx):
    n = g.word_count(text)
    return [g.R("length", f"too long: {n} words (limit {p['limit']})")] if n > p["limit"] else []


_AGENCY_ACRONYMS = r"\b(ICE|CBP|DHS|USCIS|ERO|HSI|DEA|FBI)\b"
_AGENCY_NAMES = r"immigration and customs enforcement|customs and border protection|border patrol|homeland security|\bla migra\b|aduanas y protecci"


def no_agency_names(p, text, ctx):
    """Locked decision: no agency name or acronym on screen. Say 'immigration officers'."""
    hits = {m.group(0) for m in re.finditer(_AGENCY_ACRONYMS, text)}
    hits |= {m.group(0).lower() for m in re.finditer(_AGENCY_NAMES, text, re.I)}
    return [g.R("agency_name", f"names an agency: {sorted(hits)}")] if hits else []


_STOCK = re.compile(
    r"\b(delve|tapestry|testament to|vibrant|pivotal|crucial role|stands as a|serves as a|it(?:'s| is) important to note|i hope this helps|here(?:'s| is) what you need to know)\b"
    r"|\b(tapiz|es un testimonio de|testimonio de|en el panorama|en el mundo actual|cabe destacar|es importante destacar|espero que esto (?:te|le) ayude)\b", re.I)
_CONTRAST = re.compile(
    r"\bnot (?:just|only|merely) [^.\n]{1,60}, (?:but|it(?:'s| is))\b|\bit(?:'s| is) not [^.\n]{1,40}[,;] it(?:'s| is)\b"
    r"|\bno (?:es|son|se trata de|fue) (?:solo|sólo|solamente|simplemente|únicamente) [^.\n]{1,60}\bsino\b|\bno solo [^.\n]{1,60}\bsino (?:también )?", re.I)


def no_stock_phrases(p, text, ctx):
    """Voice skill: stock AI phrases and the 'not X but Y' tic."""
    hits = [m.group(0) for m in _STOCK.finditer(text)] + [m.group(0)[:40] for m in _CONTRAST.finditer(text)]
    return [g.R("stock_phrase", f"stock or inflated wording: {sorted(set(hits))[:3]}")] if hits else []


REGISTRY = {f.__name__: f for f in (required_labels, numbered_after, cited_bullets, ends_with_referral,
                                    vetted_links_present, required_headings, max_words, no_agency_names, no_stock_phrases)}
