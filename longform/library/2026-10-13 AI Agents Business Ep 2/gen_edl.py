"""Edit decisions for AI Agents Business Ep 2: PaperRows (OBS take 2026-10-13 13-51-49) as a ccut EDL.

One 12:32 take: talking-head hook 0-59.4 (OBS stinger 59.4-61.9), the Agents Window 61.9-189.8, the PaperRows
site 191.4-535.4 (landing page to 418.7, then the demo: file picker 423, Stripe checkout 469.8-477.3, Excel
485.9-518.3), the Obsidian "PaperRows Simple Map" canvas 535.6-705.8 (he pans it himself), talking-head outro from 706.

Rules carried from taste.md: cut only pauses, ums, stutters, restarts and true repeats (Day 20 v2, confirmed);
no repair dissolves; transitions only on real scene changes; landing page full frame with the 1.2 s pause rule;
payment full frame; punch-ins static (CapCut 9.2), facecam overlay fixed; narration that contradicts the screen
is cut and the screen's wording carded. Coley's email and card on the Stripe page are blurred.
Run: python gen_edl.py  ->  edit.edl.json
"""
import json
import re
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
MAIN = "D:/OBS Video/2026-10-13 13-51-49.mp4"
GFX = HERE / "graphics" / "out"
AUD = HERE / "audio"
W, H = 3840, 2160
TAIL, HEAD = 0.14, 0.10

# ---- words and silences -------------------------------------------------------------
_SYN = {"okay": "ok", "alright": "allright", "rose": "rows"}
_norm = lambda s: _SYN.get(re.sub(r"[^a-z0-9]", "", s.lower()), re.sub(r"[^a-z0-9]", "", s.lower()))
WORDS = [(_norm(w["w"]), w["s"], w["e"]) for s in json.loads((HERE / "main.wav.words.json").read_text(encoding="utf-8"))["segments"]
         for w in s["words"]]
WORDS = [w for w in WORDS if w[0]]
for i in range(len(WORDS) - 2, -1, -1):        # "Paper Rose" / "PaperRows" -> one token
    if WORDS[i][0] == "paper" and WORDS[i + 1][0] == "rows":
        WORDS[i:i + 2] = [("paperrows", WORDS[i][1], WORDS[i + 1][2])]

def silences(path):
    t = re.findall(r"silence_(start|end): ([0-9.]+)", path.read_text())
    out, cur = [], None
    for kind, v in t:
        if kind == "start":
            cur = float(v)
        elif cur is not None:
            out.append((cur, float(v))); cur = None
    return out
SIL = silences(HERE / "sil35.txt")

def find(phrase, hint, win=45.0):
    """(start of first word, end of last word) of the phrase nearest the hint second."""
    toks = [_norm(t) for t in phrase.replace("paper rows", "paperrows").split() if _norm(t)]
    best = None
    for i in range(len(WORDS) - len(toks) + 1):
        if abs(WORDS[i][1] - hint) > win:
            continue
        if all(WORDS[i + k][0] == toks[k] for k in range(len(toks))):
            d = abs(WORDS[i][1] - hint)
            if best is None or d < best[0]:
                best = (d, WORDS[i][1], WORDS[i + len(toks) - 1][2])
    if best is None:
        raise SystemExit(f"phrase not found near {hint}: {phrase!r}")
    return best[1], best[2]

def snap_in(s):
    c = [e for a, e in SIL if s - 0.7 <= e <= s + 0.25]
    return (max(c) - HEAD) if c else s - 0.10

def snap_out(e):
    c = [a for a, b in SIL if e - 0.5 <= a <= e + 0.6]
    return (min(c) + TAIL) if c else e + 0.08

def keep(start, end, hint, kind="screen", end_hint=None, at_in=None, at_out=None):
    """at_in / at_out override a snapped edge that catches a neighbouring word (set from isolated snippets)."""
    s, _ = find(start, hint)
    _, e = find(end, end_hint if end_hint is not None else hint, win=90.0)
    return (round(at_in if at_in is not None else snap_in(s), 3), round(at_out if at_out is not None else snap_out(e), 3), kind)

