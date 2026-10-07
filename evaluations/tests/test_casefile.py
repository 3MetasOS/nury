"""The case-file checker must catch what it is meant to catch. Offline. Run: python3 -m pytest evaluations/tests -q"""
import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import casefile_check as c


def case(files):
    d = tempfile.mkdtemp()
    for n, t in files.items():
        (Path(d) / n).write_text(t)
    return d


CLEAN = {"index.md": "# Case\n[triage](01-triage.md)", "01-triage.md": "ok", "log.md": "draft_rejected: banned_phrase",
         "nextsteps.svg": "<svg>Immigration Advocates https://www.immigrationadvocates.org/nonprofit/legaldirectory/</svg>"}


def test_clean_case_passes():
    assert c.check_case_dir(case(CLEAN), "detention") == []


def test_rejected_draft_text_found():
    f = dict(CLEAN, **{"02-rights.md": "texto bueno. Su caso será desestimado."})
    assert any("rejected-draft" in p for p in c.check_case_dir(case(f), "detention", ["Su caso será desestimado"]))


def test_key_found():
    f = dict(CLEAN, **{"log.md": "token abc123SECRETVALUE789"})
    assert any("key value" in p for p in c.check_case_dir(case(f), "detention", secrets=["abc123SECRETVALUE789"]))


def test_bearer_pattern_found():
    f = dict(CLEAN, **{"log.md": "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9abcdef"})
    assert any("bearer" in p for p in c.check_case_dir(case(f), "detention"))


def test_unvetted_link_in_map_found():
    f = dict(CLEAN, **{"nextsteps.svg": "<svg>visit detentionlocator.org or https://fakelawyer.com/help</svg>"})
    probs = c.check_case_dir(case(f), "detention")
    assert sum("unvetted link" in p for p in probs) == 2


def test_file_names_not_flagged():
    f = dict(CLEAN, **{"index.md": "see [map](nextsteps.svg) and index.md and case.json"})
    assert c.check_case_dir(case(f), "detention") == []


def test_unvetted_phone_found():
    f = dict(CLEAN, **{"03-attorney.md": "Llame al 602-555-0142"})
    assert any("unvetted phone" in p for p in c.check_case_dir(case(f), "detention"))


def test_log_must_not_quote_matches():
    f = dict(CLEAN, **{"log.md": "banned_phrase: promises an outcome (matched 'garantizamos')"})
    assert any("matched phrase" in p for p in c.check_case_dir(case(f), "detention"))


def test_edit_must_reach_the_page():
    assert any("edited text" in p for p in c.check_case_dir(case(CLEAN), "detention", edit_marker="EDITADO-7Q"))


def test_svg_namespace_is_not_a_link_but_a_real_w3_link_is():
    ok = dict(CLEAN, **{"nextsteps.svg": '<svg xmlns="http://www.w3.org/2000/svg">x</svg>'})
    assert c.check_case_dir(case(ok), "detention") == []
    bad = dict(CLEAN, **{"nextsteps.svg": '<svg xmlns="http://www.w3.org/2000/svg">see http://www.w3.org/help</svg>'})
    assert any("unvetted link" in p for p in c.check_case_dir(case(bad), "detention"))
