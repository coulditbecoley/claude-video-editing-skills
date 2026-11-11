"""QA for headless Shorts (render_shorts.py specs sN.json -> out/Short N - <title>.mp4). Replaces qa_round.py.

    python shorts_qa.py --lint [N ...]   # preflight: spec + lint only (before rendering)
    python shorts_qa.py [N ...]          # final acceptance: lint + the rendered file (a missing final FAILs)
    python shorts_qa.py --self-test
Run in <edit>/shorts/. Default N: every sN.json.

Lint (both modes): the long-form lint_edl rules through an explicit adapter (cut inside a word FAILs; quiet-run and
end-hold WARNs), spec timing (one offset per segment starting at 0, each within a frame of the cumulative piece
lengths render_shorts uses, segments summing to the spec total), captions / images / rings inside the timeline,
caption overlaps, Shorts graphic floors (FAIL < 0.5 s, WARN < 1.0 s; long-form floors don't apply), caption dwell
(WARN < 0.3 s). Transcript: ../main.wav.words.json (the pass gen_shorts cuts from), else ../main.wav.literal.json.
Final (default mode): the exact file render_shorts writes for the spec's title (other "Short N - *.mp4" files are
reported as stale), then the shared long-form contract (qa_lib.final_items: exact frames, 1080x1920 at 60 fps,
AAC 48 kHz, duration, -14 LUFS / <= -1 dBTP; failed measurements FAIL), clicks on out/sN_voice.wav with explicit
NOT CHECKED coverage, and a 10-frame contact sheet row (blank cells reported).
Writes probe/qa_sheet.jpg + probe/qa_report.json (with spec and final identities); exit 1 on any FAIL.
"""
import glob, hashlib, json, math, os, sys

LF = os.environ.get("LF_SCRIPTS", r"%USERPROFILE%\.claude\skills\edit-longform\scripts")
sys.path.insert(0, LF)
import qa_lib, lint_edl  # noqa: E402

HERE = os.getcwd()
SHORT_FLOORS = {"read": (0.5, 1.0), "card": (0.5, 1.0), "diagram": (0.5, 1.0), "accent": (0.3, 0.3), "cover": (0.0, 0.0)}
CAPTION_MIN = 0.3


def final_name(spec, n):
    """Exactly what render_shorts.render() writes."""
    safe = "".join(c for c in spec["title"] if c not in '\\/:*?"<>|')
    return os.path.join(HERE, "out", f"Short {n} - {safe.rstrip('.')}.mp4")


def to_edl(spec):
    """Shorts spec -> the long-form EDL shape lint_edl reads. Explicit on purpose: segments keep in/out/speed/mute
    (voice = spec['voice'] on the source timeline), images and sfx carry over, no music (the bed is ducked inside
    render_shorts). Transitions are drawn on cuts but not listed per segment, so transition clearance isn't applied."""
    segs = [{"in": s["in"], "out": s["out"], "speed": s.get("speed", 1.0), "mute": bool(s.get("mute"))}
            for s in spec["segments"]]
    return {"segments": segs, "images": spec.get("images", []), "sfx": spec.get("sfx", []), "music": [],
            "voice": {spec["source"]: spec["voice"]}}


