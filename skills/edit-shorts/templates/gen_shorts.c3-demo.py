"""9:16 YouTube Shorts cut from the C3 Research demo recording, as ccut EDLs (one per Short).

Coley (2026-10-02): "create vertical short 9x16 clips ... professionally edited with professional
transitions ... each short starts off with a hook", in a short-form style made for product demos
(not the trading-card-hit skill).

v2 (Codex Shorts audit, Coley: "make all recommended short reel fixes"):
- Nothing outlives the picture: every overlay is clamped to the runtime.
- Captions: words picked by overlap (no words lost at trims), no flush at contiguous joins, no
  overlaps, a minimum dwell, hyphen/brand normalising, junk tokens dropped.
- Everything important sits above y=2880 (YouTube's bottom UI). Talking-head face reframed higher.
- One progress system: a single "2/5 COPY THE ADDRESS" step label, a single stage label on the
  fast-forward plus "TIME COMPRESSED". No 5-item strips.
- No automatic 1.08 punch on screen shots (deliberate crops instead). Full-frame shots crop the
  browser chrome and taskbar.
- Transitions only on real view changes; cuts within a step.
- Cards clear before the next section; one at a time. Report proof = faithful report excerpts.
- Endings: payoff first, then that Short's own closing line + site. The bed lifts under the muted
  fast-forward.
- Per Short: S1 tighter (repeat explanation cut), S2 a followable tutorial ending on the result,
  S3 a result-led recut with a much shorter wait, S4 opens on the warning, S5 rebuilt around one
  claim and the unknowns, S6 no backtrack and ends on the fresh-review action.
Run: python gen_shorts.py  ->  s1.edl.json ... s6.edl.json  (renders caption PNGs via node)
"""
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
EDIT = HERE.parent
MAIN = "~/Projects/Youtube/videos/2026-10-01 10-19-41.mp4"
VOICE = str(EDIT / "audio" / "voice-main.wav")
GFX = EDIT / "graphics" / "out"
GFXS = EDIT / "graphics" / "out_shorts"
CAPS = HERE / "caps"
AUD = EDIT / "audio"
CW, CH = 2160, 3840            # canvas (never shadow these)
SEAM = 1990                    # split layout: page above, facecam below
SAFE_BOTTOM = 2880             # YouTube's UI covers the bottom quarter: nothing important below this
CAM_CLIP = str(EDIT / "facecam-tight.mp4")     # 734x546 inner crop of the OBS facecam (no rounded corners)
CAM_W, CAM_H = 734, 546
CAM_K = CW / CAM_W             # facecam scaled to the full canvas width
CAM_RECT = [0, SEAM, CAM_W, SEAM + CAM_H]
# The OBS facecam is NOT in the recording here (checked frame by frame): the DexScreener chart/tab, the wait
CAM_OFF = [(227.25, 234.8), (343.5, 1134.5)]
FULL_S = 3.8                   # full-frame screen scale: crops the browser tabs/bookmarks and the taskbar

Y_TOP = 330                    # hook card, then the step/stage label
Y_CARD = 940                   # cards and report excerpts (upper page band, clear of the hook card above)
Y_CAP = {"split": SEAM, "full": 2560, "talk": 2560}

# ---- transcript ---------------------------------------------------------------------------
WORDS = [w for s in json.loads((EDIT / "audio" / "voice-main.wav.literal.json").read_text(encoding="utf-8"))["segments"]
         for w in s["words"]]
FIX = {"orbeo": "Orbio", "orbeo,": "Orbio,", "cq": "C3", "c-cube": "C3", "robinhoodchain.": "Robinhood Chain."}
SKIP = {"connections."}        # Whisper noise on the tail of "options" (low confidence, not a word he said)

def silences():
    t = re.findall(r"silence_(start|end): ([0-9.]+)", (EDIT / "silences-main.txt").read_text())
    out, cur = [], None
    for kind, v in t:
        if kind == "start":
            cur = float(v)
        elif cur is not None:
            out.append((cur, float(v))); cur = None
    return out
SIL = silences()

