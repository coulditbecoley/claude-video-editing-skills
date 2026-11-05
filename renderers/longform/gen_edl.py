"""Edit decisions for "3 AI Setups Business Challenge, Video 1" (OBS 2026-11-02 09-39-28 + 2026-11-03 09-35-15,
joined losslessly into D:/edits/0939/src.mp4; part B starts at 1246.45) as an EDL for render_mp4.py (no CapCut).

Source map: talking-head hook 0-92.7; asgardagents.com 92.7-171.8; the kit page 171.8-181.8; Paperclip onboarding
181.8-246.8; the Obsidian overview canvas 246.8-579.6; Paperclip agents 579.6-623.8; desktop 623.8-634 (personal icons:
cut); Hermes and Grok Bot setup 634-675.4; all three ready and the prompts 675.4-807.9; the build, silent, 807.9-1246.45;
part B: talking head 1246.45-1322.3; Home Year (Paperclip) 1322.3-1538.2; First Market Loadout (Hermes) 1538.2-1733.4;
Midnight Workshop (Grok Bot) 1733.4-1912; the three sites side by side 1912-1965.4; talking-head outro 1965.4-2036.7.

Rules from taste.md: cut only pauses, ums, stutters, restarts and true repeats; transitions on real scene changes only;
landing pages (the three sites) full-frame; pause cuts only across a still screen, moving pauses fast-forward; every SFX
on its animation's hit frame; lip sync per unit (60 fps here, since we render ourselves); absolute claims qualified by
the logged human boundary (Build Monitor Log 2026-11-02 and Site Polish Plan in the vault).
Run: python gen_edl.py  ->  edit.edl.json
"""
import json
import os
import re
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
MAIN = "D:/edits/0939/src.mp4"
GFX = HERE / "graphics" / "out"
AUD = HERE / "audio"
W, H = 3840, 2160
FPS = 60
TAIL, HEAD = 0.14, 0.10
q = lambda t: round(round(t * FPS) / FPS, 4)

# ---- words and silences -------------------------------------------------------------
_SYN = {"okay": "ok", "alright": "allright", "gonna": "going", "wanna": "want", "grokbot": "grok", "grogbot": "grok"}
_n0 = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
_norm = lambda s: _SYN.get(_n0(s), _n0(s))
WORDS = [(_norm(w["w"]), w["s"], w["e"]) for s in json.loads((HERE / "main.wav.words.json").read_text(encoding="utf-8"))["segments"]
         for w in s["words"]]
WORDS = [w for w in WORDS if w[0]]
for i in range(len(WORDS) - 2, -1, -1):       # "grok bot" -> "grok"
    if WORDS[i][0] == "grok" and WORDS[i + 1][0] == "bot":
        WORDS[i:i + 2] = [("grok", WORDS[i][1], WORDS[i + 1][2])]


def silences(path):
    t = re.findall(r"silence_(start|end): ([0-9.]+)", path.read_text(errors="ignore"))
    out, cur = [], None
    for kind, v in t:
        if kind == "start":
            cur = float(v)
        elif cur is not None:
            out.append((cur, float(v))); cur = None
    return out


SIL = silences(HERE / "sil40.txt")
import energy as _EN


def _merge_breaths(sil):
    out = []
    for a, b in sil:
        if out and a - out[-1][1] < 0.3 and (a - out[-1][1] < 0.02 or max(_EN.db(out[-1][1], a, 0.01)) < -26):
            out[-1] = (out[-1][0], b)
        else:
            out.append((a, b))
    return out


SIL = _merge_breaths(SIL)


def find(phrase, hint, win=45.0):
    toks = [_norm(t) for t in phrase.split() if _norm(t)]
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


