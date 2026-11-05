"""Edit decisions for "Asgard Agents Day 6" as a ccut EDL (v2, after Coley's review).

One OBS take: talking head 0-56, Obsidian canvas 57-216, Agents Window 216-440,
Paperclip 440-457, X (suspended) 457-486, Agents Window to the end.

v2 (Coley, 2026-09-29): cut the stutters, no speech clipped at transitions, zooms
follow the cursor, fix the 6:10 glitch (tab switch + a cut 0.46 s later), smooth the exit.
The screen sections now run on ONE continuous camera (keyframe `path` per piece) instead
of per-piece zooms and pushes: the per-piece push restarted at every join, which read
as a jump at each cut. Inside a zoom window the camera follows the tracked cursor
(cursor.json from track_cursor.py) with a dead zone; outside, a slow push.
Graphics and cues are in SOURCE time and mapped onto the edited timeline.
Run: python gen_edl.py  ->  edit.edl.json
"""
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).parent
MAIN = "~/Projects/Youtube/videos/2026-09-29 12-25-48.mp4"
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

SIL = silences(HERE / "silences-main-fine.txt")

# (in, out, kind). Transition edges leave >= 0.35 s after the last word and >= 0.25 s
# before the first (v1 cut "doing." and "Come with me." within 0.06 s: the flash and
# whoosh ate the word).
SPANS = [
    (12.45, 20.15, "talk"),     # hook: "This is day six ... Let's see what they're doing."
    (48.3, 52.35, "talk"),      # take 2: "We're going to jump into Obsidian... Come with me."
    (58.75, 213.7, "screen"),   # Obsidian canvas: "Okay, now that we're in Obsidian..."
    (218.15, 434.85, "screen"),  # Agents Window
    (440.05, 561.3, "screen"),  # Paperclip, X, Agents Window, outro (drops "Up next."); ends in the silence after "update."
]
OUTRO = 509.5               # calmer pacing from "So right now, that's day six update"
MAX_GAP = 0.4               # pauses longer than this collapse (taste.md)
TAIL, HEAD = 0.14, 0.10     # speech kept either side of a collapsed pause (word tails decay, keep more after)
OUTRO_GAP, OUTRO_TAIL, OUTRO_HEAD = 0.6, 0.2, 0.14
NOCOLLAPSE = [(457.35, 457.84), (485.97, 486.86)]   # the pauses right after the two tab switches: the swipe needs the room

# Semantic cuts (source seconds): restatements, stumbles, filler.
CUTS = [
    (122.47, 122.93),   # "their, you know, Heimdall" -> "their Heimdall"
    (130.54, 132.2),    # "So they did find that." (restates the line before)
    (162.24, 162.40),   # doubled "the" in "So the the yesterday's"
    (191.95, 192.36),   # "um, because it's it's really" -> "because it's really"
    (220.45, 221.32),   # "This is agent asgardagents.com" -> "This is asgardagents.com"
    (231.30, 231.88),   # "So this is there, the window" -> "So this is the window"
    (234.2, 238.52),    # "You can, we'll start at the top left. So you're looking at the agents window."
    (247.7, 250.9),     # "and it's, you know," before "it's time worked"
    (261.7, 262.65),    # "and you can," after "23"
    (271.68, 272.36),   # stutter "great, great graph" -> "great graph"
    (280.9, 282.2),     # "if, you know, agents" -> "if agents"
    (319.15, 320.54),   # "We're not doing anything." (restates "nobody working")
    (365.42, 368.9),    # "And so far he is. There's rankings."
    (413.1, 414.9),     # "you know, the newest three tokens" (restates "the latest three tokens")
    (425.36, 428.78),   # doubled "the. ... The company"
    (477.0, 477.92),    # "you know,"
    (503.18, 503.33),   # stutter "for that that agents" -> "for that agents"
    (514.12, 515.9),    # "Nothing new." (restates "Nothing else has taken place")
    (526.72, 530.62),   # "I think they have." (false start)
    (536.45, 538.47),   # "So this is day six." (restates)
]
# Splits that are not cuts (continuous source, so ccut puts no voice fade there): the tab switches.
SPLITS = [457.14, 485.75]

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
            if e - s <= gap or s < a or e > b or any(abs(s - ns) < 0.05 for ns, _ in NOCOLLAPSE):
                continue
            if s + tail > cur:
                out.append([cur, s + tail, kind])
            cur = e - head
        out.append([cur, b, kind])
    res = []
    for a, b, kind in out:
        cuts = [c for c in SPLITS if a + 0.3 < c < b - 0.3]
        for x, y in zip([a] + cuts, cuts + [b]):
            res.append([x, y, kind])
    return [p for p in res if p[1] - p[0] > 0.05]