def span(a, b, pad=(0.10, 0.14)):
    """Source span from the word starting at `a` to the word starting at `b` (literal-pass start times),
    padded outward but never into a neighbouring word."""
    i = min(range(len(WORDS)), key=lambda k: abs(WORDS[k]["s"] - a))
    j = min(range(len(WORDS)), key=lambda k: abs(WORDS[k]["s"] - b))
    assert abs(WORDS[i]["s"] - a) < 0.03 and abs(WORDS[j]["s"] - b) < 0.03, (a, b)
    s0 = WORDS[i]["s"] - pad[0]
    if i > 0:
        s0 = max(s0, WORDS[i - 1]["e"] + 0.02)
    e0 = WORDS[j]["e"] + pad[1]
    if j + 1 < len(WORDS):
        e0 = min(e0, WORDS[j + 1]["s"] - 0.03)
    return round(s0, 3), round(e0, 3)

def T(a, b, **o): return ("talk", span(a, b), o)
def S(a, b, start=None, end=None, **o):
    x, y = span(a, b)
    return ("screen", (start or x, end or y), o)   # start/end: edges set by ear/energy where Whisper's times run long
def Sx(a, b, **o): return ("screen", (a, b), o)    # explicit source times (verified by ear)
def F(a, b, speed, **o): return ("ff", (a, b), dict(o, speed=speed))

RING = (0.40, 0.55, 3.0)          # loading ring + stage name + elapsed timer
PAGE = (0.49, 0.50, 2.05)         # the site column, full width
DEX = (0.21, 0.45, 2.4)           # DexScreener: chain list + token names (ORBIO row) together
REPORT = (0.45, 0.50, 2.3)
FF = lambda fast: [F(344.0, 1098.0, fast), F(1098.0, 1141.55, 20)]   # the wait; "Report ready" lands at 20x
RETURN = [Sx(1141.80, 1142.90, tr="flash"), S(1144.04, 1145.82)]    # "And we are | back with a completed report." (one "back")
VERDICT = S(1159.10, 1160.42, focus=REPORT)                         # "And here we go, verdict unverified."
def HOLD(a, b, focus=REPORT):
    """An evidence hold: the report page itself, muted, full-frame with no facecam (no silent lips),
    so a report excerpt stays up long enough to read (Codex: ~4 s). The bed carries it."""
    return ("screen", (a, b), {"hold": True, "focus": focus})
VERDICT_HOLD = HOLD(1161.30, 1164.40)

