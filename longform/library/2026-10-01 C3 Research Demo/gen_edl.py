"""Edit decisions for the C3 Research demo (OBS take 2026-10-01 10-19-41) as a ccut EDL.

One take: talking-head hook 0-30, the c3research.io landing + Request Research page 30-111,
DexScreener (three aborted takes 111-213, the clean one 213-234), back to C3, pay 234-311,
loading screen narration 311-344, then he leaves while the research runs (344-1142),
back at 1142 with the report, research library, X profile, talking-head outro from 1325.5.

Coley's ask: keep the loading screen but fast-forward it from when he hits load until he
comes back in to talk. His narration over the loading screen (311-344, "we're going to fast
forward through this...") stays at normal speed; the 40x starts at "I'll see you then"
and ends just before "And we are back".

No cursor tracker (Coley, 2026-10-01): zooms are aimed at the element being discussed,
on one continuous camera across pieces.
Graphics and cues are in SOURCE time and mapped onto the edited timeline.
v2 (Coley's review, 2026-10-01): the landing page plays full-frame (no zoom, no push, few cuts);
a Swipe + whoosh lands on the real tap into Request Research; the Base tile shows Base's mark;
the wallet phase is full-frame so you see it connect; then a polish pass on transitions and timing:
pauses are only cut where the screen is still (a pause cut while he scrolls made the page jump),
speech cuts that still jump get a short Dissolve, and every page change gets its transition on
the frame it happens (Read report, research library, the X tab), with chips landing after it.
v3 (Codex audit, Coley: "make your best recommended choices", 2026-10-01): the facecam is one fixed
size (zooms aim so the recording's own copy falls off-frame); the 40x eases to 15x for its last stage
so "Report ready" lands; the library and the whole exit are full-frame and static; Read report is a
clean hard cut on the click (speech keeps its breath); result cards say what the report says; the
hook, the 7-day reasoning and the repeated X pitch are trimmed; the CA zoom frames the copy row.
Run: python gen_edl.py  ->  edit.edl.json
"""
import json
import math
import re
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
MAIN = "~/Projects/Youtube/videos/2026-10-01 10-19-41.mp4"
GFX = HERE / "graphics" / "out"
AUD = HERE / "audio"
W, H = 3840, 2160
FF_SPEED = 40.0
FF_EASE, FF_EASE_AT = 15.0, 1098.0   # "Report ready" appears ~1098: the last stretch runs at 15x so it lands (~2.9 s)

def silences(path):
    t = re.findall(r"silence_(start|end): ([0-9.]+)", path.read_text())
    out, cur = [], None
    for kind, v in t:
        if kind == "start":
            cur = float(v)
        elif cur is not None:
            out.append((cur, float(v)))
            cur = None
    return out

SIL = silences(HERE / "silences-main.txt")

# (in, out, kind). Transition edges leave >= 0.35 s after the last word and >= 0.25 s before the first.
SPANS = [
    (1.75, 24.0, "talk"),       # hook: "Are you tired of the Robinhood rugs? ... Come with me."
    (31.62, 61.9, "screen"),     # landing page -> "head on over to Request Research and get started." (tap at 60.467)
    (75.35, 112.4, "screen"),    # Request Research page -> "head on over to DexScreener." (drops "We're on the...")
    (216.12, 252.05, "screen"),   # clean DexScreener take, Orbio, paste, pay options (drops the 3 aborted takes)
    (301.05, 344.0, "screen"),   # "And connect your wallet", pay, loading narration -> "I'll see you then."
    (344.0, 1141.55, "ff"),       # loading screen at 40x while he's away
    (1141.55, 1296.6, "screen"),  # "And we are back" -> report, research library
    (1298.5, 1352.6, "screen"),  # outro: "So that is how simple..." (X profile, then talking head from 1325.5)
]
TALK_FROM = 1325.6          # OBS crossfades screen -> talking head here (its own transition; kept)
OUTRO = 1298.5              # calm exit from here
MAX_GAP = 0.4
TAIL, HEAD = 0.14, 0.10
LANDING = (31.6, 60.47)     # Coley: full landing page the whole time, not so many cuts
LANDING_GAP = 1.2
FULL_FRAME = [LANDING, (245.0, 311.2),   # no zoom, no push: the landing page and the wallet connecting
              (1245.7, 1273.4), (1284.9, 1400.0)]   # the research library (an overview page) and the whole calm exit
