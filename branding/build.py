"""Build the Nury logo files. Pure SVG out: the wordmark and tagline are converted to outlines.

Fonts (Fraunces, Inter; both SIL Open Font License) are read at build time from BRAND_FONT_DIR
(Fraunces.ttf, Inter.ttf, the Google Fonts variable files). Nothing here ships a font.
Usage: BRAND_FONT_DIR=/path python3 branding/build.py [option]   (option: c is the brand; "options" writes the archive)
"""
import os, sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

OUT = Path(__file__).resolve().parent
FD = Path(os.environ["BRAND_FONT_DIR"])
INK, SURFACE, TEXT, AMBER = "#0d1015", "#131824", "#ece7dc", "#e8a33d"
PAPER, AMBER_DEEP = "#f7f3ea", "#b8680f"   # light background and a darker amber that holds 3:1 on paper

def inst(name, axes):
    f = TTFont(FD / name)
    return instancer.instantiateVariableFont(f, axes, inplace=False)

FRAUNCES = inst("Fraunces.ttf", {"wght": 600, "opsz": 48, "SOFT": 0, "WONK": 0})
INTER = inst("Inter.ttf", {"wght": 500, "opsz": 14})

def text_path(font, text, size, x, y, tracking=0.0):
    gs = font.getGlyphSet(); cmap = font.getBestCmap(); upm = font["head"].unitsPerEm; s = size / upm
    d, pen_x = [], x
    for ch in text:
        g = cmap[ord(ch)]; sp = SVGPathPen(gs, ntos=lambda v: ('%.2f' % v).rstrip('0').rstrip('.'))
        gs[g].draw(TransformPen(sp, (s, 0, 0, -s, pen_x, y)))
        d.append(sp.getCommands()); pen_x += gs[g].width * s + tracking * size
    return " ".join(d), pen_x - x

# ---- marks, 64 x 64 grid. Each is one shape; flame is a cutout (evenodd) so it works in one colour. ----
FLAME = "M32 30 C36.5 35 38.5 38.5 38.5 42.2 A6.5 6.5 0 0 1 25.5 42.2 C25.5 38.5 27.5 35 32 30 Z"
MARKS = {
 # A: a lantern with a peaked roof and a ring. Solid, flame cut out of the glass.
 "a": ('<path fill-rule="evenodd" d="M32 14.2 L46.6 25 H17.4 Z '
       'M20.4 27 H43.6 L42 49.4 H22 Z M32 30.6 C36 35 37.8 38 37.8 41.4 A5.8 5.8 0 0 1 26.2 41.4 C26.2 38 28 35 32 30.6 Z '
       'M18.4 51.2 H45.6 Q47.2 51.2 47.2 52.8 V55.4 H16.8 V52.8 Q16.8 51.2 18.4 51.2 Z"/>'
       '<circle cx="32" cy="9.4" r="3.4" fill="none" stroke-width="2.4"/>', "stroke"),
 # B: arched lantern hung from a loop of cord. The arch keeps it plain; the loop is the quiet nod to the cord.
 "b": ('<path fill-rule="evenodd" d="M19 51 V31.5 A13 13 0 0 1 45 31.5 V51 Z '
       'M32 29.6 C36.4 34.4 38.4 37.8 38.4 41.6 A6.4 6.4 0 0 1 25.6 41.6 C25.6 37.8 27.6 34.4 32 29.6 Z '
       'M16.4 53 H47.6 V56.6 H16.4 Z"/>'
       '<circle cx="32" cy="12" r="4.4" fill="none" stroke-width="2.6"/>'
       '<path fill="none" stroke-width="2.6" stroke-linecap="round" d="M32 16.4 V19.6"/>', "stroke"),
 # CS: C with heavier strokes, for sizes under 24 px and the favicon.
 "cs": ('<path fill="none" stroke-width="5.6" stroke-linejoin="round" d="M19 26 H45 L42.4 49 H21.6 Z"/>'
        '<path fill="none" stroke-width="5.6" stroke-linecap="round" d="M14.4 26 H49.6 M16.4 54.2 H47.6"/>'
        '<circle cx="32" cy="12" r="5.2" fill="none" stroke-width="3.6"/>'
        '<path fill="none" stroke-width="3.6" d="M32 17.2 V23"/>'
        '<path stroke="none" d="M32 31.2 C35.4 35 36.8 37.6 36.8 40.4 A4.8 4.8 0 0 1 27.2 40.4 C27.2 37.6 28.6 35 32 31.2 Z"/>', "stroke"),
 # C: the Nury mark. Outline lantern, solid flame, ring at the top.
 "c": ('<path fill="none" stroke-width="4.2" stroke-linejoin="round" d="M21 25.4 H43 L40.8 50 H23.2 Z"/>'
       '<path fill="none" stroke-width="4.2" stroke-linecap="round" d="M16.6 25.4 H47.4 M18.6 53.8 H45.4"/>'
       '<circle cx="32" cy="12.2" r="4.6" fill="none" stroke-width="2.8"/>'
       '<path fill="none" stroke-width="2.8" d="M32 16.8 V22"/>'
       '<path stroke="none" d="M32 31.4 C35.8 35.6 37.4 38.4 37.4 41.2 A5.4 5.4 0 0 1 26.6 41.2 C26.6 38.4 28.2 35.6 32 31.4 Z"/>', "stroke"),
}

