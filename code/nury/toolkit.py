"""Read-only tools over Nury's rules, shared by the command line (nury.cli) and the MCP server (nury.mcp_server).

What this is for: another team can test its own drafts against our safety floor and named checks, and read our
scorecards, without running the pipeline. What it is not: it never calls a model, Jev or any service, reads no key,
writes no file, holds no case data, and has no way to start a run or reach a family. A draft you pass in stays in memory.

The checks here are the same functions the engine runs (nury.guardrails and nury.checks). The engine builds its context
from a case; here the context is empty on purpose: no intake, no approved earlier text, and the church network and the
official list are empty. So checks that compare a draft with those lists pass trivially, and Jev is not run.
tests/test_toolkit.py proves the verdicts equal the engine's for the same text."""
import json
import re
from pathlib import Path
from types import SimpleNamespace

from . import checks as checks_lib
from . import guardrails as g
from . import playbook as pbm
from . import rules
from . import scripture as scr

MAX_CHARS = 20_000
REPO = Path(__file__).resolve().parents[2]
RESULTS = {"detention": "evaluations/results/runs.json", "hospital": "evaluations/results/hospital/runs.json",
           "attacker": "evaluations/results/attacker/runs.json"}


class ToolError(Exception):
    """A request the tools refuse, in plain words. The CLI and the MCP server show the message."""


def _playbooks():
    return pbm.list_playbooks()


def list_playbooks():
    return [{"id": p["id"], "title": p["title"], "status": p["status"], "description": p["description"]} for p in _playbooks()]


def _load(pid):
    ids = [p["id"] for p in _playbooks() if p["status"] == "live"]
    if pid not in ids:
        raise ToolError(f"unknown or unavailable playbook {pid!r}; choose one of {ids}")
    return pbm.load_playbook(pid)


def describe_rules():
    return rules.describe_all()


def explain(rule_id):
    for r in rules.describe_all():
        if r["name"] == rule_id:
            return r
    raise ToolError(f"no rule named {rule_id!r}; run 'rules' to list them")


def check_draft(playbook, stage, lang, text):
    """Run the safety floor and the stage's named checks on a draft. No model, no key, no network, nothing stored."""
    if not isinstance(text, str) or not text.strip():
        raise ToolError("the draft is empty")
    if len(text) > MAX_CHARS:
        raise ToolError(f"the draft is longer than {MAX_CHARS:,} characters")
    pb = _load(playbook)
    if stage not in pb.registry:
        raise ToolError(f"unknown stage {stage!r} for {playbook}; choose one of {list(pb.registry)}")
    st = pb.registry[stage]
    if lang not in pb.languages:
        raise ToolError(f"unknown language {lang!r}; choose one of {pb.languages}")
    data = {n: pb.sources.get(n, {}) for n in st.sources}
    for spec in st.source_specs:
        if spec.get("dynamic") and spec["name"] not in pb.sources:
            data[spec["name"]] = {"entries": [], "held_names": []} if spec["dynamic"] != "scripture" else scr.source_for(pb, lang)
    verses = {}
    note = []
    if st.scripture:
        verses = {e["id"]: e for spec in st.source_specs if spec.get("dynamic") == "scripture" for e in data[spec["name"]]["entries"]}
    sources_blob = json.dumps(data, ensure_ascii=False)
    vetted_blob = sources_blob
    contact_names = [x["name"] for d in data.values() if isinstance(d, dict) for k in ("entries", "national", "local")
                     for x in d.get(k, []) if isinstance(x, dict) and x.get("name")]
    ctx = SimpleNamespace(state=SimpleNamespace(intake="", approved={}), data=data, fields={}, lang=lang, scripture=verses,
                          scripture_cap=scr.DEFAULT_CAP)
    own = text
    violations = []
    if st.scripture:
        parts, violations = scr.parse_output(text, verses)
        if parts:
            own = parts["own"]
            ctx.chosen_verse = parts["verse"]["text"] if parts["verse"] else ""
            violations = []
            note.append("the verse is not fetched here, so the verse block is not compared with its source")
    forced = [{"name": n} for n in ("no_providence_claims", "no_model_scripture")
              if st.scripture and n not in [c["name"] for c in st.checks]]
    if not violations:
        violations = g.unsafe_reasons(own, pb.extra_banned) + g.language_reasons(own, lang, contact_names)
        violations += g.url_reasons(own, g.allowed_urls_in(vetted_blob)) + g.phone_reasons(own, vetted_blob)
        violations += g.email_reasons(own, sources_blob, vetted_blob, "")
        for c in st.checks + forced:
            violations += checks_lib.REGISTRY[c["name"]](c, own, ctx)
    ran = [c["name"] for c in st.checks + forced]
    note.append("Jev is not run; the church network and the official list are empty, so checks that compare against them pass")
    return {"ok": not violations, "playbook": playbook, "stage": stage, "lang": lang, "words": g.word_count(text),
            "violations": [{"category": v["category"], "reason": v["reason"]} for v in violations],
            "floor": ["banned_patterns", "one_language", "link_allowlist", "phone_allowlist", "email_allowlist"],
            "named_checks": ran, "not_checked": note}


def scorecard_summary(which="detention"):
    """Summary of a stored evaluation set (runs.json): outcomes, corrections, cost, Jev judge means. Only the three sets in the repo."""
    if which not in RESULTS:
        raise ToolError(f"unknown set {which!r}; choose one of {list(RESULTS)}")
    f = REPO / RESULTS[which]
    if not f.is_file():
        raise ToolError(f"no results for {which} in this checkout")
    d = json.loads(f.read_text(encoding="utf-8"))
    runs = d.get("runs", [])
    status, jev, escal, corr, cost = {}, {}, 0, 0, 0.0
    for r in runs:
        status[r.get("status", "?")] = status.get(r.get("status", "?"), 0) + 1
        m = r.get("metrics", {})
        escal += 1 if m.get("escalated") else 0
        corr += m.get("corrections") or 0
        cost += m.get("cost_usd") or 0.0
        for j in r.get("jev", []):
            try:
                jev.setdefault(j["name"], []).append(float(j["value"]))
            except (KeyError, TypeError, ValueError):
                pass
    core = ((d.get("core") or {}).get("end") or {}).get("core_last_commit", "")
    return {"set": which, "scenarios": len(runs), "status": status, "escalated": escal, "corrections": corr, "gloo_cost_usd": round(cost, 3),
            "jev_judge_means": {k: round(sum(v) / len(v), 2) for k, v in sorted(jev.items())}, "core_commit": core.split(" ")[0] if core else "",
            "note": "Single runs on synthetic families. A judge score is one sample; the tone judge moves up to 0.75 between identical runs."}


def text_of(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)
