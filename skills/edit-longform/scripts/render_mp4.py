"""Render edit.edl.json straight to a 4K60 MP4, no CapCut (3 AI Setups Challenge Video 1, 2026-11-03).

Adds over the 2026-10-29 version: a per-piece lip-sync picture map (seg["pic"]: voice time -> picture time), animated
graphics as 60 fps PNG sequences (im["seq"]), masks drawn under the transitions (im["under"]), and Flash_Cut /
Dissolve / Swipe_Up transitions.

Reads the same EDL ccut builds from (cuts, per-unit lip sync, graphics, SFX, music stem)
and does what CapCut 9.2 can't: 60 fps, eased camera moves, motion-blurred custom
transitions, spring-eased graphic animations, sample-exact SFX and a mastered mix.

  python render_mp4.py video [--workers 4] [--from S --to S]   # picture, in parallel chunks
  python render_mp4.py audio                                    # mix.wav (voice + music + sfx, mastered)
  python render_mp4.py mux                                      # final MP4
  python render_mp4.py still T [T ...]                          # PNG frames at timeline seconds, for checks
"""
import json, math, os, subprocess, sys
from concurrent.futures import ProcessPoolExecutor
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EDIT = os.path.dirname(HERE)
E = json.load(open(os.path.join(EDIT, "edit.edl.json"), encoding="utf-8"))
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

# talking-head pieces (camera shots, not screen recordings): measured from frame brightness
TH_CACHE = os.path.join(HERE, "talking_head.json")


_THR = json.load(open(os.path.join(EDIT, "th_ranges.json")))


