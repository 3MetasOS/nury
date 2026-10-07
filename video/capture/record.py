"""Capture the live demo run of the CURRENT app at true phone layout (390x844 CSS, 2x, via the DevTools screencast; see screencast.py).
One session: home, crisis chooser (both live cards), Detention page, Begin, demo intake, demo-guardrail box, Begin, optional Protected names screen, five gates (each held in the READY state), package.
Usage: python capture/record.py [base_url] [out_dir] [--detention-only] [--dry]
  --dry stops before Begin, so no Gloo call is made (use it to check the front half).
Writes out_dir/run.mp4 and out_dir/marks.txt (seconds; also 'reject' = first time the strip says 'Draft rejected', 'protected' = the Protected names screen)."""
import re, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent)); from screencast import Cast
args = [a for a in sys.argv[1:] if not a.startswith("--")]
base = args[0] if args else "http://localhost:8080/"; out = Path(args[1] if len(args) > 1 else "capture/raw"); out.mkdir(parents=True, exist_ok=True)
DRY = "--dry" in sys.argv; ONLY = "--detention-only" in sys.argv
HOLD = 5.0  # seconds a READY gate (all buttons bright) stays on screen before Approve
marks = []
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, color_scheme="dark"); page = ctx.new_page()
    page.goto(base); page.wait_for_timeout(1500); cast = Cast(ctx, page); cast.start()
    mark = lambda n: marks.append(f"{cast.now():6.1f} {n}")
    vis = lambda name, tag="button": page.locator(f"{tag}:visible", has_text=re.compile(name)).first
    page.wait_for_timeout(2200); mark("home")
    vis("Respond to a crisis").click(); page.wait_for_timeout(1500)
    if ONLY: page.evaluate("document.querySelectorAll('#chooser-list a, #chooser-list > *').forEach(e=>{if(!/Immigration detention/.test(e.innerText))e.style.display='none'})")
    mark("selector"); page.wait_for_timeout(3200)
    # click the Detention card's own link in the page (a mouse click on the sheet can land on the neighbouring card while it animates), then VERIFY it is Detention
    page.evaluate("[...document.querySelectorAll(\"a[href$='/crisis/detention']\")].find(a => a.offsetParent).click()"); page.wait_for_timeout(2200); mark("crisis")
    if "Immigration detention" not in page.inner_text("body"): raise RuntimeError("not on the Detention page: stop before any Gloo call")
    vis("Begin the response").click(); page.wait_for_timeout(1800); mark("intake_empty")
    vis("Use (demo|the sample) intake").click(); page.wait_for_timeout(2200); mark("intake")
    if "Maria" not in page.input_value("#intake") and "Maria" not in page.inner_text("body"): raise RuntimeError("the intake is not the Detention demo (Maria): stop before any Gloo call")
    page.check("#demo"); page.wait_for_timeout(700)
    if DRY:
        mark("end"); n = cast.stop(out / "run.mp4"); b.close(); (out / "marks.txt").write_text("\n".join(marks) + "\n"); print("dry run:", n, "frames\n" + "\n".join(marks)); sys.exit()
    vis("^Begin$").click(); mark("start")
    try:  # the Protected names step, if the app shows it
        page.wait_for_selector("#b-protect-go", state="visible", timeout=6000); mark("protected"); page.wait_for_timeout(3700); page.click("#b-protect-go")
    except Exception: pass
    prev_title = ""
    for i in range(1, 6):
        t_end = time.time() + 240; seen_reject = False
        while time.time() < t_end:
            # a NEW gate: visible and its title differs from the one we just approved (the old gate lingers for a moment)
            if page.locator("#gate:not(.hidden)").count() and page.inner_text("#g-title").strip() != prev_title: break
            if not seen_reject and "Draft rejected" in (page.inner_text("#strip") if page.locator("#strip:not(.hidden)").count() else ""):
                seen_reject = True; mark("reject"); mark(f"strip: rejected, stage {i}")
            page.wait_for_timeout(150)
        else: raise TimeoutError(f"gate {i} never appeared")
        t_rdy = time.time() + 20   # READY: every visible gate button is enabled (polled with evaluate: the app's CSP forbids wait_for_function)
        while time.time() < t_rdy and not page.evaluate("[...document.querySelectorAll('#gate .btn')].filter(b=>b.offsetParent).every(b=>!b.disabled)"): page.wait_for_timeout(150)
        prev_title = page.inner_text('#g-title').strip()
        mark(f"gate{i} shown: {prev_title[:40]!r}")
        strip = page.locator("#strip:not(.hidden)")
        if strip.count(): mark(f"strip: {strip.inner_text()[:80]!r}")
        page.wait_for_timeout(int(HOLD * 1000))
        if i == 5:  # the pastor changes ONE word in the editor, then Save and approve (E9 'He changes one word.' needs this on screen)
            SWAPS = [("sabemos", "entendemos"), ("difícil", "duro"), ("comprensible", "natural"), ("noche", "madrugada"), ("pronto", "mañana"), ("miedo", "temor"),
                     ("ayudar", "apoyar"), ("estamos", "seguimos"), ("caminar", "andar"), ("fuerte", "firme"), ("sola", "solitaria"), ("prometer", "asegurar")]
            page.click("#b-edit"); page.wait_for_timeout(1400); mark("edit")
            hit = page.evaluate("""(sw) => { const t = document.querySelector('#g-edit'); const v = t.value;
              for (const [a, b] of sw) { const m = new RegExp('\\\\b' + a + '\\\\b', 'i').exec(v); if (m) { t.focus(); t.setSelectionRange(m.index, m.index + a.length); return [m[0], b]; } } return null; }""", SWAPS)
            if hit:
                word = hit[1] if hit[0][0].islower() else hit[1].capitalize()
                page.keyboard.type(word, delay=110); mark(f"edit_word: {hit[0]} -> {word}"); page.wait_for_timeout(1800)
                page.click("#b-edit-save"); mark("edit_done"); mark("approve5"); page.wait_for_timeout(600); continue
            mark("edit_skipped: no known word in the draft"); page.click("#b-cancel"); page.wait_for_timeout(600)
        page.click("#b-approve"); mark(f"approve{i}"); page.wait_for_timeout(600)
    page.wait_for_selector("#v-pkg:not(.hidden), #b-copyall", timeout=60_000); mark("package"); page.wait_for_timeout(4000); mark("end")
    n = cast.stop(out / "run.mp4"); b.close()
(out / "marks.txt").write_text("\n".join(marks) + "\n"); print(n, "frames\n" + "\n".join(marks))
