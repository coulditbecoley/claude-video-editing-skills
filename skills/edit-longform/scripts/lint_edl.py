"""Pre-build lint for an edit EDL (CapCut and Rendered MP4 modes, long-form and Shorts).

    python lint_edl.py <edit.edl.json> [--voice <processed voice wav>] [--words <whisper words json>] [--json out.json]
    python lint_edl.py --self-test

FAIL (exit 1):
  - invalid timeline input: non-finite or negative in/out, out <= in, speed <= 0 (checked before any arithmetic)
  - a missing media file: image PNG, every frame 000..frames-1 of an image's PNG sequence, sfx, music, voice
  - an audio cut edge inside a word (video-use rule 6). Needs BOTH signals: the edge is inside a transcript word's
    span AND the voice shows no boundary within +/-30 ms (no -40 dB quiet run, no dip 12 dB below the local speech
    level). Missing voice or words means NOT CHECKED, never FAIL.
  - a graphic under its hard floor (qa_lib.FLOORS: 1.5 s, taste.md accepted; accents 0.5 s)
  - an sfx peak_at outside the timeline (it is an output-timeline target; render_mp4 subtracts the sample's peak)
WARN:
  - an audio cut edge in a quiet run under 400 ms ("tight" under 150 ms: the step 2 rule says don't cut there
    unless re-heard; lint can't hear, so it warns instead of failing)
  - speech inside a transition clearance (0.35 s after the last word / 0.25 s before the first; taste.md confirmed)
  - a graphic under its readable floor, a graphic entering or leaving inside a transition
  - under 1 s from the last audible word to the start of the closing fade (or the end)
  - NOT CHECKED notes when words or voice are missing
Voice mapping follows render_mp4 cmd_audio exactly: an unmuted piece plays voice from (in - av_offset) for its
timeline length (out - in) / speed, at normal rate (speed-ups are not time-stretched). Audio boundaries are found on
that mapping, not on picture in/out, so an av_offset-only jump is a boundary (audit r2 #4).
Transcript precedence (shared with render_mp4 check): --words, then the EDL's "words", then <edl dir>/main.wav.literal.json,
main.wav.words.json. A missing explicit transcript is a FAIL. Words count where they OVERLAP a piece's voice range.
The closing fade is an image with pop "fade" that runs to the end; anything else measures to the end.
"""
import argparse, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import qa_lib  # noqa: E402

GAP_TIGHT, GAP_WARN = 0.150, 0.400
END_HOLD = 1.0
TR_AFTER, TR_BEFORE = 0.35, 0.25
WORD_IN, WORD_OUT = 0.04, 0.08   # ponytail: interior margins; Whisper starts are good, ends run long (SKILL.md step 2)


def load_words(path):
    j = json.load(open(path, encoding="utf-8"))
    segs = j["segments"] if isinstance(j, dict) else j
    return sorted((float(w["s"]), float(w["e"]), w["w"].strip()) for s in segs for w in s.get("words", []))


def resolve_words(edl_path, E, cli=None):
    """(path or None, error or None). One precedence for lint and check (audit r3 #8): --words, then the EDL's
    "words" (relative to the EDL), then <edl dir>/main.wav.literal.json, main.wav.words.json. An explicit path that
    doesn't exist is an error, never silently swapped for a default."""
    d = os.path.dirname(os.path.abspath(edl_path))
    for label, v in (("--words", cli), ("EDL 'words'", E.get("words"))):
        if v:
            pth = v if os.path.isabs(v) else os.path.join(d, v)
            return (pth, None) if os.path.exists(pth) else (None, f"{label} transcript not found: {pth}")
    for f in ("main.wav.literal.json", "main.wav.words.json"):
        if os.path.exists(os.path.join(d, f)):
            return os.path.join(d, f), None
    return None, None


def word_at(words, t):
    """The word whose interior (start + WORD_IN .. end - WORD_OUT) contains t, else None."""
    import bisect
    k = bisect.bisect_right(words, (t, float("inf"), "")) - 1
    for s, e, w in words[max(0, k - 1):k + 1]:
        if s + WORD_IN < t < e - WORD_OUT:
            return w, s, e
    return None


