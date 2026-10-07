"""What the pastor changed, recorded so a person can learn from it. Off unless NURY_FEEDBACK is set.

    NURY_FEEDBACK=off      (default) nothing is recorded.
    NURY_FEEDBACK=on       the diff is stored at sentence level: only the sentences that CHANGED (removed, added,
                           replaced), never a whole draft, and only after the Pseudonymizer has turned names and
                           identifiers into tokens. The file therefore holds TOKENIZED TEXT.
    NURY_FEEDBACK=counts   the stricter mode: only counts and edit-type tags. No sentence is stored at all.

The consent sentence the app shows when this is on is CONSENT_SENTENCE.

Rules this file keeps:
- Whole drafts are never stored. Quoted Scripture is never stored (a changed verse is only a tag).
- Every sentence is checked before it is stored. If it still holds a protected value, a name-like word, or anything the
  Pseudonymizer would still tokenize, the change is DROPPED and counted (dropped_unsafe). Fail closed.
- If there is no Pseudonymizer to use, sentence mode degrades to counts for that line (degraded: true).
- Every field that is not a changed sentence must be a number, a bool, null or a short slug.
- A feedback failure never breaks a run: record_* return False.
- Files are daily (feedback-YYYYMMDD.jsonl) so retention is deleting old files (prune).

Nothing here changes a prompt, a rule or a threshold. A person reads the learning report and decides.
"""

import difflib
import json
import os
import re
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import ledger
from . import privacy as pv
from . import scripture

DEFAULT_DIR = "data/feedback"
CONSENT_SENTENCE = ("Nury also records what you change, without names, to improve its drafts; "
                    "a person reviews every change before it is used.")
ACTIONS = ("approve", "edit", "stop")
CHIPS = ("good_as_is", "too_long", "not_my_voice", "wrong_tone", "inaccurate")
CHIP_LABELS = {"good_as_is": "Good as is", "too_long": "Too long", "not_my_voice": "Not my voice",
               "wrong_tone": "Wrong tone", "inaccurate": "Inaccurate"}
REVISION_RESULTS = {"went as hoped": "went_as_hoped", "did not go as hoped": "did_not_go_as_hoped", "unknown": "unknown"}
MAX_SENTENCES = 12
MAX_SENTENCE_CHARS = 400
_LOCK = threading.Lock()
_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
_DISCLAIMER = re.compile(r"^\s*Nury (?:is an AI assistant|es un asistente de IA)", re.I)
_LABEL = re.compile(r"^\s*(?:Nury draft for pastor review|Borrador de Nury para revisi[oó]n del pastor)\s*$", re.I)
_BULLET = re.compile(r"^\s*(?:[-•*]|\d+[.)])\s+")


def mode():
    v = (os.environ.get("NURY_FEEDBACK") or "off").strip().lower()
    return "sentences" if v in ("on", "sentences", "1", "true") else "counts" if v == "counts" else "off"


def feedback_dir(root=None):
    return Path(root or os.environ.get("NURY_FEEDBACK_DIR") or DEFAULT_DIR)


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


# ---------- turning two texts into a structured diff ----------

def sentences(text):
    """The text's own sentences, without the label, the disclaimer paragraph, bullets or the verse block."""
    t = scripture.strip_block(text or "")
    out = []
    for para in re.split(r"\n\s*\n", t):
        if _DISCLAIMER.match(para) or _LABEL.match(para.strip()):
            continue
        for s in _SPLIT.split(para):
            s = _BULLET.sub("", s).strip()
            if s and not _LABEL.match(s):
                out.append(re.sub(r"\s+", " ", s))
    return out


def _words(ss):
    return sum(len(s.split()) for s in ss)


def diff_sentences(before, after):
    """(removed, added, replaced) as lists, from two lists of sentences."""
    norm = lambda ss: [re.sub(r"\W+", " ", s.lower()).strip() for s in ss]  # noqa: E731
    a, b = norm(before), norm(after)
    removed, added, replaced = [], [], []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if op == "delete":
            removed += before[i1:i2]
        elif op == "insert":
            added += after[j1:j2]
        elif op == "replace":
            n = min(i2 - i1, j2 - j1)
            replaced += [{"from": before[i1 + k], "to": after[j1 + k]} for k in range(n)]
            removed += before[i1 + n:i2]
            added += after[j1 + n:j2]
    return removed, added, replaced