OUTRO_GAP, OUTRO_TAIL, OUTRO_HEAD = 0.6, 0.2, 0.14

# Semantic cuts (source seconds): restatements, stumbles, filler, doubled words.
CUTS = [
    (21.50, 22.95),       # "I'm going to get into it." -> "...we have available. Come with me." (tighter hook)
    (36.28, 37.12),       # "uh," before "website"
    (38.40, 40.30),       # "It is, um," -> "website. Gives you a short example"
    (217.46, 217.70),     # doubled "you" in "the chain that you You are looking"
    (1142.92, 1143.98),   # "we are back, back with" -> "we are back with"
    (1151.50, 1151.97),   # the blank page between "Read report" and the report loading (inside the 0.65 s pause)
    (1188.75, 1190.80),   # "all of these answers," (restates "find all of these answers for you")
    (1193.76, 1194.15),   # doubled "if If you trust"
    (1217.94, 1218.50),   # stray "it."
    (1226.86, 1227.95),   # "a complete, complete deep dive" -> "a complete deep dive"
    (1234.42, 1236.30),   # "and they," -> "AI agents do not play. Their job"
    (1239.30, 1244.45),   # "So you can download it as a PDF if you want to save it. If not," (said at 1207 already)
    (1258.27, 1269.76),   # "and seven days is the max ... create a new report." restates "things change very fast" (cuts the hidden "you know," too)
    (1286.10, 1287.28),   # "So there you go. Yeah,"
    (1315.00, 1323.55),   # "So if you want to head on to X, follow us there. You're going to get updates every single day..." (one X pitch + the handle card is enough)
    (1347.38, 1348.45),   # "And yeah,"
]
# Splits that are not cuts (continuous source: no voice fade): tab switches mid-sentence,
# where the facecam turns on/off inside the fast-forward, and the outro's crossfade to camera.
# Each tab/page switch is split on the frame it happens (10 fps diff peaks, refined at 30 fps).
TAP, DEX_TAB, C3_TAB, LIBRARY, X_TAB = 60.45, 111.25, 233.75, 1245.78, 1306.48
SPLITS = [TAP, DEX_TAB, C3_TAB, 350.5, FF_EASE_AT, LIBRARY, X_TAB, TALK_FROM]   # no split where the cam returns at 1134.5: 0.18 s at 40x

# ---- what the screen does (frames.npz from frames_cache.py) ----------------------------
_F = np.load(HERE / "frames.npz")
_FR = [(float(k), _F[k]) for k in _F.files]
def frame_at(t):
    for t0, a in _FR:
        i = round((t - t0) * 10)
        if 0 <= i < len(a):
            return a[i].astype(np.int16)
    return None
def moves(t0, t1):
    """Per-0.1 s screen motion between t0 and t1 (None where not cached)."""
    out, t = [], t0
    while t + 0.1 <= t1 + 1e-6:
        a, b = frame_at(t), frame_at(t + 0.1)
        out.append(None if a is None or b is None else float(np.abs(a - b).mean()))
        t += 0.1
    return out
def jump(t0, t1):
    a, b = frame_at(t0), frame_at(t1)
    return 0.0 if a is None or b is None else float(np.abs(a - b).mean())
STILL = 1.0    # mean grey diff per 0.1 s below this = the screen is still (cursor moves score ~0.1)

