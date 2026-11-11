"""Word-level transcription for edits (faster-whisper). One cached entry point for CPU and GPU (audit r6 #1).

  GPU (default for real edits; run with a Python that has faster-whisper + nvidia-cublas-cu12 + nvidia-cudnn-cu12==9.*,
  e.g. the gpuw venv):   python <skill>/scripts/transcribe_words.py --gpu [--literal] [--prompt "Names, Brands"] <files>
  CPU fallback (from %USERPROFILE%\\Code\\capcut-cli):  uv run python <skill>/scripts/transcribe_words.py <files>

Writes <file>.words.json (default) or <file>.literal.json (--literal) next to each input:
  {"file", "key", "duration", "segments": [{"start","end","text","words":[{"w","s","e","p"}]}]}

--literal sets condition_on_previous_text=False: Whisper's default smooths over flubs, so a false start disappears
from the text while staying in the audio. Run the literal pass before deciding cuts, and always for verify.
--prompt primes spelling of product and people names. --gpu = CUDA float16, model medium.en unless --model is given
(the Day 35 recipe). Files longer than 15 min are transcribed in ~600 s chunks cut at a silence near each boundary
(a 37-min take ran the single pass out of memory), with word times offset back to the full file.
Cache (video-use rule 9): the output stores a key (version, source size + mtime_ns, mode, model, device, compute,
prompt hash); an unchanged input with the same settings is skipped without loading a model. --force re-runs.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

ap = argparse.ArgumentParser()
ap.add_argument("files", nargs="+")
ap.add_argument("--literal", action="store_true")
ap.add_argument("--prompt", default="")
ap.add_argument("--gpu", action="store_true")
ap.add_argument("--model")
ap.add_argument("--force", action="store_true")
a = ap.parse_args()
DEVICE, COMPUTE = ("cuda", "float16") if a.gpu else ("cpu", "int8")
MODEL = a.model or ("medium.en" if a.gpu else "small")
CHUNK, LONG = 600.0, 900.0


def key(f):
    st = os.stat(f)
    return {"v": 3, "size": st.st_size, "mtime_ns": st.st_mtime_ns, "literal": a.literal, "model": MODEL,
            "device": DEVICE, "compute": COMPUTE, "prompt": hashlib.sha256(a.prompt.encode()).hexdigest()[:12]}


def duration(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True, check=True).stdout)


def bounds(f, dur):
    """Chunk edges near every CHUNK seconds, moved to the middle of a nearby silence."""
    if dur <= LONG:
        return [0.0, dur]
    log = subprocess.run(["ffmpeg", "-i", f, "-af", "silencedetect=n=-40dB:d=0.4", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    mids = [(float(s) + float(e)) / 2 for s, e in zip(re.findall(r"silence_start: ([0-9.]+)", log),
                                                       re.findall(r"silence_end: ([0-9.]+)", log))]
    out, t = [0.0], CHUNK
    while t < dur - 60:
        near = min(mids, key=lambda m: abs(m - t)) if mids else t
        out.append(near if abs(near - t) < 60 else t)
        t = out[-1] + CHUNK
    return out + [dur]


def load_model():
    if a.gpu and os.name == "nt":   # Windows: pip CUDA DLLs onto the path (was gpuw_boot.py); Linux uses LD_LIBRARY_PATH
        for d in glob.glob(os.path.join(sys.prefix, "Lib", "site-packages", "nvidia", "*", "bin")):
            os.add_dll_directory(d)
            os.environ["PATH"] = d + os.pathsep + os.environ["PATH"]
    from faster_whisper import WhisperModel
    return WhisperModel(MODEL, device=DEVICE, compute_type=COMPUTE)


m = None
for f in a.files:
    path = f + (".literal.json" if a.literal else ".words.json")
    k = key(f)
    if not a.force and os.path.exists(path):
        try:
            if json.load(open(path, encoding="utf-8")).get("key") == k:
                print("cached", path, flush=True)
                continue
        except ValueError:
            pass
    m = m or load_model()
    kw = {"condition_on_previous_text": False} if a.literal else {}
    dur = duration(f)
    out = []
    with tempfile.TemporaryDirectory() as td:
        edges = bounds(f, dur)
        for c0, c1 in zip(edges, edges[1:]):
            src = f
            if len(edges) > 2:
                src = os.path.join(td, "c.wav")
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(c0), "-to", str(c1), "-i", f, "-ar", "16000",
                                "-ac", "1", src], check=True)
            else:
                c0 = 0.0
            segs, _ = m.transcribe(src, word_timestamps=True, vad_filter=False, initial_prompt=a.prompt or None, **kw)
            out += [{"start": s.start + c0, "end": s.end + c0, "text": s.text.strip(),
                     "words": [{"w": w.word, "s": w.start + c0, "e": w.end + c0, "p": round(w.probability, 2)}
                               for w in s.words]} for s in segs]
            if len(edges) > 2:
                print(f"chunk {c0:.0f}-{c1:.0f} done", flush=True)
    tmp = path + ".next"
    json.dump({"file": f, "key": k, "duration": dur, "segments": out}, open(tmp, "w", encoding="utf-8"), indent=1)
    os.replace(tmp, path)
    print("done", path, len(out), flush=True)
