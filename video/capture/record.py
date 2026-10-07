"""Rehearsal/final capture of the Nury app at phone size (390x844 CSS, rendered 2x via html zoom).
Playwright video does not scale with device_scale_factor, so we use a 780x1688 viewport and zoom:2.
Usage: python capture/record.py [base_url] [out_dir] [--full-selector]
Shot 1b default (hack-sensei decision b): the selector shows ONLY the Detention card.
Pass --full-selector for version (a): all cards as the app draws them.
Needs: playwright + system Chrome. Server must already run. Reads no secrets.
Writes out_dir/run.webm and out_dir/marks.txt (seconds at each gate and at the end).
"""
import re, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

FULL = "--full-selector" in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith("--")]
base = args[0] if args else "http://127.0.0.1:8099/"
out = Path(args[1] if len(args) > 1 else "capture/raw"); out.mkdir(parents=True, exist_ok=True)
HOLD = 3.5  # seconds the viewer can read each gate before Approve

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
    page.check("#demo"); page.wait_for_timeout(800)
    page.click("#btn-start"); mark("start")
    for i in range(1, 6):
        page.wait_for_selector("#gate:not(.hidden)", timeout=240_000)
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
