#!/usr/bin/env python3
"""Deck screenshots from the real app, light mode, 2x, tightly cropped, no browser chrome.
Run from the repo root with two servers up (no key needed, no model call):
  LIVE  http://127.0.0.1:8080  the normal app with its saved (synthetic) cases
  REPLAY http://127.0.0.1:8096 the same app started with NURY_REPLAY=1 NURY_FEEDBACK=on (a recorded run: sample intake, gates, final page)
Usage: python3 presentation/screens/capture_screens.py [live|replay|final|gate|overview|pdf|all]
Needs agent-browser, Pillow, and pdftoppm for the PDF pages. The app is not changed: only a screenshot is taken."""
import json, os, subprocess, sys, tempfile, time, zipfile, urllib.request
from pathlib import Path
from PIL import Image

os.environ.setdefault("AGENT_BROWSER_SESSION", "nury-screens")      # its own browser session: other agents drive the default one
OUT = Path(__file__).resolve().parent
LIVE, REPLAY = "http://127.0.0.1:8080", "http://127.0.0.1:8096"
ES_CASE = "detention-20261007-052545-0556"          # a synthetic Spanish detention case (Jose, Maria)
TMP = Path(tempfile.mkdtemp(prefix="nury_screens_"))


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


def open_light(url, w, h=2400):
    ab("set", "viewport", str(w), str(h), "2")
    ab("open", "about:blank")
    ab("open", url)
    ab("wait", "1200")
    ev("try{localStorage.setItem('nury-theme','light')}catch(e){};location.reload();1")
    ab("wait", "2200")


def until(js, secs=60):
    for _ in range(secs):
        if ev(js) is True or ev(js) == "true":
            return True
        ab("wait", "1000")
    return False


def settle():
    # the slides carry their own handwritten asides: hide the app's hint notes in the picture (a style in the open page only, the app is not changed)
    ev("(()=>{if(!document.getElementById('nohn')){const s=document.createElement('style');s.id='nohn';s.textContent='.hnote{display:none!important}';document.head.append(s)}document.activeElement&&document.activeElement.blur();window.scrollTo(0,0);return 1})()")
    ab("wait", "400")


def rect_js(sel):
    return f"(()=>{{const e=document.querySelector({json.dumps(sel)});if(!e)return null;const r=e.getBoundingClientRect();return JSON.stringify([r.left,r.top+scrollY,r.right,r.bottom+scrollY])}})()"


def snap(name, w, bottom_sel=None, top_sel=None, pad=20, box_sel=None, max_h=None, crop_h=None):
    """Screenshot at the current state and crop: from the page top (header included) or top_sel, to the bottom of bottom_sel (+pad); or just the box of box_sel."""
    settle()
    raw = TMP / (name + ".png")
    ab("screenshot", str(raw))
    im = Image.open(raw)
    s = 2
    if box_sel:
        r = ev(rect_js(box_sel))
        x0, y0, x1, y1 = max(0, r[0] - pad), max(0, r[1] - pad), min(w, r[2] + pad), r[3] + pad
    else:
        y0 = ev(rect_js(top_sel))[1] - pad if top_sel else 0
        y1 = (ev(rect_js(bottom_sel))[3] + pad) if bottom_sel else im.height / s
        x0, x1 = 0, w
    if crop_h:
        y1 = min(y1, y0 + crop_h)
    if max_h:
        y1 = min(y1, max_h)
    im.crop((int(x0 * s), int(max(0, y0) * s), int(x1 * s), int(min(y1, im.height / s) * s))).save(OUT / f"{name}-{w}.png", optimize=True)
    print("wrote", f"{name}-{w}.png", Image.open(OUT / f"{name}-{w}.png").size)


def live(w):
    open_light(LIVE + "/#/", w); ab("wait", "800")
    snap("01-home", w, bottom_sel="main")
    open_light(LIVE + "/#/cases", w); ab("wait", "600")
    snap("09-cases", w, bottom_sel="main")
    open_light(LIVE + "/network", w); ab("wait", "800")
    snap("08-network", w, bottom_sel="main")
    open_light(LIVE + f"/#/case/{ES_CASE}", w); ab("wait", "1500")
    ev("window.scrollTo(0,0);1")
    snap("07-case-overview", w, crop_h=1400 if w > 600 else 1900)
    open_light(LIVE + "/about", w); ab("wait", "800")
    snap("12-about", w, bottom_sel="section.sec", pad=24)


