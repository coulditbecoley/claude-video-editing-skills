"""Render edit.edl.json straight to a 4K60 MP4, no CapCut (3 AI Setups Challenge Video 1, 2026-11-03).

Adds over the 2026-10-29 version: a per-piece lip-sync picture map (seg["pic"]: voice time -> picture time), animated
graphics as 60 fps PNG sequences (im["seq"]), masks drawn under the transitions (im["under"]), and Flash_Cut /
Dissolve / Swipe_Up transitions.

Reads the same EDL ccut builds from (cuts, per-unit lip sync, graphics, SFX, music stem)
and does what CapCut 9.2 can't: 60 fps, eased camera moves, motion-blurred custom
transitions, spring-eased graphic animations, sample-exact SFX and a mastered mix.

  python render_mp4.py video [--workers 4|auto] [--from S --to S]   # picture, in parallel chunks (auto: cgroup quota / 2)
  python render_mp4.py video --changed                          # re-render only chunks whose graphics changed
  python render_mp4.py audio                                    # mix.wav (voice + music + sfx, mastered)
  python render_mp4.py mux                                      # final MP4
  python render_mp4.py still T [T ...]                          # PNG frames at timeline seconds, for checks
  python render_mp4.py check [--final F] [--words W] [--no-stills] [--deadline S] [-v]  # post-render QA -> out/check/, exit 1 on FAIL
                                                                  # (stills include output_evidence.py: flashes, holds, sheets)
"""
import json, math, os, subprocess, sys
from concurrent.futures import ProcessPoolExecutor
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EDIT = os.path.dirname(HERE)
_EDL_BYTES = open(os.path.join(EDIT, "edit.edl.json"), "rb").read()
E = json.loads(_EDL_BYTES.decode("utf-8"))
import hashlib as _hl
EDL_SHA0 = _hl.sha256(_EDL_BYTES).hexdigest()     # what this process renders; any later disk change = refuse to commit


def _edl_sha_now():
    return _hl.sha256(open(os.path.join(EDIT, "edit.edl.json"), "rb").read()).hexdigest()


