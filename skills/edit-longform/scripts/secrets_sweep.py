# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["rapidocr-onnxruntime", "numpy", "onnxruntime-gpu==1.22.*", "nvidia-cudnn-cu12==9.8.*",
#   "nvidia-cublas-cu12", "nvidia-cuda-runtime-cu12", "nvidia-cufft-cu12", "nvidia-curand-cu12", "nvidia-cuda-nvrtc-cu12"]
# [tool.uv]
# override-dependencies = ["onnxruntime; sys_platform == 'never'"]
# ///
# GPU OCR (2026-11-04): onnxruntime-gpu 1.22 needs cuDNN 9.8 exactly (9.28 fails "CUDNN_BACKEND_API_FAILED"), and the
# CPU onnxruntime that rapidocr pulls in must be overridden away or it shadows the GPU build. 1.1 s vs 4.8 s a frame.
"""Find (and optionally blur) API keys, tokens and passwords visible in a screen recording.

    uv run secrets_sweep.py <clip.mp4>                 # report -> <clip>.secrets.json
    uv run secrets_sweep.py <clip.mp4> --apply         # also writes <clip>.redacted.mp4
    uv run secrets_sweep.py <clip.mp4> --every 1.5 --pad 24

OCRs one frame every --every seconds, flags text that looks like a secret, merges hits on the
same spot into time spans (padded by one sample each side, since a secret can appear between
samples), and with --apply blurs those boxes over those spans into a copy of the clip. Use the
redacted copy as the edit source (CapCut or Rendered MP4 mode); the original is never touched.

Matched text is never printed or saved in full: only the first 4 chars and the length.
ponytail: sampled OCR, so a secret on screen for less than --every s can slip through. Lower
--every for fast scrolling, and still eyeball any terminal or .env shot in review.
"""
import argparse, json, os, re, subprocess, sys
from pathlib import Path

import numpy as np
import onnxruntime as ort
try:
    ort.preload_dlls()          # loads the pip nvidia CUDA/cuDNN DLLs; harmless when absent
except Exception:
    pass
from rapidocr_onnxruntime import RapidOCR

GPU_OCR = "CUDAExecutionProvider" in ort.get_available_providers()


def make_ocr(gpu=True):
    """RapidOCR on CUDA when available. Reports the providers its three ONNX sessions actually got (audit r2: a
    requested GPU can silently fall back to CPU), not the request."""
    use = gpu and GPU_OCR
    o = RapidOCR(det_use_cuda=use, cls_use_cuda=use, rec_use_cuda=use)
    active = []
    for name in ("text_det", "text_cls", "text_rec"):
        m = getattr(o, name, None)
        inf = getattr(m, "infer", None) or getattr(m, "session", None)     # det/cls use .infer, rec uses .session
        sess = getattr(inf, "session", inf)
        active.append(sess.get_providers()[0] if hasattr(sess, "get_providers") else "unknown")
    return o, all(a == "CUDAExecutionProvider" for a in active)

PATTERNS = [
    r"sk-[A-Za-z0-9_\-]{16,}", r"\b[sprw]k_(live|test)_[A-Za-z0-9]{10,}", r"\bre_[A-Za-z0-9_]{20,}",
    r"gh[pousr]_[A-Za-z0-9]{20,}", r"github_pat_[A-Za-z0-9_]{20,}", r"AKIA[0-9A-Z]{16}",
    r"xox[abprs]-[A-Za-z0-9\-]{10,}", r"AIza[0-9A-Za-z_\-]{30,}", r"eyJ[\w\-]{10,}\.[\w\-]{10,}",
    r"(?i)(api[_ ]?key|token|secret|passw(or)?d|private[_ ]?key|bearer)\s*[=:]\s*\S{6,}",
    r"\b[0-9a-fA-F]{40,}\b",                        # hex keys (incl. 64-char private keys)
    r"[A-Za-z0-9_\-+/]{32,}={0,2}",                 # long base64/base58-ish blobs
]
RX = [re.compile(p) for p in PATTERNS]


def looks_secret(text):
    for rx in RX:
        m = rx.search(text)
        if m and not m.group(0).isalpha():          # a 32-letter word isn't a key
            return True
    return False


def mask(text):
    return f"{text[:4]}... ({len(text)} chars)"


