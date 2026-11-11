"""Edit decisions for "5 AI agents, $50, one job" (Day 1), as a ccut EDL.

Story spans are picked from the word-level transcript; inside each span every
silence longer than 0.7s collapses to a 0.35s breath (profiles/youtube.md).
Graphics, zooms and transitions are written in SOURCE time and mapped onto the
edited timeline here, so a trim change never leaves a logo on the wrong word.
Run: python gen_edl.py  ->  edit.edl.json
"""
import json
import os
import re
from pathlib import Path

HERE = Path(__file__).parent
V = os.environ.get("EDIT_SRC_DIR", "~/Projects/Youtube/videos")   # pod: /workspace/edits/<job>/src
MAIN = f"{V}/2026-09-25 12-34-31.mp4"
OUTRO = f"{V}/2026-09-25 12-46-15.mp4"
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

SIL = {MAIN: silences(HERE / "silences-main-fine.txt"), OUTRO: silences(HERE / "silences-outro-fine.txt")}

# (source, in, out, kind). kind: "talk" = talking head (gets punch-ins), "screen".
SPANS = [
    (MAIN, 2.45, 13.55, "talk"),      # cold open: "I gave five AI agents..."
    (MAIN, 18.55, 29.05, "talk"),     # "...inside the Paperclip AI workforce" (slow "work... force")
    (MAIN, 55.75, 70.2, "talk"),      # "I'm going to show you how we've set up..." -> "Let's go."
    (MAIN, 86.0, 196.35, "screen"),   # canvas: council + loop (skips the false start at 78s)
    (MAIN, 203.4, 407.8, "screen"),   # loop cont. + rules (skips the "inappropriate" stumble)
    (MAIN, 412.55, 620.55, "screen"),  # Paperclip + X account (drops "All right.")
    (MAIN, 624.05, 635.1, "screen"),  # "the very first post..." (drops "So, yeah, here's this and")
    (OUTRO, 1.0, 9.6, "talk"),        # outro take 2 (take 1 was partial)
]
CAM = {"rect": [2920, 1428, 3714, 2034], "clip": str(HERE / "facecam-crop.mp4")}   # facecam box in the recording (measured) + that box cropped to its own clip
CAM_GROW = {1.4: 1.21}                                   # council zoom: cam grows to cover the zoomed copy
DRIFT = 0.05   # zoom holds push in 5% over their length (wiki: zoom drift keeps still shots alive)
MAX_GAP, KEEP = 0.4, 0.24   # tight long-form pacing (AI Video Editing wiki: Jowett ~0.2s)

# Semantic cuts (source seconds): lines that restate the one beside them, and stumbles.
CUTS = {MAIN: [
    (96.62, 102.5),    # "I'm going to show you what they do... their plan on creating a profit" (restates the line before)
    (107.0, 111.08),   # "That's what I do for all of my agents. And here are the same ones. I always lay them out."
    (159.55, 164.26),  # "So it's semi simple, I guess, but we're going to go over it one by one."
    (176.4, 177.3),    # "So that's their goal."
    (204.3, 206.1),    # false start "They launch," (found by the literal re-transcription)
    (284.0, 287.04),   # "Up next, pretty much what we just said,"
    (419.3, 424.13),   # "There are plenty to see and to get an idea of what it does."
    (509.1, 511.18),   # "So they are just waiting right now." (next line says it)
    (593.34, 594.72),  # the doubled "to" in "tell them to to do anything"
    (600.2, 604.09),   # "They have already released this bulk token. Well," (he corrects it: promoting)
]}

def pieces():
    out = []
    spans = []
    for src, a, b, kind in SPANS:
        cur = a
        for ca, cb in sorted(CUTS.get(src, [])):
            if a < ca < b:
                spans.append((src, cur, ca, kind)); cur = cb
        spans.append((src, cur, b, kind))
    for src, a, b, kind in spans:
        cur = a
        for s, e in SIL[src]:
            if e - s <= MAX_GAP or s < a or e > b:
                continue
            if s + KEEP / 2 > cur:
                out.append([src, cur, s + KEEP / 2, kind])
            cur = e - KEEP / 2
        out.append([src, cur, b, kind])
    return [p for p in out if p[2] - p[1] > 0.05]

