"""Edit decisions for Asgard Agents Day 13 (OBS take 2026-10-06 10-44-11) as a ccut EDL.

One take: talking-head hook and intro 0-41, the Obsidian "Day 13 - What's New" canvas 41-287
(Coley pans and zooms it himself), the Agents Window at asgardagents.com 287-379 (he hides the
facecam at 319.5 because it covered the Pump.fun panel), Farcaster 379-393, Bluesky 393-410,
talking-head outro from 410.5.

Built on the C3 Research v3 rules (taste.md): no cursor tracker, one continuous camera, facecam is one
fixed size and zooms snap (punch-in) while it's in the shot, pauses are cut only across still screen,
transitions land on the real screen change, calm exit.
He says "day 11" in the intro; the canvas and the hook card say Day 13, so "day 11 of" is cut.
Graphics and cues are in SOURCE time and mapped onto the edited timeline.
Run: python gen_edl.py  ->  edit.edl.json
"""
import json
import math
import re
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
MAIN = "~/Projects/Youtube/videos/2026-10-06 10-44-11.mp4"
GFX = HERE / "graphics" / "out"
AUD = HERE / "audio"
W, H = 3840, 2160

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

SIL = silences(HERE / "sil35.txt")      # -35 dB: his breaths sit between -40 and -35 and split the -40 map

# (in, out, kind). Transition edges leave >= 0.35 s after the last word and >= 0.25 s before the first.
SPANS = [
    # v2 cold open (Codex audit #3: lead with the stakes). Same source as the canvas section, kind "cold"
    (90.36, 98.45, "cold"),     # "Right now they are still 23% down from their beginning balance. They're not profitable yet."
    (229.2, 235.68, "cold"),     # "October 10th is really their deadline. They want to make money... four days away."
    (5.55, 10.98, "talk"),      # hook: "Come check out how far the five AI agents have gotten in running their own business."
    (31.12, 35.6, "talk"),      # "Let's get on over to Obsidian and check out the canvas. Let's go." (v2: the agenda intro is cut)
    (44.25, 286.75, "screen"),   # Obsidian canvas -> "...check out the updates that they have made."
    (288.3, 410.5, "screen"),    # Agents Window, Farcaster, Bluesky -> "We're going to get back into full..."
    (410.5, 439.4, "talk"),      # OBS switches to the camera mid-"full screen": the transition sits on that frame
]
OUTRO = 405.6               # calm exit from "But that is the update for today."
MAX_GAP = 0.4
TAIL, HEAD = 0.14, 0.10
OUTRO_GAP, OUTRO_TAIL, OUTRO_HEAD = 0.6, 0.2, 0.14