def _num(x):
    """A real JSON number (not a string, not a bool) that is finite."""
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def validate(E):
    """Timeline input errors, before any arithmetic (audit r2 #8, r3 #7): JSON numbers only (a "3" string or a bool
    is refused, not coerced), finite, in >= 0, out > in, speed > 0, finite av_offset, positive transition durations,
    image start/duration, integer sequence frame counts."""
    bad = []
    for i, s in enumerate(E.get("segments", [])):
        vals = {k: s.get(k, d) for k, d in (("in", None), ("out", None), ("speed", 1.0), ("av_offset", 0.0))}
        wrong = [k for k, v in vals.items() if not _num(v)]
        if wrong:
            bad.append(f"segment {i}: {', '.join(wrong)} must be finite numbers")
            continue
        if vals["in"] < 0:
            bad.append(f"segment {i}: in {vals['in']} is negative")
        elif vals["out"] <= vals["in"]:
            bad.append(f"segment {i}: out {vals['out']} <= in {vals['in']}")
        elif vals["speed"] <= 0:
            bad.append(f"segment {i}: speed {vals['speed']} must be > 0")
        tr = s.get("transition")
        if tr is not None and not (_num(tr.get("duration", 0.5)) and tr.get("duration", 0.5) > 0):
            bad.append(f"segment {i}: transition duration must be a positive number")
    for n, im in enumerate(E.get("images", [])):
        if not (_num(im.get("start")) and _num(im.get("duration")) and im["duration"] > 0):
            bad.append(f"images[{n}]: start/duration must be numbers, duration > 0")
        sq = im.get("seq")
        if sq is not None and not (isinstance(sq.get("frames"), int) and not isinstance(sq.get("frames"), bool)
                                   and sq["frames"] > 0):
            bad.append(f"images[{n}]: seq.frames must be a positive integer")
    if not E.get("segments"):
        bad.append("no segments")
    return bad


def timeline(E):
    P, off = [], 0.0
    for i, s in enumerate(E["segments"]):
        sp = float(s.get("speed", 1.0))
        d = (s["out"] - s["in"]) / sp
        av = float(s.get("av_offset", 0.0))
        P.append({"i": i, "s": s, "t0": off, "t1": off + d, "mute": bool(s.get("mute")),
                  "v0": s["in"] - av, "v1": s["in"] - av + d})       # audible voice range, render_mp4 semantics
        off += d
    contig = [i > 0 and abs(E["segments"][i - 1]["out"] - s["in"]) < 1e-3 for i, s in enumerate(E["segments"])]
    return P, off, contig


def audio_boundaries(P):
    """Indices i where the audible voice is discontinuous between piece i-1 and i."""
    out = []
    for i in range(1, len(P)):
        a, b = P[i - 1], P[i]
        if a["mute"] and b["mute"]:
            continue
        if not a["mute"] and not b["mute"] and abs(a["v1"] - b["v0"]) < 1e-3:
            continue
        out.append(i)
    return out


def seq_missing(im):
    sq = im.get("seq")
    if not sq:
        return []
    v = sq["dir"].rstrip("/\\") + ".mp4"
    if os.path.exists(v):                      # video-backed sequence (render_mp4.seq_video): no PNG frames needed
        import subprocess
        r = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                            "stream=nb_read_packets", "-of", "csv=p=0", v], capture_output=True, text=True)
        try:
            n = int(r.stdout.strip().rstrip(","))
        except ValueError:
            return [f"{v} (unreadable)"]
        return [f"{v} (has {n} frames, needs {int(sq['frames'])})"] if n < int(sq["frames"]) else []
    if not os.path.isdir(sq["dir"]):
        return [sq["dir"]]
    return [os.path.join(sq["dir"], f"{k:03d}.png") for k in range(int(sq["frames"]))
            if not os.path.exists(os.path.join(sq["dir"], f"{k:03d}.png"))]