PS = pieces()

def to_out(t):
    """Source second -> edited-timeline second (snaps into the nearest kept piece)."""
    off = 0.0
    for a, b, _ in PS:
        if a - 0.4 <= t <= b + 0.4:
            return off + min(max(t, a), b) - a
        off += b - a
    raise SystemExit(f"source {t} is cut out")

def cut_at(t):
    return round(to_out(t), 3)

TOTAL = sum(b - a for a, b, _ in PS)

# ---- camera -----------------------------------------------------------------
CAM = {"rect": [2920, 1428, 3714, 2034], "clip": str(HERE / "facecam-crop.mp4")}
CX0, CY0, CX1, CY1 = 2920 / W, 1428 / H, 3714 / W, 2034 / H

# Zoom windows (source in, out, scale, u, v): (u, v) is where the camera starts (the element
# being talked about); from there it follows the cursor.
ZOOMS = [
    (74.2, 106.3, 1.6, 0.34, 0.41),     # canvas col 1: new website, vote, their own video
    (106.3, 117.25, 1.6, 0.51, 0.35),   # col 2: dodged a scam name
    (117.33, 139.6, 1.6, 0.51, 0.42),   # col 2 after the pan: skipped launch, reviewer
    (140.4, 155.5, 1.6, 0.73, 0.33),    # col 3: X account suspended
    (157.43, 173.9, 1.6, 0.40, 0.57),   # the numbers
    (174.6, 203.3, 1.4, 0.55, 0.50),    # what's next: marketing beyond X
    (242.6, 298.2, 1.5, 0.30, 0.52),    # Odin's card: minutes, resting, graph, streak, 3rd in the hall
    (299.8, 309.3, 1.6, 0.30, 0.90),    # the ticker along the bottom
    (309.9, 344.3, 1.5, 0.42, 0.30),    # the top stat bar
    (345.2, 381.4, 1.6, 0.90, 0.30),    # right column: X link, watching, rankings, polls
    (382.8, 399.3, 1.4, 0.88, 0.60),    # the Chronicle (the facecam limits how far down it can go)
    (440.3, 457.1, 1.6, 0.80, 0.30),    # Paperclip: FEN-278, "Marketing without X"
    (457.7, 468.2, 1.6, 0.43, 0.33),    # X: "Your account is suspended"
]
TAU_S, TAU_P = 0.22, 0.30        # camera smoothing (s): scale ramps ~0.6 s, pans ease in ~0.9 s
DEAD = 0.30                      # cursor may drift within +-DEAD/s of the camera centre before it follows
PUSH, PUSH_MAX = 0.0035, 0.04    # slow push outside zooms: +0.35%/s, capped at 4%

cur = json.loads((HERE / "cursor.json").read_text())
CUR_T0, CUR_FPS = cur["t0"], cur["fps"]
CUR = []                         # forward-filled cursor (u, v) or None before the first fix
last = None
for t, x, y, _ in cur["pts"]:
    if x is not None:
        last = (x / W, y / H)
    CUR.append(last)
