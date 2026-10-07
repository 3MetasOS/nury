"""The five agent stages. Each stage returns a dict:

    {"title": ..., "content": ..., "sources": [...], "needs_review": True}

Every stage ends at a human approval gate: the pipeline pauses and the pastor
reviews before anything moves forward or reaches the family.
"""

import json
import os

from . import guardrails
from .gloo_client import GlooClient, GuardrailBlock

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _load(name):
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
        return json.load(f)


def _stage(title, content, sources, self_corrections=0):
    problems = guardrails.check_output(content)
    if problems:
        raise ValueError(f"Stage {title!r} output failed safety check: {problems}")
    return {
        "title": title,
        "content": content.strip(),
        "sources": sources,
        "needs_review": True,
        "disclaimer": guardrails.disclaimer(),
        "self_corrections": self_corrections,
    }


def _ask_with_self_correction(client, prompt, instructions, title, max_retries=2):
    """Ask the model, check the output against the guardrails, and on failure
    feed the failure back to the model for a retry — the agent checks its own
    output and fixes its mistakes instead of failing on the first attempt.

    Returns (content, corrections_made). If every attempt fails, raises so the
    failure escalates to the human instead of shipping bad output.
    """
    corrections = 0
    attempt_instructions = instructions
    problems = []
    for attempt in range(max_retries + 1):
        content = client.ask(prompt, instructions=attempt_instructions)
        problems = guardrails.check_output(content)
        if not problems:
            return content, corrections
        corrections += 1
        if attempt < max_retries:
            attempt_instructions = (
                instructions
                + "\n\nYour previous output failed the safety check for these reasons:\n"
                + "\n".join(f"- {p}" for p in problems)
                + "\nRegenerate the output avoiding these issues. "
                "Do not explain what went wrong; just produce the corrected output."
            )
    raise ValueError(
        f"Stage {title!r} output failed safety check "
        f"after {max_retries + 1} attempts: {problems}"
    )


def triage(client: GlooClient, intake_text: str):
    """Turn the pastor's raw intake into a structured case summary."""
    instructions = guardrails.SYSTEM_BOUNDARY + (
        "\nExtract a structured case summary from the pastor's intake notes. "
        "Return: situation (1-2 sentences), people involved, location, "
        "family language (es/en), urgency (high/medium/low) with one-line reason, "
        "and the 3 most important missing facts to ask about. "
        "Do not give advice. Keep it factual and brief."
    )
    content, corrections = _ask_with_self_correction(
        client, intake_text, instructions, "1. Triage"
    )
    return _stage("1. Triage", content, sources=["pastor intake"],
                  self_corrections=corrections)


def rights_brief(client: GlooClient, case: dict):
    """Know-your-rights information grounded in the seed data, in the family's language."""
    rights = _load("know_your_rights.json")
    lang = case.get("language", "es")
    bullets = "\n".join(
        f"- {r['topic']}: {r['summary_es'] if lang == 'es' else r['summary_en']} (source: {r['source']})"
        for r in rights["entries"]
    )
    instructions = guardrails.SYSTEM_BOUNDARY + (
        "\nUsing ONLY the rights information below, write a calm, plain-language "
        f"brief for the family in {'Spanish' if lang == 'es' else 'English'}. "
        "Keep each point to one or two short sentences. "
        "End by urging them to speak with an immigration attorney before acting.\n\n"
        f"{bullets}"
    )
    content, corrections = _ask_with_self_correction(
        client, "Write the family rights brief.", instructions, "2. Rights brief"
    )
    sources = sorted({r["source"] for r in rights["entries"]})
    return _stage("2. Rights brief", content, sources=sources,
                  self_corrections=corrections)


