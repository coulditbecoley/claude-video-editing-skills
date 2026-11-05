"""Edit decisions for the new series, Episode 1: the agents pick a business (OBS take 2026-10-06 11-05-08).

One 37:38 take, paused in OBS between rounds (hard picture jumps at 550, 715, 795, 997, 1235, 1561, 1892,
2030, 2065, 2184). Talking-head intro 0-82, the terminal (Claude left, Codex right, Herdr between them)
83-1891 across six research rounds, Paperclip 1892-2065, the Obsidian "PaperRows" canvas 2065-2184,
talking-head outro 2184-2258. The business they land on is PaperRows (a bank statement converter).

Rules from taste.md (all accepted or confirmed): cold open on the stakes, hook, no captions, static punch-ins
only (CapCut 9.2 ignores video keyframes), fixed facecam overlay, pauses cut only across still screen,
transitions on real screen changes, 40x-style fast-forward for silent waits, calm exit.
Keeps are written as the words he says (start phrase, end phrase); edges snap into the nearest silence.
Graphics and cues are in SOURCE time and mapped onto the edited timeline.
Run: python gen_edl.py  ->  edit.edl.json
"""
import json
import re
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
MAIN = "~/Projects/Youtube/videos/2026-10-06 11-05-08.mp4"
GFX = HERE / "graphics" / "out"
AUD = HERE / "audio"
SFXD = HERE.parent / "2026-10-06 AI Agents" / "audio"     # the licensed ElevenLabs pop / whoosh / impact from Day 13
W, H = 3840, 2160
TAIL, HEAD = 0.14, 0.10

# ---- words and silences -------------------------------------------------------------
_SYN = {"okay": "ok", "codecs": "codex", "alright": "allright"}
_norm = lambda s: _SYN.get(re.sub(r"[^a-z0-9]", "", s.lower()), re.sub(r"[^a-z0-9]", "", s.lower()))
WORDS = [(_norm(w["w"]), w["s"], w["e"]) for s in json.loads((HERE / "main.words.json").read_text(encoding="utf-8"))["segments"]
         for w in s["words"]]
WORDS = [w for w in WORDS if w[0]]

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

def keep(start, end, hint, kind="screen", end_hint=None, at_in=None, at_out=None):
    """at_in / at_out override a snapped edge that catches a neighbouring word (set from isolated snippets)."""
    s, _ = find(start, hint)
    _, e = find(end, end_hint if end_hint is not None else hint, win=90.0)
    return (round(at_in if at_in is not None else snap_in(s), 3), round(at_out if at_out is not None else snap_out(e), 3), kind)

def cutp(start, end, hint):
    """Cut a phrase inside a keep: from just before its first word to just before the word after it."""
    s, e = find(start, hint)
    _, e = find(end, hint)
    nxt = min((w[1] for w in WORDS if w[1] > e - 0.01), default=e + 0.2)
    return (round(s - 0.06, 3), round(nxt - 0.06, 3))