SHORTS = {
    "s1": dict(title="C3 Short 1 - Rug Check", hook="hook-s1", bed="jonas", cta="cta-s1", pieces=[
        T(1.94, 5.00),                                         # "Are you tired of the Robinhood rugs? Let me help you out."
        T(12.96, 20.80),                                       # "What this tool does is give you AI agents to audit any CA token contract..."
        S(79.98, 82.42, focus=(0.33, 0.42, 3.0), tr="zoom"),   # "we do have a limited time offer, 19 bucks per report."
        S(89.08, 92.94, focus=(0.36, 0.45, 2.17)),             # "Save yourself hours and hours of research and let AI do it."
        *FF(300), *RETURN, VERDICT, VERDICT_HOLD,
    ]),
    "s2": dict(title="C3 Short 2 - How To Audit", hook="hook-s2", bed="vaitsez", cta="cta-s2", pieces=[
        S(109.04, 111.78, split=111.267),                      # cold open on the instruction (the generic promise line cut: Codex, ~40 s target)                      # "...head on over to DexScreener." (swipe on the real tab switch)
        S(216.22, 217.28, focus=DEX), S(217.70, 221.26, focus=DEX),   # "pick the chain that | you are looking to audit and the token,"
        S(221.74, 222.64, focus=DEX),                          # "we're just going to go with Orbio," (chatter after it cut)
        S(226.14, 231.36, focus=(0.92, 0.50, 3.16)),           # "...you just grab the Orbio contract address,"
        S(232.96, 238.96, split=233.767, focus=(0.35, 0.45, 2.6)),  # "you're going to head back on over to C3, paste it in,"
        S(245.02, 251.58, end=252.12, focus=(0.33, 0.55, 2.6)),     # "You can pay with Solana, USDT, USDC. You have options."
        Sx(300.75, 302.32, focus=(0.33, 0.45, 2.4)),           # "And connect your wallet."
        S(304.39, 305.20, focus=(0.90, 0.26, 2.8)),            # "Go ahead and make that confirmation," (the Phantom pop-up, top right)
        S(306.56, 308.62, focus=(0.33, 0.45, 2.4)),            # "you're connected, now you just pay." (Connected visible)
        S(310.86, 314.08),                                     # "Once the payment goes through... the loading screen,"
        *FF(300), *RETURN, VERDICT, VERDICT_HOLD,
    ]),
    "s3": dict(title="C3 Short 3 - 13 Minutes In 20 Seconds", hook="hook-s3", bed="verclub", cta="cta-s3", pieces=[
        S(316.96, 318.62, focus=RING),                         # "All right, we're going to fast forward through this,"
        F(344.0, 1098.0, 100), F(1098.0, 1141.55, 15),         # ~7.5 s of wait, then "Report ready" lands (~2.9 s)
        *RETURN, VERDICT, VERDICT_HOLD,
    ]),
    "s4": dict(title="C3 Short 4 - Before You Audit", hook="hook-s4", bed="jonas", cta="cta-s4", pieces=[
        S(327.14, 339.54, start=327.17, focus=RING),           # "be sure that the token ... completed its bonding curve or your audit will just fail and you'll get a credit back..."
    ]),
    "s5": dict(title="C3 Short 5 - Inside The Report", hook="hook-s5", bed="vaitsez", cta="cta-s5", pieces=[
        VERDICT, HOLD(1161.30, 1164.40),                       # cold open: "And here we go, verdict unverified." + hold on the verdict excerpt
        Sx(1171.06, 1175.47, focus=(0.52, 0.55, 2.3), tr="swipe"), Sx(1176.72, 1177.68, focus=(0.52, 0.55, 2.3)),  # "So what the token claims, a lot of unverified | information"
        HOLD(1177.90, 1180.30, focus=(0.52, 0.55, 2.3)),       # hold on the claim excerpt
        S(1210.90, 1214.72, start=1211.26, focus=(0.52, 0.50, 2.3), tr="swipe"),   # starts after an "um" (1210.88-1211.22)   # "Some unknowns. It will tell you what it wasn't able to find from that token."
        HOLD(1214.80, 1219.40, focus=(0.52, 0.50, 2.3)),       # hold on the unknowns excerpt + the report's own "limits, not findings" line
    ]),
    "s6": dict(title="C3 Short 6 - Why 7 Days", hook="hook-s6", bed="verclub", cta="cta-s6", pieces=[
        Sx(1253.93, 1258.27),                                  # "The reason we have a seven-day timer is because things change with tokens very fast"
        S(1246.70, 1247.54, end=1247.85), S(1248.86, 1252.62, start=1248.62),   # "These will pop up when | anyone completes a report to be viewed for seven days." ("uh" cut; library, no backtrack)
        S(1269.76, 1270.84, end=1271.38),                      # "Here are some that have been created,"
        S(1272.10, 1277.22, start=1272.00, split=1273.40),     # "they are outdated, but if you click on it, | you do have the option to prepare a fresh review." ("uh" cut)                    # "Here are some that have been created. They are outdated, but if you click on it, | you do have the option to prepare a fresh review."
    ]),
}
# per-piece focus after a split (the part after the split point gets this)
AFTER_SPLIT = {233.767: (0.35, 0.45, 2.6), 1273.40: (0.40, 0.55, 2.4), 111.267: (0.30, 0.45, 2.4)}