def still_cut(a, b):
    """Longest stretch of [a, b] where the screen doesn't move: the part of a pause that can go
    without the page jumping. Talking head / uncached time counts as still."""
    m = moves(a, b)
    best, run_s = (a, a), None
    for i, v in enumerate(m + [99.0]):
        t = a + i * 0.1
        if v is None or v < STILL:
            run_s = t if run_s is None else run_s
        else:
            if run_s is not None and t - run_s > best[1] - best[0]:
                best = (run_s, t)
            run_s = None
    return best

def pieces():
    spans = []
    for a, b, kind in SPANS:
        cur = a
        for ca, cb in sorted(CUTS):
            if a < ca < b:
                spans.append((cur, ca, kind)); cur = cb
        spans.append((cur, b, kind))
    out = []
    for a, b, kind in spans:
        cur = a
        if kind != "ff":          # the fast-forward keeps every frame
            for s, e in SIL:
                outro = s >= OUTRO
                gap, tail, head = (OUTRO_GAP, OUTRO_TAIL, OUTRO_HEAD) if outro else (MAX_GAP, TAIL, HEAD)
                if LANDING[0] <= s < LANDING[1]:
                    gap = LANDING_GAP
                if e - s <= gap or s < a or e > b:
                    continue
                x, y = s + tail, e - head
                if kind == "screen":
                    x, y = still_cut(x, y)      # a scroll inside the pause plays out instead of jumping
                    if y - x < 0.25:
                        continue
                if x > cur:
                    out.append([cur, x, kind])
                cur = y
        out.append([cur, b, kind])
    res = []
    for a, b, kind in out:
        cuts = [c for c in SPLITS if a + 0.3 < c < b - 0.3]
        for x, y in zip([a] + cuts, cuts + [b]):
            k = "talk" if kind == "screen" and x >= TALK_FROM - 1e-6 else kind
            res.append([x, y, k])
    return [p for p in res if p[1] - p[0] > 0.05]

PS = pieces()
speed = lambda kind, a=0.0: (FF_EASE if a >= FF_EASE_AT - 1e-6 else FF_SPEED) if kind == "ff" else 1.0
dur = lambda p: (p[1] - p[0]) / speed(p[2], p[0])

def to_out(t):
    """Source second -> edited-timeline second (snaps into the nearest kept piece)."""
    off = 0.0
    for p in PS:
        a, b, kind = p
        if a - 0.4 <= t <= b + 0.4:
            return off + (min(max(t, a), b) - a) / speed(kind, a)
        off += dur(p)
    raise SystemExit(f"source {t} is cut out")

def cut_at(t):
    return round(to_out(t), 3)

TOTAL = sum(dur(p) for p in PS)

# ---- facecam --------------------------------------------------------------------
CAM = {"rect": [2920, 1428, 3714, 2034], "clip": str(HERE / "facecam-crop.mp4")}
CX0, CY0, CX1, CY1 = 2920 / W, 1428 / H, 3714 / W, 2034 / H
# when the recorded facecam is visible (cam_on.json: std of the box, 2 fps); gaps under 2 s are noise
CAM_ON = []
for a, b in json.loads((HERE / "cam_on.json").read_text()):
    if CAM_ON and a - CAM_ON[-1][1] < 2.0:
        CAM_ON[-1][1] = b
    else:
        CAM_ON.append([a, b])
cam_visible = lambda a, b: any(x <= a + 0.3 and b - 0.3 <= y for x, y in CAM_ON)

