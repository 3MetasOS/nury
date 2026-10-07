#!/usr/bin/env python3
"""Prepare a clip Juan recorded for the Remotion composition 'JuanClip'.
Cleans the audio (clip/clean_clip.sh), copies the result to remotion/public/incoming/, reads an optional SRT into captions, and prints the render command.
Usage: python3 clip/prepare_clip.py incoming/take2.mp4 --start 5 --end 21 --duration 15 [--srt incoming/take2.srt]
Rules: the clip is cut to the duration or sped up/down by at most 5 percent; it is never stretched further. If it is shorter, the last frame holds."""
import argparse, json, re, subprocess, shutil
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument("clip"); ap.add_argument("--start", type=float, default=0); ap.add_argument("--end", type=float); ap.add_argument("--duration", type=float, required=True); ap.add_argument("--srt")
a = ap.parse_args(); here = Path(__file__).resolve().parent; pub = here.parent / "remotion" / "public" / "incoming"; pub.mkdir(parents=True, exist_ok=True)
clean = pub / (Path(a.clip).stem + "_clean.mp4")
subprocess.run([str(here / "clean_clip.sh"), a.clip, str(clean)], check=True)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(clean)], capture_output=True, text=True).stdout)
end = a.end or dur
caps = []
if a.srt:
    t = lambda x: sum(float(v) * m for v, m in zip(re.split("[:,]", x), (3600, 60, 1, .001)))
    for blk in open(a.srt, encoding="utf-8").read().replace("\r", "").strip().split("\n\n"):
        L = blk.split("\n")
        m = re.match(r"(\S+) --> (\S+)", L[1] if len(L) > 1 else "")
        if m: caps.append({"from": t(m.group(1)), "to": t(m.group(2)), "text": " ".join(L[2:])})
props = {"file": f"incoming/{clean.name}", "start": a.start, "end": end, "duration": a.duration, "captions": caps}
(pub / "props.json").write_text(json.dumps(props, indent=1))
print(json.dumps(props)[:300]); print("render: cd video/remotion && npx remotion render src/index.ts JuanClip out/juanclip.mp4 --props=public/incoming/props.json")