# per-Short graphics: (source second, image, dir, clear_at_source or None). Cards clear at the next section.
CARDS = {
    "s1": [(12.96, "logo-c3", GFX, 16.0), (81.58, "stat-price", GFX, None), (1159.80, "ex-verdict", GFXS, None)],
    "s2": [(111.70, "logo-dex", GFX, None), (1159.80, "ex-verdict", GFXS, None)],
    "s3": [(1159.80, "ex-verdict", GFXS, None)],
    "s4": [(327.17, "card-bonding", GFXS, None)],
    "s5": [(1159.40, "ex-verdict", GFXS, None), (1171.50, "ex-claim", GFXS, None),
           (1211.40, "ex-unknowns", GFXS, 1215.40), (1215.40, "quote-limits", GFXS, None)],
    "s6": [(1251.0, "stat-7days", GFX, None)],
}
STEPS = {"s2": [111.267, 226.14, 233.767, 245.02, 310.86]}   # one current-step label, lit as he reaches each step
STAGES = [344.0, 452.0, 678.0, 1008.0, 1098.0, 1141.55]
KEYWORDS = {"AI", "AGENTS", "RUGS", "RUG", "AUDIT", "CA", "CONTRACT", "C3", "19", "BUCKS", "HOURS", "DEXSCREENER",
            "ORBIO", "PAY", "SOLANA", "USDT", "USDC", "WALLET", "CONNECTED", "LOADING", "FAST", "FORWARD", "REPORT",
            "VERDICT", "UNVERIFIED", "BONDING", "CURVE", "FAIL", "FREE", "CREDIT", "UNKNOWNS", "SEVEN-DAY", "SEVEN",
            "DAYS", "OUTDATED", "FRESH", "REVIEW", "LIBRARY", "CLAIMS", "ADDRESS", "PASTE"}
MAX_GAP, TAIL, HEAD = 0.45, 0.12, 0.08

def in_off(t):
    return any(a <= t < b for a, b in CAM_OFF)

def build_pieces(spec):
    out = []
    for kind, (a, b), o in spec["pieces"]:
        cuts = [a]
        if kind != "ff" and not o.get("hold"):
            for s, e in SIL:
                if a < s and e < b and e - s > MAX_GAP:
                    cuts += [s + TAIL, e - HEAD]
        cuts.append(b)
        segs = [(cuts[k], cuts[k + 1]) for k in range(0, len(cuts), 2)]
        for k, (x, y) in enumerate(segs):
            pts = sorted({p for p in [o.get("split")] + [c for r in CAM_OFF for c in r] if p and x + 0.2 < p < y - 0.2})
            bounds = [x] + pts + [y]
            for m in range(len(bounds) - 1):
                po = dict(o) if (k == 0 and m == 0) else {kk: v for kk, v in o.items() if kk != "tr"}
                if m > 0 and o.get("split") and abs(bounds[m] - o["split"]) < 1e-6:
                    po["tr"] = "swipe"          # the real tab/page switch
                if o.get("split") and bounds[m] >= o["split"] - 1e-6 and o["split"] in AFTER_SPLIT:
                    po["focus"] = AFTER_SPLIT[o["split"]]
                out.append([round(bounds[m], 3), round(bounds[m + 1], 3), kind, po])
    return [p for p in out if p[1] - p[0] > 0.05]

def layout(kind, a, o=None):
    if kind == "talk":
        return "talk"
    return "full" if (kind == "ff" or in_off(a) or (o or {}).get("hold")) else "split"

def frame_for(kind, a, o, punch):
    """ccut frame {scale, x, y}. Scale is relative to CapCut's fit-to-width (3840 src -> 2160 canvas)."""
    lay = layout(kind, a, o)
    if lay == "talk":
        S_ = 3.16 * punch; u, v, cy = 0.49, 0.55, CH / 2       # v 0.55: the face sits higher (v1 had too much headroom)
        band = CH
    else:
        u, v, S_ = o.get("focus") or (RING if kind == "ff" else PAGE)
        if lay == "full":
            S_ = max(S_, FULL_S); cy = CH / 2; band = CH
        else:
            cy = SEAM / 2; band = SEAM
    half_h = 1215 * S_
    v = min(max(v, cy / half_h), 1 - (band - cy) / half_h)
    u = min(max(u, 0.5 / S_), 1 - 0.5 / S_)
    tx = (-(u - 0.5) * 2160 * S_) / (CW / 2)
    ty = (CH / 2 + (v - 0.5) * 1215 * S_ - cy) / (CH / 2)
    return {"scale": round(S_, 4), "x": round(tx, 4), "y": round(ty, 4)}