# ---- the edit, in story order ------------------------------------------------------------
KEEPS = [
    # cold open: their own claim over the site they built, then the scoreboard
    keep("they said hey we can 100", "so they built it", 201, "cold", at_in=199.33),
    keep("so they have one sale so far", "one sale so far", 685.5, "cold", at_out=687.66),
    # hook (talking head)
    keep("a week ago you and i sat here", "all on their own", 3, "talk", at_in=2.05),
    keep("theyve done that", "what they created", 12, "talk", end_hint=17),
    keep("in this video im going to show you", "have put together", 20, "talk"),
    keep("the agents decided on a business called paper rows", "paper rows", 27, "talk"),   # restart dropped
    keep("in short paper rows is just a bank statement converter", "converter", 37.6, "talk"),
    keep("so it takes your solid pdf", "lets go", 42, "talk", end_hint=50, at_out=50.85),
    # 01 the Agents Window
    keep("all right first were going to jump into the agents window", "coming soon", 71.6, end_hint=101.5),
    keep("you have to stick around for that video", "next week", 102.1),
    keep("so lets get a little update on the window", "a couple updates", 107, end_hint=132.8),
    keep("the agents now get paid for their time", "future video on that", 133.2, end_hint=167),
    keep("anyway we are here for the paper rows business", "view their new website", 168.1, end_hint=189, at_out=189.72),
    # 02 PaperRows: the site
    # one keep across his scroll to How it works, so the page moves on continuous audio
    keep("and here we are in the paper rows website", "stay on your computer", 192, end_hint=287, at_in=191.62),
    # "So no data reaches a server or the agents themselves" is cut: the page's own table lists what reaches the server
    keep("so they cant read your name", "theyll reply", 292.3, end_hint=417.2, at_out=418.61),   # his scroll back up plays
    # 03 the demo
    keep("so up next were going to give a demo", "how things work", 418.9, end_hint=534, at_out=534.62),
    # 04 the canvas
    # he pans the canvas between lines, so the keeps run continuous and only still pauses are cut
    keep("now were in the obsidian canvas", "zero help", 537, end_hint=656.4, at_in=536.5),
    # "They, you know, they complete the, uh, pay, payroll, the, um" (restart) is cut
    keep("they complete the payroll the customer service", "everyone else", 665.5, end_hint=701, at_out=701.75),
    # outro (talking head); the first "so with that being said" falls in OBS's switch to the camera
    keep("with that being said be sure to check out", "next update", 710, "talk", end_hint=747.5, at_in=709.35),
]
OUTRO = 705.9
MAX_GAP = 0.4
OUTRO_GAP, OUTRO_TAIL, OUTRO_HEAD = 0.6, 0.2, 0.14
SITE = (191.0, 418.7)      # the landing page: pauses only over 1.2 s (confirmed C3 rule)

# Stutters inside keeps (source seconds), each confirmed in an isolated snippet (snip.py).
CUTS = [
    (151.04, 151.27),     # "on play payroll" -> "on payroll"
    (174.52, 176.47),     # "we, uh, you know, rejected" -> "we rejected"
    (254.36, 256.26),     # "before it is, uh, before you pay" -> "before you pay"
    (306.20, 308.12),     # "which I agree with. I fully agree with, um" (repeat)
    (339.96, 340.56),     # "the, the agent window"
    (343.38, 344.22),     # "who has, you know, clicked"
    (378.70, 379.68),     # "if you're, you know, your job" -> "if your job"
    (439.70, 440.03),     # "finished the, the statement"
    (594.66, 596.20),     # "that the, uh, you know, beginning"
    (682.12, 683.66),     # v2 (Codex #3): "so 11 people have tried it" -- the counter is 11 previews, not 11 people
]

# ---- what the screen does (frames.npz, 5 fps) ----------------------------------------
FPS_C = 5
_F = np.load(HERE / "frames.npz")
_FR = [(float(k), _F[k]) for k in _F.files]
def frame_at(t):
    for t0, a in _FR:
        i = round((t - t0) * FPS_C)
        if 0 <= i < len(a):
            return a[i].astype(np.int16)
    return None
def moves(t0, t1):
    out, t = [], t0
    while t + 1 / FPS_C <= t1 + 1e-6:
        a, b = frame_at(t), frame_at(t + 1 / FPS_C)
        out.append(None if a is None or b is None else float(np.abs(a - b).mean()))
        t += 1 / FPS_C
    return out
