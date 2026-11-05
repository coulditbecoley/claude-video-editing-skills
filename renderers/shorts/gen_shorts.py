"""YouTube Shorts v2 (9:16, 1080x1920, 60 fps) from the 3 AI Setups Challenge Video 1 raw, rendered by render_shorts.py
(no CapCut). v2 applies Codex's Shorts audit (SHORTS AUDIT - Codex.md, 25 items): recut spans, real scene-change
transitions, overlap-based captions kept out of the UI zones, one card slot, readable native assets, product-proof crops,
honest qualifiers, a montage only where the facecam exists. v1 is kept as gen_shorts.v1.py.
Layouts: "split" = screen band on top (y 0-740) + facecam below (740-1920; eyes ~1140, mouth ~1425, above YouTube's
bottom UI at ~1440); "th" = full-height 9:16 face crop. Pieces are voice source seconds; pauses over 0.45 s collapse to
0.18 s; long-form filler cuts apply; lip sync: picture = voice + S(t) from the long-form curve.
Run: python gen_shorts.py  ->  sN.json  (then: python render_shorts.py captions; python render_shorts.py render all)"""
import json, os, re, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).parent
EDIT = HERE.parent
sys.path.insert(0, str(EDIT)); os.chdir(EDIT)
os.environ.setdefault("MUSIC_STEM", "0")
import gen_edl as G
os.chdir(HERE)
GFX = EDIT / "graphics" / "out"
MAN = json.loads((GFX / "manifest.json").read_text())
AUD = EDIT / "audio"
W, H, FPS = 1080, 1920, 60
SEAM = 740
q = lambda t: round(round(t * FPS) / FPS, 4)
F5 = np.load("D:/edits/0939/frames5.npy")

TH = json.loads((EDIT / "th_ranges.json").read_text())
is_th = lambda t: any(a <= t <= b for a, b in TH)
CAMBOX = (2920, 1428, 3714, 2034)
# the recorded facecam exists in the source until 926.6 (from 926.8 the build view replaces it), then again in part B:
# montage pieces stay inside it (Codex #11)
CAM_ON = [(0, 926.6), (1246.45, 2037)]


def band_for(t):
    if 1322 <= t < 1538: return (380, 40, 2500)
    if 1538 <= t < 1733: return (560, 40, 2340)
    if 1733 <= t < 1912: return (520, 40, 2380)
    if 1912 <= t < 1966: return (300, 40, 2600)
    if 246 <= t < 580: return (420, 110, 2460)
    return (0, 0, 2900)


def cam_for(t):
    cx = 3186 if t < 1246.45 else 3262
    return (cx - 266, 1452, 533, 582)


def th_for(t, punch):
    if t < 1246.45:
        cx, w, h, y0 = 1890, 1215, 2160, 0
        if punch:
            w, h, y0 = 1125, 2000, 40
    else:
        cx, w, h, y0 = 1975, 1125, 2000, 160
        if punch:
            w, h, y0 = 1040, 1850, 200
    return (cx - w // 2, y0, w, h)


def wend(t):
    return max(e for w, s, e in G.WORDS if s <= t + 0.02 and s >= t - 3)


LOCAL_CUTS = [(1917.36, 1919.74), (490.31, 491.34)]    # + round 8 QA: "so the, you know, the project" -> "so the project"    # "So that's, that's, uh, interesting" -> "So that's interesting"


def pieces_of(sp):
    """sp = (a, b) or (a, b, opts); opts: x=True (b is exact), band=(x0, y0, w) a product-proof crop"""
    a, b = sp[0], sp[1]
    opts = sp[2] if len(sp) > 2 else {}
    a0 = a - 0.08
    b0 = b if opts.get("x") else wend(b) + 0.1
    cur, sub = a0, []
    for ca, cb in sorted(c for c in G.CUTS + LOCAL_CUTS if a0 < c[0] < b0):
        sub.append((cur, ca)); cur = cb
    sub.append((cur, b0))
    out = []
    for x0, x1 in sub:
        c = x0
        for s, e in G.SIL:
            if s > x0 and e < x1 and e - s > 0.45:
                out.append([round(c, 3), round(s + 0.09, 3), opts]); c = e - 0.09
        out.append([round(c, 3), round(x1, 3), opts])
    return [p for p in out if p[1] - p[0] > 0.08]


def fdiff(t):
    """screen change at picture second t (frames5, 5 fps, facecam masked)"""
    i = int(round(t * 5))
    if i < 1 or i >= len(F5):
        return 0.0
    a, b = F5[i - 1].astype(np.int16), F5[i].astype(np.int16)
    a[70:103, 145:188] = 0; b[70:103, 145:188] = 0
    return float(np.abs(a - b).mean())


import subprocess
_REF = {}


def refine(t):
    """round 7: the exact change frame at 60 fps (+-0.3 s around the 5 fps hit), facecam masked"""
    if t in _REF:
        return _REF[t]
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t - 0.3:.3f}", "-i", G.MAIN, "-t", "0.6", "-vf", "fps=60,scale=240:135,format=gray",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 135, 240).astype(np.int16)
    fr[:, 88:, 180:] = 0; fr[:, 130:, :] = 0
    d = np.abs(np.diff(fr, axis=0)).mean((1, 2))
    _REF[t] = round(t - 0.3 + (int(d.argmax()) + 1) / 60, 4) if len(d) else t
    return _REF[t]


