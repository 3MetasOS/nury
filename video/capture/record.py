"""Rehearsal/final capture of the Nury app at phone size (390x844 CSS, rendered 2x via html zoom).
Playwright video does not scale with device_scale_factor, so we use a 780x1688 viewport and zoom:2.
Usage: python capture/record.py [base_url] [out_dir] [--detention-only]
Selector default: all cards as the app draws them (hospital is live and scored). --detention-only hides the others.
Needs: playwright + system Chrome. Server must already run. Reads no secrets.
Writes out_dir/run.webm and out_dir/marks.txt (seconds at each gate and at the end).
"""
import re, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

FULL = "--detention-only" not in sys.argv  # hospital is live and scored: the selector shows both live cards by default
args = [a for a in sys.argv[1:] if not a.startswith("--")]
base = args[0] if args else "http://127.0.0.1:8099/"
out = Path(args[1] if len(args) > 1 else "capture/raw"); out.mkdir(parents=True, exist_ok=True)
HOLD = 5.0  # seconds the viewer can read each READY gate (all three buttons bright) before Approve

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    ctx = b.new_context(viewport={"width": 780, "height": 1688}, device_scale_factor=1,
                        record_video_dir=str(out), record_video_size={"width": 780, "height": 1688},
                        color_scheme="dark")
    page = ctx.new_page(); t0 = time.time(); marks = []
    mark = lambda n: marks.append(f"{time.time()-t0:6.1f} {n}")
    page.goto(base); page.add_style_tag(content="html{zoom:2}"); page.wait_for_timeout(1500); mark("intake")
    page.wait_for_timeout(1200); mark("selector")
    if not FULL:  # hide every card except Detention, plus the "Coming soon" ones
        page.evaluate("document.querySelectorAll('.pick').forEach(b=>{if(!/Immigration detention/.test(b.innerText))b.style.display='none'})")
    card = page.get_by_role("button", name=re.compile("Immigration detention"))
    card.hover(); page.wait_for_timeout(2500)  # shot 1b: selector holds ~4 s with Detention highlighted
    card.click(); page.wait_for_timeout(1200)
    page.click("#btn-demo"); page.wait_for_timeout(2500)
    pn = page.get_by_text(re.compile("Protected names", re.I))
    if pn.count():  # shot 2b: only exists once privacy is wired in the app
        mark("protected"); page.wait_for_timeout(3700)
    page.check("#demo"); page.wait_for_timeout(800)
    page.click("#btn-start"); mark("start")
    for i in range(1, 6):
        # wait for the real gate; note the first time the guardrail strip shows a rejection (shot 7 needs it on stage 2)
        t_end = time.time() + 240; seen_reject = False
        while time.time() < t_end:
            if page.locator("#gate:not(.hidden)").count(): break
            if not seen_reject and "Draft rejected" in (page.inner_text("#strip") if page.locator("#strip:not(.hidden)").count() else ""):
                seen_reject = True; mark("reject"); mark(f"strip: rejected, stage {i}")
            page.wait_for_timeout(150)
        else: raise TimeoutError(f"gate {i} never appeared")
        # READY state: Approve, Edit and Stop all enabled
        page.wait_for_function("[...document.querySelectorAll('#gate .btn')].filter(b=>b.offsetParent).every(b=>!b.disabled)", timeout=20_000)
        mark(f"gate{i} shown: {page.inner_text('#g-title')[:40]!r}")
        strip = page.locator("#strip:not(.hidden)")
        if strip.count(): mark(f"strip: {strip.inner_text()[:80]!r}")
        page.wait_for_timeout(int(HOLD * 1000))
        page.click("#b-approve"); mark(f"approve{i}")
        page.wait_for_timeout(600)
    page.wait_for_selector("#v-pkg:not(.hidden)", timeout=60_000); mark("package")
    page.wait_for_timeout(4000); mark("end")
    path = page.video.path(); ctx.close(); b.close()
Path(out / "marks.txt").write_text("\n".join(marks) + "\n")
Path(path).rename(out / "run.webm")
print("\n".join(marks))