def probe(clip):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:format=duration", "-of", "json", str(clip)],
                         capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    return j["streams"][0]["width"], j["streams"][0]["height"], float(j["format"]["duration"])


def frames(clip, every, sw, sh, hw=True, cmd=None):
    """Yield every `every`-th second as a BGR array at sw x sh. ffmpeg decodes on the GPU and drops the rest
    (OpenCV's grab() software-decodes every 4K frame, which was the whole cost). Fails closed: any nonzero decoder
    exit raises, in CPU and GPU mode alike, so a crashed decode can never pass as a finished scan."""
    cmd = cmd or (["ffmpeg", "-v", "error"] + (["-hwaccel", "cuda"] if hw else []) + [
        "-i", str(clip), "-vf", f"fps=1/{every},scale={sw}:{sh}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"])
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=0)
    n = sw * sh * 3
    buf = bytearray(n)
    try:
        while True:
            view, got = memoryview(buf), 0
            while got < n:
                r = p.stdout.readinto(view[got:])
                if not r:
                    break
                got += r
            if got == 0:
                break
            if got < n:
                raise RuntimeError(f"decoder returned a partial frame ({got} of {n} bytes)")
            yield np.frombuffer(buf, np.uint8).reshape(sh, sw, 3)
        rc = p.wait()
        if rc != 0:
            raise RuntimeError(f"decoder exited {rc}" + ("; retry with --cpu" if hw else ""))
    finally:
        if p.poll() is None:
            p.kill()
            p.wait()


TILE, TILE_DIFF = 32, 6.0   # ponytail: per-tile mean abs diff (grey, 0-255); one new terminal line moves its tile by ~100


def changed(prev, cur):
    """True when any tile changed. Tiles are 32x32, and the partial tiles along the right and bottom edges are
    their own (smaller) tiles: averaging the leftover 24-row strip across the full width hid a new bottom terminal
    line (audit r2 #1). A whole-frame mean hid one too (audit r1 #1)."""
    if prev is None or prev.shape != cur.shape:
        return True
    d = np.abs(cur.astype(np.float32) - prev.astype(np.float32))
    ys, xs = np.arange(0, d.shape[0], TILE), np.arange(0, d.shape[1], TILE)
    sums = np.add.reduceat(np.add.reduceat(d, ys, axis=0), xs, axis=1)
    hs = np.diff(np.append(ys, d.shape[0]))
    ws = np.diff(np.append(xs, d.shape[1]))
    return bool((sums / np.outer(hs, ws)).max() > TILE_DIFF)