# Semantic cuts (source seconds): restatements, stumbles, filler, doubled words.
# v2 (Codex audit #4): about 40 s more of repeated setup comes out of the canvas.
CUTS = [
    (51.60, 53.70),       # "Day 13 video." (restates the line before)
    (59.40, 61.76),       # "So they have launched seven total." (restates "seven coins total")
    (86.62, 90.38),       # "So now they're attempting to launch on three different platforms. Uh," (said at 67-76)
    (94.93, 95.72),       # "their, uh, beginning balance" -> "their beginning balance"
    (96.50, 97.15),       # "Uh," before "they're not profitable yet"
    (98.30, 107.90),      # v2: "There they are. You guys already know who they are. This is our third video..." (re-intro)
    (110.60, 112.62),     # doubled "now. Now," -> "a Telegram channel now. Every single thing"
    (116.80, 124.45),     # v2: "You can go watch it live, see their updates, P&Ls... any updates from them."
    (129.45, 134.45),     # v2: "So they do have those social medias as well. You can follow them there. Uh,"
    (136.50, 138.74),     # "So these guys have their email. They can" -> "their own email. You can email them"
    (145.02, 146.70),     # "other options, you know," -> "sign up for anything that requires an email"
    (161.50, 170.57),     # v2 (audit #2): "They have no announcement... until the new story is ready." (the card says confirmed on chain)
    (184.27, 188.36),     # "three launch pads. Yes, I just explained that. They're letting you know again."
    (190.75, 206.34),     # v2: "So they decided that their platform... wasn't high enough quality... So they did update that."
    (213.00, 215.34),     # "So they could have changed it to that. I'm not real sure."
    (216.72, 217.45),     # "Uh," before "X is still suspended"
    (231.50, 232.00),     # "Uh," before "they want to make money"
    (235.71, 241.62),     # v2: "Uh, so we're going to see what they decide on October 10th. Uh, it looks like the next coin,"
    (244.50, 255.00),     # v2: "I don't know what that's about... wait for the launch... to be honest."
    (259.60, 267.62),     # "Obviously, you still have the live website... We have made updates to that site."
    (274.35, 281.58),     # Telegram and email again + "All right," -> "token progress. We're going to head on over"
    (312.68, 313.62),     # "So that's what they're doing."
    (316.62, 325.25),     # "I guess you can't see it. Hold on, my face is in the way..." (13 hours said already)
    (363.34, 365.08),     # "You can see he is number one."
    (371.10, 373.00),     # "And the next token." (restated right after)
    (381.45, 382.52),     # "That is available."
]
# Splits that are not cuts (continuous source, no voice fade): tab switches mid-sentence.
FARCASTER_TAB, BLUESKY_TAB = 379.4, 393.4
SPLITS = [FARCASTER_TAB, BLUESKY_TAB]

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
        for s, e in SIL:
            outro = s >= OUTRO
            gap, tail, head = (OUTRO_GAP, OUTRO_TAIL, OUTRO_HEAD) if outro else (MAX_GAP, TAIL, HEAD)
            if e - s <= gap or s < a or e > b:
                continue
            x, y = s + tail, e - head
            if kind != "talk":
                x, y = still_cut(x, y)      # a scroll inside the pause plays out instead of jumping
                if y - x < 0.25:
                    continue
            if x > cur:
                out.append([cur, x, kind])
            cur = y
        out.append([cur, b, kind])
    res = []
    for a, b, kind in out:
        # v2: zoom edges are splits too (continuous source, no voice fade): each zoom is its own piece
        # with a fixed frame, because CapCut 9.2 ignores keyframe timing on video clips
        edges = SPLITS + ([e for w in ZOOMS for e in w[:2]] if kind == "screen" else [])
        cuts = sorted(c for c in set(edges) if a + 0.3 < c < b - 0.3)
        for x, y in zip([a] + cuts, cuts + [b]):
            res.append([x, y, kind])
    return [p for p in res if p[1] - p[0] > 0.05]

# ---- camera -------------------------------------------------------------------------
# Zoom windows (source in, out, scale, u, v): (u, v) is the centre of the element being talked about.
# Every window sits inside a still stretch of the canvas (he pans it himself between them).
# v2: no keyframes. CapCut 9.2 (updated 2026-10-06) holds a video clip at its LAST keyframe for the
# whole clip (proven with a test draft), so v1's snapped zooms never showed and ramps landed off target.
# Each window is now its own piece with a static frame: a clean punch-in.
ZOOMS = [
    (56.30, 59.40, 1.5, 0.45, 0.47),   # scoreboard: "7 coins"
    (69.70, 86.62, 1.5, 0.55, 0.42),   # "3 launchpads": PONS, Flap and Pump.fun
    (90.38, 93.40, 1.5, 0.60, 0.42),   # "0.0147 ETH ... down 23%"
    (107.90, 124.45, 1.5, 0.47, 0.44),  # "Their own Telegram channel"
    (124.45, 129.45, 1.5, 0.50, 0.60),  # "Farcaster and Bluesky"
    (134.45, 149.80, 1.5, 0.45, 0.68),  # "Their own email"
    (153.20, 161.50, 1.5, 0.56, 0.37),  # "Paused a launch halfway"
    (170.50, 181.00, 1.5, 0.55, 0.55),  # "Brand check on every post"
    (188.36, 213.00, 1.5, 0.62, 0.39),  # "Pro-quality logos" (through Codex and Higgsfield)
    (219.20, 224.80, 1.5, 0.64, 0.47),  # "X and Reddit suspended"
    (241.62, 244.50, 1.5, 0.56, 0.54),  # "$OHDEER: next coin, from a Florida news story"
    (268.00, 270.60, 1.5, 0.66, 0.56),  # "Watch live: asgardagents.com"
    (297.80, 306.50, 1.5, 0.40, 0.85),  # the new token charts: PONS, Flap, Pump.fun row
    (313.70, 316.62, 1.6, 0.25, 0.82),  # "LATEST COIN $NOODLE"
    (325.25, 335.80, 1.6, 0.90, 0.82),  # the Treasury (facecam hidden from 319.5)
    (336.10, 343.00, 1.6, 0.90, 0.15),  # Telegram, Farcaster, Bluesky buttons, top right
    (343.30, 353.90, 1.6, 0.45, 0.13),  # fees collected: 0 ETH, 0.0989 SOL
    (357.30, 363.34, 1.6, 0.90, 0.27),  # Valhalla: Thor is number one
    (365.08, 378.00, 1.6, 0.90, 0.45),  # fan polls: vote the MVP and the next coin's vibe
    (386.00, 393.40, 1.6, 0.47, 0.55),  # Farcaster: their Noodle post (the profile plays full-frame first)
    (398.80, 401.30, 1.5, 0.50, 0.30),  # Bluesky: "marked this account as automated"
]