def keep(start, hint, kind="screen", end_hint=None, at_in=None, at_out=None):
    """From the phrase `start` (nearest `hint`) to the last word ending by end_hint (default: the phrase's own end)."""
    s, e = find(start, hint)
    if end_hint is not None:
        e = max(w[2] for w in WORDS if s <= w[1] and w[2] <= end_hint + 0.35)
    return [round(at_in if at_in is not None else snap_in(s), 3), round(at_out if at_out is not None else snap_out(e), 3), kind]


# ---- the edit, in story order ------------------------------------------------------------
# "mont" keeps are picture-only time-lapses of the agents working (muted, MONT_OUT output seconds each).
MONT_OUT = {}


def mont(a, b, out):
    MONT_OUT[(a, b)] = out
    return [a, b, "mont"]


HOOK_IN = float(os.environ.get("HOOK_IN", "8.409125"))   # exactly 72 frames shorter than v3, so the v3 picture after the hook splices on unchanged
KEEPS = [
    # cold open: six hours later, the three products (each line names one)
    keep("everyone stopped at six hours", 1256.0, "cold"),
    keep("home year a 12 month home maintenance planner for homeowners and renters", 1344.6, "cold"),
    keep("first market loadout", 1546.5, "cold"),
    keep("a holiday escape room you can print tonight", 1745.0, "cold"),
    # hook (talking head)
    keep("its time to put grok", 2.7, "talk", end_hint=69.0, at_in=HOOK_IN, at_out=74.05),   # v4: the clean take (a false start "It's time." at 2.56 and a 5 s pause go)
    # 01 the kit: asgardagents.com and the order page
    keep("we are over on the asgardagents", 110.8, end_hint=177.6),
    # 02 Paperclip: a new organization, Claude enters the agents
    keep("but from here", 178.0, end_hint=211.0),
    keep("ok while we wait for the agents", 227.7, end_hint=238.3),
    # 03 the rules (the Obsidian overview the agents built)
    keep("so here we are in obsidian", 250.2, end_hint=571.3),
    # 04 setup: Paperclip's agents, then Hermes and Grok Bot
    keep("lets get back into the creation", 571.6, end_hint=620.0),
    keep("all right we are in hermes", 635.6, end_hint=661.1),
    keep("all right and here we go you can see all three", 676.1, end_hint=807.9),
    # 05 the build: a muted time-lapse of the three teams working (picture only)
    mont(812.0, 822.5, 2.2), mont(900.0, 930.0, 2.6), mont(1000.0, 1060.0, 2.6), mont(1150.0, 1244.0, 3.2),
    # 06 six hours later (talking head)
    keep("and six hours is up", 1251.8, "talk", end_hint=1319.0),
    # 07-09 the three sites
    keep("here we are in the business", 1324.0, end_hint=1536.9),
    keep("here we are this is going to be the hermes", 1540.6, end_hint=1732.9),
    keep("and here we are on the grok project", 1735.3, end_hint=1905.7),   # v3: the second "interesting" goes
    # 10 the prices side by side, then the outro (talking head from 1965.4)
    keep("so paperclip 12", 1908.1, end_hint=1963.0),
    keep("of these items offered", 1967.2, "talk", end_hint=2031.9, at_in=None),
]
COLD_N = 4
OUTRO = 1965.4
# the outro keep starts on "any of these items offered" (the second take): the cut removes the first "any of these items"
KEEPS[-1][0] = round(snap_in(find("any of these items offered", 1964.3)[0]), 3)
KEEPS[-2][1] = round(1961.75, 3)          # "...watching this video need" | (the first "any of these items" is a restart)
KEEPS[4][0] = HOOK_IN                   # unrounded, so the shortening is a whole number of frames
KEEPS[6][0] = KEEPS[5][1]               # "...grab the Asgard Agent Kit." | "But from here" (contiguous; no overlap)
LANDING = [(1322.3, 1912.0)]              # the sites play full-frame: pauses only over 1.2 s, and only while still
MAX_GAP = 0.4
FF_MIN, FF_OUT, FF_MAX = 0.55, 0.35, 3.0
OUTRO_GAP, OUTRO_TAIL, OUTRO_HEAD = 0.6, 0.2, 0.14

