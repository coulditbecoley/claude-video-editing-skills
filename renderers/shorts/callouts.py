"""Round 8: on-screen callouts. When a spoken caption word is a price/number and the screen band shows that price, OCR the
band at that moment and ring the exact text. Writes callouts.json {n: [{box, start, duration, word}]} (output px, top band).
python callouts.py   (after gen_shorts.py; gen_shorts.py picks callouts.json up on its next run)"""
import json, os, re, subprocess
import numpy as np
from rapidocr_onnxruntime import RapidOCR

HERE = os.path.dirname(os.path.abspath(__file__))
W, SEAM = 1080, 740
ocr = RapidOCR()
NUM = re.compile(r"^\$?(\d+)$")
out = {}
for n in range(1, 9):
    d = json.load(open(os.path.join(HERE, f"s{n}.json"), encoding="utf-8"))
    segs, offs, res, last = d["segments"], d["offsets"], [], -9
    toks = [(w, tw) for c in d["captions"] for w, tw in zip(c["text"], c["wt"])]
    cards = [(im["start"], im["start"] + im["duration"]) for im in d["images"] if im.get("slot") == "top"]
    for j, (w, tw) in enumerate(toks):
        nxt = toks[j + 1][0] if j + 1 < len(toks) else ""
        w2 = {"NINE": "9", "TWELVE": "12"}.get(w, w)
        m = NUM.match(w2)
        price = m and (w.startswith("$") or nxt in ("BUCKS", "DOLLARS", "DOLLAR"))
        if not price or tw - last < 1.2 or any(a - 0.1 <= tw <= b + 1.3 for a, b in cards):
            continue
        if True:
            i = max(j for j, o in enumerate(offs) if o <= tw + 1e-6)
            s = segs[i]
            if s["layout"] != "split" or s["mute"]:
                continue
            x0, y0, bw = s["band"]; bh = round(bw * SEAM / W) // 2 * 2
            pt = s["in"] + (tw - offs[i]) * s["speed"] + s["pic_off"] + 0.15
            raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{pt:.3f}", "-i", d["source"], "-frames:v", "1", "-vf",
                                  f"crop={bw}:{bh}:{x0}:{y0}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
            img = np.frombuffer(raw, np.uint8).reshape(bh, bw, 3)
            r, _ = ocr(img)
            best = None
            for box, text, conf in r or []:
                t = text.replace(" ", "")
                if "$" in t and re.search(rf"(?<!\d){m.group(1)}(?!\d)", t) and float(conf) > 0.6:
                    xs, ys = [p[0] for p in box], [p[1] for p in box]
                    # ring just the price token when the OCR line is longer ("$12 USD, one-time")
                    k = t.find(m.group(1)); frac0 = max(0, t.find("$")) / len(t); frac1 = min(1, (k + len(m.group(1)) + 0.5) / len(t))
                    bx0 = min(xs) + (max(xs) - min(xs)) * frac0; bx1 = min(xs) + (max(xs) - min(xs)) * frac1
                    cand = (bx0, min(ys), bx1, max(ys))
                    if best is None or (cand[3] - cand[1]) > (best[3] - best[1]):
                        best = cand
            if best:
                sc = W / bw
                bx = [round(best[0] * sc) - 14, round(best[1] * sc) - 10, round(best[2] * sc) + 14, round(best[3] * sc) + 10]
                if bx[3] < SEAM - 6 and bx[2] - bx[0] > 24:
                    res.append({"box": bx, "start": round(tw - 0.05, 3), "duration": 1.3, "word": w})
                    last = tw
    out[n] = res
    print(n, [(r["word"], r["start"], r["box"]) for r in res])
json.dump(out, open(os.path.join(HERE, "callouts.json"), "w"), indent=1)
