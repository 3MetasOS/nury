#!/usr/bin/env python3
"""Cuts the deck's three crops from the screenshots in presentation/screens (run after capture_screens.py).
chooser = the whole popup; gate = the stage-1 gate card; case-overview = the case header, tabs and the five-stage sequence."""
from pathlib import Path
from PIL import Image
S = Path(__file__).resolve().parent
O = S.parent / "images" / "screens"
O.mkdir(exist_ok=True)
Image.open(S / "03-chooser-1280.png").convert("RGB").save(O / "chooser.png", optimize=True)
Image.open(S / "05-gate-1280.png").convert("RGB").crop((630, 596, 1930, 2434)).save(O / "gate.png", optimize=True)
Image.open(S / "07-case-overview-1280.png").convert("RGB").crop((208, 160, 2352, 1040)).save(O / "case-overview.png", optimize=True)