MOVED = []                       # seconds since the cursor last moved, per sample
since, prev = 99.0, None
for p in CUR:
    since = 0.0 if (p and prev and (abs(p[0] - prev[0]) + abs(p[1] - prev[1])) > 0.002) else since + 1 / CUR_FPS
    MOVED.append(since)
    prev = p

def cursor_at(t):
    i = round((t - CUR_T0) * CUR_FPS)
    return (CUR[i], MOVED[i]) if 0 <= i < len(CUR) else (None, 99.0)

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
    off_r = CX0 - 1 / s + m            # u at or below this: copy falls off the right edge
    off_b = CY0 - 1 / s + m            # v at or below this: copy falls off the bottom
    cov_u, cov_v = CX0 * (1 - 1 / s) + m, CY0 * (1 - 1 / s) + m
    if u <= off_r + 1e-9 or v <= off_b + 1e-9 or (u <= cov_u + 1e-9 and v <= cov_v + 1e-9):
        return u, v
    cands = [(min(u, off_r), v), (u, min(v, off_b)), (min(u, cov_u), min(v, cov_v))]
    cands = [(clamp(a), clamp(b)) for a, b in cands]
    return min(cands, key=lambda c: (c[0] - u) ** 2 + (c[1] - v) ** 2)

def cam_grow(s, u, v):
    l, t = u - 0.5 / s, v - 0.5 / s
    zx0, zy0, zx1, zy1 = (CX0 - l) * s, (CY0 - t) * s, (CX1 - l) * s, (CY1 - t) * s
    if zx0 >= 1 or zy0 >= 1:
        return 1.0
    g = max((min(zx1, 1) - CX0) / (CX1 - CX0), (min(zy1, 1) - CY0) / (CY1 - CY0), 1.0)
    return round(g + 0.015, 4)

def to_frame(s, u, v):
    return round(s, 4), round((0.5 - u) * 2 * s, 4), round((v - 0.5) * 2 * s, 4)

def camera():
    """Simulate the camera over output time. Returns per piece index: (path keys, cam keys, ring samples)."""
    res = {}
    state = None              # smoothed (s, u, v)
    follow = None             # dead-zone centre inside the current window
    push_from = 0.0           # output time the current slow push started
    off = 0.0
    prev_kind, prev_win = None, None
    for i, (a, b, kind) in enumerate(PS):
        d = b - a
        if kind != "screen":
            off += d; prev_kind = kind; state = None
            continue
        if prev_kind != "screen":
            push_from = off   # a new screen section starts flat
        n = max(2, math.ceil(d * CUR_FPS) + 1)
        keys, cams, ring = [], [], []
        for k in range(n):
            ts = a + d * k / (n - 1)
            to = off + d * k / (n - 1)
            w = window_at(ts)
            c, moved = cursor_at(ts)
            if w is not prev_win:
                if w:
                    follow = list(w[3:5])
                else:
                    push_from = to
                prev_win = w
            if w:
                s_t = w[2]
                if c:
                    lim = DEAD / s_t
                    for j in (0, 1):
                        if c[j] > follow[j] + lim:
                            follow[j] = c[j] - lim
                        elif c[j] < follow[j] - lim:
                            follow[j] = c[j] + lim
                follow[0], follow[1] = allowed(s_t, *follow)
                u_t, v_t = follow
            else:
                s_t = 1 + min(PUSH * (to - push_from), PUSH_MAX)
                u_t, v_t = 0.5, 0.5
            if state is None:
                state = [s_t, u_t, v_t]
            else:
                dt = d / (n - 1) if k else 0.0
                if dt:
                    fs, fp = 1 - math.exp(-dt / TAU_S), 1 - math.exp(-dt / TAU_P)
                    state[0] += (s_t - state[0]) * fs
                    state[1] += (u_t - state[1]) * fp
                    state[2] += (v_t - state[2]) * fp
            s_, u_, v_ = state[0], *allowed(state[0], state[1], state[2])
            state[1], state[2] = u_, v_
            keys.append((round(d * k / (n - 1), 3), *to_frame(s_, u_, v_)))
            cams.append((round(k / (n - 1), 4), cam_grow(s_, u_, v_)))
            if c and moved < 2.5:
                # cursor on the output canvas after the camera transform
                l, t = u_ - 0.5 / s_, v_ - 0.5 / s_
                X, Y = (c[0] - l) * s_ * W, (c[1] - t) * s_ * H
                g = cams[-1][1]
                over_cam = X > 2920 - 60 and Y > 1428 - 60 and X < 2920 + (3714 - 2920) * g + 60
                if 40 < X < W - 40 and 40 < Y < 2060 and not over_cam:
                    ring.append((round(to, 3), round(X), round(Y)))
                    continue
            ring.append((round(to, 3), None, None))
        res[i] = (thin(keys), thin_cam(cams), ring)
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
    20.15: ("White_Flash", 0.35),       # hook -> intro
    52.35: ("Zoom_Transition", 0.6),    # talking head -> screen
    213.7: ("Swipe_Left", 0.6),         # Obsidian -> Agents Window
    434.85: ("Swipe_Left", 0.6),        # Agents Window -> Paperclip
    457.14: ("Swipe_Left", 0.4),        # Paperclip -> X (tab switch, mid-sentence: short)
    485.75: ("Swipe_Left", 0.4),        # X -> Agents Window (the 6:10 glitch in v1)
}

