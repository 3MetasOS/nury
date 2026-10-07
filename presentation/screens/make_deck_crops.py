#!/usr/bin/env python3
"""Cuts the deck's crops from the screenshots in presentation/screens (run after capture_screens.py).
chooser = the whole popup; gate = the stage-1 gate card cut to its title bar, the first lines of the draft, the feedback chips and the
Approve / Edit / Stop row (the middle of the draft is left out, shown as three dots); case-sequence = the five-stage sequence card."""
from pathlib import Path
from PIL import Image, ImageDraw
S = Path(__file__).resolve().parent
O = S.parent / "images" / "screens"
O.mkdir(exist_ok=True)
Image.open(S / "03-chooser-1280.png").convert("RGB").save(O / "chooser.png", optimize=True)
card = Image.open(S / "05-gate-1280.png").convert("RGB").crop((630, 596, 1930, 2434))      # the whole gate card, 1300 px wide
top, bottom = card.crop((0, 0, 1300, 304)), card.crop((0, 1490, 1300, 1838))
gap = 64
out = Image.new("RGB", (1300, top.height + gap + bottom.height), (255, 253, 248))
out.paste(top, (0, 0)); out.paste(bottom, (0, top.height + gap))
d = ImageDraw.Draw(out)
for k in (-1, 0, 1):
    d.ellipse((650 + k * 30 - 7, top.height + gap // 2 - 7, 650 + k * 30 + 7, top.height + gap // 2 + 7), fill=(184, 104, 15))
out.save(O / "gate.png", optimize=True)
Image.open(S / "07-case-sequence-960.png").convert("RGB").save(O / "case-sequence.png", optimize=True)
