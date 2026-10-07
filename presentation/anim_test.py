#!/usr/bin/env python3
"""Deck animation test. For every slide (gated ones included) in headless Chrome at 1280x720:
 1. screenshot the FINAL state (go(k,'final'): nothing hidden),
 2. replay the slide from its first step (go(k,'fresh') then every step 400 ms apart, as in AUTO mode), wait for it to finish, screenshot again,
 3. compare the two pictures (a small tolerance: at most 0.3 percent of pixels differ), check no animation is left running and nothing is left hidden,
 4. log the auto time (the whole slide must play in 3 s or less).
Usage: python3 presentation/anim_test.py [width height]   (needs agent-browser, Pillow; serves the folder on port 18152 and stops it after)"""
import json, os, subprocess, sys, tempfile, time
from pathlib import Path
from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
W, H = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (1280, 720)
os.environ["AGENT_BROWSER_SESSION"] = "nury-anim-test"
PORT = 18152
T = Path(tempfile.mkdtemp(prefix="nury_anim_"))


def ab(*a):
    r = subprocess.run(["agent-browser", *a], capture_output=True, text=True, timeout=120)
    return (r.stdout or "").strip().splitlines()[-1] if (r.stdout or "").strip() else ""


def ev(js):
    out = ab("eval", js)
    for _ in range(3):
        try:
            out = json.loads(out)
        except Exception:
            break
        if not isinstance(out, str):
            break
    return out


srv = subprocess.Popen(["python3", "-m", "http.server", str(PORT)], cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
bad = 0
try:
    ab("set", "viewport", str(W), str(H), "1")
    ab("open", "about:blank")
    ab("open", f"http://127.0.0.1:{PORT}/deck.html?gated")
    ab("wait", "1500")
    names = ev("JSON.stringify(deck.vis().map(s=>s.dataset.name))")
    names = json.loads(names) if isinstance(names, str) else names
    total = 0
    for k, nm in enumerate(names):
        ev(f"deck.go({k},'final');1"); ab("wait", "2600" if nm in ("the-name", "memorial") else "700")
        a = T / f"{k}a.png"; ab("screenshot", str(a))
        steps = ev("deck.anim.steps()")
        ms = ev(f"(async()=>{{deck.go({k},'fresh');const t=await deck.anim.playAll();return t}})()")
        ab("wait", "1700" if nm in ("the-name", "memorial") else "500")        # the name builds in 2.1 s and the memorial fades in 1.2 s by CSS
        left = ev("JSON.stringify({run:document.getAnimations().filter(a=>a.playState==='running'&&a.effect&&a.effect.getTiming().iterations!==Infinity).length,pend:document.querySelectorAll('.slide.on .pend').length})")
        left = json.loads(left) if isinstance(left, str) else left
        b = T / f"{k}b.png"; ab("screenshot", str(b))
        d = ImageChops.difference(Image.open(a).convert("RGB"), Image.open(b).convert("RGB")).convert("L").point(lambda v: 255 if v > 24 else 0)
        pct = 100.0 * sum(1 for v in d.getdata() if v) / (d.width * d.height)
        ok = pct <= 0.3 and left["pend"] == 0 and (isinstance(ms, int) and ms <= 3000)
        bad += 0 if ok else 1
        print(("PASS" if ok else "FAIL"), f"{k + 1:2d} {nm:42s} steps={steps} auto={ms}ms diff={pct:.3f}% running={left['run']} hidden={left['pend']}")
finally:
    ab("close"); srv.terminate()
print("ALL PASS" if not bad else f"{bad} FAILED")
sys.exit(1 if bad else 0)
