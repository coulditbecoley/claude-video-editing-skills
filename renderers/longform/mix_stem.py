"""Pre-mix the music cues of edit.edl.json into one stem that ducks under his voice -> audio/music-stem.wav.
The beds play at their gap level (music_plan.py targets) and a sidechain compressor keyed by the stitched voice
(qa_voice.wav, which matches the timeline sample for sample) pulls them ~5 dB down under speech, so the music sits
~20 dB under the voice while he talks and swells back in the pauses and through the transitions.
gen_edl.py swaps its cues for this stem when the stem matches the timeline length (MUSIC_STEM=0 to skip).
usage: python mix_stem.py   (after gen_edl.py and verify_voice.py)"""
import json, subprocess
from pathlib import Path
E = json.loads(Path("edit.edl.json").read_text(encoding="utf-8"))
cues = json.loads(Path("audio/music-cues.json").read_text(encoding="utf-8"))   # written by gen_edl.py (the plan, pre-stem)
total = sum((s["out"] - s["in"]) / s.get("speed", 1.0) for s in E["segments"])
_qv = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "qa_voice.wav"],
                           capture_output=True, text=True).stdout)
# 2026-11-03 (Codex audit #4): a qa_voice from an older EDL ducked the music 3.55 s off. Refuse a stale sidechain key.
assert abs(_qv - total) < 0.01, f"qa_voice.wav is {_qv:.3f} s but the EDL is {total:.3f} s: regenerate it from the current EDL first"
args, chains = ["ffmpeg", "-v", "error", "-y"], []
for i, c in enumerate(cues):
    args += ["-i", c["path"]]
    d, fi, fo, at = c["duration"], c.get("fade_in", 0.0), c.get("fade_out", 0.0), c["at"]
    f = f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start={c['start_offset']}:duration={d},asetpts=PTS-STARTPTS"
    if fi: f += f",afade=t=in:d={fi}"
    if fo: f += f",afade=t=out:st={max(0.0, d - fo)}:d={fo}"
    f += f",volume={c['volume']},adelay={round(at * 1000)}:all=1[m{i}]"
    chains.append(f)
n = len(cues)
args += ["-i", "qa_voice.wav"]
chains.append("".join(f"[m{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0:dropout_transition=0,apad,atrim=duration={total:.3f}[mus]")
chains.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=duration={total:.3f}[key]")
# ~6 dB of gain reduction at his speech level (about -14 dBFS RMS against a -26 dB threshold, ratio 2.2); 40 ms attack so a
# word's onset is already ducked, 450 ms release so the 0.24 s collapsed pauses don't pump and longer gaps swell
chains.append("[mus][key]sidechaincompress=threshold=0.05:ratio=2.2:attack=40:release=450:makeup=1:knee=4[out]")
chains[-1] = chains[-1].replace("[out]", "[o0]"); chains.append(f"[o0]apad=whole_dur={total:.3f},atrim=duration={total:.3f}[out]")
args += ["-filter_complex", ";".join(chains), "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000", "audio/music-stem.wav"]
subprocess.run(args, check=True)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "audio/music-stem.wav"],
                           capture_output=True, text=True).stdout)
Path("audio/music-stem.json").write_text(json.dumps({"total": round(total, 3), "duration": dur, "cues": len(cues)}), encoding="utf-8")
print(f"music-stem.wav {dur:.2f}s (timeline {total:.2f}s) from {n} cues")
