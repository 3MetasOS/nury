"""Privacy layer: pseudonymize before anything leaves the device.

PrivacyClient wraps the Gloo client (the engine already takes `client=`, so the core does not change).

  Outbound  names the pastor protected, phones, emails, street addresses, dates, A-numbers, case
            numbers and ID numbers become stable tokens: [PERSON_1], [PHONE_1], [ADDRESS_1] ...
  Mapping   stays local, in memory (and in the case file on the pastor's machine). Never sent.
  Inbound   the reply is detokenized locally. Mangled tokens ([PERSON 1], PERSON_1) are repaired.
            A token the map does not know makes the client ask again (max 2 more calls); if it still
            fails the token becomes [?] so the pastor sees a gap at the gate, never a stray token.

Honest limit: this removes direct identifiers. Context ("14 years", "his workplace") can still
hint at who a person is. Cities and states are kept on purpose; street addresses are not.
"""

import os
import re
import unicodedata

_TYPES = ("PERSON", "PLACE", "PHONE", "EMAIL", "ADDRESS", "DOB", "DATE", "ANUMBER", "CASE", "ID")
_T = "|".join(_TYPES)
_BRACKETED = re.compile(r"\[\s*(" + _T + r")[\s_\-]*(\d+)\s*\]", re.I)
_BARE = re.compile(r"(?<![\[\w])(" + _T + r")_(\d+)\b(?!\])", re.I)
_ANY_TOKEN = re.compile(r"\[(?:" + _T + r")_\d+\]")

_ACC = {"a": "aáàäâã", "e": "eéèëê", "i": "iíìïî", "o": "oóòöôõ", "u": "uúùüû", "n": "nñ", "c": "cç"}

_MONTHS = ("january|february|march|april|may|june|july|august|september|october|november|december|"
           "jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec|enero|febrero|marzo|abril|mayo|junio|julio|"
           "agosto|septiembre|setiembre|octubre|noviembre|diciembre")
_YEAR = r"(?:19|20)\d{2}"
_DATE_PATTERNS = [
    re.compile(r"(?<!\d)(?:0?[1-9]|1[0-2])[/.-](?:0?[1-9]|[12]\d|3[01])[/.-]" + _YEAR + r"(?!\d)"),
    re.compile(r"(?<!\d)(?:0?[1-9]|[12]\d|3[01])[/.-](?:0?[1-9]|1[0-2])[/.-]" + _YEAR + r"(?!\d)"),
    re.compile(r"(?<!\d)" + _YEAR + r"-\d{2}-\d{2}(?!\d)"),
    re.compile(r"\b(?:" + _MONTHS + r")\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+" + _YEAR + r"\b", re.I),
    re.compile(r"\b\d{1,2}\s+de\s+(?:" + _MONTHS + r")\s+de\s+" + _YEAR + r"\b", re.I),
]
_DOB_CUE = re.compile(r"(born|dob|birth|birthday|nació|nacio|nacimiento|cumpleaños)[^.\n]{0,25}$", re.I)

_STREET = (r"(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Lane|Ln|Way|Court|Ct|Place|Pl|Highway|Hwy|"
           r"Calle|Avenida|Camino|Carretera)")
_ADDR_EN = re.compile(r"(?<!\w)\d{1,6}\s+(?:(?-i:[NSEW])\.?\s+|(?:North|South|East|West)\s+)?(?:(?-i:[A-Z0-9][\w'’.\-]*)\s+){0,3}?"
                      + _STREET + r"\b\.?(?:,?\s*(?:Apt|Apartment|Unit|Suite|Ste|#)\.?\s*[\w\-]+)?", re.I)
_ADDR_ES = re.compile(r"\b(?:Calle|Avenida|Av\.|Camino|Carretera)\s+(?:[\wÁÉÍÓÚÑáéíóúñ'’.\-]+\s+){0,3}?"
                      r"(?:#|No\.?|núm\.?|número)?\s*\d{1,6}\b(?:,?\s*(?:Apt|Apartamento|Depto|Unit|#)\.?\s*[\w\-]+)?", re.I)
