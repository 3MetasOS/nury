"""The rules, described. Metadata only: nothing here changes how a draft is checked.

describe_all() returns one entry for every floor rule, every named check and every Jev question:

    {name, kind, explanation, where, stages: [{playbook, stage}], playbooks: [id, ...]}

kind is "floor" (nothing can remove it), "check" (a named rule a playbook lists in stages.json, or that the
engine adds for a stage) or "classifier" (a Jev question). The app's GET /api/rules reads this.
The explanations are written by hand and a test fails if a check has none.
"""

from . import checks as checks_lib
from . import jev_gate

FLOOR = [
    ("boundary_prompt", "Nine hard rules go into every prompt: information only, no advice or prediction, only the vetted sources, urge the family to see a professional, never claim to be a pastor, counselor or lawyer, list only vetted contacts and never endorse one, calm plain words, one language, no byline.", "code/nury/guardrails.py"),
    ("banned_phrases", "A draft is rejected if it predicts an outcome, promises or guarantees one, gives advice (what to sign or plead), recommends an attorney, or claims to be a lawyer, counselor, pastor or doctor, in English or Spanish. Nineteen patterns; a playbook can add more and cannot remove any.", "code/nury/guardrails.py"),
    ("one_language", "A Spanish draft may not mix in English words. Names, links, fixed headings and the names of vetted contacts are ignored.", "code/nury/guardrails.py"),
    ("link_allowlist", "Every link must come from the vetted sources or from text the pastor already approved. An invented link is rejected.", "code/nury/guardrails.py"),
    ("phone_allowlist", "Every phone number must come from the vetted sources or approved text.", "code/nury/guardrails.py"),
    ("email_allowlist", "Every email address must come from the vetted sources, approved text or the intake.", "code/nury/guardrails.py"),
    ("disclaimer_on_every_output", "Every output ends with the disclaimer that Nury is an AI assistant, not a lawyer, doctor, pastor, counselor or therapist. A playbook cannot drop the required wording; the loader refuses it.", "code/nury/playbook.py"),
    ("three_attempts_then_the_pastor", "A rejected draft is regenerated with the reasons, not the draft. After three attempts the stage ends with no draft and 'I'll handle this manually.'", "code/nury/engine.py"),
    ("rejected_drafts_stay_hidden", "The pastor never sees a rejected draft. The audit log keeps its categories only.", "code/nury/engine.py"),
    ("approval_gate", "Every stage ends at Approve, Edit or Stop. Later stages read the approved or edited text.", "code/nury/engine.py"),
    ("vetted_sources_only", "Playbook sources are files with an approval status. A source that is not approved blocks the playbook; a rejected entry is dropped.", "code/nury/playbook.py"),
    ("no_send_path", "Nothing is sent to the family. The only outbound calls are the model, the Jev classifier and, when set, a Scripture passage lookup.", "code/nury/engine.py"),
    ("tokens_not_names", "Names, phones, emails, addresses, dates and IDs become tokens before any request goes to a model or to Jev. The token map never leaves the app.", "code/nury/privacy.py"),
]

CHECKS = {
    "required_labels": "The draft must carry every label the stage asks for, such as SITUATION, PEOPLE and URGENCY.",
    "numbered_after": "After a marker such as MISSING FACTS, the draft must list exactly the number of numbered items the stage asks for.",
    "cited_bullets": "Every bullet in a rights or information brief must name the vetted source it comes from.",
    "ends_with_referral": "The brief must end by urging the family to speak with a professional: an attorney or the care team.",
    "vetted_links_present": "Every vetted national link the stage must carry is present in the draft.",
    "required_headings": "The checklist must have its three headings, for example DO TONIGHT, DO NOT DO and GATHER THESE DOCUMENTS.",
    "max_words": "The draft may not run past the stage's word limit (the pastoral message: 120 words of Nury's own sentences).",
    "no_agency_names": "No government agency name or acronym appears on screen; the draft says 'immigration officers'.",
    "no_stock_phrases": "No stock AI sentence patterns, such as 'it is not just X, it is Y'.",
    "no_endorsement_words": "No word that ranks or endorses a contact, such as best or recommended. The line 'listed does not mean recommended' is allowed.",
    "official_list_rules": "Contacts from the official Department of Justice list keep their exact name and own phone or link, are never called free, carry the 'listed does not mean recommended' line, and a held entry is never named.",
    "listed_contacts_known": "Every contact in the draft is one we gave: the church network or the vetted lists. A person's name in neither list is rejected.",
    "network_entries_present": "Every church-network contact handed to the stage appears, labeled as the church's own, with its phone or link.",
    "no_unauthorized_promises": "The pastor's voice may invite but may not say anyone is searching, preparing, sending, calling back or visiting, or use a time word such as soon for an action, unless the pastor wrote it.",
    "no_providence_claims": "Nury's own sentences may not say what God will do for the case, why it happened, or what God knows, sees, feels, wants or intends beyond the chosen verse. The quoted verse is not checked.",
    "no_model_scripture": "The model writes no Bible reference and no verse text. The app inserts the verse.",
    "verse_block_verbatim": "The verse block equals the vetted source word for word, with its reference and version name, and fits the word cap.",
    "no_name_after_call": "The pastor's voice says 'call me' or 'call the pastor', never 'call <Name>', unless the intake names that contact.",
    "do_not_directives": "A DO NOT line about signing needs a vetted point that says so, and a hospital DO NOT line may never direct a decision about care.",
    "triage_facts_only": "Triage states facts from the intake: no advice and no claim about what is critical or what to preserve.",
}

_CHECK_WHERE = "code/nury/checks.py"
_JEV_WHERE = "code/nury/jev_gate.py"


def _uses(playbook_ids=("detention", "hospital")):
    """name -> [(playbook, stage)], for named checks, skill checks, engine-added checks and Jev questions."""
    from . import playbook as pbm
    used = {}
    for pid in playbook_ids:
        pb = pbm.load_playbook(pid)
        for st in pb.stages:
            names = [c["name"] for c in st.checks] + [c["name"] for sk in st.skills for c in sk.checks]
            if st.scripture:
                names += ["no_providence_claims", "no_model_scripture", "verse_block_verbatim"]
            for n in names:
                used.setdefault(n, [])
                if (pid, st.id) not in used[n]:
                    used[n].append((pid, st.id))
            for q in st.jev:
                used.setdefault("jev_" + q, []).append((pid, st.id))
    return used


def describe_all(playbook_ids=("detention", "hospital")):
    used = _uses(playbook_ids)
    out = []

    def entry(name, kind, text, where):
        st = used.get(name, [])
        return {"name": name, "kind": kind, "explanation": text, "where": where,
                "stages": [{"playbook": p, "stage": s} for p, s in st], "playbooks": sorted({p for p, _ in st})}
    for n, text, where in FLOOR:
        out.append({"name": n, "kind": "floor", "explanation": text, "where": where, "stages": [], "playbooks": list(playbook_ids)})
    for n in sorted(checks_lib.REGISTRY):
        out.append(entry(n, "check", CHECKS[n], _CHECK_WHERE))
    for q in sorted(jev_gate.QUESTIONS):
        out.append(entry("jev_" + q, "classifier", "Jev (a third-party classifier) answers this yes or no question about the draft: " + jev_gate.QUESTIONS[q] + " A probability of 0.50 or more rejects the draft.", _JEV_WHERE))
    return out


def describe(name):
    return next((e for e in describe_all() if e["name"] == name), None)
