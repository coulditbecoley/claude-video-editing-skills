"""Edit decisions for AI Agents Business Ep 3, the PaperRows update (OBS take 2026-10-23 11-18-15) as a ccut EDL.

One 10:32 take: talking-head hook 0-25.3 (OBS fade into the canvas 25.3-25.45), the agents' "PaperRows Simple Map"
Obsidian canvas 25.4-263.3, the Agents Window 263.3-336.73 (his click on PaperRows; a grey page load 336.73-337.77),
the PaperRows site (the folder drop 371-376, the results, the save dialog 400.47-405.2, the downloads), Excel
431.6-472.5, the PaperRows site again (Help > Send feedback 490.1), talking-head outro from 532.25 with five sign-off
takes (the clean ones are kept).

Rules carried from taste.md: cut only pauses, ums, stutters, restarts and true repeats (Day 20 v2, confirmed); no
repair dissolves; transitions only on real scene changes; pause cuts only across still screen; punch-ins static
(CapCut 9.2), facecam overlay fixed; narration that overreaches the screen is cut or carded with the screen's wording;
personal details in OS dialogs blurred; every SFX placed by its own peak on the animation's hit frame; every image
and SFX start on the 30 fps grid; lip sync per section from the whole-take mouth map (sync_sections.json).
Run: python gen_edl.py  ->  edit.edl.json
"""
import json
import re
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
MAIN = "D:/OBS Video/2026-10-23 11-18-15.mp4"
GFX = HERE / "graphics" / "out"
AUD = HERE / "audio"
W, H = 3840, 2160
FPS = 30
TAIL, HEAD = 0.14, 0.10
q = lambda t: round(round(t * FPS) / FPS, 4)     # snap an output second to the 30 fps grid

# ---- words and silences -------------------------------------------------------------
_SYN = {"okay": "ok", "alright": "allright", "rose": "rows", "gonna": "going"}
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
    # cold open: the new folder drop, the goal, the score so far
    keep("were going to drag it on in here", "they are populated", 371.7, "cold", at_in=371.46, at_out=376.30),
    keep("the goal is five paying customers", "the goal is five paying customers", 248.4, "cold", at_in=248.22, at_out=250.12),
    keep("so far they have had four customers", "so far they have had four customers", 316.1, "cold", at_in=316.33, at_out=319.14),
    # hook (talking head)
    keep("in this video", "show you the outline", 2.9, "talk", end_hint=18.3, at_in=2.62, at_out=19.32),
    # 01-03 the agents' PaperRows canvas: how it works, the new folder drop, who runs it
    keep("here we are in the obsidian canvas", "and lets move on to that", 32.0, end_hint=256.5, at_in=31.66, at_out=257.86),
    # 04 the Agents Window; his click on PaperRows (336.73) sits in the "uh, uh," cut at 336.02-336.80
    keep("and here we are in the agents window", "lets get into that", 266.4, end_hint=352.3, at_in=266.08, at_out=353.10),
    # 05 the folder drop, live (his 11 s setup 353-364 is dead air and cut; same page either side)
    keep("so i have some demo statements", "after they are opened", 364.5, end_hint=415.6, at_in=364.26, at_out=417.96),
    # 06 the CSV in Excel (the wait for Excel 418-434 is cut; the swipe lands on that cut)
    keep("and here you go", "any other ones as well", 434.3, end_hint=469.4, at_in=433.95, at_out=470.40),
    # 07 send feedback
    keep("one last thing", "and you can do that", 481.5, end_hint=521.9, at_in=481.20, at_out=522.90),
    # outro (talking head): the update line, the clean retake of the share ask, the clean sign-off
    keep("that is the update on the", "same style of client", 536.2, "talk", end_hint=550.6, at_in=535.90, at_out=551.22),
    keep("if you know any accountants or bookkeepers that could use a system like this", "into csv files", 574.5, "talk",
         end_hint=584.5, at_in=574.26, at_out=585.62),
    keep("thats all for the paperrows update", "have done next", 620.1, "talk", end_hint=626.4, at_in=620.10, at_out=627.60),
]
COLD_N = 3
OUTRO = 535.0
MAX_GAP = 0.4
OUTRO_GAP, OUTRO_TAIL, OUTRO_HEAD = 0.6, 0.2, 0.14