def jump(t0, t1):
    a, b = frame_at(t0), frame_at(t1)
    return 0.0 if a is None or b is None else float(np.abs(a - b).mean())
STILL = 1.0

def still_cut(a, b):
    m = moves(a, b)
    best, run_s = (a, a), None
    for i, v in enumerate(m + [99.0]):
        t = a + i / FPS_C
        if v is None or v < STILL:
            run_s = t if run_s is None else run_s
        else:
            if run_s is not None and t - run_s > best[1] - best[0]:
                best = (run_s + (0.2 if run_s > a else 0.0), t)   # Ep 2: let a pan settle before cutting
            run_s = None
    return best

# Screen changes inside continuous speech: splits, not cuts (no voice fade), so a swipe lands on the frame.
TO_STRIPE, FROM_STRIPE, TO_EXCEL, FROM_EXCEL = 469.80, 477.317, 485.90, 518.317
SITE_CLICK, TO_CANVAS, OBS_TO_CAM = 189.80, 535.53, 705.8
SPLITS = [TO_STRIPE, FROM_STRIPE, TO_EXCEL, FROM_EXCEL]
end_before = lambda t: max(k[1] for k in KEEPS if k[1] <= t + 0.5 and k[2] == "screen")

# Punch-ins (source in, out, scale, u, v): (u, v) is the centre of what he's talking about.
# The Agents Window is still the whole time; the demo only between its scrolls (motion map).
ZOOMS = [
    (75.8, 86.2, 1.5, 0.30, 0.25),      # "follow along... asgardagents.com": the header, URL and Odin/Thor cards
    (106.8, 131.9, 1.6, 0.31, 0.31),    # the new animations: Odin, Thor, Loki asleep by the fire
    (132.6, 167.6, 1.6, 0.31, 0.69),    # paid for their time: Token and Payroll (company holds 95,570,850)
    (168.0, 189.7, 1.6, 0.435, 0.775),  # "here for the PaperRows business": the Businesses panel, $5.00, Try it
    (431.2, 440.0, 1.5, 0.38, 0.55),    # the checks: 7 passed, 1 not checked
    (485.9, 518.317, 1.5, 0.30, 0.55),    # the CSV in Excel: description, amount, balance
]

def pieces():
    spans = []
    for a, b, kind in KEEPS:
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
            if SITE[0] <= s <= SITE[1]:
                gap = 1.2          # v2 (Codex #5): the PaperRows landing page keeps its pauses under 1.2 s
            if e - s <= gap or s < a or e > b:
                continue
            if any(s <= c <= e for c in SPLITS):
                continue           # a screen change inside this pause: keep the pause whole so the swipe lands in it
            x, y = s + tail, e - head
            if kind != "talk":
                x, y = still_cut(x, y)
                if y - x < 0.25 or jump(x, y) > 2.0:     # Ep 2: a pause cut that would still jump the picture stays in
                    continue
            if x > cur:
                out.append([cur, x, kind])
            cur = y
        out.append([cur, b, kind])
    res = []
    for a, b, kind in out:
        edges = SPLITS + ([e for w in ZOOMS for e in w[:2]] if kind in ("screen", "cold") else [])
        cuts = sorted(c for c in set(edges) if a + 0.3 < c < b - 0.3)
        for x, y in zip([a] + cuts, cuts + [b]):
            res.append([x, y, kind])
    return [p for p in res if p[1] - p[0] > 0.05]

PS = pieces()
dur = lambda p: p[1] - p[0]

def to_out(t, cold=False):
    """Source second -> edited-timeline second; the cold open reuses source, so it's opt-in."""
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

# ---- facecam and framing ---------------------------------------------------------------
CAM = {"rect": [2920, 1428, 3714, 2034], "clip": str(HERE / "facecam-crop.mp4")}
CX0, CY0 = 2920 / W, 1428 / H
is_screen_t = lambda t: 61.0 <= t <= OBS_TO_CAM
cam_visible = lambda a, b: is_screen_t(a) and is_screen_t(b)


