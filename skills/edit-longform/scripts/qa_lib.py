"""Shared QA helpers for headless edits: render_mp4.py `check`, lint_edl.py, and the Shorts qa_round.py.

Import by path:  sys.path.insert(0, r"%USERPROFILE%\\.claude\\skills\\edit-longform\\scripts"); import qa_lib
Self-test:       python qa_lib.py
"""
import json, os, subprocess

import numpy as np

SR = 48000

# ---------- container / loudness ----------

def probe(path):
    """frames (counted), duration, size, fps, audio codec + rate of a finished file."""
    out = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-show_entries",
                          "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,nb_read_packets,sample_rate",
                          "-of", "json", path], capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    n, d = (int(x) for x in v["r_frame_rate"].split("/"))
    return {"frames": int(v["nb_read_packets"]), "duration": float(j["format"]["duration"]),
            "width": v["width"], "height": v["height"], "fps": n / d,
            "acodec": a and a["codec_name"], "asr": a and int(a["sample_rate"])}


def loudness(path, runner=subprocess.run):
    """(integrated LUFS, true peak dBTP) via ebur128. Raises when the decode fails or the numbers aren't finite:
    ffmpeg prints a summary for a decoded prefix even when it exits nonzero (audit r2 #6)."""
    r = runner(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-map", "0:a:0", "-af", "ebur128=peak=true",
                "-f", "null", "-"], capture_output=True, text=True)
    e = r.stderr
    if r.returncode != 0 or "Summary:" not in e:
        raise RuntimeError(f"loudness decode failed (exit {r.returncode})")
    summary = e[e.rindex("Summary:"):]
    i = float(summary.split(" I:")[1].split()[0])
    tp = float(summary.split("Peak:")[1].split()[0])
    if not (np.isfinite(i) and np.isfinite(tp)):
        raise RuntimeError(f"loudness not finite: {i} / {tp}")
    return i, tp


_MONO = {}


def load_mono(path, sr=SR):
    """Decoded mono float32 audio. Memoised per (path, size, mtime_ns, rate), keeping the last 2 files: a Shorts
    batch lints 8 specs against one source voice (audit r6: 16.8 s -> 1.9 s). A changed file is decoded again."""
    import os as _os
    st = _os.stat(path)
    k = (_os.path.abspath(path), st.st_size, st.st_mtime_ns, sr)
    if k not in _MONO:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        if len(_MONO) >= 2:
            _MONO.pop(next(iter(_MONO)))
        _MONO[k] = np.frombuffer(raw, np.float32)
    return _MONO[k]

# ---------- cut clicks ----------

CLICK_WIN = 0.015     # s each side of the cut
CLICK_CTX = 0.300     # s of context each side for the baseline
CLICK_WARN = 4.0      # ponytail: step vs context ratio that earns a "listen here"; heuristic, not a certificate
CLICK_FAIL = 8.0      # and a step this far above context, at least CLICK_FAIL_DB loud, is a defect
CLICK_FLOOR_DB = -50  # a "spike" quieter than this is inaudible; never flag
CLICK_FAIL_DB = -30


def click_scan(a, sr, times):
    """For each timeline time, compare the sharpest sample step (first difference = crude high-pass) inside
    +/-CLICK_WIN with the 95th percentile of steps in the surrounding context. A click is a step far above
    what the neighbouring audio does; a word onset usually is not (speech already has steep steps).
    Run it on the VOICE stem: the full mix has intentional SFX hits on cuts. level: FAIL, WARN (listen) or None."""
    d = np.abs(np.diff(a, prepend=a[:1]))
    w, c = int(CLICK_WIN * sr), int(CLICK_CTX * sr)
    res = []
    for t in times:
        k = int(round(t * sr))
        lo, hi = max(0, k - w), min(len(d), k + w)
        if hi <= lo or k + w > len(d):
            res.append({"t": round(t, 3), "ratio": None, "peak_db": None, "level": "NOT CHECKED", "fail": False})
            continue
        peak = float(d[lo:hi].max())
        ctx = np.concatenate([d[max(0, k - c):lo], d[hi:min(len(d), k + c)]])
        base = float(np.percentile(ctx, 95)) if len(ctx) else 0.0
        ratio = peak / max(base, 1e-6)
        peak_db = 20 * np.log10(max(peak, 1e-9))
        level = None
        if peak_db > CLICK_FLOOR_DB and ratio > CLICK_WARN:
            level = "FAIL" if ratio > CLICK_FAIL and peak_db > CLICK_FAIL_DB else "WARN"
        res.append({"t": round(t, 3), "ratio": round(ratio, 2), "peak_db": round(peak_db, 1), "level": level,
                    "fail": level == "FAIL"})
    return res

