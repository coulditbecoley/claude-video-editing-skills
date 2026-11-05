"""Edit decisions for Asgard Agents Day 30 (OBS take 2026-10-23 10-40-36) as a ccut EDL.

One 19:55 take: talking-head hook 0-36.8 (OBS stinger 36.8-37.5), the Obsidian "Day 30 - What's New" canvas
37.5-450.75, the Agents Window 450.75-793.8 (a page reload at 454-460), the Sponsor the Hall page 793.8-832.2,
back to the Window to 853.4, X 853.4-950.1, the Pump.fun stream 953-1013, YouTube 1018-1121 (his home feed and
search history 1018-1048 are dead air and cut), the Window again 1121-1147, talking-head outro from 1150.

Rules carried from taste.md: cut only pauses, ums, stutters, restarts and true repeats (Day 20 v2, confirmed);
no repair dissolves; transitions only on real scene changes; pause cuts only across still screen; punch-ins
static (CapCut 9.2), facecam overlay fixed; narration that overreaches the screen is carded with the screen's
wording. Day 30 additions: every SFX is placed by its own attack (peak-aligned to the animation's hit frame),
and every image and SFX start sits on the 30 fps grid.
Run: python gen_edl.py  ->  edit.edl.json
"""
import json
import re
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
MAIN = "D:/OBS Video/2026-10-23 10-40-36.mp4"
GFX = HERE / "graphics" / "out"
AUD = HERE / "audio"
W, H = 3840, 2160
FPS = 30
TAIL, HEAD = 0.14, 0.10
q = lambda t: round(round(t * FPS) / FPS, 4)     # snap an output second to the 30 fps grid

# ---- words and silences -------------------------------------------------------------
_SYN = {"okay": "ok", "alright": "allright", "rose": "rows", "hemdell": "heimdall", "himdell": "heimdall"}
_n0 = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
_norm = lambda s: _SYN.get(_n0(s), _n0(s))
WORDS = [(_norm(w["w"]), w["s"], w["e"]) for s in json.loads((HERE / "main.wav.words.json").read_text(encoding="utf-8"))["segments"]
         for w in s["words"]]
WORDS = [w for w in WORDS if w[0]]
for i in range(len(WORDS) - 2, -1, -1):        # "Paper Rose" -> one token
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
    """at_in / at_out override a snapped edge (set from silences or isolated snippets)."""
    s, _ = find(start, hint)
    _, e = find(end, end_hint if end_hint is not None else hint, win=120.0)
    return (round(at_in if at_in is not None else snap_in(s), 3), round(at_out if at_out is not None else snap_out(e), 3), kind)

# ---- the edit, in story order ------------------------------------------------------------
# Section edges at a transition leave >= 0.35 s after the last word and >= 0.25 s before the first (confirmed).
KEEPS = [
    # cold open: the money, then the honest answer (the scoreboard's "Not yet" card)
    keep("checkouts they have made", "two businesses so far", 491.0, "cold"),
    keep("are they profitable yet", "no not yet", 121.2, "cold", at_out=124.62),
    # hook (talking head)
    keep("have you ever seen ai agents", "updates for today", 1.6, "talk", end_hint=28.5, at_in=1.40, at_out=29.84),
    # 01-05 the Obsidian canvas: scoreboard, follow along, mistakes, behind the scenes, what's next
    keep("all right weve made it to obsidian", "get the updates", 45.0, end_hint=449.0, at_in=44.30, at_out=450.02),
    # 06 the Agents Window (the reload at 454-460 falls in the cut), the Sponsor page round trip, on to X
    keep("so here we are in the agents window", "welcome to do that here", 466.3, end_hint=825.0, at_in=465.92, at_out=826.50),
    # he leaves browser fullscreen at 828.4 and swipes back to the Window at 832.2: both fall in the cut, the
    # first "But" (828.2) with them; back on the settled Window just before "But heading back"
    keep("heading back on over to the agent window", "because they did get", 836.5, end_hint=849.5, at_in=835.95, at_out=850.62),
    # 07 X (the notifications page 853.4-873 falls in the cut)
    # (the default pass hallucinated "a new account" here; the literal snippet has "they did get back on X")
    keep("and here we are on x", "very nice", 874.4, end_hint=936.0, at_in=873.90, at_out=936.72),
    # 08 the Pump.fun stream
    keep("and here we are on pump fun", "how theyre doing over there", 979.5, end_hint=1012.3, at_in=979.25, at_out=1012.92),
    # 09 YouTube (his home feed and search dropdown 1018-1048 fall in the cut)
    keep("and here we are on youtube", "that is the youtube", 1059.0, end_hint=1112.8, at_in=1058.95, at_out=1113.55),
    # outro (talking head): "And that is the update" starts at 1160.06 (energy), after a breath at 1159.7
    keep("day 30 of the asgard agents", "live 24 seven", 1162.0, "talk", end_hint=1188.5, at_in=1159.74),
]
OUTRO = 1150.0
MAX_GAP = 0.4
OUTRO_GAP, OUTRO_TAIL, OUTRO_HEAD = 0.6, 0.2, 0.14