def spec_issues(spec, total):
    """Timing the renderer actually uses (audit r3 #6): offsets and in-timeline captions/images/rings."""
    out = []
    fps = spec.get("fps", 60)
    offs, segs = spec.get("offsets", []), spec["segments"]
    if len(offs) != len(segs):
        out.append({"level": "FAIL", "t": 0, "msg": f"{len(offs)} offsets for {len(segs)} segments"})
    else:
        cum = 0.0
        for i, (o, sg) in enumerate(zip(offs, segs)):
            if not (isinstance(o, (int, float)) and math.isfinite(o)) or abs(o - cum) > 1.0 / fps:
                out.append({"level": "FAIL", "t": cum, "msg": f"offset {i} is {o}, the pieces before it add up to {cum:.3f}s"})
                break
            cum += (sg["out"] - sg["in"]) / float(sg.get("speed", 1.0))
    if abs(total - float(spec["total"])) > 0.02:
        out.append({"level": "FAIL", "t": 0, "msg": f"segments sum to {total:.3f}s but spec total is {spec['total']}"})
    T = float(spec["total"])
    for kind in ("captions", "images", "rings"):
        for n, x in enumerate(spec.get(kind, [])):
            a = float(x.get("start", 0))
            b = float(x["end"]) if "end" in x else a + float(x.get("duration", 0))
            if a < -1e-3 or b > T + 1e-3 or b < a:
                out.append({"level": "FAIL", "t": a, "msg": f"{kind}[{n}] {a:.2f}-{b:.2f}s is outside the 0-{T:.2f}s timeline"})
    caps = sorted(spec.get("captions", []), key=lambda c: float(c["start"]))
    for c1, c2 in zip(caps, caps[1:]):
        if float(c2["start"]) < float(c1["end"]) - 1e-3:
            out.append({"level": "WARN", "t": float(c2["start"]),
                        "msg": f"captions overlap: '{' '.join(c1['text'])}' and '{' '.join(c2['text'])}'"})
    for c in caps:
        d = float(c["end"]) - float(c["start"])
        if d < CAPTION_MIN:
            out.append({"level": "WARN", "t": round(float(c["start"]), 3),
                        "msg": f"caption '{' '.join(c['text'])}' shows {d:.2f}s (< {CAPTION_MIN}s)"})
    return out


def lint_short(spec, words):
    E = to_edl(spec)
    old = dict(qa_lib.FLOORS)
    qa_lib.FLOORS.update(SHORT_FLOORS)
    try:
        iss, total = lint_edl.lint(E, None if os.environ.get("QA_NO_VOICE") else spec["voice"], words)
    finally:
        qa_lib.FLOORS.clear()
        qa_lib.FLOORS.update(old)
    if not any(x["level"] == "FAIL" and x["msg"].startswith("segment") for x in iss):
        iss += spec_issues(spec, total)
    return iss


def check_final(spec, n, probe_fn=None, loud_fn=None, grab_fn=None):
    """(items, sheet row or None, identity or None)."""
    f = final_name(spec, n)
    stale = [g for g in glob.glob(os.path.join(HERE, "out", f"Short {n} - *.mp4")) if os.path.abspath(g) != os.path.abspath(f)]
    items = [{"level": "WARN", "t": None, "msg": f"stale/ambiguous final ignored: {os.path.basename(g)}"} for g in stale]
    if not os.path.exists(f):
        return items + [{"level": "FAIL", "t": None, "msg": f"final not found: {os.path.basename(f)}"}], None, None
    fps = spec.get("fps", 60)
    nf = round(float(spec["total"]) * fps)
    fi, pr, loud = qa_lib.final_items(f, nf, spec.get("size", [1080, 1920]), fps, float(spec["total"]),
                                      probe_fn=probe_fn, loud_fn=loud_fn)
    items += [{"level": x["level"], "t": x["t"], "msg": f"{x['check']}: {x['msg']}"} for x in fi]
    if pr is None:                                   # unreadable final: report it, measure nothing else (audit r4 #4)
        return items, None, {"path": f, "size": os.path.getsize(f), "mtime_ns": os.stat(f).st_mtime_ns}
    spec_path = os.path.join(HERE, f"s{n}.json")
    ci, _ = qa_lib.click_items(os.path.join(HERE, "out", f"s{n}_voice.wav"), [float(t) for t in spec.get("offsets", [])[1:]],
                               newer_than=spec_path if os.path.exists(spec_path) else None, total=float(spec["total"]))
    items += [{"level": x["level"], "t": x["t"], "msg": x["msg"]} for x in ci]
    grab = grab_fn or qa_lib.grab
    d = pr["duration"]
    row = [grab(f, 0.0 if c == 0 else 0.5 + c * (d - 0.9) / 9, w=180) for c in range(10)]
    items += [{"level": x["level"], "t": None, "msg": x["msg"]} for x in qa_lib.stills_item(row)]
    ident = {"path": f, "size": os.path.getsize(f), "mtime_ns": os.stat(f).st_mtime_ns}
    label = f"Short {n}: {pr['frames']}/{nf} fr" + (f", {loud[0]:.1f} LUFS {loud[1]:.1f} dBTP" if loud else "")
    return items, (label, row), ident


