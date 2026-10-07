#!/usr/bin/env python3
"""Measure an audio track so we can judge a cleanup without hearing it: integrated loudness, true peak, loudness range, and the noise floor
(the 10th percentile of 50 ms RMS levels: what the quietest moments sound like). Usage: python3 clip/measure.py file.(mp4|wav|m4a) [label]"""
import re, subprocess, sys
import numpy as np
f = sys.argv[1]; label = sys.argv[2] if len(sys.argv) > 2 else f
e = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", f, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
tail = e[e.rfind("Summary:"):]
g = lambda k: float(re.search(k + r":\s+(-?[\d.]+)", tail).group(1))
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
x = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768; n = 800  # 50 ms
rms = np.sqrt(np.mean(x[: len(x) // n * n].reshape(-1, n) ** 2, axis=1)) + 1e-9
db = 20 * np.log10(rms)
print(f"{label}: loudness {g('I'):.1f} LUFS, true peak {g('Peak'):.1f} dBFS, range {g('LRA'):.1f} LU, noise floor {np.percentile(db, 10):.1f} dB, speech level {np.percentile(db, 90):.1f} dB, speech-to-noise {np.percentile(db, 90) - np.percentile(db, 10):.1f} dB")
