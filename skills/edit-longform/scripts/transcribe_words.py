"""Word-level transcription for long-form edits (faster-whisper, CPU).

usage (run from your capcut-cli checkout so faster-whisper is on the path):
  uv run python <skill>/scripts/transcribe_words.py [--literal] [--prompt "Names, Brands"] file1.mp4 [file2 ...]

Writes <file>.words.json (default) or <file>.literal.json (--literal) next to each input:
  {"file", "duration", "segments": [{"start","end","text","words":[{"w","s","e","p"}]}]}

--literal sets condition_on_previous_text=False. Whisper's default smooths over
flubs, so a false start ("They launch, they have the ability...") disappears from
the text while staying in the audio. Run the literal pass before deciding cuts,
and always for the verify pass.
--prompt primes spelling of product and people names (Paperclip, Claude Code, Codex...).
"""
import argparse
import json

from faster_whisper import WhisperModel

ap = argparse.ArgumentParser()
ap.add_argument("files", nargs="+")
ap.add_argument("--literal", action="store_true")
ap.add_argument("--prompt", default="")
ap.add_argument("--model", default="small")
a = ap.parse_args()

m = WhisperModel(a.model, device="cpu", compute_type="int8")
for f in a.files:
    kw = {"condition_on_previous_text": False} if a.literal else {}
    segs, info = m.transcribe(f, word_timestamps=True, vad_filter=False,
                              initial_prompt=a.prompt or None, **kw)
    out = [{"start": s.start, "end": s.end, "text": s.text.strip(),
            "words": [{"w": w.word, "s": w.start, "e": w.end, "p": round(w.probability, 2)} for w in s.words]}
           for s in segs]
    path = f + (".literal.json" if a.literal else ".words.json")
    json.dump({"file": f, "duration": info.duration, "segments": out}, open(path, "w", encoding="utf-8"), indent=1)
    print("done", path, len(out), flush=True)