def _check():
    global HERE
    import tempfile
    os.environ["QA_NO_VOICE"] = "1"
    spec = {"title": "T.", "segments": [{"in": 0.0, "out": 1.0}, {"in": 1.5, "out": 2.0, "mute": True}], "total": 1.5,
            "offsets": [0.0, 1.0], "source": "s", "voice": "missing.wav", "fps": 60,
            "images": [{"path": "card-x.png", "start": 0, "duration": 0.7}],
            "captions": [{"text": ["HI"], "start": 0.0, "end": 0.2}, {"text": ["YO"], "start": 0.1, "end": 0.6}], "sfx": []}
    iss = lint_short(spec, None)
    lv = sorted((x["level"], x["msg"].split(":")[0].split(" ")[0]) for x in iss)
    assert ("WARN", "card-x.png") in lv and any("shows 0.20s" in x["msg"] for x in iss), lv
    assert any("captions overlap" in x["msg"] for x in iss), iss
    assert any(x["level"] == "FAIL" and "missing" in x["msg"] for x in iss), lv
    assert qa_lib.FLOORS["card"] == (1.5, 5.0), "Shorts floors leaked into long-form"
    # audit r3 #6: offsets that don't match the pieces, items past the end, wrong total
    assert any("offset 1 is 99" in x["msg"] for x in lint_short(dict(spec, offsets=[0.0, 99]), None))
    assert any("offsets for" in x["msg"] for x in lint_short(dict(spec, offsets=[0.0]), None))
    assert any("outside the" in x["msg"] for x in lint_short(dict(spec, captions=[{"text": ["X"], "start": 1.2, "end": 3.0}]), None))
    assert any("spec total" in x["msg"] for x in lint_short(dict(spec, total=9.0), None))
    # audit r3 #5: final mode - missing final FAILs; wrong rate FAILs; failed loudness FAILs; blank stills reported;
    # a stale other-title final is reported, not inspected
    HERE = tempfile.mkdtemp()
    os.makedirs(os.path.join(HERE, "out"))
    it, row, _ = check_final(spec, 1)
    assert any(x["level"] == "FAIL" and "final not found" in x["msg"] for x in it), it
    open(final_name(spec, 1), "wb").write(b"x")
    open(os.path.join(HERE, "out", "Short 1 - Old Title.mp4"), "wb").write(b"x")
    fake = {"frames": 90, "width": 1080, "height": 1920, "fps": 60.0, "duration": 1.5, "acodec": "aac", "asr": 44100}

    def bad_loud(p):
        raise RuntimeError("decode failed")
    it, row, _ = check_final(spec, 1, probe_fn=lambda p: fake, loud_fn=bad_loud, grab_fn=lambda *a, **k: None)
    msgs = [(x["level"], x["msg"]) for x in it]
    for want in ("audio:", "loudness: NOT MEASURED", "review stills failed", "stale/ambiguous", "NOT CHECKED"):
        assert any(want in m for _, m in msgs), (want, msgs)
    assert sum(lvl == "FAIL" for lvl, _ in msgs) == 2, msgs
    # audit r4 #4: a corrupt final is a structured FAIL, nothing else is measured
    it, row, _ = check_final(spec, 1)
    assert row is None and any("unreadable" in x["msg"] and x["level"] == "FAIL" for x in it), it
    # audit r5 #4: a malformed first spec doesn't stop the batch, and the report is replaced
    open(os.path.join(HERE, "s1.json"), "w").write("{")
    json.dump(spec, open(os.path.join(HERE, "s2.json"), "w"))
    os.makedirs(os.path.join(HERE, "probe"), exist_ok=True)
    open(os.path.join(HERE, "probe", "qa_report.json"), "w").write('{"sentinel": 1}')
    assert run([1, 2], True) == 1
    rep_ = json.load(open(os.path.join(HERE, "probe", "qa_report.json")))
    assert "sentinel" not in rep_ and "could not process" in rep_["shorts"]["1"]["items"][0]["msg"], rep_
    assert rep_["shorts"]["2"]["spec_sha256"], rep_
    print("shorts_qa self-test OK")


