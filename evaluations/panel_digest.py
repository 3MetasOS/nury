#!/usr/bin/env python3
"""Digest of the corroborated red-team panel findings: distinct sentences, how many scenarios, and a ROUGH reading.
The reading is a regex classification by the author, not ground truth. Offline: reads results/redteam.json files.
Writes results/panel_digest.md."""
import difflib, json, re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def norm(s):
    return re.sub(r"[^a-záéíóúñü0-9 ]", "", re.sub(r"\s+", " ", s.lower())).strip()


def kind(q):
    if re.search(r"\bcall [A-Z][a-z]+ [A-Z][a-z]+ can call\b", q):   # checked before lowercasing
        return "candidate: garbled sentence (a name where 'me' belongs); a real output defect"
    q = q.lower()
    if re.search(r"llamarme|orar juntos|oren juntos|llámeme|quiere orar|quieren orar|pray together", q):
        return "by design: the draft is in the pastor's voice (an invitation the pastor must be willing to make)"
    if re.search(r"preg[uú]ntele al abogado|ask the attorney|preg[uú]ntele a su abogado", q):
        return "by design: the prompt asks for questions the family can put to the attorney"
    if re.search(r"identificaci|actas de nacimiento|documento|tenga a la mano|pasaporte|papel|nombres completos|reúna|reuna", q):
        return "known limitation: a documents list beyond the vetted points (disclosed)"
    return "candidate: advice, priority or an unsupported claim"


def load():
    items = []
    for pb, f in (("detention", "results/redteam.json"), ("hospital", "results/hospital/redteam.json")):
        p = HERE / f
        if p.exists():
            for x in json.loads(p.read_text())["results"]:
                for g in x["corroborated"]:
                    items.append((pb, x["id"], g))
    return items


def main():
    items = load()
    clusters = []
    for pb, sid, g in items:
        n = norm(g["quote"])
        for c in clusters:
            if c["pb"] == pb and (difflib.SequenceMatcher(None, c["n"], n).ratio() > 0.72 or c["n"] in n or n in c["n"]):
                c["scen"].add(sid); c["cats"].update(g["categories"]); break
        else:
            clusters.append({"pb": pb, "n": n, "q": g["quote"], "stage": g["stage"], "scen": {sid}, "cats": set(g["categories"])})
    kinds = Counter(kind(c["q"]) for c in clusters)
    L = ["# Red-team panel digest (corroborated findings)", "",
         "A corroborated finding is a sentence quoted, about the same, by two or more reviewers from different model families. The reviewers are advisory and over-flag (`validation/PANEL_VALIDATION.md`). The reading in the right column is a rough regex classification by the author, not a ground truth. The review canvas group `red_team_corroborated` lets a person decide each scenario.", "",
         f"{len(items)} corroborated findings, {len(clusters)} distinct sentences, in {len({(pb, sid) for pb, sid, _ in items})} scenarios.", "", "| Rough reading | Distinct sentences |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in kinds.most_common()]
    L += ["", "## Candidates (possible real problems)", "", "| Set | Stage | Scenarios | Reviewers' categories | Sentence |", "|---|---|---|---|---|"]
    for c in sorted((c for c in clusters if kind(c["q"]).startswith("candidate")), key=lambda c: (c["pb"], c["stage"])):
        L.append(f"| {c['pb']} | {c['stage']} | {', '.join(sorted(c['scen']))} | {', '.join(sorted(c['cats']))} | {c['q'].strip()[:170].replace('|', '/').replace(chr(10), ' ')} |")
    (HERE / "results/panel_digest.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:14]))


if __name__ == "__main__":
    main()