# ---------- silence runs (same rule as the edits' runs.py: -40 dB, 10 ms frames, runs >= 40 ms) ----------

QUIET_DB, HOP, MIN_RUN = -40.0, 0.01, 0.04


def frame_db(a, sr, t0, t1):
    i0, i1, h = max(0, int(t0 * sr)), min(len(a), int(t1 * sr)), int(HOP * sr)
    x = a[i0:i1]
    n = len(x) // h
    if n == 0:
        return np.array([]), t0
    r = np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(1) + 1e-12)
    return 20 * np.log10(r), i0 / sr


def quiet_len_at(a, sr, t, span=1.5):
    """Length (s) of the quiet run containing time t; 0.0 when t sits in sound. Short runs (< MIN_RUN) of the
    other kind are absorbed, as runs.py does."""
    db, base = frame_db(a, sr, t - span, t + span)
    if not len(db):
        return 0.0
    q = db < QUIET_DB
    k = min(len(q) - 1, max(0, int(round((t - base) / HOP))))
    m = int(MIN_RUN / HOP)

    def run_edge(i, step):
        while 0 <= i + step < len(q):
            j = i + step
            if not q[j]:
                n = 0                                   # count the sound blip; absorb it if short
                while 0 <= j < len(q) and not q[j]:
                    n, j = n + 1, j + step
                if n >= m or not (0 <= j < len(q)):
                    return i
                i = j
            else:
                i = j
        return i

    if not q[k]:
        # inside sound: a blip shorter than MIN_RUN between quiet frames still counts as quiet
        lo = hi = k
        while lo > 0 and not q[lo - 1]:
            lo -= 1
        while hi < len(q) - 1 and not q[hi + 1]:
            hi += 1
        if hi - lo + 1 >= m:
            return 0.0
    return (run_edge(k, 1) - run_edge(k, -1) + 1) * HOP

def quiet_len_near(a, sr, t, tol=0.03):
    """Longest quiet run within +/-tol of t (edges are placed on 10 ms runs, so allow a few frames of slack)."""
    return max(quiet_len_at(a, sr, t + k * HOP) for k in range(-int(tol / HOP), int(tol / HOP) + 1))

DIP_DB = 12.0   # ponytail: a word boundary in connected speech dips this far below the local speech level (REF: 19 dB)


def dip_near(a, sr, t, tol=0.03):
    """True when a frame within +/-tol of t sits DIP_DB below the local speech level (75th percentile of +/-0.5 s).
    Connected speech never reaches -40 dB between words, but the boundary still dips; flat speech does not."""
    db, base = frame_db(a, sr, t - 0.5, t + 0.5)
    if not len(db):
        return False
    level = float(np.percentile(db, 75))
    k0 = max(0, int(round((t - tol - base) / HOP)))
    k1 = min(len(db), int(round((t + tol - base) / HOP)) + 1)
    return bool(k1 > k0 and db[k0:k1].min() <= level - DIP_DB)

# ---------- graphics durations ----------

FLOORS = {            # kind: (fail below, warn below) seconds; video-use numbers, provisional (taste.md)
    "read":    (1.5, 3.0),    # fail: taste.md (accepted) "never under 1.5 s"; warn: video-use readable floors
    "card":    (1.5, 5.0),
    "diagram": (1.5, 8.0),
    "accent":  (0.5, 1.5),    # logo pops / chips may be quicker, but under 1.5 s still earns a look
    "cover":   (0.0, 0.0),
}
PREFIX_KIND = {
    "logo": "accent", "chip": "accent", "pill": "accent", "price": "accent", "clock": "accent", "subscribe": "accent",
    "card": "card", "team": "card", "agents": "card", "prod": "card", "build": "card", "sum": "card", "recap": "card",
    "steps": "diagram", "vs": "diagram", "diagram": "diagram",
    "black": "cover", "mask": "cover", "cover": "cover",
}


def graphic_kind(im):
    if im.get("kind"):
        return im["kind"]
    if im.get("under"):
        return "cover"
    base = os.path.basename(im["path"]).lower()
    stem = base.split("-")[0].split("_")[0].split(".")[0]
    return PREFIX_KIND.get(stem, "read")


