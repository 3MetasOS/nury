"""Render Eric's 11 approved lines (presentation/ERIC_LINES.md) with ElevenLabs. One take per line, same settings as the audition.
Text is sent exactly as the sheet says ('Nury' normal spelling; 2:07 AM as 'two oh seven A M'). Output: vo/arc/L1.wav .. L11.wav (-16 LUFS, 48 kHz mono), durations in vo/arc/durations.json.
Key from env or repo-root .env; never printed. Usage: python3 vo/eleven_arc.py [--dry] [L3 L6 ...]  (names = retake only those)"""
import json, subprocess, sys, tempfile
from pathlib import Path
here = Path(__file__).resolve().parent
src = open(here / "eleven_audition.py").read().replace("__file__", repr(str(here / "eleven_audition.py")))
ns = {"__name__": "ea"}; exec(compile(src, "ea", "exec"), ns)
call, SETTINGS = ns["call"], ns["SETTINGS"]
ERIC = "cjVigY5qzO86Huf0OWal"
L = {"L1": "Two oh seven A M. Maria is calling.", "L2": "Her husband was detained last evening.", "L3": "This is Nury.", "L4": "Five stages. A gate after each.",
     "L5": "Her language. Every point cited.", "L6": "Unsafe draft. Rejected. He never sees it.", "L7": "Gloo AI Studio writes, seeing tokens, not names.",
     "L8": "Jev checks every draft. People decide.", "L9": "A warm message. His to edit.", "L10": "Nury is not a pastor. It never sends.",
     "L11": "An AI crisis response agent.",
     "E1": "He types what she says.", "E4": "Pick a crisis. Triage comes first.", "E5": "Approve, edit or stop.", "E6": "Only from vetted sources.",
     "E7": "It rewrites. It checks again.", "E8": "Then contacts, a checklist, a message.", "E9": "He changes one word."}
want = [a for a in sys.argv[1:] if a[:1] in "LE" and a != "--dry"] or list(L)
print(len(want), "lines,", sum(len(L[k]) for k in want), "characters")
if "--dry" in sys.argv: sys.exit()
out = here / "arc"; out.mkdir(exist_ok=True); dpath = out / "durations.json"
dur = json.load(open(dpath)) if dpath.exists() else {}
for k in want:
    mp3 = call(f"/v1/text-to-speech/{ERIC}?output_format=mp3_44100_128", {"text": L[k], "model_id": "eleven_multilingual_v2", "voice_settings": SETTINGS}, raw=True)
    with tempfile.NamedTemporaryFile(suffix=".mp3") as f:
        f.write(mp3); f.flush()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f.name, "-af", "loudnorm=I=-16:TP=-1.5:LRA=7", "-ar", "48000", "-ac", "1", str(out / f"{k}.wav")], check=True)
    dur[k] = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out / f"{k}.wav")], capture_output=True, text=True).stdout)
    with open(here / "auditions" / "LOG.md", "a") as f: f.write(f"- ARC Eric {k}: {len(L[k])} characters\n")
    print(k, round(dur[k], 2), "s")
json.dump(dur, open(dpath, "w"), indent=1)
