"""Render the sN.json Shorts (gen_shorts.py) to 1080x1920 60 fps MP4s, no CapCut.
  python render_shorts.py captions            # caption PNGs (Playwright, captions.mjs)
  python render_shorts.py render 1 2 ...|all  # picture + audio + mux -> out/Short N - <title>.mp4
  python render_shorts.py still N t ...       # JPG stills for checks
Picture: ffmpeg decodes each piece at 60 fps with the lip-sync offset (picture = voice + pic_off), crops the screen band
and the facecam (or the talking-head crop), stacks them, and hands frames to Python, which draws transitions on the cuts,
the animated cards (60 fps PNG sequences from graphics/render_anim.mjs), the captions and the seam.
Audio: voice pieces with 15 ms fades (time-lapse muted), the bed ducked under the voice (sidechain), SFX on their
peak_at, two-pass loudnorm to -14 LUFS / -1 dBTP."""
import json, math, os, subprocess, sys
from concurrent.futures import ProcessPoolExecutor
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
CAPS = os.path.join(HERE, "captions"); os.makedirs(CAPS, exist_ok=True)
W, H, FPS, SR = 1080, 1920, 60, 48000
SEAM = 740
DEC = "scale=in_color_matrix=bt709:in_range=tv:out_range=pc:flags=bicubic,format=bgr24"
ease = lambda x: (lambda x: 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2)(min(max(x, 0.0), 1.0))
eout = lambda x, k=3: 1 - (1 - min(max(x, 0.0), 1.0)) ** k


def load(n):
    return json.load(open(os.path.join(HERE, f"s{n}.json"), encoding="utf-8"))


# ---------- picture ----------
def vf_for(seg, sp):
    pre = f"setpts=(PTS-STARTPTS)/{sp},fps={FPS}," if sp != 1.0 else ""
    if seg["layout"] == "th":
        x, y, w, h = seg["th"]
        return f"[0:v]{pre}crop={w}:{h}:{x}:{y},scale={W}:{H}:flags=lanczos,{DEC}[o]"
    x0, y0, w = seg["band"]; h = round(w * SEAM / W) // 2 * 2
    cx, cy, cw, ch = seg["cam"]
    return (f"[0:v]{pre}split[a][b];[a]crop={w}:{h}:{x0}:{y0},scale={W}:{SEAM}:flags=lanczos[t];"
            f"[b]crop={cw}:{ch}:{cx}:{cy},scale={W}:{H - SEAM}:flags=lanczos[c];[t][c]vstack,{DEC}[o]")


def frames(seg, n, src):
    sp = seg["speed"]
    t0 = seg["in"] + seg["pic_off"]
    cmd = ["ffmpeg", "-v", "error", "-hwaccel", "cuda", "-ss", f"{t0:.4f}", "-i", src, "-t", f"{n / FPS * sp + 0.25:.4f}", "-an",
           "-filter_complex", vf_for(seg, sp), "-map", "[o]", "-frames:v", str(n), "-f", "rawvideo", "-"]
    pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=0)
    size, last = W * H * 3, None
    for _ in range(n):
        a = np.empty((H, W, 3), np.uint8); mv, got = memoryview(a).cast("B"), 0
        while got < size:
            k = pr.stdout.readinto(mv[got:])
            if not k:
                break
            got += k
        if got == size:
            last = a
        yield last if last is not None else np.zeros((H, W, 3), np.uint8)
    pr.stdout.close(); pr.kill(); pr.wait()


def one_frame(seg, lt, src):
    s2 = dict(seg); s2["in"] = seg["in"] + lt * seg["speed"]
    return next(frames(s2, 1, src))


# ---------- round 1: picture finish ----------
_x = np.arange(256, dtype=np.float32) / 255
_S = np.clip(255 * (_x - 0.035 * np.sin(2 * np.pi * _x)), 0, 255)
# soft S-curve on the face, a touch of warmth in the mids (R up, B down), ends pinned
LUT_FACE = np.dstack([np.clip(_S - 4 * np.sin(np.pi * _x), 0, 255), _S, np.clip(_S + 5 * np.sin(np.pi * _x), 0, 255)]).astype(np.uint8)[None, :, :]
LUT_FACE = LUT_FACE.reshape(1, 256, 3)