def _safe(sentence, ps):
    """True only if the sentence is fine to store. It must already be pseudonymized."""
    if not sentence or len(sentence) > MAX_SENTENCE_CHARS:
        return False
    have = len(pv._ANY_TOKEN.findall(sentence))
    if len(pv._ANY_TOKEN.findall(pv.Pseudonymizer().pseudonymize(sentence, names=False))) != have:
        return False                                   # an address, phone, email, date or ID is still in it
    if any(t.get("kind") == "person" and t.get("suggested") for t in pv.propose_terms(sentence)):
        return False                                   # a name-like word is still in it
    low = sentence.lower()
    for term in (ps.terms() if ps is not None else []):
        words = term if isinstance(term, str) else str(term)
        if len(words) > 2 and words.lower() in low:
            return False                               # a protected term the pastor named is still in it
    return True


def _ps(privacy_client):
    if privacy_client is None or not getattr(privacy_client, "enabled", False):
        return None
    return getattr(privacy_client, "ps", None)


def _tag_list(before, after, removed, added, replaced, verse_changed):
    wb, wa = _words(before), _words(after)
    tags = ["shorter" if wa < wb * 0.9 else "longer" if wa > wb * 1.1 else "same_length"]
    if removed:
        tags.append("sentences_removed")
    if added:
        tags.append("sentences_added")
    if replaced:
        tags.append("sentences_replaced")
    if verse_changed:
        tags.append("verse_changed")
    return tags


def _events_for(stage_id, events):
    cats, jev = {}, {}
    for e in events or []:
        if e.get("stage") != stage_id:
            continue
        if e.get("kind") == "draft_rejected":
            for c in e.get("reason_categories") or []:
                cats[c] = cats.get(c, 0) + 1
        if e.get("kind") == "jev_gate" and e.get("question") not in (None, "*"):
            d = jev.setdefault(e["question"], {"decisions": {}, "probs": []})
            d["decisions"][e["decision"]] = d["decisions"].get(e["decision"], 0) + 1
            if e.get("probability") is not None:
                d["probs"].append(round(float(e["probability"]), 3))
    return cats, jev


def build_line(stage, action, draft_text, final_text, privacy_client, audit_events, outcome_label=None, reason_chip=None,
               playbook=None, language=None, run_id=None, force_mode=None):
    m = force_mode or mode()
    stage_id = getattr(stage, "stage_id", stage)
    if action not in ACTIONS:
        raise ledger.LedgerError("unknown action")
    chip = reason_chip if reason_chip in CHIPS else None
    label = REVISION_RESULTS.get(outcome_label, outcome_label if outcome_label in REVISION_RESULTS.values() else None)
    ps = _ps(privacy_client)
    degraded = False
    if m == "sentences" and ps is None:
        m, degraded = "counts", True                   # nothing to pseudonymize with: store counts only
    line = {"type": "gate", "ts": _now(), "run": run_id, "playbook": playbook, "stage": stage_id, "language": language,
            "mode": m, "action": action, "reason_chip": chip, "revision_result": label, "degraded": degraded,
            "counts": None, "tags": [], "rule_categories": {}, "jev": {}, "dropped_unsafe": 0}
    line["rule_categories"], line["jev"] = _events_for(stage_id, audit_events)
    if action == "edit" and final_text is not None:
        before, after = sentences(draft_text), sentences(final_text)
        if ps is not None:
            before, after = [ps.pseudonymize(s) for s in before], [ps.pseudonymize(s) for s in after]
        removed, added, replaced = diff_sentences(before, after)
        verse_changed = scripture.BLOCK_RE.search(draft_text or "") is not None and \
            (scripture.BLOCK_RE.search(final_text or "") is None or
             scripture.BLOCK_RE.search(draft_text).group(0) != scripture.BLOCK_RE.search(final_text).group(0))
        line["counts"] = {"words_before": _words(before), "words_after": _words(after), "sentences_before": len(before),
                          "sentences_after": len(after), "removed": len(removed), "added": len(added), "replaced": len(replaced)}
        line["tags"] = _tag_list(before, after, removed, added, replaced, verse_changed)
        if m == "sentences":
            dropped = 0
            keep_r, keep_a, keep_p = [], [], []
            for s_ in removed[:MAX_SENTENCES]:
                if _safe(s_, ps):
                    keep_r.append(s_)
                else:
                    dropped += 1
            for s_ in added[:MAX_SENTENCES]:
                if _safe(s_, ps):
                    keep_a.append(s_)
                else:
                    dropped += 1
            for p_ in replaced[:MAX_SENTENCES]:
                if _safe(p_["from"], ps) and _safe(p_["to"], ps):
                    keep_p.append(p_)
                else:
                    dropped += 1
            line["diff"] = {"removed": keep_r, "added": keep_a, "replaced": keep_p}
            line["dropped_unsafe"] = dropped
    return line