# ---- camera -------------------------------------------------------------------------
# Zoom windows (source in, out, scale, u, v): (u, v) is the centre of the element being talked about.
ZOOMS = [
    (79.3, 91.5, 1.6, 0.33, 0.40),      # "$19 per report", limited time offer
    (99.6, 111.2, 1.6, 0.38, 0.52),     # chain picker: Ethereum, Base, Solana, Robinhood
    (226.4, 233.6, 2.0, 0.92, 0.50),    # the ORBIO contract-address row and its copy button (right edge of the pair page)
    (237.6, 245.0, 1.6, 0.35, 0.45),    # paste the CA, Robinhood Chain selected
    (315.0, 1105.0, 1.5, 0.40, 0.55),   # loading: the ring, the stage name and the elapsed timer (through the 40x)
    (1153.3, 1161.4, 1.5, 0.38, 0.50),  # report header, "verdict unverified"
    (1171.0, 1178.6, 1.5, 0.52, 0.50),  # claim matrix: "what the token claims"
    (1210.8, 1222.3, 1.5, 0.52, 0.50),  # what stays unknown
    (1275.0, 1279.8, 1.5, 0.40, 0.50),  # Doggie Mode: prepare a fresh review (the page re-flows until 1274.8)
]
TAU_S, TAU_P = 0.22, 0.30        # camera smoothing (s, output time)
PUSH, PUSH_MAX = 0.0035, 0.04    # slow push outside zooms: +0.35%/s, capped at 4%

def window_at(t):
    for w in ZOOMS:
        if w[0] <= t < w[1]:
            return w
    return None

def allowed(s, u, v):
    """Keep the frame inside the picture and the zoomed facecam copy either off-frame or
    under the cam overlay (it grows from its top-left, so the copy must not start above/left of it)."""
    m = 0.5 / s
    clamp = lambda a: min(max(a, m), 1 - m)
    u, v = clamp(u), clamp(v)
    off_r = CX0 - 1 / s + m
    off_b = CY0 - 1 / s + m
    cov_u, cov_v = CX0 * (1 - 1 / s) + m, CY0 * (1 - 1 / s) + m
    # v3: the overlay never grows (Codex audit: a growing facecam reads as broken), so the copy must be off-frame
    if u <= off_r + 1e-9 or v <= off_b + 1e-9:
        return u, v
    cands = [(min(u, off_r), v), (u, min(v, off_b))]
    cands = [(clamp(a), clamp(b)) for a, b in cands]
    return min(cands, key=lambda c: (c[0] - u) ** 2 + (c[1] - v) ** 2)

def clamp_only(s, u, v):
    m = 0.5 / s
    return min(max(u, m), 1 - m), min(max(v, m), 1 - m)

def cam_grow(s, u, v):
    """v3: always 1.0 (fixed facecam). Kept as a check: anything else means the copy is visible."""
    l, t = u - 0.5 / s, v - 0.5 / s
    zx0, zy0 = (CX0 - l) * s, (CY0 - t) * s
    assert zx0 >= 1 - 1e-3 or zy0 >= 1 - 1e-3 or s < 1.0005, (s, u, v)
    return 1.0
    zx0, zy0, zx1, zy1 = (CX0 - l) * s, (CY0 - t) * s, (CX1 - l) * s, (CY1 - t) * s
    if zx0 >= 1 or zy0 >= 1:
        return 1.0
    g = max((min(zx1, 1) - CX0) / (CX1 - CX0), (min(zy1, 1) - CY0) / (CY1 - CY0), 1.0)
    return round(g + 0.015, 4)

def to_frame(s, u, v):
    return round(s, 4), round((0.5 - u) * 2 * s, 4), round((v - 0.5) * 2 * s, 4)