def changes(a, b):
    """real screen changes inside a piece (picture seconds), each > 0.5 s from its ends"""
    out, t = [], a + 0.5
    while t < b - 0.5:
        if fdiff(t) > 12 and (not out or t - out[-1] > 1.0):
            out.append(round(t - 0.1, 2))
        t += 0.2
    return out


NOT_CHANGES = [1652.81]     # round 9 (#5): S3's vertical scroll inside one section, not a new page
MONT = [(812.0, 822.5, 1.6), (900.0, 926.0, 1.6)]   # the build, sped up, where his facecam is still in the recording

SHORTS = {
    1: dict(title="3 AI Teams, 6 Hours, $100", bed="el-shorts-a.wav", hook="sh2-hook-1", end="sh2-end-6",
            spans=[(9.08, 14.86, {"x": True}), (17.24, 22.28, {"x": True}), (283.92, 286.64), (372.26, 374.78), "MONT", (1251.99, 1254.01),
                   (1344.21, 1348.49, {"band": (880, 250, 1200)}), (1553.41, 1555.53), (1746.41, 1749.01)],
            post_from=1300, teams=[(1344.21, "sh2-t-paperclip"), (1553.41, "sh2-t-hermes"), (1746.41, "sh2-t-grok")]),     # #11
    2: dict(title="A $12 Home Planner Made by AI", bed="el-recap.wav", hook="sh2-hook-2", end="sh2-end-2", post_from=0, test_at=(17.9, 19.97),
            spans=[(1344.21, 1348.49, {"band": (880, 250, 1200)}), (1350.29, 1353.79, {"band": (1700, 150, 1400)}),
                   (1361.13, 1368.01, {"band": (880, 380, 1160)}), (1370.95, 1375.31, {"band": (880, 560, 1160)})]),
    3: dict(title="What Am I Looking At? Hermes Built This", bed="el-shorts-b.wav", hook="sh2-hook-3", end="sh2-end-3", post_from=0,
            spans=[(1605.28, 1606.90, {"x": True, "band": (750, 700, 1800)}), (1545.17, 1547.27), (1550.93, 1555.53),
                   (1580.49, 1582.50, {"x": True}), (1563.57, 1566.83), (1598.11, 1599.53, {"band": (750, 420, 1900)}),
                   (1644.05, 1654.85, {"x": True})]),
    4: dict(title="Grok Built a Printable Escape Room", bed="el-window-b.mp3", hook="sh2-hook-4", end="sh2-end-4", post_from=0, test_at=(16.2, 18.28),
            spans=[(1796.98, 1800.38), (1742.67, 1749.01), (1768.40, 1774.04), (1790.16, 1791.58),
                   (1808.62, 1811.64, {"band": (860, 720, 1050)}), (1815.90, 1819.60, {"band": (800, 600, 2100)})]),
    5: dict(title="Which AI Priced Higher?", bed="el-shorts-b.wav", hook="sh2-hook-5", end="sh2-end-5", post_from=0, hook_d=0.5,
            card_words=[("sh2-p1", "12", 1), ("sh2-p2", "NINE", 1), ("sh2-p3", "NINE", 2)],      # #2: hits on the spoken prices
            spans=[(1911.3, 1922.95), (1927.77, 1931.95)]),
    6: dict(title="6 Hours. No Second Chance.", bed="el-intro.mp3", hook="sh2-hook-6", end="sh2-end-6",
            spans=[(355.62, 358.32, {"band": (1100, 600, 1800)}), (345.88, 350.04, {"band": (1150, 640, 1750)}),
                   (359.56, 361.00, {"band": (880, 560, 1800)}), (372.26, 374.78, {"band": (1600, 150, 1800), "hold": True}),
                   (396.0, 401.62, {"band": (1150, 640, 1750)}), (407.20, 410.80, {"band": (1150, 300, 1750)}),
                   (412.08, 416.56, {"band": (1250, 150, 1850)})]),
    7: dict(title="Automated, But It Asks Permission", bed="el-shorts-a.wav", hook="sh2-hook-7", end="sh2-end-7", hook_d=1.5,
            spans=[(779.19, 782.33, {"band": (1760, 1460, 760)}), (786.29, 787.99, {"band": (2150, 500, 1250)}),
                   (480.12, 482.22, {"band": (1000, 450, 1900)}), (483.84, 491.66, {"band": (1000, 450, 1900)})]),
    8: dict(title="How Much Help Did the AI Need?", bed="el-term-a.wav", hook="sh2-hook-8b", end=None, hook_d=2.0, after_from=1246.45, tail_cards=(1277.06, ["sh2-h1", "sh2-h2", "sh2-h3"]),
            spans=[(550.14, 552.06, {"x": True, "band": (1100, 80, 1950)}), (1271.69, 1275.26), (1277.06, 1278.44), (1282.96, 1284.57), (1264.63, 1270.03)]),
}