def allowed(s, u, v):
    """Keep the frame inside the picture and the zoomed facecam copy off-frame (fixed-size overlay)."""
    m = 0.5 / s
    clamp = lambda a: min(max(a, m), 1 - m)
    u, v = clamp(u), clamp(v)
    off_r, off_b = CX0 - 1 / s + m, CY0 - 1 / s + m
    if u <= off_r + 1e-9 or v <= off_b + 1e-9:
        return u, v
    cands = [(clamp(min(u, off_r)), v), (u, clamp(min(v, off_b)))]
    cands = [c for c in cands if c[0] <= off_r + 1e-9 or c[1] <= off_b + 1e-9]
    return min(cands, key=lambda c: (c[0] - u) ** 2 + (c[1] - v) ** 2)

def to_frame(s, u, v):
    return round(s, 4), round((0.5 - u) * 2 * s, 4), round((v - 0.5) * 2 * s, 4)

def frame_of(p):
    a, b, kind = p
    if kind not in ("screen", "cold"):
        return None
    mid = (a + b) / 2
    w = next((z for z in ZOOMS if z[0] <= mid < z[1]), None)
    if not w:
        return None
    u, v = allowed(w[2], w[3], w[4])
    return to_frame(w[2], u, v)

FRAMES = [frame_of(p) for p in PS]

# ---- transitions (on the segment that ENDS at this source second) ----------------------
T_COLD_END = KEEPS[1][1]
T_TALK_END = [k for k in KEEPS if k[2] == "talk" and k[1] < 100][-1][1]
FIRST_SCREEN = [k for k in KEEPS if k[2] == "screen"][0][0]
TRANSITIONS = {
    T_COLD_END: ("White_Flash", 0.35),          # out of the cold open into the hook
    T_TALK_END: ("Snap_Zoom", 0.6),             # talking head -> the Agents Window
    end_before(SITE_CLICK): ("Swipe_Left", 0.45),      # his click on Try it -> the PaperRows site
    TO_STRIPE: ("Swipe_Left", 0.4),             # Unlock this statement -> Stripe checkout, mid-sentence
    FROM_STRIPE: ("Swipe_Left", 0.35),          # back from checkout, mid-sentence
    TO_EXCEL: ("Swipe_Left", 0.4),              # the downloaded CSV in Excel
    FROM_EXCEL: ("Swipe_Left", 0.4),            # back to the site
    end_before(TO_CANVAS): ("Zoom_to_Change", 0.6),    # the site -> the Obsidian canvas
    end_before(OBS_TO_CAM): ("Zoom_Transition", 0.5),  # the canvas -> the camera (v2: 0.5, clear of "So")
}
WHOOSH = {"White_Flash": "sfx-whoosh-air", "Snap_Zoom": "sfx-whoosh-air", "Zoom_to_Change": "sfx-whoosh-air",
          "Zoom_Transition": "sfx-whoosh-air", "Swipe_Left": "sfx-swipe"}

segments, talk_i = [], 0
for i, p in enumerate(PS):
    a, b, kind = p
    seg = {"in": round(a, 3), "out": round(b, 3)}
    if kind == "talk" and a >= OUTRO:
        pass                     # v2 (Codex #9): the outro holds one framing (calm exit, confirmed)
    elif kind == "talk":
        # v2 (Codex #6): a piece under 1.2 s keeps the previous framing instead of flashing 1.12 for half a second
        if dur(p) >= 1.2 or i == 0 or PS[i - 1][2] != "talk":
            talk_i += 1
        if talk_i % 2 == 0:
            seg["frame"] = {"scale": 1.12}
    elif FRAMES[i]:
        s_, x_, y_ = FRAMES[i]
        seg["frame"] = {"scale": s_, "x": x_, "y": y_}
        if cam_visible(a, b):
            seg["cam_overlay"] = {**CAM, "k0": 1.0}
    for tt, (name, d) in TRANSITIONS.items():
        if abs(tt - b) < 0.01 and ((kind == "cold") == (tt == T_COLD_END)):
            seg["transition"] = {"name": name, "duration": d}
    segments.append(seg)

# ---- graphics ------------------------------------------------------------------------------
images, sfx = [], []
MAN = json.loads((GFX / "manifest.json").read_text()) if (GFX / "manifest.json").exists() else {}
TOP_R, TOP_L, STAT, LOW = (3260, 330), (720, 250), (1920, 360), (1920, 1830)