exec((HERE / "cuts.py").read_text(encoding="utf-8"))
CUTS = globals().get("CUTS", [])

# ---- what the screen does (frames5.npy, 5 fps, 192x108 grey, facecam and nothing else masked) ----------------------
FPS_C = 5
_F = np.load("D:/edits/0939/frames5.npy")


def frame_at(t):
    i = round(t * FPS_C)
    if 0 <= i < len(_F):
        a = _F[i].astype(np.int16)
        a[70:103, 145:188] = 0
        return a
    return None


# Lip sync (sync_map.py): picture time = voice time + S(voice time), S piecewise linear, changing only inside pauses.
_SC = json.loads((HERE / "sync_curve.json").read_text())["points"] if (HERE / "sync_curve.json").exists() else [[0.0, 0.0]]
_SCT, _SCV = np.array([p[0] for p in _SC]), np.array([p[1] for p in _SC])


def S(t):
    return float(np.interp(t, _SCT, _SCV))


def pic_map(a, b):
    """[[voice_t, picture_t], ...] for a piece: its ends plus every curve point inside."""
    pts = [[round(a, 4), round(a + S(a), 4)]]
    pts += [[round(float(t), 4), round(float(t + v), 4)] for t, v in zip(_SCT, _SCV) if a < t < b]
    pts.append([round(b, 4), round(b + S(b), 4)])
    return pts