def talking_head():
    """camera pieces: the source ranges in th_ranges.json (measured from the frame-difference map)"""
    return {p["i"] for p in P if any(a <= p["s"]["in"] + 0.05 and p["s"]["out"] - 0.05 <= b for a, b in _THR)}


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
def grab(t, small=False):
    vf = "scale=480:-1," + DEC_CSC if small else DEC_CSC
    raw = subprocess.run(["ffmpeg", "-v", "error", "-hwaccel", "cuda", "-ss", f"{t:.4f}", "-i", SRC,
                          "-frames:v", "1", "-vf", vf, "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    w = 480 if small else CW
    return np.frombuffer(raw, np.uint8).reshape(-1, w, 3).copy()


def piece_frames(p, k0, k1):
    """Frames k0..k1-1 of piece p (60 fps output time). Normal-speed pieces read the source at its own 60 fps and pick
    each output frame's picture through the lip-sync map (a frame repeats or skips only inside a pause ramp)."""
    if p["sp"] == 1.0:
        yield from _mapped_frames(p, k0, k1)
        return
    s = p["s"]
    t = pic_t(p, k0 / FPS)
    n = k1 - k0
    cmd = ["ffmpeg", "-v", "error", "-hwaccel", "cuda", "-filter_threads", "4", "-ss", f"{t:.4f}", "-i", SRC,
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
            yield last.copy()   # a short read repeats the last frame (sub-frame rounding at the end)
    pr.stdout.close()
    pr.kill()
    pr.wait()


def _mapped_frames(p, k0, k1):
    want = [max(0, round(pic_t(p, k / FPS) * FPS)) for k in range(k0, k1)]
    for j in range(1, len(want)):
        want[j] = max(want[j], want[j - 1])          # never backwards
    f0 = want[0]
    span = want[-1] - f0 + 1
    cmd = ["ffmpeg", "-v", "error", "-hwaccel", "cuda", "-filter_threads", "4", "-ss", f"{f0 / FPS - 0.002:.4f}", "-i", SRC,
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
                cur = grab(w / FPS)
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
        _VIG = (_VIG * 256).astype(np.uint16)
    lut = GRADE_LUT
    out = cv2.LUT(img, lut)
    return ((out.astype(np.uint16) * _VIG) >> 8).astype(np.uint8)


_x = np.arange(256, dtype=np.float32) / 255
# a soft S-curve: shadows down, highlights up, ends pinned
GRADE_LUT = np.clip(255 * (_x - 0.03 * np.sin(2 * np.pi * _x)), 0, 255).astype(np.uint8)


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


def sprite(path):
    if path not in SPR:
        im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if im.shape[2] == 3:
            im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
        ys, xs = np.nonzero(im[..., 3])
        if len(ys) == 0:
            ys, xs = np.array([0]), np.array([0])
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
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
        if is_cover(im) != covers:
            continue
        st = im["start"]
        if not (st <= t < st + im["duration"]):
            continue
        if im.get("seq"):
            lt_ = t - st
            tail = im["duration"] - lt_
            q_ = ease_io(1 - tail / 0.3) if tail < 0.3 and not im.get("noexit") else 0.0       # exit: settle down and fade
            sm, dx, dy, a, bl = 1 - 0.04 * q_, 0, 18 * q_, 1 - q_, 0
            sq = im["seq"]
            path_ = os.path.join(sq["dir"], f"{min(sq['frames'] - 1, max(0, int(lt_ * FPS + 1e-6))):03d}.png")
            if len(SPR) > 60:
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
            if len(PM) > 120:
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


IMAGES = [im for im in E["images"] if os.path.exists(im["path"]) and (not im.get("seq") or os.path.isdir(im["seq"]["dir"]))]
if len(IMAGES) != len(E["images"]):
    print(f"WARNING: {len(E['images']) - len(IMAGES)} images missing on disk, skipped", flush=True)
PM = {}   # premultiplied static sprites


# ---------- picture render ----------
def render_range(args):
    f_start, f_end, path, TH = args
    global CAM_MASK
    CAM_MASK = _cam_mask()
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
                f = grab(pic_t(p, 0.0) + 1e-3)
                edge[key] = frame_for(p, f, 0.02, TH)
            else:
                p = P[tr["a"]]
                lt = p["t1"] - p["t0"] - 1 / FPS
                f = grab(pic_t(p, lt))
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
    enc.wait()
    return path


def chunks(n):
    """Split at piece starts that sit outside every transition window."""
    safe = [p["f0"] for p in P if all(abs(p["t0"] - tr["cut"]) > tr["d"] for tr in TRANS)]
    cuts, target = [0], NF / n
    for k in range(1, n):
        cuts.append(min(safe, key=lambda f: abs(f - k * target)))
    cuts = sorted(set(cuts)) + [NF]
    return list(zip(cuts[:-1], cuts[1:]))


def cmd_video(argv):
    n = int(argv[argv.index("--workers") + 1]) if "--workers" in argv else 4
    TH = talking_head()
    if "--from" in argv:
        a = round(float(argv[argv.index("--from") + 1]) * FPS)
        b = round(float(argv[argv.index("--to") + 1]) * FPS)
        render_range((a, b, os.path.join(OUT, f"test_{a}_{b}.mp4"), TH))
        return
    jobs = [(a, b, os.path.join(OUT, f"part{k:02d}.mp4"), TH) for k, (a, b) in enumerate(chunks(n))]
    with ProcessPoolExecutor(n) as ex:
        parts = list(ex.map(render_range, jobs))
    with open(os.path.join(OUT, "parts.txt"), "w") as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(OUT, "parts.txt"),
                    "-c", "copy", os.path.join(OUT, "picture.mp4")], check=True)
    print("picture.mp4 done")


def cmd_still(argv):
    global CAM_MASK
    CAM_MASK = _cam_mask()
    TH = talking_head()
    for ts in argv:
        t = float(ts)
        p = next(q for q in P if q["t0"] <= t < q["t1"])
        lt = t - p["t0"]
        src = grab(pic_t(p, lt))
        img = frame_for(p, src, lt, TH)
        for tr in TRANS:
            if abs(t - tr["cut"]) < tr["d"] / 2:
                if t < tr["cut"]:
                    q = P[tr["b"]]; o = frame_for(q, grab(pic_t(q, 0.0) + 0.002), 0.02, TH)
                else:
                    q = P[tr["a"]]; lq = q["t1"] - q["t0"] - 1 / FPS; o = frame_for(q, grab(pic_t(q, lq)), lq, TH)
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
        # equal-power micro-fades at real cuts only (contiguous splits stay seamless)
        if not contig[i] and L > 4 * fade:
            seg[:fade] *= np.sin(np.linspace(0, np.pi / 2, fade))[:, None]
        if not (i + 1 < len(P) and contig[i + 1]) and L > 4 * fade:
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
    dst = os.path.join(HERE, E.get("output", "edit 4K60.mp4"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(OUT, "picture.mp4"), "-i", os.path.join(OUT, "mix.wav"),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", str(SR),
                    "-movflags", "+faststart", "-shortest", dst], check=True)
    print(dst)


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"video": cmd_video, "audio": cmd_audio, "mux": cmd_mux, "still": lambda a: cmd_still(a)}[cmd](sys.argv[2:])