# Stutters, fillers and true repeats inside keeps (source seconds), each confirmed in an isolated snippet.
exec((HERE / "cuts.py").read_text(encoding="utf-8")) if (HERE / "cuts.py").exists() else None
CUTS = globals().get("CUTS", [])

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
    """motion of the PICTURE that plays at voice times t0..t1 (the picture is shifted by S)"""
    sh = S(t0) if "S" in globals() else 0.0
    t0, t1 = t0 + sh, t1 + sh
    out, t = [], t0
    while t + 1 / FPS_C <= t1 + 1e-6:
        a, b = frame_at(t), frame_at(t + 1 / FPS_C)
        out.append(None if a is None or b is None else float(np.abs(a - b).mean()))
        t += 1 / FPS_C
    return out
def jump(t0, t1):
    a, b = frame_at(t0 + (S(t0) if "S" in globals() else 0.0)), frame_at(t1 + (S(t1) if "S" in globals() else 0.0))
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
                best = (run_s + (0.2 if run_s > a else 0.0), t)   # let a scroll settle before cutting
            run_s = None
    return best

# Screen changes inside continuous speech or a kept pause: splits, not cuts, so a swipe lands on the frame.
# v3 lip sync (Coley, 2026-10-23: "the face cam and the audio speech do not line up"). The OBS webcam picture lags
# the mic (measured with MediaPipe lip landmarks, lipsync_mp.py / lip_scan.py), and the voice chain adds 25 ms on
# top (afftdn). All cut decisions are made on the voice; at the very end every segment's in/out moves by +SYNC and
# the voice file is the cleaned voice delayed by SYNC (audio/voice-sync.wav), so the voice plays exactly what it did
# and the picture comes from SYNC later, matching the mouth. Graphics and SFX keep their timeline positions.
# v4: the lag is NOT constant (Codex v3 audit; lip_timeline.py): ~378 ms through the canvas and early Window, ~83 ms
# after source ~720 s, so each section gets its own picture shift (sync_sections.json). A piece never spans a section
# edge (each edge sits in a cut or a transition). The voice keeps the original cleaned file via ccut's av_offset.
SECTIONS = json.loads((HERE / "sync_sections.json").read_text())["sections"]
def S(t):
    return next((o for a, b, o in SECTIONS if a <= t < b), 0.0)
SYNC = None
TO_SPONSOR = 793.767 - S(793.767)  # the click frame, in voice time (so the shifted picture splits ON the click)
SPLITS = [TO_SPONSOR]
SPLIT_KEEP = (0.45, 0.55)        # a long pause around a split keeps this much either side of the switch frame

