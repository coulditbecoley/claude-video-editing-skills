"""Picture evidence from a FINISHED MP4, so the pod catches picture defects before delivery (2026-11-08).

The claude-edits job needed three extra revision passes (g2-g4) for defects visible only in the final frames: a near-white
flash where a graphic stopped covering a White_Flash transition, qualifiers sharp for ~2 s, a chart complete for 5.6 s,
and a code illustration that didn't match its claim. This measures the first three and builds the image packet for the
fourth (Codex with images, `codex exec -i`).

  python output_evidence.py <final.mp4> <edit.edl.json> [--out DIR] [--cpu] [--no-sheets] [--keep-grid]
  python output_evidence.py --self-test

Supported input: CFR 60 fps that agrees with the EDL (the renderer's output); anything else is a structured FAIL.
One decode pass (CUDA when available): per-frame mean luma at 64x36, plus a 960x540 JPEG every 15th frame (0.25 s).
The packet is built in a fresh temp folder and swapped into DIR (default <final dir>/evidence) only when complete; the
old packet is marked incomplete first, so a crash leaves a FAIL, never an old PASS. DIR holds:
  report.json   status complete|failed (+ stage, error), items (FAIL/WARN, qa_lib format, "g" = graphic id),
                flashes, holds, overrides applied, index_sha256
  index.json    exactly the packet's sheets with sha256, plus final / EDL / overrides / generator identity
  images.txt    the sheet files to attach to Codex (one per line, from the index, never a glob)
  frames.md     every sheet and the times of its cells, to name frames in the Codex brief
  flash_NN.jpg  every detected flash by decoded frame index: before | onset | peak | decay | after
  overview_NN.jpg every 10 s;  scenes_NN.jpg  entry-0.25 | entry | +0.5 | mid | exit-0.25 | exit | exit+0.5 per graphic
  settled_NN.jpg  each graphic in its complete, settled state at 960 px (read the text here)
  hold_GNN.jpg    quarter-second strip of every graphic whose hold FAILs or WARNs
Exit 1 on any FAIL.

Hold = seconds the graphic is SHARP and COMPLETE: from the first 0.25 s sample after which nothing (except regions that
move throughout, like a face bubble or a screen recording) differs from its last settled sample, to its exit. Kind
comes from the EDL image's "kind" (read | card | diagram | accent); without one: name tokens (table/chart/ret... =
diagram, map/chapter/logo/chip = accent), else full-screen = card, overlay = read.

Overrides live in evidence_overrides.json next to the EDL (not in the EDL: an EDL edit would force a re-render and
re-mux for a review decision):
  {"hold_ok":  {"43": {"reason": "gold highlight steps over rows complete from 501.75", "audit": "R2"}},
   "flash_ok": {"7.950": {"reason": "hook White_Flash, frames on flash_00", "audit": "R2"}}}
keyed by graphic id / the transition's cut time (3 dp). Each must be an object with a non-empty reason and audit
"R<n>" (the Codex round that adjudicated it); anything else is ignored with a WARN and the FAIL stands. The delivery
audit must name the index_sha256 and carry a disposition line for every override (report.json "overrides").
"""
import json, os, subprocess, sys, time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import qa_lib  # noqa: E402

GRID_S = 0.25                      # hold sampling step (the step the PC audits used)
GW, GH = 960, 540                  # grid frame size
LW, LH = 64, 36                    # luma frame size
BLOCK = 16                         # settle compares 16 px blocks of the 960x540 grid frame
# tuned on claude-edits against the PC audits' quarter-second reads (v3: retention complete 542.50, privacy footer sharp
# 698.00, disclosure 450.75-451.00; v4: retention 541.00, disclosure 449.00, privacy 695.50, code 632.00); a
# shift-tolerant (min/max dilated) variant was tried and lost the v4 privacy footer, so it isn't used
T_SET = 28.0                       # block mean abs diff (0-255) above which a block differs from the settled frame
Z_SAME = 0.9                       # block pattern correlation at or above which a change is tint/glow, not content
FLAT = 6.0                         # block std below which a block is flat (no pattern to compare)
TOL_BLOCKS = 4                     # blocks allowed off (sparkles, JPEG); a sharpening footer line is 13+ blocks
# hold floors by kind: (FAIL below, WARN below), seconds of sharp complete display (Coley's audit floors, 2026-11-08)
HOLD_FLOORS = {"read": (3.0, 3.0), "card": (5.0, 7.0), "diagram": (8.0, 8.0), "accent": (0.0, 1.0)}
DIAGRAM_TOKENS = {"table", "chart", "graph", "ret", "retention", "diagram", "steps", "vs", "compare", "timeline"}
ACCENT_TOKENS = {"map", "chapter", "logo", "chip", "pill", "price", "clock", "subscribe"}
# flash (mean luma 0-255 at 64x36): see flashes(). Tuned on claude-edits v3 (532.80 peak 252 from 31, 706.68 peak 254
# from 54) and v4 (both gone; v4 max 67 there)
FLASH_JUMP, FLASH_MIN, FLASH_BACK = 100.0, 200.0, 0.5
FPS_REQUIRED = 60                  # render_mp4 renders 60 fps CFR; the grid step (15 frames) and labels assume it
INTERVAL_TOL = "1/20"              # one frame interval may differ from 1/60 s by 5% (concat joins: 2-4%)
OVERRIDES = "evidence_overrides.json"
GENERATOR = [os.path.abspath(__file__), os.path.join(HERE, "qa_lib.py")]


# ---------- EDL ----------

def timeline(E):
    """(total seconds, transitions [{name, d, cut}]) with render_mp4's semantics (speed, centred transitions)."""
    t, trans = 0.0, []
    for i, s in enumerate(E["segments"]):
        t += (s["out"] - s["in"]) / s.get("speed", 1.0)
        tr = s.get("transition")
        if tr and i + 1 < len(E["segments"]):
            trans.append({"name": tr["name"], "d": tr.get("duration", 0.5), "cut": t})
    return t, trans


def _name(im):
    p = (im.get("seq") or {}).get("dir") or im["path"]
    return os.path.splitext(os.path.basename(p.rstrip("/\\")))[0]


def hold_kind(im, full):
    if im.get("kind"):
        return im["kind"]
    toks = set(_name(im).lower().replace("-", "_").split("_"))
    if toks & DIAGRAM_TOKENS:
        return "diagram"
    if toks & ACCENT_TOKENS:
        return "accent"
    return "card" if full else "read"


def graphics(E, total):
    """Graphics to measure: every image except covers/masks, with visible span and kind."""
    cw, ch = E["resolution"]
    out = []
    for n, im in enumerate(E["images"]):
        if qa_lib.graphic_kind(im) == "cover":
            continue
        full = abs(im["x"] - cw / 2) < 2 and abs(im["y"] - ch / 2) < 2
        t0 = float(im["start"])
        t1 = min(total, t0 + float(im["duration"]))
        exit_ = 0.0 if im.get("noexit") else 0.3                # seq exit settle / pop-out fade
        out.append({"i": n, "name": _name(im), "full": full, "kind": hold_kind(im, full),
                    "anchor": [im["x"] * GW / cw / BLOCK, im["y"] * GH / ch / BLOCK],
                    "t0": t0, "t1": t1, "t_vis": t1 - exit_})
    return out