# Split points (source) so zooms/transitions get their own segment.
SPLITS = {MAIN: [8.57, 12.3, 59.55, 63.44, 110.3, 155.6, 330.3, 385.3, 494.3, 501.2, 577.8, 596.3, 599.8],
          OUTRO: [4.05, 5.85]}  # sentence gaps: extra punch-in cuts on the talking head

def split(ps):
    out = []
    for src, a, b, kind in ps:
        cuts = [c for c in SPLITS.get(src, []) if a < c < b]
        for x, y in zip([a] + cuts, cuts + [b]):
            out.append([src, x, y, kind])
    return out

PS = split(pieces())

def to_out(src, t):
    """Source second -> edited-timeline second (snaps into the nearest kept piece)."""
    off = 0.0
    best = None
    for s, a, b, _ in PS:
        if s == src and a - 0.4 <= t <= b + 0.4:
            return off + min(max(t, a), b) - a
        off += b - a
    raise SystemExit(f"source {t} of {Path(src).name} is cut out")

# Zooms (source windows) -> scale + centre of interest (u, v as fractions of the frame).
ZOOMS = [
    (110.3, 155.6, 1.4, 0.525, 0.36),   # the council cards while each agent is named
    (330.3, 385.3, 1.5, 0.34, 0.45),   # the rules panel
    (494.3, 501.2, 1.6, 0.68, 0.33),   # aimed high so the zoomed facecam falls off the bottom   # Paperclip: the blocked column (tonight's launch)
    (596.3, 599.8, 1.6, 0.49, 0.32),   # X banner + avatar they chose
]

def zoom_for(src, a, b):
    for za, zb, s, u, v in ZOOMS:
        if src == MAIN and a >= za - 1e-6 and b <= zb + 1e-6:
            return {"scale": s, "x": round((0.5 - u) * 2 * s, 4), "y": round((v - 0.5) * 2 * s, 4), "ramp": 0.6}
    return None

# Transitions go on the segment that ENDS at this source second.
TRANSITIONS = {
    (MAIN, 13.55): ("White_Flash", 0.35),       # hook -> intro
    (MAIN, 70.2): ("Zoom_Transition", 0.6),     # talking head -> screen
    (MAIN, 407.8): ("Swipe_Left", 0.6),         # canvas -> Paperclip
    (MAIN, 577.8): ("Swipe_Left", 0.6),         # Paperclip -> X
    (MAIN, 635.1): ("Zoom_Transition", 0.6),    # screen -> outro
}

segments, talk_i = [], 0
for src, a, b, kind in PS:
    seg = {"in": round(a, 3), "out": round(b, 3)}
    if src != MAIN:
        seg["source"] = src
    if kind == "talk":
        # alternate framing on every talking-head cut: a punch-in hides the jump
        if talk_i % 2:
            seg["frame"] = {"scale": 1.12}
        talk_i += 1
    z = zoom_for(src, a, b)
    if z:
        # one continuous camera move across all pieces of a zoom window:
        # first ramps in, middle ones hold, last ramps out
        win = [p for p in PS if p[0] == src and zoom_for(p[0], p[1], p[2]) == z]
        first, last = win[0][1] == a, win[-1][2] == b
        hold = [p for p in win[1:-1]]
        hold_len = sum(p[2] - p[1] for p in hold) or 1.0   # not H: that's the canvas height
        done = sum(p[2] - p[1] for p in hold if p[2] <= a)          # hold time before this piece
        at = lambda frac: 1 + DRIFT * frac                           # drift factor at a point in the hold
        k = lambda f: {"s": round(z["scale"] * f, 4), "x": round(z["x"] * f, 4), "y": round(z["y"] * f, 4)}
        if last and not first:
            seg["zoom"] = {**z, **{kk: v for kk, v in zip(("scale", "x", "y"), k(at(1)).values())}, "in": False, "out": True}
        elif first:
            seg["zoom"] = {**z, "in": True, "out": last}
        else:
            f0, f1 = at(done / hold_len), at((done + b - a) / hold_len)
            seg["frame"] = {"scale": z["scale"], "x": z["x"], "y": z["y"]}
            seg["drift"] = {"s0": k(f0)["s"], "x0": k(f0)["x"], "y0": k(f0)["y"], "s1": k(f1)["s"], "x1": k(f1)["x"], "y1": k(f1)["y"]}
    if z:
        # keep the recorded facecam whole over the zoom (see CAM); only the council zoom,
        # too wide to push the cam off-screen, grows the cam to cover the zoomed copy
        grow = CAM_GROW.get(z["scale"], 1.0)
        d = b - a; r = min(0.6, d / 3) / d
        if first and last:
            seg["cam_overlay"] = {**CAM, "keys": [(0, 1.0), (r, grow), (1 - r, grow), (1, 1.0)]}
        elif first:
            seg["cam_overlay"] = {**CAM, "keys": [(0, 1.0), (r, grow), (1, grow)]}
        elif last:
            seg["cam_overlay"] = {**CAM, "keys": [(0, grow), (1 - r, grow), (1, 1.0)]}
        else:
            seg["cam_overlay"] = {**CAM, "k0": grow}
    elif kind == "screen" and "frame" not in seg and b - a > 6:
        seg["drift"] = {"s0": 1.0, "s1": 1.035}                      # still screen shot: slow push
    for (ts, tt), (name, d) in TRANSITIONS.items():
        if ts == src and abs(tt - b) < 0.01:
            seg["transition"] = {"name": name, "duration": d}
    segments.append(seg)
