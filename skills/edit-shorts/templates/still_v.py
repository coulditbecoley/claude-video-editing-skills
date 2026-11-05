"""Render what a 9:16 Short shows at output seconds, from the files (never CapCut's timeline).
usage: python still_v.py s1 0.5 4 12 ...  ->  probe/s1_<t>.jpg (540x960)"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
E = json.loads((HERE / f"{sys.argv[1]}.edl.json").read_text(encoding="utf-8"))
CW, CH = E["resolution"]
(HERE / "probe").mkdir(exist_ok=True)

def frame(src, t):
    out = HERE / "probe" / "_f.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", src, "-frames:v", "1", str(out)], check=True)
    return Image.open(out).convert("RGBA")

for T in map(float, sys.argv[2:]):
    off = 0.0
    for seg in E["segments"]:
        d = (seg["out"] - seg["in"]) / seg.get("speed", 1.0)
        if off <= T < off + d:
            break
        off += d
    ts = seg["in"] + (T - off) * seg.get("speed", 1.0)
    src = frame(E["source"], ts)
    f = seg.get("frame", {"scale": 1, "x": 0, "y": 0})
    S = f["scale"]
    w, h = round(CW * S), round(CW * S * src.height / src.width)
    img = src.resize((w, h))
    cx, cy = CW / 2 + f["x"] * CW / 2, CH / 2 - f["y"] * CH / 2
    canvas = Image.new("RGBA", (CW, CH), (0, 0, 0, 255))
    canvas.alpha_composite(img, (round(cx - w / 2), round(cy - h / 2))) if cx - w / 2 >= 0 and cy - h / 2 >= 0 else \
        canvas.paste(img, (round(cx - w / 2), round(cy - h / 2)), img)
    cam = seg.get("cam_overlay")
    if cam:
        x0, y0, x1, y1 = cam["rect"]
        k = cam.get("k0", 1.0)
        c = frame(cam["clip"], ts).resize((round((x1 - x0) * k), round((y1 - y0) * k)))
        canvas.paste(c, (x0, y0), c)
    for im in E["images"]:
        if im["start"] <= T < im["start"] + im["duration"]:
            p = Image.open(im["path"]).convert("RGBA")
            sc = im.get("scale", 1.0)
            p = p.resize((round(p.width * sc), round(p.height * sc)))
            canvas.paste(p, (round(im["x"] - p.width / 2), round(im["y"] - p.height / 2)), p)
    out = HERE / "probe" / f"{sys.argv[1]}_{T:.1f}.jpg"
    canvas.convert("RGB").resize((540, 960)).save(out)
    print(out.name, f"src {ts:.2f}")