def sweep(clip, every, hw=True, ocr=None, frame_iter=None):
    w, h, dur = probe(clip) if frame_iter is None else frame_iter[1]
    k = min(1.0, 1920 / w)                           # OCR at <=1080p: 4K OCR is far slower, no gain
    sw, sh = int(w * k) // 2 * 2, int(h * k) // 2 * 2
    if ocr is None:
        ocr, on_gpu = make_ocr(hw)
        print(f"OCR on {'GPU (all three sessions on CUDA)' if on_gpu else 'CPU'}", file=sys.stderr)
    hits, prev, last, n, calls = [], None, [], 0, 0
    for i, frame in enumerate(frames(clip, every, sw, sh, hw) if frame_iter is None else frame_iter[0]):
        n = i + 1
        grey = frame.mean(axis=2)
        if changed(prev, grey):
            last, calls = [], calls + 1
            for box, text, _conf in (ocr(frame)[0] or []):
                if looks_secret(text):
                    xs, ys = [p[0] * w / sw for p in box], [p[1] * h / sh for p in box]
                    last.append({"box": [min(xs), min(ys), max(xs), max(ys)], "text": mask(text)})
            prev = grey
        hits += [{"t": i * every, **x} for x in last]
    expected = int(dur // every) + 1
    if n == 0 or n < expected - 1:
        raise RuntimeError(f"incomplete scan: {n} of ~{expected} samples decoded")
    print(f"OCR'd {calls} of {n} samples (rest unchanged)", file=sys.stderr)
    return hits, (w, h), dur, {"samples": n, "ocr_calls": calls}


def overlap(a, b):
    ix = min(a[2], b[2]) - max(a[0], b[0])
    iy = min(a[3], b[3]) - max(a[1], b[1])
    return ix > 0 and iy > 0


def merge(hits, every, dur):
    spans = []
    for h in hits:
        s = next((s for s in spans if overlap(s["box"], h["box"]) and h["t"] - s["end"] <= every * 1.5), None)
        if s:
            s["end"] = h["t"]
            s["box"] = [min(s["box"][0], h["box"][0]), min(s["box"][1], h["box"][1]),
                        max(s["box"][2], h["box"][2]), max(s["box"][3], h["box"][3])]
        else:
            spans.append({"start": h["t"], "end": h["t"], "box": list(h["box"]), "text": h["text"]})
    for s in spans:
        s["start"], s["end"] = max(0.0, s["start"] - every), min(dur, s["end"] + every)
    return spans


def apply(clip, spans, size, pad):
    w, h = size
    chains, last = [], "0:v"
    for k, s in enumerate(spans):
        x0, y0 = max(0, int(s["box"][0]) - pad), max(0, int(s["box"][1]) - pad)
        x1, y1 = min(w, int(s["box"][2]) + pad), min(h, int(s["box"][3]) + pad)
        bw, bh = (x1 - x0) // 2 * 2, (y1 - y0) // 2 * 2
        en = f"between(t,{s['start']:.3f},{s['end']:.3f})"
        r = max(1, min(24, bw // 4 - 1, bh // 4 - 1))  # boxblur: chroma radius must be < half the chroma plane
        chains.append(f"[{last}]split[m{k}][c{k}];[c{k}]crop={bw}:{bh}:{x0}:{y0},boxblur={r}:4[b{k}];"
                      f"[m{k}][b{k}]overlay={x0}:{y0}:enable='{en}'[v{k}]")
        last = f"v{k}"
    out = clip.with_suffix(".redacted.mp4")
    tmp = clip.with_suffix(".redacted.partial.mp4")
    # same encoder settings as render_mp4.py so the redacted source loses nothing visible; written to a temp name and
    # renamed only on success, so a stale or half-written redacted file is never mistaken for this scan's output
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(clip), "-filter_complex", ";".join(chains),
                    "-map", f"[{last}]", "-map", "0:a?", "-c:a", "copy",
                    "-c:v", "hevc_nvenc", "-preset", "p4", "-tune", "hq", "-rc", "vbr", "-cq", "17", "-b:v", "0",
                    "-maxrate", "160M", "-bufsize", "320M", str(tmp)], check=True)
    os.replace(tmp, out)
    return out


def identity(path):
    st = os.stat(path)
    return {"path": str(path), "size": st.st_size, "mtime_ns": st.st_mtime_ns}


def _check():
    assert looks_secret("OPENAI_API_KEY=sk-proj-abcd1234efgh5678ijkl")
    assert looks_secret("ghp_0123456789abcdefghijABCDEFGHIJ")
    assert looks_secret("a3f1" * 16)
    assert not looks_secret("Claude Code is editing this video")
    assert not looks_secret("internationalizationlocalizations")
    sp = merge([{"t": 0, "box": [0, 0, 10, 10], "text": ""}, {"t": 2, "box": [5, 5, 12, 12], "text": ""},
                {"t": 2, "box": [100, 100, 110, 110], "text": ""}], 2, 60)
    assert len(sp) == 2 and sp[0]["box"] == [0, 0, 12, 12] and sp[0]["end"] == 4
    # one new 400x20 terminal line on a still 1080p screen must trigger OCR (audit r1 finding 1)
    rng = np.random.default_rng(0)
    a = rng.integers(20, 24, (1080, 1920)).astype(np.float64)          # still screen + codec noise
    b = a + rng.integers(-2, 3, a.shape)
    assert not changed(a, b)
    c = b.copy()
    c[100:120, 100:500] = 255
    assert changed(b, c)
    # real rendered text in the bottom 24-row partial strip (audit r2 #1), and frames smaller than one tile
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.load_default(size=18)      # bundled with Pillow: same glyphs on Windows and Linux
    im = Image.new("L", (1920, 1080), 0)
    ImageDraw.Draw(im).text((100, 1057), "sk-proj-TESTONLY0000000000000", fill=255, font=font)
    assert changed(np.zeros((1080, 1920)), np.asarray(im, dtype=np.float64)), "bottom-strip text missed"
    im2 = Image.new("L", (1920, 1080), 0)
    ImageDraw.Draw(im2).text((1890, 500), "sk-", fill=255, font=font)       # right-edge partial column
    assert changed(np.zeros((1080, 1920)), np.asarray(im2, dtype=np.float64)), "right-edge text missed"
    assert changed(np.zeros((10, 10)), np.full((10, 10), 50.0)) and not changed(np.zeros((10, 10)), np.zeros((10, 10)))
    # end to end with a fake OCR: the second frame's new line must be OCR'd and its key found
    f1 = np.zeros((1080, 1920, 3), np.uint8)
    f2 = f1.copy()
    f2[100:120, 100:500] = 255
    calls = []

    def fake_ocr(img):
        calls.append(1)
        return ([([[100, 100], [500, 100], [500, 120], [100, 120]], "sk-proj-TESTONLY0000000000000", 0.9)]
                if img[110, 300, 0] == 255 else [],)
    hits, _, _, st = sweep(None, 2.0, ocr=fake_ocr, frame_iter=([f1, f2], (1920, 1080, 3.9)))
    assert len(calls) == 2 and len(hits) == 1 and hits[0]["t"] == 2.0, (calls, hits)
    # a decoder that emits one frame then exits 1 must raise, in CPU mode too (audit r1 finding 2)
    bad = [sys.executable, "-c", "import sys; sys.stdout.buffer.write(bytes(12)); sys.exit(1)"]
    try:
        list(frames(None, 2.0, 2, 2, hw=False, cmd=bad))
        raise AssertionError("decoder failure was accepted")
    except RuntimeError:
        pass
    # zero decoded samples must not pass as a clean scan
    try:
        sweep(None, 2.0, ocr=fake_ocr, frame_iter=([], (1920, 1080, 10.0)))
        raise AssertionError("empty scan was accepted")
    except RuntimeError:
        pass


if __name__ == "__main__":
    _check()
    ap = argparse.ArgumentParser()
    ap.add_argument("clip", type=Path)
    ap.add_argument("--every", type=float, default=2.0, help="seconds between OCR samples")
    ap.add_argument("--pad", type=int, default=20, help="px added round each blur box")
    ap.add_argument("--apply", action="store_true", help="write <clip>.redacted.mp4")
    ap.add_argument("--cpu", action="store_true", help="decode on the CPU (no NVIDIA GPU)")
    a = ap.parse_args()
    report = a.clip.with_suffix(".secrets.json")
    import hashlib
    code = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    # reuse a completed scan of the same input + sampling + code (a repeat run cost ~1.3 min per minute of 4K)
    try:
        old = json.loads(report.read_text())
        sel = old.get("selected")
        if (old.get("completed") and old.get("input") == identity(a.clip) and old.get("every") == a.every
                and old.get("code") == code and (old["spans"] == [] or not a.apply or sel)
                and (sel is None or (os.path.exists(sel["path"]) and identity(sel["path"]) == sel))):
            print(f"cached scan: {len(old['spans'])} span(s), {old['samples']} samples -> {report}")
            if sel:
                print(f"EDIT SOURCE: {sel['path']}")
                sys.exit(0)
            print("EDIT SOURCE: none - secrets found; re-run with --apply")
            sys.exit(2)
    except (OSError, ValueError, KeyError, TypeError):
        pass
    hits, size, dur, stats = sweep(a.clip, a.every, not a.cpu)    # raises on any incomplete decode: no report written
    spans = merge(hits, a.every, dur)
    for s in spans:
        print(f"{s['start']:8.1f}-{s['end']:.1f}s  box {[int(v) for v in s['box']]}  {s['text']}")
    if not spans:
        selected = a.clip                       # completed scan, nothing found: edit the input itself
    elif a.apply:
        selected = apply(a.clip, spans, size, a.pad)
    else:
        selected = None                         # secrets found, not yet blurred: no safe source yet
    report.write_text(json.dumps({"input": identity(a.clip), "every": a.every, "completed": True, "code": code, **stats,
                                  "spans": spans, "selected": selected and identity(selected)}, indent=1))
    print(f"{len(spans)} span(s), {stats['samples']} samples, {stats['ocr_calls']} OCR'd -> {report}")
    if selected:
        print(f"EDIT SOURCE: {selected}")
    else:
        print("EDIT SOURCE: none - secrets found; re-run with --apply")
    sys.exit(0 if selected else 2)
