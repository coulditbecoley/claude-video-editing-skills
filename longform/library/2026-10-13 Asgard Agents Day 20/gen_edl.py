"""Edit decisions for Asgard Agents Day 20 (OBS take 2026-10-13 09-49-53) as a ccut EDL.

One 14:54 take: talking-head hook 0-45.9 (OBS fades to the screen at 45.9), the Obsidian
"Day 20 - What's New" canvas 46-345.9 (he pans and zooms it himself), the Agents Window 345.9-489.6,
the PaperRows site 489.6-666.1 (white mode 655.4-659.0), the Agents Window again 666.1-774.2,
Paperclip's task board 774.2-811.1, the Agents Window 811.1-818.9, talking-head outro from 818.9.

Built from the Day 13 and AI Agents Business Ep 1 edits (taste.md): cold open on the stakes, hook,
no captions, static punch-ins only (CapCut 9.2 ignores video keyframes), fixed facecam overlay,
pauses cut only across still screen, transitions on the real screen change, landing pages and
Paperclip full frame, calm exit. Keeps are written as the words he says, snapped into silences.
Narration checked against the screen: Heimdall's note (the canvas says he HELD the PaperRows posts
until every claim checked out) is carded from the canvas, the vague "post is up" line is cut.
Run: python gen_edl.py  ->  edit.edl.json
"""
import json
import re
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
MAIN = "~/Projects/Youtube/videos/2026-10-13 09-49-53.mp4"
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

