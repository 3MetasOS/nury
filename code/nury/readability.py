"""Advisory reading-level numbers for family-facing drafts. Standard library only.

The formulas and the syllable heuristic are hack-ninja's documents/product/readability_check.py, copied here so the
engine can use them (tests/test_readability.py proves the two give the same numbers). The numbers go to the audit
log as one event per stage. They never block a draft and never change a result: a formula is a tripwire, not proof.
English: Flesch-Kincaid grade. Spanish: Szigriszt-Pazos (INFLESZ). Syllables are a heuristic, about a grade off.
"""
import re

TARGET = {"en": "grade 8 or lower", "es": "INFLESZ 55 or higher"}


def words_of(text):
    return re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ']+", text)


def sentences_of(text):
    parts = [p for p in re.split(r"(?<=[.!?¿¡:;])\s+|\n+", text) if words_of(p)]
    return max(len(parts), 1)


def syll_en(w):
    w = w.lower()
    w = re.sub(r"[^a-z]", "", w)
    if not w:
        return 0
    n = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and not w.endswith(("le", "ee")) and n > 1:
        n -= 1
    return max(n, 1)


def syll_es(w):
    w = w.lower()
    strong, weak = "aeoáéó", "iuüíú"
    n, prev = 0, None
    for ch in w:
        if ch in strong or ch in weak:
            if prev is None:
                n += 1
            elif (prev in strong and ch in strong) or (prev in "íú" and ch in strong + weak) or (prev in strong + weak and ch in "íú"):
                n += 1  # hiatus
            # else diphthong: same syllable
            prev = ch
        else:
            prev = None
    return max(n, 1)


def measure(text, lang):
    ws = words_of(text)
    W, S = max(len(ws), 1), sentences_of(text)
    sy = sum((syll_es if lang == "es" else syll_en)(w) for w in ws)
    m = {"words": len(ws), "sentences": S, "words_per_sentence": round(W / S, 1), "syll_per_word": round(sy / W, 2)}
    if lang == "en":
        m["fk_grade"] = round(0.39 * W / S + 11.8 * sy / W - 15.59, 1)
        m["flesch_ease"] = round(206.835 - 1.015 * W / S - 84.6 * sy / W, 1)
    else:
        P = 100 * sy / W  # syllables per 100 words
        m["fernandez_huerta"] = round(206.84 - 0.60 * P - 1.02 * (W / S), 1)
        m["szigriszt"] = round(206.835 - 62.3 * sy / W - W / S, 1)
    return m


def of_draft(text, lang):
    """measure() on a draft with markdown links and code spans reduced to their words. Never raises."""
    try:
        clean = re.sub(r"`[^`]*`|\[([^\]]*)\]\([^)]*\)", r"\1", text or "")
        m = measure(clean, "es" if lang == "es" else "en")
        m["lang"] = "es" if lang == "es" else "en"
        m["target"] = TARGET[m["lang"]]
        m["meets_target"] = m["fk_grade"] <= 8.0 if m["lang"] == "en" else m["szigriszt"] >= 55.0
        return m
    except Exception:
        return None