def chunk_words(pieces):
    """Caption chunks in output time: readable 1-4 word phrases, broken at punctuation, real gaps and
    non-contiguous cuts; never overlapping; a minimum dwell."""
    toks, off, used = [], 0.0, set()
    for idx, (a, b, kind, o) in enumerate(pieces):
        sp = o.get("speed", 1.0)
        contig = idx > 0 and abs(pieces[idx - 1][1] - a) < 1e-3
        if kind != "ff" and not o.get("hold"):
            for w in WORDS:
                # overlap, not start-in-range: a word whose start Whisper put just before a trim still counts
                if id(w) not in used and w["e"] > a + 0.06 and w["s"] < b - 0.06 and w["w"].strip().lower() not in SKIP and w.get("p", 1) > 0.15:
                    used.add(id(w))      # a long word straddling a pause cut is captioned once (v2 showed "FOR FOR")
                    t0 = off + (max(w["s"], a) - a) / sp
                    t1 = off + (min(w["e"], b) - a) / sp
                    toks.append({"t0": t0, "t1": t1, "w": FIX.get(w["w"].strip().lower(), w["w"].strip()), "brk": not contig and not toks == []})
                    contig = True
        else:
            if toks:
                toks[-1]["end_section"] = True
        off += (b - a) / sp
    # normalise: glue "-day" style tokens, "Dex Screener" -> "DexScreener"
    norm = []
    for t in toks:
        joins = norm and (t["w"].startswith("-")
                          or (norm[-1]["w"].lower() == "deck" and t["w"].lower().startswith("screener"))
                          or (norm[-1]["w"].lower() == "robin" and t["w"].lower().startswith("hood")))
        if joins:
            prev = norm[-1]
            prev["w"] = ("Dex" if prev["w"].lower() == "deck" else prev["w"]) + t["w"]
            prev["t1"] = t["t1"]
            continue
        norm.append(dict(t))
    chunks, cur = [], []
    for t in norm:
        txt = re.sub(r"[.,!?]+$", "", t["w"]).upper()
        if cur and (t["brk"] or len(cur) >= 4 or len(" ".join(x[1] for x in cur)) + len(txt) > 18 or t["t0"] - cur[-1][2] > 0.6):
            chunks.append(cur); cur = []
        if txt:
            cur.append((t["t0"], txt, t["t1"], bool(re.search(r"[.,?!]$", t["w"]))))   # 4th: ends a clause
        if re.search(r"[.,?!]$", t["w"]) or t.get("end_section"):
            if cur:
                chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    # minimum dwell: a too-short chunk joins the PREVIOUS one (same sentence: "LET ME HELP YOU OUT"),
    # else the next one (v2 merged "OUT" forward into the next sentence)
    merged, k = [], 0
    while k < len(chunks):
        c = chunks[k]
        short = (c[-1][2] - c[0][0]) < 0.35
        if short and merged and not merged[-1][-1][3] and len(merged[-1]) + len(c) <= 5 and c[0][0] - merged[-1][-1][2] < 0.4:
            merged[-1] = merged[-1] + c
        elif short and k + 1 < len(chunks) and len(c) + len(chunks[k + 1]) <= 5 and chunks[k + 1][0][0] - c[-1][2] < 0.3:
            chunks[k + 1] = c + chunks[k + 1]
        else:
            merged.append(c)
        k += 1
    res = []
    for k, c in enumerate(merged):
        st = c[0][0]
        nxt = merged[k + 1][0][0] if k + 1 < len(merged) else None
        en = c[-1][2] + 0.15
        if nxt is not None and nxt - c[-1][2] < 0.5:
            en = nxt                         # hand straight over to the next chunk
        if nxt is not None:
            en = min(en, nxt - 0.02)         # never overlap
        words = [x[1] for x in c]
        hi = next((i for i, w in enumerate(words) if w.strip("$") in KEYWORDS), None)
        res.append({"start": round(st, 3), "end": round(max(en, st + 0.3), 3), "words": words, "hi": hi})
    for k in range(len(res) - 1):            # dwell padding must not create an overlap
        res[k]["end"] = min(res[k]["end"], round(res[k + 1]["start"] - 0.02, 3))
    return res

