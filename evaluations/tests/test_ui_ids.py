"""The page must not repeat an id, and every id its script uses must exist once.
A repeated id (b-save) made getElementById return the wrong button, so the Package screen's Save did nothing for a real click.
Offline. Run: python3 -m pytest evaluations/tests -q"""
import re
from collections import Counter
from pathlib import Path

STATIC = Path(__file__).resolve().parents[2] / "code" / "app" / "static"
ROOT = Path(__file__).resolve().parents[2]


def parts(name):
    s = (STATIC / name).read_text(encoding="utf-8")
    html = re.sub(r"<script>.*?</script>", "", s, flags=re.S)
    js = "\n".join(re.findall(r"<script>(.*?)</script>", s, re.S))
    return html, js


def test_no_duplicate_ids_in_any_page():
    for f in STATIC.glob("*.html"):
        html, _ = parts(f.name)
        dup = [k for k, v in Counter(re.findall(r'\bid="([^"]+)"', html)).items() if v > 1]
        assert not dup, f"{f.name}: duplicate ids {dup}"


def test_every_id_used_by_the_script_exists():
    for f in STATIC.glob("*.html"):
        html, js = parts(f.name)
        ids = set(re.findall(r'\bid="([^"]+)"', html)) | set(re.findall(r'\bid="([^"]+)"', (STATIC / "shell.js").read_text(encoding="utf-8")))
        used = set(re.findall(r'\$\("([^"]+)"\)', js)) | set(re.findall(r'getElementById\("([^"]+)"\)', js))
        missing = sorted(u for u in used if u not in ids)
        assert not missing, f"{f.name}: script uses ids that are not in the page: {missing}"


def test_save_buttons_have_different_ids():
    html, _ = parts("index.html")
    assert 'id="b-save"' in html and 'id="b-edit-save"' in html


def test_no_storage_location_wording_in_user_facing_text():
    """The app will run on a server. It must not say where data is kept ('on this computer', 'stays here', 'local', 'on your device')."""
    terms = re.compile(r"this computer|stays? here|stays? on (this|your)|\blocal(ly)?\b|your device|this device|your computer|never leaves|on-?device", re.I)
    for f in STATIC.glob("*.html"):
        if f.name in ("how-it-was-built.html", "build-log.html"):      # records and documentation: held to the narrower rule below
            continue
        s = re.sub(r"<style>.*?</style>", "", f.read_text(encoding="utf-8"), flags=re.S)
        hits = [l.strip()[:80] for l in s.splitlines() if terms.search(l)]
        assert not hits, f"{f.name}: {hits}"


# ---- the shared shell (one header for every page) ----

SHELL_IDS = set(re.findall(r'\bid="([^"]+)"', (STATIC / "shell.js").read_text(encoding="utf-8")))


def test_every_page_uses_the_shared_shell_and_defines_no_header_of_its_own():
    pages = [f for f in STATIC.glob("*.html") if f.name != "case-print.html"]   # the print template is a standalone document, not a page of the app
    assert {p.name for p in pages} >= {"index.html", "network.html"}
    for f in pages:
        s = f.read_text(encoding="utf-8")
        assert '<link rel="stylesheet" href="/shell.css">' in s, f"{f.name} must load /shell.css"
        assert '<script src="/shell.js"></script>' in s, f"{f.name} must load /shell.js"
        assert "<header" not in s, f"{f.name} defines its own <header>; the shell supplies it"
        assert 'class="top"' not in s and 'class="tabs"' not in s, f"{f.name} defines its own top bar or tabs"
        assert "googleapis" not in s, f"{f.name} loads fonts from Google; fonts are self-hosted"
        assert re.search(r'<body[^>]*data-nav="|NuryShell\.setActive', s), f"{f.name} must say which tab is active"


def test_shell_has_logo_three_nav_items_toggle_and_how_link_and_no_popup():
    js = (STATIC / "shell.js").read_text(encoding="utf-8")
    assert js.count('<header class="top"') == 1
    for token in ('i-mark', 'data-nav="home"', 'data-nav="cases"', 'data-nav="network"', 'id="theme"'):
        assert token in js, token
    head = js.split("const header = `")[1].split("`;")[0]
    assert head.count("<a ") == 1 + 1 + 3 and "how-it-was-built" not in head and "observability" not in head and "self-improvement" not in head, \
        "the header holds the mark, Home, Cases, Network and the Day/Night switch only; the pages for judges live in the footer"
    foot = js.split("const footer = `")[1].split("`;")[0]
    assert foot.count("<footer") == 1 and "For judges and reviewers" in foot
    for href in ("/how-it-was-built", "/observability", "/self-improvement"):
        assert f'href="{href}"' in foot, href
    assert "Improvement" not in js.replace("Self-improvement", ""), "the page is called Self-improvement everywhere"

    assert "<dialog" not in js and 'id="about"' not in js, "the About popup is gone; the page replaces it"
    assert "An AI Crisis Response Agent" in js and "solo pastor" not in js
    css = (STATIC / "shell.css").read_text(encoding="utf-8")
    assert "@font-face" in css and ".top{" in css and ".tabs{" in css