# ---- the edit, in story order ------------------------------------------------------------
KEEPS = [
    # cold open: five rounds of no, then the first (conditional) green light
    keep("codex verdict is affirm nogo", "affirm nogo", 1249, "cold"),
    keep("after four rounds of research", "tools they have today", 1270, "cold"),
    keep("codex verdict is a go with changes", "go with changes", 1586, "cold"),
    keep("the first green light in five rounds", "made the difference", 1591, "cold"),
    # hook and intro (talking head), v2: about 25 s (Codex audit #5)
    keep("five ai agents starting their own business", "here we go", 11, "talk", at_in=11.3),
    keep("in this video were starting a new series", "a business from scratch", 22, "talk"),
    keep("and were going to let them choose what business", "absolutely cant do", 44, "talk"),
    keep("lets get into it", "lets get into it", 79, "talk", at_out=80.45),
    # the ask
    keep("were in our terminal", "what they would like to do", 92, at_in=91.2),
    keep("we are starting a brand new agent run business", "they could conduct now", 149),
    keep("now were not going to get an answer", "that would be profitable", 179),
    # Claude's first ideas (v2: the first wait is cut, not fast-forwarded)
    keep("and we have come back with some research", "or your own website", 243, end_hint=266),
    keep("ranked by opportunities", "over x402", 294, at_in=294.40),
    keep("ok i dont really know anything about that", "know anything about that", 310),
    keep("avoid faceless youtube", "not a steady income", 366),
    keep("exactly", "we learned that on the other one", 386),
    # enter Codex
    keep("so guys this is where we get codex involved", "always agree with each other", 413),
    keep("youre going to see it pop over here", "and there it is", 448, at_in=448.78),
    (460.9, 547.3, "ff"),                                          # Codex auditing (silent), 40x
    # review 1: HVAC alerts, and nobody can find customers
    keep("and the codex audit is complete", "for its own review", 551),
    keep("main conclusion", "sell a subscription first", 583),
    keep("three niches ranked by", "small texas contractors", 607),
    keep("what", "what", 632),
    keep("i dont know how thats going to work out", "going to work out", 636),
    keep("so claude pushed back", "need cold sales for business", 639),
    keep("new prompt for claude", "not the business for us", 662),
    keep("the constraint that decides everything", "personal id and bank account", 729),
    keep("ok well were going to fix that", "access to a stripe account", 736),
    # review 2: website checks, too complicated
    keep("sell a fixed price service through stripe", "through stripe", 810),
    keep("my pick", "accessibility audit", 822),
    keep("i dont know about this", "something more simple", 936),
    # review 3: a $29 kit, and no audience
    keep("codex doesnt launch any of the three as written", "both hold up", 1005),
    keep("the problems cold emails off the table", "theres almost no audience", 1014),
    keep("first a single kit", "a failure being caught", 1028),
    keep("the real problem is now clear", "nobodys around to buy them yet", 1064),
    # review 4: no-go
    keep("codex verdict is affirm nogo", "affirm nogo", 1249),
    keep("the real problems", "no way to reach buyers", 1300, end_hint=1309),
    keep("the agents cost far more than these products would earn", "i still want to give it a try", 1339),
    keep("i dont know i dont really like any of these", "looks good on paper", 1424, at_out=1435.2),   # not the trailing "So"
    # new ground rules (v2: the infrastructure and outage exception is back in, Codex audit #1)
    keep("these business ideas seem convoluted", "taken care of by myself", 1464, end_hint=1512),
    # review 5: the converter, a conditional go
    keep("codex verdict is a go with changes", "made the difference", 1586),
    keep("codex says one small converter", "every task inside the business", 1595),
    keep("the converter runs entirely", "reaches our servers", 1611),
    keep("so tech statements and csvs only at first", "no scan statements", 1629),     # v2: Codex's conditions (audit #2)
    keep("so every value is traced to its source row", "to its source row", 1647),
    keep("the plan", "then a paid download", 1760),
    keep("so this seems like something", "lets just try it", 1816),
    keep("i approve this plan", "to get this started", 1846),
    keep("be sure they come up with the business name", "name the folder after that", 1865),
    keep("so i guess were going to flip on over to paperclip", "lets go", 1885, at_out=1891.8),
    # Paperclip
    keep("all right so we are in paperclip now", "the other business running as well", 1895, at_in=1894.95),
    keep("oh somethings live", "what is wrong with odin", 1940),
    keep("ok so i cleared him and put him back to work", "were going again", 1970),
    keep("so here we are in paperclip", "see what they come up with", 2031),
    # the canvas recap: the plan, build underway
    keep("lets do a quick overview", "in their new business", 2066, at_in=2065.6),
    keep("so what they came up with was a bank statement converter", "it stays on your computer", 2080, end_hint=2106),
    keep("you pay five bucks per report", "a way to take funds", 2117, end_hint=2160),
    keep("first 30 days is going to be a good test", "going to be a good test", 2168, at_out=2170.64),   # v2: not the absolute "zero human help" (Codex audit #1)
    # outro (talking head), v2: one next step, one ask
    keep("first episode complete", "the progress of building it as we speak", 2187, "talk", end_hint=2206),
    keep("were going to keep everything in view", "or if its a bust", 2222, "talk"),
    keep("well be back in episode", "will be up soon", 2240, "talk", end_hint=2252),
]
FF_SPEED = {460.9: 40.0}      # 86.4 s -> 2.2 s (taste: about 40x)
OUTRO = 2180.0
MAX_GAP = 0.4
OUTRO_GAP, OUTRO_TAIL, OUTRO_HEAD = 0.6, 0.2, 0.14