PS = pieces()
dur = lambda p: p[1] - p[0]

def to_out(t, cold=False):
    """Source second -> edited-timeline second (snaps into the nearest kept piece).
    The cold open reuses source from the canvas: graphics map to the main section unless cold=True."""
    off = 0.0
    for p in PS:
        a, b, kind = p
        if (kind == "cold") == cold and a - 0.4 <= t <= b + 0.4:
            return off + (min(max(t, a), b) - a)
        off += dur(p)
    raise SystemExit(f"source {t} is cut out")

def cut_at(t, cold=False):
    return round(to_out(t, cold), 3)

TOTAL = sum(dur(p) for p in PS)

# ---- facecam --------------------------------------------------------------------
CAM = {"rect": [2920, 1428, 3714, 2034], "clip": str(HERE / "facecam-crop.mp4")}
CX0, CY0, CX1, CY1 = 2920 / W, 1428 / H, 3714 / W, 2034 / H
CAM_ON = [r for r in json.loads((HERE / "cam_on.json").read_text())]
cam_visible = lambda a, b: any(x <= a + 0.3 and b - 0.3 <= y for x, y in CAM_ON)

def window_at(t):
    for w in ZOOMS:
        if w[0] <= t < w[1]:
            return w
    return None

def allowed(s, u, v):
    """Keep the frame inside the picture and the zoomed facecam copy off-frame (fixed-size overlay)."""
    m = 0.5 / s
    clamp = lambda a: min(max(a, m), 1 - m)
    u, v = clamp(u), clamp(v)
    if s < 1.0005:
        return u, v
    off_r = CX0 - 1 / s + m
    off_b = CY0 - 1 / s + m
    if u <= off_r + 1e-9 or v <= off_b + 1e-9:
        return u, v
    cands = [(min(u, off_r), v), (u, min(v, off_b))]
    cands = [(clamp(a), clamp(b)) for a, b in cands]
    # at 1.5x the picture edge stops the view short of hiding the copy below it: only moving left works
    cands = [c for c in cands if c[0] <= off_r + 1e-9 or c[1] <= off_b + 1e-9]
    return min(cands, key=lambda c: (c[0] - u) ** 2 + (c[1] - v) ** 2)

def clamp_only(s, u, v):
    m = 0.5 / s
    return min(max(u, m), 1 - m), min(max(v, m), 1 - m)

def check_cam(s, u, v):
    """Fixed facecam: the camera's zoomed copy of it must be off-frame."""
    l, t = u - 0.5 / s, v - 0.5 / s
    zx0, zy0 = (CX0 - l) * s, (CY0 - t) * s
    assert zx0 >= 1 - 1e-3 or zy0 >= 1 - 1e-3 or s < 1.0005, (s, u, v)