_PO = re.compile(r"\bP\.?\s?O\.?\s+Box\s+\d+\b", re.I)
_EMAIL = re.compile(r"[\w.+\-]+@[\w\-]+(?:\.[\w\-]+)+")
_PHONE10 = re.compile(r"(?<![\w.])(?:\+?\d{1,3}[\s.-]?)?(?:\(\d{3}\)|\d{3})[\s.-]?\d{3}[\s.-]?\d{4}(?![\w])")
_PHONE7 = re.compile(r"(?<![\d.\-])\d{3}[-.\s]\d{4}(?![\d\-])")
_ANUM = re.compile(r"(?<![\w-])A[- ]?\d{8,9}(?!\d)")
_SSN = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")
_RECEIPT = re.compile(r"(?<![\w])[A-Z]{3}\d{10}(?!\d)")
_CASE = re.compile(r"(?i)\b(?:case|caso|receipt|recibo|expediente)\s*(?:number|no\.?|#|núm\.?|número|num\.?)?\s*[:#]?\s*"
                   r"((?=[A-Z0-9\-]*\d)[A-Z0-9][A-Z0-9\-]{5,})")

# Words that are capitalized but are not names. English and Spanish.
_STOP = set("""
a an the and or but if so as at by for from in into of on to with without about after before during over under
i you he she it we they me him her us them my your his its our their this that these those there here
is are was were be been being am do does did have has had will would can could may might must shall should
yes no not all any some one two three four five six seven eight nine ten
mr mrs ms dr sr sra señor señora doña don pastor reverend rev father padre hermano hermana brother sister
monday tuesday wednesday thursday friday saturday sunday lunes martes miércoles miercoles jueves viernes sábado sabado domingo
january february march april may june july august september october november december
enero febrero marzo abril mayo junio julio agosto septiembre setiembre octubre noviembre diciembre
today tonight tomorrow yesterday morning evening night hoy esta noche mañana manana ayer tarde
english spanish español espanol inglés ingles usa america american latino latina hispanic
god dios jesus jesús cristo christ biblia bible iglesia church salmo psalm señor lord amen espíritu
nury aila aclu hipaa cfr uscis dhs fbi ice cbp
she's he's it's i'm i've don't doesn't didn't can't won't isn't aren't wasn't weren't
el la los las un una unos unas y o pero si que de del al en con sin por para sobre entre desde hasta como cuando donde
yo tú tu usted ustedes él ella nosotros nosotras ellos ellas me te se lo le nos les mi mis su sus
es son era eran fue fueron ser estar está están estaba estaban estoy hay han ha he hemos
querida querido estimada estimado hola buenas gracias favor
dear hello hi thanks thank please sorry situation people location family language urgency missing facts
high medium low
what when where why how who whom whose which whether
qué que cómo como cuándo cuando dónde donde quién quien cuál cual cuánto cuanto
do tonight not gather these documents bring ask
write tell call ask say give take make keep let help find show send bring come go look wait think remember explain describe list answer respond use
please thanks thank sorry hello hi hey okay ok well now then also first second third finally however because while after before today
esto eso esta este estos estas aquello llame llama hable habla escriba escribe diga dime dígame digame ayude ayuda pida pide busque busca ponga pone
traiga trae venga vaya mire mira recuerde gracias hola buenas buen quiero necesito favor primero segundo tercero también tambien ahora entonces además
ademas pero porque cuando mientras después despues antes mucho muchas muchos mucha todo todos toda todas nada algo alguien nadie siempre nunca
""".split())
_PLACE_CUE = re.compile(r"\b(?:in|at|from|near|to|en|de|desde|cerca|hacia)\s+$", re.I)
_STATES = set("""alabama alaska arizona arkansas california colorado connecticut delaware florida georgia hawaii idaho illinois
indiana iowa kansas kentucky louisiana maine maryland massachusetts michigan minnesota mississippi missouri montana
nebraska nevada ohio oklahoma oregon pennsylvania tennessee texas utah vermont virginia washington wisconsin wyoming
mexico méxico""".split())
_PLACE_WORD = re.compile(r"^(?:hospital|medical|center|centre|clinic|church|iglesia|school|escuela|county|condado|"
                         r"street|avenue|city|ciudad)$", re.I)