# Stutters inside keeps (source seconds), set after reading the stitched voice transcript.
CUTS = [
    (1470.16, 1470.53),   # "something more less complex" -> "something less complex"
    (1834.95, 1836.08),   # "You know, it might not work." (restarted as "it might not work long term")
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
                best = (run_s, t)
            run_s = None
    return best

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
        if kind != "ff":
            for s, e in SIL:
                outro = s >= OUTRO
                gap, tail, head = (OUTRO_GAP, OUTRO_TAIL, OUTRO_HEAD) if outro else (MAX_GAP, TAIL, HEAD)
                if e - s <= gap or s < a or e > b:
                    continue
                x, y = s + tail, e - head
                if kind != "talk":
                    x, y = still_cut(x, y)
                    if y - x < 0.25:
                        continue
                if x > cur:
                    out.append([cur, x, kind])
                cur = y
        out.append([cur, b, kind])
    return [p for p in out if p[1] - p[0] > 0.05]

PS = pieces()
speed = lambda p: FF_SPEED.get(round(p[0], 1), FF_SPEED.get(p[0], 1.0)) if p[2] == "ff" else 1.0
dur = lambda p: (p[1] - p[0]) / speed(p)

def to_out(t, cold=False):
    """Source second -> edited-timeline second; the cold open reuses source, so it's opt-in."""
    off = 0.0
    for p in PS:
        a, b, kind = p
        if (kind == "cold") == cold and a - 0.4 <= t <= b + 0.4:
            return off + (min(max(t, a), b) - a) / speed(p)
        off += dur(p)
    raise SystemExit(f"source {t} is cut out")

def cut_at(t, cold=False):
    return round(to_out(t, cold), 3)

TOTAL = sum(dur(p) for p in PS)

# ---- facecam and framing ---------------------------------------------------------------
CAM = {"rect": [2920, 1428, 3714, 2034], "clip": str(HERE / "facecam-crop.mp4")}
CX0, CY0 = 2920 / W, 1428 / H
CAM_ON = json.loads((HERE / "cam_on.json").read_text())
cam_visible = lambda a, b: kind_screen(a) and any(x <= a + 0.3 and b - 0.3 <= y for x, y in CAM_ON)
kind_screen = lambda t: 83.0 <= t <= 2181.0

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

# Targeted punch-ins (source in, out, scale, u, v); everything else on the terminal alternates
# full frame / the Claude pane, so a cut on a still terminal reads as a camera cut, not a jump.
ZOOMS = [
    (1940.0, 1950.5, 1.6, 0.15, 0.82),   # "Odin run failed" toast, bottom-left of Paperclip
    (2031.0, 2041.0, 1.4, 0.40, 0.42),   # the new PaperRows project in Paperclip
]
# v2 (Codex audit #8): no alternation. One static 1.5x frame on Claude's pane while he reads its report,
# full frame for prompts, hand-offs and his own reactions between them.
CLAUDE_PANE = (1.5, 0.38, 0.55)
READ = []   # v3 (Coley, 2026-10-07): no terminal zooms. At 1.5x the frame can't hold Claude's whole pane and cut its text off
NO_ALT = [(445.0, 460.9), (1895.0, 2066.0), (2066.0, 2184.0)]   # Herdr hand-off, Paperclip, canvas: full frame unless zoomed

def frame_of(i, p):
    a, b, kind = p
    if kind not in ("screen", "cold"):
        return None
    mid = (a + b) / 2
    w = next((z for z in ZOOMS if z[0] <= mid < z[1]), None)
    if w:
        s, u, v = w[2], w[3], w[4]
    elif kind == "screen" and any(x <= mid < y for x, y in READ):
        s, u, v = CLAUDE_PANE
    else:
        return None
    u, v = allowed(s, u, v) if cam_visible(a, b) else (u, v)
    return to_frame(s, u, v)

# alternate framing at every non-contiguous join inside a screen run
FRAME_ALT, flip = [], False
for i, p in enumerate(PS):
    if i and (PS[i - 1][2] != p[2] or p[2] != "screen"):
        flip = False
    elif i and abs(PS[i - 1][1] - p[0]) > 1e-3:
        flip = not flip
    FRAME_ALT.append(flip)
FRAMES = [frame_of(i, p) for i, p in enumerate(PS)]

# ---- transitions (on the segment that ENDS at this source second) ----------------------
end_of = lambda phrase, hint: [p[1] for p in PS if abs(p[1] - KEEPS[[k for k in range(len(KEEPS))][0]][1]) < 0][0] if False else None
T_COLD_END = KEEPS[3][1]
T_TALK_END = [k for k in KEEPS if k[2] == "talk" and k[1] < 100][-1][1]
T_TERM_END = [k for k in KEEPS if k[2] == "screen" and k[1] < 1892][-1][1]
T_CLIP_END = [k for k in KEEPS if k[2] == "screen" and k[1] < 2066][-1][1]
T_CANVAS_END = [k for k in KEEPS if k[2] == "screen"][-1][1]
TRANSITIONS = {
    T_COLD_END: ("White_Flash", 0.35),
    T_TALK_END: ("Zoom_Transition", 0.6),
    T_TERM_END: ("Swipe_Left", 0.45),       # terminal -> Paperclip
    T_CLIP_END: ("Swipe_Left", 0.45),       # Paperclip -> the canvas
    T_CANVAS_END: ("Zoom_Transition", 0.6), # canvas -> talking-head outro
}
DISSOLVE = ("\u53e0\u5316", 0.3)
ROUND_JUMPS = [550.4, 714.6, 794.8, 996.8, 1561.4]   # not 1235: a hard cut lands the no-go punchline   # OBS resumed: a time skip reads as a soft dissolve
for i in range(len(PS) - 1):
    (a0, b0, k0), (a1, b1, k1) = PS[i], PS[i + 1]
    if k0 == k1 == "screen" and any(b0 <= j <= a1 for j in ROUND_JUMPS) and b0 not in TRANSITIONS and FRAMES[i] == FRAMES[i + 1]:
        TRANSITIONS[b0] = DISSOLVE

segments, talk_i = [], 0
for i, p in enumerate(PS):
    a, b, kind = p
    seg = {"in": round(a, 3), "out": round(b, 3)}
    if kind == "ff":
        seg["speed"] = speed(p)
        seg["mute"] = True
    if kind == "talk":
        if talk_i % 2:
            seg["frame"] = {"scale": 1.12}
        talk_i += 1
    elif FRAMES[i]:
        s_, x_, y_ = FRAMES[i]
        seg["frame"] = {"scale": s_, "x": x_, "y": y_}
        if cam_visible(a, b):
            seg["cam_overlay"] = {**CAM, "k0": 1.0}
    for tt, (name, d) in TRANSITIONS.items():
        if abs(tt - b) < 0.01 and (kind == "cold") == (tt == T_COLD_END):
            seg["transition"] = {"name": name, "duration": d}
    segments.append(seg)

# ---- graphics ------------------------------------------------------------------------------
images, sfx = [], []
MAN = json.loads((GFX / "manifest.json").read_text()) if (GFX / "manifest.json").exists() else {}
TOP_R, TOP_L, STAT, LOW = (3260, 330), (720, 250), (1920, 360), (1920, 1830)

def img(name, t, d, x, y, scale=1.0, sound="pop", at=None, cold=False):
    if name not in MAN:
        return
    at = cut_at(t, cold) if at is None else at
    half = MAN[name]["w"] * scale / 2
    if (x, y) == TOP_L:
        x = round(80 + half)
    elif (x, y) == TOP_R:
        x = round(3760 - half)
    images.append({"path": str(GFX / f"{name}.png"), "start": at, "duration": d, "x": x, "y": y, "scale": scale})
    if sound:
        sfx.append({"path": str(SFXD / ("pop.wav" if sound == "pop" else "sfx-impact.wav")),
                    "start": at, "volume": 0.24 if sound == "pop" else 0.25})

exec((HERE / "graphics_plan.py").read_text(encoding="utf-8")) if (HERE / "graphics_plan.py").exists() else None

FADE = 1.2
images.append({"path": str(GFX / "black-4k.png"), "start": round(TOTAL - FADE, 3), "duration": FADE, "x": 1920, "y": 1080, "pop": "fade"})
images.append({"path": str(GFX / "black-4k.png"), "start": round(TOTAL - 0.2, 3), "duration": 0.2, "x": 1920, "y": 1080, "pop": False})
for t, (name, d) in TRANSITIONS.items():
    if (name, d) != DISSOLVE:
        sfx.append({"path": str(SFXD / "sfx-whoosh.wav"), "peak_at": cut_at(t, cold=(t == T_COLD_END)), "volume": 0.32 if d >= 0.5 else 0.22})

# ---- music --------------------------------------------------------------------------------
BEDS = json.loads((AUD / "beds.json").read_text()) if (AUD / "beds.json").exists() else {}
def bed(name, at, end, target=-30.0):
    b = BEDS[name]
    off = b.get("offset", 0.0)
    return {"path": str(AUD / b["file"]), "at": round(at, 3), "start_offset": off,
            "duration": round(min(end - at, b["length"] - off), 3), "volume": round(10 ** ((target - b["lufs"]) / 20), 3)}

def fill(start, end, names, target=-30.0, fade_out=1.2, fade_in=1.0):
    cues, t, i = [], start, 0
    while end - t > 0.5:
        c = bed(names[i % len(names)], t, end, target)
        c["fade_in"], c["fade_out"] = fade_in, 1.2      # internal bed changes always fade; only the last cue takes fade_out
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
    "project": "AI Agents Business Ep 1 - Edit",
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
print(f"{len(segments)} segments, {TOTAL:.1f}s ({TOTAL/60:.2f} min), {len(images)} images, {len(sfx)} sfx, "
      f"{len(music)} music cues, {sum(1 for s in segments if 'transition' in s)} transitions, "
      f"{sum(1 for s in segments if s.get('frame', {}).get('scale', 1) > 1.13)} punch-ins")