def _ok(v):
    """A structured override {"reason": str, "audit": "R<n>"}, or None (bare truthy values don't count)."""
    import re
    if (isinstance(v, dict) and isinstance(v.get("reason"), str) and v["reason"].strip()
            and isinstance(v.get("audit"), str) and re.fullmatch(r"R\d+", v["audit"])):
        return {"reason": v["reason"].strip(), "audit": v["audit"]}
    return None


def load_overrides(edl_path):
    """(hold_ok {gid: ok}, flash_ok {cut_3dp: ok}, warnings, path or None, sha256 of the exact bytes parsed or None)."""
    import hashlib
    p = os.path.join(os.path.dirname(os.path.abspath(edl_path)), OVERRIDES)
    if not os.path.exists(p):
        return {}, {}, [], None, None
    data = open(p, "rb").read()
    raw = json.loads(data.decode("utf-8"))
    hold, flash, warns = {}, {}, []
    for key, dst, conv in (("hold_ok", hold, lambda k: int(k)), ("flash_ok", flash, lambda k: f"{float(k):.3f}")):
        for k, v in (raw.get(key) or {}).items():
            ok = _ok(v)
            if ok is None:
                warns.append(qa_lib._item("WARN", "override", f"{key} {k} ignored: needs an object with reason and "
                                                              f"audit R<n>, got {v!r}"))
            else:
                dst[conv(k)] = ok
    return hold, flash, warns, p, hashlib.sha256(data).hexdigest()


def timebase(final, E, timeout=600):
    """(FAIL message or None, frame count, every frame's presentation time in seconds, in decode order). Passes only when the EDL says 60, the stream's nominal rate is 60/1 and the
    presentation timestamps (all packets, sorted, no decode) are CFR 60: every frame-to-frame interval is 1/60 s within
    INTERVAL_TOL (plus one time-base tick) and no frame drifts half a frame or more from the 1/60 grid, so frame
    index / 60 names the right frame. Catches jittered pts and a dropped or duplicated frame (r and avg rates still
    say 60; FIRST-PASS QA AUDIT R2 #2). Not pure quantization: render_mp4's chunk concat leaves one interval of
    251 or 246 ticks (of 256 at 1/15360) per join, about 6 ms of drift over claude-edits, with every frame present."""
    from fractions import Fraction
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=r_frame_rate,time_base:packet=pts", "-of", "json", final],
                       capture_output=True, text=True, timeout=timeout)
    if r.returncode:
        return f"timebase: ffprobe failed: {r.stderr.strip()[-200:]}", 0, []
    j = json.loads(r.stdout)
    st = j["streams"][0]
    ef = float(E.get("fps", FPS_REQUIRED))
    if Fraction(st["r_frame_rate"]) != FPS_REQUIRED or ef != FPS_REQUIRED:
        return (f"timebase: final r_frame_rate {st['r_frame_rate']}, EDL fps {ef:g}; evidence supports only CFR "
                f"{FPS_REQUIRED} that agrees with the EDL"), 0, []
    tb = Fraction(st["time_base"])
    try:
        pts = sorted(int(x["pts"]) for x in j.get("packets", []))
    except (KeyError, TypeError, ValueError):
        return "timebase: a video packet has no pts", 0, []
    if len(pts) < 2:
        return "timebase: fewer than 2 video packets", len(pts), []
    frame = Fraction(1, FPS_REQUIRED)
    tol = frame * Fraction(INTERVAL_TOL) + tb                   # exact rational arithmetic, no float drift
    for k in range(1, len(pts)):
        iv = (pts[k] - pts[k - 1]) * tb
        dev = (pts[k] - pts[0]) * tb - k * frame
        if abs(iv - frame) > tol or abs(dev) >= frame / 2:
            return (f"timebase: frame {k} presents at {float((pts[k] - pts[0]) * tb):.4f}s after an interval of "
                    f"{float(iv) * 1000:.2f} ms; the 1/{FPS_REQUIRED} grid says {k / FPS_REQUIRED:.4f}s (time base {tb}): "
                    f"not CFR {FPS_REQUIRED} (dropped, duplicated or jittered frames)"), len(pts), []
    return None, len(pts), [float(v * tb) for v in pts]


# ---------- decode ----------

def decode(final, gdir, fps, cpu=False, timeout=None):
    """One pass: per-frame mean luma (np.float32 array) and grid JPEGs gdir/NNNNNN.jpg (frame NNNNNN*step).
    Returns (luma, step frames, decoder used)."""
    os.makedirs(gdir, exist_ok=True)
    for f in os.listdir(gdir):
        os.remove(os.path.join(gdir, f))
    step = max(1, round(GRID_S * fps))
    tail = (f"split=2[a][b];[a]scale={LW}:{LH}:flags=area,format=gray[l];"
            f"[b]select='not(mod(n\\,{step}))',format=yuvj420p[g]")
    attempts = [] if cpu else [("cuda", ["-hwaccel", "cuda", "-hwaccel_output_format", "cuda"],
                                f"[0:v]scale_cuda={GW}:{GH}:format=nv12,hwdownload,format=nv12,{tail}")]
    attempts.append(("cpu", ["-threads", "0"], f"[0:v]scale={GW}:{GH}:flags=area,{tail}"))
    for name, hw, fc in attempts:
        r = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", *hw, "-i", final, "-filter_complex", fc,
                            "-map", "[l]", "-fps_mode", "passthrough", "-f", "rawvideo", "pipe:1",
                            "-map", "[g]", "-fps_mode", "passthrough", "-q:v", "3", "-start_number", "0",
                            os.path.join(gdir, "%06d.jpg")], capture_output=True, timeout=timeout)
        n = len(r.stdout) // (LW * LH)
        if r.returncode == 0 and n:
            luma = np.frombuffer(r.stdout[:n * LW * LH], np.uint8).reshape(n, LH * LW).mean(axis=1, dtype=np.float32)
            return luma, step, name
        sys.stderr.write(f"decode via {name} failed: {r.stderr.decode(errors='replace')[-400:]}\n")
    raise RuntimeError("could not decode the final")


# ---------- flash ----------