def camera():
    """Simulate one continuous camera over output time. Returns per piece index: (path keys, cam keys)."""
    res, state, push_from, off, prev_win = {}, None, 0.0, 0.0, None
    prev_kind = None
    for i, p in enumerate(PS):
        a, b, kind = p
        d = dur(p)
        if kind == "talk" and a < OUTRO:       # hook: punch-in alternation, not a camera move
            off += d; prev_kind = kind; state = None; prev_win = None
            continue
        if prev_kind not in ("screen", "ff") or (kind == "talk" and prev_kind != "talk"):
            push_from = off                    # a new section starts flat
            state = None
        cam_ok = kind != "talk" and cam_visible(a, b)
        n = max(2, math.ceil(d * 10) + 1)
        keys, cams = [], []
        for k in range(n):
            ts = a + (b - a) * k / (n - 1)
            to = off + d * k / (n - 1)
            w = window_at(ts) if kind != "talk" else None
            if w is not prev_win:
                if not w:
                    push_from = to
                prev_win = w
            if w:
                s_t, u_t, v_t = w[2], w[3], w[4]
            elif any(x <= ts < y for x, y in FULL_FRAME):
                s_t, u_t, v_t = 1.0, 0.5, 0.5
                push_from = to
            else:
                # v3: no slow push where the facecam is in the shot (any scale under ~1.3 shows its copy)
                s_t, u_t, v_t = (1.0 if cam_ok else 1 + min(PUSH * (to - push_from), PUSH_MAX)), 0.5, 0.5
            if cam_ok:
                # v3: with the facecam in the shot the camera snaps (a punch-in): a ramp through
                # 1.0-1.3x would show the recording's own facecam beside the fixed overlay.
                # A key one frame earlier holds the old framing so CapCut can't interpolate across.
                tgt = [s_t, *allowed(s_t, u_t, v_t)]
                if state is not None and keys and abs(tgt[0] - state[0]) > 1e-3 and d * k / (n - 1) > 0.04:
                    keys.append((round(d * k / (n - 1) - 0.034, 3), *to_frame(*state)))
                    cams.append((round(k / (n - 1) - 0.034 / d, 4), 1.0))
                state = tgt
            elif state is None:
                state = [s_t, u_t, v_t]
            else:
                dt = d / (n - 1) if k else 0.0
                if dt:
                    fs, fp = 1 - math.exp(-dt / TAU_S), 1 - math.exp(-dt / TAU_P)
                    state[0] += (s_t - state[0]) * fs
                    state[1] += (u_t - state[1]) * fp
                    state[2] += (v_t - state[2]) * fp
            # the facecam copy only matters where the facecam is in the recording
            fit = allowed if cam_ok else clamp_only
            u_, v_ = fit(state[0], state[1], state[2])
            state[1], state[2] = u_, v_
            keys.append((round(d * k / (n - 1), 3), *to_frame(state[0], u_, v_)))
            cams.append((round(k / (n - 1), 4), cam_grow(state[0], u_, v_) if cam_ok else 1.0))
        res[i] = (thin(keys), thin_cam(cams) if cam_ok else None)
        off += d
        prev_kind = kind
    return res

def thin(keys):
    """Drop keyframes a straight line through their neighbours already gives."""
    out = [keys[0]]
    for k in range(1, len(keys) - 1):
        p, q, r = out[-1], keys[k], keys[k + 1]
        f = (q[0] - p[0]) / ((r[0] - p[0]) or 1)
        if any(abs(q[j] - (p[j] + (r[j] - p[j]) * f)) > (0.0015 if j == 1 else 0.004) for j in (1, 2, 3)):
            out.append(q)
    out.append(keys[-1])
    return out

def thin_cam(cams):
    out = [cams[0]]
    for k in range(1, len(cams) - 1):
        if abs(cams[k][1] - out[-1][1]) > 0.004:
            out.append(cams[k])
    out.append(cams[-1])
    return out

CAMERA = camera()