segments, talk_i = [], 0
for i, (a, b, kind) in enumerate(PS):
    seg = {"in": round(a, 3), "out": round(b, 3)}
    if kind == "talk":
        if talk_i % 2:
            seg["frame"] = {"scale": 1.12}      # alternate framing hides the jump cut
        talk_i += 1
    else:
        keys, cams, _ = CAMERA[i]
        seg["path"] = keys
        # the recorded facecam stays whole: its own crop sits over every screen piece,
        # growing (anchored top-left) just enough to hide the camera's zoomed copy
        seg["cam_overlay"] = {**CAM, "keys": cams}
    for tt, (name, dur) in TRANSITIONS.items():
        if abs(tt - b) < 0.01:
            seg["transition"] = {"name": name, "duration": dur}
    segments.append(seg)

# ---- graphics -------------------------------------------------------------
images, sfx = [], []
MAN = json.loads((GFX / "manifest.json").read_text())
TOP_R = (3260, 330)      # logo pop-ups
TOP_L = (720, 250)       # section chips
STAT = (1920, 360)       # number callouts

def img(name, t, dur, x, y, scale=1.0, sound="pop"):
    at = cut_at(t)
    half = MAN[name]["w"] * scale / 2
    if (x, y) == TOP_L:
        x = round(80 + half)           # chips hang off the left margin, whatever their width
    elif (x, y) == TOP_R:
        x = round(3760 - half)         # logo cards hang off the right margin
    images.append({"path": str(GFX / f"{name}.png"), "start": at, "duration": dur, "x": x, "y": y, "scale": scale})
    if sound:
        sfx.append({"path": str(AUD / ("pop.mp3" if sound == "pop" else "sfx-impact.mp3")),
                    "start": at, "volume": 0.3 if sound == "pop" else 0.5})

# hook (talking head: face is centre, so the row sits low on the chest and the title above the head)
for i, n in enumerate(["odin", "thor", "loki", "mimir", "heimdall"]):
    img(f"agent-{n}", 15.1 + i * 0.12, 2.6 - i * 0.12, 1920 + (i - 2) * 620, 1760, scale=1.15, sound="pop" if i == 0 else None)
