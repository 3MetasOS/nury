#!/usr/bin/env python3
"""Cuts the deck's crops from the screenshots in presentation/screens (run after capture_screens.py).
chooser = the whole popup; gate = the stage-1 gate (captured at 420 px) cut to its title bar, the first lines of the draft, the feedback chips and the
Approve / Edit / Stop row (the middle of the draft is left out, shown as three dots); case-sequence = the five-stage sequence card."""
from pathlib import Path
from PIL import Image, ImageDraw
S = Path(__file__).resolve().parent
O = S.parent / "images" / "screens"
O.mkdir(exist_ok=True)
Image.open(S / "03-chooser-1280.png").convert("RGB").save(O / "chooser.png", optimize=True)
import numpy as np
im = Image.open(S / "05-gate-narrow-420.png").convert("RGB")     # the gate at 420 px wide: large text in a 500 px frame
W, H = im.size
top = im.crop((0, 0, W, 342))                                   # title bar, disclaimer, the first two lines of the draft
a = np.array(im)
chip = (abs(a[:, :, 0].astype(int) - 238) < 4) & (abs(a[:, :, 1].astype(int) - 230) < 5) & (abs(a[:, :, 2].astype(int) - 214) < 7)
rows = [r for r in np.where(chip.sum(axis=1) > 60)[0] if r > 1700]
bottom = im.crop((0, int(min(rows)) - 14, W, H))                 # the reason chips and Approve / Edit / Stop
gap = 48
out = Image.new("RGB", (W, top.height + gap + bottom.height), (255, 253, 248))
out.paste(top, (0, 0)); out.paste(bottom, (0, top.height + gap))
d = ImageDraw.Draw(out)
for k in (-1, 0, 1):
    d.ellipse((W // 2 + k * 28 - 6, top.height + gap // 2 - 6, W // 2 + k * 28 + 6, top.height + gap // 2 + 6), fill=(184, 104, 15))
out.save(O / "gate.png", optimize=True)
Image.open(S / "07-case-sequence-960.png").convert("RGB").save(O / "case-sequence.png", optimize=True)
