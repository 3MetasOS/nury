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
BG = (255, 253, 248)
def stack(parts, gaps):
    """Pieces of the card one under the other, with a gap between them; the first gap carries three dots."""
    h = sum(p.height for p in parts) + sum(gaps)
    img = Image.new("RGB", (W, h), BG); y = 0; marks = []
    for i, p in enumerate(parts):
        img.paste(p, (0, y)); y += p.height
        if i < len(gaps):
            marks.append(y + gaps[i] // 2); y += gaps[i]
    return img, marks
a = np.array(im)
chip = (abs(a[:, :, 0].astype(int) - 238) < 4) & (abs(a[:, :, 1].astype(int) - 230) < 5) & (abs(a[:, :, 2].astype(int) - 214) < 7)
cnt = chip.sum(axis=1)
runs, cur = [], None
for y in range(1700, H):
    on = cnt[y] > 40
    if on and cur is None: cur = y
    if not on and cur is not None: runs.append((cur, y)); cur = None
if cur: runs.append((cur, H))
chips_top, chips_bot = runs[0][0], runs[1][1]                    # the two rows of reason chips
btn_top, btn_bot = runs[2][0], runs[2][1]                        # Approve / Edit / Stop
parts = [im.crop((0, 0, W, 104)),                                  # the title bar
         im.crop((0, 200, W, 342)),                                # SITUATION and the first two lines of the draft
         im.crop((0, chips_top - 14, W, chips_bot + 8)),           # the reason chips
         im.crop((0, btn_top - 10, W, btn_bot + 16))]              # Approve / Edit / Stop
out, marks = stack(parts, [0, 40, 20])
d = ImageDraw.Draw(out)
for k in (-1, 0, 1):
    d.ellipse((W // 2 + k * 28 - 6, marks[1] - 6, W // 2 + k * 28 + 6, marks[1] + 6), fill=(184, 104, 15))
out.save(O / "gate.png", optimize=True)
Image.open(S / "07-case-sequence-960.png").convert("RGB").save(O / "case-sequence.png", optimize=True)