img("hook-title", 17.02, 3.3, 1920, 250, scale=0.95)          # on "meme coin company"
img("logo-obsidian", 49.4, 2.4, 3150, 420)                     # "jump into Obsidian"
# Obsidian canvas
img("chip-new", 62.8, 3.4, *TOP_L)                              # "I gave them instructions..."
img("site-card", 75.4, 3.4, *TOP_R)                             # "We did build a window into the agent's workflow"
img("stat-vote", 87.16, 3.4, *STAT)                             # "you can vote"
img("logo-remotion", 101.9, 3.0, *TOP_R)                        # "their own Remotion video"
img("stat-rug", 111.4, 3.4, *STAT)                              # "already been rugged"
img("card-heimdall", 123.0, 3.4, *TOP_R)                        # "Heimdall was doing his research"
img("stat-skipped", 133.5, 3.4, *STAT)                          # "They skipped that launch"
img("chip-behind", 140.8, 2.4, *TOP_L)
img("stat-suspended", 144.0, 3.8, *STAT, sound="hit")           # punchline: "did get suspended"
img("stat-appeal", 151.1, 3.4, *STAT)                           # "We filed an appeal"
img("chip-numbers", 157.9, 2.4, *TOP_L)
img("stat-coins", 161.3, 3.6, *STAT)                            # "still on number three"
img("stat-profit", 170.2, 3.2, *STAT)                           # "not made any profits"
img("chip-next", 175.3, 3.2, *TOP_L)
img("stat-human", 185.6, 3.6, *STAT)                            # "They may need my assistance"
# Agents Window
img("chip-window", 219.3, 3.2, *TOP_L)
img("site-card", 221.4, 3.4, *TOP_R)                            # "asgardagents.com"
img("stat-odin", 261.2, 3.2, *STAT)                             # "Odin's worked today, 23"
img("stat-hall", 293.2, 3.2, *STAT)                             # "Odin is third in the hall"
img("stat-visitors", 342.4, 2.8, *STAT)                         # "We've got 65"
img("x-suspended", 346.0, 3.6, *TOP_L)                          # "the Asgard X account... suspended"
img("card-loki", 358.2, 3.4, *TOP_L)                            # "Loki is number one"
img("chip-chronicle", 383.0, 3.4, *TOP_L)
img("chip-treasury", 399.95, 1.9, *TOP_L)
img("stat-net", 402.3, 3.4, *STAT)                              # "what they have made, what they have spent"
img("stat-pons", 415.0, 3.6, *STAT)                             # "view it on Pons"
img("logo-skald", 430.8, 3.4, *TOP_R)                           # "Skald Studio"
# Paperclip, X
img("chip-paperclip", 440.95, 3.2, *TOP_L)
img("logo-paperclip", 441.2, 3.0, 3260, 1150)                   # below the zoomed Done column
img("stat-tasks", 445.6, 3.4, *STAT)                            # "up to FEN 278"
img("chip-plan", 460.8, 3.4, *TOP_L)                            # "the biggest thing we're working on"
# PROGRESS_STEPS: the plan, current step lit as he reaches it (bottom-left, clear of the facecam)
STEP_AT = [490.6, 495.6, 500.2, 509.7]
for k in range(3):
    a, b = cut_at(STEP_AT[k]), cut_at(STEP_AT[k + 1])
    images.append({"path": str(GFX / f"plan-{k + 1}.png"), "start": a, "duration": round(b - a, 3),
                   "x": 1100, "y": 1880, "scale": 0.9, "pop": "in" if k == 0 else ("out" if k == 2 else False)})
sfx.append({"path": str(AUD / "pop.mp3"), "start": cut_at(STEP_AT[0]), "volume": 0.3})
# outro: one card at a time, no overlapping pops
FADE = 1.2
img("site-bookmark", 519.3, 4.0, 1920, 1300)                    # "bookmark it"
img("cta-subscribe", 550.66, 2.6, 1920, 1620)                   # "subscribe"
img("comment-card", 553.35, round(TOTAL - cut_at(553.35) - 0.2, 3), 1920, 820)  # "who you think is your favorite agent", held into the fade
images.append({"path": str(GFX / "black-4k.png"), "start": round(TOTAL - FADE, 3), "duration": FADE, "x": 1920, "y": 1080, "pop": "fade"})

