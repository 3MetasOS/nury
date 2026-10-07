#!/usr/bin/env python3
"""Synthesize the sound assets for the 90 s film (treatment A). Everything is generated in code: no samples, nothing to license.
Writes 48 kHz mono 16-bit WAVs to remotion/public/arc/snd/. The cut places them relative to scene starts (see NuryA.tsx).
Usage: python3 sound/build_arc_sound.py"""
import wave
from pathlib import Path
import numpy as np
SR = 48000; rng = np.random.default_rng(7)
out = Path(__file__).resolve().parent.parent / "remotion" / "public" / "arc" / "snd"; out.mkdir(parents=True, exist_ok=True)
def t_(d): return np.arange(int(d * SR)) / SR
def save(name, x, peak=0.9):
    x = np.asarray(x, dtype=np.float64); m = np.max(np.abs(x)) or 1; x = x / m * peak
    with wave.open(str(out / f"{name}.wav"), "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())
def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a) * x[i] + a * s; y[i] = s
    return y
def env(d, a, r): t = t_(d); return np.minimum(1, t / max(a, 1e-3)) * np.minimum(1, (d - t) / max(r, 1e-3))
# room tone: brown noise, low-passed (18 s, loops by being placed twice if needed)
b = np.cumsum(rng.normal(size=int(18 * SR))); b -= np.linspace(b[0], b[-1], len(b)); save("room", lowpass(b / np.max(np.abs(b)), 320), 0.5)
# clock tick: 25 ms high-passed noise burst with fast decay, plus a faint low body
t = t_(0.06); n = rng.normal(size=len(t)); n = n - lowpass(n, 1500); save("tick", n * np.exp(-t / 0.006) + 0.4 * np.sin(2 * np.pi * 900 * t) * np.exp(-t / 0.012), 0.5)
# phone buzz: 140 Hz with 25 Hz flutter, 0.35 s
t = t_(0.35); save("buzz", np.sin(2 * np.pi * 140 * t) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 25 * t))) * env(0.35, 0.02, 0.05), 0.6)
# warm pad: A2 E3 A3 C#4 with slow detune, 3 s attack
def pad(d, notes, a=3.0, r=3.0, g=1.0):
    t = t_(d); x = sum(np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.004 * t + 1.3) for f in notes) * (1 + 0.08 * np.sin(2 * np.pi * 0.2 * t))
    return lowpass(x, 1100) * env(d, a, r) * g
save("pad", pad(30, [110, 164.8, 220, 277.2]), 0.8)
save("pad_back", pad(26, [110, 164.8, 220, 277.2, 329.6], a=2.0))
# resolve: A major with the 9th, warmer and a little higher
save("resolve", pad(8, [110, 164.8, 220, 277.2, 329.6, 493.9], a=0.8, r=3.0), 0.8)
# dawn tone: soft high sine, 3 s attack
t = t_(5); save("dawn", (np.sin(2 * np.pi * 880 * t) + 0.3 * np.sin(2 * np.pi * 1320 * t)) * env(5, 3.0, 1.5), 0.5)
# low note on "Passed": 110 Hz + 165 Hz, slow decay
t = t_(1.8); save("note", (np.sin(2 * np.pi * 110 * t) + 0.5 * np.sin(2 * np.pi * 165 * t)) * np.exp(-t / 0.7) * env(1.8, 0.02, 0.2), 0.8)
# foley, all noise shaped: chair creak, breath, keys, tap, page tick, paste
t = t_(0.9); c = rng.normal(size=len(t)); c = lowpass(c, 500 + 600 * (t / 0.9)[:len(c)].mean()) * (0.5 + 0.5 * np.sin(2 * np.pi * 14 * t)) ; save("creak", lowpass(c, 700) * env(0.9, 0.1, 0.4), 0.5)
t = t_(1.6); save("breath", lowpass(rng.normal(size=len(t)), 900) * np.sin(np.pi * t / 1.6) ** 2, 0.35)
def burst(d, fc, dec): t = t_(d); n = rng.normal(size=len(t)); n = n - lowpass(n, fc); return n * np.exp(-t / dec)
k = np.zeros(int(7 * SR))
for ts in np.cumsum(rng.uniform(0.07, 0.3, size=34)): 
    if ts < 6.8: i = int(ts * SR); b = burst(0.03, 900, 0.006); k[i:i + len(b)] += b * rng.uniform(0.5, 1)
save("keys", k, 0.35)
t = t_(0.18); save("tap", (np.sin(2 * np.pi * 180 * t) * np.exp(-t / 0.03) + 0.3 * burst(0.18, 600, 0.02)), 0.6)
save("page", burst(0.05, 2500, 0.012), 0.35)
save("paste", np.concatenate([burst(0.04, 800, 0.01), np.zeros(int(0.12 * SR)), burst(0.04, 800, 0.01)]), 0.4)
print("wrote", sorted(p.name for p in out.glob("*.wav")))
