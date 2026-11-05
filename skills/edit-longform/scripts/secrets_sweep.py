# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["rapidocr-onnxruntime", "numpy"]
# ///
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
import argparse, json, re, subprocess, sys
from pathlib import Path

import numpy as np
from rapidocr_onnxruntime import RapidOCR

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


def frames(clip, every, sw, sh, hw=True):
    """Yield every `every`-th second as a BGR array at sw x sh. ffmpeg decodes on the GPU and drops
    the rest; OpenCV's grab() software-decodes every 4K frame, which was the whole cost."""
    cmd = ["ffmpeg", "-v", "error"] + (["-hwaccel", "cuda"] if hw else []) + [
        "-i", str(clip), "-vf", f"fps=1/{every},scale={sw}:{sh}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=0)
    n = sw * sh * 3
    buf = bytearray(n)
    while True:
        view, got = memoryview(buf), 0
        while got < n:
            r = p.stdout.readinto(view[got:])
            if not r:
                break
            got += r
        if got < n:
            break
        yield np.frombuffer(buf, np.uint8).reshape(sh, sw, 3)
    if p.wait() != 0 and hw:
        raise RuntimeError("ffmpeg decode failed; retry with --cpu")


def sweep(clip, every, hw=True):
    w, h, dur = probe(clip)
    k = min(1.0, 1920 / w)                           # OCR at <=1080p: 4K OCR is far slower, no gain
    sw, sh = int(w * k) // 2 * 2, int(h * k) // 2 * 2
    ocr, hits, prev, last, skipped = RapidOCR(), [], None, [], 0
    for i, frame in enumerate(frames(clip, every, sw, sh, hw)):
        thumb = frame[::8, ::8].astype(np.int16)
        # ponytail: a still screen reuses the last OCR (OCR is 5-9 s a busy frame). The threshold is a guess;
        # lower it if a small change (one new terminal line) ever gets missed.
        if prev is not None and np.abs(thumb - prev).mean() < 1.5:
            skipped += 1
        else:
            last = []
            for box, text, _conf in (ocr(frame)[0] or []):
                if looks_secret(text):
                    xs, ys = [p[0] * w / sw for p in box], [p[1] * h / sh for p in box]
                    last.append({"box": [min(xs), min(ys), max(xs), max(ys)], "text": mask(text)})
            prev = thumb
        hits += [{"t": i * every, **x} for x in last]
    print(f"OCR'd {i + 1 - skipped} of {i + 1} samples (rest unchanged)", file=sys.stderr)
    return hits, (w, h), dur


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
    # same encoder settings as render_mp4.py so the redacted source loses nothing visible
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(clip), "-filter_complex", ";".join(chains),
                    "-map", f"[{last}]", "-map", "0:a?", "-c:a", "copy",
                    "-c:v", "hevc_nvenc", "-preset", "p4", "-tune", "hq", "-rc", "vbr", "-cq", "17", "-b:v", "0",
                    "-maxrate", "160M", "-bufsize", "320M", str(out)], check=True)
    return out


def _check():
    assert looks_secret("OPENAI_API_KEY=sk-proj-abcd1234efgh5678ijkl")  # gitleaks:allow (fake test value)
    assert looks_secret("ghp_0123456789abcdefghijABCDEFGHIJ")  # gitleaks:allow (fake test value)
    assert looks_secret("a3f1" * 16)
    assert not looks_secret("Claude Code is editing this video")
    assert not looks_secret("internationalizationlocalizations")
    sp = merge([{"t": 0, "box": [0, 0, 10, 10], "text": ""}, {"t": 2, "box": [5, 5, 12, 12], "text": ""},
                {"t": 2, "box": [100, 100, 110, 110], "text": ""}], 2, 60)
    assert len(sp) == 2 and sp[0]["box"] == [0, 0, 12, 12] and sp[0]["end"] == 4


if __name__ == "__main__":
    _check()
    ap = argparse.ArgumentParser()
    ap.add_argument("clip", type=Path)
    ap.add_argument("--every", type=float, default=2.0, help="seconds between OCR samples")
    ap.add_argument("--pad", type=int, default=20, help="px added round each blur box")
    ap.add_argument("--apply", action="store_true", help="write <clip>.redacted.mp4")
    ap.add_argument("--cpu", action="store_true", help="decode on the CPU (no NVIDIA GPU)")
    a = ap.parse_args()
    hits, size, dur = sweep(a.clip, a.every, not a.cpu)
    spans = merge(hits, a.every, dur)
    report = a.clip.with_suffix(".secrets.json")
    report.write_text(json.dumps({"clip": str(a.clip), "every": a.every, "spans": spans}, indent=1))
    for s in spans:
        print(f"{s['start']:8.1f}-{s['end']:.1f}s  box {[int(v) for v in s['box']]}  {s['text']}")
    print(f"{len(spans)} span(s) -> {report}")
    if a.apply and spans:
        print("redacted ->", apply(a.clip, spans, size, a.pad))
    sys.exit(0)
