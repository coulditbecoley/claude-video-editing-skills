"""Check the draft CapCut actually saved against the EDL. Run after opening the
draft in CapCut, before telling Coley it's ready.

usage: python verify_draft.py "<draft name>" <edit.edl.json>

Fails on: a canvas that isn't the EDL resolution (a 3840x1 canvas once hung every
export at 30% "Applying features..."), or any main-video / voice segment whose
timeline position, source in-point or length drifted from the EDL (a stray click
on CapCut's timeline once trimmed two clips and broke lip sync).
"""
import json
import os
import sys

name, edl_path = sys.argv[1], sys.argv[2]
d = json.load(open(os.path.expandvars(rf"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\{name}\draft_content.json"), encoding="utf-8"))
e = json.load(open(edl_path, encoding="utf-8"))
problems = []
cw, ch = d["canvas_config"]["width"], d["canvas_config"]["height"]
if [cw, ch] != list(e.get("resolution", [1920, 1080])):
    problems.append(f"canvas {cw}x{ch} != EDL {e.get('resolution')}")
main = next(t for t in d["tracks"] if t["type"] == "video")
n_voiced = sum(1 for s in e["segments"] if not s.get("mute"))   # muted (fast-forward) pieces have no voice segment
# the voice track = the audio track playing the EDL's voice file (a count match alone can pick an SFX track)
vfiles = {os.path.basename(v).lower() for v in (e.get("voice") or {}).values()}
apath = {m["id"]: os.path.basename(m.get("path", "")).lower() for m in d["materials"].get("audios", [])}
voice = [t for t in d["tracks"] if t["type"] == "audio" and t["segments"]
         and apath.get(t["segments"][0]["material_id"]) in vfiles and len(t["segments"]) == n_voiced]
off, vi = 0.0, 0
for i, s in enumerate(e["segments"]):
    sp = s.get("speed", 1.0)
    for label, track, k in (("video", main, i), ("voice", voice[0] if voice and not s.get("mute") else None, vi)):
        if track is None:
            continue
        seg = track["segments"][k]
        ts, ss = seg["target_timerange"]["start"] / 1e6, seg["source_timerange"]["start"] / 1e6
        sd = seg["source_timerange"]["duration"] / 1e6
        exp_in = s["in"] - (float(s.get("av_offset", e.get("av_offset", 0.0))) if label == "voice" else 0.0)
        if abs(ts - off) > 0.05 or abs(ss - exp_in) > 0.05 or abs(sd - (s["out"] - s["in"])) > 0.05 * sp + 0.034 * sp:   # CapCut snaps a sped-up piece to whole output frames
            problems.append(f"segment {i} {label}: expected at {off:.2f}s src {exp_in:.2f}+{s['out'] - s['in']:.2f}, "
                            f"got at {ts:.2f}s src {ss:.2f}+{sd:.2f}")
    vi += 0 if s.get("mute") else 1
    off += (s["out"] - s["in"]) / sp
print(f"canvas {cw}x{ch}, {len(main['segments'])} segments, voice track {'yes' if voice else 'NO'}")
print("\n".join(problems) if problems else "DRAFT OK")
sys.exit(1 if problems else 0)