def to_frame(s, u, v):
    return round(s, 4), round((0.5 - u) * 2 * s, 4), round((v - 0.5) * 2 * s, 4)

def frame_of(p):
    """Static framing of a screen piece: its zoom window (aimed clear of the recorded facecam) or none."""
    a, b, kind = p
    w = window_at((a + b) / 2) if kind == "screen" else None
    if not w:
        return None
    s, u, v = w[2], w[3], w[4]
    cam = cam_visible(a, b)
    u, v = (allowed if cam else clamp_only)(s, u, v)
    if cam:
        check_cam(s, u, v)
    return to_frame(s, u, v)

FRAMES = [frame_of(p) for p in PS]

# Transitions go on the segment that ENDS at this source second.
TRANSITIONS = {
    235.68: ("White_Flash", 0.35),      # out of the cold open into the talking-head hook
    35.6: ("Zoom_Transition", 0.6),     # talking head -> the Obsidian canvas
    286.75: ("Swipe_Left", 0.45),       # Obsidian -> the Agents Window
    FARCASTER_TAB: ("Swipe_Left", 0.4), # tab switch to Farcaster, mid-sentence
    BLUESKY_TAB: ("Swipe_Left", 0.4),   # tab switch to Bluesky, mid-sentence
    410.5: ("Zoom_Transition", 0.6),    # OBS's own switch to the camera, on continuous speech ("full screen")
}
# A speech cut on a screen that moved still jumps: soften it with a short Dissolve (free in CapCut).
# v2 (Codex audit #5): only where the framing is the same on both sides. A change of framing at the cut
# reads as a deliberate camera cut, and a dissolve there doubled dense canvas text.
DISSOLVE, JUMP = ("叠化", 0.3), 2.5
for i in range(len(PS) - 1):
    (a0, b0, k0), (a1, b1, k1) = PS[i], PS[i + 1]
    if k0 == k1 == "screen" and abs(b0 - a1) > 1e-3 and not any(abs(t - b0) < 0.01 for t in TRANSITIONS) \
            and FRAMES[i] == FRAMES[i + 1] \
            and b0 - a0 > 0.45 and b1 - a1 > 0.45 and jump(b0 - 0.05, a1) > JUMP:
        TRANSITIONS[b0] = DISSOLVE

segments, talk_i = [], 0
for i, p in enumerate(PS):
    a, b, kind = p
    seg = {"in": round(a, 3), "out": round(b, 3)}
    if kind == "talk":
        if talk_i % 2:
            seg["frame"] = {"scale": 1.12}      # alternate framing hides the jump cut
        talk_i += 1
    elif FRAMES[i]:
        s_, x_, y_ = FRAMES[i]
        seg["frame"] = {"scale": s_, "x": x_, "y": y_}
        if cam_visible(a, b):
            seg["cam_overlay"] = {**CAM, "k0": 1.0}   # fixed size: the recorded facecam stays whole over zooms
    for tt, (name, d) in TRANSITIONS.items():
        # a transition keyed to a main-section cut must not leak onto the cold open's copy of that second
        if abs(tt - b) < 0.01 and (kind != "cold" or name != DISSOLVE[0]):
            seg["transition"] = {"name": name, "duration": d}
    segments.append(seg)

# ---- graphics -------------------------------------------------------------------------
images, sfx = [], []
MAN = json.loads((GFX / "manifest.json").read_text())
TOP_R = (3260, 330)      # logo pop-ups
TOP_L = (720, 250)       # section chips
STAT = (1920, 360)       # number callouts
LOW = (1920, 1830)       # talking head: on the chest, never over the face

def img(name, t, d, x, y, scale=1.0, sound="pop", at=None, cold=False):
    at = cut_at(t, cold) if at is None else at
    half = MAN[name]["w"] * scale / 2
    if (x, y) == TOP_L:
        x = round(80 + half)
    elif (x, y) == TOP_R:
        x = round(3760 - half)
    images.append({"path": str(GFX / f"{name}.png"), "start": at, "duration": d, "x": x, "y": y, "scale": scale})
    if sound:
        sfx.append({"path": str(AUD / ("pop.wav" if sound == "pop" else "sfx-impact.wav")),
                    "start": at, "volume": 0.24 if sound == "pop" else 0.25})   # impact: 0.5 clipped the mix (0 dBTP)