def test_pages_do_not_redefine_shell_rules():
    for f in STATIC.glob("*.html"):
        s = f.read_text(encoding="utf-8")
        style = "".join(re.findall(r"<style>(.*?)</style>", s, re.S))
        for rule in (".top{", ".top .wrap", ".brand{", ".tabs{", ".tabs a{", ".iconbtn{", "dialog.sheet{", "@font-face"):
            assert rule not in style, f"{f.name} redefines shell rule {rule}"


def test_icons_are_served_from_one_file():
    assert (STATIC / "icons.svg").is_file()
    for f in STATIC.glob("*.html"):
        assert "<symbol" not in f.read_text(encoding="utf-8"), f"{f.name} inlines icons"


def test_icon_sprite_is_valid_xml():
    """An XML comment with a double hyphen made the sprite unparseable as a file: every icon vanished, and no test saw it."""
    import xml.dom.minidom
    d = xml.dom.minidom.parse(str(STATIC / "icons.svg"))
    assert len(d.getElementsByTagName("symbol")) >= 39
    ids = {e.getAttribute("id") for e in d.getElementsByTagName("symbol")}
    for f in STATIC.glob("*.html"):
        used = set(re.findall(r'/icons\.svg#([a-z0-9-]+)', f.read_text(encoding="utf-8")))
        assert used <= ids, f"{f.name} uses icons that are not in the sprite: {sorted(used - ids)}"
    shell_used = set(re.findall(r'IC\("([a-z0-9-]+)"', (STATIC / "shell.js").read_text(encoding="utf-8")))
    assert shell_used <= ids, sorted(shell_used - ids)


def test_how_it_was_built_page():
    page = (STATIC / "how-it-was-built.html").read_text(encoding="utf-8")
    assert 'data-live="rules"' in page and 'data-live="playbooks"' in page, "the two live markers must stay"
    assert "LIVE:" not in page, "no raw marker left in the page"
    assert "The Jev decision API from TypeSafe is used as typed judges in our evaluation harness and as a run-time draft classifier; disclosed as third-party technology per the rules." in page
    assert "solo pastor" not in page.lower() and "local computer" not in page.lower()
    assert "<dialog" not in page and "prior project" not in page


def test_live_rules_table_lists_every_named_check_in_the_registry():
    import sys
    sys.path.insert(0, str(STATIC.parents[1]))
    sys.path.insert(0, str(STATIC.parents[2]))
    from app import rules_info
    from nury import checks
    d = rules_info.rules()
    named = [r["name"] for r in d["rules"] if r["kind"] == "check"]
    assert sorted(named) == sorted(checks.REGISTRY), "the live table must list every check in the registry"
    assert len(d["rules"]) == d["count_floor"] + d["count_named"] + d["count_jev"]
    assert d["count_floor"] >= 5 and d["count_jev"] >= 1
    for r in d["rules"]:
        assert len(r["explanation"]) >= 20, f"{r['name']} has no plain explanation"
        assert r["stages"], f"{r['name']} lists no stages"


def test_every_check_a_stage_names_is_in_the_registry():
    import sys
    sys.path.insert(0, str(STATIC.parents[2]))
    from nury import checks
    from app import rules_info
    for use in rules_info._usage():
        assert use in checks.REGISTRY, f"stages.json names an unknown check: {use}"


def test_playbook_detail_api_is_safe_and_complete():
    import sys
    sys.path.insert(0, str(STATIC.parents[1]))
    sys.path.insert(0, str(STATIC.parents[2]))
    from app import rules_info
    d = rules_info.playbook_detail("detention")
    assert len(d["stages"]) == 5 and d["outcomes"]
    assert rules_info.playbook_detail("../detention") is None and rules_info.playbook_detail("nope") is None


def test_built_page_is_current_with_its_source():
    """How this was built is generated. Build into a temp folder and compare there: python3 -m app.build_docs (from code/) regenerates it."""
    import importlib, sys, tempfile
    try:
        import markdown  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("python-markdown is a build-time tool and is not installed here")
    sys.path.insert(0, str(STATIC.parents[1]))
    sys.path.insert(0, str(STATIC.parents[2]))
    from app import build_docs
    importlib.reload(build_docs)
    with tempfile.TemporaryDirectory() as d:
        build_docs.build(out=Path(d) / "how.html")
        fresh = (Path(d) / "how.html").read_text(encoding="utf-8")
    assert (STATIC / "how-it-was-built.html").read_text(encoding="utf-8") == fresh, "how-it-was-built.html is stale: run python3 -m app.build_docs"


