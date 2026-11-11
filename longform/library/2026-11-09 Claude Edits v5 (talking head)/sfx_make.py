"""Generate the v5 SFX kit with the ElevenLabs sound-effects API (Coley asked for real ElevenLabs sounds, 2026-11-09).
Key: env ELEVENLABS_API_KEY, or a line ELEVENLABS_API_KEY=... in ~/.secrets/elevenlabs.env. Never printed.
  python sfx_make.py balance          # free read: credits left
  python sfx_make.py make [name ...]  # generate missing sounds (or the named ones) into audio/sfx/<name>.mp3 + .wav
Each sound is generated ONCE (skipped if the file exists) so credits are not spent twice. Prompts are the provenance:
sfx/kit.json records prompt, duration and the response's character-cost header for every file.
"""
import json, os, subprocess, sys, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "sfx")
# one job per sound; all short, dry, modern UI / motion-design sounds, no music, no voices
KIT = {
    "whoosh_in":  (0.8, "Soft airy cinematic whoosh, smooth and clean, medium-fast pass from left to right, no impact, subtle, high quality motion graphics transition"),
    "whoosh_out": (0.6, "Very short soft reverse whoosh, gentle air suck-back, clean and subtle, motion graphics transition out"),
    "swell":      (1.6, "Deep smooth cinematic sub swell with soft airy shimmer rising then settling, elegant, for a 3D camera move in a tech explainer, no impact"),
    "tick":       (0.5, "Single soft glassy UI tick, tiny high-quality interface click, dry, subtle"),
    "light":      (0.7, "Soft warm shimmer chime as a button lights up, gentle glass sparkle, short, elegant, subtle"),
    "pop":        (0.5, "Single soft rounded bubble pop for a UI chip appearing, muted, pleasant, dry, very short"),
    "count":      (1.1, "Fast soft digital counter ticking upward in pitch, light rapid clicks rising for one second then one soft landing click"),
    "type":       (1.6, "Soft mechanical keyboard typing a short sentence, quiet, close, dry, natural rhythm"),
    "draw":       (1.0, "Smooth soft synth glide rising gently like a line being drawn on a chart, airy, clean, subtle"),
    "strike":     (0.5, "Quick pen strike-through swipe with a soft low thud at the end, dry, short"),
    "wrong":      (0.6, "Soft low muted error tone, two gentle descending notes, not harsh, short, modern interface"),
    "right":      (0.7, "Gentle bright confirmation chime, two soft ascending notes, clean modern interface, short"),
    "impact":     (1.2, "Deep soft cinematic boom with a short tail, round sub hit, not aggressive, for a big number landing on screen"),
    "riser":      (2.0, "Smooth airy riser building tension for two seconds, clean, no impact at the end, modern trailer style but subtle"),
    "slide":      (0.5, "Short soft swish of a card sliding in, light paper-like air movement, dry, subtle"),
    "scan":       (1.2, "Soft electronic scanner sweep, gentle rising hum passing by, clean sci-fi interface, subtle"),
}


def key():
    k = os.environ.get("ELEVENLABS_API_KEY")
    if not k:
        p = os.path.expanduser("~/.secrets/elevenlabs.env")
        if os.path.exists(p):
            for line in open(p, encoding="utf-8"):
                if line.strip().startswith("ELEVENLABS_API_KEY="):
                    k = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not k:
        sys.exit("no ElevenLabs key: set ELEVENLABS_API_KEY or put it in ~/.secrets/elevenlabs.env")
    return k


def call(path, body=None):
    req = urllib.request.Request("https://api.elevenlabs.io" + path, headers={"xi-api-key": key(), "Content-Type": "application/json"},
                                 data=json.dumps(body).encode() if body is not None else None)
    r = urllib.request.urlopen(req, timeout=120)
    return r.read(), dict(r.headers)


def balance():
    try:
        d = json.loads(call("/v1/user/subscription")[0])
    except urllib.error.HTTPError as e:      # a restricted key without user_read: the balance can't be read
        print("balance not readable with this key (no user_read permission); costs are logged per sound in kit.json"); return 0
    left = d["character_limit"] - d["character_count"]
    print(f"tier {d.get('tier')}: {left} credits left of {d['character_limit']}")
    return left


def make(names):
    os.makedirs(OUT, exist_ok=True)
    kit_path = os.path.join(OUT, "kit.json")
    kit = json.load(open(kit_path)) if os.path.exists(kit_path) else {}
    start = balance()
    for n in names or KIT:
        dur, prompt = KIT[n]
        mp3, wav = os.path.join(OUT, n + ".mp3"), os.path.join(OUT, n + ".wav")
        if os.path.exists(wav):
            print("have", n); continue
        data, hdr = call("/v1/sound-generation?output_format=mp3_44100_192", {"text": prompt, "duration_seconds": dur, "prompt_influence": 0.45})
        open(mp3, "wb").write(data)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", wav], check=True)
        kit[n] = {"prompt": prompt, "duration_seconds": dur, "source": "ElevenLabs sound-generation API", "made": __import__("time").strftime("%Y-%m-%d"),
                  "cost": hdr.get("character-cost") or hdr.get("Character-Cost")}
        json.dump(kit, open(kit_path, "w"), indent=1)
        print("made", n, "cost", kit[n]["cost"])
    print("spent", start - balance())


if __name__ == "__main__":
    {"balance": lambda: balance(), "make": lambda: make(sys.argv[2:])}[sys.argv[1] if len(sys.argv) > 1 else "balance"]()
