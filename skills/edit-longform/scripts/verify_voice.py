"""The verify gate: stitch the edited voice exactly as the EDL cuts it, so the
result can be re-transcribed literally and read for chopped words, bad joins and
leftover retakes, before anything is built in CapCut.

usage: python verify_voice.py <edit.edl.json> [out.wav]
then:  uv run python <skill>/scripts/transcribe_words.py --literal out.wav   (from capcut-cli)

To check one join by ear, cut 6 s around it from out.wav and transcribe just that:
the full-file pass sometimes skips a sentence that is really there.

Pieces are sliced sample-exact from the processed voice WAV(s). The old ffmpeg concat-demuxer
version rounded every inpoint/outpoint to an audio packet, so a 115-piece edit came out ~5 s
long and its timings drifted against the draft (Codex audit, AI Agents Business Ep 1, 2026-10-06).
A muted (fast-forward) piece contributes silence of its output length.
"""
import json
import sys
import wave

edl = json.load(open(sys.argv[1], encoding="utf-8"))
out = sys.argv[2] if len(sys.argv) > 2 else "qa_voice.wav"
srcs = {}

def reader(path):
    if path not in srcs:
        srcs[path] = wave.open(path, "rb")
    return srcs[path]

params, chunks = None, []
for s in edl["segments"]:
    w = reader(edl["voice"][s.get("source", edl["source"])])
    params = params or w.getparams()
    rate, width = w.getframerate(), w.getsampwidth() * w.getnchannels()
    if s.get("mute"):
        n = round((s["out"] - s["in"]) / s.get("speed", 1.0) * rate)
        chunks.append(b"\0" * (n * width))
        continue
    av = float(s.get("av_offset", edl.get("av_offset", 0.0)))   # the voice plays from (in - av_offset) (lip-sync shift)
    a, b = round((s["in"] - av) * rate), round((s["out"] - av) * rate)
    w.setpos(min(a, w.getnframes()))
    chunks.append(w.readframes(max(0, b - a)))

with wave.open(out, "wb") as o:
    o.setparams(params)
    for c in chunks:
        o.writeframes(c)
print("stitched", out)