def test_build_log_page_exists_and_has_the_newest_entry():
    """The build log changes with every milestone, so it is not compared byte for byte. It must exist and carry the newest entry number in BUILD_LOG.md at test time (built into a temp folder)."""
    import sys, tempfile
    try:
        import markdown  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("python-markdown is a build-time tool and is not installed here")
    sys.path.insert(0, str(STATIC.parents[1]))
    from app import build_docs
    newest = max(int(n) for n in re.findall(r"(?m)^## (\d+)\. ", (ROOT / "BUILD_LOG.md").read_text(encoding="utf-8")))
    with tempfile.TemporaryDirectory() as d:
        build_docs.build_log(out=Path(d) / "log.html")
        fresh = (Path(d) / "log.html").read_text(encoding="utf-8")
    assert f'id="e{newest}"' in fresh or f'id="e{newest}-2"' in fresh, "the build step finds the newest entry"
    page = (STATIC / "build-log.html").read_text(encoding="utf-8")
    assert page.count('<details class="ent"') >= 100, "the committed page exists and holds the log"



def test_how_it_was_built_has_no_computer_or_device_wording():
    """The documentation may say 'a local .env file' (a file name). It may not say where the pastor's data sits."""
    for name in ("how-it-was-built.html",):      # the build log is a record and quotes the banned words when it describes their removal
        s = re.sub(r"<style>.*?</style>", "", (STATIC / name).read_text(encoding="utf-8"), flags=re.S)
        assert not re.search(r"this computer|your computer|local computer|your device|this device|on-?device|stays? on (this|your)", s, re.I), name


def test_home_strip_does_not_type_the_check_count_or_the_old_jev_wording():
    s = (STATIC / "index.html").read_text(encoding="utf-8")
    assert "14 named checks" not in s, "the count is read from the registry (/api/features named_checks)"
    assert "a red team, human review" not in s
    assert 'id="built-checks"' not in s and 'class="built"' not in s, "the Built with card is gone from Home; the footer carries it"


def test_hand_written_notes_are_decoration_only_and_self_hosted():
    js = (STATIC / "shell.js").read_text(encoding="utf-8")
    assert 'setAttribute("aria-hidden", "true")' in js, "notes are aria-hidden: the real label carries the same information"
    assert "nury-notes" not in js and "notes-toggle" not in js and "toggleNotes" not in js, "no Hide notes control: the notes are always shown"
    assert "no-phone" not in js and "data-note-phone" not in (STATIC / "index.html").read_text(encoding="utf-8"), "one note, one text: no phone-only hidden variants"
    css = (STATIC / "shell.css").read_text(encoding="utf-8")
    assert "/fonts/GochiHand-400.woff2" in css and (STATIC / "fonts" / "GochiHand-400.woff2").is_file(), "Gochi Hand is self-hosted"
    assert "googleapis" not in css
    assert "@media (max-width:639px){.hnote" in css, "on a phone a note becomes a small caption (no rotation, no arrow)"
    assert "data-notes" not in css and ".no-phone" not in css
    credits = (ROOT.parents[0] / "branding" / "IMAGES.md").read_text(encoding="utf-8") if False else ""
    page_notes = re.findall(r'data-note="([^"]+)"', (STATIC / "index.html").read_text(encoding="utf-8") + (STATIC / "network.html").read_text(encoding="utf-8"))
    assert len(page_notes) >= 6 and all(len(n) <= 72 for n in page_notes), "short notes only (the Cases note is 69 characters, by request)"


def test_every_shell_css_brace_is_closed():
    """A dangling @media once swallowed the whole footer and note styles."""
    css = (STATIC / "shell.css").read_text(encoding="utf-8")
    assert css.count("{") == css.count("}")


def test_header_carries_the_tagline_under_the_logo_and_the_footer_the_provenance_line():
    js = (STATIC / "shell.js").read_text(encoding="utf-8")
    head = js.split("const header = `")[1].split("`;")[0]
    assert head.index('class="lk"') < head.index('class="tg"') and "An AI Crisis Response Agent" in head, "the tagline is in the header, after (below) the logo"
    css = (STATIC / "shell.css").read_text(encoding="utf-8")
    assert ".brand{display:grid" in css and ".brand .tg{display:block;white-space:nowrap" in css, "stacked, never wrapping, never beside the logo"
    foot = js.split("const footer = `")[1].split("`;")[0]
    assert "Built in Boulder, Colorado, during the Gloo AI Hackathon, October 6 to 8, 2026." in foot and 'href="/build-log"' in foot
    assert foot.index('class="prov"') < foot.index('class="fine"'), "the provenance line sits above the disclaimer"


