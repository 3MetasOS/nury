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


REGISTRY = {f.__name__: f for f in (required_labels, numbered_after, cited_bullets, ends_with_referral,
                                    vetted_links_present, required_headings, max_words)}
