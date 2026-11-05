"""Per-piece lip sync, any whole-frame lag (Day 35). The webcam lag mostly sits at ~85-100 ms or ~400-435 ms but
drifts through in-between values (317 ms at 110.8-114.2 s, 233 ms at 180-186 s, 60 fps scans), so a two-state model
leaves some pieces ~250 ms off. Here every kept unit (contiguous or overlapping pieces merged) gets the lag that
maximises mouth/voice correlation (60 fps track probe/m60/*, mouth opening vs the raw mic's 300-3000 Hz loudness,
both band-passed 2-8 Hz) over its own window (padded to >= 2.5 s), smoothed by a Viterbi over lags 0-36 frames
(60 fps) whose step cost is PEN per 100 ms of change, so a weak piece follows its neighbours and a strong one wins.
Shift = lag - 25 ms (the cleaned voice runs late), rounded to whole 30 fps frames. Writes sync_sections.json (one
section per unit, every edge in the cut between two units) and lip_units.txt.
usage: python lip_units.py [PEN=0.06]   (after gen_edl.py; re-run gen_edl.py afterwards)"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from scipy.signal import butter, filtfilt, sosfiltfilt

PEN = float(sys.argv[1]) if len(sys.argv) > 1 else 0.06
SRC = "D:/edits/0939/src.mp4"; FPS = 60; SR = 16000
m_all = np.full(int(2037.0 * FPS), np.nan)
for f in Path("probe/m60").glob("m60_*.npy"):
    a0 = float(f.stem[4:]); v = np.load(f); i0 = int(round(a0 * FPS))
    n = min(len(v), len(m_all) - i0); m_all[i0:i0 + n] = v[:n]
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-map", "0:a:0", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                     capture_output=True).stdout
x = sosfiltfilt(butter(4, [300, 3000], btype="band", fs=SR, output="sos"), np.frombuffer(raw, np.int16).astype(float))
c = lambda i: int(round(i * SR / FPS)); w = int(0.02 * SR)
e_all = np.array([np.sqrt(np.mean(x[max(0, c(i) - w // 2): c(i) + w // 2] ** 2)) if c(i) < len(x) else np.nan for i in range(len(m_all))])
e_all = np.log(np.nan_to_num(e_all, nan=np.nanmin(e_all)) + 1e-9 + 1)
m_f = m_all.copy(); m_f[~np.isfinite(m_f)] = np.nanmean(m_all)
bb, aa = butter(2, [2 / (FPS / 2), 8 / (FPS / 2)], btype="band")
M, E = filtfilt(bb, aa, m_f), filtfilt(bb, aa, e_all)
K = 37

def curve(t0, t1):
    i0, i1 = int(t0 * FPS), int(t1 * FPS)
    return np.array([np.corrcoef(M[i0:i1], E[i0 - s:i1 - s])[0, 1] for s in range(K)])

import os; os.environ['LIP_UNITS'] = '1'
import gen_edl as G
units = []
for a, b in sorted({(round(a, 3), round(b, 3)) for a, b, k in G.PS if k != "mont"}):
    if units and a <= units[-1][1] + 1e-3:
        units[-1] = (units[-1][0], max(units[-1][1], b))
    else:
        units.append((a, b))
R = []
for a, b in units:
    mid, half = (a + b) / 2, max((b - a) / 2, 1.25)
    R.append(curve(mid - half, mid + half))
R = np.nan_to_num(np.array(R), nan=0.0)
step = PEN * np.abs(np.arange(K)[:, None] - np.arange(K)[None, :]) / 6.0      # 6 frames at 60 fps = 100 ms
V = R[0].copy(); back = []
for r in R[1:]:
    tot = V[None, :] - step                       # [to, from]
    bi = tot.argmax(1); back.append(bi)
    V = tot[np.arange(K), bi] + r
path = [int(V.argmax())]
for bi in reversed(back):
    path.append(int(bi[path[-1]]))
path = path[::-1]
# round 2 (Codex #2): smoothing must not override strong own evidence. A unit whose own peak is r >= 0.40 and beats the
# smoothed choice by >= 0.10 keeps its own lag (110.85-114.16: own 317 ms r 0.52 vs smoothed 67 ms r 0.30)
# Short-window scans of the exact pieces (lip_local60.py) agreed with the own peaks at 419.2, 616.0, 833.2-839.8 and
# 1027.9 (low-lag islands inside high stretches), so the bar is r >= 0.28 with a 0.12 margin. MANUAL pins a unit where
# the exact-window scan contradicts the padded one (335.1-337.0: exact 417 ms r 0.42, padded 217 ms r 0.34).
OWN_R, OWN_MARGIN = 0.28, 0.12
MANUAL = {}
for j, r in enumerate(R):
    own = int(r.argmax())
    if r[own] >= OWN_R and r[own] - r[path[j]] >= OWN_MARGIN:
        path[j] = own
for j, (a, b) in enumerate(units):
    for k_, ms in MANUAL.items():
        if abs(a - k_) < 0.05:
            path[j] = int(round(ms * FPS / 1000))
secs, lines = [], []
for (a, b), r, k in zip(units, R, path):
    lag = k * 1000 / FPS
    fr = int(max(0, min(36, round((lag - 25) / (1000 / 60)))))   # whole 60 fps frames (we render at 60)
    own = int(r.argmax())
    flag = "  WEAK" if r[k] < 0.2 else ("  OVERRIDDEN" if r[own] - r[k] > 0.1 else "")   # WEAK = the SELECTED lag's r (Codex #2)
    lines.append(f"{a:8.2f}-{b:8.2f}  lag {lag:4.0f} ms -> {fr:2d} fr   r {r[k]:+.2f} (own best {own * 1000 / FPS:4.0f} ms r {r[own]:+.2f}){flag}")
    if secs and secs[-1][2] == fr:
        secs[-1][1] = b
    else:
        if secs:
            edge = round((secs[-1][1] + a) / 2, 3); secs[-1][1] = edge; secs.append([edge, b, fr])
        else:
            secs.append([0.0, b, fr])
secs[-1][1] = 2040.0
Path("lip_units.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
doc = ("Picture shift (s) per section, by VOICE source time, from lip_units.py: every kept unit gets the whole-frame lag "
       "that maximises its own mouth/voice correlation (60 fps, 2-8 Hz), smoothed across units by a Viterbi (step cost "
       f"{PEN} per 100 ms); shift = lag - 25 ms in whole 60 fps frames; every edge sits in the cut between two units. "
       "Per-unit evidence: lip_units.txt.")
json.dump({"_doc": doc, "sections": [[a, b, round(fr / 60, 6)] for a, b, fr in secs]}, open("sync_sections.json", "w"), indent=1)
from collections import Counter
print(len(units), "units;", len(secs), "sections; frames used:", dict(sorted(Counter(int(x.split('->')[1].split('fr')[0]) for x in lines).items())),
      "; weak", sum("WEAK" in l for l in lines), "; overridden", sum("OVERRIDDEN" in l for l in lines))