def flashes(luma, fps):
    """Brief near-white frames: a run at >= FLASH_MIN mean luma lasting at most FLASH_BACK s, at least FLASH_JUMP
    above the darker of the half-second before and after it. A White_Flash exposed by a graphic that stops covering
    it (claude-edits g3 532.80: dark graphic -> 252 in one frame) and a fully visible White_Flash bloom (706.68, also
    rejected) both qualify. A fade or cut to a white page that STAYS white is not brief and passes; so are fades to black."""
    out, n, w = [], len(luma), max(1, round(FLASH_BACK * fps))
    hi = luma >= FLASH_MIN
    k = 0
    while k < n:
        if not hi[k]:
            k += 1
            continue
        b = k
        while b < n and hi[b]:
            b += 1
        before = float(luma[max(0, k - w):k].min()) if k else float(luma[k])
        after = float(luma[b:b + w].min()) if b < n else float(luma[b - 1])
        peak = float(luma[k:b].max())
        if b - k <= w and peak - max(before, after) >= FLASH_JUMP:
            edge = max(float(luma[k] - luma[k - 1]) if k else 0.0, float(luma[b - 1] - luma[b]) if b < n else 0.0)
            out.append({"t": round(k / fps, 3), "frame": k, "frames_bright": b - k, "peak": round(peak, 1),
                        "before": round(before, 1), "after": round(after, 1), "hard_edge": round(edge, 1),
                        "luma": [round(float(x), 1) for x in luma[max(0, k - 3):b + 3]]})
        k = b
    return out


def flash_transition(f, trans, fps):
    """f["cut"] = the cut time (3 dp) of the EDL transition whose cut lies inside the bright run (+-2 frames), else
    None. A declared White_Flash is not an approval (claude-edits g3 532.80 and 706.68 were declared and rejected):
    only a flash_ok override for that cut is."""
    a, b = f["frame"] - 2, f["frame"] + f["frames_bright"] - 1 + 2
    f["cut"] = next((f"{tr['cut']:.3f}" for tr in trans if a <= tr["cut"] * fps <= b), None)
    return f


def flash_items(fl, trans, fps, flash_ok):
    items = []
    for n, f in enumerate(fl):
        flash_transition(f, trans, fps)
        msg = (f"flash_{n:02d}: near-white frames {f['frame']}-{f['frame'] + f['frames_bright'] - 1}, mean luma "
               f"{max(f['before'], f['after']):.0f} -> {f['peak']:.0f}"
               + (f", at the transition cut {f['cut']}" if f["cut"] else ""))
        ok = flash_ok.get(f["cut"]) if f["cut"] else None
        f["flash_ok"] = ok
        items.append(qa_lib._item("WARN" if ok else "FAIL", "flash",
                                  msg + (f"; flash_ok ({ok['audit']}): {ok['reason']}" if ok else ""), f["t"]))
    return items


def top_line(items, gs):
    """One line for a pod agent to work in one batch: counts plus the worst hold shortfalls."""
    fl = [x for x in items if x["check"] == "flash"]
    failed = {x["g"] for x in items if x["check"] == "hold" and x["level"] == "FAIL"}
    hf = [g for g in gs if g["i"] in failed and g.get("hold") is not None]
    floor = lambda g: HOLD_FLOORS.get(g["kind"], HOLD_FLOORS["read"])[0]
    worst = sorted(hf, key=lambda g: floor(g) - g["hold"], reverse=True)[:6]
    return (f"{sum(x['level'] == 'FAIL' for x in fl)} flash FAIL, {sum(x['level'] == 'WARN' for x in fl)} flash_ok; "
            f"{len(failed)} hold FAIL" + (", worst: " + "; ".join(
                f"G{g['i']:02d} {g['name']} @{g['t0']:.1f} {g['hold']:.1f}s of {floor(g):.0f}s" for g in worst)
                if worst else ""))


# ---------- holds ----------

def _gray(path):
    import cv2
    return cv2.imread(path, cv2.IMREAD_GRAYSCALE)