def moves(t0, t1, rect=None):
    sh = S(t0)
    t0, t1 = t0 + sh, t1 + sh
    sl = (slice(None), slice(None)) if rect is None else \
        (slice(max(0, rect[1] // 20 - 1), min(108, rect[3] // 20 + 2)), slice(max(0, rect[0] // 20 - 1), min(192, rect[2] // 20 + 2)))
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
    if all(v is not None and v < STILL for v in m) and jump(a, b) < STILL:
        return (a, b)
    best, run_s = (a, a), None
    for i, v in enumerate(m + [99.0]):
        t = a + i / FPS_C
        if v is None or v < STILL:
            run_s = t if run_s is None else run_s
        else:
            if run_s is not None and t - run_s > best[1] - best[0]:
                best = (run_s + (0.2 if run_s > a else 0.0), t)
            run_s = None
    return best


# Real page changes inside a keep (PICTURE seconds, frames5 diff peaks): the piece splits on that frame and the
# transition lands on it (confirmed rule). A change inside a pause keeps SPLIT_KEEP of the pause around it.
SCENES = [
    (171.80, "Swipe_Left", 0.4),          # asgardagents.com -> the kit's order page ("This is the screen")
    (181.80, "Swipe_Left", 0.4),          # -> Paperclip, new organization ("go and set up paperclip.ai")
    (579.60, "Swipe_Left", 0.4),          # Obsidian -> back in Paperclip (inside the pause before "Here we are back")
]
SPLITS = [round(p - S(p - S(p)), 3) for p, *_ in SCENES]
SCENE_AT = SPLITS
SPLIT_KEEP = (0.45, 0.55)
JUMPY = set()

exec((HERE / "zooms.py").read_text(encoding="utf-8")) if (HERE / "zooms.py").exists() else None
ZOOMS = globals().get("ZOOMS", [])
SCREEN_KINDS = ("screen", "cold")


def landing(t):
    return any(a <= t <= b for a, b in LANDING)


def pieces():
    spans = []
    for a, b, kind in KEEPS:
        if kind == "mont":
            spans.append((a, b, kind)); continue
        cur = a
        for ca, cb in sorted(CUTS):
            if a < ca < b:
                spans.append((cur, ca, kind)); cur = cb
        spans.append((cur, b, kind))
    out = []
    for a, b, kind in spans:
        if kind == "mont":
            out.append([a, b, kind]); continue
        cur = a
        for s, e in SIL:
            outro = s >= OUTRO
            gap, tail, head = (OUTRO_GAP, OUTRO_TAIL, OUTRO_HEAD) if outro else (MAX_GAP, TAIL, HEAD)
            if kind == "screen" and landing(s):
                gap = 1.2
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
                sx, sy = still_cut(x, y)
                ok = sy - sx >= 0.25 and jump(sx, sy) <= 2.0
                for k, (m0, m1) in enumerate([(x, sx), (sy, y)] if ok else [(x, y)]):
                    if m1 - m0 > FF_MIN and m0 >= cur:
                        if m0 > cur:
                            out.append([cur, m0, kind])
                        out.append([m0, m1, "ff"])
                        cur = m1
                    if ok and k == 0:
                        if sx > cur:
                            out.append([cur, sx, kind])
                        cur = max(cur, sy)
                continue
            if x > cur:
                out.append([cur, x, kind])
            cur = y
        out.append([cur, b, kind])
    res = []
    for a, b, kind in out:
        edges = SPLITS + ([e for w in ZOOMS for e in w[:2]] if kind in SCREEN_KINDS else [])
        cuts = sorted(c for c in set(edges) if a + 0.3 < c < b - 0.3)
        for x, y in zip([a] + cuts, cuts + [b]):
            res.append([x, y, kind])
    return [p for p in res if p[1] - p[0] > 0.05]


PS = pieces()
_ff_out = lambda p: round((p[1] - p[0]) / min(FF_MAX, max(1.5, (p[1] - p[0]) / FF_OUT)), 3)


def spd(p):
    if p[2] == "ff":
        return (p[1] - p[0]) / _ff_out(p)
    if p[2] == "mont":
        return (p[1] - p[0]) / MONT_OUT[(p[0], p[1])]
    return 1.0


dur = lambda p: (p[1] - p[0]) / spd(p)


def to_out(t, cold=False):
    off = 0.0
    for p in PS:
        a, b, kind = p
        if (kind == "cold") == cold and a - 0.4 <= t <= b + 0.4:
            return off + (min(max(t, a), b) - a) / spd(p)
        off += dur(p)
    raise SystemExit(f"source {t} is cut out")


def cut_at(t, cold=False):
    return round(to_out(t, cold), 3)


TOTAL = sum(dur(p) for p in PS)

# ---- facecam and framing ---------------------------------------------------------------
CAM = {"rect": [2920, 1428, 3714, 2034]}
CX0, CY0 = 2920 / W, 1428 / H
TH = json.loads((HERE / "th_ranges.json").read_text())
is_talk_t = lambda t: any(a <= t <= b for a, b in TH)
is_screen_t = lambda t: not is_talk_t(t)
cam_visible = lambda a, b: is_screen_t(a) and is_screen_t(b)


def allowed(s, u, v):
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


def frame_of(i, p):
    a, b, kind = p
    if kind not in SCREEN_KINDS:
        return None
    mid = (a + b) / 2
    w = next((z for z in ZOOMS if z[0] <= mid < z[1]), None)
    if w:
        u, v = allowed(w[2], w[3], w[4])
        return to_frame(w[2], u, v)
    return None


FRAMES = [frame_of(i, p) for i, p in enumerate(PS)]


def end_of(i):
    a, b, kind = KEEPS[i]
    return max(p[1] for p in PS if p[2] == kind and a - 1e-3 <= p[0] < b and p[1] <= b + 1e-3)


def last_piece_end_before(t):
    return max(p[1] for p in PS if p[1] <= t + 1e-3 and p[2] != "cold")


T_COLD_END = end_of(COLD_N - 1)
# Transitions keyed on the source second a piece ENDS (non-cold pieces unless the key is the cold open's end).
TRANSITIONS = {T_COLD_END: ("White_Flash", 0.4)}
for i in range(COLD_N - 1):
    TRANSITIONS[end_of(i)] = ("Flash_Cut", 0.18)          # the cold open's beats: a short bloom between them
_K = lambda i: end_of(i)
TRANSITIONS.update({
    _K(4): ("Zoom_Transition", 0.5),   # the hook (camera) -> asgardagents.com
    _K(6): ("Flash_Cut", 0.25),        # "we'll be back" -> "while we wait" (a time skip on the same page)
    _K(7): ("Swipe_Left", 0.45),       # -> Obsidian
    _K(9): ("Swipe_Left", 0.4),        # Paperclip -> Hermes
    _K(10): ("Swipe_Left", 0.4),       # Hermes + Grok Bot setup -> all three ready
    _K(11): ("Light_Leaks", 0.8),      # the prompts fire -> the build time-lapse
    _K(12): ("Dissolve", 0.3), _K(13): ("Dissolve", 0.3), _K(14): ("Dissolve", 0.3),
    _K(15): ("Zoom_Transition", 0.5),  # the time-lapse -> six hours later (camera)
    _K(16): ("Light_Leaks", 0.8),      # -> the first site (the big reveal)
    _K(17): ("Swipe_Left", 0.45),      # Home Year -> First Market Loadout
    _K(18): ("Swipe_Left", 0.45),      # -> Midnight Workshop
    _K(20): ("Zoom_Transition", 0.5),  # the three sites -> the camera outro
})
for v, (p, name, d) in zip(SCENE_AT, SCENES):
    if any(a <= v <= b for a, b, k in KEEPS if k == "screen"):
        ends = [q_[1] for q_ in PS if q_[2] == "screen"]
        near = min(ends, key=lambda e: abs(e - v))
        TRANSITIONS[near if abs(near - v) < 0.35 else v] = (name, d)   # a change right at a pause cut lands on that cut
WHOOSH = {"White_Flash": "sfx-whoosh-air", "Flash_Cut": "sfx-whoosh-air", "Zoom_Transition": "sfx-whoosh-air",
          "Swipe_Left": "sfx-swipe", "Swipe_Up": "sfx-swipe", "Light_Leaks": "sfx-riser-air", "Dissolve": "sfx-whoosh-air"}

segments, talk_i = [], 0
for i, p in enumerate(PS):
    a, b, kind = p
    seg = {"in": round(a, 3), "out": round(b, 3), "kind": kind}
    if kind in ("ff", "mont"):
        seg["speed"], seg["mute"] = spd(p), True
    if kind == "talk" and a >= OUTRO:
        seg["still"] = True              # the outro holds one framing, no push (confirmed calm exit; Codex #10)
    elif kind == "talk" or (kind == "cold" and is_talk_t(a)):
        if dur(p) >= 1.2 or i == 0 or PS[i - 1][2] != "talk":
            talk_i += 1
        if talk_i % 2 == 0:
            seg["frame"] = {"scale": 1.12}
    elif FRAMES[i]:
        s_, x_, y_ = FRAMES[i]
        seg["frame"] = {"scale": s_, "x": x_, "y": y_}
        if cam_visible(a, b):
            seg["cam_overlay"] = {"rect": CAM["rect"]}
    for tt, (name, d) in TRANSITIONS.items():
        if abs(tt - b) < 0.01 and ((kind == "cold") == (tt == T_COLD_END or any(abs(tt - end_of(j)) < 0.01 for j in range(COLD_N - 1)))):
            seg["transition"] = {"name": name, "duration": d}
    segments.append(seg)

# ---- graphics and sound -------------------------------------------------------------------
images, sfx = [], []
MAN = json.loads((GFX / "manifest.json").read_text()) if (GFX / "manifest.json").exists() else {}
if os.environ.get("GFX_STUB"):      # phrase/timing check before the graphics exist
    import collections
    MAN = collections.defaultdict(lambda: {"w": 1200, "h": 500, "frames": 50, "hit": 0.12}, MAN)
SND = {"pop": ("pop.wav", 0.22), "coin": ("sfx-coin.wav", 0.14), "chime": ("sfx-chime.wav", 0.15),
       "boom": ("sfx-boom.wav", 0.28), "swish": ("sfx-swish-soft.wav", 0.15), "sparkle": ("sfx-sparkle.wav", 0.13),
       "tick": ("sfx-tick.wav", 0.14), "impact": ("sfx-impact.wav", 0.17), "riser": ("sfx-riser.wav", 0.12),
       "whoosh": ("sfx-whoosh-air.wav", 0.18), "type": ("sfx-tick.wav", 0.06)}
# animation hit offsets in render_mp4.py (seconds after the image start): the SFX peak lands here
HIT = {True: 0.133, "in": 0.133, "glow": 0.067, "slide": 0.100, "fade": 0.0, False: 0.0}
hit_of = lambda pop: (0.0 if pop.endswith("_out") else HIT["slide"]) if isinstance(pop, str) and pop.startswith("slide") else HIT.get(pop, 0.1)


def sound_at(kind, at, vol=None, peak=True):
    f, v = SND[kind]
    s = {"path": str(AUD / f), "volume": vol if vol is not None else v}
    s["peak_at" if peak else "start"] = q(at)
    sfx.append(s)


def img(name, t, d, x, y, scale=1.0, sound="pop", at=None, cold=False, pop=True, vol=None, seq=None):
    if name not in MAN:
        print(f"MISSING graphic {name}"); return
    raw_at = cut_at(t, cold) if at is None else at
    at = q(raw_at)
    d = round(q(raw_at + d) - at, 4)
    im = {"path": str(GFX / f"{name}.png"), "start": at, "duration": d, "x": x, "y": y, "scale": scale, "pop": pop}
    if MAN[name].get("frames"):
        im["seq"] = {"dir": str(GFX / name), "frames": MAN[name]["frames"]}
    images.append(im)
    if sound:
        sound_at(sound, at + (MAN[name].get("hit", hit_of(pop)) if MAN[name].get("frames") else hit_of(pop)), vol)
    return im


from PIL import Image as _Image, ImageDraw as _Draw, ImageFilter as _Filter
import subprocess as _sp


def _frame_rgb(t_src):
    raw = _sp.run(["ffmpeg", "-v", "error", "-ss", f"{t_src:.3f}", "-i", MAIN, "-frames:v", "1", "-f", "rawvideo",
                   "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return _Image.frombytes("RGB", (W, H), raw)


def mask(name, box, t_src, a_pic, b_pic, cold=False):
    """Opaque blurred, darkened patch from the frame at t_src over box, while the PICTURE is a_pic..b_pic."""
    path = GFX / f"{name}.png"
    if not path.exists():
        from PIL import ImageEnhance as _En
        fr = _frame_rgb(t_src).crop(box).filter(_Filter.GaussianBlur(48))
        fr = _En.Brightness(fr).enhance(0.55).convert("RGBA")
        m = _Image.new("L", fr.size, 0); _Draw.Draw(m).rounded_rectangle((0, 0, fr.width - 1, fr.height - 1), radius=22, fill=255)
        fr.putalpha(m); fr.save(path)
    def _o(t):      # a mask edge that falls in a cut takes the nearest kept second
        v = t - S(t)
        p = min((p for p in PS if (p[2] == "cold") == cold), key=lambda p: 0 if p[0] <= v <= p[1] else min(abs(v - p[0]), abs(v - p[1])))
        return cut_at(min(max(v, p[0]), p[1]), cold)
    a_out, b_out = q(_o(a_pic)), q(_o(b_pic)) + 2 / FPS      # v3 (Codex #6): end outward, never a frame short of the cut
    images.append({"path": str(path), "start": a_out, "duration": round(b_out - a_out, 3),
                   "x": (box[0] + box[2]) // 2, "y": (box[1] + box[3]) // 2, "scale": 1.0, "pop": False, "under": True})


GFX.mkdir(parents=True, exist_ok=True)
exec((HERE / "graphics_plan.py").read_text(encoding="utf-8")) if (HERE / "graphics_plan.py").exists() else None

FADE = 1.2
if (GFX / "black-4k.png").exists():
    images.append({"path": str(GFX / "black-4k.png"), "start": q(TOTAL - FADE), "duration": FADE, "x": 1920, "y": 1080, "pop": "fade"})
_cold_keys = {end_of(j) for j in range(COLD_N)}
for t, (name, d) in TRANSITIONS.items():
    wf = WHOOSH[name]
    if not (AUD / f"{wf}.wav").exists():
        wf = "sfx-whoosh-air"
    vol = {"sfx-whoosh-air": 0.24, "sfx-swipe": 0.17, "sfx-riser-air": 0.2}.get(wf, 0.2)
    if name == "Flash_Cut":
        vol = 0.12
    if name == "Dissolve":
        vol = 0.06                       # v3 (Codex #15): the time-lapse steps stay quiet
    sfx.append({"path": str(AUD / f"{wf}.wav"), "peak_at": q(cut_at(t, cold=(t in _cold_keys))), "volume": vol})

# ---- music ----------------------------------------------------------------------------------
BEDS = json.loads((AUD / "beds.json").read_text()) if (AUD / "beds.json").exists() else {}


MUSIC_GAIN_DB = 2.5     # v4 (Coley): "slightly increase the background music"
SFX_GAIN = 10 ** (2.0 / 20)   # v4 (Coley): "and sound effects", +2 dB


def bed(name, at, end, target=-32.0, offset=None):
    b = BEDS[name]
    off = b.get("offset", 0.0) if offset is None else offset
    return {"path": str(AUD / b["file"]), "at": round(at, 3), "start_offset": off,
            "duration": round(min(end - at, b["length"] - off), 3), "volume": round(10 ** ((target + MUSIC_GAIN_DB - b["lufs"]) / 20), 3)}


music = []
if BEDS and (HERE / "music_plan.py").exists():
    exec((HERE / "music_plan.py").read_text(encoding="utf-8"))
(AUD / "music-cues.json").write_text(json.dumps(music, indent=1), encoding="utf-8")
_stem = AUD / "music-stem.json"
if os.environ.get("MUSIC_STEM", "1") == "1" and _stem.exists():
    _st = json.loads(_stem.read_text())
    if abs(_st["total"] - TOTAL) < 0.02:
        music = [{"path": str(AUD / "music-stem.wav"), "at": 0.0, "start_offset": 0.0, "duration": round(TOTAL, 3), "volume": 1.0}]
    else:
        print(f"MUSIC STEM STALE ({_st['total']} vs {TOTAL:.3f}): run verify_voice.py and mix_stem.py, then gen_edl.py again")

for seg, p in zip(segments, PS):
    seg["pic"] = pic_map(p[0], p[1])     # render_mp4.py reads the picture through this map; the voice plays at in..out

for _s in sfx:
    _s["volume"] = round(_s["volume"] * SFX_GAIN, 4)
edl = {"project": "3 AI Setups Challenge - Video 1", "output": os.environ.get("OUT_NAME", "3 AI Setups Challenge Video 1 - 4K60.mp4"), "source": MAIN, "resolution": [W, H], "fps": FPS,
       "voice": {MAIN: str(AUD / "voice-main.wav")}, "segments": segments, "images": images, "sfx": sfx, "music": music}
(HERE / "edit.edl.json").write_text(json.dumps(edl, indent=1), encoding="utf-8")
if __name__ == "__main__":
    print(f"{len(segments)} segments, {TOTAL:.1f}s ({TOTAL / 60:.2f} min), {len(images)} images, {len(sfx)} sfx, "
          f"{len(music)} music cues, {sum(1 for s in segments if 'transition' in s)} transitions "
          f"(of {len(TRANSITIONS)} planned)")