def render_caps(all_chunks):
    CAPS.mkdir(exist_ok=True)
    uniq = {}
    for c in all_chunks:
        key = " ".join(c["words"]) + f"|{c['hi']}"
        c["file"] = uniq.setdefault(key, f"cap{len(uniq):03d}.png")
    (CAPS / "caps.json").write_text(json.dumps([{"file": f, "words": k.split("|")[0].split(" "),
                                                  "hi": None if k.split("|")[1] == "None" else int(k.split("|")[1])}
                                                 for k, f in uniq.items()]), encoding="utf-8")
    subprocess.run(["node", str(EDIT / "graphics" / "render_captions.mjs")], check=True, capture_output=True)
    return json.loads((CAPS / "manifest.json").read_text())

BEDS = {"jonas": (AUD / "music-jonas.mp3", -8.9, 136.9), "verclub": (AUD / "music-verclub.mp3", -7.6, 130.3),
        "vaitsez": (AUD / "music-vaitsez.mp3", -8.2, 174.4)}
TRANS = {"zoom": ("Zoom_Transition", 0.45), "swipe": ("Swipe_Left", 0.35), "flash": ("White_Flash", 0.3)}

def man(name, d):
    return json.loads((d / "manifest.json").read_text())[name]

def main():
    plans = {sid: build_pieces(spec) for sid, spec in SHORTS.items()}
    chunks = {sid: chunk_words(P) for sid, P in plans.items()}
    capman = render_caps([c for v in chunks.values() for c in v])
    report = {}
    for sid, spec in SHORTS.items():
        P = plans[sid]
        segs, images, sfx = [], [], []
        off, talk_i, starts = 0.0, 0, []
        for i, (a, b, kind, o) in enumerate(P):
            sp = o.get("speed", 1.0)
            contig = i > 0 and abs(P[i - 1][1] - a) < 1e-3
            punch = 1.0
            if kind == "talk":
                if not contig:
                    talk_i += 1
                punch = 1.0 if talk_i % 2 else 1.08     # talking head only: hides its jump cut
            seg = {"in": a, "out": b, "frame": frame_for(kind, a, o, punch)}
            if kind == "ff":
                seg["speed"] = sp; seg["mute"] = True
            if o.get("hold"):
                seg["mute"] = True
            if layout(kind, a, o) == "split":
                seg["cam_overlay"] = {"rect": CAM_RECT, "clip": CAM_CLIP, "k0": round(CAM_K, 4)}
            segs.append(seg); starts.append(off)
            off += (b - a) / sp
        # the end: hold into silence only (never into his next words)
        last = segs[-1]
        nxt = min((w["s"] for w in WORDS if w["s"] > last["out"] - 0.02), default=last["out"] + 1.4)
        ext = max(0.0, min(1.4, nxt - 0.08 - last["out"])) if (P[-1][2] != "ff" and not P[-1][3].get("hold")) else 0.0
        last["out"] = round(last["out"] + ext, 3); off += ext
        total = round(off, 3)
        clamp = lambda st, d: max(0.0, round(min(d, total - st), 3))

        def at(t):
            for (a, b, kind, o), st in zip(P, starts):
                if a - 0.3 <= t <= b + 0.3:
                    return round(st + (min(max(t, a), b) - a) / o.get("speed", 1.0), 3)
            return None
        # transitions: only where the piece asks (real view changes), whoosh peak on the cut
        tr_times = []
        for i, (a, b, kind, o) in enumerate(P):
            if o.get("tr") and i > 0:
                name, d = TRANS[o["tr"]]
                segs[i - 1]["transition"] = {"name": name, "duration": d}
                sfx.append({"path": str(AUD / "sfx-whoosh.mp3"), "peak_at": round(starts[i], 3), "volume": 0.34})
                tr_times.append(starts[i])
        ff_i = [i for i, p in enumerate(P) if p[2] == "ff"]
        if ff_i:   # into the wait: a whoosh on the speed-up, no transition
            sfx.append({"path": str(AUD / "sfx-whoosh.mp3"), "peak_at": round(starts[ff_i[0]], 3), "volume": 0.3})
        # hook title: frame 0, full opacity, pops out
        hm = man(spec["hook"], GFXS)
        images.append({"path": str(GFXS / f"{spec['hook']}.png"), "start": 0.0, "duration": 2.6,
                       "x": CW // 2, "y": Y_TOP + 60, "scale": min(1.0, 2040 / hm["w"]), "pop": "out"})
        # payoff then closing line: the CTA starts after the last word, over the held shot
        last_word = max(c["end"] for c in chunks[sid])
        cta_at = round(max(min(last_word + 0.1, total - 1.6), total - 1.6 if P[-1][3].get("hold") else 0), 3)   # after a hold: the last 1.6 s
        # captions
        for c in chunks[sid]:
            if c["start"] >= total:
                continue
            cm = capman[c["file"]]
            pi = max(k for k, st in enumerate(starts) if st <= c["start"] + 1e-6)
            y = Y_CAP[layout(P[pi][2], P[pi][0], P[pi][3])]
            images.append({"path": str(CAPS / c["file"]), "start": c["start"], "duration": clamp(c["start"], c["end"] - c["start"]),
                           "x": CW // 2, "y": y, "scale": min(1.0, 2000 / cm["w"]), "pop": "in"})
        # cards: one at a time, cleared at the next card / section cut / CTA
        cards = [(at(t), name, d, at(clr) if clr else None) for t, name, d, clr in CARDS.get(sid, []) if at(t) is not None]
        cuts_out = sorted(tr_times)   # cards clear at section changes (transitions), not at small speech-repair cuts
        for k, (s0, name, d, clr) in enumerate(cards):
            s0 = max(s0, 0.5)                                     # below the hook card, so it can land on its line
            end = min([e for e in [clr, cta_at] + [c[0] for c in cards[k + 1:]] + [t for t in cuts_out if t > s0 + 1.5] if e] or [total])
            if not name.startswith(("ex-", "quote", "card-")):
                end = min(end, s0 + 3.2)          # info cards are brief emphasis; report excerpts / the key warning hold
            m = man(name, d)
            dur = clamp(s0, end - s0 - 0.05)
            if dur < 1.2:
                continue
            images.append({"path": str(d / f"{name}.png"), "start": round(s0, 3), "duration": dur,
                           "x": CW // 2, "y": Y_CARD, "scale": min(1.0, 2000 / m["w"])})
            if name == "ex-verdict":
                sfx.append({"path": str(AUD / "sfx-impact.mp3"), "start": round(s0, 3), "volume": 0.42})   # the payoff: impact, no pop
            else:
                sfx.append({"path": str(AUD / "pop.mp3"), "start": round(s0, 3), "volume": 0.26})
        # one current-step label (s2)
        if sid in STEPS:
            pts = [at(t) for t in STEPS[sid]]
            ends = pts[1:] + [at(1098.0)]
            for k, (s0, e0) in enumerate(zip(pts, ends)):
                s0 = max(s0, 2.7)
                if e0 - s0 < 0.8:
                    continue
                m = man(f"step-{k + 1}", GFXS)
                images.append({"path": str(GFXS / f"step-{k + 1}.png"), "start": round(s0, 3), "duration": clamp(s0, e0 - s0),
                               "x": CW // 2, "y": Y_TOP, "scale": min(1.0, 2000 / m["w"]), "pop": "in" if k == 0 else False})
        # the wait: one stage label + "time compressed", nothing in the bottom quarter
        if ff_i:
            s_ff, e_ff = at(344.0), at(1141.55)
            c0 = max(s_ff + 0.1, 2.65)       # never under the hook card
            images.append({"path": str(GFXS / "compressed.png"), "start": round(c0, 3), "duration": clamp(c0, at(1098.0) - c0),
                           "x": CW // 2, "y": Y_TOP, "scale": min(1.0, 2000 / man("compressed", GFXS)["w"]), "pop": "in"})
            for k in range(5):
                s0, e0 = at(STAGES[k]), at(STAGES[k + 1])
                if e0 - s0 < 0.6:
                    continue                      # a stage that would only flash is skipped
                m = man(f"stage-{k + 1}", GFXS)
                images.append({"path": str(GFXS / f"stage-{k + 1}.png"), "start": round(s0 + (0.1 if k == 0 else 0), 3),
                               "duration": clamp(s0, e0 - s0 - (0.1 if k == 0 else 0)),
                               "x": CW // 2, "y": 2560, "scale": min(1.0, 2000 / m["w"]), "pop": "in" if k == 0 else False})
            sfx.append({"path": str(AUD / "sfx-riser.mp3"), "peak_at": e_ff, "volume": 0.3})
        # closing line (payoff first, then the site)
        cm_ = man(spec["cta"], GFXS)
        images.append({"path": str(GFXS / f"{spec['cta']}.png"), "start": cta_at, "duration": clamp(cta_at, total - cta_at),
                       "x": CW // 2, "y": Y_CARD, "scale": min(1.0, 1950 / cm_["w"]), "pop": "in"})
        sfx.append({"path": str(AUD / "pop.mp3"), "start": cta_at, "volume": 0.24})
        # music: one bed; it lifts under the muted wait, then settles back
        path, lufs, length = BEDS[spec["bed"]]
        vol = lambda target: round(10 ** ((target - lufs) / 20), 3)
        if ff_i:
            s_ff, e_ff = at(344.0), at(1141.55)
            cuts_m = [(0.0, s_ff, -27.0), (s_ff, e_ff, -21.0), (e_ff, total, -27.0)]
        else:
            cuts_m = [(0.0, total, -27.0)]
        music, pos = [], 0.0
        for k, (m0, m1, tgt) in enumerate(cuts_m):
            if m1 - m0 < 0.1:
                continue
            music.append({"path": str(path), "at": round(m0, 3), "start_offset": round(m0 % length, 3),
                          "duration": round(min(m1 - m0, length - (m0 % length)), 3), "volume": vol(tgt),
                          "fade_in": 0.2 if k == 0 else 0.15, "fade_out": 1.0 if m1 >= total - 1e-3 else 0.15})
        edl = {"project": spec["title"], "source": MAIN, "resolution": [CW, CH], "fps": 30,
               "voice": {MAIN: VOICE}, "segments": segs, "images": images, "sfx": sfx, "music": music}
        (HERE / f"{sid}.edl.json").write_text(json.dumps(edl, indent=1), encoding="utf-8")
        # self-checks: nothing past the picture, no caption overlaps, nothing important in the bottom quarter
        ends_ = [im["start"] + im["duration"] for im in images]
        assert max(ends_) <= total + 1e-3, (sid, max(ends_), total)
        caps = sorted((im["start"], im["start"] + im["duration"]) for im in images if "caps" in im["path"])
        assert all(caps[k][1] <= caps[k + 1][0] + 1e-3 for k in range(len(caps) - 1)), sid
        for im in images:
            if "caps" in im["path"] or "out_shorts" in im["path"] or "out" in im["path"]:
                h = (capman.get(Path(im["path"]).name) or {}).get("h") or 0
                assert im["y"] + h * im.get("scale", 1) / 2 <= SAFE_BOTTOM + 60, (sid, im["path"], im["y"])
        report[sid] = (total, len(segs), len(chunks[sid]), sum(1 for s in segs if s.get("transition")))
    for sid, (t, n, c, tr) in report.items():
        print(f"{sid}: {t:5.1f}s  {n:2d} pieces  {c:3d} caption chunks  {tr} transitions  -> {SHORTS[sid]['title']}")

if __name__ == "__main__":
    main()