def graphic_issues(images):
    out = []
    for n, im in enumerate(images):
        k = graphic_kind(im)
        fail, warn = FLOORS.get(k, FLOORS["read"])
        d = float(im["duration"])
        if d < fail:
            out.append({"i": n, "t": im["start"], "kind": k, "dur": round(d, 2), "level": "FAIL",
                        "msg": f"{k} graphic {d:.2f}s < {fail}s", "path": os.path.basename(im["path"])})
        elif d < warn:
            out.append({"i": n, "t": im["start"], "kind": k, "dur": round(d, 2), "level": "WARN",
                        "msg": f"{k} graphic {d:.2f}s < readable {warn}s", "path": os.path.basename(im["path"])})
    return out

# ---------- frames + contact sheets ----------

def grab(path, t, w=480, timeout=None):
    """One frame of a finished file at t (accurate seek), scaled to width w, as an RGB array. timeout (s): None waits
    forever; on expiry ffmpeg is killed and None is returned (a failed still)."""
    try:
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0.0, t):.4f}", "-i", path, "-frames:v", "1",
                            "-vf", f"scale={w}:-2", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True,
                           timeout=timeout)
    except subprocess.TimeoutExpired:
        return None
    raw = r.stdout
    if r.returncode != 0 or not raw:
        return None                    # callers count None cells as failed review stills
    from PIL import Image
    import io
    return Image.open(io.BytesIO(raw)).convert("RGB")


def start_time(path, timeout=60):
    """The video stream's first presentation time (s), as ffmpeg -copyts reports frame times."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=start_time",
                        "-of", "csv=p=0", path], capture_output=True, text=True, timeout=timeout)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def frames_near(path, times, w, h, fps=60, timeout=120):
    """For each presentation time (s, file timestamps), the decoded frame whose own timestamp is nearest, within half a
    frame, else None: [(PIL image or None, its pts_time or None)]. One bounded decode of the covering window with
    -copyts and passthrough sync; every output frame's timestamp is read from showinfo, so cells are identified by
    the frame's real time, never by assuming the first frame after -ss is the requested one (FIRST-PASS QA R3 #1)."""
    import re
    from PIL import Image
    lo, hi = min(times), max(times)
    ss = max(0.0, lo - 1.0)
    try:
        r = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "info", "-ss", f"{ss:.6f}", "-copyts",
                            "-t", f"{hi - ss + 0.5:.6f}", "-i", path, "-vf", f"scale={w}:{h},showinfo",
                            "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return [(None, None) for _ in times]
    ts = [float(m) for m in re.findall(rb"Parsed_showinfo.*? pts_time:\s*(-?[0-9.]+)", r.stderr)]
    size = w * h * 3
    n = len(r.stdout) // size
    if r.returncode != 0 or n != len(ts) or not n:
        return [(None, None) for _ in times]
    out = []
    for t in times:
        k = min(range(n), key=lambda i: abs(ts[i] - t))
        ok = abs(ts[k] - t) < 0.5 / fps
        out.append((Image.frombytes("RGB", (w, h), r.stdout[k * size:(k + 1) * size]), ts[k]) if ok else (None, None))
    return out


def sheet(rows, path, label_h=22):
    """rows: list of (label, [PIL images or None]). Labels drawn with PIL (ffmpeg drawtext crashes on fontconfig)."""
    from PIL import Image, ImageDraw
    cells = [im for _, ims in rows for im in ims if im is not None]
    if not cells:
        return None
    cw, ch = cells[0].size
    cols = max(len(ims) for _, ims in rows)
    g = Image.new("RGB", (cw * cols, (ch + label_h) * len(rows)), (16, 16, 16))
    dr = ImageDraw.Draw(g)
    for r, (label, ims) in enumerate(rows):
        y = r * (ch + label_h)
        dr.text((6, y + 4), label, fill=(240, 220, 120))
        for c, im in enumerate(ims):
            if im is not None:
                g.paste(im.resize((cw, ch)), (c * cw, y + label_h))
    g.save(path, quality=85)
    return path

# ---------- shared final acceptance (long-form check + Shorts QA; audit r3 #5) ----------

def _item(level, check, msg, t=None):
    return {"level": level, "check": check, "t": t, "msg": msg}


