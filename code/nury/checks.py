"""Named stage checks. A playbook lists them by name in stages.json.

They add to the safety floor (guardrails.py + the engine). They never replace it.
Each check: (params, text, ctx) -> list of violations. ctx has .state, .data, .fields, .lang.
"""

import json
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


_ENDORSE = re.compile(
    r"\b(?:highly recommended|recommended|we recommend|i recommend|top[- ]rated|best (?:lawyer|attorney|option|choice|clinic|help)|the best)\b"
    r"|\b(?:recomendad[oa]s?|recomendamos|recomiendo|recomendar|altamente recomendad\w+)\b|\b(?:el|la|los|las)\s+mejor(?:es)?\b", re.I)
_TITLED = re.compile(r"\b(?:Lic\.|Licenciad[oa]|Abogad[oa]|Attorney|Atty\.|Esq\.|Dr\.|Dra\.)\s+[A-ZÁÉÍÓÚÑ][\w'’]+(?:\s+[A-ZÁÉÍÓÚÑ][\w'’]+)?")


_NEGATED = re.compile(r"(?:does not mean|doesn't mean|is not|not|no significa|no quiere decir|no implica|no es|no son|ni)\W+(?:\w+\W+){0,3}$", re.I)


def no_endorsement_words(p, text, ctx):
    """Nury lists contacts. It never ranks or endorses one. 'Listed does not mean recommended' is allowed."""
    hits = sorted({m.group(0).lower() for m in _ENDORSE.finditer(text)
                   if not _NEGATED.search(text[max(0, m.start() - 45):m.start()])})
    return [g.R("endorsement", f"endorsing or ranking words: {hits[:3]}")] if hits else []


_FREE = re.compile(r"\b(?:free|gratis|gratuit[oa]s?|sin costo|sin cargo|no cost|at no charge)\b", re.I)
_CAVEAT = re.compile(r"does not mean|doesn't mean|no significa|no quiere decir|no implica|no es una recomendaci|no son recomendaci", re.I)


def official_list_rules(p, text, ctx):
    """The DOJ official list, as Juan approved it. A held entry is never named. A listed entry keeps its exact
    name with its own phone or link. Nothing from the list is called free. The 'listed does not mean
    recommended' caveat is present when any entry is listed."""
    d = ctx.data.get(p["source"]) or {}
    out, low = [], _fold(text)
    for held in d.get("held_names", []):
        if _fold(held) in low:
            out.append(g.R("ungrounded_claim", f"names an official-list entry that is on hold: {held[:40]}"))
    entries = d.get("entries", [])
    lines = text.splitlines()
    for e in entries:
        nm = _fold(e["name"].split(" (")[0])
        digits = [re.sub(r"\D", "", ph) for ph in e.get("phones", []) if ph]
        for i, ln in enumerate(lines):
            lnd = re.sub(r"\D", "", ln)
            if nm in _fold(ln) or any(ph and ph in lnd for ph in digits):
                window = " ".join(lines[i:i + 2])
                if _FREE.search(window):
                    out.append(g.R("ungrounded_claim", f"calls an official-list provider free: {e['name'][:40]}"))
                    break
        alltext = re.sub(r"\D", "", text)
        present = (nm in low or any(ph and ph in alltext for ph in digits) or (e.get("url") and g._norm_url(e["url"]) in g._norm_url(text))
                   or (e.get("email") and e["email"].lower() in text.lower()))
        if not present:
            out.append(g.R("missing_vetted_entry", f"official-list entry left out: {e['name'][:40]}"))
    if entries and not _CAVEAT.search(text):
        out.append(g.R("missing_vetted_entry", "official list is missing the 'listed does not mean recommended' line"))
    return out


def _entries(ctx, names):
    out = []
    for n in names:
        d = ctx.data.get(n) or {}
        for key in ("entries", "national", "local"):
            out += [e for e in d.get(key, []) if isinstance(e, dict)]
    return out