# Transitions go on the segment that ENDS at this source second.
TRANSITIONS = {
    24.0: ("Zoom_Transition", 0.6),    # talking-head hook -> the site
    TAP: ("Swipe_Left", 0.45),         # the tap on Request Research -> the full request page
    DEX_TAB: ("Swipe_Left", 0.4),      # tab switch to DexScreener, mid-sentence
    C3_TAB: ("Swipe_Left", 0.4),       # tab switch back to C3, mid-sentence
    1141.55: ("White_Flash", 0.35),    # out of the fast-forward: "And we are back"
    LIBRARY: ("Swipe_Left", 0.4),      # the research library, mid-sentence
    X_TAB: ("Swipe_Left", 0.4),        # tab switch to X, mid-sentence
}
# A speech cut on a screen that moved still jumps: soften it with a short Dissolve (free in CapCut)
DISSOLVE, JUMP = ("\u53e0\u5316", 0.3), 2.5
for i in range(len(PS) - 1):
    (a0, b0, k0), (a1, b1, k1) = PS[i], PS[i + 1]
    # 1151.50 (Read report) and 1286.10 (back to the library) are clicks: a hard cut reads as navigation,
    # a dissolve there doubled two dense pages (Codex audit 4:59)
    if k0 == k1 == "screen" and abs(b0 - a1) > 1e-3 and not any(abs(t - b0) < 0.01 for t in TRANSITIONS) \
            and not any(abs(t - b0) < 0.01 for t in (1151.50, 1286.10)) \
            and b0 - a0 > 0.45 and b1 - a1 > 0.45 and jump(b0 - 0.05, a1) > JUMP:
        TRANSITIONS[b0] = DISSOLVE

segments, talk_i = [], 0
for i, p in enumerate(PS):
    a, b, kind = p
    seg = {"in": round(a, 3), "out": round(b, 3)}
    if kind == "ff":
        seg["speed"] = speed(kind, a)
        seg["mute"] = True                     # no chipmunk voice: music carries the fast-forward
    if i in CAMERA:
        keys, cams = CAMERA[i]
        seg["path"] = keys
        if cams:
            # the recorded facecam stays whole: its own crop sits over every piece where it's visible,
            # growing (anchored top-left) just enough to hide the camera's zoomed copy
            seg["cam_overlay"] = {**CAM, "keys": cams}
    elif kind == "talk":
        if talk_i % 2:
            seg["frame"] = {"scale": 1.12}      # alternate framing hides the jump cut
        talk_i += 1
    for tt, (name, d) in TRANSITIONS.items():
        if abs(tt - b) < 0.01:
            seg["transition"] = {"name": name, "duration": d}
    segments.append(seg)

# ---- graphics -------------------------------------------------------------------------
images, sfx = [], []
MAN = json.loads((GFX / "manifest.json").read_text())
TOP_R = (3260, 330)      # logo pop-ups
TOP_L = (720, 250)       # section chips
STAT = (1920, 360)       # number callouts
LOW = (1920, 1830)       # talking head: on the chest, never over the face

def img(name, t, d, x, y, scale=1.0, sound="pop", at=None):
    at = cut_at(t) if at is None else at
    half = MAN[name]["w"] * scale / 2
    if (x, y) == TOP_L:
        x = round(80 + half)
    elif (x, y) == TOP_R:
        x = round(3760 - half)
    images.append({"path": str(GFX / f"{name}.png"), "start": at, "duration": d, "x": x, "y": y, "scale": scale})
    if sound:
        sfx.append({"path": str(AUD / ("pop.mp3" if sound == "pop" else "sfx-impact.mp3")),
                    "start": at, "volume": 0.3 if sound == "pop" else 0.5})