def fade_start(E, total):
    """Start of the closing fade, or the end. Only an image the renderer actually fades in (pop == "fade") that runs
    to the end counts; a static page cover held to the end is not a fade (audit r3 #4)."""
    ends = [float(im["start"]) for im in E.get("images", [])
            if im.get("pop") == "fade" and float(im["start"]) + float(im["duration"]) >= total - 0.05]
    return min(ends) if ends else total


def audible_words(words, p):
    """Words audible in piece p, by interval OVERLAP with its voice range (audit r3 #3: a word that starts before the
    piece but runs into it is audible), clipped to the range and mapped to output time: (out_start, out_end, word)."""
    out = []
    for s_, e, w in words or []:
        a, b = max(s_, p["v0"]), min(e, p["v1"])
        if b > a:
            out.append((p["t0"] + a - p["v0"], p["t0"] + b - p["v0"], w))
    return out


def lint(E, voice=None, words=None):
    issues = []

    def add(level, t, msg):
        issues.append({"level": level, "t": round(float(t), 3), "msg": msg})

    for m in validate(E):
        add("FAIL", 0, m)
    if issues:
        return issues, 0.0                       # no derived checks on an invalid timeline
    P, total, contig = timeline(E)

    # media
    for kind in ("images", "sfx", "music"):
        for n, x in enumerate(E.get(kind, [])):
            vseq = x.get("seq") and os.path.exists(x["seq"]["dir"].rstrip("/\\") + ".mp4")   # path unused then
            if not os.path.exists(x["path"]) and not vseq:
                add("FAIL", float(x.get("start", x.get("at", x.get("peak_at", 0)))), f"{kind}[{n}] missing: {x['path']}")
    for n, im in enumerate(E.get("images", [])):
        miss = seq_missing(im)
        if miss:
            add("FAIL", im["start"], f"images[{n}] sequence incomplete: {len(miss)} missing, first {miss[0]}")
    for src, wav in E.get("voice", {}).items():
        if not os.path.exists(wav):
            add("FAIL", 0, f"voice wav missing: {wav}")
    t_ = 0.0
    for n, s in enumerate(E["segments"]):                  # per-segment picture source (render_mp4 "src")
        if s.get("src") and not os.path.exists(s["src"]):
            add("FAIL", t_, f"segments[{n}] src missing: {s['src']}")
        t_ += (s["out"] - s["in"]) / s.get("speed", 1.0)
    for n, s in enumerate(E.get("sfx", [])):
        t = float(s.get("peak_at", s.get("start", 0)))
        if not (math.isfinite(t) and 0 <= t <= total):
            add("FAIL", t if math.isfinite(t) else 0, f"sfx[{n}] at {t}s is outside the 0-{total:.2f}s timeline")

    # audio cut edges
    if voice is None and E.get("voice"):
        voice = list(E["voice"].values())[0]
    a = qa_lib.load_mono(voice) if voice and os.path.exists(voice) else None
    sr = qa_lib.SR
    if a is not None:
        vlen = len(a) / sr
        for p in P:
            if not p["mute"] and (p["v0"] < -1e-3 or p["v1"] > vlen + 1e-3):
                add("FAIL", p["t0"], f"segment {p['i']}: voice range {p['v0']:.2f}-{p['v1']:.2f}s is outside the "
                                     f"{vlen:.2f}s voice wav")
    bounds = audio_boundaries(P)
    if bounds and a is None:
        add("WARN", 0, "voice wav unavailable: cut-gap and word-interior checks NOT CHECKED")
    if bounds and not words:
        add("WARN", 0, "no word transcript: word-interior, transition-clearance and end-hold word checks NOT CHECKED")
    edges = []
    for i in bounds:
        edges += [(i, "out", P[i - 1], P[i - 1]["v1"], P[i]["t0"]), (i, "in", P[i], P[i]["v0"], P[i]["t0"])]
    voiced = [p for p in P if not p["mute"]]
    if voiced:                       # the very first and last audible edges are cuts too (audit r3 #3)
        edges = [(0, "in", voiced[0], voiced[0]["v0"], voiced[0]["t0"])] + edges \
                + [(len(P), "out", voiced[-1], voiced[-1]["v1"], voiced[-1]["t1"])]
    for i, label, piece, at, t_out in edges:
        cur = {"t0": t_out}
        if True:
            if piece["mute"] or a is None:
                continue
            g = qa_lib.quiet_len_near(a, sr, at)
            dip = qa_lib.dip_near(a, sr, at)
            hit = word_at(words, at) if words else None
            where = (f"cut {i} ({label} edge, voice {at:.2f}s)" if 0 < i < len(P)
                     else f"{'opening' if label == 'in' else 'closing'} edge (voice {at:.2f}s)")
            if hit and g == 0.0 and not dip:
                add("FAIL", cur["t0"], f"{where} is inside '{hit[0]}' ({hit[1]:.2f}-{hit[2]:.2f}s) in flat speech "
                                       f"(no pause or dip within 30 ms) - snap it to a word boundary")
            elif g < GAP_WARN:
                tag = "tight" if g < GAP_TIGHT else "re-hear"
                add("WARN", cur["t0"], f"{where}: quiet run {g * 1000:.0f} ms ({tag})")

    # transition clearances, in output time through the voice mapping
    windows = []
    for k, p in enumerate(P[:-1]):
        tr = p["s"].get("transition")
        if not tr:
            continue
        half = float(tr.get("duration", 0.5)) / 2
        windows.append((p["t1"] - half, p["t1"] + half))
        if not words:
            continue
        b = P[k + 1]
        if not p["mute"]:
            ends = [oe for os_, oe, w in audible_words(words, p)]
            if ends:
                clear = (p["t1"] - half) - max(ends)
                if clear < TR_AFTER:
                    add("WARN", p["t1"], f"transition at {p['t1']:.2f}s starts {clear:.2f}s after the last word "
                                         f"(want >= {TR_AFTER}s)")
        if not b["mute"]:
            starts = [os_ for os_, oe, w in audible_words(words, b)]
            if starts:
                clear = min(starts) - (p["t1"] + half)
                if clear < TR_BEFORE:
                    add("WARN", p["t1"], f"transition at {p['t1']:.2f}s ends {clear:.2f}s before the first word "
                                         f"(want >= {TR_BEFORE}s)")

    # graphics: floors apply to the VISIBLE interval (audit r4 #3); off-timeline graphics never show
    visible = []
    for n, im in enumerate(E.get("images", [])):
        a0, a1 = float(im["start"]), float(im["start"]) + float(im["duration"])
        if a0 < -1e-3 or a0 >= total - 1e-3:
            add("FAIL", max(0.0, min(a0, total)), f"images[{n}] {os.path.basename(im['path'])} starts at {a0:.2f}s, "
                                                  f"outside the 0-{total:.2f}s timeline: it never shows")
            continue
        if a1 > total + 1e-3:
            add("WARN", a0, f"{os.path.basename(im['path'])} runs past the end ({a1:.2f}s > {total:.2f}s): "
                            f"only {total - a0:.2f}s shows")
        visible.append(dict(im, duration=min(a1, total) - a0))
    for g in qa_lib.graphic_issues(visible):
        add(g["level"], g["t"], f"{g['path']}: {g['msg']}")
    for n, im in enumerate(E.get("images", [])):
        if qa_lib.graphic_kind(im) == "cover":
            continue
        a0, a1 = float(im["start"]), float(im["start"]) + float(im["duration"])
        for w0, w1 in windows:
            if w0 < a0 < w1 or w0 < a1 < w1:
                add("WARN", a0, f"{os.path.basename(im['path'])} enters or leaves inside a transition ({w0:.2f}-{w1:.2f}s)")
                break

    # end hold: last audible word (any voiced piece) to the closing fade
    fs = fade_start(E, total)
    if words:
        last = None
        for p in P:
            if p["mute"]:
                continue
            for os_, oe, w in audible_words(words, p):
                last = oe if last is None else max(last, oe)
        if last is not None and fs - last < END_HOLD:
            add("WARN", last, f"only {fs - last:.2f}s from the last spoken word to the "
                              f"{'closing fade' if fs < total else 'end'} (want >= {END_HOLD}s)")
    else:
        add("WARN", total, "end hold NOT CHECKED (no word transcript)")
    return issues, total


