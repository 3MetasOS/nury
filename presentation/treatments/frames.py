"""Storyboard frames for the three treatments. Flat vector, our palette, no faces, no real people.
Each function returns an SVG string, 640 x 360. Text uses Georgia so it renders anywhere."""
import re
from pathlib import Path
HERE = Path(__file__).resolve().parent
INK, DEEP, AMB, DAMB, PAPER, TXT, MUT = "#0d1015", "#131824", "#e8a33d", "#b8680f", "#f6f1e7", "#ece7dc", "#8d887c"
RED, GRN = "#d9605a", "#5fb37c"

def _inner(path):
    s = (HERE.parent / path).read_text()
    return re.sub(r'^<svg[^>]*>|</svg>$', '', s.strip())

def svg(body, tc, bg=INK, tcolor=MUT):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360" role="img"><rect width="640" height="360" fill="{bg}"/>'
            f'{body}<text x="12" y="348" font-family="Georgia,serif" font-size="13" fill="{tcolor}">{tc}</text></svg>')

def glow(cx, cy, rx, ry, c=AMB, o=.25):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{c}" opacity="{o}"/><ellipse cx="{cx}" cy="{cy}" rx="{rx*.6}" ry="{ry*.6}" fill="{c}" opacity="{o}"/>'

def txt(x, y, s, size=22, c=TXT, anchor="start", w=400, fam="Georgia,serif", it=False):
    st = ' font-style="italic"' if it else ''
    return f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" fill="{c}" text-anchor="{anchor}" font-weight="{w}"{st}>{s}</text>'

def phone(cx, cy, w=70, lit=True, screen=AMB):
    h = w * 2
    return (f'<rect x="{cx-w/2}" y="{cy-h/2}" width="{w}" height="{h}" rx="10" fill="#000"/>'
            f'<rect x="{cx-w/2+5}" y="{cy-h/2+8}" width="{w-10}" height="{h-16}" rx="6" fill="{screen if lit else DEEP}"/>')

def table(y=265):
    return f'<rect x="0" y="{y}" width="640" height="{360-y}" fill="#06080b"/><rect x="0" y="{y}" width="640" height="2" fill="#1d2430"/>'

def mug(x, y):
    return f'<rect x="{x}" y="{y}" width="22" height="26" rx="4" fill="#1b212c"/><path d="M{x+22} {y+6} q10 0 10 8 q0 8 -10 8" fill="none" stroke="#1b212c" stroke-width="4"/>'

def pastor(x, y=215, s=1.0):
    # seated silhouette from behind: head and shoulders, no face
    return (f'<g transform="translate({x} {y}) scale({s})"><circle cx="0" cy="-58" r="26" fill="#05070a"/>'
            f'<path d="M-70 60 Q-72 -22 -34 -30 Q0 -20 34 -30 Q72 -22 70 60 Z" fill="#05070a"/></g>')

def hand(x, y, rot=0, c="#05070a", s=1.0):
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})" fill="{c}">'
            '<rect x="-30" y="-8" width="60" height="46" rx="16"/>'
            '<rect x="-30" y="-52" width="12" height="52" rx="6"/><rect x="-15" y="-60" width="12" height="60" rx="6"/>'
            '<rect x="0" y="-58" width="12" height="58" rx="6"/><rect x="15" y="-50" width="12" height="50" rx="6"/>'
            '<rect x="-52" y="-4" width="30" height="13" rx="6" transform="rotate(-24 -52 0)"/></g>')

def family_window(x=320, y=150, scale=1.0):
    g = (f'<g transform="translate({x} {y}) scale({scale})"><rect x="-90" y="-100" width="180" height="200" rx="90" fill="#05070a"/>'
         f'<rect x="-78" y="-88" width="156" height="176" rx="78" fill="{AMB}"/><rect x="-78" y="-12" width="156" height="100" fill="{AMB}"/>')
    def person(px, h, w):
        return (f'<circle cx="{px}" cy="{88-h-w*.55}" r="{w*.42}" fill="#05070a"/>'
                f'<path d="M{px-w/2} 88 V{88-h*.7} Q{px-w/2} {88-h-w*.1} {px} {88-h-w*.1} Q{px+w/2} {88-h-w*.1} {px+w/2} {88-h*.7} V88 Z" fill="#05070a"/>')
    g += person(-38, 70, 30) + person(-6, 46, 22) + person(18, 50, 22) + person(46, 72, 30)
    return g + '<path d="M0 -88 V88 M-78 8 H78" stroke="#05070a" stroke-width="3"/></g>'

def shoes(x=60, y=300, s=.8):
    return f'<g transform="translate({x} {y}) scale({s})">' + _inner('images/shoes-door.svg').split('</rect>')[-1][-700:] + '</g>'