# ---- the edit, in story order ------------------------------------------------------------
KEEPS = [
    # v3 (Coley, 2026-10-13: "only cut out pauses and ums and unimportant information"): every line that carries
    # information is back; cuts are pauses, ums, stutters, restarts and lines that repeat an earlier one.
    # cold open: the agents hold the keys, not him
    keep("every single transaction is taken care of by thor", "by thor", 211, "cold"),
    keep("nobody else can get it done", "or even my own", 221, "cold", at_out=230.55),
    # hook (talking head)
    keep("you have got to see", "have done", 4, "talk", at_in=3.4),
    keep("this is day 20 update", "a week ago", 13, "talk"),
    keep("today were going to give you an update", "running on their own", 23, "talk", end_hint=34),
    keep("so lets go over here and jump into the canvas", "into the canvas", 35, "talk"),
    # 01 the canvas: what changed in seven days
    keep("here we are in the obsidian canvas", "since our last update", 60, at_in=59.15, end_hint=69),
    keep("were going to do a quick rundown", "whats coming next", 70),
    keep("first up overview", "first up overview", 80),
    keep("they did get their first sale", "go over that shortly", 92, at_out=95.80),
    keep("they did release their own asgard token", "asgard token", 102, at_out=107.62),   # not the doubled "token."
    keep("so now the entire ecosystem has its token", "built around", 108),
    keep("they decided that they should be paid for their work", "get paid in", 113),
    keep("so now they get paid every minute", "100 asgard tokens", 119),
    # follow along
    keep("of course as always if you want to follow the agents", "clearly marked", 131, end_hint=150),
    # they catch their own mistakes
    keep("up next this is just more things", "always do security", 151.5),
    keep("they catch their own mistakes", "thats their job", 158, at_in=158.55),
    keep("so theyre just letting you know", "they always test everything", 161, end_hint=170),
    keep("first payday is coming up", "up until then", 171, end_hint=180),
    # behind the scenes
    keep("behind the scenes things that have been updated", "have been updated", 198.5),
    keep("every single transaction is taken care of by thor", "make that happen", 211),
    keep("nobody else can get it done", "on their own is just crazy", 221, end_hint=243),
    keep("they did change the agents window", "video game arcade style", 245, end_hint=260),
    # what's next
    keep("now their goal is to grow their newest business", "newest business", 269),
    keep("they are no longer creating meme coins", "on their ecosystem token", 280),
    keep("and now theyre running their paper rows", "converter", 285, at_out=292.5),
    keep("their proudest moment", "run in the browser", 293),
    keep("so all of your bank statements stay private", "never leave your browser", 299.4, end_hint=304.5),
    keep("there is another business that theyre going to take over", "take it over though", 309, end_hint=320),
    keep("i will no longer have any interaction with it", "interaction with it", 320, at_out=322.3),
    keep("you can even email these guys", "reply to you", 332),
    keep("all right were going to move on to the fun stuff", "over to the agents window", 338),
    # 02 the Agents Window
    keep("and here we are in the agents window", "in the agents window", 351, at_in=350.55),
    keep("a lot of things have changed", "since our last update", 357),
    keep("now there are animations", "i dont tell them what to do", 363, end_hint=373, at_out=373.62),
    keep("so i guess right now is sleepy time", "sleepy time", 380, at_out=382.75),
    keep("if they are at work", "what theyre doing", 384, at_in=384.72),
    keep("ive seen loki on a computer", "posts on accounts", 391, at_in=391.35),
    keep("moving down to the lower left", "token and payroll", 399, at_in=399.5),
    keep("so no more meme coins", "and their ecosystem", 404.3, end_hint=410.5),
    keep("their goal with it is to pay themselves", "as well", 412, end_hint=425),
    keep("if any of these agents go outside", "paid in asgard token", 429, end_hint=448),
    keep("down here is the chart", "updated in real time", 455, end_hint=468),
    keep("once the agents get their first payday", "different speeds", 471, end_hint=484, at_in=471.25),
    keep("up next their newest business", "talking about it", 484, end_hint=490),
    # 03 PaperRows
    keep("so this is something that they come up with", "come up with", 491.4),
    keep("there is a completely new youtube series", "decided to create", 494),
    keep("all i did was ask them", "would be profitable", 501),
    keep("so they did the research", "did the research", 509),
    keep("they said a bank statement", "customer service emails", 511, end_hint=521),
    keep("they said they could handle everything", "human interaction", 523, end_hint=533),
    keep("obviously very small things had to be done by me", "extremely small", 534),
    keep("really all this is is you go in here", "readable csv", 543.5, end_hint=553, at_out=554.6),
    keep("so if you ever need to give your accountant", "throughout the business", 555, end_hint=564, at_out=564.38),
    keep("this is exactly the tool you would use", "you would use", 567),
    keep("the biggest thing about this tool", "stay on your computer", 569),
    keep("so a lot of these tools", "sharing your information with them", 575, end_hint=584.5),
    keep("the point of this project", "never reaches a server", 585),
    keep("the agents do not see any of your information", "stays with you", 592, end_hint=601),
    keep("that was their biggest achievement", "proud of the privacy", 601.8, end_hint=608.4),
    keep("here it is its simple", "show you the statement", 609.6, end_hint=619),
    keep("and then if you would like to get the csv file", "designed it for", 619, end_hint=637),
    keep("and if you want to learn more", "customer service", 637.9, end_hint=649.3),
    keep("so yeah thats their newest achievement", "they built this", 651.2, end_hint=653.8),
    keep("here were going to blind you real quick", "maybe some people would", 656, end_hint=660.5, at_out=661.2),
    keep("so lets get back here to the agent window", "agent window", 666, at_in=666.15),
    # 04 next business, socials
    keep("you can see a blank box here", "coming soon", 669),
    keep("this business was partially created by the agents", "c3 research", 675),
    keep("so i did have a hand in helping them create this", "create this", 683.4),
    keep("obviously they did the coding and assisted me", "my idea", 687),
    keep("i wanted a token research tool", "as simple as that", 695, end_hint=702.3),
    keep("you put in the token ca", "information sheet", 702),
    keep("c3research io is the website", "on this channel", 711, at_in=711.6, end_hint=720.4),
    keep("we do have the social media accounts", "top right here", 725),
    keep("be sure to give the agents a follow", "talk to others", 733, end_hint=745),
    keep("but these other three", "i dont do anything", 746, end_hint=751.2),
    keep("they are commenting back to people", "on those three", 752, end_hint=770.6, at_out=771.7),
    # 05 Paperclip
    keep("all of this is run inside of paperclip", "paperclip ai", 776.4, at_in=776.22, at_out=779.4),
    keep("all i did was set up the agents in here", "need to get done", 780),
    keep("you can see theres stuff here waiting", "a certain degree", 788, end_hint=800),
    # one keep across the tab switch, so the swipe sits in his real 0.6 s pause on continuous audio
    keep("obviously if theres a usage limit", "what they have going on", 801, at_in=801.3, end_hint=818, at_out=819.7),
    # outro (talking head)
    keep("if you like this series", "follow along", 820, "talk", at_in=819.7),
    keep("were going to do another update", "previous business are doing", 823, "talk", end_hint=830.3),
    keep("if you want to watch the agents work", "all day every day", 831, "talk", end_hint=841, at_out=841.72),
    keep("its all about being public", "alive on the window soon", 854.7, "talk", end_hint=881),
    keep("that is all we have for today", "have gotten into", 882),
]
for i, k in enumerate(KEEPS):
    if k[0] >= 819.0 and k[2] == "screen":
        KEEPS[i] = (k[0], k[1], "talk")