TOTAL = sum(s["out"] - s["in"] for s in segments)

def cut_at(src, t):
    return round(to_out(src, t), 3)

# ---- graphics -------------------------------------------------------------
images, sfx = [], []
def img(name, src, t, dur, x, y, scale=1.0, sound="pop"):
    at = cut_at(src, t)
    images.append({"path": str(GFX / f"{name}.png"), "start": at, "duration": dur, "x": x, "y": y, "scale": scale})
    if sound:
        sfx.append({"path": str(AUD / ("pop.mp3" if sound == "pop" else "sfx-impact.mp3")),
                    "start": at, "volume": 0.3 if sound == "pop" else 0.5})

TOP_R = (3260, 330)          # logo pop-ups on the screen sections
TOP_L = (720, 250)           # section chips
STAT = (1920, 360)           # big number callouts

for i, n in enumerate(["odin", "thor", "loki", "mimir", "heimdall"]):
    img(f"agent-{n}", MAIN, 3.46 + i * 0.12, 2.9 - i * 0.12, 1920 + (i - 2) * 650, 400, scale=1.3, sound="pop" if i == 0 else None)
img("logo-x", MAIN, 6.58, 2.5, 3180, 820)
img("hook-title", MAIN, 7.8, 3.4, 1920, 300)       # on "one job"
img("logo-paperclip", MAIN, 24.94, 3.0, 3150, 420)
img("logo-obsidian", MAIN, 87.26, 3.0, *TOP_R)
img("chip-council", MAIN, 102.8, 3.4, *TOP_L)
img("chip-loop", MAIN, 156.7, 3.4, *TOP_L)
img("stat-daily", MAIN, 243.0, 3.6, *STAT)
img("logo-x", MAIN, 249.16, 3.0, *TOP_R)
img("stat-broke", MAIN, 293.0, 3.2, *STAT, sound="hit")
img("chip-rules", MAIN, 303.95, 3.4, *TOP_L)
img("logo-ethereum", MAIN, 322.7, 3.2, *TOP_R)
img("stat-bank", MAIN, 322.9, 3.4, *STAT, sound=None)
img("stat-max", MAIN, 331.2, 3.4, *STAT)
img("stat-fees", MAIN, 344.88, 3.4, *STAT)
img("handle-asgard", MAIN, 393.5, 4.0, 1920, 1560)
img("chip-paperclip", MAIN, 413.4, 3.4, *TOP_L)
img("logo-paperclip", MAIN, 413.18, 3.0, *TOP_R)
img("vs-providers", MAIN, 436.4, 7.2, 1920, 900)          # VS_SPLIT: why the council is split across providers
img("chip-x", MAIN, 579.6, 3.4, *TOP_L)
img("stat-day1", MAIN, 628.4, 3.6, *STAT)
img("coin-bulk", MAIN, 530.0, 3.6, 3175, 330)             # IMAGE_CARD: the real $BULK logo
img("coin-emu", MAIN, 612.88, 5.0, 3215, 330)             # IMAGE_CARD: $EMU, "not an ostrich"
# PROGRESS_STEPS: the daily loop, current step lit as he reaches it
STEP_AT = [164.9, 180.62, 190.12, 206.16, 246.52, 269.7, 287.08, 297.5, 299.9]
for k in range(8):
    a, b = cut_at(MAIN, STEP_AT[k]), cut_at(MAIN, STEP_AT[k + 1])
    images.append({"path": str(GFX / f"steps-{k + 1}.png"), "start": a, "duration": round(b - a, 3),
                   "x": 1357, "y": 1942, "scale": 0.85, "pop": "in" if k == 0 else ("out" if k == 7 else False)})