# cards: (asset, source second, seconds, y). One upper slot; native sh2 assets at scale 1.0.
CARDS = {
    1: [("sh2-r1", 284.14, 2.6, 330), ("sh2-r3", 372.26, 2.6, 330)],
    6: [("sh2-r1", 345.88, 4.2, 330), ("sh2-r2", 359.56, 1.6, 330), ("sh2-r3", 372.26, 2.6, 330), ("sh2-r4", 396.0, 5.6, 330),
        ("sh2-r5", 407.20, 3.6, 330), ("sh2-r6", 412.08, 4.5, 330)],
}

RAW = [(w["w"].strip(), w["s"], w["e"]) for s in json.load(open(EDIT / "main.wav.words.json", encoding="utf-8"))["segments"] for w in s["words"]]
# round 9 (#3): caption corrections the transcript can't give (checked by isolated snippets + 10 ms energy)
RAW += [("It's", 9.15, 9.42), ("time", 9.45, 9.74), ("to", 9.76, 9.96), ("Look", 779.0, 779.18), ("I", 1276.98, 1277.08)]
RAW.sort(key=lambda x: x[1])
FORCE = {1908.3258: 1911.42, 1917.9658: 1919.76, 490.92: 491.36, 1565.4711: 1565.5}   # stretched/straddling words -> real start
FIX = {"grokbot": "GROK BOT", "grogbot": "GROK BOT", "hermey's": "HERMES", "clod": "CLAUDE", "codecs": "CODEX", "edible": "EDITABLE",
       "scald": "SKALD", "ok": "OK", "okay": "OK", "allright": "ALL RIGHT", "alright": "ALL RIGHT"}
ACCENT = re.compile(r"^(\$?\d|PAPERCLIP|HERMES|GROK|CLAUDE|OPUS|SIX|HOURS|BUDGET|ESCAPE|PACKING|CRAFT|CHECKLIST|PLANNER|ZIP|MONEY|HELP|"
                    r"STRUGGLE|FIX|NINE|SPAM|SUBSCRIPTION|GO|SEND|ALLOW|RACE|LOOKING|PUZZLES?|TIMELINE|DOWNLOAD|TOP-UPS|MARKETING)")


def norm_tok(t):
    k = re.sub(r"[^a-z0-9'$%.-]", "", t.lower()).strip(".")
    if k in FIX:
        return FIX[k]
    return re.sub(r"[^A-Z0-9'$%.-]", "", t.upper()).strip(".-")