# hook (talking head)
img("hook-title", 3.18, 3.0, 1920, 250, scale=0.95)                  # "Robinhood rugs?"
img("logo-c3", 9.3, 3.2, *TOP_R)                                     # "our C3 Research AI-powered audit tool"
img("stat-agents", 14.6, 3.6, *LOW, scale=0.9)                       # "AI agents to audit any CA token contract"
# the site
img("chip-site", 33.3, 2.8, *TOP_L)
img("site-card", 34.4, 3.4, *TOP_R)                                  # "landing page of the C3 Research website"
img("chip-request", 61.6, 2.6, *TOP_L)                              # the request page lands at 60.47 (+ swipe)
img("stat-price", 81.58, 3.4, *STAT)                                 # "19 bucks per report"
img("stat-hours", 89.08, 3.0, *STAT)                                 # "Save yourself hours and hours of research"
img("stat-unbiased", 93.5, 3.4, *STAT)                               # "They are unbiased"
img("chains", 99.9, 4.4, 3160, 420, scale=0.9)                       # "Ethereum, Base, Solana and Robinhood chain"
img("logo-dex", 112.35, 3.0, *TOP_R)                                  # "head on over to DexScreener"
# picking the token, paying
img("chip-token", 216.9, 2.6, *TOP_L)
img("card-orbio", 222.64, 3.0, *TOP_R)                               # "we're just going to go with Orbio"
img("stat-ca", 229.9, 3.0, *STAT)                                    # "grab the Orbio contract address"
img("stat-pay", 248.38, 3.4, *STAT)                                  # "Solana, USDT, USDC"
img("logo-phantom", 304.4, 3.0, *TOP_L)                              # Phantom pop-up is top right: card goes left
# PROGRESS_STEPS: the five steps, current one lit as he reaches it (bottom-left, clear of the facecam)
STEP_AT = [216.6, 229.9, 235.5, 245.98, 311.48, 316.3]
for k in range(5):
    a, b = cut_at(STEP_AT[k]), cut_at(STEP_AT[k + 1])
    images.append({"path": str(GFX / f"steps-{k + 1}.png"), "start": a, "duration": round(b - a, 3),
                   "x": 1060, "y": 1900, "scale": 0.85, "pop": "in" if k == 0 else ("out" if k == 4 else False)})
sfx.append({"path": str(AUD / "pop.mp3"), "start": cut_at(STEP_AT[0]), "volume": 0.3})
img("chip-agents", 315.2, 2.8, *TOP_L)                               # the loading page lands at 314.5
img("stat-bonding", 329.4, 4.6, *STAT)                               # "has already completed its bonding curve"
# the fast-forward: badge for the whole run, the page's own stages mirrored on a strip
t_ff, t_back = cut_at(344.0), cut_at(1141.55)
img("ff-badge", 0, round(cut_at(FF_EASE_AT) - t_ff - 0.15, 3), *TOP_L, at=round(t_ff + 0.15, 3))   # 40x only
STAGE_AT = [344.0, 452.0, 678.0, 1008.0, 1098.0, 1140.2]             # read off the loading page (15 s resolution)
for k in range(5):
    a, b = cut_at(STAGE_AT[k]) + (0.3 if k == 0 else 0), cut_at(STAGE_AT[k + 1])
    images.append({"path": str(GFX / f"stage-{k + 1}.png"), "start": round(a, 3), "duration": round(b - a, 3),
                   "x": 1920, "y": 1900, "scale": 0.9, "pop": "in" if k == 0 else ("out" if k == 4 else False)})
    sfx.append({"path": str(AUD / "pop.mp3"), "start": round(a, 3), "volume": 0.22})
sfx.append({"path": str(AUD / "sfx-riser.mp3"), "peak_at": t_back, "volume": 0.3})
sfx.append({"path": str(AUD / "sfx-whoosh.mp3"), "peak_at": round(t_ff + 0.05, 3), "volume": 0.32})   # into the 40x
# the report
img("stat-ready", 1145.5, 3.4, *STAT)                                # "back with a completed report"
img("chip-report", 1153.4, 2.8, *TOP_L)
img("stat-verdict", 1160.35, 3.6, *STAT, sound="hit")                # punchline: "verdict unverified"
img("stat-pdf", 1207.6, 3.0, *STAT)                                  # "download this as a PDF"
img("stat-unknowns", 1211.0, 3.6, *STAT)                             # "Some unknowns"
img("stat-play", 1233.0, 3.4, *STAT)                                 # "AI agents do not play"
img("chip-library", 1246.95, 2.8, *TOP_L)                            # after the swipe into the library
img("stat-7days", 1252.2, 3.4, *STAT)                                # "viewed for seven days"
img("stat-fresh", 1276.4, 3.4, *STAT)                                # "prepare a fresh review"
# outro: one card at a time
img("logo-x", 1307.6, 3.8, *TOP_R)                                   # after the swipe to the X tab
img("stat-network", 1330.5, 3.4, *LOW, scale=0.9)                    # "add a network"
img("cta-subscribe", 1338.14, 2.3, 1920, 1700)                       # "please subscribe"
img("stat-affiliate", 1340.8, 3.6, *LOW, scale=0.9)                  # "affiliate program dropping soon"
FADE = 1.2
images.append({"path": str(GFX / "black-4k.png"), "start": round(TOTAL - FADE, 3), "duration": FADE, "x": 1920, "y": 1080, "pop": "fade"})