# v2 cold open (Codex audit #3): the stakes first, full-frame canvas with the number on screen
img("stat-down", 91.42, 3.6, *STAT, cold=True)                       # "still 23% down"
img("stat-oct10", 229.48, round(cut_at(235.3, True) - cut_at(229.48, True), 3), *STAT, cold=True)   # "October 10th... four days away"
# hook (talking head): the premise above his head, the five agents across his chest
img("hook-title", 7.52, round(cut_at(10.9) - cut_at(7.52), 3), 1920, 250, scale=0.95)   # "the five AI agents"
for k, (n, t) in enumerate([("odin", 8.22), ("thor", 8.5), ("loki", 8.8), ("mimir", 9.1), ("heimdall", 9.4)]):
    img(f"agent-{n}", t, round(cut_at(10.9) - cut_at(t), 3), 1080 + 420 * k, 1800, scale=0.85, sound="pop" if k == 0 else None)
img("logo-obsidian", 32.76, 2.4, *TOP_R)                             # "over to Obsidian"
# 01 the scoreboard
img("chip-score", 54.66, 2.8, *TOP_L)                                # "Where we are as of now"
img("stat-coins", 57.62, 3.0, *STAT)                                 # "seven coins total"
img("pads", 78.92, 4.2, 3160, 470, scale=0.9)                        # "Pons, Flap and Pump.fun"
img("stat-down", 92.62, 3.4, *STAT)                                  # "still 23% down"
# 02 follow along
img("chip-follow", 108.0, 2.8, *TOP_L)
img("logo-telegram", 109.22, 3.4, *TOP_R)                            # "a Telegram channel"
img("logo-farcaster", 127.28, 3.2, *TOP_R)                           # "a Farcaster..."
img("logo-bluesky", 128.32, 2.6, 3240, 700)                          # "...and Bluesky account", stacked under it
img("card-email", 135.78, 3.4, *TOP_R)                               # "their own email"
# 03 they caught their own mistakes
img("chip-mistakes", 152.74, 2.8, *TOP_L)                            # "They did pause a launch halfway"
img("stat-final", 158.3, 3.0, *STAT)                                 # the canvas: "No announcement until the launch is confirmed on chain"
img("stat-brand", 171.06, 3.2, *STAT)                                # "Brand check on every post" (canvas: the old name gets blocked)
# 04 behind the scenes
img("chip-behind", 183.1, 1.6, *TOP_L)
img("logos-new", 189.7, round(cut_at(208.4) - cut_at(189.7), 3), *STAT)   # "their logo quality", held until Codex
img("logo-codex", 208.52, 2.6, *TOP_R)                               # "Codex Image Generation"
img("logo-higgsfield", 211.34, 2.6, 3240, 700)                          # "Higgsfield API access"
img("logo-x", 218.36, 1.6, *TOP_R)                                   # "X is still suspended"
img("logo-reddit", 220.34, 2.8, *TOP_R)                              # "a Reddit account"
img("stat-banned", 223.24, 3.6, *STAT, sound="hit")                  # punchline: "Reddit booted them"
# 05 what's next
img("chip-next", 229.0, 2.6, *TOP_L)                                 # "October 10th is really their deadline"
img("coin-ohdeer", 242.6, 3.6, *TOP_R)                              # "a story out of Florida"
img("site-card", 268.65, 3.4, *TOP_R)                                # "asgardagents.com"
# 06 the Agents Window (lands after the swipe)
img("chip-window", 290.3, 2.8, *TOP_L)
img("stat-charts", 297.1, 3.0, *STAT)                                # "they have added charts"
img("vs-chains", 307.64, 3.6, 1920, 420, scale=0.9)                  # "a Sol token, the other two are ETH on Robinhood"
img("coin-noodle", 314.72, 3.2, *TOP_R)                          # "newest token is Noodle" (the zoom sits bottom-left)
img("stat-sol", 347.72, 3.4, 1920, 1750)                             # "Sol almost 0.1" (the zoom sits on the top bar)
img("card-thor", 362.36, 3.0, 720, 1500)                             # "Thor is number one" (zoom is top right)
img("stat-vote", 365.64, 3.2, 2150, 1750)                            # "vote for your favorite agent"
# 07 their own socials
img("chip-social", 380.6, 2.6, *TOP_L)                               # after the swipe to Farcaster
img("logo-farcaster", 383.8, 2.8, *TOP_R)                            # "go follow the agents"
img("stat-own", 392.38, 3.0, 1920, 1800)                             # "doing it all on their own"
img("stat-bot", 399.18, 3.0, 1920, 1800)                             # "they are bot accounts"
# outro: one card at a time, nothing over the face
img("stat-series", 416.68, 3.6, *LOW, scale=0.9)                     # "start a new series"
img("stat-recap", 420.76, 3.6, *LOW, scale=0.9)                      # "This one is a meme coin business": where Day 13 leaves them
img("comment-card", 425.9, 5.0, *LOW, scale=0.85)                    # "ask them what business they would like to start"
img("cta-subscribe", 433.44, 2.6, 1920, 1760)                        # "go ahead and subscribe"
FADE = 1.2
images.append({"path": str(GFX / "black-4k.png"), "start": round(TOTAL - FADE, 3), "duration": FADE, "x": 1920, "y": 1080, "pop": "fade"})
images.append({"path": str(GFX / "black-4k.png"), "start": round(TOTAL - 0.2, 3), "duration": 0.2, "x": 1920, "y": 1080, "pop": False})

