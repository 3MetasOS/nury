"""Read what pastors changed (data/feedback) and how runs behaved (data/ledger), and write a plain report with candidate
improvements. Nothing in this script changes Nury. A candidate is a draft in candidates/<id>.md with status "proposed".

    cd code && python3 tools/learning_report.py --out ../documents/product/LEARNING_REPORT.md
    cd code && python3 tools/learning_report.py --feedback DIR --ledger DIR --candidates ../candidates --synthetic

Each candidate has a TYPE (prompt_line, new_rule, new_jev_question, new_scenario), the evidence counts that justify it, and a
draft change. It needs at least --min (default 3) separate pastor edits before it is proposed. Evidence below that is only listed.
"""
import argparse
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import candidates as cand  # noqa: E402
from nury import feedback as fb  # noqa: E402
from nury import ledger  # noqa: E402

REPO = HERE.parents[1]


def _prompt_path(playbook, stage):
    try:
        for s in json.loads((REPO / "code" / "playbooks" / playbook / "stages.json").read_text()):
            if s["id"] == stage:
                return f"code/playbooks/{playbook}/{s['prompt']}"
    except Exception:
        pass
    return f"code/playbooks/{playbook}/prompts/{stage}.txt"


def _ngrams(sentence, n=3):
    words = [w for w in re.findall(r"[\w'\[\]]+", sentence.lower())]
    out = set()
    for i in range(len(words) - n + 1):
        g = words[i:i + n]
        if any("[" in w or "]" in w or any(c.isdigit() for c in w) for w in g):
            continue
        out.add(" ".join(g))
    return out


def analyze(rows, ledger_rows=None, min_evidence=3):
    gates = [r for r in rows if r.get("type") == "gate"]
    chips = [r for r in rows if r.get("type") == "chip"]
    outcomes = [r for r in rows if r.get("type") == "outcome"]
    by = defaultdict(list)
    for g in gates:
        by[(g.get("playbook") or "unknown", g["stage"])].append(g)
    stages = {}
    for key, gs in sorted(by.items()):
        edits = [g for g in gs if g["action"] == "edit"]
        c = Counter()
        for g in gs:
            if g.get("reason_chip"):
                c[g["reason_chip"]] += 1
        for ch in chips:
            if (ch.get("playbook") or "unknown", ch["stage"]) == key:
                c[ch["reason_chip"]] += 1
        tags = Counter(t for g in edits for t in g.get("tags", []))
        seen_cat = sum(1 for g in edits if g.get("rule_categories"))
        seen_unc = sum(1 for g in edits if any("uncertain" in d["decisions"] or "reject" in d["decisions"] for d in g.get("jev", {}).values()))
        grams = Counter()
        for g in edits:
            d = g.get("diff") or {}
            sents = list(d.get("removed", [])) + [p["from"] for p in d.get("replaced", [])]
            for gram in set().union(*[_ngrams(s) for s in sents]) if sents else set():
                grams[gram] += 1
        wa = [g["counts"]["words_after"] for g in edits if g.get("counts") and "shorter" in g.get("tags", [])]
        stages[key] = {"gates": len(gs), "approved": sum(1 for g in gs if g["action"] == "approve"), "edited": len(edits),
                       "stopped": sum(1 for g in gs if g["action"] == "stop"), "edit_rate": round(len(edits) / len(gs), 3) if gs else None,
                       "tags": dict(tags), "chips": dict(c), "edits_with_rule_rejections_seen": seen_cat,
                       "edits_with_jev_uncertain_or_reject": seen_unc, "dropped_unsafe": sum(g.get("dropped_unsafe", 0) for g in gs),
                       "common_removed_phrases": [(p, n) for p, n in grams.most_common(5) if n >= min_evidence],
                       "words_after_when_shorter": wa, "modes": sorted({g["mode"] for g in gs}), "sentences_available": any("diff" in g for g in gs)}
    oc = defaultdict(Counter)
    for o in outcomes:
        oc[o.get("playbook") or "unknown"][o["revision_result"]] += 1
    for g in gates:
        if g.get("revision_result"):
            oc[g.get("playbook") or "unknown"][g["revision_result"]] += 0
    led = None
    if ledger_rows:
        ls = [r for r in ledger_rows if r["type"] == "stage"]
        led = {"stage_lines": len(ls), "escalated_stages": sum(1 for s in ls if s["escalated"]),
               "avg_attempts": round(sum(s["attempts"] for s in ls) / len(ls), 2) if ls else None}
    return {"gates": len(gates), "edits": sum(1 for g in gates if g["action"] == "edit"), "stages": stages,
            "outcomes": {k: dict(v) for k, v in oc.items()}, "ledger": led, "min": min_evidence,
            "modes": sorted({g["mode"] for g in gates}), "degraded": sum(1 for g in gates if g.get("degraded"))}


