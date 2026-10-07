"""Audition Kokoro-82M voices on VO lines 01-03 (locked text). Usage: kvenv/bin/python vo/kokoro_audition.py
Writes vo/auditions/kokoro_<voice>_<NN>.wav. Offline after the first model download."""
import soundfile as sf, sys
from pathlib import Path
from kokoro import KPipeline
here = Path(__file__).resolve().parent
lines = dict(l.strip().split('|', 1) for l in open(here / 'lines.txt') if l.strip())
voices = sys.argv[1:] or ['af_heart', 'af_nicole', 'am_michael']
pipe = KPipeline(lang_code='a')
for v in voices:
    for k in ['01', '02', '03']:
        audio = [a for _, _, a in pipe(lines[k], voice=v, speed=0.92)]
        import numpy as np
        sf.write(here / 'auditions' / f'kokoro_{v}_{k}.wav', np.concatenate(audio), 24000)
        print(v, k, 'ok')