for t, (name, d) in TRANSITIONS.items():
    if (name, d) != DISSOLVE:      # a dissolve smooths a cut; it isn't a scene change, so no whoosh
        sfx.append({"path": str(AUD / "sfx-whoosh.wav"), "peak_at": cut_at(t, cold=(t == 235.68)), "volume": 0.32 if d >= 0.5 else 0.22})

# ---- music: a new bed per section, cut dead on "Reddit booted them" -------------------
BEDS = json.loads((AUD / "beds.json").read_text()) if (AUD / "beds.json").exists() else {}
def bed(name, at, end, target=-30.0, offset=None):
    b = BEDS[name]
    offset = b.get("offset", 0.0) if offset is None else offset   # skip a bed's quiet build-up
    return {"path": str(AUD / b["file"]), "at": round(at, 3), "start_offset": offset,
            "duration": round(min(end - at, b["length"] - offset), 3), "volume": round(10 ** ((target - b["lufs"]) / 20), 3)}

def window_cues(cues):
    """Drop a final sliver (< 3 s) of a bed restarting: the next section's bed starts there instead."""
    if len(cues) > 1 and cues[-1]["duration"] < 3.0:
        cues.pop()
        cues[-1]["fade_out"] = 1.5
    return cues

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

t_screen = cut_at(44.25)
t_dead = cut_at(223.24)       # "Reddit booted them": music stops dead, impact hit
t_resume = cut_at(225.9)      # "So no X or Reddit." (the music comes back on the button line)
t_window = cut_at(288.3)
t_outro = cut_at(OUTRO)
music = []
if BEDS:
    music = (fill(0.0, t_screen, ["intro"], target=-29.0, fade_out=0.6)
             + fill(t_screen, t_dead, ["canvas"], fade_out=0.0)
             + fill(t_resume, t_window, ["canvas2"], fade_out=0.5)
             + window_cues(fill(t_window, t_outro, ["window"])))
    music += fill(music[-1]["at"] + music[-1]["duration"] - 1.0, TOTAL, ["outro"], target=-26.0, fade_out=3.0)

edl = {
    "project": "Asgard Agents Day 13 - Edit",
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
print(f"{len(segments)} segments, {TOTAL:.1f}s ({TOTAL/60:.2f} min), {len(images)} images, {len(sfx)} sfx, "
      f"{len(music)} music cues, {nk} camera keys, {sum(1 for s in segments if 'transition' in s)} transitions")