def _vig(w, h, amt):
    yy, xx = np.mgrid[0:h // 8, 0:w // 8].astype(np.float32)
    r = np.sqrt(((xx - w / 16) / (w / 16)) ** 2 + ((yy - h / 16) / (h / 16)) ** 2)
    v = 1 - amt * np.clip((r - 0.5) / 0.9, 0, 1) ** 1.6
    return (cv2.resize(v, (w, h), interpolation=cv2.INTER_LINEAR)[..., None] * 256).astype(np.uint16)


VIG_TH, VIG_CAM = _vig(W, H, 0.26), _vig(W, H - SEAM, 0.22)


def push(img, s, cx, cy):
    if s <= 1.0005:
        return img
    M = cv2.getRotationMatrix2D((cx, cy), 0, s)
    return cv2.warpAffine(img, M, (img.shape[1], img.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def finish(img, seg, k, nfr, t=None):
    """grade + vignette on the face only (screens stay true for legibility) and a slow push through each piece:
    3% on the talking head, 1.5% on the screen band and the facecam band (frame k of nfr)"""
    u = k / max(1, nfr - 1)
    if t is not None and seg.get("chain"):          # round 9: one push across contiguous pieces
        c0, cl = seg["chain"]; u = min(1.0, max(0.0, (t - c0) / max(cl, 1e-3)))
    if seg["layout"] == "th":
        img = push(img, 1 + 0.03 * u, W / 2, 820)
        img = cv2.LUT(img, LUT_FACE)
        return ((img.astype(np.uint16) * VIG_TH) >> 8).astype(np.uint8)
    if not seg["mute"]:
        st = 0.035 * (1 - eout(k / 15)) if seg.get("settle") and k < 15 else 0.0     # round 8: reframe-cut settle
        if not seg.get("hold"):
            img[:SEAM] = push(img[:SEAM], 1 + 0.015 * u + st, W / 2, SEAM / 2)
    cam = cv2.LUT(img[SEAM:], LUT_FACE)          # round 9: the face band holds still (grade only)
    img[SEAM:] = ((cam.astype(np.uint16) * VIG_CAM) >> 8).astype(np.uint8)
    return img


_GOLD = np.array([0x51, 0xC4, 0xF5], np.float32)
_SEAMW = (np.sin(np.linspace(0, np.pi, W)) ** 0.6)[None, :, None].astype(np.float32)     # brightest mid, fading at the edges


def seam(img, seg):
    """a thin gold seam with a soft shadow on split shots"""
    if seg["layout"] != "split":
        return img
    g = img[SEAM - 2:SEAM + 2].astype(np.float32)
    k = 0.35 + 0.6 * _SEAMW
    img[SEAM - 2:SEAM + 2] = (_GOLD * k + g * (1 - k)).astype(np.uint8)
    for d, a in ((3, 0.22), (4, 0.12), (5, 0.06)):            # a soft gold glow either side of the line
        for y in (SEAM - d, SEAM + d - 1):
            r = img[y:y + 1].astype(np.float32); kk = a * _SEAMW
            img[y:y + 1] = (_GOLD * kk + r * (1 - kk)).astype(np.uint8)
    sh = img[SEAM + 5:SEAM + 46].astype(np.float32)
    sh *= np.linspace(0.6, 1.0, sh.shape[0])[:, None, None] ** 1.4
    img[SEAM + 5:SEAM + 46] = sh.astype(np.uint8)
    up = img[SEAM - 26:SEAM - 5].astype(np.float32)          # and a little depth on the screen side
    up *= np.linspace(1.0, 0.8, up.shape[0])[:, None, None]
    img[SEAM - 26:SEAM - 5] = up.astype(np.uint8)
    return img


def blur_h(img, k):
    if k < 3:
        return img
    sm = cv2.resize(img, (W // 3, H // 3), interpolation=cv2.INTER_AREA)
    sm = cv2.blur(sm, (max(3, int(k / 3) | 1), 1))
    return cv2.resize(sm, (W, H), interpolation=cv2.INTER_LINEAR)


def zoom(img, s, blur=0.0):
    M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, s)
    out = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REPLICATE)
    if blur > 0.02:
        sm = cv2.resize(out, (W // 4, H // 4)).astype(np.float32); acc = np.zeros_like(sm)
        for j in range(5):
            M2 = cv2.getRotationMatrix2D((W / 8, H / 8), 0, 1 + blur * j / 5)
            acc += cv2.warpAffine(sm, M2, (W // 4, H // 4), borderMode=cv2.BORDER_REPLICATE)
        out = cv2.resize((acc / 5).astype(np.uint8), (W, H))
    return out


def transition(name, d, u, A, B, live):
    """v2 (Codex #12): only the screen band moves; the facecam band below the seam is the live frame, untouched"""
    if name.endswith("Top"):
        out = live.copy()
        t = _transition(name[:-3], d, u, A[:SEAM], B[:SEAM])
        out[:SEAM] = t
        return out
    return _transition(name, d, u, A, B)


def _transition(name, d, u, A, B):
    """u in 0..1 across the window, cut at 0.5; A = outgoing picture, B = incoming"""
    Wd, Hd = A.shape[1], A.shape[0]
    if name == "Swipe":
        e = ease(u); sh = int(e * Wd)
        # round 7: the incoming side lands with a 3% settle (scale) so the whip feels caught, not slid
        if u > 0.5:
            B = push(B, 1 + 0.03 * (1 - eout((u - 0.5) * 2)), Wd / 2, Hd / 2)
        img = np.empty_like(A); img[:, :Wd - sh] = A[:, sh:]; img[:, Wd - sh:] = B[:, :sh]
        k = int(6 * u * (1 - u) * 260)
        if k >= 3:
            sm = cv2.resize(img, (Wd // 3, max(1, Hd // 3)), interpolation=cv2.INTER_AREA)
            sm = cv2.blur(sm, (max(3, int(k / 3) | 1), 1))
            img = cv2.resize(sm, (Wd, Hd), interpolation=cv2.INTER_LINEAR)
        return img
    if name == "Zoom":
        if u < 0.5:
            e = ease(u * 2); img = zoom(A, 1 + 0.4 * e, 0.12 * e)
        else:
            e = 1 - eout((u - 0.5) * 2); img = zoom(B, 1 + 0.3 * e, 0.1 * e)
        dip = max(0.0, 1 - abs(u - 0.5) * 8) * 0.35
        return cv2.convertScaleAbs(img, alpha=1 - dip) if dip else img
    if name == "Flash":
        # round 7: an exposure bloom (brighten + soft glow), peaking on the cut, instead of a flat white wash
        e = max(0.0, 1 - abs(u - 0.5) * 2) ** 1.8
        base = A if u < 0.5 else B
        glow = cv2.GaussianBlur(cv2.resize(base, (Wd // 4, Hd // 4)), (0, 0), 6)
        glow = cv2.resize(glow, (Wd, Hd))
        out = cv2.addWeighted(base, 1.0, glow, 0.9 * e, 255 * 0.35 * e)
        return out
    return B if u >= 0.5 else A


# ---------- overlays ----------
SPR = {}


def sprite(path):
    if path not in SPR:
        if len(SPR) > 200:
            SPR.clear()
        im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if im.shape[2] == 3:
            im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
        SPR[path] = im
    return SPR[path]


def settle(t, h, amp=0.10, T=0.30):
    """0 at t=0, 1 at the hit h (ease-out), then a damped overshoot settling by h+T"""
    if t <= h:
        return eout(t / h, 3)
    x = (t - h) / T
    return 1.0 if x >= 1 else 1 + amp * math.sin(math.pi * x) * (1 - x) ** 1.5


def over(dst, spr, cx, cy, sc, alpha, shine=None):
    h0, w0 = spr.shape[:2]
    w, h = max(1, round(w0 * sc)), max(1, round(h0 * sc))
    sp = cv2.resize(spr, (w, h), interpolation=cv2.INTER_AREA if sc < 1 else cv2.INTER_LINEAR)
    if shine is not None and 0 < shine < 1:
        # round 3: one diagonal light sweep across the card, masked by its own alpha
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        d = (xx + 0.45 * yy) / (w + 0.45 * h)
        g = np.exp(-((d - (shine * 1.5 - 0.25)) / 0.07) ** 2) * 0.22
        rgb = sp[..., :3].astype(np.float32)
        sp = sp.copy(); sp[..., :3] = np.clip(rgb + (255 - rgb) * g[..., None], 0, 255).astype(np.uint8)
    x0, y0 = round(cx - w / 2), round(cy - h / 2)
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if X1 <= X0 or Y1 <= Y0:
        return
    sp = sp[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    a = sp[..., 3:4].astype(np.float32) / 255 * alpha
    roi = dst[Y0:Y1, X0:X1]
    if shine is not None:      # round 3: cards get a soft dark backing so busy pages don't read through the glass
        bk = cv2.GaussianBlur(sp[..., 3], (0, 0), 6).astype(np.float32)[..., None] / 255 * alpha * 0.55
        roi[:] = (roi * (1 - bk)).astype(np.uint8)
    roi[:] = (sp[..., :3] * a + roi * (1 - a)).astype(np.uint8)


def draw_images(img, t, ims):
    for im in ims:
        lt = t - im["start"]
        if not (0 <= lt < im["duration"]):
            continue
        tail = im["duration"] - lt
        q = ease(1 - tail / 0.22) if tail < 0.22 and not im.get("noexit") else 0.0
        badge = im.get("slot") == "badge"
        # round 3: spring settle in (scale + a short rise), lift-and-fade out, one shine sweep on the cards
        sp_in = settle(lt, 0.14, amp=0.06 if badge else 0.09, T=0.34)
        if im["start"] == 0 and "hook" in im["path"] and lt < 0.22:       # round 6: the hook title slams in
            sp_in *= 1 + 0.16 * (1 - eout(lt / 0.22))
        rise = (1 - min(1.0, sp_in)) * 26
        if im.get("seq"):
            k = min(im["seq"]["frames"] - 1, int(lt * FPS + 1e-6) + HOOK_OFF * (im["start"] == 0 and "hook" in im["path"]))
            path = os.path.join(im["seq"]["dir"], f"{k:03d}.png")
            hook0 = im["start"] == 0 and "hook" in im["path"]
            sc = im["scale"] * (0.94 + 0.06 * sp_in) * (1 - 0.05 * q); a = (1.0 if hook0 else min(1.0, lt / 0.06)) * (1 - q)
        else:
            path = im["path"]
            sc = im["scale"] * (0.85 + 0.15 * sp_in) * (1 - 0.05 * q); a = min(1.0, lt / 0.08) * (1 - q)
        sh = (lt - 0.38) / 0.55 if im["duration"] > 1.2 and not badge else -1.0
        if a > 0.01:
            over(img, sprite(path), im["x"], im["y"] + rise - 20 * q, sc, a, shine=sh)
    return img


_SCRIM = (np.clip(1 - np.linspace(0, 1, 760) ** 2.2, 0, 1) * 0.78).astype(np.float32)[:, None, None]


def hook_scrim(img, t, hd=2.6):
    """darken the top of the frame behind the hook title (its own duration, round 9), fading out with it"""
    if t >= hd:
        return img
    k = 1.0 if t < hd - 0.3 else 1 - (t - (hd - 0.3)) / 0.3
    top = img[:760].astype(np.float32)
    img[:760] = (top * (1 - _SCRIM * k)).astype(np.uint8)
    return img


HOOK_OFF = 44   # round 6: frame 0 shows the finished hook title; the slam, punch and shake carry the motion


def hook_punch(img, t):
    """round 6: the first frame lands punched in 7% and eases out over 0.4 s with the hit"""
    return push(img, 1 + 0.07 * (1 - eout(t / 0.4, 3)), W / 2, H / 2) if t < 0.4 else img


def hook_shake(img, t, hit=0.02):
    """round 6: a short decaying camera shake on the hook's hit (overlays included)"""
    x = t - hit
    if not (0 <= x < 0.28):
        return img
    k = (1 - x / 0.28) ** 2
    dx, dy = 9 * k * math.sin(x * 95), 6 * k * math.cos(x * 120)
    M = np.float32([[1.012, 0, dx - 0.006 * W], [0, 1.012, dy - 0.006 * H]])
    return cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REPLICATE)


GOLD = (0x51, 0xC4, 0xF5)


def draw_rings(img, t, rings):
    """round 8: a gold ring draws itself around the price on screen, a soft spotlight dims the rest of the band"""
    for r in rings:
        lt = t - r["start"]
        if not (0 <= lt < r["duration"]):
            continue
        x0, y0, x1, y1 = r["box"]
        fade = min(1.0, (r["duration"] - lt) / 0.2) * min(1.0, lt / 0.08)
        band = img[:SEAM].astype(np.float32)
        mask = np.zeros((SEAM, W), np.float32); cv2.rectangle(mask, (x0 - 20, y0 - 20), (x1 + 20, y1 + 20), 1.0, -1)
        mask = cv2.GaussianBlur(mask, (0, 0), 18)
        img[:SEAM] = (band * (1 - 0.32 * fade * (1 - mask[..., None]))).astype(np.uint8)
        p = eout(lt / 0.3, 3)                      # the stroke draws on over 0.3 s, starting top-left, clockwise
        pts = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]], np.float32)
        seglen = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]; L = seglen[-1] * p
        poly = [pts[0]]
        for a_, b_, s0, s1 in zip(pts[:-1], pts[1:], seglen[:-1], seglen[1:]):
            if L <= s0:
                break
            poly.append(a_ + (b_ - a_) * min(1.0, (L - s0) / (s1 - s0)))
        poly = np.array(poly, np.int32).reshape(-1, 1, 2)
        glow = np.zeros_like(img[:SEAM])
        cv2.polylines(glow, [poly], False, GOLD, 12, cv2.LINE_AA); glow = cv2.GaussianBlur(glow, (0, 0), 7)
        img[:SEAM] = cv2.addWeighted(img[:SEAM], 1.0, glow, 0.8 * fade, 0)
        top = img[:SEAM].copy(); cv2.polylines(top, [poly], False, GOLD, 5, cv2.LINE_AA)
        img[:SEAM] = cv2.addWeighted(img[:SEAM], 1 - fade, top, fade, 0)
    return img


def draw_caps(img, t, caps, n):
    for k, c in enumerate(caps):
        if c["start"] <= t < c["end"]:
            lt = t - c["start"]
            p = eout(lt / 0.11) if lt < 0.11 else 1.0
            sc = 0.82 + 0.18 * p + (0.04 * math.sin(math.pi * min(1, lt / 0.2)) if lt < 0.2 else 0)
            act = max([0] + [i for i, wt in enumerate(c.get("wt", [])) if wt <= t + 1e-6])     # round 2: the word being said is lit
            spr = sprite(os.path.join(CAPS, f"s{n}_{k:03d}_{act}.png"))
            fit = min(1.0, c.get("maxw", 960) / (spr.shape[1] * 1.04))       # the visible box, overshoot included (Codex #7)
            over(img, spr, c.get("x", W / 2), c["y"], sc * fit, min(1.0, lt / 0.05))
    return img


# ---------- render ----------
def render_picture(n):
    S = load(n); src = S["source"]; segs, offs = S["segments"], S["offsets"]
    NF = round(S["total"] * FPS)
    starts = [round(o * FPS) for o in offs] + [NF]
    path = os.path.join(OUT, f"s{n}_picture.mp4")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-vf", "scale=in_range=pc:out_color_matrix=bt709:out_range=tv,format=yuv420p", "-color_range", "tv",
                            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                            "-c:v", "h264_nvenc", "-preset", "p5", "-tune", "hq", "-rc", "vbr", "-cq", "18", "-b:v", "0", "-maxrate", "40M",
                            "-bufsize", "80M", "-profile:v", "high", "-g", "120", path], stdin=subprocess.PIPE)
    trans = []   # (cut frame, name, half-width frames, i)
    for i, s in enumerate(segs):
        if s.get("tr") and i + 1 < len(segs):
            trans.append((starts[i + 1], s["tr"][0], round(s["tr"][1] / 2 * FPS), i))
    edges = {}
    for cut, name, hw, i in trans:
        na, nb = starts[i + 1] - starts[i], starts[i + 2] - starts[i + 1]
        edges[(i, "a")] = seam(finish(one_frame(segs[i], (na - 1) / FPS, src).copy(), segs[i], na - 1, na), segs[i])
        edges[(i, "b")] = seam(finish(one_frame(segs[i + 1], 0.0, src).copy(), segs[i + 1], 0, nb), segs[i + 1])
    for i, s in enumerate(segs):
        nfr = starts[i + 1] - starts[i]
        held = None
        for k, fr in enumerate(frames(s, nfr, src)):
            f = starts[i] + k; t = f / FPS
            if s.get("hold"):                          # round 9 (#4): the screen band holds its first frame (live face below)
                if held is None:
                    held = fr[:SEAM].copy()
                fr = fr.copy(); fr[:SEAM] = held
            img = seam(finish(fr.copy(), s, k, nfr, t), s)
            for cut, name, hw, j in trans:
                if cut - hw <= f < cut + hw:
                    u = (f - (cut - hw)) / (2 * hw)
                    img = transition(name, 2 * hw, u, img, edges[(j, "b")], img) if f < cut else transition(name, 2 * hw, u, edges[(j, "a")], img, img)
            img = hook_punch(img, t)
            img = hook_scrim(img, t, S.get("hook_d", 2.6))
            img = draw_rings(img, t, S.get("rings", []))
            img = draw_images(img, t, S["images"])
            img = draw_caps(img, t, S["captions"], n)
            enc.stdin.write(memoryview(np.ascontiguousarray(img)).cast("B"))
    enc.stdin.close(); enc.wait()
    return path


def wav(path, a=None, d=None):
    cmd = ["ffmpeg", "-v", "error"] + (["-ss", str(a)] if a is not None else []) + ["-i", path] + (["-t", str(d)] if d else []) + \
          ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()


def render_audio(n):
    S = load(n); L = int(round(S["total"] * SR))
    V = np.zeros((L, 2), np.float32); fade = int(0.015 * SR)
    for s, o in zip(S["segments"], S["offsets"]):
        if s["mute"]:
            continue
        x = wav(S["voice"], s["in"], s["out"] - s["in"])
        x[:fade] *= np.linspace(0, 1, fade)[:, None]; x[-fade:] *= np.linspace(1, 0, fade)[:, None]
        i0 = int(round(o * SR)); n_ = min(len(x), L - i0); V[i0:i0 + n_] += x[:n_]
    FX = np.zeros_like(V)
    for e in S["sfx"]:
        x = wav(e["path"]) * e["volume"]
        env = np.convolve(np.abs(x).mean(1), np.ones(480) / 480, "same"); po = int(env.argmax())
        st = int(round(e["peak_at"] * SR)) - po
        if st < 0:
            x, st = x[-st:], 0
        n_ = min(len(x), L - st)
        if n_ > 0:
            FX[st:st + n_] += x[:n_]
    tmp = lambda k: os.path.join(OUT, f"s{n}_{k}.wav")
    for k, arr in (("voice_raw", V), ("fx", FX)):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s24le", tmp(k)],
                       input=arr.tobytes(), check=True)
    # round 5: phone-speaker voice chain: rumble out, a little mud out, presence up, sibilance tamed, gentle levelling
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp("voice_raw"), "-af",
                    "highpass=f=80,equalizer=f=280:t=q:w=1.0:g=-2.5,equalizer=f=3400:t=q:w=1.2:g=2.0,"
                    "equalizer=f=11000:t=h:w=0.7:g=1.5,deesser=i=0.35:m=0.5:f=0.5,"
                    "acompressor=threshold=0.12:ratio=2.2:attack=6:release=90:makeup=1.25:knee=3", "-c:a", "pcm_s24le", tmp("voice")], check=True)
    # bed: looped to length, ~-27 LUFS before the duck, ducked ~8 dB under the voice; a bump in muted stretches
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", S["bed"], "-i", tmp("voice"), "-filter_complex",
                    f"[0:a]aresample={SR},aformat=channel_layouts=stereo,atrim=duration={S['total']:.3f},loudnorm=I=-24:TP=-3:LRA=7,"
                    "equalizer=f=2800:t=q:w=1.3:g=-4,"
                    f"afade=t=in:d=0.3,afade=t=out:st={max(0, S['total'] - 1.2):.3f}:d=1.2[m];"
                    "[m][1:a]sidechaincompress=threshold=0.03:ratio=4.5:attack=20:release=320:makeup=1[d]", "-map", "[d]",
                    "-c:a", "pcm_s24le", tmp("bed")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp("voice"), "-i", tmp("bed"), "-i", tmp("fx"), "-filter_complex",
                    "[0:a][1:a][2:a]amix=inputs=3:normalize=0[x]", "-map", "[x]", "-c:a", "pcm_s24le", tmp("pre")], check=True)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", tmp("pre"), "-af", "loudnorm=I=-14:TP=-1.2:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    j = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    af = (f"loudnorm=I=-14:TP=-1.2:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
          f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp("pre"), "-af", af, "-ar", str(SR), "-c:a", "pcm_s24le", tmp("mix")], check=True)
    return tmp("mix")