_CAP = re.compile(r"[A-ZÁÉÍÓÚÑ][a-záéíóúñ'’]{2,}(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ'’]{2,}){0,2}")


def _norm(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn").casefold().strip()


def _accent_pattern(term):
    out = []
    for ch in term:
        base = _norm(ch)
        if base in _ACC:
            out.append("[" + _ACC[base] + _ACC[base].upper() + "]")
        elif ch.isspace():
            out.append(r"\s+")
        else:
            out.append(re.escape(ch))
    return "".join(out)


def propose_terms(text):
    """Candidate names for the pastor to confirm. [{term, kind, count, suggested}], most frequent first.

    kind is 'person' or 'place' (a guess). suggested is True for likely people and False for likely
    places (a state, or a word that follows in/at/from/en/de). The pastor's final list is what counts."""
    seen = {}
    _where = [None]
    text = Pseudonymizer().pseudonymize(text or "", names=False)     # addresses, phones, ids are not names
    for m in _CAP.finditer(text):
        phrase = m.group(0)
        _where[0] = _context(text, m.start(), m.end())
        words = phrase.split()
        while words and _norm(words[0]) in _STOP:
            words.pop(0)
        while words and _norm(words[-1]) in _STOP:
            words.pop()
        if not words or any(_norm(w) in _STOP for w in words):
            # keep only the non-stop words as separate candidates
            words = [w for w in words if _norm(w) not in _STOP]
            for w in words:
                _tally(seen, w, text, m.start(), m.end(), _where[0])
            continue
        _tally(seen, " ".join(words), text, m.start(), m.end(), _where[0])
    out = []
    for term, info in seen.items():
        # A lone capitalized word that only ever opens a sentence ("Write exactly that", "Please call") is usually
        # not a name. Keep it only if it also appears mid-sentence, follows a title, or is followed by a verb.
        if " " not in term and not info["mid"] and not info["title"] and not info["verbish"]:
            continue
        out.append({"term": term, "kind": info["kind"], "count": info["count"], "suggested": info["kind"] == "person"})
    return sorted(out, key=lambda x: (-x["count"], x["term"]))


_STATE_NEXT = re.compile(r"^,\s*([A-Za-zÁÉÍÓÚÑáéíóúñ]+)")


_TITLES = {"sr", "sra", "srta", "mr", "mrs", "ms", "miss", "dr", "dra", "don", "dona", "doña", "pastor", "pastora", "hermano", "hermana",
           "senor", "señor", "senora", "señora", "father", "padre", "madre", "sister", "brother"}
_AUX = {"is", "was", "has", "had", "said", "told", "asked", "es", "esta", "está", "tiene", "dijo", "dice", "fue", "era", "llamo", "llamó",
        "called", "wants", "quiere", "says", "needs", "necesita", "can", "does", "did", "are", "were", "lives", "vive", "works", "trabaja"}
_VERB_END = ("ed", "ió", "ó", "aron", "ieron", "ía", "aba", "ando", "iendo")


def _context(text, pos, end):
    """(is the word at the start of a sentence, does it follow a title, is the next word verb-like)."""
    before = text[:pos].rstrip()
    initial = (not before) or before[-1] in ".!?\n¿¡:;\"“"
    prev = re.findall(r"[\w']+", before[-20:])
    title = bool(prev) and _norm(prev[-1]) in {_norm(t) for t in _TITLES} and not initial
    nxt = re.match(r"\s*,?\s*([\w']+)", text[end:end + 40])
    nw = _norm(nxt.group(1)) if nxt else ""
    verbish = nw in {_norm(a) for a in _AUX} or nw.endswith(tuple(_norm(v) for v in _VERB_END)) and len(nw) > 3
    return initial, title, verbish


def _tally(seen, term, text, pos, end, ctx=None):
    key = _norm(term)
    kind = "person"
    first = key.split()[0] if key else ""
    nxt = _STATE_NEXT.match(text[end:end + 30])
    if (first in _STATES or _PLACE_CUE.search(text[max(0, pos - 12):pos]) or _PLACE_WORD.match(term.split()[-1])
            or (nxt and _norm(nxt.group(1)) in _STATES)):
        kind = "place"
    e = seen.setdefault(term, {"kind": kind, "count": 0, "mid": False, "title": False, "verbish": False})
    e["count"] += 1
    initial, title, verbish = ctx or (False, False, False)
    e["mid"] = e["mid"] or not initial
    e["title"] = e["title"] or title
    e["verbish"] = e["verbish"] or (initial and verbish)


class Pseudonymizer:
    """Stable tokens for one case. The map never leaves this object."""

    def __init__(self, protected=()):
        self._tok = {}       # (type, normalized value) -> token
        self._val = {}       # token -> original surface
        self._n = {}         # type -> counter
        self._terms = []     # [(regex, type, key)] longest first
        self._allow_digits = set()   # phones of vetted contacts (the church network): never tokenized
        self._allow_text = set()     # their links and emails
        for t in protected:
            if isinstance(t, dict):
                self.add_term(t["term"], t.get("kind", "person"))
            else:
                self.add_term(t)

    # --- protected terms ---
    def add_term(self, term, kind="person"):
        term = (term or "").strip()
        if len(term) < 2:
            return None
        typ = "PLACE" if kind == "place" else "PERSON"
        if typ == "PERSON" and " " in term:           # a full name also protects each part on its own
            for part in term.split():
                if len(part) >= 3 and _norm(part) not in _STOP:
                    self.add_term(part, kind)
        key = _norm(term)
        if any(k == key for _, _, k in self._terms):
            return self._tok.get((typ, key))
        rx = re.compile(r"(?<![\w])" + _accent_pattern(term) + r"(?![\w])", re.I)
        self._terms.append((rx, typ, key))
        self._terms.sort(key=lambda x: -len(x[2]))
        return self._token(typ, key, term)

    def terms(self):
        return [self._val[self._tok[(t, k)]] for _, t, k in self._terms if (t, k) in self._tok]

    def allow(self, literals):
        """Vetted contact details (a network entry's phone, link, email). They are professionals, not
        the family: they go to the model as they are and are never tokenized."""
        for x in literals or []:
            x = str(x or "").strip()
            if not x:
                continue
            d = re.sub(r"\D", "", x)
            if len(d) >= 7:
                self._allow_digits.add(d[-10:])
            self._allow_text.add(x.lower())

    def _allowed(self, surface):
        d = re.sub(r"\D", "", surface)
        return (len(d) >= 7 and d[-10:] in self._allow_digits) or surface.lower() in self._allow_text

    # --- tokens ---
    def _token(self, typ, key, surface):
        tk = self._tok.get((typ, key))
        if tk:
            return tk
        self._n[typ] = self._n.get(typ, 0) + 1
        tk = f"[{typ}_{self._n[typ]}]"
        self._tok[(typ, key)] = tk
        self._val[tk] = surface
        return tk

    def map(self):
        return dict(self._val)

    # --- outbound ---
    def pseudonymize(self, text, patterns=True, names=True):
        if not text:
            return text
        t = text
        self._stash = []
        if patterns:
            t = self._sub(t, _EMAIL, "EMAIL")
            t = self._sub(t, _SSN, "ID")
            t = self._sub(t, _ANUM, "ANUMBER")
            t = self._sub(t, _RECEIPT, "CASE")
            t = self._sub_group(t, _CASE, "CASE")
            for rx in _DATE_PATTERNS:
                t = self._sub_date(t, rx)
            for rx in (_ADDR_EN, _ADDR_ES, _PO):
                t = self._sub(t, rx, "ADDRESS")
            t = self._sub(t, _PHONE10, "PHONE")
            t = self._sub(t, _PHONE7, "PHONE")
        if names:
            for rx, typ, key in self._terms:
                t = rx.sub(lambda m, typ=typ, key=key: self._token(typ, key, m.group(0)), t)
        for i, v in enumerate(self._stash):          # put the vetted contact details back, exactly as they were
            t = t.replace(f"\ue000{i}\ue001", v)
        return t

    def _sub(self, t, rx, typ):
        def f(m):
            if self._allowed(m.group(0)):
                self._stash.append(m.group(0))       # later patterns must not cut into it
                return f"\ue000{len(self._stash) - 1}\ue001"
            return self._token(typ, _norm(m.group(0)), m.group(0))
        return rx.sub(f, t)

    def _sub_group(self, t, rx, typ):
        return rx.sub(lambda m: m.group(0)[: m.start(1) - m.start(0)] + self._token(typ, _norm(m.group(1)), m.group(1)), t)

    def _sub_date(self, t, rx):
        def f(m):
            cue = _DOB_CUE.search(t[max(0, m.start() - 40):m.start()])
            typ = "DOB" if cue else "DATE"
            return self._token(typ, _norm(m.group(0)), m.group(0))
        return rx.sub(f, t)

    # --- inbound ---
    def detokenize(self, text):
        """(text, unresolved). Repairs [PERSON 1], PERSON_1, [person_1]. Unknown tokens are reported."""
        unresolved = []

        def fix(m):
            tk = f"[{m.group(1).upper()}_{int(m.group(2))}]"
            if tk in self._val:
                return self._val[tk]
            unresolved.append(tk)
            return tk
        out = _BRACKETED.sub(fix, text or "")
        out = _BARE.sub(fix, out)
        return out, unresolved

    def has_tokens(self, text):
        return bool(_ANY_TOKEN.search(text or ""))


_NOTE = ("\n\nPRIVACY: Tokens such as [PERSON_1] or [PHONE_1] stand for real names and numbers that are hidden from you. "
         "Copy each token exactly as written, with the square brackets. Never translate, change, or invent a token. "
         "Use a token wherever you would write that name or number.")


class PrivacyClient:
    """Wraps a client with ask(user_input, instructions=None, **kw) -> (text, meta)."""

    MAX_FIX_CALLS = 2

    def __init__(self, inner, protected=(), enabled=True):
        self.inner = inner
        self.enabled = enabled
        self.ps = Pseudonymizer(protected)
        self.events = []          # no values: kinds, tokens, counts only

    @classmethod
    def from_intake(cls, inner, intake, accept="people", extra=(), enabled=True):
        """Protect every suggested candidate in the intake (for evals and tests). The app asks the pastor."""
        pc = cls(inner, [c for c in propose_terms(intake) if c["suggested"] or accept == "all"], enabled)
        for t in extra:
            pc.add_term(t)
        return pc

    def allow_network(self, entries):
        """Tell the privacy layer which phones and links belong to the pastor's vetted contacts."""
        from .network import literals
        self.ps.allow(literals(entries))

    def allow_playbook(self, pb):
        """One call per session: keep the vetted contact details of this run intact: the church network, the
        official list, and every phone and link in the playbook's own sources. (Not the family's.)"""
        import json as _json
        from .network import literals, load_network
        from .gloo_client import load_env  # noqa: F401
        lits = literals(load_network().list())
        f = pb.dir / "sources" / "official_list.json"
        if f.is_file():
            lits += literals(_json.loads(f.read_text(encoding="utf-8")).get("entries", []))
            lits += [e.get("email", "") for e in _json.loads(f.read_text(encoding="utf-8")).get("entries", [])]
        blob = _json.dumps(pb.sources, ensure_ascii=False)
        from .guardrails import allowed_urls_in
        lits += allowed_urls_in(blob) + re.findall(r"\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}", blob)
        self.ps.allow(lits)

    def add_term(self, term, kind="person"):
        tk = self.ps.add_term(term, kind)
        if tk:
            self.events.append({"event": "term_added", "token": tk})
        return tk

    def map(self):
        """token -> real value. Local only. Saved in the case file by casefile.save_case(privacy=...)."""
        return self.ps.map()

    def wrap_gate(self, gate):
        """Gate wrapper: names a pastor adds in an edit are protected before the next stage runs."""
        def wrapped(result):
            d = gate(result)
            if d.action == "edit" and d.text:
                known = {_norm(w) for t in self.ps.terms() for w in t.split()}
                for c in propose_terms(d.text):
                    words = [_norm(w) for w in c["term"].split()]
                    if c["suggested"] and not all(w in known for w in words) and self._mid_sentence(d.text, c["term"]):
                        self.add_term(c["term"], "person")
                        self.events.append({"event": "edit_name_protected", "stage": result.stage_id})
            return d
        return wrapped

    @staticmethod
    def _mid_sentence(text, term):
        i = text.find(term)
        if i <= 0:
            return False
        before = text[:i].rstrip()
        return bool(before) and before[-1] not in ".!?:\n¿¡"

    def ask(self, user_input, instructions=None, **kw):
        if not self.enabled:
            return self.inner.ask(user_input, instructions=instructions, **kw)
        out_in = self.ps.pseudonymize(user_input)
        # instructions hold the rules and vetted sources: protect names only, leave vetted phones and links alone
        out_ins = self.ps.pseudonymize(instructions, patterns=False) if instructions else instructions
        tokens_out = self.ps.has_tokens(out_in) or self.ps.has_tokens(out_ins or "")
        if tokens_out and out_ins is not None:
            out_ins = out_ins + _NOTE
        total = {"latency_s": 0.0, "input_tokens": 0, "output_tokens": 0}
        text, meta, calls, unresolved = "", {}, 0, []
        for _ in range(1 + self.MAX_FIX_CALLS):
            calls += 1
            text, meta = self.inner.ask(out_in, instructions=out_ins, **kw)
            for k in total:
                total[k] = round(total[k] + (meta.get(k) or 0), 3)
            text, unresolved = self.ps.detokenize(text)
            if not unresolved:
                break
            self.events.append({"event": "unknown_token", "tokens": sorted(set(unresolved))})
            out_ins = (out_ins or "") + ("\n\nYour last reply used tokens that do not exist: " + ", ".join(sorted(set(unresolved)))
                                         + ". The only valid tokens are: " + ", ".join(sorted(self.ps.map())) + ". Use only those, exactly as written.")
        if unresolved:
            for tk in set(unresolved):
                text = text.replace(tk, "[?]")
            self.events.append({"event": "token_dropped", "tokens": sorted(set(unresolved))})
        meta = dict(meta)
        meta.update(total)
        meta["privacy"] = {"tokens": len(self.ps.map()), "extra_calls": calls - 1}
        return text, meta

    def __getattr__(self, name):          # model, text_of, respond ... pass through to the inner client
        return getattr(self.inner, name)


def privacy_enabled(flag=None):
    """On by default. Off with NURY_PRIVACY=off or flag=False (for A/B runs)."""
    if flag is not None:
        return bool(flag)
    return os.environ.get("NURY_PRIVACY", "on").lower() not in ("off", "0", "false", "no")


def make_client(inner=None, protected=(), intake=None, enabled=None):
    """The client the app and the eval adapter should use. Returns a PrivacyClient (on) or the plain client (off).

    protected: the pastor's confirmed terms. intake: pass it instead when no pastor confirms (evals):
    every suggested person in the intake is protected."""
    from .gloo_client import GlooClient
    inner = inner or GlooClient()
    if not privacy_enabled(enabled):
        return inner
    if intake is not None:
        return PrivacyClient.from_intake(inner, intake, extra=list(protected))
    return PrivacyClient(inner, protected)