def final_items(path, nf, size, fps, total, probe_fn=None, loud_fn=None):
    """The deliverable contract: exact frames, size, fps, AAC 48 kHz, duration within 0.1 s, -14 +/- 0.5 LUFS and
    <= -1.0 dBTP. A failed measurement is a FAIL, never a skip. Returns (items, probe dict, (I, TP) or None)."""
    probe_fn, loud_fn = probe_fn or probe, loud_fn or loudness
    items = []
    try:
        pr = probe_fn(path)
    except (subprocess.CalledProcessError, ValueError, KeyError, StopIteration, TypeError, OSError) as e:
        # truncated / not a video / no video stream: a structured FAIL, no invented metadata (audit r4 #4)
        return [_item("FAIL", "container", f"final unreadable ({type(e).__name__}): nothing else measured")], None, None
    if pr["frames"] != nf:
        items.append(_item("FAIL", "frames", f"{pr['frames']} frames, needs {nf}"))
    if [pr["width"], pr["height"]] != list(size) or abs(pr["fps"] - fps) > 0.01:
        items.append(_item("FAIL", "format", f"{pr['width']}x{pr['height']} @ {pr['fps']:.2f}, needs {size[0]}x{size[1]} @ {fps}"))
    dd = abs(pr["duration"] - total)
    if dd > 0.1:
        items.append(_item("FAIL", "duration", f"container {pr['duration']:.3f}s vs timeline {total:.3f}s"))
    elif dd > 0.05:
        items.append(_item("WARN", "duration", f"container {pr['duration']:.3f}s vs timeline {total:.3f}s"))
    loud = None
    if pr["acodec"] is None:
        items.append(_item("FAIL", "audio", "no audio stream"))
    else:
        if pr["acodec"] != "aac" or pr["asr"] != SR:
            items.append(_item("FAIL", "audio", f"audio {pr['acodec']} {pr['asr']} Hz, the deliverable needs aac {SR} Hz"))
        try:
            loud = loud_fn(path)
            if abs(loud[0] + 14) > 0.5 or loud[1] > -1.0:
                items.append(_item("FAIL", "loudness", f"{loud[0]:.1f} LUFS / {loud[1]:.1f} dBTP, want -14 +/- 0.5 / <= -1.0"))
        except RuntimeError as e:
            items.append(_item("FAIL", "loudness", f"NOT MEASURED: {e}"))
    return items, pr, loud


def click_items(stem, cuts, newer_than=None, total=None, audio=None):
    """Click scan of a voice stem at the cut times, with explicit coverage: a missing/stale/short stem or cuts past
    its end are NOT CHECKED (WARN), never silently dropped. Returns (items, per-cut results)."""
    import os as _os
    items = []
    if audio is None:
        if not _os.path.exists(stem) or (newer_than and _os.path.getmtime(stem) < _os.path.getmtime(newer_than)):
            return [_item("WARN", "click", f"{_os.path.basename(stem)} missing or older than the edit: "
                                           f"{len(cuts)} cuts NOT CHECKED")], []
        try:
            audio = load_mono(stem)
        except (subprocess.CalledProcessError, OSError, ValueError) as e:
            return [_item("WARN", "click", f"{_os.path.basename(stem)} unreadable ({type(e).__name__}): "
                                           f"{len(cuts)} cuts NOT CHECKED")], []
    if total is not None and abs(len(audio) / SR - total) > 0.05:
        items.append(_item("WARN", "click", f"voice stem is {len(audio) / SR:.2f}s, timeline {total:.2f}s"))
    res = click_scan(audio, SR, cuts)
    for c in res:
        if c["level"] in ("FAIL", "WARN"):
            items.append(_item(c["level"], "click", f"voice step {c['ratio']}x context at {c['peak_db']} dB"
                               + ("" if c["level"] == "FAIL" else " - listen"), c["t"]))
    nc = sum(c["level"] == "NOT CHECKED" for c in res)
    if nc:
        items.append(_item("WARN", "click", f"{nc} of {len(cuts)} cuts NOT CHECKED (past the end of the voice stem)"))
    return items, res


def stills_item(cells):
    bad = sum(c is None for c in cells)
    return [_item("WARN", "stills", f"{bad} of {len(cells)} review stills failed to decode")] if bad else []

# ---------- compact console output (token budget: every FAIL, WARNs grouped; full list stays in the JSON) ----------
WARN_GROUPS = [("quiet run", "tight / re-hear joins"), ("transition at", "transition clearance"),
               ("readable", "graphic under readable floor"), ("enters or leaves", "graphic edge inside a transition"),
               ("runs past the end", "graphic clipped by the end"), ("spoken word", "end hold"),
               ("NOT CHECKED", "NOT CHECKED"), ("- listen", "soft clicks (listen)"), ("caption", "captions"),
               ("stale", "stale finals"), ("provenance", "provenance")]