def candidates_from(a, today, synthetic, start=1):
    out, n = [], start
    N = a["min"]

    def cid(slug):
        nonlocal n
        s = f"c-{n:04d}-{slug}"
        n += 1
        return s
    for (pb, stage), s in a["stages"].items():
        short_n = max(s["tags"].get("shorter", 0), s["chips"].get("too_long", 0))
        if short_n >= N and s["words_after_when_shorter"]:
            target = max(50, int(statistics.median(s["words_after_when_shorter"]) // 5 * 5))
            line = f"Keep it to about {target} words.\n"
            meta = cand.new_meta(cid(f"{pb}-{stage}-length"), "prompt_line",
                                 {"playbook": pb, "stage": stage, "edits": s["edited"], "edits_shorter": s["tags"].get("shorter", 0),
                                  "chip_too_long": s["chips"].get("too_long", 0), "target_words": target}, today, synthetic)
            out.append((meta, f"Shorter {stage} drafts for {pb}", f"In {s['edited']} edits of the {stage} stage, {s['tags'].get('shorter', 0)} made the text shorter and "
                        f"{s['chips'].get('too_long', 0)} pastors tapped 'Too long'. The median length of the shortened versions was {target} words.",
                        [{"kind": "append", "file": _prompt_path(pb, stage), "text": "\n" + line}], ""))
        chosen = []
        for gram, count in s["common_removed_phrases"]:
            if any(len(set(gram.split()) & set(c.split())) >= 2 for c in chosen):
                continue                                   # overlaps a phrase already proposed: it is the same finding
            if len(chosen) >= 2:
                break
            chosen.append(gram)
            words = gram.split()
            pat = r"\b" + r"\s+".join(re.escape(w) for w in words) + r"\b"
            meta = cand.new_meta(cid(f"{pb}-{stage}-phrase"), "new_rule",
                                 {"playbook": pb, "stage": stage, "phrase_words": len(words), "edits_removing_it": count, "edits": s["edited"]}, today, synthetic)
            out.append((meta, f"Pastors remove the phrase '{gram}' in {stage}", f"{count} of {s['edited']} edits removed or replaced a sentence containing '{gram}'.",
                        [{"kind": "json_append", "file": f"code/playbooks/{pb}/playbook.json", "key": "extra_banned",
                          "value": {"pattern": pat, "why": "pastors removed this phrase in the learning loop (candidate: review before use)"}}],
                        "\nCaution: `extra_banned` applies to every stage of the playbook, not only this one. A person decides if a ban or a prompt line is the better fix.\n"))
        voice = s["chips"].get("not_my_voice", 0) + s["chips"].get("wrong_tone", 0)
        if voice >= N:
            meta = cand.new_meta(cid(f"{pb}-{stage}-voice"), "prompt_line",
                                 {"playbook": pb, "stage": stage, "chip_not_my_voice": s["chips"].get("not_my_voice", 0),
                                  "chip_wrong_tone": s["chips"].get("wrong_tone", 0), "edits": s["edited"]}, today, synthetic)
            out.append((meta, f"Voice or tone of {stage} drafts for {pb}", f"{voice} chips said 'Not my voice' or 'Wrong tone' on this stage.", [],
                        "\nA person reads the replaced sentences in the feedback file (if sentence mode was on), writes one prompt line, and adds it as a change block.\n"))
        if s["chips"].get("inaccurate", 0) >= N and s["edits_with_jev_uncertain_or_reject"] >= N:
            meta = cand.new_meta(cid(f"{pb}-{stage}-accuracy"), "new_jev_question",
                                 {"playbook": pb, "stage": stage, "chip_inaccurate": s["chips"]["inaccurate"],
                                  "edits_where_jev_was_uncertain_or_rejected": s["edits_with_jev_uncertain_or_reject"]}, today, synthetic)
            out.append((meta, f"Accuracy in {stage} drafts for {pb}", f"{s['chips']['inaccurate']} pastors tapped 'Inaccurate', and Jev was uncertain or rejected in "
                        f"{s['edits_with_jev_uncertain_or_reject']} of the edited drafts.", [],
                        "\nThis may be a Jev question or its criteria (shared wording in `nury/jev_gate.py` and `evaluations/judges/jev_judges.py`). Write it by hand, validate it on stored drafts, then propose it.\n"))
    for pb, o in a["outcomes"].items():
        bad = o.get("did_not_go_as_hoped", 0)
        if bad >= N:
            meta = cand.new_meta(cid(f"{pb}-outcome"), "new_scenario",
                                 {"playbook": pb, "revisions_did_not_go_as_hoped": bad, "revisions_total": sum(o.values())}, today, synthetic)
            slug = f"{pb}-after-outcome-review"
            yaml_text = (f"id: {slug}\nnumber: 99\nplaybook: {pb}\ncategory: workflow\ntitle: TODO a fictional case like those that did not go as hoped\n"
                         f"intake: TODO a person writes a fictional intake. Do not paste anything from a real case.\noutput_language: es\n"
                         f"pastor_actions: {{1: approve, 2: approve, 3: approve, 4: approve, 5: approve}}\nexpected_behavior: TODO\n"
                         f"pass_criteria:\n  deterministic: [banned_phrases, disclaimers, allowlist, language, workflow, completeness]\n  jev_noul: {{}}\n  jev_score: {{}}\n"
                         f"fault_injection: null\nflags: {{}}\n")
            out.append((meta, f"A scenario for {pb} cases that did not go as hoped", f"{bad} of {sum(o.values())} 'Something changed' answers for {pb} said it did not go as hoped.",
                        [{"kind": "add_file", "file": f"evaluations/scenarios/99-{slug}.yaml", "content": yaml_text}],
                        "\nThe draft scenario contains TODO fields and cannot run until a person writes a fictional intake. The test script refuses a candidate that still has TODO in a new file.\n"))
    return out


def _show(p):
    """A path for the report: relative to the repository when it is inside it, so no home folder is printed."""
    try:
        return str(Path(p).resolve().relative_to(REPO))
    except Exception:
        return Path(str(p)).name


def render(a, cands, synthetic, fb_dir, led_dir):
    L = ["# Learning report", ""]
    if synthetic:
        L += ["> **SYNTHETIC DATA.** This report was built from synthetic scenarios (scenario 16, pastor edits a stage, and the revision scenarios), not from any real pastor. "
              "No real pastor has used Nury. It shows how the loop works, not what pastors want.", ""]
    L += ["Nothing in this report changes Nury. A candidate is a proposal. A person approves it in its review file, it passes the before and after test, "
          "and it ships in a normal release.", "",
          f"- Feedback read from: `{_show(fb_dir)}`. Modes seen: {', '.join(a['modes']) or 'none'}. Lines that fell back to counts for lack of a pseudonymizer: {a['degraded']}.",
          f"- Gate lines: {a['gates']}. Edits: {a['edits']}. Evidence needed for a candidate: at least {a['min']} separate edits or chips.", ""]
    if "counts" in a["modes"] and "sentences" not in a["modes"]:
        L += ["**Counts mode only:** the feedback file holds no sentences, so this report can say how often and how much pastors changed things, never what they wrote. "
              "Candidates that need the words (a banned phrase, a voice line) cannot be proposed.", ""]
    L += ["## What pastors changed, by crisis and stage", "",
          "| Crisis | Stage | Gates | Edited | Edit rate | Shorter | Longer | Chips | Edits where a rule had rejected a draft | Edits where Jev was uncertain or rejected |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for (pb, st), s in a["stages"].items():
        chips = ", ".join(f"{fb.CHIP_LABELS.get(k, k)} {v}" for k, v in sorted(s["chips"].items())) or "none"
        L.append(f"| {pb} | {st} | {s['gates']} | {s['edited']} | {s['edit_rate']} | {s['tags'].get('shorter', 0)} | {s['tags'].get('longer', 0)} | {chips} | "
                 f"{s['edits_with_rule_rejections_seen']} | {s['edits_with_jev_uncertain_or_reject']} |")
    if a["outcomes"]:
        L += ["", "## 'Something changed' answers", "", "| Crisis | Went as hoped | Did not go as hoped | Unknown |", "|---|---|---|---|"]
        for pb, o in sorted(a["outcomes"].items()):
            L.append(f"| {pb} | {o.get('went_as_hoped', 0)} | {o.get('did_not_go_as_hoped', 0)} | {o.get('unknown', 0)} |")
    if a["ledger"]:
        L += ["", f"Run ledger (`{_show(led_dir)}`): {a['ledger']['stage_lines']} stage lines, {a['ledger']['escalated_stages']} escalated, {a['ledger']['avg_attempts']} attempts on average."]
    L += ["", "## Candidate improvements", ""]
    if not cands:
        L.append(f"None. No pattern reached {a['min']} separate edits or chips.")
    for meta, title, why, changes, extra in cands:
        L += [f"### {meta['id']}: {title}", "", f"- TYPE: **{meta['type']}**   STATUS: {meta['status']}", f"- Evidence: {json.dumps(meta['evidence'])}", f"- Why: {why}",
              f"- Draft change: {'a change block (see the candidate file)' if changes else 'none yet: a person writes it'}", ""]
        for c in changes:
            L += ["```", json.dumps(c, ensure_ascii=False, indent=1)[:900], "```", ""]
    L += ["## Dropped for safety", "", f"Sentences dropped because they still looked like a protected value or a name: "
          f"{sum(s['dropped_unsafe'] for s in a['stages'].values())}. They are counted, never stored.", ""]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--feedback", default=None)
    ap.add_argument("--ledger", default=None)
    ap.add_argument("--out", default=str(REPO / "documents/product/LEARNING_REPORT.md"))
    ap.add_argument("--candidates", default=None, help="write proposed candidate files here (never overwrites)")
    ap.add_argument("--min", type=int, default=3)
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--today", default=str(date.today()))
    a = ap.parse_args(argv)
    rows = fb.read_all(a.feedback)
    lrows = ledger._read(a.ledger)
    an = analyze(rows, lrows, a.min)
    cs = candidates_from(an, a.today, a.synthetic)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(render(an, cs, a.synthetic, a.feedback or fb.DEFAULT_DIR, a.ledger or ledger.DEFAULT_DIR), encoding="utf-8")
    written = []
    if a.candidates:
        Path(a.candidates).mkdir(parents=True, exist_ok=True)
        for meta, title, why, changes, extra in cs:
            f = Path(a.candidates) / f"{meta['id']}.md"
            if not f.exists():
                f.write_text(cand.render(meta, title, why, changes, extra), encoding="utf-8")
                written.append(f.name)
    print(f"report: {a.out}; candidates proposed: {len(cs)}; files written: {written}")
    return an, cs


if __name__ == "__main__":
    main()