def render(n, audio_only=False):
    S = load(n)
    pic = os.path.join(OUT, f"s{n}_picture.mp4") if audio_only else render_picture(n)
    mix = render_audio(n)
    safe = "".join(c for c in S["title"] if c not in '\\/:*?"<>|')
    dst = os.path.join(OUT, f"Short {n} - {safe.rstrip('.')}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", pic, "-i", mix, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
                    "-movflags", "+faststart", "-shortest", dst], check=True)
    return dst


def stills(n, ts):
    S = load(n); src = S["source"]
    for t in ts:
        i = max(j for j, o in enumerate(S["offsets"]) if o <= t)
        s = S["segments"][i]
        nfr = round((S["offsets"][i + 1] if i + 1 < len(S["offsets"]) else S["total"]) * FPS) - round(S["offsets"][i] * FPS)
        k = round((t - S["offsets"][i]) * FPS)
        img = seam(finish(one_frame(s, t - S["offsets"][i], src).copy(), s, k, nfr), s)
        img = hook_punch(img, t); img = hook_scrim(img, t)
        img = draw_rings(img, t, S.get("rings", [])); img = draw_images(img, t, S["images"]); img = draw_caps(img, t, S["captions"], n); img = hook_shake(img, t)
        cv2.imwrite(os.path.join(OUT, f"still_s{n}_{t:06.2f}.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 88])


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "captions":
        jobs = []
        for f in sorted(os.listdir(HERE)):
            if f.startswith("s") and f.endswith(".json") and f[1:-5].isdigit():
                S = json.load(open(os.path.join(HERE, f), encoding="utf-8"))
                for k, c in enumerate(S["captions"]):
                    jobs.append({"name": f"s{S['n']}_{k:03d}", "words": c["text"], "accent": c["accent"]})
        json.dump(jobs, open(os.path.join(CAPS, "jobs.json"), "w"))
        subprocess.run(["node", os.path.join(HERE, "captions.mjs")], check=True)
    elif cmd == "render":
        ns = list(range(1, 9)) if sys.argv[2:] == ["all"] else [int(x) for x in sys.argv[2:]]
        with ProcessPoolExecutor(4) as ex:
            for p in ex.map(render, ns):
                print("done", p, flush=True)
    elif cmd == "audio":           # picture unchanged: re-mix and re-mux only
        ns = list(range(1, 9)) if sys.argv[2:] == ["all"] else [int(x) for x in sys.argv[2:]]
        with ProcessPoolExecutor(4) as ex:
            for p in ex.map(render, ns, [True] * len(ns)):
                print("done", p, flush=True)
    elif cmd == "still":
        stills(int(sys.argv[2]), [float(x) for x in sys.argv[3:]])