def captions_for(pcs, offs, segs, total):
    """each raw word goes to the kept voiced piece it overlaps most (Codex #5), timed in output; chunks of <= 3 words
    break at pauses, punctuation, layout changes and source jumps (Codex #6); end <= next start and <= total"""
    toks = []
    SILS = G.SIL
    cont = lambda b_, a_: a_ - b_ < 0.05 or any(s_ <= b_ + 0.05 and e_ >= a_ - 0.05 for s_, e_ in SILS)
    for w, s, e in RAW:
        fk = next((v for k_, v in FORCE.items() if abs(k_ - s) < 0.002), None)
        if fk is not None:
            s, e = fk, max(fk + 0.12, min(e, fk + 0.6))
        best, bo = None, 0.0
        for i, ((a, b, _), sg) in enumerate(zip(pcs, segs)):
            if sg["mute"]:
                continue
            ov = min(e, b) - max(s, a)
            if ov > bo:
                best, bo = i, ov
        if best is None:
            continue
        a, b, _ = pcs[best]
        # round 9 (#3): Whisper stretches word ENDS across pauses, so judge a word by where it starts: inside the piece
        # (0.15 s grace at the head, none in the last 0.12 s), or mostly inside it
        head_cont = best > 0 and cont(pcs[best - 1][1], a) and not segs[best - 1]["mute"]      # a pause-collapse join, not a jump
        tail_cont = best + 1 < len(pcs) and cont(b, pcs[best + 1][0]) and not segs[best + 1]["mute"]
        lo_ok = head_cont or s >= a - 0.15
        hi_ok = tail_cont or s < b - 0.12
        if not ((lo_ok and hi_ok and bo >= 0.04) or bo >= 0.6 * (e - s)):
            continue
        t = norm_tok(w)
        if not t:
            continue
        toks.append([t, offs[best] + max(s, a) - a, offs[best] + min(e, b) - a, w, best])
    toks.sort(key=lambda x: x[1])
    for i in range(len(toks) - 1, 0, -1):          # "5 5" -> "5.5"
        if toks[i][0] == "5" and toks[i - 1][0] == "5" and toks[i][1] - toks[i - 1][2] < 0.4:
            toks[i - 1][0] = "5.5"; toks[i - 1][2] = toks[i][2]; del toks[i]
    chunks, cur = [], []
    for t in toks:
        if cur:
            p = cur[-1]
            jump = t[4] != p[4] and abs(pcs[t[4]][0] - pcs[p[4]][1]) > 1.0
            lay = segs[t[4]]["layout"] != segs[p[4]]["layout"]
            if len(cur) >= 3 or t[1] - p[2] > 0.35 or re.search(r"[.,?!]$", p[3]) or jump or lay:
                chunks.append(cur); cur = []
        cur.append(t)
    if cur:
        chunks.append(cur)
    out = []
    for k, c in enumerate(chunks):
        st = c[0][1]
        nxt = chunks[k + 1][0][1] if k + 1 < len(chunks) else total
        en = min(nxt, max(c[-1][2] + 0.25, st + 0.4), total - 0.02)
        if k + 1 < len(chunks) and nxt - c[-1][2] < 0.6:
            en = nxt
        words = [x[0] for x in c]
        acc = next((i for i, w in enumerate(words) if ACCENT.match(w)), max(range(len(words)), key=lambda i: len(words[i])))
        lay = segs[c[0][4]]["layout"]
        out.append({"text": words, "accent": acc, "start": q(st), "end": q(en), "wt": [q(x[1]) for x in c],
                    "x": 540 if lay == "split" else 500, "y": SEAM if lay == "split" else 1280, "maxw": 960 if lay == "split" else 840})
    return out


KIT = AUD / "el-sfx" / "kit"      # round 4: ElevenLabs SFX v3 (PROVENANCE.md next to the kit)
SND = {"pop": "el-sfx/kit/pop-1.wav", "coin": "el-sfx/kit/cash-1.wav", "tick": "el-sfx/kit/tick-1.wav", "boom": "el-sfx/kit/hit-1.wav",
       "riser": "el-sfx/kit/riser-1.wav", "whoosh": "el-sfx/kit/endwhoosh-1.wav", "swipe": "el-sfx/kit/swoosh-1.wav",
       "swipe2": "el-sfx/kit/swoosh-2.wav", "flash": "el-sfx/kit/flash-1.wav", "ffwd": "el-sfx/kit/ffwd-1.wav"}
