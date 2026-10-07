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
    page.locator('a[href="#/crisis/detention"]:visible').first.click(force=True); page.wait_for_timeout(2200); mark("crisis")
    vis("Begin the response").click(); page.wait_for_timeout(1800); mark("intake_empty")
    vis("Use demo intake").click(); page.wait_for_timeout(2200); mark("intake")
    page.check("#demo"); page.wait_for_timeout(700)
    if DRY:
        mark("end"); n = cast.stop(out / "run.mp4"); b.close(); (out / "marks.txt").write_text("\n".join(marks) + "\n"); print("dry run:", n, "frames\n" + "\n".join(marks)); sys.exit()
    vis("^Begin$").click(); mark("start")
    try:  # the Protected names step, if the app shows it
        page.wait_for_selector("#b-protect-go", state="visible", timeout=6000); mark("protected"); page.wait_for_timeout(3700); page.click("#b-protect-go")
    except Exception: pass
    for i in range(1, 6):
        t_end = time.time() + 240; seen_reject = False
        while time.time() < t_end:
            if page.locator("#gate:not(.hidden)").count(): break
            if not seen_reject and "Draft rejected" in (page.inner_text("#strip") if page.locator("#strip:not(.hidden)").count() else ""):
                seen_reject = True; mark("reject"); mark(f"strip: rejected, stage {i}")
            page.wait_for_timeout(150)
        else: raise TimeoutError(f"gate {i} never appeared")
        page.wait_for_function("[...document.querySelectorAll('#gate .btn')].filter(b=>b.offsetParent).every(b=>!b.disabled)", timeout=20_000)
        mark(f"gate{i} shown: {page.inner_text('#g-title')[:40]!r}")
        strip = page.locator("#strip:not(.hidden)")
        if strip.count(): mark(f"strip: {strip.inner_text()[:80]!r}")
        page.wait_for_timeout(int(HOLD * 1000)); page.click("#b-approve"); mark(f"approve{i}"); page.wait_for_timeout(600)
    page.wait_for_selector("#v-pkg:not(.hidden), #b-copyall", timeout=60_000); mark("package"); page.wait_for_timeout(4000); mark("end")
    n = cast.stop(out / "run.mp4"); b.close()
(out / "marks.txt").write_text("\n".join(marks) + "\n"); print(n, "frames\n" + "\n".join(marks))