def print_items(items, verbose=False, indent=""):
    """Print every FAIL in full; WARNs one line per kind: count + up to 8 times. verbose=True prints everything."""
    ts = lambda x: "" if x.get("t") is None else f"{x['t']:.2f}s"
    fails = [x for x in items if x["level"] == "FAIL"]
    warns = [x for x in items if x["level"] != "FAIL"]
    for x in sorted(fails, key=lambda x: x.get("t") or 0):
        print(f"{indent}FAIL  {ts(x):>9}  {x['msg']}")
    if verbose:
        for x in sorted(warns, key=lambda x: x.get("t") or 0):
            print(f"{indent}WARN  {ts(x):>9}  {x['msg']}")
        return
    groups = {}
    for x in warns:
        g = next((name for key, name in WARN_GROUPS if key in x["msg"]), None)
        groups.setdefault(g, []).append(x)
    for g, xs in groups.items():
        if g is None:                                    # unclassified warnings are rare: print them in full
            for x in xs:
                print(f"{indent}WARN  {ts(x):>9}  {x['msg']}")
            continue
        times = [ts(x) for x in sorted(xs, key=lambda x: x.get("t") or 0) if x.get("t") is not None]
        more = f" +{len(times) - 8}" if len(times) > 8 else ""
        print(f"{indent}WARN  x{len(xs):<3} {g}" + (f": {', '.join(times[:8])}{more}" if times else f": {xs[0]['msg']}"))

# ---------- frame cadence ----------