# cursor highlight ring: shown while the cursor is moving (and 2.5 s after), never over the facecam
runs, curr = [], []
for i in sorted(CAMERA):
    for t, X, Y in CAMERA[i][2]:
        if X is None:
            if curr:
                runs.append(curr); curr = []
        else:
            if curr and t - curr[-1][0] > 0.4:     # a cut between samples: start a new run
                runs.append(curr); curr = []
            curr.append((t, X, Y))
    if curr:
        runs.append(curr); curr = []
merged = []
for r in runs:                                   # a ring blinking off for a moment is noise: bridge gaps under 2 s
    if merged and r[0][0] - merged[-1][-1][0] < 2.0:
        merged[-1].extend(r)
    else:
        merged.append(list(r))
rings = 0
for r in merged:
    t0, t1 = r[0][0], r[-1][0]
    if t1 - t0 < 1.5 or t0 > TOTAL - FADE - 1:
        continue
    path, lastp = [], None
    for t, X, Y in r:
        if lastp is None or abs(X - lastp[1]) + abs(Y - lastp[2]) > 6:
            path.append((round(t - t0, 3), X, Y)); lastp = (t, X, Y)
    if path[-1][0] < t1 - t0:
        path.append((round(t1 - t0, 3), r[-1][1], r[-1][2]))
    images.append({"path": str(GFX / "cursor-ring.png"), "start": t0, "duration": round(t1 - t0, 3),
                   "x": r[0][1], "y": r[0][2], "keys": path})
    rings += 1

for t in TRANSITIONS:
    sfx.append({"path": str(AUD / "sfx-whoosh.mp3"), "peak_at": cut_at(t), "volume": 0.38 if TRANSITIONS[t][1] >= 0.5 else 0.28})

# ---- music: a new bed per section, cut dead on "suspended" -------------------
BEDS = {"jonas": (AUD / "music-jonas.mp3", -8.9, 136.9), "verclub": (AUD / "music-verclub.mp3", -7.6, 130.3),
        "vaitsez": (AUD / "music-vaitsez.mp3", -8.2, 174.4)}
def bed(name, at, end, target=-30.0, offset=0.0):
    path, lufs, length = BEDS[name]
    return {"path": str(path), "at": round(at, 3), "start_offset": offset,
            "duration": round(min(end - at, length - offset), 3), "volume": round(10 ** ((target - lufs) / 20), 3)}

def fill(start, end, names, target=-30.0, fade_out=1.2):
    cues, t, i = [], start, 0
    while end - t > 0.5:
        c = bed(names[i % len(names)], t, end, target)
        c["fade_in"], c["fade_out"] = 1.0, fade_out
        cues.append(c)
        t += c["duration"]
        i += 1
    cues[-1]["fade_out"] = fade_out
    return cues

t_screen = cut_at(58.75)
t_dead = cut_at(144.0)       # "...did get suspended." music stops dead, impact hit
t_resume = cut_at(149.3)     # "We have since fixed that."
t_window = cut_at(218.15)
t_paper = cut_at(440.05)
t_outro = cut_at(509.7)      # "So right now, that's day six update"
music = (fill(0.0, t_screen, ["jonas"], target=-28.0, fade_out=0.6)
         + fill(t_screen, t_dead, ["verclub"], fade_out=0.0)
         + fill(t_resume, t_window, ["vaitsez"])
         + fill(t_window, t_paper, ["verclub", "vaitsez"])
         + fill(t_paper, t_outro, ["vaitsez"])
         + fill(t_outro, TOTAL, ["jonas"], target=-26.0, fade_out=3.0))

edl = {
    "project": "Asgard Agents Day 6 - Edit",
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
print(f"{len(segments)} segments, {TOTAL:.1f}s ({TOTAL/60:.2f} min), {len(images)} images ({rings} cursor rings), "
      f"{len(sfx)} sfx, {len(music)} music cues, {nk} camera keys")