def overview_seq():
    """The case Overview's sequence card at 960 px (the narrowest width that keeps the five stages in a row), so its labels stay readable when the deck shrinks it."""
    open_light(LIVE + f"/#/case/{ES_CASE}", 960); ab("wait", "1500")
    snap("07-case-sequence", 960, box_sel="#case-page .ovc", pad=10)


def gate_narrow():
    """The stage-1 gate at 420 px wide, so the text is large when the deck shows it in a 500 px frame."""
    open_light(REPLAY + "/#/crisis/detention", 420); ab("wait", "2200")
    ev("[...document.querySelectorAll('[data-begin]')].find(b=>b.getBoundingClientRect().height>0).click();1"); ab("wait", "900")
    ev("document.getElementById('btn-demo').click();1"); ab("wait", "500")
    ev("document.getElementById('btn-start').click();1"); ab("wait", "1500")
    ev("document.getElementById('b-protect-go').click();1"); ab("wait", "9000")
    snap("05-gate-narrow", 420, box_sel="#gate", pad=0)


def replay(w):
    open_light(REPLAY + "/#/", w); ab("wait", "800")
    ev("[...document.querySelectorAll('button,a')].find(b=>/Respond to a crisis/.test(b.textContent)&&b.getBoundingClientRect().height>0).click();1"); ab("wait", "900")
    snap("03-chooser", w, box_sel="#chooser", pad=0)
    ev("document.getElementById('chooser').close();location.hash='#/crisis/detention';1"); ab("wait", "1500")
    snap("02-crisis", w, bottom_sel="#crisis-page svg.dgm", pad=24)
    ev("[...document.querySelectorAll('[data-begin]')].find(b=>b.getBoundingClientRect().height>0).click();1"); ab("wait", "900")
    ev("document.getElementById('btn-demo').click();1"); ab("wait", "500")
    snap("04-intake", w, bottom_sel="#v-intake .card, #v-intake form, #v-intake", pad=24)
    ev("document.getElementById('btn-start').click();1"); ab("wait", "1500")
    ev("document.getElementById('b-protect-go').click();1"); ab("wait", "9000")
    snap("05-gate", w, bottom_sel="#gate")


def final(w):
    """The final page of a real approved Spanish case (its saved text), shown through the same stub the browser tests use. No model call, no 'Recorded run' label."""
    stub = " ".join((Path(__file__).resolve().parents[2] / "evaluations" / "browser" / "finalstub.js").read_text(encoding="utf-8").split("\n"))
    open_light(LIVE + "/#/", w); ab("wait", "800")
    ev(f"(async()=>{{{stub}; await window.__finalStub({json.dumps(ES_CASE)},{{addVerse:true}}); sid='x'; show('v-pkg'); poll(); return 1}})()")
    ab("wait", "2500")
    snap("06-final-es", w, bottom_sel="#final", crop_h=1500 if w > 600 else 2000)
    ev("document.getElementById('b-export').click();1"); ab("wait", "500")
    snap("10-export-menu", w, top_sel=".keyfacts", bottom_sel="#b-export-menu", pad=24)


def pdf():
    data = urllib.request.urlopen(f"{LIVE}/api/case/{ES_CASE}/export").read()
    zp = TMP / "case.zip"; zp.write_bytes(data)
    with zipfile.ZipFile(zp) as z:
        z.extractall(TMP / "z")
    for kind, nm in (("family", "Family copy.pdf"), ("pastor", "Pastor copy.pdf")):
        f = next((TMP / "z").rglob(nm))
        subprocess.run(["pdftoppm", "-f", "1", "-l", "1", "-scale-to-x", "1200", "-scale-to-y", "-1", "-png", str(f), str(TMP / kind)], check=True)
        p = next(TMP.glob(f"{kind}-*.png"))
        Image.open(p).convert("RGB").save(OUT / f"11-pdf-{kind}-1200.png", optimize=True)
        print("wrote", f"11-pdf-{kind}-1200.png", Image.open(OUT / f"11-pdf-{kind}-1200.png").size)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    for w in (1280, 390):
        if what in ("live", "all"):
            live(w)
        if what in ("replay", "all"):
            replay(w)
        if what in ("final", "all"):
            final(w)
    if what in ("gate", "all"):
        gate_narrow()
    if what in ("overview", "all"):
        overview_seq()
    if what in ("pdf", "all"):
        pdf()