SND = {"pop": ("pop.wav", 0.24), "coin": ("sfx-coin.wav", 0.22), "chime": ("sfx-chime.wav", 0.16),
       "boom": ("sfx-boom.wav", 0.30), "swish": ("sfx-swish-soft.wav", 0.16), "sparkle": ("sfx-sparkle.wav", 0.14),
       "glitch": ("sfx-glitch.wav", 0.12), "tick": ("sfx-tick.wav", 0.18), "impact": ("sfx-impact.wav", 0.17)}

def sound_at(kind, at, vol=None):
    f, v = SND[kind]
    sfx.append({"path": str(AUD / f), "start": round(at, 3), "volume": vol if vol is not None else v})

def img(name, t, d, x, y, scale=1.0, sound="pop", at=None, cold=False, pop=True):
    if name not in MAN:
        return
    at = cut_at(t, cold) if at is None else at
    half = MAN[name]["w"] * scale / 2
    if (x, y) == TOP_L:
        x = round(80 + half)
    elif (x, y) == TOP_R:
        x = round(3760 - half)
    images.append({"path": str(GFX / f"{name}.png"), "start": at, "duration": d, "x": x, "y": y, "scale": scale, "pop": pop})
    if sound:
        sound_at(sound, at)


# ---- v3 visual layer: highlight boxes on what he's talking about, a facecam frame, chapter whooshes ----------
from PIL import Image as _Image, ImageDraw as _Draw, ImageFilter as _Filter
GOLD = (245, 196, 81)

def piece_at(t):
    for i, p in enumerate(PS):
        if p[2] != "cold" and p[0] - 0.01 <= t <= p[1] + 0.01:
            return i, p
    raise SystemExit(f"highlight at {t} is cut out")

def _box_png(w, h, color=GOLD, stroke=10, pad=40):
    path = GFX / f"hl-{w}x{h}-{color[0]}.png"
    if not path.exists():
        W_, H_ = w + 2 * pad, h + 2 * pad
        glow = _Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
        _Draw.Draw(glow).rounded_rectangle((pad, pad, pad + w, pad + h), radius=26, outline=color + (200,), width=stroke * 3)
        glow = glow.filter(_Filter.GaussianBlur(14))
        _Draw.Draw(glow).rounded_rectangle((pad, pad, pad + w, pad + h), radius=26, outline=color + (255,), width=stroke)
        glow.save(path)
    return path

def hl(rect, t, d, color=GOLD, sound=True):
    """Glowing box around a SOURCE-pixel rect at source second t, mapped through that piece's punch-in."""
    i, p = piece_at(t)
    fr = segments[i].get("frame") or {"scale": 1.0, "x": 0.0, "y": 0.0}
    sc, fx, fy = fr.get("scale", 1.0), fr.get("x", 0.0), fr.get("y", 0.0)
    u, v = 0.5 - fx / (2 * sc), 0.5 + fy / (2 * sc)
    l, tp = (u - 0.5 / sc) * W, (v - 0.5 / sc) * H
    x0, y0, x1, y1 = [(rect[0] - l) * sc, (rect[1] - tp) * sc, (rect[2] - l) * sc, (rect[3] - tp) * sc]
    x0, y0, x1, y1 = max(x0, 8), max(y0, 8), min(x1, W - 8), min(y1, H - 8)
    w, h = round(x1 - x0), round(y1 - y0)
    # hold across the next pieces while the framing is the same and the cut doesn't jump (a pause cut on a
    # still page); never past a real change of picture
    avail, j = p[1] - t, i
    while avail < d and j + 1 < len(PS) and FRAMES[j + 1] == FRAMES[i] and PS[j + 1][2] == p[2] \
            and jump(PS[j][1] - 0.05, PS[j + 1][0]) < 1.0 and not any(abs(tt - PS[j][1]) < 0.01 for tt in TRANSITIONS):
        j += 1
        avail += PS[j][1] - PS[j][0]
    d = round(min(d, avail), 3)
    at = cut_at(t)
    images.append({"path": str(_box_png(w, h, color)), "start": at, "duration": d,
                   "x": round((x0 + x1) / 2), "y": round((y0 + y1) / 2), "scale": 1.0, "pop": "glow"})
    if sound:
        sound_at("tick", at)