# Punch-ins (source in, out, scale, u, v): (u, v) is the centre of what he's talking about (filled in zooms.py).
exec((HERE / "zooms.py").read_text(encoding="utf-8")) if (HERE / "zooms.py").exists() else None
ZOOMS = globals().get("ZOOMS", [])

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
            if e - s <= gap or s < a or e > b:
                continue
            sp = [c for c in SPLITS if s <= c <= e]
            if sp:
                # a screen change inside this pause: keep a short stretch either side so the swipe lands on it
                c = sp[0]
                for x, y in ((s + tail, c - SPLIT_KEEP[0]), (c + SPLIT_KEEP[1], e - head)):
                    if kind != "talk":
                        x, y = still_cut(x, y)
                    if y - x >= 0.25 and jump(x, y) <= 2.0:
                        if x > cur:
                            out.append([cur, x, kind])
                        cur = y
                continue
            x, y = s + tail, e - head
            if kind != "talk":
                x, y = still_cut(x, y)
                if y - x < 0.25 or jump(x, y) > 2.0:     # a pause cut that would still jump the picture stays in
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
is_screen_t = lambda t: 37.5 <= t <= 1147.0
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
T_TALK_END = KEEPS[2][1]
end_of = lambda i: KEEPS[i][1]
TRANSITIONS = {
    T_COLD_END: ("White_Flash", 0.35),          # out of the cold open into the hook
    T_TALK_END: ("Snap_Zoom", 0.6),             # talking head -> the Obsidian canvas
    end_of(3): ("Zoom_to_Change", 0.6),         # the canvas -> the Agents Window
    TO_SPONSOR: ("Swipe_Left", 0.4),            # his click on the sponsor bar -> Sponsor the Hall, mid-sentence
    end_of(4): ("Swipe_Left", 0.4),             # Sponsor the Hall -> back to the Window
    end_of(5): ("Swipe_Left", 0.45),            # the Window -> X
    end_of(6): ("Swipe_Left", 0.45),            # X -> the Pump.fun stream
    end_of(7): ("Swipe_Left", 0.45),            # Pump.fun -> YouTube
    end_of(8): ("Zoom_Transition", 0.5),        # YouTube -> the camera
}
WHOOSH = {"White_Flash": "sfx-whoosh-air", "Snap_Zoom": "sfx-whoosh-air", "Zoom_to_Change": "sfx-whoosh-air",
          "Zoom_Transition": "sfx-whoosh-air", "Swipe_Left": "sfx-swipe"}

segments, talk_i = [], 0
for i, p in enumerate(PS):
    a, b, kind = p
    seg = {"in": round(a, 3), "out": round(b, 3)}
    if kind == "talk" and a >= OUTRO:
        pass                     # the outro holds one framing (calm exit, confirmed)
    elif kind == "talk":
        # a piece under 1.2 s keeps the previous framing instead of flashing 1.12 for half a second
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

# ---- graphics and sound ---------------------------------------------------------------------
images, sfx = [], []
MAN = json.loads((GFX / "manifest.json").read_text()) if (GFX / "manifest.json").exists() else {}
TOP_R, TOP_L, STAT, LOW = (3260, 330), (720, 250), (1920, 360), (1920, 1830)

# Each sound has one job, and a HIT: the frame its animation lands (pop at full size, slide at its fastest,
# glow settled, chip bar in). The sample's own loudest point is placed on that frame (ccut peak_at).
SND = {"pop": ("pop.wav", 0.24), "coin": ("sfx-coin.wav", 0.22), "chime": ("sfx-chime.wav", 0.16),
       "boom": ("sfx-boom.wav", 0.30), "swish": ("sfx-swish-soft.wav", 0.16), "sparkle": ("sfx-sparkle.wav", 0.14),
       "glitch": ("sfx-glitch.wav", 0.12), "tick": ("sfx-tick.wav", 0.16), "impact": ("sfx-impact.wav", 0.17)}
# v2 (Codex #1): read off ccut's saved keys. Pop reaches full size at 154 ms (frame 5), a glow settles at 200 ms
# (frame 6), a slide reaches its overshoot at 220 ms (frame 7); a "_out"-only strip swaps in place (frame 0).
HIT = {True: 5 / FPS, "in": 5 / FPS, "glow": 6 / FPS, "slide": 7 / FPS, "fade": 0.0, False: 0.0}   # whole frames into the clip
hit_of = lambda pop: (0.0 if pop.endswith("_out") else HIT["slide"]) if isinstance(pop, str) and pop.startswith("slide") else HIT.get(pop, 0.1)

def sound_at(kind, at, vol=None, peak=True):
    f, v = SND[kind]
    s = {"path": str(AUD / f), "volume": vol if vol is not None else v}
    s["peak_at" if peak else "start"] = q(at)      # frame-aligned: CapCut snaps clips to frames (audio/pad_sfx.py)
    sfx.append(s)

