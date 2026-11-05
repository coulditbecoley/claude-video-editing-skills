"""Verify an exported edit against its EDL: picture sync, voice sync, loudness.

usage: python verify_export.py <export.mp4>
Picture: every plain segment (no zoom or punch-in) is frame-matched to its source
time and must be closer to it than to the source shifted by +-0.5 s.
Voice: the export audio is cross-correlated with the voice the EDL says should
play, in 8 s windows; every window must line up within one frame (33 ms).
"""
import json
import subprocess
import sys

import numpy as np

EXP = sys.argv[1]
e = json.load(open("edit.edl.json"))
SR = 8000


def frame(path, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1",
                          "-vf", "scale=160:90,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).astype(float)


def pcm(path, ss, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ss:.3f}", "-t", f"{t:.3f}", "-i", path, "-vn",
                          "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(float)


imgs = [(i["start"], i["start"] + i["duration"]) for i in e["images"]]
off, pic_bad, pic_n = 0.0, [], 0
for s in e["segments"]:
    d = s["out"] - s["in"]
    for frac in ((0.3, 0.7) if "frame" not in s and "zoom" not in s and "drift" not in s and d > 0.8 else ()):
        to = off + d * frac
        if not any(a - 0.2 <= to <= b + 0.2 for a, b in imgs):
            src, ts = s.get("source", e["source"]), s["in"] + d * frac
            a = frame(EXP, to)
            right = np.abs(a - frame(src, ts)).mean()
            wrong = min(np.abs(a - frame(src, ts + dt)).mean() for dt in (-0.5, 0.5))
            if wrong >= 0.4:     # skip static shots: the source barely changes, so the test can't discriminate
                pic_n += 1
                if right >= wrong:
                    pic_bad.append((round(to, 1), round(right, 2), round(wrong, 2)))
    off += d
total = off
print(f"picture: {pic_n} segments checked, {len(pic_bad)} out of sync {pic_bad}")

# expected voice for the whole timeline
parts = []
for s in e["segments"]:
    parts.append(pcm(e["voice"][s.get("source", e["source"])], s["in"], s["out"] - s["in"]))
expv = np.concatenate(parts)
got = pcm(EXP, 0, total)
n = min(len(expv), len(got))
env = lambda x: np.convolve(np.abs(x[:n]), np.ones(80) / 80, "same")[::40]   # 5 ms envelope
A, B = env(expv), env(got)
worst = 0
for w0 in range(0, int(total) - 8, 8):
    a, b = A[w0 * 200:(w0 + 8) * 200], B[w0 * 200:(w0 + 8) * 200]
    if a.std() < 1e-6 or b.std() < 1e-6:
        continue
    a, b = (a - a.mean()) / a.std(), (b - b.mean()) / b.std()
    cc = [np.dot(a[max(0, l):len(a) + min(0, l)], b[max(0, -l):len(b) - max(0, l)]) / len(a) for l in range(-40, 41)]
    lag = (int(np.argmax(cc)) - 40) * 5
    worst = max(worst, abs(lag))
    if abs(lag) > 33:
        print(f"  voice off at {w0}-{w0 + 8}s: {lag} ms (corr {max(cc):.2f})")
print(f"voice: worst window offset {worst} ms over {total:.0f} s")

lo = subprocess.run(["ffmpeg", "-v", "info", "-i", EXP, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"],
                    capture_output=True, text=True).stderr
summary = lo[lo.rfind("Summary"):]
print("loudness:", " ".join(l.strip() for l in summary.splitlines() if l.strip().startswith(("I:", "Peak:"))))
ok = not pic_bad and worst <= 33
print("VERIFY", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