def attorney_match(client: GlooClient, case: dict):
    """Attorney directory: national resources now, local entries as the church adds them."""
    directory = _load("attorney_directory.json")
    lang = case.get("language", "es")
    lines = []
    for entry in directory["national"]:
        lines.append(f"- {entry['name']}: {entry['description']} — {entry['url']}")
    for entry in directory.get("local", []):
        lines.append(
            f"- {entry['name']} ({entry.get('area', '')}): {entry.get('phone', '')} {entry.get('url', '')}"
        )
    if not directory.get("local"):
        lines.append(
            "- [TODO] Add vetted local immigration attorneys and legal-aid orgs here."
        )
    instructions = guardrails.SYSTEM_BOUNDARY + (
        "\nFormat the attorney directory below as a clean, scannable list for the "
        f"pastor in {'Spanish' if lang == 'es' else 'English'}. Group national "
        "hotlines/directories first, then local. Add one line on what to have "
        "ready before calling (names, dates, any paperwork). Do not recommend "
        "a specific attorney.\n\n" + "\n".join(lines)
    )
    content, corrections = _ask_with_self_correction(
        client, "Format the attorney directory.", instructions, "3. Attorney directory"
    )
    return _stage("3. Attorney directory", content, sources=["attorney_directory.json"],
                  self_corrections=corrections)


def family_checklist(client: GlooClient, case: dict):
    """Tonight's checklist: what to do, what NOT to do, documents to gather."""
    lang = case.get("language", "es")
    instructions = guardrails.SYSTEM_BOUNDARY + (
        "\nWrite a tonight-only checklist for a family whose loved one was just "
        f"detained, in {'Spanish' if lang == 'es' else 'English'}. Three sections: "
        "DO TONIGHT (5-7 concrete steps), DO NOT DO (4-5 items), "
        "GATHER THESE DOCUMENTS (IDs, paperwork, contact numbers). "
        "General information only — no case-specific legal strategy."
    )
    content, corrections = _ask_with_self_correction(
        client,
        f"Case summary: {case.get('summary', '')}",
        instructions,
        "4. Family checklist",
    )
    return _stage("4. Family checklist", content, sources=["pastor intake"],
                  self_corrections=corrections)


def pastoral_draft(client: GlooClient, case: dict):
    """A compassionate message draft for the pastor to send the family."""
    lang = case.get("language", "es")
    instructions = guardrails.SYSTEM_BOUNDARY + (
        "\nDraft a short pastoral message (under 120 words) the pastor can send "
        f"to the family tonight, in {'Spanish' if lang == 'es' else 'English'}. "
        "Warm, steady, hopeful. Acknowledge their fear, affirm the church is with "
        "them, mention practical help is being arranged (attorney search, checklist). "
        "No legal claims, no promises about outcomes."
    )
    content, corrections = _ask_with_self_correction(
        client,
        f"Case summary: {case.get('summary', '')}",
        instructions,
        "5. Pastoral message draft",
    )
    return _stage("5. Pastoral message draft", content, sources=["pastor intake"],
                  self_corrections=corrections)


STAGES = [triage, rights_brief, attorney_match, family_checklist, pastoral_draft]


def run_pipeline(client, intake_text, approve=None, language="es"):
    """Run all stages in order, pausing at each human approval gate.

    approve(stage) -> bool. If it returns False, the pipeline stops.
    Default approve() prompts on the console.
    """
    if approve is None:

        def approve(stage):
            print(f"\n--- Pastor review: {stage['title']} ---")
            answer = input("Approve and continue? [Y/n] ").strip().lower()
            return answer in ("", "y", "yes")

    case = {"summary": intake_text, "language": language}
    results = []
    # Stage 1 needs the raw intake; later stages need the structured case.
    first = triage(client, intake_text)
    results.append(first)
    if not approve(first):
        return results
    case["structured"] = first["content"]

    for stage_fn in STAGES[1:]:
        try:
            stage = stage_fn(client, case)
        except GuardrailBlock as e:
            stage = _stage(
                stage_fn.__name__,
                f"[Blocked by Gloo guardrails — pastor handles manually]\n{e}",
                sources=[],
            )
        results.append(stage)
        if not approve(stage):
            break
    return results
