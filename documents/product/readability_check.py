#!/usr/bin/env python3
"""Reading-level check for the family-facing page text. Standard library only.

Usage:  python3 readability_check.py FILE [--lang en|es]
        echo "text" | python3 readability_check.py - --lang es

English: Flesch-Kincaid grade and Flesch Reading Ease.
Spanish: Fernandez-Huerta and Szigriszt-Pazos (INFLESZ scale). Spanish has no grade level.
Syllables are counted with a simple heuristic, so scores are approximate (about one grade off).
Use it as a tripwire, not a verdict. Exit code 1 when the text misses the target.
"""
import re
import sys

TARGETS = {"en": ("grade <= 8", lambda m: m["fk_grade"] <= 8.0),
           "es": ("INFLESZ >= 55 (normal or easier)", lambda m: m["szigriszt"] >= 55.0)}


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


def main(argv):
    if not argv:
        print(__doc__); return 2
    lang = "en"
    if "--lang" in argv:
        lang = argv[argv.index("--lang") + 1]
    src = argv[0]
    text = sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()
    text = re.sub(r"`[^`]*`|\[([^\]]*)\]\([^)]*\)", r"\1", text)
    m = measure(text, lang)
    label, ok = TARGETS[lang]
    print(m)
    print(f"target {label}: {'PASS' if ok(m) else 'MISS'}")
    if m["words_per_sentence"] > 20:
        print("note: average sentence is over 20 words")
    return 0 if ok(m) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