SLOT_TOP, SLOT_BOT = (1920, 330), (1700, 1860)
_hlboxes = []       # (start, end, x0, y0, x1, y1) of every highlight placed so far, in output px

def _box(name, x, y, scale):
    w, h = MAN[name]["w"] * scale, MAN[name]["h"] * scale
    return x - w / 2, y - h / 2, x + w / 2, y + h / 2

def img(name, t, d, x="auto", y=None, scale=None, sound="pop", at=None, cold=False, pop=True, vol=None):
    """A card at source second t for d seconds. x="auto" takes the top slot unless a highlight box lives there,
    else the bottom slot (anchored left of the facecam). Cards wider than 2400 px are scaled to fit."""
    if name not in MAN:
        return
    raw_at = cut_at(t, cold) if at is None else at
    at = q(raw_at)
    d = round(q(raw_at + d) - at, 4)          # the end on the frame grid too, so swapped strips never overlap
    if scale is None:
        scale = min(0.85, 2400 / MAN[name]["w"])
    half = MAN[name]["w"] * scale / 2
    if x == "auto":
        def clash(cx, cy):
            b = _box(name, cx, cy, scale)
            return any(a0 < at + d and at < a1 and b[0] < x1_ and x0_ < b[2] and b[1] < y1_ and y0_ < b[3]
                       for a0, a1, x0_, y0_, x1_, y1_ in _hlboxes)
        bx = min(SLOT_BOT[0], round(2860 - half))
        x, y = (SLOT_TOP if not clash(*SLOT_TOP) else (bx, SLOT_BOT[1]))
    elif x == "low":
        x, y = min(SLOT_BOT[0], round(2860 - half)), SLOT_BOT[1]
    elif (x, y) == TOP_L:
        x = round(80 + half)
    elif (x, y) == TOP_R:
        x = round(3760 - half)
    images.append({"path": str(GFX / f"{name}.png"), "start": at, "duration": round(d, 3), "x": x, "y": y, "scale": round(scale, 3), "pop": pop})
    if sound:
        sound_at(sound, at + hit_of(pop), vol)

# ---- highlight boxes on what he's talking about, a facecam frame ---------------------------------
from PIL import Image as _Image, ImageDraw as _Draw, ImageFilter as _Filter
GOLD = (245, 196, 81)

def piece_at(t):
    for i, p in enumerate(PS):
        if p[2] != "cold" and p[0] - 0.01 <= t <= p[1] + 0.01:
            return i, p
    for i, p in enumerate(PS):      # inside a cut: the next kept frame, if it's close
        if p[2] != "cold" and 0 < p[0] - t < 1.0:
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

def pic_jump(a, b):
    """picture difference between two PICTURE times (no sync shift)"""
    fa, fb = frame_at(a), frame_at(b)
    return 0.0 if fa is None or fb is None else float(np.abs(fa - fb).mean())

