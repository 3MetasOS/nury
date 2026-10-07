"""Non-live screens from the CURRENT app (no Gloo call): home, the crisis chooser (both live cards), the crisis page, the demo intake typed in.
Usage: python capture/record_ui.py [base_url] [out_dir]  ->  out_dir/ui.mp4 and ui_marks.json (seconds into the video)."""
import json, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent)); from screencast import Cast
base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080/"
out = Path(sys.argv[2] if len(sys.argv) > 2 else "capture/raw_ui"); out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, color_scheme="dark"); page = ctx.new_page()
    page.goto(base); page.wait_for_timeout(1200); cast = Cast(ctx, page); cast.start(); marks = {}
    def vis(name, tag="button"): return page.locator(f"{tag}:visible", has_text=re.compile(name)).first
    page.wait_for_timeout(2200); marks["home"] = cast.now()
    vis("Respond to a crisis").click(); page.wait_for_timeout(1800); marks["selector"] = cast.now(); page.wait_for_timeout(2400)
    page.locator('a[href="#/crisis/detention"]:visible').first.click(force=True); page.wait_for_timeout(1800); marks["crisis"] = cast.now()
    page.wait_for_timeout(1800); vis("Begin the response").click(); page.wait_for_timeout(1800); marks["intake_empty"] = cast.now()
    vis("Use demo intake").click(); page.wait_for_timeout(2600); marks["intake"] = cast.now(); page.wait_for_timeout(2200); marks["end"] = cast.now()
    n = cast.stop(out / "ui.mp4"); b.close()
json.dump(marks, open(out / "ui_marks.json", "w"), indent=1); print(n, "frames", marks)