# Stutters, fillers and true repeats inside keeps (source seconds), each confirmed in an isolated snippet.
exec((HERE / "cuts.py").read_text(encoding="utf-8"))
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
def moves(t0, t1, rect=None):
    """motion of the PICTURE that plays at voice times t0..t1 (the picture is shifted by S); rect (source px) limits
    it to that region (frames.npz is 192x108, 20 source px a cell), padded by one cell"""
    sh = S(t0)
    t0, t1 = t0 + sh, t1 + sh
    sl = (slice(None), slice(None)) if rect is None else         (slice(max(0, rect[1] // 20 - 1), min(108, rect[3] // 20 + 2)), slice(max(0, rect[0] // 20 - 1), min(192, rect[2] // 20 + 2)))
    out, t = [], t0
    while t + 1 / FPS_C <= t1 + 1e-6:
        a, b = frame_at(t), frame_at(t + 1 / FPS_C)
        out.append(None if a is None or b is None else float(np.abs(a[sl] - b[sl]).mean()))
        t += 1 / FPS_C
    return out
def jump(t0, t1):
    a, b = frame_at(t0 + S(t0)), frame_at(t1 + S(t1))
    return 0.0 if a is None or b is None else float(np.abs(a - b).mean())
STILL = 1.0
STILL_HL = 3.0

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

# Lip sync (Day 30 lesson 15): the webcam lag is mapped over the whole take and each section gets its own whole-frame
# picture shift (sync_sections.json). All cut decisions are made on the voice; at the very end every segment's in/out
# moves by +S and ccut plays the voice from (in - av_offset), the original voice time. Every section edge sits in a cut.
SECTIONS = json.loads((HERE / "sync_sections.json").read_text())["sections"]
def S(t):
    return next((o for a, b, o in SECTIONS if a <= t < b), 0.0)
TO_FEEDBACK = round(490.133 - 0.066667, 3)   # his click on Help > Send feedback (picture 490.133), in voice time
SPLITS = [TO_FEEDBACK]
SPLIT_KEEP = (0.45, 0.55)
TO_SITE = 336.02                 # the "uh, uh," cut that holds his click on PaperRows (picture 336.733): a hard cut onto
# the settled page (cover-site) with a quiet swipe sound. A Swipe transition can't be used here: the static cover would
# pop in halfway through it and the moving picture would show through its facecam hole.

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
is_screen_t = lambda t: 25.4 <= t <= 532.2
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
T_COLD_END = KEEPS[COLD_N - 1][1]
T_TALK_END = KEEPS[COLD_N][1]
end_of = lambda i: KEEPS[i][1]
TRANSITIONS = {
    T_COLD_END: ("White_Flash", 0.35),          # out of the cold open into the hook
    T_TALK_END: ("Snap_Zoom", 0.6),             # talking head -> the Obsidian canvas
    end_of(4): ("Zoom_to_Change", 0.6),         # the canvas -> the Agents Window
    end_of(6): ("Swipe_Left", 0.45),            # PaperRows -> Excel
    end_of(7): ("Swipe_Left", 0.45),            # Excel -> PaperRows (Send feedback)
    TO_FEEDBACK: ("Swipe_Left", 0.4),           # PaperRows home -> the Send feedback page, mid-sentence
    end_of(8): ("Zoom_Transition", 0.5),        # the site -> the camera
}
WHOOSH = {"White_Flash": "sfx-whoosh-air", "Snap_Zoom": "sfx-whoosh-air", "Zoom_to_Change": "sfx-whoosh-air",
          "Zoom_Transition": "sfx-whoosh-air", "Swipe_Left": "sfx-swipe"}

# outro: one framing per keep, alternating, so the two retake joins read as camera cuts (calm exit otherwise)
OUTRO_SCALE = {9: 1.0, 10: 1.12, 11: 1.0}
keep_of = lambda p: next(i for i, (a, b, k) in enumerate(KEEPS) if a - 1e-6 <= p[0] and p[1] <= b + 1e-6 and k == p[2])

segments, talk_i = [], 0
for i, p in enumerate(PS):
    a, b, kind = p
    seg = {"in": round(a, 3), "out": round(b, 3)}
    if kind == "talk" and a >= OUTRO:
        sc = OUTRO_SCALE.get(keep_of(p), 1.0)
        if sc != 1.0:
            seg["frame"] = {"scale": sc}
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

# Each sound has one job, and a HIT: the frame its animation lands. Read off ccut's saved keys (Day 30 Codex #1):
# pop full size at 154 ms (frame 5), glow settled at 200 ms (frame 6), slide overshoot at 220 ms (frame 7), a swap
# in place (frame 0). The sample's own loudest point is placed on that frame (ccut peak_at; samples padded so the
# peak sits on a whole frame, audio/pad_sfx.py).
SND = {"pop": ("pop.wav", 0.24), "coin": ("sfx-coin.wav", 0.22), "chime": ("sfx-chime.wav", 0.16),
       "boom": ("sfx-boom.wav", 0.30), "swish": ("sfx-swish-soft.wav", 0.16), "sparkle": ("sfx-sparkle.wav", 0.14),
       "glitch": ("sfx-glitch.wav", 0.12), "tick": ("sfx-tick.wav", 0.16), "impact": ("sfx-impact.wav", 0.17)}
HIT = {True: 5 / FPS, "in": 5 / FPS, "glow": 6 / FPS, "slide": 7 / FPS, "fade": 0.0, False: 0.0}
hit_of = lambda pop: (0.0 if pop.endswith("_out") else HIT["slide"]) if isinstance(pop, str) and pop.startswith("slide") else HIT.get(pop, 0.1)

def sound_at(kind, at, vol=None, peak=True):
    f, v = SND[kind]
    s = {"path": str(AUD / f), "volume": vol if vol is not None else v}
    s["peak_at" if peak else "start"] = q(at)
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
        print(f"MISSING graphic {name}"); return
    raw_at = cut_at(t, cold) if at is None else at
    at = q(raw_at)
    d = round(q(raw_at + d) - at, 4)
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
    fa, fb = frame_at(a), frame_at(b)
    return 0.0 if fa is None or fb is None else float(np.abs(fa - fb).mean())

def hl(rect, t, d, color=GOLD, sound=True, mt=None):
    """Glowing box around a SOURCE-pixel rect at voice second t, mapped through that piece's punch-in. mt = the
    PICTURE time the rect was measured on (default t + S(t) + 0.1); if the picture under t differs from that frame,
    the box shows when the picture IS that frame (Day 30 lesson 19); held only while the page under it is still."""
    mt = t + S(t) + 0.1 if mt is None else mt
    if pic_jump(mt, t + S(t)) > 1.0:
        t = mt - S(mt)
    i, p = piece_at(t)
    t = max(t, p[0] + 0.02)
    fr = segments[i].get("frame") or {"scale": 1.0, "x": 0.0, "y": 0.0}
    sc, fx, fy = fr.get("scale", 1.0), fr.get("x", 0.0), fr.get("y", 0.0)
    u, v = 0.5 - fx / (2 * sc), 0.5 + fy / (2 * sc)
    l, tp = (u - 0.5 / sc) * W, (v - 0.5 / sc) * H
    x0, y0, x1, y1 = [(rect[0] - l) * sc, (rect[1] - tp) * sc, (rect[2] - l) * sc, (rect[3] - tp) * sc]
    x0, y0, x1, y1 = max(x0, 8), max(y0, 8), min(x1, W - 8), min(y1, H - 8)
    if cam_visible(t, t) and x1 > CAM["rect"][0] - 30 and y1 > CAM["rect"][1] - 30:
        y1 = CAM["rect"][1] - 40         # the box stops above the facecam instead of running under it
    w, h = round(x1 - x0), round(y1 - y0)
    if w < 40 or h < 20:
        print(f"HL OFF-FRAME at {t:.2f} {rect} (frame {fr})"); return
    avail, j = p[1] - t, i
    while avail < d and j + 1 < len(PS) and FRAMES[j + 1] == FRAMES[i] and PS[j + 1][2] == p[2] \
            and jump(PS[j][1] - 0.05, PS[j + 1][0]) < 1.0 and not any(abs(tt - PS[j][1]) < 0.01 for tt in TRANSITIONS):
        j += 1
        avail += PS[j][1] - PS[j][0]
    d = round(min(d, avail), 3)
    # hold only while the page under the box is still: motion inside the box (padded one cell), so the Window's
    # animations and the cursor elsewhere don't count; a scroll reads 4-13, a cursor drifting inside the box 1-3.
    # If he's still finishing a scroll when the line starts, the box waits for the first still frame (up to 2 s),
    # and it never shows for under 1.5 s (accepted rule).
    m = moves(t, t + d + 2.0, rect)
    best = (0, 0)
    for k0 in range(0, min(len(m), 11)):
        if m[k0] is None or m[k0] >= STILL_HL:
            continue
        k = k0
        while k < len(m) and m[k] is not None and m[k] < STILL_HL and (k - k0) / FPS_C < d:
            k += 1
        if (k - k0) / FPS_C >= 1.5:
            best = (k0, k); break
    if best == (0, 0):
        print(f"HL SKIPPED at {t:.2f} {rect}: no 1.5 s still run"); return
    t0_new = t + best[0] / FPS_C
    if t0_new > p[1] - 0.2:
        print(f"HL SKIPPED at {t:.2f} {rect}: still run starts past its piece"); return
    fa, fb = frame_at(mt), frame_at(t0_new + S(t0_new))
    sl = (slice(max(0, rect[1] // 20 - 1), min(108, rect[3] // 20 + 2)), slice(max(0, rect[0] // 20 - 1), min(192, rect[2] // 20 + 2)))
    if fa is not None and fb is not None and float(np.abs(fa[sl] - fb[sl]).mean()) > 2.0:
        print(f"HL SKIPPED at {t:.2f} {rect}: the page under it moved since the measurement frame"); return
    t, d = t0_new, round(min(d, (best[1] - best[0]) / FPS_C, avail - best[0] / FPS_C), 3)
    if d < 1.5:
        print(f"HL SKIPPED at {t:.2f} {rect}: only {d:.2f} s in its pieces"); return
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

# ---- covers and masks (placed first, so they sit on the lowest image tracks under every card) -----------------------
import subprocess as _sp
def _frame_rgb(t_src):
    from PIL import Image as _I
    raw = _sp.run(["ffmpeg", "-v", "error", "-ss", f"{t_src:.3f}", "-i", MAIN, "-frames:v", "1", "-f", "rawvideo",
                   "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return _I.frombytes("RGB", (W, H), raw)

def cover(name, t_still, a_voice, b_pic, cold=False):
    """Full-frame still of the settled page (source picture time t_still) with a hole for the live facecam, from voice
    second a_voice until the PICTURE reaches b_pic (a page-load flash under it)."""
    path = GFX / f"{name}.png"
    if not path.exists():
        im = _frame_rgb(t_still).convert("RGBA")
        hole = _Image.new("L", (W, H), 255)
        x0, y0, x1, y1 = CAM["rect"]
        _Draw.Draw(hole).rounded_rectangle((x0 + 40, y0 + 40, x1 - 40, y1 - 40), radius=24, fill=0)
        im.putalpha(hole); im.save(path)
    a_out = q(cut_at(a_voice, cold))
    b_out = q(cut_at(b_pic - S(b_pic), cold))
    images.append({"path": str(path), "start": a_out, "duration": round(b_out - a_out, 3), "x": W // 2, "y": H // 2,
                   "scale": 1.0, "pop": False})

def mask(name, box, t_src, a_pic, b_pic):
    """Opaque blurred, darkened patch from the frame at t_src over box, while the PICTURE is a_pic..b_pic."""
    path = GFX / f"{name}.png"
    if not path.exists():
        from PIL import ImageEnhance as _En
        fr = _frame_rgb(t_src).crop(box).filter(_Filter.GaussianBlur(48))
        fr = _En.Brightness(fr).enhance(0.55).convert("RGBA")
        m = _Image.new("L", fr.size, 0); _Draw.Draw(m).rounded_rectangle((0, 0, fr.width - 1, fr.height - 1), radius=22, fill=255)
        fr.putalpha(m); fr.save(path)
    a_out, b_out = q(cut_at(a_pic - S(a_pic))), q(cut_at(b_pic - S(b_pic)))
    images.append({"path": str(path), "start": a_out, "duration": round(b_out - a_out, 3),
                   "x": (box[0] + box[2]) // 2, "y": (box[1] + box[3]) // 2, "scale": 1.0, "pop": False})

GFX.mkdir(parents=True, exist_ok=True)
# the grey page load after his click on PaperRows (picture 336.733-337.767), then the page rebuilds its heading and
# upload panel until ~338.75 (Codex audit #2: a 338.10 exit showed the rebuild). The still IS the exit frame, so the
# hand-over to the live page matches (only the hero animation and the facecam move).
cover("cover-site", 338.85, 336.80, 338.85)
# the save dialog shows his OneDrive account name and folder names (picture 400.47-405.2)
mask("mask-savedialog", (0, 0, 1640, 1090), 402.5, 400.40, 405.30)

exec((HERE / "graphics_plan.py").read_text(encoding="utf-8")) if (HERE / "graphics_plan.py").exists() else None
facecam_frame()

FADE = 1.2
if (GFX / "black-4k.png").exists():
    images.append({"path": str(GFX / "black-4k.png"), "start": q(TOTAL - FADE), "duration": FADE, "x": 1920, "y": 1080, "pop": "fade"})
    images.append({"path": str(GFX / "black-4k.png"), "start": q(TOTAL - 0.2), "duration": 0.2, "x": 1920, "y": 1080, "pop": False})
sfx.append({"path": str(AUD / "sfx-swipe.wav"), "peak_at": q(cut_at(TO_SITE)), "volume": 0.12})   # the hard cut onto PaperRows
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
    assert S(seg["in"]) == S(seg["out"] - 1e-6) == sh, f"piece {seg['in']}-{seg['out']} spans a sync section edge"
    if sh:
        seg["in"], seg["out"] = round(seg["in"] + sh, 4), round(seg["out"] + sh, 4)
        seg["av_offset"] = sh            # ccut plays the voice from (in - av_offset): the original voice time
VOICE_FILE = AUD / "voice-main.wav"

edl = {
    "project": "AI Agents Business Ep 3 - Edit",
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
