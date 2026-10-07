"""Rehearsal/final capture of the Nury app at phone size (390x844 CSS, rendered 2x via html zoom).
Playwright video does not scale with device_scale_factor, so we use a 780x1688 viewport and zoom:2.
Usage: python capture/record.py [base_url] [out_dir]
Needs: playwright + system Chrome. Server must already run. Reads no secrets.
Writes out_dir/run.webm and out_dir/marks.txt (seconds at each gate and at the end).
"""
import sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765/"
out = Path(sys.argv[2] if len(sys.argv) > 2 else "capture/raw"); out.mkdir(parents=True, exist_ok=True)
HOLD = 3.5  # seconds the viewer can read each gate before Approve

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    ctx = b.new_context(viewport={"width": 780, "height": 1688}, device_scale_factor=1,
                        record_video_dir=str(out), record_video_size={"width": 780, "height": 1688},
                        color_scheme="dark")
    page = ctx.new_page(); t0 = time.time(); marks = []
    mark = lambda n: marks.append(f"{time.time()-t0:6.1f} {n}")
    page.goto(base); page.add_style_tag(content="html{zoom:2}"); page.wait_for_timeout(1500); mark("intake")
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