sfx.append({"path": str(AUD / "pop.mp3"), "start": cut_at(MAIN, STEP_AT[0]), "volume": 0.3})
img("cta-subscribe", OUTRO, 3.1, 3.4, 1920, 1620)
img("handle-asgard", OUTRO, 4.3, 4.2, 1920, 330)
# fade to black over the last 0.45 s, as a black overlay (an opacity keyframe on the main clip hung the export)
images.append({"path": str(GFX / "black-4k.png"), "start": round(TOTAL - 0.45, 3), "duration": 0.45, "x": 1920, "y": 1080, "pop": "fade"})

# whoosh peak on every transition cut; a hit + dead music on "game over"
for (src, t), _ in TRANSITIONS.items():
    sfx.append({"path": str(AUD / "sfx-whoosh.mp3"), "peak_at": cut_at(src, t), "volume": 0.38})

# ---- music: a new bed per section, cut dead on the "game over" line ----------
def lufs_vol(track, lufs, target=-30.0):
    return round(10 ** ((target - lufs) / 20), 3)
BEDS = {"jonas": (AUD / "music-jonas.mp3", -8.9, 136.9), "verclub": (AUD / "music-verclub.mp3", -7.6, 130.3),
        "vaitsez": (AUD / "music-vaitsez.mp3", -8.2, 174.4)}
def bed(name, at, end, target=-30.0, offset=0.0):
    path, lufs, length = BEDS[name]
    return {"path": str(path), "at": round(at, 3), "start_offset": offset,
            "duration": round(min(end - at, length - offset), 3), "volume": lufs_vol(name, lufs, target)}

t_screen = cut_at(MAIN, 86.0)
t_broke = cut_at(MAIN, 294.95)      # "...this entire experiment is over."
t_resume = cut_at(MAIN, 297.5)      # "Tomorrow they have a new token already planned."
t_paper = cut_at(MAIN, 412.55)
t_outro = cut_at(OUTRO, 1.0)
def fill(start, end, names, target=-30.0, fade_out=1.2):
    """Chain beds back to back until the section is covered; fade the joins."""
    cues, t, i = [], start, 0
    while end - t > 0.5:
        c = bed(names[i % len(names)], t, end, target)
        c["fade_in"], c["fade_out"] = 1.0, fade_out
        cues.append(c)
        t += c["duration"]
        i += 1
    cues[-1]["fade_out"] = fade_out
    return cues

music = (fill(0.0, t_screen, ["jonas"], target=-28.0, fade_out=0.6)
         + fill(t_screen, t_broke, ["verclub", "vaitsez"], fade_out=0.0)   # dead stop on "over."
         + fill(t_resume, t_paper, ["vaitsez"])
         + fill(t_paper, t_outro, ["verclub", "jonas"])
         + fill(t_outro, TOTAL, ["jonas"], target=-26.0, fade_out=2.0))

edl = {
    "project": "Asgard Agents Day 1 - Edit",
    "source": MAIN,
    "resolution": [W, H],

    "fps": 30,
    "voice": {MAIN: str(AUD / "voice-main.wav"), OUTRO: str(AUD / "voice-outro.wav")},
    "segments": segments,
    "images": images,
    "sfx": sfx,
    "music": music,
}
(HERE / "edit.edl.json").write_text(json.dumps(edl, indent=1), encoding="utf-8")
print(f"{len(segments)} segments, {TOTAL:.1f}s ({TOTAL/60:.2f} min), {len(images)} images, {len(sfx)} sfx, {len(music)} music cues")
for m in music:
    print("  music", Path(m["path"]).stem, m["at"], m["duration"], m["volume"])
