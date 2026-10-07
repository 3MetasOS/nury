"""Render cards to 1920x1080 PNG. Usage: python cards/render.py [outdir]  (proof card only if PROOF='pass,n,caught,src' is set)"""
import os, sys
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright
here = Path(__file__).resolve().parent; out = Path(sys.argv[1] if len(sys.argv) > 1 else here / "out"); out.mkdir(parents=True, exist_ok=True)
jobs = [("end", f"file://{here}/end.html")]
if os.environ.get("PROOF"):
    a, n, c, *s = os.environ["PROOF"].split(","); jobs.append(("proof", f"file://{here}/proof.html?pass={a}&n={n}&caught={c}&src={quote(','.join(s))}"))
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome"); pg = b.new_page(viewport={"width": 1920, "height": 1080})
    for name, url in jobs:
        pg.goto(url); pg.wait_for_timeout(1500); pg.screenshot(path=str(out / f"{name}.png")); print(out / f"{name}.png")
    b.close()