def lantern(cx, cy, size=64, color=AMB, lit=True):
    inner = _inner('../branding/logo-mark.svg').replace('#e8a33d', color)
    return f'<g transform="translate({cx-size/2} {cy-size/2}) scale({size/64})">{inner}</g>'

def app(cx, cy, w=150, step=1, strip=None, dark=True):
    h = w * 1.9; x0, y0 = cx - w/2, cy - h/2
    b = f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="14" fill="#000"/><rect x="{x0+6}" y="{y0+8}" width="{w-12}" height="{h-16}" rx="9" fill="{INK}"/>'
    for i in range(5):
        on = i < step
        b += f'<circle cx="{x0+22+i*(w-44)/4}" cy="{y0+30}" r="6" fill="{AMB if on else "#2a3140"}"/>'
    for j, ww in enumerate([.7, .9, .5, .8, .6]):
        b += f'<rect x="{x0+16}" y="{y0+56+j*18}" width="{(w-32)*ww}" height="7" rx="3.5" fill="#2a3140"/>'
    b += f'<rect x="{x0+16}" y="{y0+h-60}" width="{(w-32)/2-4}" height="24" rx="8" fill="{AMB}"/><rect x="{x0+16+(w-32)/2+4}" y="{y0+h-60}" width="{(w-32)/2-4}" height="24" rx="8" fill="#2a3140"/>'
    if strip == "red":
        b += f'<rect x="{x0+12}" y="{y0+h-100}" width="{w-24}" height="26" rx="8" fill="{RED}"/><rect x="{x0+20}" y="{y0+h-90}" width="{w-60}" height="6" rx="3" fill="#fff" opacity=".85"/>'
    if strip == "green":
        b += f'<rect x="{x0+12}" y="{y0+h-100}" width="{w-24}" height="26" rx="8" fill="{GRN}"/><rect x="{x0+20}" y="{y0+h-90}" width="{w/2}" height="6" rx="3" fill="#fff" opacity=".85"/>'
    return b

def clock(s, x=320, y=70, size=56, c=AMB, anchor="middle"):
    return txt(x, y, s, size, c, anchor, 600)

def card_entry(x=320, y=60, light=True):
    c = INK if light else TXT
    return (lantern(x-130, y+22, 40, DAMB if light else AMB) + txt(x-100, y+40, "Nury", 54, c, "start", 600) +
            txt(x-100, y+68, "/NOO-ree/  proper noun", 16, MUT if light else MUT, "start", 400, "Arial,sans-serif", True) +
            txt(x-100, y+100, "1. A given name from Arabic nūr, “light”.", 18, c, "start", 400, "Arial,sans-serif") +
            txt(x-100, y+126, "2. An AI crisis response agent.", 18, c, "start", 400, "Arial,sans-serif") +
            txt(x-100, y+156, "see also: lantern", 14, MUT, "start", 400, "Arial,sans-serif", True))

def tech(c1=AMB, bg=INK):
    xs = [60, 190, 320, 450, 580]; labs = ["pastor", "tokens", "Gloo AI Studio", "checks", "a person"]
    b = ""
    for i, (x, l) in enumerate(zip(xs, labs)):
        b += f'<rect x="{x-48}" y="150" width="96" height="46" rx="10" fill="{DEEP}" stroke="{c1}" stroke-width="2"/>' + txt(x, 178, l, 13, TXT, "middle", 400, "Arial,sans-serif")
        if i: b += f'<path d="M{xs[i-1]+48} 173 H{x-48}" stroke="{c1}" stroke-width="2"/>'
    b += txt(320, 240, "leak test 90 checks, 0 found  ·  judge unsafe 0.89–0.98, safe 0.02–0.24", 14, MUT, "middle", 400, "Arial,sans-serif")
    b += txt(320, 262, "a full package: 50 to 56 s, about 9 cents", 14, MUT, "middle", 400, "Arial,sans-serif")
    b += txt(320, 300, "Evaluation harness uses the Jev decision API from TypeSafe as typed judges; disclosed as third-party technology per the rules.", 9.5, "#6f6a5f", "middle", 400, "Arial,sans-serif")
    return b

def memorial():
    b = lantern(320, 110, 56, DAMB)
    for i, w in enumerate([300, 400, 190, 230, 150]):
        b += f'<rect x="{320-w/2}" y="{168+i*22}" width="{w}" height="8" rx="4" fill="#c9bfa8"/>'
    return b + txt(320, 300, "Juan’s words, text only, no voice", 12, MUT, "middle", 400, "Arial,sans-serif", True)

def eric(s):
    return f'<rect x="12" y="304" width="{min(616, 7.8*len(s)+52)}" height="26" rx="13" fill="#000" opacity=".55"/>' + txt(26, 322, f"Eric: “{s}”", 14, TXT, "start", 400, "Arial,sans-serif")