def _write_json(path, obj):
    """Sidecars and manifests are written to a temp name and renamed: a crash never leaves half a JSON file."""
    with open(path + ".next", "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(path + ".next", path)


def _audio_inputs():
    """Identity of everything `audio` consumes (audit r5 #2): the voice WAV(s), every music and SFX file (size +
    mtime_ns, the convention used for the source), the EDL bytes and the renderer (the mix implementation)."""
    def ident(f):
        try:
            st = os.stat(f)
            return [st.st_size, st.st_mtime_ns]
        except OSError:
            return None
    files = sorted(set(list(E["voice"].values()) + [m["path"] for m in E["music"]] + [x["path"] for x in E["sfx"]]))
    return {"edl_sha256": EDL_SHA0, "renderer": _hl.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest(),
            "files": {f: ident(f) for f in files}}
SRC = E["source"]
FPS = 60
CW, CH = E["resolution"]          # canvas; never shadow these
SR = 48000
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# ---------- timeline ----------
SEGS = E["segments"]
P, off = [], 0.0
for i, s in enumerate(SEGS):
    sp = s.get("speed", 1.0)
    d = (s["out"] - s["in"]) / sp
    P.append({"i": i, "s": s, "t0": off, "t1": off + d, "sp": sp})
    off += d
TOTAL = off
NF = round(TOTAL * FPS)
for p in P:
    p["f0"], p["f1"] = round(p["t0"] * FPS), round(p["t1"] * FPS)
contig = [i > 0 and abs(SEGS[i - 1]["out"] - s["in"]) < 1e-3 for i, s in enumerate(SEGS)]


def _vrange(p):
    """Audible voice range of a piece, exactly as cmd_audio plays it: from in - av_offset, 1:1, for its timeline length."""
    a0 = p["s"]["in"] - float(p["s"].get("av_offset", 0.0))
    return a0, a0 + (p["t1"] - p["t0"])


# audio-continuous joins: both unmuted and the voice runs on without a jump (an av_offset-only change is a jump)
acontig = [i > 0 and not P[i - 1]["s"].get("mute") and not p["s"].get("mute")
           and abs(_vrange(P[i - 1])[1] - _vrange(p)[0]) < 1e-3 for i, p in enumerate(P)]



TH_RANGES = os.path.join(EDIT, "th_ranges.json")


def talking_head():
    """Camera (talking-head) pieces get the face grade. Source ranges come from <edit>/th_ranges.json:
    [[src_start_s, src_end_s], ...], the camera-only stretches of the source, read off the contact sheet or a
    frame-difference map. [] means no camera pieces. Only `video` and `still` need it."""
    if not os.path.exists(TH_RANGES):
        raise SystemExit(f"missing {TH_RANGES}: write [[src_start, src_end], ...] for camera-only source ranges "
                         f"([] if none), checked against the contact sheet")
    thr = json.load(open(TH_RANGES))
    assert all(len(r) == 2 and r[0] < r[1] for r in thr), "th_ranges.json: each entry is [start, end] with start < end"
    # a segment with its own "src" (another recording) is never a camera piece of the main source
    return {p["i"] for p in P if not p["s"].get("src")
            and any(a <= p["s"]["in"] + 0.05 and p["s"]["out"] - 0.05 <= b for a, b in thr)}


# transitions: centred on the cut, half each side (CapCut's placement, so the SFX peaks still land)
TRANS = []
for p in P:
    tr = p["s"].get("transition")
    if tr and p["i"] + 1 < len(P):
        TRANS.append({"name": tr["name"], "d": tr.get("duration", 0.5), "cut": p["t1"], "a": p["i"], "b": p["i"] + 1})


def ease_io(x):           # smoothstep-ish cubic in-out
    x = min(max(x, 0.0), 1.0)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out(x, k=3):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** k


# colour: BT.709 limited range (the source's tags), pinned explicitly on decode and encode
DEC_CSC = "scale=in_color_matrix=bt709:in_range=tv:flags=accurate_rnd+full_chroma_int,format=bgr24"
ENC_CSC = "scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd,format=yuv420p"


# ---------- picture time (lip-sync map) ----------
def pic_t(p, lt):
    """source picture second shown at piece-local output time lt"""
    s = p["s"]
    v = s["in"] + lt * p["sp"]
    m = s.get("pic")
    if not m or p["sp"] != 1.0:
        return v + (m[0][1] - m[0][0] if m else 0.0)
    return float(np.interp(v, [a for a, b in m], [b for a, b in m]))


# ---------- decode ----------
def grab(t, small=False, src=None):
    vf = "scale=480:-1," + DEC_CSC if small else DEC_CSC
    raw = subprocess.run(["ffmpeg", "-v", "error", "-hwaccel", "cuda", "-ss", f"{t:.4f}", "-i", src or SRC,
                          "-frames:v", "1", "-vf", vf, "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    w = 480 if small else CW
    return np.frombuffer(raw, np.uint8).reshape(-1, w, 3).copy()


def piece_frames(p, k0, k1):
    """Frames k0..k1-1 of piece p (60 fps output time). Normal-speed pieces read the source at its own 60 fps and pick
    each output frame's picture through the lip-sync map (a frame repeats or skips only inside a pause ramp)."""
    yield from _own(_mapped_frames(p, k0, k1) if p["sp"] == 1.0 else _speed_frames(p, k0, k1))


_END = object()


def _own(frames):
    """Compositing draws in place, so a source buffer that is yielded again for the next frame (a lip-sync repeat, or
    the held last frame after a short read) goes out as a copy and the repeat starts from the pristine decode. Before
    2026-11-08 the repeat started from the already composited frame and semi-transparent overlays blended twice
    (M-S6 audit R1 #3). Copies only on repeats: one frame of lookahead, no extra decode."""
    it = iter(frames)
    cur = next(it, _END)
    while cur is not _END:
        nxt = next(it, _END)
        yield cur.copy() if nxt is cur else cur
        cur = nxt


def _speed_frames(p, k0, k1):
    s = p["s"]
    t = pic_t(p, k0 / FPS)
    n = k1 - k0
    cmd = ["ffmpeg", "-v", "error", "-hwaccel", "cuda", "-filter_threads", "4", "-ss", f"{t:.4f}", "-i", s.get("src") or SRC,
           "-t", f"{n / FPS * p['sp'] + 0.2:.4f}", "-an",
           "-vf", f"setpts=(PTS-STARTPTS)/{p['sp']},fps={FPS},{DEC_CSC}", "-f", "rawvideo", "-"]
    pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=0)
    size = CW * CH * 3
    last = None
    for _ in range(n):
        arr = np.empty((CH, CW, 3), np.uint8)
        mv, got = memoryview(arr).cast("B"), 0
        while got < size:
            k = pr.stdout.readinto(mv[got:])
            if not k:
                break
            got += k
        if got == size:
            last = arr
            yield last
        else:
            yield last          # a short read repeats the last frame (sub-frame rounding at the end); _own copies
    pr.stdout.close()
    pr.kill()
    pr.wait()


def _mapped_frames(p, k0, k1):
    want = [max(0, round(pic_t(p, k / FPS) * FPS)) for k in range(k0, k1)]
    for j in range(1, len(want)):
        want[j] = max(want[j], want[j - 1])          # never backwards
    f0 = want[0]
    span = want[-1] - f0 + 1
    cmd = ["ffmpeg", "-v", "error", "-hwaccel", "cuda", "-filter_threads", "4", "-ss", f"{f0 / FPS - 0.002:.4f}", "-i", p["s"].get("src") or SRC,
           "-frames:v", str(span), "-an", "-vf", DEC_CSC, "-f", "rawvideo", "-"]
    pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=0)
    size = CW * CH * 3
    cur, idx = None, f0 - 1
    for w in want:
        while idx < w:
            arr = np.empty((CH, CW, 3), np.uint8)
            mv, got = memoryview(arr).cast("B"), 0
            while got < size:
                k = pr.stdout.readinto(mv[got:])
                if not k:
                    break
                got += k
            idx += 1
            if got == size:
                cur = arr
            elif cur is None:
                cur = grab(w / FPS, src=p["s"].get("src"))
        yield cur
    pr.stdout.close(); pr.kill(); pr.wait()


# ---------- camera ----------
CAM_RECT = E.get("cam_rect", [2920, 1428, 3714, 2034])
for s in SEGS:
    if s.get("cam_overlay"):
        CAM_RECT = s["cam_overlay"]["rect"]
        break


def cam_of(p, lt, TH):
    """(scale, x, y) at local time lt. x/y in CapCut half-canvas units."""
    s = p["s"]
    fr = s.get("frame") or {}
    sc, x, y = fr.get("scale", 1.0), fr.get("x", 0.0), fr.get("y", 0.0)
    dur = p["t1"] - p["t0"]
    if p["i"] in TH and not s.get("still"):
        # slow push on talking head: 3 % over the piece (CapCut 9.2 can't animate this)
        k = 1 + 0.03 * lt / max(dur, 1e-3)
        return sc * k, x * k, y * k
    # a framing change on a CONTIGUOUS join (no jump to hide) eases over 0.35 s instead of snapping
    i = p["i"]
    if i > 0 and contig[i]:
        pf = SEGS[i - 1].get("frame") or {}
        prev = (pf.get("scale", 1.0), pf.get("x", 0.0), pf.get("y", 0.0))
        if prev != (sc, x, y) and lt < 0.35:
            e = ease_io(lt / 0.35)
            return tuple(a + (b - a) * e for a, b in zip(prev, (sc, x, y)))
    return sc, x, y


def apply_cam(src, sc, x, y):
    if abs(sc - 1) < 1e-4 and abs(x) < 1e-5 and abs(y) < 1e-5:
        return src
    tx = (1 - sc) * CW / 2 + x * CW / 2
    ty = (1 - sc) * CH / 2 - y * CH / 2
    M = np.float32([[sc, 0, tx], [0, sc, ty]])
    return cv2.warpAffine(src, M, (CW, CH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


# rounded mask + thin gold rim for the facecam overlay on zoomed shots
def _cam_mask():
    x0, y0, x1, y1 = CAM_RECT
    w, h = x1 - x0, y1 - y0
    m = np.zeros((h, w), np.uint8)
    r = 34
    cv2.rectangle(m, (r, 0), (w - r, h), 255, -1)
    cv2.rectangle(m, (0, r), (w, h - r), 255, -1)
    for cx, cy in ((r, r), (w - r, r), (r, h - r), (w - r, h - r)):
        cv2.circle(m, (cx, cy), r, 255, -1, cv2.LINE_AA)
    return cv2.GaussianBlur(m, (3, 3), 0).astype(np.float32) / 255


def frame_for(p, src, lt, TH):
    return draw_images(_frame_for(p, src, lt, TH), p["t0"] + lt, covers=True)


def _frame_for(p, src, lt, TH):
    sc, x, y = cam_of(p, lt, TH)
    out = apply_cam(src, sc, x, y)
    if p["s"].get("cam_overlay") and (sc > 1.0001):
        # the recorded facecam stays at its original box and size (confirmed rule)
        x0, y0, x1, y1 = CAM_RECT
        if out is src:
            out = out.copy()
        out[y0:y1, x0:x1] = cv2.blendLinear(src[y0:y1, x0:x1], out[y0:y1, x0:x1], CAM_MASK, 1 - CAM_MASK)
    if p["i"] in TH:
        out = grade_th(out)
    return out


# talking head: gentle contrast and a soft vignette (screens stay untouched: text accuracy)
_VIG = None


def grade_th(img):
    global _VIG
    if _VIG is None:
        yy, xx = np.mgrid[0:CH // 8, 0:CW // 8].astype(np.float32)
        r = np.sqrt(((xx - CW / 16) / (CW / 16)) ** 2 + ((yy - CH / 16) / (CH / 16)) ** 2)
        v = 1 - 0.22 * np.clip((r - 0.55) / 0.85, 0, 1) ** 1.6
        _VIG = cv2.resize(v, (CW, CH), interpolation=cv2.INTER_LINEAR)[..., None]
        _VIG = np.ascontiguousarray(np.repeat((_VIG * 256).astype(np.uint16), 3, axis=2))   # per channel, for cv2
    # (LUT[x] * vig) >> 8, bit-exact with the numpy version and ~2.5x less CPU (M-S6, 2026-11-08): a uint16 LUT,
    # an exact integer multiply (<= 255 * 256 fits uint16), then the high byte of each uint16 is the >> 8
    out = cv2.multiply(cv2.LUT(img, GRADE_LUT16), _VIG)
    return cv2.extractChannel(out.view(np.uint8).reshape(CH, CW * 3, 2), 1 if sys.byteorder == "little" else 0).reshape(CH, CW, 3)


_x = np.arange(256, dtype=np.float32) / 255
# a soft S-curve: shadows down, highlights up, ends pinned
GRADE_LUT = np.clip(255 * (_x - 0.03 * np.sin(2 * np.pi * _x)), 0, 255).astype(np.uint8)
GRADE_LUT16 = GRADE_LUT.astype(np.uint16)


# ---------- transitions ----------
def blur_dir(img, k, horiz=True):
    """Directional motion blur, done at quarter res (fast, and it reads the same in motion)."""
    if k < 3:
        return img
    sm = cv2.resize(img, (CW // 4, CH // 4), interpolation=cv2.INTER_AREA)
    kk = max(3, int(k / 4) | 1)
    sm = cv2.blur(sm, (kk, 1) if horiz else (1, kk))
    return cv2.resize(sm, (CW, CH), interpolation=cv2.INTER_LINEAR)


def zoom_blur(img, sc, strength):
    """Radial zoom blur: average of scaled copies around `sc`, at quarter res."""
    sm = cv2.resize(img, (CW // 4, CH // 4), interpolation=cv2.INTER_AREA).astype(np.float32)
    w, h = CW // 4, CH // 4
    acc = np.zeros_like(sm)
    n = 6
    for j in range(n):
        s = sc * (1 + strength * j / n)
        M = cv2.getRotationMatrix2D((w / 2, h / 2), 0, s)
        acc += cv2.warpAffine(sm, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
    return cv2.resize((acc / n).astype(np.uint8), (CW, CH), interpolation=cv2.INTER_LINEAR)


def scale_c(img, s):
    if abs(s - 1) < 1e-4:
        return img
    M = cv2.getRotationMatrix2D((CW / 2, CH / 2), 0, s)
    return cv2.warpAffine(img, M, (CW, CH), borderMode=cv2.BORDER_REPLICATE)


def mix(a, b, w):
    return cv2.addWeighted(a, 1 - w, b, w, 0)


_LEAK = None


_GRID = np.mgrid[0:CH // 8, 0:CW // 8].astype(np.float32)


def light_leak(u, strength):
    """Procedural warm leak: drifting gold/amber blobs, uint8 BGR at full size."""
    yy, xx = _GRID
    h, w = yy.shape
    img = np.zeros((h, w, 3), np.float32)
    for cx, cy, r, col in ((0.15 + 0.7 * u, 0.3, 0.55, (40, 150, 255)), (0.9 - 0.5 * u, 0.75, 0.45, (60, 200, 255)),
                           (0.5, 0.1 + 0.3 * u, 0.35, (120, 230, 255))):
        d = ((xx / w - cx) ** 2 + ((yy / h - cy) * 0.6) ** 2) / r ** 2
        img += np.exp(-d * 3)[..., None] * np.float32(col)
    img = np.clip(img * strength, 0, 255).astype(np.uint8)
    return cv2.resize(img, (CW, CH), interpolation=cv2.INTER_LINEAR)


def transition_frame(tr, t, live, other):
    """live = this side's real frame; other = the far side's held edge frame (hidden by motion)."""
    d, cut = tr["d"], tr["cut"]
    u = (t - (cut - d / 2)) / d                     # 0..1 across the window
    before = t < cut
    A, B = (live, other) if before else (other, live)
    name = tr["name"]
    if name == "White_Flash":
        # exposure bloom to white at the cut
        e = 1 - abs(u - 0.5) * 2                       # 0 -> 1 -> 0
        e = e ** 1.5
        base = A if before else B
        glow = cv2.GaussianBlur(cv2.resize(base, (CW // 8, CH // 8)), (0, 0), 6)
        glow = cv2.resize(glow, (CW, CH))
        img = cv2.addWeighted(base, 1.0, glow, 0.8 * e, 0)
        white = np.full_like(img, 255)
        return mix(img, white, min(1.0, e * 1.05))
    if name == "Flash_Cut":
        # a quick exposure bloom on a hard cut (the cold open's beats, a time skip)
        e = max(0.0, 1 - abs(u - 0.5) * 2) ** 2
        base = A if before else B
        glow = cv2.resize(cv2.GaussianBlur(cv2.resize(base, (CW // 8, CH // 8)), (0, 0), 5), (CW, CH))
        img = cv2.addWeighted(base, 1.0, glow, 0.9 * e, 0)
        return mix(img, np.full_like(img, 255), 0.55 * e)
    if name == "Dissolve":
        # a soft cross-dissolve with a slight push (the time-lapse's steps)
        e = ease_io(u)
        return mix(scale_c(A, 1 + 0.03 * e), scale_c(B, 1.03 - 0.03 * e), e)
    if name == "Swipe_Up":
        e = ease_io(u)
        shift = int(e * CH)
        img = np.empty_like(A)
        img[:CH - shift] = A[shift:]
        img[CH - shift:] = B[:shift]
        vel = 6 * u * (1 - u)
        return blur_dir(img, vel * 240, horiz=False)
    if name == "Swipe_Left":
        # whip pan: A and B on one strip moving left, blurred by velocity
        e = ease_io(u)
        shift = int(e * CW)
        img = np.empty_like(A)
        img[:, :CW - shift] = A[:, shift:]
        img[:, CW - shift:] = B[:, :shift]
        vel = 6 * u * (1 - u)                         # derivative shape of the ease, peak at the cut
        return blur_dir(img, vel * 340)
    if name in ("Zoom_to_Change", "Zoom_Transition", "Snap_Zoom"):
        # zoom through: A pushes in with radial blur, B lands from a slight overscale
        if before:
            e = ease_io(u * 2) if u < 0.5 else 1
            img = scale_c(A, 1 + 0.35 * e)
            img = zoom_blur(img, 1.0, 0.12 * e) if e > 0.05 else img
        else:
            e = 1 - ease_out((u - 0.5) * 2)
            img = scale_c(B, 1 + 0.25 * e)
            img = zoom_blur(img, 1.0, 0.10 * e) if e > 0.05 else img
        # a short dip through the cut so the change isn't a hard swap
        dip = max(0.0, 1 - abs(u - 0.5) * 8) * 0.35
        return cv2.convertScaleAbs(img, alpha=1 - dip) if dip else img
    if name == "Light_Leaks":
        e = ease_io(u)
        base = mix(A, B, e)
        lk = light_leak(u, 0.6 * math.sin(math.pi * u) ** 1.3)
        # screen blend: glows, never blows out
        return 255 - cv2.multiply(255 - base, 255 - lk, scale=1 / 255)
    return mix(A, B, ease_io(u))


# ---------- graphics ----------
SPR = {}
VID = {}   # video-backed sequences: path -> [capture, next index, last frame]


def seq_video(sq):
    """A sequence whose folder has a sibling <dir>.mp4 is read from that video (opaque full-frame scenes: 40 4K
    scenes as PNG ~60 GB, as libx264 crf10 ~2 GB; claude-edits cloud run 2026-11-08). PNG + alpha stays for overlays."""
    v = sq["dir"].rstrip("/\\") + ".mp4"
    return v if os.path.exists(v) else None


def vid_frame(v, k):
    """Frame k (BGR) of video v, reading forward without a seek when possible. The returned array is cached and
    must not be written to: sprite() only reads it (alpha stack + crop copy)."""
    st = VID.get(v)
    if st is None:
        if len(VID) > 3:
            for o in list(VID.values()):
                o[0].release()
            VID.clear()
        st = VID[v] = [cv2.VideoCapture(v), 0, None]
    cap = st[0]
    if st[2] is not None and st[1] - 1 == k:
        return st[2]
    if st[1] != k:
        cap.set(cv2.CAP_PROP_POS_FRAMES, k)
    ok, fr = cap.read()
    if not ok:
        raise SystemExit(f"cannot read frame {k} of {v}")
    st[1], st[2] = k + 1, fr
    return fr


def sprite(path):
    if path not in SPR:
        im = vid_frame(*path) if isinstance(path, tuple) else cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if im.shape[2] == 3:
            im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
        # bounding box of alpha > 0; cv2.boundingRect is ~10x cheaper than np.nonzero, same box (M-S6)
        x0, y0, bw, bh = cv2.boundingRect(cv2.extractChannel(im, 3))
        if bw == 0:
            x0, y0, bw, bh = 0, 0, 1, 1                  # fully transparent: a 1 px crop at the origin, as before
        y1, x1 = y0 + bh, x0 + bw
        # keep the crop offset relative to the sprite centre so placement doesn't move
        SPR[path] = (im[y0:y1, x0:x1].copy(), im.shape[1], im.shape[0], x0, y0)
    return SPR[path]


def premul(sp, a):
    """(fg*alpha, 255-alpha) as 3-channel uint8, for blend()."""
    al = sp[..., 3] if a >= 0.997 else cv2.convertScaleAbs(sp[..., 3], alpha=a)
    a3 = cv2.merge([al, al, al])
    return cv2.multiply(sp[..., :3], a3, scale=1 / 255), 255 - a3


def blend(dst, pm, inv):
    """dst (uint8 view, in place) <- pm + dst*inv/255. cv2 SIMD, no float."""
    cv2.add(pm, cv2.multiply(dst, inv, scale=1 / 255), dst=dst)


HIT = {"pop": 0.133, "slide": 0.100, "glow": 0.067}   # SFX in the EDL peak on these offsets


def settle(t, h, amp=0.10, T=0.30):
    """0 at t=0, reaches 1 at the hit h (ease-out), then a damped overshoot that settles by h+T."""
    if t <= h:
        return ease_out(t / h, 3)
    x = (t - h) / T
    if x >= 1:
        return 1.0
    return 1 + amp * math.sin(math.pi * x) * (1 - x) ** 1.5


def anim(im, t):
    """(scale_mult, dx, dy, alpha, blur_px) for an image at local time t."""
    d = im["duration"]
    pop = im.get("pop", True)
    tail = d - t
    if pop == "fade":
        return 1, 0, 0, min(1.0, t / d), 0
    if pop is False:
        return 1, 0, 0, 1, 0
    if pop == "glow":
        a = ease_out(t / 0.2) if t < 0.2 else 1
        s = 1.06 - 0.06 * ease_out(t / HIT["glow"] / 2.5) if t < 0.2 else 1
        if tail < 0.3:
            a *= ease_io(tail / 0.3)
        return s, 0, 0, a, 0
    if isinstance(pop, str) and pop.startswith("slide"):
        mode = "in" if pop.endswith("_in") else "out" if pop.endswith("_out") else "both"
        side = pop.rsplit("_", 1)[0] if mode != "both" else pop
        dx, dy = {"slide_l": (-1, 0), "slide_r": (1, 0), "slide_up": (0, -1), "slide_down": (0, 1)}[side]
        offx, offy = 0.12 * CW / 2, 0.12 * CH / 2
        k, a, bl = 0.0, 1.0, 0
        if mode != "out" and t < 0.5:
            p = settle(t, HIT["slide"], amp=0.05, T=0.28)
            k = 1 - p
            a = min(1.0, t / 0.09)
            if t < HIT["slide"]:
                bl = 120 * (1 - t / HIT["slide"])         # motion blur while it travels
        if mode != "in" and tail < 0.25:
            q = ease_io(1 - tail / 0.25)
            k += 0.7 * q
            a *= 1 - q
            bl = max(bl, 60 * q)
        return 1, dx * offx * k, dy * offy * k, a, (bl, dx != 0)
    # pop (True / "in" / "out" / "both")
    s, a = 1.0, 1.0
    if pop != "out" and t < 0.5:
        s = 0.55 + 0.45 * settle(t, HIT["pop"], amp=0.16, T=0.32)
        a = min(1.0, t / 0.1)
    if pop != "in" and tail < 0.25:
        q = ease_io(1 - tail / 0.25)
        s *= 1 - 0.3 * q
        a *= 1 - q
    return s, 0, 0, a, 0


def is_cover(im):
    if im.get("under"):
        return True                      # masks: part of the picture, so transitions move them
    if im.get("seq"):
        return False
    _, fw, fh, _, _ = sprite(im["path"])
    return im.get("pop") is False and (fh, fw) == (CH, CW)


def draw_images(frame, t, covers=False):
    """covers=True draws only full-frame page stills (part of the picture, so transitions move them);
    covers=False draws every other graphic on top."""
    out = frame
    for im in IMAGES:
        st = im["start"]
        if not (st <= t < st + im["duration"]):
            continue
        if is_cover(im) != covers:      # after the time test: is_cover loads the PNG, and SPR is cleared during sequences
            continue
        if im.get("seq"):
            lt_ = t - st
            tail = im["duration"] - lt_
            q_ = ease_io(1 - tail / 0.3) if tail < 0.3 and not im.get("noexit") else 0.0       # exit: settle down and fade
            sm, dx, dy, a, bl = 1 - 0.04 * q_, 0, 18 * q_, 1 - q_, 0
            sq = im["seq"]
            k_ = min(sq['frames'] - 1, max(0, int(lt_ * FPS + 1e-6)))
            v_ = seq_video(sq)
            path_ = (v_, k_) if v_ else os.path.join(sq["dir"], f"{k_:03d}.png")
            if len(SPR) > 8:            # was 60: 60/120 4K sprites per worker OOM-killed 8 workers in a 62 GB pod
                SPR.clear()
        else:
            sm, dx, dy, a, bl = anim(im, t - st)
            path_ = im["path"]
        if a <= 0.003:
            continue
        spr, fw, fh, ox, oy = sprite(path_)
        sc = float(im.get("scale", 1.0)) * sm
        h0, w0 = spr.shape[:2]
        w, h = max(1, round(w0 * sc)), max(1, round(h0 * sc))
        # the full PNG is centred on (x, y); the crop sits at (ox, oy) inside it
        cx = im["x"] + dx + (ox + w0 / 2 - fw / 2) * sc
        cy = im["y"] + dy + (oy + h0 / 2 - fh / 2) * sc
        x0, y0 = round(cx - w / 2), round(cy - h / 2)
        sp = spr if (w, h) == (w0, h0) else cv2.resize(spr, (w, h), interpolation=cv2.INTER_AREA if sc < 1 else cv2.INTER_LINEAR)
        if bl and bl[0] >= 3:
            k = int(bl[0]) | 1
            sp = cv2.blur(sp, (k, 1) if bl[1] else (1, k))
        sx0, sy0 = max(0, -x0), max(0, -y0)
        X0, Y0 = max(0, x0), max(0, y0)
        X1, Y1 = min(CW, x0 + w), min(CH, y0 + h)
        if X1 <= X0 or Y1 <= Y0:
            continue
        static = sp is spr and a >= 0.997 and not (bl and bl[0] >= 3)
        sp = sp[sy0:sy0 + (Y1 - Y0), sx0:sx0 + (X1 - X0)]
        key = (path_, sx0, sy0, X1 - X0, Y1 - Y0)
        if static:
            if len(PM) > 24:
                PM.clear()
            if key not in PM:
                PM[key] = premul(sp, 1.0)
            pm, inv = PM[key]
        else:
            pm, inv = premul(sp, a)
        if not out.flags.writeable:
            out = out.copy()
        blend(out[Y0:Y1, X0:X1], pm, inv)
    return out


IMAGES = E["images"]


def _missing_assets():
    """Every image PNG and every sequence frame 000..frames-1 that the render needs but isn't on disk."""
    miss = []
    for n, im in enumerate(E["images"]):
        sq = im.get("seq")
        if not os.path.exists(im["path"]) and not (sq and seq_video(sq)):     # a video-backed seq never reads path
            miss.append(f"images[{n}] {im['path']}")
        if sq and not seq_video(sq):
            for k in range(int(sq["frames"])):
                f = os.path.join(sq["dir"], f"{k:03d}.png")
                if not os.path.exists(f):
                    miss.append(f"images[{n}] {f}")
                    break
    return miss


def _require_assets():
    miss = _missing_assets()
    if miss:
        raise SystemExit(f"{len(miss)} required graphic file(s) missing, e.g. {miss[0]} (run lint_edl.py)")
PM = {}   # premultiplied static sprites


# ---------- picture render ----------
def render_range(args):
    f_start, f_end, path, TH = args
    if os.environ.get("HL_FAIL_AT") == "encode":
        open(path, "wb").write(b"partial")
        raise RuntimeError("injected failure at encode")
    global CAM_MASK
    CAM_MASK = _cam_mask()
    import time
    t_start = time.monotonic()
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{CW}x{CH}", "-r", str(FPS),
         "-filter_threads", "4", "-i", "-", "-vf", ENC_CSC,
         "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
         "-c:v", "hevc_nvenc", "-preset", "p4", "-tune", "hq", "-rc", "vbr", "-cq", "17", "-b:v", "0",
         "-maxrate", "160M", "-bufsize", "320M", "-profile:v", "main", "-g", "120",
         "-bf", "3", "-spatial-aq", "1", path],   # no temporal AQ: its CUDA pass starved 6 parallel encoders (2026-11-03)
        stdin=subprocess.PIPE, bufsize=CW * CH * 3 * 2)
    edge = {}   # held edge frames for transitions, per (transition idx, side)

    def edge_frame(tr, side):
        key = (id(tr), side)
        if key not in edge:
            if side == "b":
                p = P[tr["b"]]
                f = grab(pic_t(p, 0.0) + 1e-3, src=p["s"].get("src"))
                edge[key] = frame_for(p, f, 0.02, TH)
            else:
                p = P[tr["a"]]
                lt = p["t1"] - p["t0"] - 1 / FPS
                f = grab(pic_t(p, lt), src=p["s"].get("src"))
                edge[key] = frame_for(p, f, lt, TH)
        return edge[key]

    done = 0
    for p in P:
        a, b = max(p["f0"], f_start), min(p["f1"], f_end)
        if a >= b:
            continue
        for k, src in enumerate(piece_frames(p, a - p["f0"], b - p["f0"])):
            f = a + k
            t = f / FPS
            lt = t - p["t0"]
            img = frame_for(p, src, lt, TH)
            for tr in TRANS:
                if abs(t - tr["cut"]) < tr["d"] / 2:
                    other = edge_frame(tr, "b" if t < tr["cut"] else "a")
                    img = transition_frame(tr, t, img, other)
                    break
            img = draw_images(img, t)
            enc.stdin.write(memoryview(np.ascontiguousarray(img)).cast("B"))
            done += 1
            if done % 600 == 0:
                print(f"[{os.path.basename(path)}] {done}/{f_end - f_start}", flush=True)
    enc.stdin.close()
    rc = enc.wait()
    if rc != 0:
        raise RuntimeError(f"encoder exited {rc} for {path}")
    print(f"[{os.path.basename(path)}] done {f_end - f_start} frames in {time.monotonic() - t_start:.1f}s", flush=True)
    return path


CHUNK_S = 45.0   # ponytail: target chunk length; small chunks make `video --changed` rebuild less (audit r6 rec 2)


def chunks(n):
    """Split at piece starts that sit outside every transition window: at least n chunks (one per worker), and about
    CHUNK_S seconds each, so a one-graphic fix in a 20-min edit rebuilds ~45 s instead of a sixth of the video."""
    safe = [p["f0"] for p in P if all(abs(p["t0"] - tr["cut"]) > tr["d"] for tr in TRANS)]
    w = n
    n = max(n, round(TOTAL / CHUNK_S))
    n = -(-n // w) * w      # whole rounds per worker: 17 chunks on 8 workers left one straggler running alone (M-S6)
    cuts, target = [0], NF / n
    for k in range(1, n):
        cuts.append(min(safe, key=lambda f: abs(f - k * target)))
    cuts = sorted(set(cuts)) + [NF]
    return list(zip(cuts[:-1], cuts[1:]))


# ---------- partial re-render (plan T2) ----------
# Recovery contract (audit r3 #1): every render (full or partial) writes NEW generation-named parts
# (partKK.gN.mp4) and never touches the parts the current manifest references. The manifest replace is the one
# commit point; picture.mp4 is materialised after it and checked against the identity the manifest records, so a
# crash anywhere leaves either the old generation fully usable or the new one committed and re-materialisable.
CHUNKS_JSON = os.path.join(OUT, "chunks.json")
CACHE_VERSION = 3
# slack round a changed graphic: a transition can show its held edge frame up to half its width away, plus 2 frames
DIRTY_PAD = max([tr["d"] / 2 for tr in TRANS] + [0.0]) + 2 / FPS
PICTURE = os.path.join(OUT, "picture.mp4")


def _test_edl_edit(stage):
    """Test hook: HL_TEST_EDL_REPLACE=<file> (+ HL_TEST_EDL_STAGE, default pre_verify) saves a new EDL mid-render."""
    if os.environ.get("HL_TEST_EDL_REPLACE") and os.environ.get("HL_TEST_EDL_STAGE", "pre_verify") == stage:
        import shutil
        shutil.copy(os.environ["HL_TEST_EDL_REPLACE"], os.path.join(EDIT, "edit.edl.json"))


def _fail_at(stage):
    """Test hook: HL_FAIL_AT=<stage> raises here (fixture failure injection only)."""
    if os.environ.get("HL_FAIL_AT") == stage:
        raise RuntimeError(f"injected failure at {stage}")


def _hash_file(path, h=None):
    import hashlib
    h = h or hashlib.blake2b(digest_size=16)
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h


def _file_ident(path):
    st = os.stat(path)
    return [st.st_size, st.st_mtime_ns]          # full-resolution mtime (audit r3 #2)


def _asset_id(im):
    """Content identity of an image entry's pixels: the PNG plus every sequence frame, in order."""
    import hashlib
    h = hashlib.blake2b(digest_size=16)
    sq = im.get("seq")
    if os.path.exists(im["path"]) and not (sq and seq_video(sq)):
        _hash_file(im["path"], h)
    if sq and seq_video(sq):
        _hash_file(seq_video(sq), h)
    elif sq:
        for k in range(int(sq["frames"])):
            f = os.path.join(sq["dir"], f"{k:03d}.png")
            h.update(f"{k:03d}".encode())
            if os.path.exists(f):
                _hash_file(f, h)
            else:
                h.update(b"MISSING")
    return h.hexdigest()


def _layout_key():
    """Everything that moves time or pixels outside graphics. Any change here forces a full render. The source is
    treated as immutable once edited from; size + full-resolution mtime catches replacements (audit r3 #2)."""
    import hashlib
    th = open(TH_RANGES, "rb").read().decode() if os.path.exists(TH_RANGES) else None
    blob = {"v": CACHE_VERSION, "segments": E["segments"], "fps": FPS, "resolution": [CW, CH], "cam_rect": CAM_RECT,
            "source": [SRC] + _file_ident(SRC), "th_ranges": th,
            "extra_src": {f: _file_ident(f) for f in sorted({s_["src"] for s_ in SEGS if s_.get("src")})},
            "renderer": _hash_file(os.path.abspath(__file__)).hexdigest()}
    return hashlib.sha256(json.dumps(blob, sort_keys=True).encode()).hexdigest()


def _img_entries():
    return [{"key": json.dumps({"e": im, "id": _asset_id(im)}, sort_keys=True),
             "t0": float(im["start"]), "t1": float(im["start"]) + float(im["duration"])} for im in E["images"]]


def _dirty_spans(old, new):
    """Intervals to rebuild: every added/removed/changed entry (old AND new interval, so a moved card rebuilds both
    places), plus entries whose stacking order changed against a time-overlapping neighbour."""
    ok = {e["key"] for e in old}
    nk = {e["key"] for e in new}
    spans = [(e["t0"], e["t1"]) for e in old if e["key"] not in nk] + [(e["t0"], e["t1"]) for e in new if e["key"] not in ok]

    def below(lst):
        return {e["key"]: {f["key"] for f in lst[:i] if f["t0"] < e["t1"] and e["t0"] < f["t1"]} for i, e in enumerate(lst)}
    bo, bn = below(old), below(new)
    for e in new:
        if e["key"] in bo and bo[e["key"]] != bn[e["key"]]:
            spans.append((e["t0"], e["t1"]))
    return [(a - DIRTY_PAD, b + DIRTY_PAD) for a, b in spans]


def _count_frames(path):
    if not os.path.exists(path):
        return -1
    r = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                        "stream=nb_read_packets", "-of", "csv=p=0", path], capture_output=True, text=True)
    try:
        return int(r.stdout.strip())
    except ValueError:
        return -1


def _concat(chunks, dst):
    """Join the parts (dicts with path, a, b) by stream copy. Each part's length is given explicitly in whole frames:
    without it the concat demuxer offset every join by the part's mp4 duration and left 251/246-tick intervals on the
    1/15360 grid (13 short frames, ~6 ms drift on a 12:47 final; 2026-11-08). Durations are differences of cumulative
    microsecond boundaries, so rounding never accumulates. Picture bytes are unchanged; only timestamps move."""
    lst = dst + ".txt"
    us = lambda f: round(f * 1_000_000 / FPS)
    with open(lst, "w") as f:
        for c in chunks:
            f.write(f"file '{c['path']}'\nduration {(us(c['b']) - us(c['a'])) / 1e6:.6f}\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", dst], check=True)
    _fail_at("concat")
    got = _count_frames(dst)
    if got != NF:
        raise RuntimeError(f"concat produced {got} frames, expected {NF}")
    bad = _grid_errors(dst)
    if bad:
        raise RuntimeError(f"concat timestamps are not an exact {FPS} fps grid: {bad}")


def _grid_errors(path):
    """'' when the video packets' pts, sorted, start at 0 and step exactly one frame; else a short description."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=time_base:packet=pts",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    rows = [l.strip().rstrip(",") for l in r.stdout.splitlines() if l.strip()]
    tb = next((l for l in rows if "/" in l), None)
    if tb is None:
        return "no time base"
    num, den = map(int, tb.split("/"))
    if den % (FPS * num):
        return f"time base {tb} has no whole-tick frame step"
    step = den // (FPS * num)
    pts = sorted(int(l) for l in rows if l.lstrip("-").isdigit())
    off = [(k, b - a) for k, (a, b) in enumerate(zip(pts, pts[1:])) if b - a != step]
    if pts and pts[0] != 0:
        return f"first pts {pts[0]}"
    return f"{len(off)} intervals not {step} ticks, first at frame {off[0][0] + 1}: {off[0][1]}" if off else ""


def _load_manifest():
    if not os.path.exists(CHUNKS_JSON):
        return None
    try:
        m = json.load(open(CHUNKS_JSON))
    except ValueError:
        return None
    return m if m.get("version") == CACHE_VERSION else None


def _visual_deps():
    """What the picture depends on, beyond the EDL text (audit r5 #1): layout key (segments, source, th_ranges,
    canvas, renderer) and the content keys of every graphic, in order."""
    import hashlib
    return {"layout_key": _layout_key(),
            "images": hashlib.sha256(json.dumps([e["key"] for e in _img_entries()]).encode()).hexdigest()}


def _visual_deps_of(man):
    import hashlib
    return {"layout_key": man["layout_key"],
            "images": hashlib.sha256(json.dumps([e["key"] for e in man["images"]]).encode()).hexdigest()}


def _picture_current(man):
    return man is not None and os.path.exists(PICTURE) and _file_ident(PICTURE) == man.get("picture")


def _materialise(man):
    """Rebuild picture.mp4 from a committed manifest's parts (after a crash between commit and picture swap, or a
    deleted/replaced picture)."""
    tmp = os.path.join(OUT, "picture.next.mp4")
    _concat(man["chunks"], tmp)
    os.replace(tmp, PICTURE)
    man["picture"] = _file_ident(PICTURE)
    _write_json(CHUNKS_JSON, man)


def _commit(chunks_meta, n, gen, key0, imgs0, old_man):
    """Verify parts, refuse if the inputs changed mid-render, stage picture + manifest, then commit with ONE replace
    (the manifest), swap the picture, and only then delete parts the new manifest no longer references."""
    _test_edl_edit("pre_verify")
    for c in chunks_meta:
        got = _count_frames(c["path"])
        if got != c["b"] - c["a"]:
            raise RuntimeError(f"{c['path']}: {got} frames, expected {c['b'] - c['a']}")
    if _edl_sha_now() != EDL_SHA0:
        raise RuntimeError("edit.edl.json changed on disk during the render; nothing committed, re-run")
    if _layout_key() != key0 or [e["key"] for e in _img_entries()] != [e["key"] for e in imgs0]:
        raise RuntimeError("the source or graphics changed during the render; nothing committed, re-run")
    tmp = os.path.join(OUT, "picture.next.mp4")
    _concat(chunks_meta, tmp)
    _test_edl_edit("after_concat")
    # again, immediately before the commit: concat can take a while (audit r5 #5)
    if _edl_sha_now() != EDL_SHA0:
        raise RuntimeError("edit.edl.json changed on disk during the render; nothing committed, re-run")
    if _layout_key() != key0 or [e["key"] for e in _img_entries()] != [e["key"] for e in imgs0]:
        raise RuntimeError("the source or graphics changed during the render; nothing committed, re-run")
    man = {"version": CACHE_VERSION, "gen": gen, "layout_key": key0, "workers": n, "images": imgs0,
           "chunks": chunks_meta, "picture": _file_ident(tmp), "edl_sha256": EDL_SHA0}
    json.dump(man, open(CHUNKS_JSON + ".next", "w"), indent=1)
    _fail_at("commit")
    os.replace(CHUNKS_JSON + ".next", CHUNKS_JSON)                       # <- commit point
    _fail_at("after_commit")
    os.replace(tmp, PICTURE)
    live = {c["path"] for c in chunks_meta}
    for c in (old_man or {}).get("chunks", []):
        if c["path"] not in live and os.path.exists(c["path"]):
            os.remove(c["path"])


class _Lock:
    """One writer per edit: a second render in the same out/ refuses instead of racing the parts."""
    def __enter__(self):
        self.path = os.path.join(OUT, "render.lock")
        try:
            self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise SystemExit(f"{self.path} exists: another render is running (delete it if a crash left it behind)")
        os.write(self.fd, str(os.getpid()).encode())
        return self

    def __exit__(self, *a):
        os.close(self.fd)
        os.remove(self.path)


def _plan_changed(man, key0, imgs0):
    """(dirty chunk list or None for a full render, reason)."""
    if man is None:
        return None, "no current out/chunks.json (missing, unreadable or an older cache version)"
    if man["layout_key"] != key0:
        return None, "segments, source, th_ranges.json, canvas or renderer changed"
    for c in man["chunks"]:
        if _count_frames(c["path"]) != c["b"] - c["a"]:
            return None, f"part {os.path.basename(c['path'])} missing or not {c['b'] - c['a']} frames"
    spans = _dirty_spans(man["images"], imgs0)
    dirty = [c for c in man["chunks"] if any(s0 * FPS < c["b"] and c["a"] < s1 * FPS for s0, s1 in spans)]
    return dirty, f"{len(spans)} changed graphic span(s) -> {len(dirty)} of {len(man['chunks'])} chunk(s)"


def _cg_limit(d, v2):
    """CPU quota / period set in cgroup directory d (v2 cpu.max or v1 cfs files), or None: unlimited, absent or
    invalid (non-integer, zero or negative)."""
    try:
        if v2:
            q, p = open(os.path.join(d, "cpu.max")).read().split()[:2]
        else:
            q, p = (open(os.path.join(d, f)).read().strip() for f in ("cpu.cfs_quota_us", "cpu.cfs_period_us"))
        q, p = int(q), int(p)                       # "max" (v2 unlimited) raises here
    except (OSError, ValueError):
        return None
    return q / p if q > 0 and p > 0 else None       # v1 unlimited is -1


def _affinity():
    if hasattr(os, "sched_getaffinity"):
        return len(os.sched_getaffinity(0))
    try:
        import psutil                               # Windows: the process affinity mask, when psutil is installed
        return len(psutil.Process().cpu_affinity())
    except Exception:
        return os.cpu_count() or 1


def _cpu_quota(root="/sys/fs/cgroup", proc="/proc/self/cgroup", affinity=None):
    """CPUs this process may really use: the affinity mask, capped by the tightest CPU quota on this process's
    cgroup path (from /proc/self/cgroup, v2 or v1) and every ancestor up to the mount. A pod's nproc reports the host
    (48) while its quota is ~13.6. Directories that aren't visible (a host path inside a container) are skipped."""
    dirs = [(root, True), (os.path.join(root, "cpu"), False)]          # the mount itself (container's own cgroup)
    try:
        lines = open(proc).read().splitlines()
    except OSError:
        lines = []
    for line in lines:
        parts = line.split(":", 2)
        if len(parts) != 3:
            continue
        ctl, path = parts[1], parts[2].strip("/")
        if ctl == "":
            bases = [(root, True)]
        elif "cpu" in ctl.split(","):
            bases = [(os.path.join(root, ctl), False), (os.path.join(root, "cpu"), False)]
        else:
            continue
        segs = [s for s in path.split("/") if s]
        for base, v2 in bases:
            dirs += [(os.path.join(base, *segs[:k]), v2) for k in range(len(segs), -1, -1)]   # k=0: the mount itself
    # ponytail: assumes the standard /sys/fs/cgroup layout (v2 unified, or v1 cpu / cpu,cpuacct mounts there);
    # other mount points need /proc/self/mountinfo resolution
    lims = [x for x in (_cg_limit(d, v2) for d, v2 in dirs) if x]
    return float(min([affinity if affinity is not None else _affinity()] + lims))


def _workers(argv):
    """--workers N, or --workers auto = one worker per 2 usable CPUs (13.6 -> 6, the pilot's measured setting)."""
    if "--workers" not in argv:
        return 4
    v = argv[argv.index("--workers") + 1] if argv.index("--workers") + 1 < len(argv) else ""
    if v == "auto":
        return max(1, int(_cpu_quota() // 2))
    if not v.isdigit() or int(v) < 1:
        raise SystemExit(f"--workers needs a positive whole number or 'auto', got {v!r}")
    return int(v)


def _cv_threads(n):
    """OpenCV threads per worker: share the quota instead of each worker spawning one per (host) CPU. Oversubscribed
    cv2 threads cost ~2x CPU-seconds on warps/transitions (measured 2026-11-08); results are identical."""
    cv2.setNumThreads(max(1, int(_cpu_quota() // n)))


def _cost(job):
    """Rough CPU weight of a chunk for longest-first dispatch: talking-head frames (warp + grade) cost ~2x."""
    a, b, _, TH = job
    return sum((min(p["f1"], b) - max(p["f0"], a)) * (2 if p["i"] in TH else 1) for p in P if p["f0"] < b and a < p["f1"])


def cmd_video(argv):
    n = _workers(argv)
    _require_assets()
    TH = talking_head()
    if "--from" in argv:
        a = round(float(argv[argv.index("--from") + 1]) * FPS)
        b = round(float(argv[argv.index("--to") + 1]) * FPS)
        _cv_threads(n if "--workers" in argv else 1)
        render_range((a, b, os.path.join(OUT, f"test_{a}_{b}.mp4"), TH))
        return
    with _Lock():
        man = _load_manifest()
        key0, imgs0 = _layout_key(), _img_entries()          # input snapshot, re-checked before commit
        gen = int((man or {}).get("gen", 0)) + 1
        if "--changed" in argv:
            dirty, why = _plan_changed(man, key0, imgs0)
            if dirty is not None:
                print("--changed:", why)
                if not dirty:
                    if _picture_current(man):
                        print("--changed: nothing to re-render; picture.mp4 is current")
                    else:
                        _materialise(man)
                        print("--changed: picture.mp4 re-materialised from the committed parts")
                    return
                newp = {c["k"]: os.path.join(OUT, f"part{c['k']:02d}.g{gen}.mp4") for c in dirty}
                nw = min(man["workers"], len(dirty))
                with ProcessPoolExecutor(nw, initializer=_cv_threads, initargs=(nw,)) as ex:
                    list(ex.map(render_range, sorted([(c["a"], c["b"], newp[c["k"]], TH) for c in dirty], key=_cost, reverse=True)))
                meta = [dict(c, path=newp.get(c["k"], c["path"])) for c in man["chunks"]]
                _commit(meta, man["workers"], gen, key0, imgs0, man)
                print("picture.mp4 done (partial)")
                return
            print(f"--changed: full render ({why})")
        jobs = [(a, b, os.path.join(OUT, f"part{k:02d}.g{gen}.mp4"), TH) for k, (a, b) in enumerate(chunks(n))]
        print(f"video: {len(jobs)} chunks, {n} workers, {max(1, int(_cpu_quota() // n))} cv2 threads each, "
              f"{_cpu_quota():.2f} usable CPUs", flush=True)
        with ProcessPoolExecutor(n, initializer=_cv_threads, initargs=(n,)) as ex:
            list(ex.map(render_range, sorted(jobs, key=_cost, reverse=True)))      # longest first; commit stays in k order
        _commit([{"k": k, "a": a, "b": b, "path": path} for k, (a, b, path, _) in enumerate(jobs)], n, gen, key0, imgs0, man)
        print("picture.mp4 done")


def cmd_still(argv):
    _require_assets()
    global CAM_MASK
    CAM_MASK = _cam_mask()
    TH = talking_head()
    for ts in argv:
        t = float(ts)
        p = next(q for q in P if q["t0"] <= t < q["t1"])
        lt = t - p["t0"]
        src = grab(pic_t(p, lt), src=p["s"].get("src"))
        img = frame_for(p, src, lt, TH)
        for tr in TRANS:
            if abs(t - tr["cut"]) < tr["d"] / 2:
                if t < tr["cut"]:
                    q = P[tr["b"]]; o = frame_for(q, grab(pic_t(q, 0.0) + 0.002, src=q["s"].get("src")), 0.02, TH)
                else:
                    q = P[tr["a"]]; lq = q["t1"] - q["t0"] - 1 / FPS; o = frame_for(q, grab(pic_t(q, lq), src=q["s"].get("src")), lq, TH)
                img = transition_frame(tr, t, img, o)
        img = draw_images(img, t)
        cv2.imwrite(os.path.join(OUT, f"still_{t:07.2f}.jpg"), cv2.resize(img, (1920, 1080), interpolation=cv2.INTER_AREA),
                    [cv2.IMWRITE_JPEG_QUALITY, 90])


# ---------- audio ----------
def load_wav(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)


def peak_offset(a):
    env = np.abs(a).mean(1)
    win = SR // 100
    e = np.convolve(env, np.ones(win) / win, "same")
    return int(e.argmax())


def cmd_audio(argv):
    with _Lock():
        before = _audio_inputs()
        _mix_audio()
        if _audio_inputs() != before:
            raise SystemExit("audio: an input changed while mixing; mix.wav not blessed, re-run `audio`")
        mixp = os.path.join(OUT, "mix.wav")
        _write_json(mixp + ".json", {**before, "mix": _file_ident(mixp)})


def _mix_audio():
    n = int(round(TOTAL * SR))
    mixv = np.zeros((n, 2), np.float32)
    vpath = list(E["voice"].values())[0]
    V = load_wav(vpath)
    fade = int(E.get("voice_fade", 0.03) * SR)
    for i, p in enumerate(P):
        s = p["s"]
        if s.get("mute"):
            continue
        av = float(s.get("av_offset", 0.0))
        a0 = int(round((s["in"] - av) * SR))
        L = int(round(p["t1"] * SR)) - int(round(p["t0"] * SR))
        seg = V[max(0, a0):a0 + L].copy()
        if len(seg) < L:
            seg = np.vstack([seg, np.zeros((L - len(seg), 2), np.float32)])
        # equal-power micro-fades at audio discontinuities only (continuous voice stays seamless)
        if not acontig[i] and L > 4 * fade:
            seg[:fade] *= np.sin(np.linspace(0, np.pi / 2, fade))[:, None]
        if not (i + 1 < len(P) and acontig[i + 1]) and L > 4 * fade:
            seg[-fade:] *= np.cos(np.linspace(0, np.pi / 2, fade))[:, None]
        o = int(round(p["t0"] * SR))
        mixv[o:o + L] += seg[:max(0, min(L, n - o))]
    mus = np.zeros_like(mixv)
    for m in E["music"]:
        M = load_wav(m["path"])[int(m.get("start_offset", 0) * SR):] * float(m.get("volume", 1.0))
        o = int(m["at"] * SR)
        L = min(len(M), n - o, int(m["duration"] * SR))
        mus[o:o + L] += M[:L]
    fx = np.zeros_like(mixv)
    cache = {}
    for s in E["sfx"]:
        if s["path"] not in cache:
            A = load_wav(s["path"])
            cache[s["path"]] = (A, peak_offset(A))
        A, po = cache[s["path"]]
        st = int(round(float(s["peak_at"]) * SR)) - po if "peak_at" in s else int(round(float(s["start"]) * SR))
        A = A * float(s.get("volume", 1.0))
        if st < 0:
            A, st = A[-st:], 0
        L = min(len(A), n - st)
        fx[st:st + L] += A[:L]
    total = mixv + mus + fx
    for name, arr in (("voice", mixv), ("music", mus), ("sfx", fx), ("premaster", total)):
        write_wav(os.path.join(OUT, f"{name}.wav"), arr)
    # two-pass loudnorm: -14 LUFS integrated, -1.0 dBTP (YouTube target, under the -1 dB peak rule)
    pre = os.path.join(OUT, "premaster.wav")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", pre, "-af", "loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    af = (f"loudnorm=I=-14:TP=-1.0:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", pre, "-af", af, "-ar", str(SR), "-c:a", "pcm_s24le",
                    os.path.join(OUT, "mix.wav")], check=True)
    print("measured", j["input_i"], "LUFS", j["input_tp"], "dBTP ->", "mix.wav")


def write_wav(path, arr):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", path], input=arr.astype(np.float32).tobytes(), check=True)


def cmd_mux(argv):
    """Mux the committed picture generation with a mix made from this EDL. Refuses an obsolete generation or a mix
    from an older EDL; re-materialises picture.mp4 when it doesn't match the committed manifest (crash between commit
    and swap, or a stale copy). Writes out/final.json: which generation, picture, mix and EDL produced the final."""
    dst = _final_path()
    with _Lock():
        man = _load_manifest()
        mixp = os.path.join(OUT, "mix.wav")
        try:
            mj = json.load(open(mixp + ".json"))
        except (OSError, ValueError):
            mj = None
        if mj is None or mj.get("mix") != _file_ident(mixp) or {k: mj.get(k) for k in ("edl_sha256", "renderer", "files")} != _audio_inputs():
            raise SystemExit("mux: out/mix.wav was not made from this edit.edl.json and its current audio files "
                             "(or was changed since): run `audio`")
        vis = None
        if man is not None:
            vis = _visual_deps()
            if _visual_deps_of(man) != vis:               # always, not only when the EDL text changed (audit r5 #1)
                raise SystemExit("mux: the committed picture is from an older edit or older graphics/source: "
                                 "run `video --changed`")
            if not _picture_current(man):
                _materialise(man)
                print("mux: picture.mp4 re-materialised from committed generation", man["gen"])
        else:
            print("mux: no generation manifest (legacy picture.mp4): provenance recorded as unverified")
        _mux_run(dst)
        _write_json(os.path.join(OUT, "final.json"),
                    {"final": _file_ident(dst), "gen": man and man["gen"], "picture": _file_ident(PICTURE),
                     "mix": _file_ident(mixp), "edl_sha256": EDL_SHA0, "visual": vis, "audio": mj,
                     "verified": man is not None})
    print(dst)


def _mux_run(dst):
    # never -shortest: a mix a few ms short of the picture made ffmpeg drop the last 1-4 video frames (REF long-form
    # 80321/80322, Shorts 2/4/5/7/8, found by `check` 2026-11-04). Pad the audio and pin the length to NF frames.
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(OUT, "picture.mp4"), "-i", os.path.join(OUT, "mix.wav"),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", "apad", "-c:a", "aac", "-b:a", "320k",
                    "-ar", str(SR), "-frames:v", str(NF), "-t", f"{NF / FPS:.6f}", "-movflags", "+faststart", dst], check=True)


# ---------- check: post-render QA (plan T1) ----------
QA_DIRS = [os.environ.get("LF_SCRIPTS", r"%USERPROFILE%\.claude\skills\edit-longform\scripts"), HERE]
STILL_W = 480
EDL_PATH = os.path.join(EDIT, "edit.edl.json")


def _final_path():
    """Where `mux` writes the deliverable (cmd_mux uses this too)."""
    return os.path.join(HERE, E.get("output", "edit 4K60.mp4"))


def _sha(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:                      # chunked: the final is ~6 GB
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def _cut_times():
    """Timeline times of picture cuts, audio discontinuities and transition centres, de-duplicated."""
    ts = sorted({round(p["t0"], 4) for p in P[1:] if not contig[p["i"]] or not acontig[p["i"]]}
                | {round(tr["cut"], 4) for tr in TRANS})
    return [t for t in ts if 0.0 < t < TOTAL]




_START = {}


def _grab_window(final, t, offs, timeout=60):
    """Frames of the FINAL file at t+off for each off (timeline seconds), decoded in one bounded pass per cut. Each cell
    is the frame whose own decoded timestamp is nearest (qa_lib.frames_near), not "the first frame after -ss + k":
    near-CFR finals (concat joins) shifted that by a frame (FIRST-PASS QA R3 #1). None = failed or timed-out still."""
    import qa_lib
    if final not in _START:
        _START[final] = qa_lib.start_time(final)
    w, h = STILL_W, int(round(STILL_W * CH / CW / 2)) * 2
    ts = [_START[final] + max(0.0, min(TOTAL - 1 / FPS, t + off)) for off in offs]
    return [im for im, _ in qa_lib.frames_near(final, ts, w, h, FPS, timeout)]


def cmd_check(argv):
    for d in QA_DIRS:
        if os.path.exists(os.path.join(d, "qa_lib.py")):
            sys.path.insert(0, d)
            break
    import qa_lib, lint_edl
    final = argv[argv.index("--final") + 1] if "--final" in argv else _final_path()
    cdir = os.path.join(OUT, "check")
    os.makedirs(cdir, exist_ok=True)
    items = []
    if not os.path.exists(final):                 # still publish a current report (audit r5 #6)
        msg = f"final not found: {final} (run video, audio, mux first; picture.mp4 alone is not a deliverable)"
        _write_json(os.path.join(cdir, "report.json"), {"final": None, "summary": "final not found, 1 FAIL",
                                                        "items": [{"level": "FAIL", "check": "final", "t": None, "msg": msg}]})
        print(f"FAIL  {msg}")
        sys.exit(1)

    def item(level, what, msg, t=None):
        items.append({"level": level, "check": what, "t": t, "msg": msg})

    # overall deadline (FIRST-PASS QA AUDIT R2 #4): a current FAIL report goes down first, and a watchdog replaces it
    # with a deadline FAIL and exits if the whole check outlives --deadline seconds (default 3600; CPU-only evidence
    # alone measured 16.6 min on Coley's PC, the pod's CPU budget is unmeasured). Child ffmpeg processes of a killed
    # check are left to finish their own bounded work.
    import time
    budget = float(argv[argv.index("--deadline") + 1]) if "--deadline" in argv else 3600.0
    t_deadline = time.time() + budget
    rp_ = os.path.join(cdir, "report.json")

    def _fail_report(stage):
        msg = f"check not complete ({stage})"
        _write_json(rp_, {"final": final, "status": "incomplete", "summary": msg,
                          "evidence": {"status": "incomplete", "index_sha256": None},
                          "items": [{"level": "FAIL", "check": "check", "t": None, "msg": msg}]})
    _fail_report("running")
    import threading

    def _expire():
        _fail_report(f"overall deadline of {budget:.0f}s passed")
        print(f"FAIL  check: overall deadline of {budget:.0f}s passed", flush=True)
        os._exit(1)
    watchdog = threading.Timer(budget, _expire)
    watchdog.daemon = True
    watchdog.start()

    # 0. provenance: was this final muxed from this EDL's committed picture and a current mix?
    fj = os.path.join(OUT, "final.json")
    prov, prov_bad = None, None
    if os.path.exists(fj):
        try:
            prov = json.load(open(fj))
            missing = [k for k in ("final", "edl_sha256", "verified", "visual", "audio") if k not in prov]
            if missing:
                prov_bad = f"out/final.json is missing {', '.join(missing)}"
        except ValueError:
            prov_bad = "out/final.json is corrupt (truncated or not JSON)"
    if prov_bad:
        item("FAIL", "provenance", prov_bad + ": re-run mux")
    elif prov is None or os.path.abspath(final) != os.path.abspath(_final_path()):
        item("WARN", "provenance", "no out/final.json for this file: provenance NOT CHECKED (legacy or --final)")
    elif prov["final"] != _file_ident(final):
        item("FAIL", "provenance", "the final was changed or replaced after `mux` recorded it")
    elif prov["edl_sha256"] != EDL_SHA0:
        item("FAIL", "provenance", "the final was muxed from an older edit.edl.json: run video --changed, audio, mux")
    elif not prov.get("verified"):
        item("WARN", "provenance", "muxed from a legacy picture with no generation manifest")
    else:
        if prov["visual"] != _visual_deps():
            item("FAIL", "provenance", "graphics, source, th_ranges or renderer changed since the final was muxed: "
                                       "run video --changed, then mux")
        a = prov["audio"] or {}
        if {k: a.get(k) for k in ("edl_sha256", "renderer", "files")} != _audio_inputs():
            item("FAIL", "provenance", "a voice, music or SFX file (or the renderer) changed since the mix: run audio, then mux")
    # 1-2. the deliverable contract, shared with Shorts QA (qa_lib.final_items)
    fi, pr, loud = qa_lib.final_items(final, NF, [CW, CH], FPS, TOTAL)
    items += fi
    # 3. clicks at cuts (picture cuts + audio discontinuities) on the VOICE stem; the mix has intended SFX hits
    cuts = _cut_times()
    ci, clicks = qa_lib.click_items(os.path.join(OUT, "voice.wav"), cuts, newer_than=EDL_PATH, total=TOTAL)
    items += ci
    # 4. EDL rules (cut inside a word, graphic floors, transitions, end hold, missing media) via lint_edl
    wp, werr = lint_edl.resolve_words(EDL_PATH, E, argv[argv.index("--words") + 1] if "--words" in argv else None)
    if werr:
        item("FAIL", "words", werr)
    elif not wp:
        item("WARN", "words", "no transcript (--words, EDL 'words', main.wav.literal/words.json): word checks NOT CHECKED")
    lint_iss, _ = lint_edl.lint(E, list(E["voice"].values())[0], lint_edl.load_words(wp) if wp else None)
    for x in lint_iss:
        item(x["level"], "lint", x["msg"], x["t"])
    # 5. stills around every cut and samples, from the FINAL file (for eyes, not auto-judged)
    if "--no-stills" not in argv and pr is not None:
        offs = (-0.25, -1 / FPS, 1 / FPS, 0.25)
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(6) as ex:                # one ffmpeg per cut, 6 at a time (was ~5.5 min serial at 4K)
            grabs = list(ex.map(lambda t: _grab_window(final, t, offs), cuts))
        rows = [(f"cut {t:8.2f}s   -0.25 | -1f | +1f | +0.25", g) for t, g in zip(cuts, grabs)]
        for k in range(0, len(rows), 8):
            qa_lib.sheet(rows[k:k + 8], os.path.join(cdir, f"cuts_{k // 8:02d}.jpg"))
        samp = [("first 2 s", _grab_window(final, 0.0, (0.0, 0.5, 1.0, 1.9))),
                ("middle", [_grab_window(final, TOTAL * f, (0.0,))[0] for f in (0.25, 0.5, 0.75)]),
                ("last 2 s", _grab_window(final, TOTAL - 2.0, (0.0, 0.7, 1.4, 1.95)))]
        qa_lib.sheet(samp, os.path.join(cdir, "samples.jpg"))
        items += qa_lib.stills_item([im for _, ims in rows + samp for im in ims])
        # 6. picture evidence from the final (2026-11-08): flash scan of every frame, sharp+complete reading hold of
        # every graphic, contact sheets for the Codex image audit (out/check/evidence/frames.md names them)
        # (never raises: a stage failure comes back as status "failed" with a FAIL item)
        import output_evidence
        ev = output_evidence.run(final, EDL_PATH, os.path.join(cdir, "evidence"), deadline=t_deadline - 30)
        items += ev["items"]
        evidence = {"status": ev["status"], "dir": os.path.join(cdir, "evidence"), "index_sha256": ev.get("index_sha256"),
                    "identity": ev.get("identity"), "top": ev["top"], "generator_sha256": _sha(output_evidence.__file__)}
        # the packet must describe this final and the EDL this check (and the render) read, byte for byte
        idn = ev.get("identity")
        if ev["status"] == "complete" and idn and (
                idn["edl_sha256"] != EDL_SHA0 or idn["edl_sha256"] != _sha(EDL_PATH)
                or [idn["final"]["size"], idn["final"]["mtime_ns"]] != [os.path.getsize(final), os.stat(final).st_mtime_ns]):
            evidence["status"] = "mismatch"
            item("FAIL", "evidence", "picture evidence describes a different final or EDL than this check: re-run check")
        print("EVIDENCE:", ev["status"], ev["top"], "|", ev["summary"])
    else:
        # picture evidence is part of passing QA: a skipped run is a FAIL, so the manifest gate (no QA FAILs) refuses it
        why = "--no-stills" if "--no-stills" in argv else "final unreadable"
        evidence = {"status": "skipped", "reason": why, "index_sha256": None}
        items.append({"level": "FAIL", "check": "evidence", "t": None,
                      "msg": f"picture evidence not complete (skipped: {why}); run check without --no-stills"})
    # review windows for eyes and ears: every flagged time, each transition, the closing fade
    review = sorted({round(x["t"], 2) for x in items if x["t"] is not None} | {round(tr["cut"], 2) for tr in TRANS}
                    | {round(max(0.0, TOTAL - 2.0), 2)})
    nf = sum(x["level"] == "FAIL" for x in items)
    summary = ((f"{pr['frames']}/{NF} frames, " if pr else "UNREADABLE final, ")
               + (f"{loud[0]:.1f} LUFS {loud[1]:.1f} dBTP, " if loud else "")
               + f"{len(cuts)} cuts, {sum(1 for c in clicks if c['level'])} click flags, {nf} FAIL, {len(items) - nf} WARN")
    # the final's identity includes its sha256 (manifest gate rule 3): the evidence packet's when it describes this exact
    # file (same size and mtime), else hashed here
    fid = {"path": final, "size": os.path.getsize(final), "mtime_ns": os.stat(final).st_mtime_ns}
    eid = (evidence.get("identity") or {}).get("final") or {}
    fid["sha256"] = (eid["sha256"] if eid.get("sha256") and [eid.get("size"), eid.get("mtime_ns")] == [fid["size"], fid["mtime_ns"]]
                     else _sha(final))
    ident = {"final": fid,
             "edl_sha256": _sha(EDL_PATH), "renderer_sha256": _sha(os.path.abspath(__file__)),
             "qa_lib_sha256": _sha(qa_lib.__file__), "lint_sha256": _sha(lint_edl.__file__),
             "words": wp, "note": "hashes identify what was checked, not what produced the final"}
    watchdog.cancel()
    rp = os.path.join(cdir, "report.json")
    json.dump({**ident, "status": "complete", "provenance": prov, "evidence": evidence, "summary": summary, "items": items, "clicks": clicks,
               "review_windows": review}, open(rp + ".next", "w"), indent=1)
    os.replace(rp + ".next", rp)                     # a failed run never leaves the previous report looking current
    qa_lib.print_items([dict(x, msg=f"{x['check']}: {x['msg']}") for x in items], "-v" in argv)
    print(f"REVIEW (look + listen): {len(review)} times in report.json review_windows")
    print("CHECK:", summary, "->", cdir)
    sys.exit(1 if nf else 0)

if __name__ == "__main__":
    cmd = sys.argv[1]
    {"video": cmd_video, "audio": cmd_audio, "mux": cmd_mux, "still": lambda a: cmd_still(a), "check": cmd_check}[cmd](sys.argv[2:])