VERBOSE = "-v" in sys.argv


def run(ns, lint_only):
    """The batch. Every Short is read, parsed, hashed and checked inside its own boundary (audit r5 #4), and a shared
    input failure still publishes a failed report, so probe/qa_report.json always describes THIS run."""
    os.makedirs(os.path.join(HERE, "probe"), exist_ok=True)
    rp = os.path.join(HERE, "probe", "qa_report.json")
    rows, report, nfail = [], {"mode": "lint" if lint_only else "final", "shorts": {}}, 0
    try:
        wp = next((os.path.join(HERE, "..", f) for f in ("main.wav.words.json", "main.wav.literal.json")
                   if os.path.exists(os.path.join(HERE, "..", f))), None)
        words = lint_edl.load_words(wp) if wp else None
        report["words"] = wp
    except Exception as e:
        report["batch_error"] = f"transcript unreadable ({type(e).__name__}: {e})"
        json.dump(report, open(rp + ".next", "w"), indent=1)
        os.replace(rp + ".next", rp)
        print("FAIL  " + report["batch_error"])
        return 1
    print(f"words: {wp or 'none (word checks NOT CHECKED)'}; mode: {'preflight lint' if lint_only else 'final acceptance'}")
    for n in ns:
        sp = os.path.join(HERE, f"s{n}.json")
        ident, spec_sha = None, None
        try:
            raw = open(sp, "rb").read()
            spec_sha = hashlib.sha256(raw).hexdigest()
            spec = json.loads(raw.decode("utf-8"))
            iss = lint_short(spec, words)
            if not lint_only:
                fin, row, ident = check_final(spec, n)
                iss += fin
                if row:
                    rows.append(row)
        except Exception as e:                       # one broken Short never loses the rest of the batch
            iss = [{"level": "FAIL", "t": None, "msg": f"QA could not process s{n}.json ({type(e).__name__}: {e})"}]
        report["shorts"][n] = {"spec_sha256": spec_sha, "final": ident, "items": iss}
        f = sum(x["level"] == "FAIL" for x in iss)
        nfail += f
        print(f"Short {n}: {f} FAIL, {len(iss) - f} WARN")
        qa_lib.print_items(iss, VERBOSE, indent="   ")
    if rows:
        qa_lib.sheet(rows, os.path.join(HERE, "probe", "qa_sheet.jpg"))
    json.dump(report, open(rp + ".next", "w"), indent=1)
    os.replace(rp + ".next", rp)
    print(f"SHORTS QA: {len(ns)} Shorts, {nfail} FAIL -> probe/qa_report.json")
    return 1 if nfail else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _check()
        sys.exit(0)
    lint_only = "--lint" in sys.argv
    ns = [int(a) for a in sys.argv[1:] if a.isdigit()] or sorted(
        int(os.path.basename(p)[1:-5]) for p in glob.glob(os.path.join(HERE, "s*.json")) if os.path.basename(p)[1:-5].isdigit())
    sys.exit(run(ns, lint_only))