OLD_SND = {"pop": "pop.wav", "coin": "sfx-coin.wav", "tick": "sfx-tick.wav", "boom": "sfx-boom.wav", "swish": "sfx-swish-soft.wav",
       "sparkle": "sfx-sparkle.wav", "riser": "sfx-riser.wav", "impact": "sfx-impact.wav", "whoosh": "sfx-whoosh-air.wav", "swipe": "sfx-swipe.wav"}


def build(n, spec):
    # pieces, split at real screen changes inside them: a swipe on the top band at the change frame (Codex #13)
    raw = []
    for sp in spec["spans"]:
        if sp == "MONT":
            raw += [[a, b, {"mont": d}] for a, b, d in MONT]
        else:
            raw += pieces_of(sp)
    pcs, chg = [], []
    for a, b, o in raw:
        if "mont" not in o and not is_th((a + b) / 2) and "band" not in o:
            for c in [refine(c) for c in changes(a + G.S(a), b + G.S(b))]:
                c = c - G.S(c)
                if any(abs(c - x) < 0.4 for x in NOT_CHANGES):
                    continue
                pcs.append([a, round(c, 3), o]); chg.append(True); a = round(c, 3)
        pcs.append([a, b, o]); chg.append(False)
    segs, offs, off, talk_i = [], [], 0.0, 0
    for i, (a, b, o) in enumerate(pcs):
        mid = (a + b) / 2
        layout = "th" if is_th(mid) else "split"
        sp = (b - a) / o["mont"] if "mont" in o else 1.0
        seg = {"in": a, "out": b, "speed": round(sp, 6), "mute": "mont" in o, "layout": layout, "pic_off": round(G.S(a), 4)}
        if o.get("hold"):
            seg["hold"] = True
        if layout == "th":
            talk_i += 1
            seg["th"] = th_for(mid, talk_i % 2 == 0)
        else:
            x0, y0, w = o.get("band") or band_for(mid)
            seg["band"] = (x0, y0, w); seg["cam"] = cam_for(mid)
            hh = round(w * SEAM / W)
            assert (x0 + w <= CAMBOX[0] or y0 + hh <= CAMBOX[1]) and y0 + hh <= 2088, (n, a, seg["band"])
            assert any(p <= a and b <= r for p, r in CAM_ON), (n, a, "no facecam in the source here")
        if segs:
            prev = segs[-1]
            if chg[i - 1]:
                prev["tr"] = ["SwipeTop", 0.3]            # the real change frame, inside continuous audio
            elif seg["mute"] != prev["mute"] and layout == "split" and prev["layout"] == "split":
                prev["tr"] = ["FlashTop", 0.24]           # into / out of the time-lapse
            elif (prev["layout"] == layout == "split" and prev["band"] != seg["band"] and not (seg["mute"] and prev["mute"])
                  and (abs(a - prev["out"]) > 60 or band_for(a) != band_for(prev["out"]))):    # round 7: a reframe on the same page is a clean cut
                prev["tr"] = ["SwipeTop", 0.3]            # a new view across a cut (app or crop change)
            elif prev["layout"] == layout == "split" and prev["band"] != seg["band"] and not seg["mute"]:
                seg["settle"] = True                      # round 8: a reframe cut lands with a short settle
        segs.append(seg); offs.append(off); off += (b - a) / sp
    total = off
    # round 9 (#8): one continuous push per run of contiguous source pieces with the same framing (no reset at pause cuts)
    ch0 = 0
    for i, sg in enumerate(segs):
        if i and not (abs(sg["in"] - segs[i - 1]["out"]) < 1.0 and sg["layout"] == segs[i - 1]["layout"]
                      and sg.get("band") == segs[i - 1].get("band") and not segs[i - 1].get("tr") and not sg["mute"]):
            ch0 = i
        sg["chain"] = ch0
    for i, sg in enumerate(segs):
        js = [j for j, x in enumerate(segs) if x["chain"] == sg["chain"]]
        sg["chain"] = [round(offs[js[0]], 4), round(offs[js[-1]] + (segs[js[-1]]["out"] - segs[js[-1]]["in"]) / segs[js[-1]]["speed"] - offs[js[0]], 4)]
    images, sfx = [], []

    def out_at(t):
        hit = [o_ + (t - a) / s_["speed"] for o_, s_, (a, b, _) in zip(offs, segs, pcs) if a - 0.05 <= t <= b + 0.05 and not s_["mute"]]
        if hit:
            return hit[0]
        nxt = [(a - t, o_) for o_, s_, (a, b, _) in zip(offs, segs, pcs) if 0 < a - t < 3.0]
        if nxt:
            return min(nxt)[1]
        raise KeyError(t)

    def img(name, at, dur, x, y, sc=1.0, sound=None, vol=0.16, slot=None):
        if name not in MAN:
            print("MISSING", name); return None
        at = q(at); dur = round(min(dur, total - at), 3)
        im = {"path": str(GFX / f"{name}.png"), "start": at, "duration": dur, "x": x, "y": y, "scale": sc, "pop": True, "slot": slot}
        if MAN[name].get("frames"):
            im["seq"] = {"dir": str(GFX / name), "frames": MAN[name]["frames"]}
        images.append(im)
        if sound:
            sfx.append({"path": str(AUD / SND[sound]), "peak_at": q(at + MAN[name].get("hit", 0.13)), "volume": vol})
        return im
    hook_d = spec.get("hook_d", 2.6)
    img(spec["hook"], 0.0, hook_d, 540, 320, sound="boom", vol=0.12, slot="top")
    sfx[-1]["peak_at"] = q(max(0.02, MAN[spec["hook"]].get("hit", 0.16) - 44 / FPS))     # round 6: matches HOOK_OFF in the renderer (clamped to frame ~1)
    caps = captions_for(pcs, offs, segs, total)
    wt_ = [(w, t) for c in caps for w, t in zip(c["text"], c["wt"])]
    def word_at(w, k):
        hits = [t for x, t in wt_ if x == w]
        return hits[k - 1]
    cs = [(nm, word_at(w, k)) for nm, w, k in spec.get("card_words", [])]
    for k_, (name, t_) in enumerate(cs):
        at = t_ - MAN[name].get("hit", 0.12)
        nx = cs[k_ + 1][1] - MAN[cs[k_ + 1][0]].get("hit", 0.12) if k_ + 1 < len(cs) else total - 1.5
        img(name, at, nx - at, 540, 360, sound="coin" if k_ == 0 else "tick", vol=0.4 if k_ == 0 else 0.2, slot="top")
        images[-1]["noexit"] = k_ + 1 < len(cs)
    for name, t, d, y in CARDS.get(n, []):
        try:
            at = max(out_at(t), hook_d)
        except KeyError:
            print("CARD TIME CUT OUT", n, name, t); continue
        snd = "coin" if name == "sh2-p1" else ("tick" if name.startswith(("sh2-r", "sh2-h", "sh2-p")) else "pop")
        img(name, at, d, 540, y, sound=snd, vol={"coin": 0.4, "tick": 0.2, "pop": 0.17}[snd], slot="top")
    if spec.get("tail_cards"):      # S8: the help cards close the Short, evenly spaced (their kicker carries the end line)
        t0 = out_at(spec["tail_cards"][0]); names = spec["tail_cards"][1]; d = (total - t0) / len(names)
        for i, nm in enumerate(names):
            img(nm, t0 + i * d, d, 540, 330, sound="tick", vol=0.2, slot="top")
    if spec["end"]:
        img(spec["end"], total - 1.5, 1.5, 540, 360, sound="whoosh", vol=0.106, slot="top")     # Codex #16
    # one upper slot: a card ends when the next one in the slot starts; relit states hand over without an exit (#8, #10)
    top = sorted([im for im in images if im.get("slot") == "top"], key=lambda im: im["start"])
    images[:] = [im for im in images if im.get("slot") != "top" or im["duration"] > 0.15 or im is top[-1]]
    for a_, b_ in zip(top, top[1:]):
        a_["duration"] = round(min(a_["duration"], b_["start"] - a_["start"]), 3)
        same_family = os.path.basename(a_["path"])[:5] == os.path.basename(b_["path"])[:5] and "end" not in b_["path"]
        if a_["duration"] >= b_["start"] - a_["start"] - 1e-3 and same_family and "sh2-p" in a_["path"]:
            a_["noexit"] = True
    # post-deadline badge through the site footage, its own row under the slot (Codex #3)
    if "post_from" in spec:
        st = [o_ for o_, s_, (a, b, _) in zip(offs, segs, pcs) if a >= max(spec["post_from"], 1300) and s_["layout"] == "split"]
        if st:
            b0 = max(st[0], hook_d)      # round 2: top edge, after the hook, clear of the seam captions
            img("sh2-post", b0, total - b0 - 1.5, 540, 78, slot="badge")
    if spec.get("test_at"):
        a_, b_ = spec["test_at"]; img("sh2-test", a_, b_ - a_, 540, 240, slot="badge2")
    if spec.get("after_from"):
        st = [o_ for o_, s_ in zip(offs, segs) if s_["in"] >= spec["after_from"]]
        if st:
            img("sh2-after", max(st[0], hook_d), 2.2, 540, 78, slot="badge")
    for k_, (t_, nm) in enumerate(spec.get("teams", [])):
        a_ = out_at(t_); nx = out_at(spec["teams"][k_ + 1][0]) if k_ + 1 < len(spec["teams"]) else total - 1.5
        img(nm, a_ + 0.15, nx - a_ - 0.15, 540, 240, slot="badge2")
    # the montage label, no clock (excerpts, not a measured six hours; Codex #15); the riser leads INTO it (#25)
    if any(s_["mute"] for s_ in segs):
        m0 = next(o_ for o_, s_ in zip(offs, segs) if s_["mute"])
        m1 = max(o_ + (s_["out"] - s_["in"]) / s_["speed"] for o_, s_ in zip(offs, segs) if s_["mute"])
        img("sh2-mont", m0 + 0.2, m1 - m0 - 0.3, 540, 78, slot="badge")
        sfx.append({"path": str(AUD / SND["riser"]), "peak_at": q(m0), "volume": 0.11})
        sfx.append({"path": str(AUD / SND["ffwd"]), "peak_at": q(m1 - 0.6), "volume": 0.17})    # the time-lapse texture
    k_ = 0
    for o_, s_, (a, b, _) in zip(offs, segs, pcs):
        if s_.get("tr"):
            k_ += 1     # alternate the two swooshes so repeated swipes don't sound copy-pasted
            nm = ("swipe" if k_ % 2 else "swipe2") if s_["tr"][0] == "SwipeTop" else "flash"
            sfx.append({"path": str(AUD / SND[nm]), "peak_at": q(o_ + (b - a) / s_["speed"]), "volume": 0.19 if nm != "flash" else 0.22})
    caps = captions_for(pcs, offs, segs, total)
    # round 8: price callouts (callouts.py: OCR-located on the band at the spoken word)
    CO = HERE / "callouts.json"
    rings = json.loads(CO.read_text()).get(str(n), []) if CO.exists() else []
    for r_ in rings:
        i_ = max(j for j, o_ in enumerate(offs) if o_ <= r_["start"] + 1e-6)
        end_ = offs[i_] + (segs[i_]["out"] - segs[i_]["in"]) / segs[i_]["speed"]
        r_["duration"] = round(min(r_["duration"], end_ - r_["start"]), 4)
    for r_ in rings:
        sfx.append({"path": str(AUD / SND["pop"]), "peak_at": q(r_["start"] + 0.12), "volume": 0.24})
    return {"n": n, "title": spec["title"], "total": round(total, 3), "segments": segs, "offsets": offs, "images": images,
            "captions": caps, "sfx": sfx, "rings": rings, "hook_d": hook_d, "bed": str(AUD / spec["bed"]), "voice": str(AUD / "voice-main.wav"),
            "source": G.MAIN, "size": [W, H], "fps": FPS, "seam": SEAM}


if __name__ == "__main__":
    which = [int(x) for x in sys.argv[1:]] or list(SHORTS)
    for n in which:
        d = build(n, SHORTS[n])
        (HERE / f"s{n}.json").write_text(json.dumps(d, indent=1), encoding="utf-8")
        print(f"s{n}: {d['total']:.1f}s, {len(d['segments'])} pieces, {len(d['captions'])} captions, {len(d['images'])} images, "
              f"{sum(1 for s in d['segments'] if s.get('tr'))} transitions  {d['title']}")