def _check(line):
    shell = {k: v for k, v in line.items() if k != "diff"}
    ledger._check_clean(shell)
    d = line.get("diff")
    if d is not None:
        if sorted(d) != ["added", "removed", "replaced"]:
            raise ledger.LedgerError("bad diff shape")
        for s in d["removed"] + d["added"]:
            if not isinstance(s, str):
                raise ledger.LedgerError("diff sentence is not text")
        for p in d["replaced"]:
            if sorted(p) != ["from", "to"]:
                raise ledger.LedgerError("bad replaced pair")


def _write(line, root=None):
    _check(line)
    d = feedback_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    name = "feedback-" + datetime.now(timezone.utc).strftime("%Y%m%d") + ".jsonl"
    with _LOCK, open(d / name, "a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False, sort_keys=True) + "\n")


def record_gate(stage, action, draft_text, final_text, privacy_client, audit_events, outcome_label=None, reason_chip=None,
                playbook=None, language=None, run_id=None, root=None):
    """The server calls this at each gate. Returns True if a line was written. Never raises."""
    if mode() == "off":
        return False
    try:
        _write(build_line(stage, action, draft_text, final_text, privacy_client, audit_events, outcome_label, reason_chip,
                          playbook, language, run_id), root)
        return True
    except Exception:
        return False


def record_chip(stage, chip, playbook=None, language=None, run_id=None, root=None):
    """The pastor taps a reason chip after the gate (POST /api/feedback). One small line."""
    if mode() == "off" or chip not in CHIPS:
        return False
    try:
        _write({"type": "chip", "ts": _now(), "run": run_id, "playbook": playbook, "stage": getattr(stage, "stage_id", stage),
                "language": language, "reason_chip": chip}, root)
        return True
    except Exception:
        return False


def record_outcome(playbook, result, language=None, root=None):
    """The 'Something changed' answer: went as hoped, did not go as hoped, unknown. The pastor's note is NOT stored."""
    label = REVISION_RESULTS.get(result, result if result in REVISION_RESULTS.values() else None)
    if mode() == "off" or label is None:
        return False
    try:
        _write({"type": "outcome", "ts": _now(), "playbook": playbook, "language": language, "revision_result": label}, root)
        return True
    except Exception:
        return False


# ---------- reading and retention ----------

def read_all(root=None, since=None):
    d = feedback_dir(root)
    if not d.is_dir():
        return []
    cut = ledger._since(since)
    out = []
    for f in sorted(d.glob("feedback-*.jsonl")):
        for ln in f.read_text(encoding="utf-8").splitlines():
            try:
                x = json.loads(ln)
            except ValueError:
                continue
            if cut is None or x.get("ts", "") >= cut:
                out.append(x)
    return out


def prune(days, root=None):
    """Retention: delete daily files older than `days`. This is the only way a feedback file is ever removed."""
    d = feedback_dir(root)
    gone = []
    if not d.is_dir():
        return gone
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y%m%d")
    for f in d.glob("feedback-*.jsonl"):
        if f.stem.split("-")[1] < cutoff:
            f.unlink()
            gone.append(f.name)
    return gone