def hl(rect, t, d, color=GOLD, sound=True, mt=None):
    """Glowing box around a SOURCE-pixel rect at voice second t, mapped through that piece's punch-in.
    mt = the picture time the rect was measured on (probe/hlgrid_*: phrase start + 0.4 s; calls use t = start + 0.3,
    so the default is t + 0.1). v4 (Codex v4 audit, the treasury box): with the lip-sync shift the picture under t is
    t + S(t); if the canvas has moved since the measurement frame, show the box when the picture IS that frame."""
    mt = t + 0.1 if mt is None else mt
    if pic_jump(mt, t + S(t)) > 1.0:
        t = mt - S(t)
    i, p = piece_at(t)
    t = max(t, p[0] + 0.02)
    fr = segments[i].get("frame") or {"scale": 1.0, "x": 0.0, "y": 0.0}
    sc, fx, fy = fr.get("scale", 1.0), fr.get("x", 0.0), fr.get("y", 0.0)
    u, v = 0.5 - fx / (2 * sc), 0.5 + fy / (2 * sc)
    l, tp = (u - 0.5 / sc) * W, (v - 0.5 / sc) * H
    x0, y0, x1, y1 = [(rect[0] - l) * sc, (rect[1] - tp) * sc, (rect[2] - l) * sc, (rect[3] - tp) * sc]
    x0, y0, x1, y1 = max(x0, 8), max(y0, 8), min(x1, W - 8), min(y1, H - 8)
    w, h = round(x1 - x0), round(y1 - y0)
    if w < 40 or h < 20:
        print(f"HL OFF-FRAME at {t:.2f} {rect} (frame {fr})"); return
    # hold across the next pieces while the framing is the same and the cut doesn't jump; never past a change
    avail, j = p[1] - t, i
    while avail < d and j + 1 < len(PS) and FRAMES[j + 1] == FRAMES[i] and PS[j + 1][2] == p[2] \
            and jump(PS[j][1] - 0.05, PS[j + 1][0]) < 1.0 and not any(abs(tt - PS[j][1]) < 0.01 for tt in TRANSITIONS):
        j += 1
        avail += PS[j][1] - PS[j][0]
    d = round(min(d, avail), 3)
    # hold only while the screen under the box is still (he scrolls the canvas between lines)
    still = 0.0
    for v in moves(t, t + d):
        if v is None or v >= STILL:
            break
        still += 1 / FPS_C
    d = round(min(d, max(still, 0.0)), 3)
    if d < 1.5:          # never under 1.5 s on screen (accepted rule)
        return
    at = q(cut_at(t))
    _hlboxes.append((at, at + d, x0, y0, x1, y1))
    images.append({"path": str(_box_png(w, h, color)), "start": at, "duration": d,
                   "x": round((x0 + x1) / 2), "y": round((y0 + y1) / 2), "scale": 1.0, "pop": "glow"})
    if sound:
        sound_at("tick", at + HIT["glow"])

def facecam_frame():
    """A thin gold frame on the recorded facecam (rounded), one image per screen run between transitions."""
    path = GFX / "facecam-frame.png"
    x0, y0, x1, y1 = CAM["rect"]
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
        screen = p[2] in ("screen", "cold") and is_screen_t(p[0])
        if screen and run is None:
            prev_tr = i > 0 and any(abs(tt - PS[i - 1][1]) < 0.01 for tt in TRANSITIONS)
            run = off + (0.8 if prev_tr else 0.0)
        end_here = round(p[1], 3) in tr_ends or not screen or i == len(PS) - 1
        if run is not None and (not screen or end_here):
            stop = off + (d_ if screen else 0.0)
            if stop - run > 1.0:
                images.append({"path": str(path), "start": q(run), "duration": round(stop - q(run), 3),
                               "x": (x0 + x1) // 2, "y": (y0 + y1) // 2, "scale": 1.0, "pop": "glow"})
            run = None
        off += d_

exec((HERE / "graphics_plan.py").read_text(encoding="utf-8")) if (HERE / "graphics_plan.py").exists() else None
facecam_frame()

FADE = 1.2
images.append({"path": str(GFX / "black-4k.png"), "start": q(TOTAL - FADE), "duration": FADE, "x": 1920, "y": 1080, "pop": "fade"})
images.append({"path": str(GFX / "black-4k.png"), "start": q(TOTAL - 0.2), "duration": 0.2, "x": 1920, "y": 1080, "pop": False})
# transitions: the whoosh's loudest point sits on the cut frame (the middle of the CapCut transition)
for t, (name, d) in TRANSITIONS.items():
    sfx.append({"path": str(AUD / f"{WHOOSH[name]}.wav"), "peak_at": q(cut_at(t, cold=(t == T_COLD_END))),
                "volume": 0.26 if WHOOSH[name] == "sfx-whoosh-air" else 0.18})

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

for seg in segments:
    sh = S((seg["in"] + seg["out"]) / 2)
    assert S(seg["in"]) == S(seg["out"]) == sh, f"piece {seg['in']}-{seg['out']} spans a sync section edge"
    if sh:
        seg["in"], seg["out"] = round(seg["in"] + sh, 4), round(seg["out"] + sh, 4)
        seg["av_offset"] = sh            # ccut plays the voice from (in - av_offset): the original voice time
VOICE_FILE = AUD / "voice-main.wav"

edl = {
    "project": "Asgard Agents Day 30 - Edit",
    "source": MAIN,
    "resolution": [W, H],
    "fps": FPS,
    "voice": {MAIN: str(VOICE_FILE)},
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