OUTRO = 819.0
MAX_GAP = 0.4
OUTRO_GAP, OUTRO_TAIL, OUTRO_HEAD = 0.6, 0.2, 0.14
SITE = (489.55, 666.1)

# Stutters inside keeps (source seconds), set after reading the stitched voice transcript.
CUTS = [
    (685.80, 686.55),     # "helping them, you know, create this"
    (715.30, 717.62),     # "find it in our other YouTube channel, uh, in our other YouTube videos" (restart)
    (530.74, 532.38),     # "with no, none to little human interaction" -> "with little human interaction"
    (139.78, 141.12),     # "go to the, uh, agents window"
    (141.72, 144.42),     # "agents window, uh, asgardagents.com"
    (872.72, 873.14),     # "if you need a token, meme coin token researched" -> "a meme coin token"
    (795.15, 796.36),     # "try to, you know, tell them" -> "try to tell them"
    (803.75, 805.60),     # "or, you know, a sign in" -> "or a sign in"
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

# Screen changes inside continuous speech: splits, not cuts (no voice fade), so a swipe lands on the frame.
PAPERROWS_CLICK, BACK_TO_WINDOW, TO_PAPERCLIP, PAPERCLIP_OUT, OBS_TO_CAM = 489.55, 666.10, 774.15, 811.10, 818.93
SPLITS = [PAPERROWS_CLICK, PAPERCLIP_OUT, OBS_TO_CAM]
# The other screen changes fall in pauses he never speaks across: the transition sits on that cut instead.
end_before = lambda t: max(k[1] for k in KEEPS if k[1] <= t + 0.5 and k[2] == "screen")

# Punch-ins (source in, out, scale, u, v): (u, v) is the centre of what he's talking about.
# Each window sits in a still stretch of the screen; allowed() keeps the recorded facecam copy off-frame.
ZOOMS = [
    (91.0, 100.0, 1.5, 0.45, 0.45),      # scoreboard: "1st sale" (PaperRows made its first $5 sale)
    (101.5, 108.5, 1.5, 0.68, 0.40),     # scoreboard: "ASGARD, their own ecosystem token"
    (130.5, 151.0, 1.6, 0.34, 0.60),     # follow along: Telegram, Farcaster and Bluesky, Discord
    (151.2, 171.0, 1.5, 0.55, 0.60),     # they caught their own mistakes column
    (171.2, 178.4, 1.6, 0.27, 0.80),     # what's next: "First payday, 14 October"
    (222.2, 242.2, 1.6, 0.59, 0.40),     # behind the scenes: "A locked signing service" (Thor)
    (244.0, 259.2, 1.6, 0.585, 0.50),    # behind the scenes: "Arcade cabinets"
    (361.0, 383.0, 1.6, 0.31, 0.31),     # Odin, Thor, Loki asleep by the fire (the new animations)
    (389.0, 398.5, 1.6, 0.40, 0.31),     # Loki's card: "I've seen Loki on a computer posting"
    (399.0, 416.6, 1.6, 0.31, 0.69),     # lower left: token and payroll (v2: wide for the hiring plan, Codex #9)
    (455.0, 484.5, 1.6, 0.31, 0.69),     # lower left again: the Pump.fun chart and the wallets
    (723.5, 771.5, 1.6, 0.89, 0.15),     # top right: Telegram, Farcaster, Bluesky, Discord
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
                if y - x < 0.25:
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
is_screen_t = lambda t: 46.0 <= t <= 818.9
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
T_CANVAS_END = [k for k in KEEPS if k[2] == "screen" and k[1] < 346][-1][1]
TRANSITIONS = {
    T_COLD_END: ("White_Flash", 0.35),          # out of the cold open into the hook
    T_TALK_END: ("Zoom_Transition", 0.6),       # talking head -> the canvas
    T_CANVAS_END: ("Swipe_Left", 0.45),         # Obsidian -> the Agents Window tab
    PAPERROWS_CLICK: ("Swipe_Left", 0.4),       # his click into PaperRows, mid-sentence
    end_before(BACK_TO_WINDOW): ("Swipe_Left", 0.4),   # PaperRows -> back to the Agents Window tab
    end_before(TO_PAPERCLIP): ("Swipe_Left", 0.45),    # the Agents Window -> Paperclip's task board
    PAPERCLIP_OUT: ("Swipe_Left", 0.4),                # Paperclip -> the Agents Window for the sign-off, in his pause
    OBS_TO_CAM: ("Zoom_Transition", 0.6),       # OBS's own switch to the camera, on continuous speech
}
DISSOLVE, JUMP = ("\u53e0\u5316", 0.3), 2.5
# v3 (Coley: "a lot of transitions cut off valuable information"): no repair dissolves on speech cuts at all.
# A dissolve blends the screen across the cut and smears the text he is reading; pauses are cut only where the
# screen is still, so a plain cut reads clean. Transitions stay only on real scene changes.
for i in ([] if True else range(len(PS) - 1)):
    (a0, b0, k0), (a1, b1, k1) = PS[i], PS[i + 1]
    if k0 == k1 == "screen" and abs(b0 - a1) > 1e-3 and not any(abs(t - b0) < 0.01 for t in TRANSITIONS) \
            and FRAMES[i] == FRAMES[i + 1] and b0 - a0 > 0.45 and b1 - a1 > 0.45 and jump(b0 - 0.05, a1) > JUMP:
        TRANSITIONS[b0] = DISSOLVE

segments, talk_i = [], 0
for i, p in enumerate(PS):
    a, b, kind = p
    seg = {"in": round(a, 3), "out": round(b, 3)}
    if kind == "talk":
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
        sfx.append({"path": str(AUD / ("pop.wav" if sound == "pop" else "sfx-impact.wav")),
                    "start": at, "volume": 0.24 if sound == "pop" else 0.17})


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
                   "x": round((x0 + x1) / 2), "y": round((y0 + y1) / 2), "scale": 1.0, "pop": "fade"})
    if sound:
        sfx.append({"path": str(AUD / "pop.wav"), "start": at, "volume": 0.14})

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
        screen = p[2] in ("screen", "cold") and 46.0 <= p[0] < OBS_TO_CAM
        if screen and run is None:
            prev_tr = i > 0 and any(abs(tt - PS[i - 1][1]) < 0.01 for tt in TRANSITIONS)
            run = off + (0.8 if prev_tr else 0.0)
        end_here = round(p[1], 3) in tr_ends or not screen or i == len(PS) - 1
        if run is not None and (not screen or end_here):
            stop = off + (d_ if screen else 0.0)
            if stop - run > 1.0:
                images.append({"path": str(path), "start": round(run, 3), "duration": round(stop - run, 3),
                               "x": (x0 + x1) // 2, "y": (y0 + y1) // 2, "scale": 1.0, "pop": "fade"})
            run = None
        off += d_

exec((HERE / "graphics_plan.py").read_text(encoding="utf-8")) if (HERE / "graphics_plan.py").exists() else None
facecam_frame()

FADE = 1.2
images.append({"path": str(GFX / "black-4k.png"), "start": round(TOTAL - FADE, 3), "duration": FADE, "x": 1920, "y": 1080, "pop": "fade"})
images.append({"path": str(GFX / "black-4k.png"), "start": round(TOTAL - 0.2, 3), "duration": 0.2, "x": 1920, "y": 1080, "pop": False})
for t, (name, d) in TRANSITIONS.items():
    if (name, d) != DISSOLVE:
        sfx.append({"path": str(AUD / "sfx-whoosh.wav"), "peak_at": round(cut_at(t, cold=(t == T_COLD_END)) - 0.06, 3),
                    "volume": 0.26 if d >= 0.5 else 0.2})

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
    "project": "Asgard Agents Day 20 - Edit",
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