def cadence(path, seconds=120):
    """Decoded presentation timestamps of the first `seconds` (sorted, so B-frame packet order can't fool it).
    Returns (frames, nominal fps, share of intervals off by more than 25% of a frame, worst interval in ms)."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-read_intervals", f"%+{seconds}",
                        "-show_entries", "frame=best_effort_timestamp_time", "-of", "json", path],
                       capture_output=True, text=True, check=True)
    # JSON, not CSV: H.264 side data put a trailing comma on the first CSV row (audit r4 #5)
    ts = []
    for fr in json.loads(r.stdout).get("frames", []):
        try:
            v = float(fr.get("best_effort_timestamp_time"))
        except (TypeError, ValueError):
            continue
        if np.isfinite(v):
            ts.append(v)
    ts.sort()
    if len(ts) < 3:
        raise RuntimeError("too few frames to judge cadence")
    d = np.diff(ts)
    nominal = 1.0 / float(np.median(d))
    off = float(np.mean(np.abs(d - 1 / nominal) > 0.25 / nominal))
    return len(ts), round(nominal, 3), round(off, 4), round(float(d.max()) * 1000, 1)

# ---------- self-test ----------

def _check():
    sr = SR
    t = np.arange(int(2 * sr)) / sr
    tone = 0.2 * np.sin(2 * np.pi * 220 * t).astype(np.float32)
    rng = np.random.default_rng(1)
    # clean splice: phase-continuous tone -> nothing
    assert click_scan(tone, sr, [1.0])[0]["level"] is None
    # narrow impulse on quiet room tone -> FAIL
    quiet = (0.002 * rng.standard_normal(len(t))).astype(np.float32)
    bad = quiet.copy()
    bad[sr:sr + 3] = 0.6
    assert click_scan(bad, sr, [1.0])[0]["level"] == "FAIL", click_scan(bad, sr, [1.0])
    # a consonant-like onset: noise burst starting at the cut inside ongoing speech-level noise -> not FAIL
    sp = (0.08 * rng.standard_normal(len(t))).astype(np.float32)
    sp[sr:sr + 2400] += (0.25 * rng.standard_normal(2400)).astype(np.float32)
    assert click_scan(sp, sr, [1.0])[0]["level"] != "FAIL", click_scan(sp, sr, [1.0])
    # a quiet join (both sides near-silent) -> nothing
    assert click_scan(quiet, sr, [1.0])[0]["level"] is None
    # cut times past the end of a short stem are NOT CHECKED, never silently dropped
    assert [c["level"] for c in click_scan(quiet[:sr // 10], sr, [1.0, 2.0])] == ["NOT CHECKED", "NOT CHECKED"]

    # shared final contract: wrong audio rate is a FAIL, failed loudness is a FAIL, short stem / blank stills reported
    fake = {"frames": 120, "width": 1080, "height": 1920, "fps": 60.0, "duration": 2.0, "acodec": "aac", "asr": 44100}

    def bad_loud(p):
        raise RuntimeError("decode failed")
    it, _, _ = final_items("x", 120, [1080, 1920], 60, 2.0, probe_fn=lambda p: fake, loud_fn=bad_loud)
    assert {(i["check"], i["level"]) for i in it} == {("audio", "FAIL"), ("loudness", "FAIL")}, it
    ci, _ = click_items("x", [1.0, 5.0], total=6.0, audio=np.zeros(SR * 2, np.float32))
    assert any("NOT CHECKED" in i["msg"] for i in ci) and any("voice stem is" in i["msg"] for i in ci), ci
    assert stills_item([None, None, 1])[0]["level"] == "WARN"
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print_items([_item("FAIL", "x", "boom", 1.0)] + [_item("WARN", "x", f"cut {k}: quiet run 0 ms (tight)", float(k))
                                                         for k in range(12)])
    out = buf.getvalue().splitlines()
    assert len(out) == 2 and out[0].startswith("FAIL") and "x12" in out[1] and "+4" in out[1], out
    # audit r4 #4: an unreadable final is a structured FAIL; an unreadable stem is NOT CHECKED
    import tempfile, os as _os
    td = tempfile.mkdtemp()
    junk = _os.path.join(td, "junk.mp4")
    open(junk, "wb").write(b"not an mp4")
    it, pr_, _ = final_items(junk, 10, [16, 16], 60, 1.0)
    assert pr_ is None and it[0]["check"] == "container" and it[0]["level"] == "FAIL", it
    ci2, _ = click_items(junk, [0.5])
    assert "NOT CHECKED" in ci2[0]["msg"], ci2
    # audit r4 #5: cadence on an ordinary libx264 clip (trailing-comma CSV case) and a VFR clip
    h264 = _os.path.join(td, "c.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=60:duration=1",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", h264], check=True)
    n_, fps_, off_, _w = cadence(h264, 1)
    assert n_ >= 55 and abs(fps_ - 60) < 0.5 and off_ == 0.0, (n_, fps_, off_)
    vfr = _os.path.join(td, "v.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=60:duration=2",
                    "-vf", "select='not(mod(n\\,3))+lt(n\\,60)'", "-fps_mode", "vfr", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", vfr], check=True)
    assert cadence(vfr, 2)[2] > 0.01, cadence(vfr, 2)

    class R:
        returncode, stderr = 1, "Summary:\n  Integrated loudness:\n    I: -14.0 LUFS\n  True peak:\n    Peak: -1.3 dBFS"
    try:
        loudness("x", runner=lambda *a, **k: R())
        raise AssertionError("failed decode accepted")
    except RuntimeError:
        pass
    # silence measurement: 0.5 s gap between two tones
    a = np.concatenate([tone[:sr], np.zeros(sr // 2, np.float32), tone[:sr]])
    g = quiet_len_at(a, sr, 1.25)
    assert 0.45 <= g <= 0.55, g
    assert quiet_len_at(a, sr, 0.5) == 0.0
    # soft dip between connected words (-14 -> -33 dB for 80 ms) is a boundary; flat speech is not
    sp = (0.2 * np.sin(2 * np.pi * 180 * np.arange(sr) / sr)).astype(np.float32)
    sp[int(0.5 * sr):int(0.58 * sr)] *= 0.06
    assert dip_near(sp, sr, 0.54) and not dip_near(sp, sr, 0.25)
    # graphics floors
    imgs = [{"path": "x/stat-1.png", "start": 0, "duration": 1.0}, {"path": "x/chip-a.png", "start": 0, "duration": 0.6},
            {"path": "x/card-b.png", "start": 0, "duration": 3.0}, {"path": "x/black.png", "start": 0, "duration": 0.2}]
    lv = [(i["i"], i["level"]) for i in graphic_issues(imgs)]
    assert lv == [(0, "FAIL"), (1, "WARN"), (2, "WARN")], lv
    print("qa_lib self-test OK")


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3 and sys.argv[1] == "cadence":
        n, fps, off, worst = cadence(sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 120)
        print(f"{n} frames, nominal {fps} fps, {off * 100:.2f}% intervals off by >25%, worst {worst} ms"
              + ("  -> VFR: conform to CFR" if off > 0.01 else "  -> constant enough"))
        sys.exit(0)
    _check()
