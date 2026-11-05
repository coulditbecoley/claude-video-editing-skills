"""QA after a polish round: contact sheet (10 frames per Short), loudness, duration, frame count.
python qa_round.py R   ->  probe/round_R_sheet.jpg + printed table"""
import glob, os, subprocess, sys, json
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
R = sys.argv[1]
fs = sorted(glob.glob(os.path.join(HERE, "out", "Short *.mp4")))
cols = 10
g = Image.new("RGB", (180 * cols, 320 * len(fs)))
for r, f in enumerate(fs):
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-show_entries", "format=duration:stream=nb_read_packets",
                                    "-select_streams", "v", "-of", "json", f], capture_output=True, text=True).stdout)
    d = float(pr["format"]["duration"]); nf = int(pr["streams"][0]["nb_read_packets"])
    e = subprocess.run(["ffmpeg", "-hide_banner", "-i", f, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = [l for l in e.splitlines() if " I:" in l][-1].split()[1]; P = [l for l in e.splitlines() if "Peak:" in l][-1].split()[1]
    print(f"{os.path.basename(f)[:8]}  {d:5.1f}s  {nf} frames  {I} LUFS  peak {P}")
    for c in range(cols):
        t = 0.5 + c * (d - 0.9) / (cols - 1)
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", f, "-frames:v", "1", "-vf", "scale=180:320", "-f", "rawvideo",
                              "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        g.paste(Image.frombytes("RGB", (180, 320), raw), (c * 180, r * 320))
g.save(os.path.join(HERE, "probe", f"round_{R}_sheet.jpg"), quality=85)