def test_build_log_page_is_static_scanned_and_in_the_shell():
    import sys
    sys.path.insert(0, str(ROOT / "code"))
    from app import build_docs
    page = (STATIC / "build-log.html").read_text(encoding="utf-8")
    assert '<script src="/shell.js"></script>' in page and '<link rel="stylesheet" href="/shell.css">' in page and "<header" not in page
    assert "Source:" in page and "BUILD_LOG.md in the repository" in page and "2026-10-06 19:36 MDT" in page
    assert page.count('<details class="ent"') >= 100, "every entry is a collapsible block"
    nums = [int(n) for n in re.findall(r'<span class="num mono">#(\d+)</span>', page)]
    assert nums == sorted(nums, reverse=True), "newest on top"
    text = re.sub(r"<[^>]+>", " ", page)
    assert build_docs.scan_log(text) == [], "no key, token, email or phone is published"
    assert "fetch(" not in page and "/BUILD_LOG" not in page.replace("BUILD_LOG.md in the repository", ""), "static: nothing is read from the repository at run time"


def test_the_build_log_scan_catches_secrets_and_personal_data():
    import sys
    sys.path.insert(0, str(ROOT / "code"))
    from app import build_docs
    for bad in ("call 303-555-0101 now", "mail ana@example.com", "GLOO_API_KEY=abc123xyz", "token sk-abcdefghij1234", "Authorization: Bearer abcdefghij12345"):
        assert build_docs.scan_log(bad), bad
    assert build_docs.scan_log("an invented address x@invented.org is allowed") == []


def test_only_the_header_and_the_footer_carry_the_logo():
    """The header shows the logo and tagline; a second lockup in a page body (the Welcome card included) is clutter. The footer keeps one; the print view of the final page shows one."""
    for f in STATIC.glob("*.html"):
        n = f.read_text(encoding="utf-8").count('class="lockup"')
        assert n == 0, f"{f.name} has {n} in-page lockups (the header and the footer carry the logo)"
    css = (STATIC / "final.css").read_text(encoding="utf-8")
    assert ".fp-lock{display:none}" in css and ".fp-lock{display:block" in css.split("@media print")[1], "screen: no logo in the final page body; print: one"


def test_footer_links_and_document_pages():
    js = (STATIC / "shell.js").read_text(encoding="utf-8")
    foot = js.split("const footer = `")[1].split("`;")[0]
    for href in ("/how-it-was-built", "/observability", "/self-improvement", "/what-did-not-work", "/economics", "/pattern", "/standards"):
        assert f'href="{href}"' in foot, href
    assert "Standards we use" in foot and "What did not work" in foot
    for name in ("standards", "what-did-not-work", "economics", "pattern"):
        page = (STATIC / f"{name}.html").read_text(encoding="utf-8")
        assert '<script src="/shell.js"></script>' in page and "<header" not in page and 'class="lockup"' not in page, name
    std = (STATIC / "standards.html").read_text(encoding="utf-8")
    assert std.count('class="fr ') == 6 and 'role="img"' in std, "the six functions are drawn with a text alternative"
    assert "Not known." in (STATIC / "what-did-not-work.html").read_text(encoding="utf-8")


def test_diagrams_are_drawn_from_data_and_have_text_alternatives():
    js = (STATIC / "diagrams.js").read_text(encoding="utf-8")
    assert "function flow(stages" in js and "function strip(stages" in js and 'role: "img"' in js and "aria-label" in js
    assert "innerHTML" not in js, "server text goes in with textContent"
    idx = (STATIC / "index.html").read_text(encoding="utf-8")
    assert "NuryDiagram.flow(st," in idx and 'class:"seq"' in idx, "the case page draws its stages as five links (live HTML), the crisis page as a drawn flow"
    how = (STATIC / "how-it-was-built.html").read_text(encoding="utf-8")
    assert how.count('class="adg"') == 2, "architecture and loop"
    assert 'class="adg"' not in (STATIC / "network.html").read_text(encoding="utf-8"), "the network page has notes, not a diagram"


def test_privacy_off_banner_text_and_hook():
    idx = (STATIC / "index.html").read_text(encoding="utf-8")
    assert 'id="privacy-off"' in idx and "Privacy is off: names go to the model as typed." in idx
    assert '$("privacy-off").hidden=!(pv&&pv.on===false)' in idx and '"/api/privacy"' in idx


def test_replay_mode_hooks():
    idx = (STATIC / "index.html").read_text(encoding="utf-8")
    for tok in ('id="replay-line-intake"', 'id="replay-line-run"', 'href="/run-your-own"', 'id="replay-note"', "Use the sample intake", "s.replay_note", "RECORDED (not a live Jev check)"):
        assert tok in idx, tok
    fin = (STATIC / "final.js").read_text(encoding="utf-8")
    assert 'row("Mode", "Recorded run"' in fin and "fp-rec" in fin
    assert "readOnly=rp" in idx, "in replay the typing box is read-only; the sample intake is the path"