for t, (name, d) in TRANSITIONS.items():
    if (name, d) != DISSOLVE:      # a dissolve smooths a cut; it isn't a scene change, so no whoosh
        quiet = t == 1151.50   # words sit 0.13 s / 0.07 s either side of this one: keep its whoosh low
        sfx.append({"path": str(AUD / "sfx-whoosh.mp3"), "peak_at": cut_at(t), "volume": 0.18 if quiet else 0.38 if d >= 0.5 else 0.28})

# ---- music: a new bed per section, cut dead on "verdict unverified" -------------------
BEDS = {"jonas": (AUD / "music-jonas.mp3", -8.9, 136.9), "verclub": (AUD / "music-verclub.mp3", -7.6, 130.3),
        "vaitsez": (AUD / "music-vaitsez.mp3", -8.2, 174.4)}
def bed(name, at, end, target=-30.0, offset=0.0):
    path, lufs, length = BEDS[name]
    return {"path": str(path), "at": round(at, 3), "start_offset": offset,
            "duration": round(min(end - at, length - offset), 3), "volume": round(10 ** ((target - lufs) / 20), 3)}

def fill(start, end, names, target=-30.0, fade_out=1.2, fade_in=1.0):
    cues, t, i = [], start, 0
    while end - t > 0.5:
        c = bed(names[i % len(names)], t, end, target)
        c["fade_in"], c["fade_out"] = fade_in, fade_out
        cues.append(c)
        t += c["duration"]
        i += 1
    cues[-1]["fade_out"] = fade_out
    return cues

t_screen = cut_at(31.62)
t_dex = cut_at(216.12)
t_load = cut_at(311.48)
t_dead = cut_at(1160.35)      # "verdict unverified": music stops dead, impact hit
t_resume = cut_at(1162.0)     # "So we're not gonna read all this"
t_outro = cut_at(1298.5)
music = (fill(0.0, t_screen, ["jonas"], target=-28.0, fade_out=0.6)
         + fill(t_screen, t_dex, ["verclub"])
         + fill(t_dex, t_load, ["vaitsez"])
         + fill(t_load, t_ff, ["verclub"], fade_out=0.3)
         + fill(t_ff, t_back, ["jonas"], target=-20.0, fade_out=0.4, fade_in=0.3)   # no voice: the bed carries the 40x
         + fill(t_back, t_dead, ["vaitsez"], fade_out=0.0)
         + fill(t_resume, t_outro, ["verclub", "vaitsez"])
         + fill(t_outro, TOTAL, ["jonas"], target=-26.0, fade_out=3.0))

edl = {
    "project": "C3 Research Demo - Edit",
    "source": MAIN,
    "resolution": [W, H],
    "fps": 30,
    "voice": {MAIN: str(AUD / "voice-main.wav")},
    "segments": segments,
    "images": images,
    "sfx": sfx,
    "music": music,
}
(HERE / "edit.edl.json").write_text(json.dumps(edl, indent=1), encoding="utf-8")
nk = sum(len(s.get("path", [])) for s in segments)
ff = [s for s in segments if s.get("speed")]
print(f"{len(segments)} segments, {TOTAL:.1f}s ({TOTAL/60:.2f} min), {len(images)} images, {len(sfx)} sfx, "
      f"{len(music)} music cues, {nk} camera keys, fast-forward {sum((s['out']-s['in'])/s['speed'] for s in ff):.1f}s "
      f"from {sum(s['out']-s['in'] for s in ff):.0f}s")