def mark_svg(opt, color, size=64, extra=""):
    body, kind = MARKS[opt]
    stroke_attr = f' stroke="{color}"' if kind else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="{size}" height="{size}" role="img" '
            f'aria-label="Nury lantern mark"{extra}><g fill="{color}"{stroke_attr}>{body}</g></svg>')

def mark_group(opt, color, x, y, scale):
    body, kind = MARKS[opt]
    stroke_attr = f' stroke="{color}"' if kind else ""
    return f'<g transform="translate({x} {y}) scale({scale})" fill="{color}"{stroke_attr}>{body}</g>'

def lockup(opt, mark_color, word_color, tag_color, bg=None, tagline=True):
    H = 96 if tagline else 72
    ms = 64 * (H / 96) if False else 64
    wd, ww = text_path(FRAUNCES, "Nury", 56, 82, 52, tracking=0.0)
    parts = []
    W = 82 + ww + 8
    if tagline:
        _td, _tw = text_path(INTER, "the crisis-response agent for solo pastors", 11.5, 84, 76, tracking=0.012); W = max(W, 84 + _tw + 8)
    if bg: parts.append(f'<rect x="-20" y="-12" width="{W+40:.0f}" height="104" fill="{bg}"/>')
    parts.append(mark_group(opt, mark_color, 0, 8, 1))
    parts.append(f'<path fill="{word_color}" d="{wd}"/>')
    if tagline:
        td, tw = text_path(INTER, "the crisis-response agent for solo pastors", 11.5, 84, 76, tracking=0.012)
        parts.append(f'<path fill="{tag_color}" d="{td}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-20 -12 {W+40:.0f} 104" width="{W+40:.0f}" height="104" role="img" '
            f'aria-label="Nury, the crisis-response agent for solo pastors">'+"".join(parts)+'</svg>'), W

def favicon(opt):
    body, kind = MARKS[opt + "s"] if opt + "s" in MARKS else MARKS[opt]
    stroke_attr = f' stroke="{AMBER}"' if kind else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="32" height="32">'
            f'<rect width="64" height="64" rx="14" fill="{INK}"/>'
            f'<g transform="translate(32 32) scale(1.12) translate(-32 -33)" fill="{AMBER}"{stroke_attr}>{body}</g></svg>')

if __name__ == "__main__":
    opt = sys.argv[1] if len(sys.argv) > 1 else "c"
    if opt == "options":
        ARCH = OUT / "archive"; ARCH.mkdir(exist_ok=True)
        cells = []
        for o, name in (("a", "A. Peaked lantern (not chosen)"), ("b", "B. Arched lantern, hung from a cord loop (not chosen)"), ("c", "C. Outline lantern (chosen)")):
            dk, _ = lockup(o, AMBER, TEXT, "#a9a59b", bg=INK)
            lt, _ = lockup(o, AMBER_DEEP, INK, "#55524a", bg=PAPER)
            cells.append(f'<section><h2>{name}</h2><div class="r"><div class="dk">{dk}</div><div class="lt">{lt}</div></div>'
              f'<div class="r s"><div class="dk"><span>64</span>{mark_svg(o,AMBER,64)}<span>32</span>{mark_svg(o,AMBER,32)}<span>16</span>{mark_svg(o,AMBER,16)}</div>'
              f'<div class="lt"><span>64</span>{mark_svg(o,INK,64)}<span>32</span>{mark_svg(o,INK,32)}<span>16</span>{mark_svg(o,INK,16)}<span>one colour</span></div></div></section>')
        html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Nury logo options (archive)</title>
<style>body{{margin:0;background:#111;color:#ece7dc;font:15px/1.5 system-ui,sans-serif;padding:20px}}h1{{font-family:Georgia,serif}}h2{{margin:.2em 0 .4em;font-size:18px}}
section{{margin:0 0 28px}}.r{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:10px;margin-bottom:10px}}
.dk,.lt{{border-radius:10px;padding:14px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}}.dk{{background:{INK}}}.lt{{background:{PAPER};color:{INK}}}
svg[aria-label^="Nury,"]{{max-width:100%;height:auto}}span{{font-size:12px;opacity:.7}}</style></head><body>
<h1>Nury logo options (archive)</h1><p>Juan chose C. A and B are kept here for the record.</p>{"".join(cells)}</body></html>'''
        (ARCH / "options.html").write_text(html)
        for o in ("a", "b"):
            (ARCH / f"logo-mark-{o}.svg").write_text(mark_svg(o, AMBER, 64))
        print("archive written")
    else:
        (OUT / "logo-mark.svg").write_text(mark_svg(opt, AMBER, 64))
        small = opt + "s"
        if small in MARKS: (OUT / "logo-mark-small.svg").write_text(mark_svg(small, AMBER, 64))
        s_, w = lockup(opt, AMBER, TEXT, "#a9a59b", bg=INK); (OUT / "logo-lockup.svg").write_text(s_)
        s_, _ = lockup(opt, AMBER_DEEP, INK, "#55524a", bg=PAPER); (OUT / "logo-lockup-light.svg").write_text(s_)
        (OUT / "favicon.svg").write_text(favicon(opt)); print("final", opt, round(w))