def _check():
    import subprocess, tempfile
    import numpy as np
    sr = qa_lib.SR
    tone = (0.2 * np.sin(2 * np.pi * 220 * np.arange(sr) / sr)).astype(np.float32)
    v = np.concatenate([tone, np.zeros(int(0.5 * sr), np.float32), tone, tone])   # speech 0-1, gap 1-1.5, 1.5-3.5
    d = tempfile.mkdtemp()
    wav = os.path.join(d, "v.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-", wav],
                   input=v.tobytes(), check=True)
    E = {"voice": {"src": wav}, "images": [], "sfx": [], "music": [],
         "segments": [{"in": 0.0, "out": 1.2}, {"in": 1.4, "out": 2.5}, {"in": 2.5, "out": 2.6}, {"in": 3.0, "out": 3.4}]}
    words = [(0.0, 1.0, "one"), (1.5, 2.55, "two"), (2.9, 3.5, "three")]
    iss, total = lint(E, words=words)
    fails = [x for x in iss if x["level"] == "FAIL"]
    # cut 3's in edge and the closing edge (3.4 s, still inside "three") are both mid-word
    assert sorted(x["msg"].split(" (")[0] for x in fails) == ["closing edge", "cut 3"], iss
    assert any("cut 3 (out edge" in x["msg"] and "tight" in x["msg"] for x in iss), iss
    assert not any("cut 1" in x["msg"] for x in iss), iss
    assert any("last spoken word" in x["msg"] for x in iss)
    # a Whisper word stretched over the real gap must not FAIL a cut placed in that gap
    iss2, _ = lint(E, words=[(0.0, 1.45, "one"), (1.5, 2.55, "two"), (2.9, 3.5, "three")])
    assert not any("cut 1" in x["msg"] for x in iss2), iss2
    # av_offset: everything shifted +0.3 s in the picture with av_offset 0.3 reads the same voice
    E3 = dict(E, segments=[dict(s_, **{"in": s_["in"] + 0.3, "out": s_["out"] + 0.3, "av_offset": 0.3})
                           for s_ in E["segments"]])
    assert sorted(x["msg"].split(" (")[0] for x in lint(E3, words=words)[0] if x["level"] == "FAIL") == ["closing edge", "cut 3"]
    # inside a word 150 ms from a long gap: still FAIL (no "nearest silence" rescue)
    E4 = dict(E, segments=[{"in": 0.0, "out": 0.85}, {"in": 1.5, "out": 3.4}])
    assert any(x["level"] == "FAIL" and "inside 'one'" in x["msg"] for x in lint(E4, words=words[:2])[0])
    # muted pieces are skipped
    E5 = dict(E, segments=[{"in": 0.0, "out": 0.5, "mute": True}, {"in": 0.7, "out": 0.9, "mute": True}])
    assert not any(x["msg"].startswith("cut") for x in lint(E5, words=words)[0])
    # transition clearance
    E6 = dict(E, segments=[{"in": 0.0, "out": 1.2, "transition": {"name": "Dissolve", "duration": 0.4}},
                           {"in": 1.0, "out": 3.4}])
    m6 = [x["msg"] for x in lint(E6, words=[(0.0, 1.0, "one"), (1.5, 2.55, "two")])[0]]
    assert any("after the last word" in m for m in m6) and not any("before the first word" in m for m in m6), m6
    # audit r2 #3A: hold is measured to the closing fade, not the end
    png = os.path.join(d, "black.png")
    open(png, "wb").write(b"x")
    E7 = dict(E, segments=[{"in": 0.0, "out": 3.4}], images=[{"path": png, "start": 2.75, "duration": 0.65, "pop": "fade"}])
    m7 = [x["msg"] for x in lint(E7, words=[(1.5, 1.9, "two")])[0]]
    assert any("closing fade" in m for m in m7), m7
    # audit r2 #3B: an unmuted speed-up plays voice 1:1 from in, so a word at source 2.9 ends 0.1 s before the end
    E8 = dict(E, segments=[{"in": 0.0, "out": 6.0, "speed": 2.0}])
    m8 = [x["msg"] for x in lint(E8, words=[(2.5, 2.9, "w")])[0]]
    assert any("only 0.10s" in m for m in m8), m8
    # audit r2 #4: picture-contiguous but av_offset jump is an audio boundary and gets checked
    E9 = dict(E, segments=[{"in": 0.0, "out": 1.3}, {"in": 1.3, "out": 3.4, "av_offset": -1.6}])
    assert audio_boundaries(timeline(E9)[0]) == [1]
    # audit r2 #5A: words but no voice -> NOT CHECKED, not FAIL
    E10 = dict(E, voice={"src": os.path.join(d, "nope.wav")})
    i10 = lint(E10, words=words)[0]
    assert any("NOT CHECKED" in x["msg"] for x in i10) and not any("inside" in x["msg"] for x in i10), i10
    # audit r2 #8: invalid input FAILs before arithmetic
    assert any("negative" in x["msg"] for x in lint(dict(E, segments=[{"in": -2, "out": 3}]))[0])
    assert any("speed 0" in x["msg"] for x in lint(dict(E, segments=[{"in": 0, "out": 3, "speed": 0}]))[0])
    # audit r2 #2: a sequence with its folder or an interior frame missing FAILs
    sd = os.path.join(d, "seq")
    os.makedirs(sd)
    for k in (0, 2):
        open(os.path.join(sd, f"{k:03d}.png"), "wb").write(b"x")
    E11 = dict(E, images=[{"path": png, "start": 0.0, "duration": 2.0, "seq": {"dir": sd, "frames": 3}},
                          {"path": png, "start": 0.0, "duration": 2.0, "seq": {"dir": sd + "x", "frames": 3}}])
    m11 = [x["msg"] for x in lint(E11, words=words)[0] if x["level"] == "FAIL"]
    assert sum("sequence incomplete" in m for m in m11) == 2, m11
    # video-backed sequence (<dir>.mp4, no PNGs): enough frames passes, too few FAILs; a missing segment src FAILs
    vd = os.path.join(d, "scene")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=red:s=64x36:r=60", "-frames:v", "5",
                    "-pix_fmt", "yuv420p", vd + ".mp4"], check=True)
    seqv = lambda k: dict(E, images=[{"path": png, "start": 0.0, "duration": 2.0, "seq": {"dir": vd, "frames": k}}])
    assert not any("sequence incomplete" in x["msg"] for x in lint(seqv(5), words=words)[0])
    assert any("has 5 frames, needs 6" in x["msg"] for x in lint(seqv(6), words=words)[0] if x["level"] == "FAIL")
    m17 = lint(dict(E, segments=[{"in": 0.0, "out": 1.2, "src": os.path.join(d, "other.mp4")}]), words=words)[0]
    assert any(x["level"] == "FAIL" and "src missing" in x["msg"] for x in m17), m17
    # audit r3 #4: a static page cover held to the end is not a fade
    cov = os.path.join(d, "cover-page.png")
    open(cov, "wb").write(b"x")
    E12 = dict(E, segments=[{"in": 0.0, "out": 3.4}], images=[{"path": cov, "start": 0.0, "duration": 3.4, "pop": False}])
    m12 = [x["msg"] for x in lint(E12, words=[(1.5, 1.9, "two")])[0]]
    assert not any("closing fade" in m or "spoken word" in m for m in m12), m12
    # audit r3 #3: a word overlapping the whole kept piece is audible (end hold sees it); opening mid-word FAILs
    E13 = dict(E, segments=[{"in": 2.0, "out": 3.0}])
    m13 = [x for x in lint(E13, words=[(1.5, 3.1, "long")])[0]]
    assert any("spoken word" in x["msg"] for x in m13), m13
    assert any(x["level"] == "FAIL" and "opening edge" in x["msg"] for x in m13), m13
    # audit r3 #7: strings, bools, NaN offset, bad transition, bad seq count, voice range outside the wav
    assert any("must be finite numbers" in x["msg"] for x in lint(dict(E, segments=[{"in": "0", "out": "3"}]))[0])
    assert any("av_offset" in x["msg"] for x in lint(dict(E, segments=[{"in": 0, "out": 3, "av_offset": float("nan")}]))[0])
    assert any("transition duration" in x["msg"] for x in
               lint(dict(E, segments=[{"in": 0, "out": 1, "transition": {"duration": 0}}, {"in": 1, "out": 2}]))[0])
    assert any("seq.frames" in x["msg"] for x in
               lint(dict(E, images=[{"path": png, "start": 0, "duration": 2, "seq": {"dir": sd, "frames": "3"}}]))[0])
    assert any("outside the" in x["msg"] for x in lint(dict(E, segments=[{"in": 3.0, "out": 9.0}]))[0])
    # audit r3 #8: explicit transcript wins over defaults; a missing explicit one is an error, not a fallback
    edl = os.path.join(d, "e.edl.json")
    open(os.path.join(d, "main.wav.literal.json"), "w").write("{}")
    open(os.path.join(d, "chosen.json"), "w").write("{}")
    assert resolve_words(edl, {"words": "chosen.json"}) == (os.path.join(d, "chosen.json"), None)
    assert resolve_words(edl, {}) == (os.path.join(d, "main.wav.literal.json"), None)
    assert resolve_words(edl, {"words": "gone.json"})[0] is None
    assert resolve_words(edl, {"words": "chosen.json"}, cli=os.path.join(d, "main.wav.literal.json"))[0].endswith("literal.json")
    # audit r4 #3: a 3 s read graphic starting 1 s before the end shows 1 s -> FAIL; one past the end -> FAIL;
    # one ending exactly at the end -> fine
    rd = os.path.join(d, "read-info.png")
    open(rd, "wb").write(b"x")
    base = dict(E, segments=[{"in": 0.0, "out": 3.4}])
    m14 = [(x["level"], x["msg"]) for x in lint(dict(base, images=[{"path": rd, "start": 2.4, "duration": 3.0}]), words=words)[0]]
    assert ("FAIL" in [l for l, m in m14 if "1.00s" in m]) and any("runs past the end" in m for _, m in m14), m14
    m15 = [x for x in lint(dict(base, images=[{"path": rd, "start": 9.0, "duration": 2.0}]), words=words)[0]]
    assert any(x["level"] == "FAIL" and "never shows" in x["msg"] for x in m15), m15
    m16 = [x for x in lint(dict(base, images=[{"path": rd, "start": 0.4, "duration": 3.0}]), words=words)[0]]
    assert not any("past the end" in x["msg"] or "never shows" in x["msg"] for x in m16), m16
    print("lint_edl self-test OK")


if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] == "--self-test":
        _check()
        sys.exit(0)
    ap = argparse.ArgumentParser()
    ap.add_argument("edl")
    ap.add_argument("--voice")
    ap.add_argument("--words")
    ap.add_argument("--json")
    ap.add_argument("-v", "--verbose", action="store_true", help="print every WARN (default: grouped)")
    a = ap.parse_args()
    E = json.load(open(a.edl, encoding="utf-8"))
    wp, werr = resolve_words(a.edl, E, a.words)
    words = load_words(wp) if wp else None
    print(f"words: {wp or werr or 'none (word checks NOT CHECKED)'}")
    iss, total = lint(E, a.voice, words)
    if werr:
        iss.insert(0, {"level": "FAIL", "t": 0.0, "msg": werr})
    iss.sort(key=lambda x: (x["level"] != "FAIL", x["t"]))
    qa_lib.print_items(iss, a.verbose)
    nf = sum(x["level"] == "FAIL" for x in iss)
    print(f"{nf} FAIL, {len(iss) - nf} WARN, timeline {total:.2f}s")
    json.dump(iss, open(a.json or os.path.splitext(os.path.abspath(a.edl))[0] + ".lint.json", "w"), indent=1)
    sys.exit(1 if nf else 0)
