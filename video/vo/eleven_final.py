"""Render the full narration with Eric (ElevenLabs premade). One file per locked line (lines.txt), same settings as the audition.
Lines with 'Nury' get two takes: NN.wav (normal spelling) and NN_noory.wav (respelling in the request only, never on screen).
Outputs go to remotion/public/vo/ at -16 LUFS, 48 kHz mono, and durations to vo/eleven_durations.json. Key from env or repo-root .env; never printed.
Usage: python3 vo/eleven_final.py [--dry]   (--dry prints the character count and exits)"""
import json, subprocess, sys, tempfile
from pathlib import Path
sys.argv_backup = sys.argv; here = Path(__file__).resolve().parent
src = open(here / "eleven_audition.py").read().replace("__file__", repr(str(here / "eleven_audition.py")))
ns = {"__name__": "ea"}; exec(compile(src, "ea", "exec"), ns)
call, SETTINGS, lines = ns["call"], ns["SETTINGS"], ns["lines"]
ERIC = "cjVigY5qzO86Huf0OWal"
jobs = [(k, k, t) for k, t in lines.items()] + [(k, k + "_noory", t.replace("Nury", "Noory")) for k, t in lines.items() if "Nury" in t]
total = sum(len(t) for _, _, t in jobs); print(len(jobs), "takes,", total, "characters")
if "--dry" in sys.argv: sys.exit()
out = here.parent / "remotion" / "public" / "vo"; out.mkdir(parents=True, exist_ok=True); dur = {}
log = here / "auditions" / "LOG.md"
for k, name, text in jobs:
    mp3 = call(f"/v1/text-to-speech/{ERIC}?output_format=mp3_44100_128", {"text": text, "model_id": "eleven_multilingual_v2", "voice_settings": SETTINGS}, raw=True)
    with tempfile.NamedTemporaryFile(suffix=".mp3") as f:
        f.write(mp3); f.flush()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f.name, "-af", "loudnorm=I=-16:TP=-1.5:LRA=7", "-ar", "48000", "-ac", "1", str(out / f"{name}.wav")], check=True)
    dur[name] = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out / f"{name}.wav")], capture_output=True, text=True).stdout)
    with open(log, "a") as f: f.write(f"- FINAL Eric {name}: {len(text)} characters\n")
    print(name, round(dur[name], 2), "s")
json.dump(dur, open(here / "eleven_durations.json", "w"), indent=1)