def facecam_frame():
    """A thin gold frame on the recorded facecam (rounded 36 px), one image per screen run between transitions."""
    path = GFX / "facecam-frame.png"
    x0, y0, x1, y1 = 2920, 1428, 3714, 2034
    pad, st = 30, 7
    if not path.exists():
        im = _Image.new("RGBA", (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), (0, 0, 0, 0))
        g = im.copy()
        _Draw.Draw(g).rounded_rectangle((pad, pad, pad + x1 - x0, pad + y1 - y0), radius=38, outline=GOLD + (150,), width=st * 3)
        g = g.filter(_Filter.GaussianBlur(10))
        _Draw.Draw(g).rounded_rectangle((pad, pad, pad + x1 - x0, pad + y1 - y0), radius=38, outline=GOLD + (235,), width=st)
        g.save(path)
    off, run = 0.0, None
    tr_ends = {round(t, 3) for t in TRANSITIONS}
    for i, p in enumerate(PS):
        d_ = dur(p)
        screen = p[2] in ("screen", "cold") and 61.0 <= p[0] < OBS_TO_CAM
        if screen and run is None:
            prev_tr = i > 0 and any(abs(tt - PS[i - 1][1]) < 0.01 for tt in TRANSITIONS)
            run = off + (0.8 if prev_tr else 0.0)
        end_here = round(p[1], 3) in tr_ends or not screen or i == len(PS) - 1
        if run is not None and (not screen or end_here):
            stop = off + (d_ if screen else 0.0)
            if stop - run > 1.0:
                images.append({"path": str(path), "start": round(run, 3), "duration": round(stop - run, 3),
                               "x": (x0 + x1) // 2, "y": (y0 + y1) // 2, "scale": 1.0, "pop": "glow"})
            run = None
        off += d_

exec((HERE / "graphics_plan.py").read_text(encoding="utf-8")) if (HERE / "graphics_plan.py").exists() else None
facecam_frame()

FADE = 1.2
images.append({"path": str(GFX / "black-4k.png"), "start": round(TOTAL - FADE, 3), "duration": FADE, "x": 1920, "y": 1080, "pop": "fade"})
images.append({"path": str(GFX / "black-4k.png"), "start": round(TOTAL - 0.2, 3), "duration": 0.2, "x": 1920, "y": 1080, "pop": False})
for t, (name, d) in TRANSITIONS.items():
    sfx.append({"path": str(AUD / f"{WHOOSH[name]}.wav"), "peak_at": round(cut_at(t, cold=(t == T_COLD_END)) - 0.06, 3),
                "volume": 0.30 if WHOOSH[name] == "sfx-whoosh-air" else 0.20})

# ---- music --------------------------------------------------------------------------------
BEDS = json.loads((AUD / "beds.json").read_text()) if (AUD / "beds.json").exists() else {}
def bed(name, at, end, target=-32.0, offset=None):
    b = BEDS[name]
    off = b.get("offset", 0.0) if offset is None else offset
    return {"path": str(AUD / b["file"]), "at": round(at, 3), "start_offset": off,
            "duration": round(min(end - at, b["length"] - off), 3), "volume": round(10 ** ((target - b["lufs"]) / 20), 3)}

def fill(start, end, names, target=-32.0, fade_out=1.2, fade_in=1.0):
    cues, t, i = [], start, 0
    while end - t > 0.5:
        c = bed(names[i % len(names)], t, end, target)
        c["fade_in"], c["fade_out"] = fade_in, 1.2
        cues.append(c); t += c["duration"]; i += 1
    if len(cues) > 1 and cues[-1]["duration"] < 3.0:
        cues.pop()
    if cues:
        cues[-1]["fade_out"] = fade_out
    return cues

music = []
if BEDS:
    exec((HERE / "music_plan.py").read_text(encoding="utf-8"))

edl = {
    "project": "AI Agents Business Ep 2 - Edit",
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
if __name__ == "__main__":
    print(f"{len(segments)} segments, {TOTAL:.1f}s ({TOTAL/60:.2f} min), {len(images)} images, {len(sfx)} sfx, "
          f"{len(music)} music cues, {sum(1 for s in segments if 'transition' in s)} transitions, "
          f"{sum(1 for s in segments if s.get('frame', {}).get('scale', 1) > 1.13)} punch-ins")