def _blocks(a, b):
    import cv2
    d = cv2.absdiff(a, b)
    return cv2.resize(d, (a.shape[1] // BLOCK, a.shape[0] // BLOCK), interpolation=cv2.INTER_AREA).astype(np.float32)


def _differ(a, b):
    """Blocks that differ in CONTENT: mean abs diff over T_SET and the block's pattern changed (normalised
    correlation under Z_SAME), unless both are flat. A highlight tint, a glow pulse or a brightness ramp keeps the
    pattern and doesn't count; text appearing, sharpening or changing does."""
    import cv2
    sz = (a.shape[1] // BLOCK, a.shape[0] // BLOCK)
    box = lambda x: cv2.resize(x, sz, interpolation=cv2.INTER_AREA)
    fa, fb = a.astype(np.float32), b.astype(np.float32)
    ma, mb = box(fa), box(fb)
    sa = np.sqrt(np.maximum(box(fa * fa) - ma * ma, 0))
    sb = np.sqrt(np.maximum(box(fb * fb) - mb * mb, 0))
    z = (box(fa * fb) - ma * mb) / np.maximum(sa * sb, 1e-3)
    return (box(np.abs(fa - fb)) > T_SET) & (z < Z_SAME) & ~((sa < FLAT) & (sb < FLAT))


def _align(f, ref):
    """f warped onto ref (affine ECC at half size): full-screen graphics carry a slow baked-in push (claude-edits:
    ~0.4% per 0.25 s), which would otherwise read as 'still changing' to the very end."""
    import cv2
    a = cv2.resize(ref, (ref.shape[1] // 2, ref.shape[0] // 2), interpolation=cv2.INTER_AREA).astype(np.float32)
    b = cv2.resize(f, (a.shape[1], a.shape[0]), interpolation=cv2.INTER_AREA).astype(np.float32)
    w = np.eye(2, 3, dtype=np.float32)
    try:
        _, w = cv2.findTransformECC(a, b, w, cv2.MOTION_AFFINE,
                                    (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 40, 1e-5), None, 5)
    except cv2.error:
        return f                                     # no fit (entry animation, different content): compare as is
    w[:, 2] *= 2
    return cv2.warpAffine(f, w, (f.shape[1], f.shape[0]), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                          borderMode=cv2.BORDER_REPLICATE)


def overlay_region(frames, pre, anchor):
    """Blocks of an overlay (lower third, chip) on moving video: the connected patch, nearest the EDL anchor (block
    coordinates), that is stable over the last 0.5 s and differs from the frame before the graphic entered; bbox
    grown by one block. The face behind it keeps moving, so it never joins the patch. None = no patch found."""
    import cv2
    ref = frames[-1]
    stable = np.max([_blocks(f, ref) for f in frames[-3:]], axis=0) <= T_SET
    core = (stable & (_blocks(pre, ref) > T_SET)).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(core, connectivity=8)
    if n < 2:
        return None
    c = 1 + int(np.argmin([np.hypot(*(cen[j] - anchor)) - 0.5 * np.sqrt(st[j, cv2.CC_STAT_AREA]) for j in range(1, n)]))
    x, y, w, h = st[c, :4]
    reg = np.zeros_like(core, bool)
    reg[max(0, y - 1):y + h + 1, max(0, x - 1):x + w + 1] = True
    return reg


def settle(frames, region=None):
    """frames: grayscale samples GRID_S apart, the last one the settled reference. Returns (index of the first sample
    from which every later sample matches the reference, share of blocks moving throughout). Each block's difference
    is the smaller of as-is and push-aligned, so a static overlay on moving video and a pushing full-screen card both
    read as settled; text appearing or sharpening differs either way. region: only these blocks count (overlays)."""
    m = len(frames)
    if m < 2:
        return 0, 0.0
    ref = frames[-1]
    al = [_align(f, ref) for f in frames[:-1]] + [ref] if region is None else frames
    diff = lambda i, j: _differ(frames[i], frames[j]) & _differ(al[i], al[j])      # differs as-is AND aligned
    moving = np.stack([diff(k, k - 1) for k in range(1, m)])          # (m-1, by, bx)
    # moving throughout: changes in over half of all steps AND still changing in the last second (a face, a video);
    # a build that finished early never counts, so a late build can't hide itself
    tail = moving[-min(4, m - 1):]
    dyn = (moving.mean(axis=0) > 0.5) & (tail.sum(axis=0) >= min(2, len(tail)))
    keep = ~dyn if region is None else (~dyn & region)
    off = np.array([int((diff(k, m - 1) & keep).sum()) for k in range(m)])
    bad = np.nonzero(off > TOL_BLOCKS)[0]
    return (int(bad[-1]) + 1 if len(bad) else 0), float(dyn.mean())


def in_transition(t, trans):
    return any(abs(t - tr["cut"]) <= tr["d"] / 2 + 1e-6 for tr in trans)


def measure_hold(g, gdir, step, fps, trans):
    """Fill g with settled_t, hold, samples; None hold when it can't be measured. Grid image k is decoded frame
    k*step, so its time is k*step/fps (exactly 0.25 s at the required 60 fps)."""
    dt = step / fps
    ks = [k for k in range(int(np.ceil(g["t0"] / dt)), int(np.floor(g["t_vis"] / dt - 1e-9)) + 1)
          if not in_transition(k * dt, trans) and os.path.exists(os.path.join(gdir, f"{k:06d}.jpg"))]
    g["samples"] = [round(k * dt, 2) for k in ks]
    if len(ks) < 2:
        g.update(settled_t=None, hold=None, moving=None)
        return g
    frames = [_gray(os.path.join(gdir, f"{k:06d}.jpg")) for k in ks]
    # a fade-out at the end (closing fade, baked-in exit) is not the settled state: stop at the last sample that still
    # has 70% of the scene's peak contrast
    con = [float(f.std()) for f in frames]
    last = max(k for k in range(len(frames)) if con[k] >= 0.7 * max(con))
    if last >= 1 and last < len(frames) - 1:
        ks, frames = ks[:last + 1], frames[:last + 1]
        g["t_vis"] = min(g["t_vis"], ks[-1] * dt + dt)
        g["faded_from"] = round(ks[-1] * dt + dt, 2)
    region = None
    pre = os.path.join(gdir, f"{ks[0] - 1:06d}.jpg")
    if not g["full"] and os.path.exists(pre):
        region = overlay_region(frames, _gray(pre), np.array(g["anchor"]))
        g["region_blocks"] = None if region is None else int(region.sum())
    s, dyn = settle(frames, region)
    g["settled_t"] = round(ks[s] * dt, 2)
    # complete from the settled sample to the visible end (the exit animation and any transition already excluded)
    g["hold"] = round(ks[-1] * dt + dt - g["settled_t"], 2) if s < len(ks) else 0.0
    g["hold"] = min(g["hold"], round(g["t_vis"] - g["settled_t"], 2))
    g["moving"] = round(dyn, 3)
    return g


def hold_items(gs, hold_ok=None):
    """FAIL/WARN per graphic, each carrying "g" (the integer graphic id). Unmeasured or unreliable holds are FAILs
    (unresolved, not proof of readability) unless a structured hold_ok covers them."""
    hold_ok = hold_ok or {}
    items = []
    for g in gs:
        lbl = f"G{g['i']:02d} {g['name']} ({g['kind']}, {'full' if g['full'] else 'overlay'}, {g['t0']:.2f}-{g['t1']:.2f})"
        fail, warn = HOLD_FLOORS.get(g["kind"], HOLD_FLOORS["read"])
        ok = hold_ok.get(g["i"])
        g["hold_ok"] = ok
        if g["hold"] is None:
            lv, t, msg = ("FAIL" if fail > 0 else "WARN"), g["t0"], f"{lbl}: hold NOT MEASURED (too short to sample)"
        elif g["moving"] and g["moving"] > 0.3 and g["full"]:
            lv, t, msg = "FAIL", g["t0"], (f"{lbl}: {g['moving']:.0%} of the frame moves throughout, hold "
                                           f"{g['hold']:.2f}s NOT RELIABLE: adjudicate its strip")
        elif g["hold"] < fail:
            lv, t, msg = ("FAIL", g["settled_t"],
                          f"{lbl}: complete only {g['hold']:.2f}s from {g['settled_t']:.2f}, floor {fail:.0f}s")
        elif g["hold"] < warn:
            lv, t, msg = ("WARN", g["settled_t"],
                          f"{lbl}: complete {g['hold']:.2f}s from {g['settled_t']:.2f}, readable {warn:.0f}s")
        else:
            continue
        if lv == "FAIL" and ok:
            lv, msg = "WARN", msg + f"; hold_ok ({ok['audit']}): {ok['reason']}"
        items.append(dict(qa_lib._item(lv, "hold", msg, t), g=g["i"]))
    return items


# ---------- sheets ----------

def _cell(gdir, t, w=480, dt=GRID_S):
    from PIL import Image
    p = os.path.join(gdir, f"{int(round(t / dt)):06d}.jpg")
    if not os.path.exists(p):
        return None
    im = Image.open(p).convert("RGB")
    return im.resize((w, w * GH // GW))


def _frames_at(final, idxs, pts, w=480, timeout=120):
    """Decoded frames by ordinal: frame k is the one presenting at pts[k] (the packet timestamps timebase() read), found
    by its own decoded timestamp, so a near-CFR file (concat joins) can't shift a cell by one frame."""
    h = int(round(w * GH / GW / 2)) * 2
    got = qa_lib.frames_near(final, [pts[k] for k in idxs], w, h, FPS_REQUIRED, timeout)
    return [im for im, _ in got]


def flash_sheets(final, out, fl, fps, n_frames, pts, timeout=120):
    """flash_NN.jpg per detected flash: before | onset | peak | decay | after, labelled by decoded frame index."""
    idx = {}
    for n, f in enumerate(fl):
        k, b = f["frame"], f["frame"] + f["frames_bright"] - 1
        lum = f["luma"]                                          # frames max(0, k-3) .. b+2
        o = min(3, k)
        peak = k + int(np.argmax(lum[o:o + f["frames_bright"]]))
        picks = [("before", k - 6), ("before", k - 1), ("onset", k), ("peak", peak), ("decay", b + 1),
                 ("decay", b + 4), ("after", b + 15), ("after", b + 30)]
        picks = [(lab, min(max(0, i), n_frames - 1)) for lab, i in picks]
        ims = _frames_at(final, [i for _, i in picks], pts, timeout=timeout)
        if any(im is None for im in ims):
            raise RuntimeError(f"flash_{n:02d}: exact frames failed to decode")
        lab = lambda ps: " | ".join(f"{a} f{i} {pts[i] - pts[0]:.3f}s" for a, i in ps)
        name = f"flash_{n:02d}.jpg"
        qa_lib.sheet([(lab(picks[:4]), ims[:4]), (lab(picks[4:]), ims[4:])], os.path.join(out, name))
        idx[name] = [f"flash_{n:02d} at {f['t']:.3f}s" + (f" (transition cut {f['cut']})" if f.get("cut") else ""),
                     lab(picks[:4]), lab(picks[4:])]
    return idx


def sheets(final, gdir, out, gs, total, fps, flagged, dt=GRID_S, timeout=60):
    """Contact sheets for eyes / codex exec -i. Returns ({sheet file: [cell descriptions]}, failed settled grabs)."""
    idx = {}
    cell = lambda gd, t, w=480: _cell(gd, t, w, dt)
    snap = lambda t: round(min(max(0.0, t), total - 1 / fps) / dt) * dt
    # overview: every 10 s, 4 per row, 6 rows per sheet
    ts = [float(t) for t in np.arange(0, total, 10.0)]
    rows = [(" | ".join(f"{t:.0f}s" for t in ts[k:k + 4]), [cell(gdir, t) for t in ts[k:k + 4]]) for k in range(0, len(ts), 4)]
    for k in range(0, len(rows), 6):
        f = f"overview_{k // 6:02d}.jpg"
        qa_lib.sheet(rows[k:k + 6], os.path.join(out, f))
        idx[f] = [r[0] for r in rows[k:k + 6]]
    # scenes: entry/mid/exit per graphic, 8 rows per sheet
    offs = ("entry-0.25", "entry", "entry+0.5", "mid", "exit-0.25", "exit", "exit+0.5")
    rows = []
    for g in gs:
        t0, t1 = g["t0"], g["t1"]
        tt = [snap(x) for x in (t0 - 0.25, t0, t0 + 0.5, (t0 + t1) / 2, t1 - 0.25, t1 - 1 / fps, t1 + 0.5)]
        rows.append((f"G{g['i']:02d} {g['name']}  " + " | ".join(f"{o} {t:.2f}" for o, t in zip(offs, tt)),
                     [cell(gdir, t, 320) for t in tt]))
    for k in range(0, len(rows), 8):
        f = f"scenes_{k // 8:02d}.jpg"
        qa_lib.sheet(rows[k:k + 8], os.path.join(out, f))
        idx[f] = [r[0] for r in rows[k:k + 8]]
    # settled: complete state at 960 px from the final itself (accurate seek), 2 per row, 2 rows per sheet
    from concurrent.futures import ThreadPoolExecutor
    pick = [(g, round((g["settled_t"] + g["t_vis"]) / 2, 2) if g.get("settled_t") is not None else round((g["t0"] + g["t1"]) / 2, 2))
            for g in gs]
    with ThreadPoolExecutor(6) as ex:
        ims = list(ex.map(lambda gt: qa_lib.grab(final, gt[1], w=960, timeout=timeout), pick))
    cells = [(f"G{g['i']:02d} {g['name']} @{t:.2f}s", im) for (g, t), im in zip(pick, ims)]
    rows = [("   ||   ".join(c[0] for c in cells[k:k + 2]), [c[1] for c in cells[k:k + 2]]) for k in range(0, len(cells), 2)]
    for k in range(0, len(rows), 2):
        f = f"settled_{k // 2:02d}.jpg"
        qa_lib.sheet(rows[k:k + 2], os.path.join(out, f))
        idx[f] = [r[0] for r in rows[k:k + 2]]
    # quarter-second strips of flagged graphics
    for g in gs:
        if g["i"] not in flagged:
            continue
        ts = [t for t in g.get("samples", [])] or [snap(g["t0"])]
        ts = ts + [snap(g["t1"] + 0.25)]
        rows = [(" | ".join(f"{t:.2f}" for t in ts[k:k + 6]), [cell(gdir, t, 320) for t in ts[k:k + 6]])
                for k in range(0, len(ts), 6)]
        f = f"hold_G{g['i']:02d}.jpg"
        qa_lib.sheet(rows, os.path.join(out, f))
        idx[f] = [f"G{g['i']:02d} {g['name']} every 0.25 s"] + [r[0] for r in rows]
    return idx, sum(1 for im in ims if im is None)


# ---------- main ----------

def _sha(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def _write_json(path, obj):
    json.dump(obj, open(path + ".next", "w"), indent=1)
    os.replace(path + ".next", path)


def _mark_incomplete(out, final, edl_path, stage, error=None):
    """A FAIL report in DIR: written before work starts (so an old PASS never survives a crash) and on any failure."""
    os.makedirs(out, exist_ok=True)
    status = "failed" if error else "incomplete"
    msg = f"picture evidence not complete ({status} at {stage}" + (f": {error}" if error else "") + ")"
    rep = {"status": status, "stage": stage, "error": error, "final": final, "edl": edl_path,
           "top": msg, "summary": msg, "items": [qa_lib._item("FAIL", "evidence", msg)], "index_sha256": None}
    _write_json(os.path.join(out, "report.json"), rep)
    for f in ("index.json", "images.txt"):                     # nothing in DIR may look like a current packet
        try:
            os.remove(os.path.join(out, f))
        except OSError:
            pass
    return rep


def _left(deadline, stage):
    """Seconds left before the overall deadline (None = no deadline); raises TimeoutError when spent."""
    if deadline is None:
        return None
    left = deadline - time.time()
    if left <= 0:
        raise TimeoutError(f"overall deadline passed before {stage}")
    return left


def _ident(path):
    st = os.stat(path)
    return [st.st_size, st.st_mtime_ns]


def run(final, edl_path, out, cpu=False, make_sheets=True, keep_grid=False, decode_timeout=None, deadline=None,
        _hook=None):
    """Build the packet; never raises for a bad input or a stage failure: returns (and writes) a failed report.
    deadline: absolute time.time() by which the whole run must finish (check's overall budget). _hook(stage) is for
    the self-test's mutation probes only."""
    import hashlib, shutil, tempfile
    from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, wait
    out = os.path.abspath(out)
    _mark_incomplete(out, final, edl_path, "start")
    tmp = tempfile.mkdtemp(prefix=".evidence-", dir=os.path.dirname(out))
    hx = ThreadPoolExecutor(1)                                  # the final's hash: a result-bearing, bounded task
    stage = "inputs"
    hook = _hook or (lambda st: None)
    try:
        t_start = time.time()
        # snapshot: the EDL and override bytes parsed are the bytes hashed; the final's identity is taken first
        edl_bytes = open(edl_path, "rb").read()
        edl_sha = hashlib.sha256(edl_bytes).hexdigest()
        E = json.loads(edl_bytes.decode("utf-8"))
        final_id0 = _ident(final)
        h_final = hx.submit(_sha, final)
        stage = "edl"
        total, trans = timeline(E)
        gl = graphics(E, total)
        hold_ok, flash_ok, items, ov_path, ov_sha = load_overrides(edl_path)
        stage = "timebase"
        bad, n_pts, pts = timebase(final, E, timeout=_left(deadline, stage) or 600)
        if bad:
            raise ValueError(bad)
        fps = float(FPS_REQUIRED)
        stage = "decode"
        gdir = os.path.join(tmp, "grid")
        dto = decode_timeout or 120 + 2.0 * total
        luma, step, dec = decode(final, gdir, fps, cpu, min(dto, _left(deadline, stage) or dto))
        t_dec = time.time() - t_start
        hook("decoded")
        if len(luma) != n_pts:
            raise ValueError(f"decoded {len(luma)} frames but the stream has {n_pts} packets")
        if abs(len(luma) - round(total * fps)) > 2:
            items.append(qa_lib._item("WARN", "frames", f"decoded {len(luma)} frames, timeline {round(total * fps)}"))
        stage = "flash"
        fl = flashes(luma, fps)
        items += flash_items(fl, trans, fps, flash_ok)
        stage = "holds"
        with ProcessPoolExecutor(max(1, min(8, (os.cpu_count() or 2) - 1))) as ex:      # ~0.1 s per sample, CPU-bound
            futs = [ex.submit(measure_hold, g, gdir, step, fps, trans) for g in gl]
            done, todo = wait(futs, timeout=_left(deadline, stage))
            if todo:
                for f_ in todo:
                    f_.cancel()
                raise TimeoutError(f"overall deadline passed during holds ({len(todo)} graphics unmeasured)")
            gs = [f_.result() for f_ in futs]
        hi = hold_items(gs, hold_ok)
        items += hi
        idx = {}
        if make_sheets:
            stage = "flash sheets"
            _left(deadline, stage)
            idx.update(flash_sheets(final, tmp, fl, fps, len(luma), pts))
            stage = "sheets"
            _left(deadline, stage)
            sh, nbad = sheets(final, gdir, tmp, gs, total, fps, {x["g"] for x in hi}, dt=step / fps)
            idx.update(sh)
            if nbad:
                raise RuntimeError(f"{nbad} settled frames failed to decode")
        stage = "final hash"
        hook("before publish")
        sz = os.path.getsize(final)
        final_sha = h_final.result(timeout=min(120 + sz / 50e6, _left(deadline, stage) or 1e9))   # raises on failure
        if not final_sha:
            raise RuntimeError("final sha256 missing")
        stage = "unchanged inputs"                             # refuse to publish evidence for bytes we didn't measure
        if _ident(final) != final_id0:
            raise RuntimeError("the final changed while it was being measured")
        if hashlib.sha256(open(edl_path, "rb").read()).hexdigest() != edl_sha:
            raise RuntimeError("the EDL changed while it was being measured")
        ov_now = load_overrides(edl_path)[4]
        if ov_now != ov_sha:
            raise RuntimeError(f"{OVERRIDES} changed while it was being measured")
        stage = "publish"
        overrides = ([{"key": f"hold_ok:G{g['i']}", "type": "hold_ok", "g": g["i"], "name": g["name"], **g["hold_ok"]}
                      for g in gs if g.get("hold_ok")]
                     + [{"key": f"flash_ok:{f['cut']}", "type": "flash_ok", "cut": f["cut"], **f["flash_ok"]}
                        for f in fl if f.get("flash_ok")])
        status = "complete" if make_sheets else "measured-no-sheets"
        index = {"status": status,
                 "final": {"path": os.path.abspath(final), "size": final_id0[0], "mtime_ns": final_id0[1],
                           "sha256": final_sha},
                 "edl": {"path": os.path.abspath(edl_path), "sha256": edl_sha},
                 "overrides": {"path": ov_path, "sha256": ov_sha, "applied": overrides},
                 "generator": {os.path.basename(g): _sha(g) for g in GENERATOR},
                 "files": {f: _sha(os.path.join(tmp, f)) for f in idx}}
        _write_json(os.path.join(tmp, "index.json"), index)
        index_sha = _sha(os.path.join(tmp, "index.json"))
        open(os.path.join(tmp, "images.txt"), "w").write("".join(f + "\n" for f in idx))
        if not make_sheets:
            items.append(qa_lib._item("FAIL", "evidence", "picture evidence not complete (--no-sheets: no image packet)"))
        nf = sum(x["level"] == "FAIL" for x in items)
        secs = round(time.time() - t_start, 1)
        summary = (f"{len(luma)} frames, {len(fl)} flashes, {len(gs)} graphics, "
                   f"{sum(1 for x in hi if x['level'] == 'FAIL')} hold FAIL, {nf} FAIL, {len(items) - nf} WARN, "
                   f"{secs}s ({dec} decode {t_dec:.0f}s)")
        top = top_line(items, gs)
        rep_ = {"status": status, "top": top, "index_sha256": index_sha, "final": final, "edl": edl_path,
                "identity": {"final": index["final"], "edl_sha256": edl_sha},
                "summary": summary, "items": items, "flashes": fl, "overrides": overrides,
                "holds": [{k: v for k, v in g.items() if k != "samples"} for g in gs], "sheets": idx,
                "floors": HOLD_FLOORS, "decoder": dec, "seconds": secs}
        _write_json(os.path.join(tmp, "report.json"), rep_)
        np.save(os.path.join(tmp, "luma.npy"), luma)
        with open(os.path.join(tmp, "frames.md"), "w", encoding="utf-8") as fh:
            fh.write(f"# Output evidence: {os.path.basename(final)}\n\n**{top}**\n\n{summary}\n\n"
                     f"EVIDENCE INDEX: {index_sha}\nSHEETS: {len(idx)} (images.txt)\n\n")
            for f, cells in idx.items():
                fh.write(f"## {f}\n" + "".join(f"- {c}\n" for c in cells) + "\n")
        if not keep_grid:
            shutil.rmtree(gdir, ignore_errors=True)        # ~3k JPEGs; the sheets keep what eyes need
        old = out + ".old"
        shutil.rmtree(old, ignore_errors=True)
        os.replace(out, old)                               # swap: DIR is the complete new packet or the FAIL marker
        os.replace(tmp, out)
        shutil.rmtree(old, ignore_errors=True)
        return rep_
    except Exception as e:                                 # structured, current FAIL; the old packet stays marked
        shutil.rmtree(tmp, ignore_errors=True)
        err = f"{type(e).__name__}: {e}"[:400]
        return _mark_incomplete(out, final, edl_path, stage, err)
    finally:
        hx.shutdown(wait=False, cancel_futures=True)       # a hash still reading a 6 GB file must not hold the caller


def _clip(path, fps, extra_vf=None, d=4):
    vf = ["-vf", extra_vf] if extra_vf else []
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x202020:s=320x180:r={fps}:d={d}",
                    *vf, "-c:v", "libx264", "-pix_fmt", "yuv420p", path], check=True)


def ffprobe_rate(path):
    return subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                           "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()


def _self_test():
    import tempfile
    fps = 60
    # flash: dark, near-white frames decaying, dark again -> flash; a fully visible bloom -> flash (706.68 was
    # rejected too); a cut to a bright page that stays bright -> none
    l = np.full(300, 30, np.float32)
    l[100:104] = [240, 220, 200, 180]
    l[104:120] = np.linspace(170, 30, 16)
    ramp = (np.linspace(0, 1, 12) ** 1.5) * 200 + 40
    l[150:162], l[162:174] = ramp, ramp[::-1]
    l[220:] = 230
    f = flashes(l, fps)
    assert [x["frame"] for x in f] == [100, 160], f
    # every flash FAILs, a declared White_Flash too; only a structured flash_ok on that cut makes it a WARN
    tr = [{"name": "White_Flash", "d": 0.4, "cut": 165 / fps}]
    assert [x["level"] for x in flash_items(f, tr, fps, {})] == ["FAIL", "FAIL"]
    ok = {f"{165 / fps:.3f}": {"reason": "hook bloom", "audit": "R2"}}
    assert [x["level"] for x in flash_items(f, tr, fps, ok)] == ["FAIL", "WARN"]
    assert _ok("yes") is None and _ok({"reason": "x"}) is None and _ok({"reason": " ", "audit": "R1"}) is None
    assert _ok({"reason": "x", "audit": "R12"}) == {"reason": "x", "audit": "R12"}
    # settle: a footer appearing late in a static card, with a "face" block that moves every sample
    rng = np.random.default_rng(0)
    base = rng.integers(0, 255, (GH, GW), np.uint8)
    frames = []
    for k in range(40):                                         # 10 s at 0.25 s
        fr = base.copy()
        fr[0:64, 0:64] = rng.integers(0, 255, (64, 64))        # moving bubble
        if k >= 32:
            fr[500:530, 100:800] = 255                         # footer from sample 32 (8.0 s)
        frames.append(fr)
    s_, dyn = settle(frames)
    assert s_ == 32 and 0 < dyn < 0.02, (s_, dyn)
    s2, _ = settle(frames[:32])                                 # static card, bubble ignored
    assert s2 == 0, s2
    # kinds, floors, graphic ids >= 100 carried as integers
    imgs = [{"path": "/x/out/s35_ret_long.mp4", "seq": {"dir": "/x/out/s35_ret_long"}, "start": 1, "duration": 10,
             "x": 1920, "y": 1080, "noexit": True},
            {"path": "/x/out/c_m8/000.png", "start": 2, "duration": 4, "x": 1100, "y": 1860},
            {"path": "/x/black.png", "start": 0, "duration": 1, "x": 1920, "y": 1080},
            {"path": "/x/out/map_m8.mp4", "start": 5, "duration": 1.5, "x": 1920, "y": 1080, "kind": "card"}]
    imgs += [{"path": "/x/black.png", "start": 0, "duration": 1, "x": 1920, "y": 1080}] * 96
    imgs += [{"path": "/x/out/s99_late.mp4", "start": 12, "duration": 6, "x": 1920, "y": 1080},
             {"path": "/x/out/c_tiny/000.png", "start": 15, "duration": 0.3, "x": 1100, "y": 1860}]
    E = {"resolution": [3840, 2160], "segments": [{"in": 0, "out": 20}], "images": imgs}
    gs = graphics(E, 20.0)
    assert [(g["i"], g["kind"], g["full"]) for g in gs] == [(0, "diagram", True), (1, "read", False), (3, "card", True),
                                                            (100, "card", True), (101, "read", False)], gs
    for g, h in zip(gs, (5.6, 3.5, 6.0, 0.4, None)):
        g.update(hold=h, settled_t=g["t0"], moving=0.0)
    it = hold_items(gs)
    assert [(x["level"], x["g"]) for x in it] == [("FAIL", 0), ("WARN", 3), ("FAIL", 100), ("FAIL", 101)], it
    top = top_line(it, gs)
    assert top.startswith("0 flash FAIL, 0 flash_ok; 3 hold FAIL, worst: G100 s99_late"), top
    assert [x["level"] for x in hold_items(gs, {0: {"reason": "y", "audit": "R1"}})][0] == "WARN"
    # end to end: a dark 60 fps clip with a 4-frame white flash at 2.0 s -> complete packet, flash FAIL, exact sheet
    td = tempfile.mkdtemp()
    mp4, edl, ev = os.path.join(td, "t.mp4"), os.path.join(td, "e.json"), os.path.join(td, "ev")
    _clip(mp4, 60, "drawbox=c=white:t=fill:enable='between(n,120,123)'")
    json.dump({"resolution": [320, 180], "fps": 60, "segments": [{"in": 0, "out": 4}], "images": []}, open(edl, "w"))
    rep = run(mp4, edl, ev, cpu=True)
    assert rep["status"] == "complete" and [round(x["t"], 2) for x in rep["flashes"]] == [2.0], rep
    assert open(os.path.join(ev, "images.txt")).read().split() == ["flash_00.jpg", "overview_00.jpg"], rep["sheets"]
    idx = json.load(open(os.path.join(ev, "index.json")))
    assert set(idx["files"]) == {"flash_00.jpg", "overview_00.jpg"} and rep["index_sha256"] == _sha(os.path.join(ev, "index.json"))
    assert "f120" in "".join(rep["sheets"]["flash_00.jpg"])
    # a failing rerun (EDL without images) replaces the PASS packet with a structured FAIL; stale sheets are gone
    json.dump({"resolution": [320, 180], "fps": 60, "segments": [{"in": 0, "out": 4}]}, open(edl, "w"))
    rep = run(mp4, edl, ev, cpu=True)
    assert rep["status"] == "failed" and rep["stage"] == "edl" and rep["items"][0]["level"] == "FAIL", rep
    assert json.load(open(os.path.join(ev, "report.json")))["status"] == "failed"
    assert not os.path.exists(os.path.join(ev, "index.json")) and not os.path.exists(os.path.join(ev, "images.txt"))
    # 30 fps final (EDL 30 or 60): structured timebase FAIL, nothing measured on a wrong clock
    mp30 = os.path.join(td, "t30.mp4")
    _clip(mp30, 30)
    for efps in (30, 60):
        json.dump({"resolution": [320, 180], "fps": efps, "segments": [{"in": 0, "out": 4}], "images": []}, open(edl, "w"))
        rep = run(mp30, edl, ev, cpu=True)
        assert rep["status"] == "failed" and rep["stage"] == "timebase" and "30/1" in rep["error"], rep
    # real VFR that r/avg rates let through (FIRST-PASS QA AUDIT R2 #2): jittered pts in MKV, one dropped frame in MP4
    mkv = os.path.join(td, "jit.mkv")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x202020:s=320x180:r=60:d=4",
                    "-vf", "setpts='(N/60+if(eq(mod(N,10),5),0.008,0))/TB'", "-fps_mode", "passthrough",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", mkv], check=True)
    drop = os.path.join(td, "drop.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x202020:s=320x180:r=60:d=4",
                    "-vf", "select='not(eq(n,100))'", "-fps_mode", "passthrough", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", drop], check=True)
    json.dump({"resolution": [320, 180], "fps": 60, "segments": [{"in": 0, "out": 4}], "images": []}, open(edl, "w"))
    for vfr, k in ((mkv, ""), (drop, "frame 100 ")):
        assert ffprobe_rate(vfr) == "60/1", vfr                 # nominal rate still says 60
        rep = run(vfr, edl, ev, cpu=True)
        assert rep["status"] == "failed" and rep["stage"] == "timebase" and "not CFR 60" in rep["error"]             and k in rep["error"], (vfr, rep)
    assert timebase(mp4, {"fps": 60})[0] is None
    # near-CFR (FIRST-PASS QA AUDIT R3 #1): one 251-tick interval in 1/15360, like render_mp4's concat joins. Frame
    # values = frame number, one white frame (90). Admitted, and every cell must be the frame an independent sequential
    # passthrough decode puts at that ordinal: across the short interval, the flash and the last frame.
    near = os.path.join(td, "near.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=black:s=64x36:r=60:d=2",
                    "-vf", "format=gray,geq=lum='if(eq(N,90),255,N)',format=yuv420p,settb=1/15360,"
                           r"setpts=PTS-if(gte(N\,60)\,5\,0)", "-fps_mode", "passthrough", "-enc_time_base", "1/15360",
                    "-c:v", "libx264", "-qp", "0", near], check=True)
    bad_, n_, pts_ = timebase(near, {"fps": 60})
    assert bad_ is None and n_ == 120, bad_
    assert any(abs((b - a) - 251 / 15360) < 1e-9 for a, b in zip(pts_, pts_[1:])), "fixture lost its 251-tick interval"
    seq = subprocess.run(["ffmpeg", "-v", "error", "-i", near, "-fps_mode", "passthrough", "-vf", "scale=64:36",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    seq = np.frombuffer(seq, np.uint8).reshape(-1, 36, 64, 3)
    assert len(seq) == 120
    want = [54, 58, 59, 60, 61, 62, 63, 64, 65, 80, 81, 82, 83, 84, 89, 90, 91, 119]
    got = qa_lib.frames_near(near, [pts_[k] for k in want], 64, 36)
    for k, (im, t) in zip(want, got):
        assert im is not None and np.array_equal(np.asarray(im), seq[k]), (k, t)
    l_near = decode(near, os.path.join(td, "ng"), 60, cpu=True)[0]
    assert len(l_near) == 120 and [x["frame"] for x in flashes(l_near, 60)] == [90]
    json.dump({"resolution": [64, 36], "fps": 60, "segments": [{"in": 0, "out": 2}], "images": []}, open(edl, "w"))
    rep = run(near, edl, ev, cpu=True)
    assert rep["status"] == "complete" and [x["frame"] for x in rep["flashes"]] == [90], rep
    from PIL import Image
    sh = np.asarray(Image.open(os.path.join(ev, "flash_00.jpg")).convert("L"))
    assert "onset f90" in "".join(rep["sheets"]["flash_00.jpg"]) and sh.max() > 240, rep["sheets"]
    json.dump({"resolution": [320, 180], "fps": 60, "segments": [{"in": 0, "out": 4}], "images": []}, open(edl, "w"))
    # inputs that change during measurement are refused (FIRST-PASS QA AUDIT R2 #3): the EDL, the override file
    def mutate_edl(stage):
        if stage == "decoded":
            json.dump({"resolution": [320, 180], "fps": 60, "segments": [{"in": 0, "out": 3}], "images": []}, open(edl, "w"))
    rep = run(mp4, edl, ev, cpu=True, _hook=mutate_edl)
    assert rep["status"] == "failed" and "EDL changed" in rep["error"], rep
    json.dump({"resolution": [320, 180], "fps": 60, "segments": [{"in": 0, "out": 4}], "images": []}, open(edl, "w"))
    ovp = os.path.join(td, OVERRIDES)
    json.dump({"flash_ok": {}}, open(ovp, "w"))
    rep = run(mp4, edl, ev, cpu=True, _hook=lambda st: st == "decoded" and json.dump(
        {"flash_ok": {"2.000": {"reason": "late approval", "audit": "R9"}}}, open(ovp, "w")))
    assert rep["status"] == "failed" and OVERRIDES in rep["error"], rep
    os.remove(ovp)
    # a failed final hash is a structured FAIL, never a complete packet with a null hash
    G = globals()
    real_sha = G["_sha"]
    G["_sha"] = lambda path: (_ for _ in ()).throw(PermissionError("probe")) if path == mp4 else real_sha(path)
    try:
        rep = run(mp4, edl, ev, cpu=True)
    finally:
        G["_sha"] = real_sha
    assert rep["status"] == "failed" and rep["stage"] == "final hash" and "PermissionError" in rep["error"], rep
    # an overall deadline already spent is a structured FAIL
    rep = run(mp4, edl, ev, cpu=True, deadline=time.time() - 1)
    assert rep["status"] == "failed" and "deadline" in rep["error"], rep
    # a stalled decode times out into a structured FAIL
    json.dump({"resolution": [320, 180], "fps": 60, "segments": [{"in": 0, "out": 4}], "images": []}, open(edl, "w"))
    rep = run(mp4, edl, ev, cpu=True, decode_timeout=0.001)
    assert rep["status"] == "failed" and rep["stage"] == "decode" and "Timeout" in rep["error"], rep
    rep = run(mp4, edl, ev, cpu=True)
    assert rep["status"] == "complete" and rep["identity"]["final"]["sha256"] == _sha(mp4), rep
    print("output_evidence self-test OK")


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--self-test" in a:
        _self_test()
        sys.exit(0)
    if len(a) < 2:
        print(__doc__)
        sys.exit(2)
    final, edl = a[0], a[1]
    out = a[a.index("--out") + 1] if "--out" in a else os.path.join(os.path.dirname(os.path.abspath(final)), "evidence")
    rep = run(final, edl, out, cpu="--cpu" in a, make_sheets="--no-sheets" not in a, keep_grid="--keep-grid" in a)
    qa_lib.print_items([dict(x, msg=f"{x['check']}: {x['msg']}") for x in rep["items"]], "-v" in a)
    print("TOP:", rep["top"])
    print("EVIDENCE:", rep["status"], rep.get("index_sha256"), rep["summary"], "->", out)
    sys.exit(1 if any(x["level"] == "FAIL" for x in rep["items"]) else 0)