def _fold(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", s or "") if unicodedata.category(c) != "Mn").casefold()


def listed_contacts_known(p, text, ctx):
    """A contact in the draft must be a contact we gave: the church network or the vetted lists.
    Church entries are copied exactly (name with its own phone or link). A titled personal name that is in
    neither list is rejected."""
    out = []
    church = _entries(ctx, p.get("church", []))
    known = _entries(ctx, p.get("church", []) + p.get("lists", []))
    low = _fold(text)
    for e in church:
        name = _fold(e["name"])
        if name and name in low:
            ph = re.sub(r"\D", "", e.get("phone", ""))
            ok = (ph and ph in re.sub(r"\D", "", text)) or (e.get("url") and g._norm_url(e["url"]) in g._norm_url(text))
            if (ph or e.get("url")) and not ok:
                out.append(g.R("ungrounded_claim", f"church contact listed without its own phone or link: {e['name'][:40]}"))
    for line in text.splitlines():
        s = line.strip()
        if not re.match(r"^[-•*]|^\d+[.)]", s):
            continue
        digits = re.sub(r"\D", "", s)
        for e in church:
            ph = re.sub(r"\D", "", e.get("phone", ""))
            if ph and ph in digits and _fold(e["name"]) not in _fold(s):
                out.append(g.R("ungrounded_claim", f"church contact name changed or missing for phone {e.get('phone')}"))
    blob = _fold(" ".join(e["name"] for e in known))
    for m in _TITLED.finditer(text):
        if _fold(m.group(0)) not in blob:
            out.append(g.R("ungrounded_claim", f"names a professional who is not in the network or vetted sources: {m.group(0)}"))
    return out


def network_entries_present(p, text, ctx):
    """Every church contact we handed over must appear, with its phone or link."""
    out = []
    low = re.sub(r"\D", "", text)
    for e in _entries(ctx, [p["source"]]):
        ph = re.sub(r"\D", "", e.get("phone", ""))
        hit = (ph and ph in low) or (e.get("url") and g._norm_url(e["url"]) in g._norm_url(text))
        if not hit:
            out.append(g.R("missing_vetted_entry", f"church contact left out: {e['name'][:40]}"))
    return out


_PROMISE = re.compile(
    r"\bwe(?: are|'re) (?:looking|searching|working|preparing|arranging|organizing|organising|putting together|gathering|finding)\b"
    r"|\b(?:we|i)(?: will|'ll| shall| am going to|'m going to| are going to|'re going to) (?:send|call|visit|bring|follow|reach|get back|be in touch|check in|arrange|find|help you find|prepare|look for|search|gather|come)\b"
    r"|\bin touch\b|\b(?:soon|shortly|right away|very soon)\b"
    r"|\bestamos (?:buscando|preparando|trabajando|organizando|armando|reuniendo|gestionando|coordinando)\b"
    r"|\b(?:les|le|te|los|la|las) (?:mandamos|enviamos|haremos llegar|llamamos|visitamos|traemos|buscamos|preparamos)\b"
    r"|\bya estamos\b|\b(?:muy )?pronto\b|\ben breve\b|\bdentro de poco\b|\bcuanto antes\b"
    r"|\b(?:vamos a|voy a) (?:buscar|enviar|mandar|llamar|visitar|preparar|traer|conseguir|encontrar|organizar|ayudar a (?:buscar|encontrar))\b"
    r"|\b(?:llamar|visitar|enviar|mandar|buscar|preparar|traer|conseguir|encontrar|organizar)(?:é|emos|aré|eremos)\b"
    r"|\b(?:llamaré|llamaremos|visitaré|visitaremos|enviaré|enviaremos|mandaré|mandaremos|buscaremos|prepararemos|traeremos|conseguiremos|encontraremos|organizaremos)\b"
    r"|\b(?:seguiremos|seguimos|estaremos|me pondré|nos pondremos|nos comunicaremos|me comunicaré) (?:en )?contacto\b|\bestaremos en contacto\b", re.I)


def no_unauthorized_promises(p, text, ctx):
    """The pastor's voice may invite (pray together, call me, you are not alone). It may not promise an action
    the church has not taken: a search, a visit, a call back, sending or preparing anything, or any time word for
    one. An action the pastor wrote in the intake is allowed."""
    intake = _fold(getattr(ctx.state, "intake", "") or "")
    hits = []
    for m in _PROMISE.finditer(text):
        word = _fold(m.group(0))
        verb = re.sub(r"[^a-z ]", "", word).split()[-1] if re.sub(r"[^a-z ]", "", word).split() else ""
        if verb and len(verb) >= 5 and verb[:5] in intake:
            continue                                     # the pastor wrote it, so it may be said
        hits.append(m.group(0))
    return [g.R("unauthorized_promise", f"promises an action nobody has taken: {sorted(set(h.lower() for h in hits))[:3]}")] if hits else []


_PROVIDENCE = re.compile(
    r"\bgod(?:'ll| will| is going to| shall)\b[^.!?\n]{0,30}\b(?:free|heal|cure|save|deliver|rescue|restore|release|fix|protect|bring|return|send)\b"
    r"|\beverything happens for a reason\b|\ball things happen for\b|\bhappens for a reason\b|\bthere(?:'s| is) a reason (?:for|why)\b"
    r"|\bgod(?:'s| has a| has) (?:plan|reason|purpose)\b|\b(?:it(?:'s| is)|that(?:'s| is)) god(?:'s)? (?:plan|will)\b|\bgod(?:'s)? will\b"
    r"|\bgod (?:is|was) (?:punishing|testing|teaching|angry)\b|\bgod (?:allowed|permitted|sent|wanted|chose)\b|\bpunishment from god\b"
    r"|\bdios (?:lo|la|los|las|te|nos|les|le) (?:liberar[aá]|sanar[aá]|curar[aá]|salvar[aá]|sacar[aá]|devolver[aá]|traer[aá]|proteger[aá])\b"
    r"|\bdios\b[^.!?\n]{0,30}\b(?:liberar[aá]|sanar[aá]|curar[aá]|salvar[aá]|sacar[aá]|devolver[aá]|traer[aá])\b"
    r"|\btodo (?:pasa|sucede|ocurre) por (?:algo|una raz[oó]n|alguna raz[oó]n)\b|\bpor algo (?:pasa|sucede|ocurre)\b"
    r"|\bes (?:la )?voluntad de dios\b|\b(?:era|es) el plan de dios\b|\bdios (?:tiene|ten[ií]a) (?:un |su )?(?:plan|prop[oó]sito|raz[oó]n)\b"
    r"|\bdios (?:est[aá]|estaba) (?:castigando|probando|ense[nñ]ando)\b|\bcastigo de dios\b|\bdios (?:permiti[oó]|quiso|envi[oó]|escogi[oó])\b", re.I)


def no_providence_claims(p, text, ctx):
    """Nury's own sentences may say God is with the family. They may not say what God will do for the case,
    why it happened, or that it is God's plan or punishment. Applies to the why-lines and the message,
    never to the quoted verse."""
    hits = sorted({m.group(0).lower() for m in _PROVIDENCE.finditer(text)})
    return [g.R("providence_claim", f"claims to know what God will do or why this happened: {hits[:3]}")] if hits else []


def _fold_words(t):
    return re.sub(r"[^\w ]", "", _fold(t)).split()


def no_model_scripture(p, text, ctx):
    """The model never writes Scripture. Its own sentences carry no reference, no quotation marks of the verse
    block, and no run of six words from any approved verse."""
    out = []
    if re.search(r"\b\d{1,3}\s*:\s*\d{1,3}\b", text) or "«" in text or "»" in text:
        out.append(g.R("invented_scripture", "do not write a Bible reference or a verse block; the app inserts the verse"))
    words = _fold_words(text)
    grams = {" ".join(words[i:i + 6]) for i in range(max(0, len(words) - 5))}
    for v in getattr(ctx, "scripture", {}).values():
        vw = _fold_words(v["text"])
        if any(" ".join(vw[i:i + 6]) in grams for i in range(max(0, len(vw) - 5))):
            out.append(g.R("invented_scripture", "do not quote Scripture in your own sentences; the app inserts the verse"))
            break
    return out


def verse_block_verbatim(p, text, ctx):
    """The verse block in a draft equals the vetted source text, with its reference and translation, and fits the cap."""
    from . import scripture as scr
    blocks = list(scr.BLOCK_RE.finditer(text))
    if not blocks:
        return []
    if len(blocks) > 1:
        return [g.R("scripture_altered", "more than one verse block")]
    b = blocks[0]
    for v in getattr(ctx, "scripture", {}).values():
        if b.group("text") == v["text"] and b.group("ref").strip() == scr.block_line(v)[2:]:
            return [] if len(v["text"].split()) <= getattr(ctx, "scripture_cap", scr.DEFAULT_CAP) else \
                [g.R("scripture_altered", "verse block is over the word cap")]
    return [g.R("scripture_altered", "the verse block does not match any approved verse word for word")]


_CALL_NAME = re.compile(
    r"\b(?:call|phone|ring|llame|llamen|llamar|llama|llamarme|contact|contacte|contacten)\s+(?:a\s+)?"
    r"(?!(?:God|Dios|Jesus|Jes[uú]s|Christ|Cristo)\b)([A-ZÁÉÍÓÚÑ][\wáéíóúñ]+)")


def no_name_after_call(p, text, ctx):
    """The pastor's voice says 'call me' or 'call the pastor'. It never writes 'call <Name>', because the only
    names in a case are the family's. (Panel finding, scenario 10: 'call Maria Lopez can call anytime'.)
    A name the pastor wrote in the intake as a contact is allowed."""
    intake = getattr(ctx.state, "intake", "") or ""
    hits = [m.group(1) for m in _CALL_NAME.finditer(text)
            if not re.search(rf"\b(?:call|llam\w*|contact\w*)\s+(?:a\s+)?{re.escape(m.group(1))}\b", intake, re.I)]
    return [g.R("garbled", f"names a person after 'call': {sorted(set(hits))[:2]}; say 'call me' or 'call the pastor'")] if hits else []


_SIGN_WORDS = re.compile(r"\b(?:sign\w*|firm\w*|autoriz\w*|authoriz\w*|authoris\w*)\b", re.I)
_DECISION_WORDS = re.compile(r"\b(?:decisions?|decide|decision(?:es)?|decid\w+|tom\w+ decisiones)\b", re.I)


def _do_not_lines(text):
    up = text.upper()
    i = up.find("DO NOT DO")
    if i < 0:
        return []
    rest = text[i + len("DO NOT DO"):]
    j = min([k for k in (rest.upper().find(h) for h in ("GATHER THESE", "WHAT TO BRING", "DO TONIGHT")) if k >= 0] or [len(rest)])
    return [l.strip() for l in rest[:j].splitlines() if re.match(r"\s*(?:[-•*]|\d+[.)])\s*\S", l)]


def do_not_directives(p, text, ctx):
    """A DO NOT line may tell the family not to sign, or not to make a care decision, only if a vetted point says so.
    signing: allowed only when the vetted points contain the signing word. decisions: p['decisions'] = 'never' forbids it."""
    vetted = _fold(json.dumps(ctx.data, ensure_ascii=False))
    out = []
    for l in _do_not_lines(text):
        if p.get("signing") and _SIGN_WORDS.search(l):
            w = _fold(_SIGN_WORDS.search(l).group(0))[:4]
            if w not in vetted:
                out.append(g.R("ungrounded_claim", f"DO NOT line about signing that no vetted point supports: {l[:70]!r}"))
        if p.get("decisions") == "never" and _DECISION_WORDS.search(l):
            out.append(g.R("ungrounded_claim", f"DO NOT line directs a decision about care: {l[:70]!r}"))
    return out


def triage_facts_only(p, text, ctx):
    """Triage is for the pastor and must be facts from the intake. No advice, no claim about what is critical or what to preserve.
    A word the pastor wrote in the intake is allowed."""
    intake = _fold(getattr(ctx.state, "intake", "") or "")
    hits = []
    for m in re.finditer(p["pattern"], text, re.I):
        if _fold(m.group(0)) not in intake:
            hits.append(m.group(0).lower())
    return [g.R("advice", f"triage must state facts, not advice or claims about what matters: {sorted(set(hits))[:3]}")] if hits else []


REGISTRY = {f.__name__: f for f in (required_labels, numbered_after, cited_bullets, ends_with_referral,
                                    vetted_links_present, required_headings, max_words, no_agency_names, no_stock_phrases, no_endorsement_words,
                                    listed_contacts_known, network_entries_present, official_list_rules,
                                    no_unauthorized_promises, no_providence_claims, no_model_scripture, verse_block_verbatim,
                                    no_name_after_call, do_not_directives, triage_facts_only)}
