"""End-to-end test of the headless path on a tiny synthetic edit (640x360, ~8 s, 5 pieces, 3 graphics).

    python run_fixture.py [--keep]

Builds a source clip + voice WAV + transcript + EDL + card PNGs + a 3-frame PNG sequence in a temp folder, copies
render_mp4.py into <tmp>/nocapcut/, and asserts:
  1  clean render (video --workers 3, audio, mux) passes check with 0 FAIL, exact frames, word checks active,
     output_evidence ran (graphics are kind "accent": 1.5 s cards in a 10 s fixture)
  2  a click injected into out/voice.wav FAILs check
  3  a final one frame short FAILs check; 3b a mix 70 ms short still muxes every frame
  4  a missing final FAILs check
  5  lint FAILs a cut inside a word; 5b a missing sequence frame: lint FAILs and `video` refuses
  T2a card moved chunk 0 -> chunk 2: --changed rebuilds exactly those two, chunk 1's file is untouched, and the
      picture matches a fresh full render at the old and new card spots
  T2b an OLDER sequence frame edited (same count): its chunk rebuilds
  T2c two overlapping cards swap stacking order: their chunk rebuilds
  T2d nothing changed but picture.mp4 deleted: re-concat, not a silent exit
  T2e speed-only change: full-render fallback;  T2f a part deleted: full fallback;  T2g render.lock: refuses
  T2h-l injected crashes (encode, concat, commit, between commit and picture swap, failed full render): the previous
      generation stays intact or the committed one is re-materialised; the lock is released
  M1  mux refuses a mix made from an older EDL (or edited by hand); check FAILs a final muxed from an older EDL
  M2  crash between commit and picture swap, then mux: the committed picture is muxed and recorded in final.json
  M3  the EDL saved on disk mid-render: the commit is refused and the previous generation stays intact
  R1  a graphic replaced at its path (no EDL edit): check FAILs, mux refuses until `video --changed`
  R2  the voice WAV replaced at its path: check FAILs, mux refuses until `audio`
  R3  a truncated out/final.json: structured provenance FAIL, report replaced
  R5  the EDL saved after concat, just before commit: refused, previous generation intact
  R6  a missing final: a FAIL report replaces the previous (passing) one
  V1  a per-segment src piece shows the other recording and is never a camera piece; a video-backed sequence
      (<dir>.mp4, no PNGs) shows the right frame; lint passes it, and FAILs / video refuses once the mp4 is gone
Needs the NVIDIA GPU (NVENC), like the real renderer. The temp folder is kept when anything fails.
"""
import json, os, shutil, subprocess, sys, tempfile, time

SK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")
W, H, FPS, SR = 640, 360, 60, 48000
TIMEOUT = 600


def run(cmd, cwd, ok=(0,)):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT)
    if r.returncode not in ok:
        raise AssertionError(f"{cmd} -> {r.returncode}\n{r.stdout[-3000:]}\n{r.stderr[-3000:]}")
    return r


def has_fail(out, key):
    """True when compact QA output has a FAIL line for this check (format: 'FAIL  <time>  <check>: <msg>')."""
    return any(l.startswith("FAIL") and f"{key}:" in l for l in out.splitlines())


def card(path, text, color):
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (220, 120), color)
    ImageDraw.Draw(im).text((20, 40), text, fill=(255, 255, 255, 255))
    im.save(path)


def build(d):
    src = os.path.join(d, "src.mp4")
    # 10 s source: test pattern + a 440 Hz "voice", silent in the cut gaps
    gaps = [(1.8, 2.4), (3.8, 4.4), (5.8, 6.0), (7.5, 7.8)]
    on = "*".join(f"(1-between(t,{a},{b}))" for a, b in gaps)
    run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=size={W}x{H}:rate={FPS}:duration=10",
         "-f", "lavfi", "-i", f"aevalsrc='0.3*sin(2*PI*440*t)*{on}':s={SR}:d=10", "-c:v", "libx264", "-g", "60",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", src], d)
    voice = os.path.join(d, "voice.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "2", "-ar", str(SR), "-c:a", "pcm_s16le", voice], d)
    words = {"segments": [{"words": [{"w": w, "s": a, "e": b} for w, a, b in
                                     (("one", 0.25, 1.8), ("two", 2.4, 3.8), ("three", 4.4, 5.8), ("four", 6.0, 7.5),
                                      ("five", 7.8, 9.0))]}]}
    json.dump(words, open(os.path.join(d, "main.wav.words.json"), "w"))
    g = os.path.join(d, "graphics")
    os.makedirs(os.path.join(g, "seq-c"))
    card(os.path.join(g, "card-a.png"), "CARD A", (200, 40, 40, 230))
    card(os.path.join(g, "card-b.png"), "CARD B", (40, 40, 200, 230))
    for k, c in enumerate(((0, 160, 0, 230), (0, 200, 0, 230), (0, 240, 0, 230))):
        card(os.path.join(g, "seq-c", f"{k:03d}.png"), f"SEQ {k}", c)
    E = {"project": "fixture", "output": "fixture.mp4", "source": src, "resolution": [W, H], "fps": FPS,
         "voice": {src: voice}, "cam_rect": [480, 240, 620, 350],
         "segments": [{"in": 0.2, "out": 2.0, "kind": "talk"},
                      {"in": 2.2, "out": 4.0, "kind": "screen", "transition": {"name": "Dissolve", "duration": 0.3}},
                      {"in": 4.2, "out": 5.9, "kind": "screen"},
                      {"in": 5.9, "out": 7.6, "kind": "screen"},
                      {"in": 7.7, "out": 9.6, "kind": "talk"}],
         # chunks come out [0, 1.8) [1.8, 5.3) [5.3, end): each graphic sits inside one chunk (plus transition pad)
         "images": [{"path": os.path.join(g, "card-a.png"), "start": 0.1, "duration": 1.5, "x": 160, "y": 90, "scale": 1.0, "pop": True, "kind": "accent"},
                    {"path": os.path.join(g, "seq-c", "000.png"), "start": 2.4, "duration": 1.6, "x": 320, "y": 200,
                     "scale": 1.0, "pop": False, "seq": {"dir": os.path.join(g, "seq-c"), "frames": 3}, "kind": "accent"},
                    {"path": os.path.join(g, "card-b.png"), "start": 6.6, "duration": 1.6, "x": 480, "y": 90, "scale": 1.0, "pop": True, "kind": "accent"}],
         "sfx": [], "music": []}
    json.dump(E, open(os.path.join(d, "edit.edl.json"), "w"), indent=1)
    json.dump([[0.0, 2.1], [7.6, 10.0]], open(os.path.join(d, "th_ranges.json"), "w"))
    nc = os.path.join(d, "nocapcut")
    os.makedirs(nc)
    shutil.copy(os.path.join(SK, "render_mp4.py"), nc)
    return E, nc


def frame(path, t):
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.4f}", "-i", path, "-frames:v", "1", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.int16)


def save_edl(d, E):
    json.dump(E, open(os.path.join(d, "edit.edl.json"), "w"), indent=1)


def main():
    keep = "--keep" in sys.argv
    d = tempfile.mkdtemp(prefix="hl_fixture_")
    ok = False
    try:
        E, nc = build(d)
        py = sys.executable
        rv = lambda *a, **k: run([py, "render_mp4.py", *a], nc, **k)
        rv("video", "--workers", "3")
        rv("audio")
        rv("mux")
        final = os.path.join(nc, "fixture.mp4")
        man = json.load(open(os.path.join(nc, "out", "chunks.json")))
        assert len(man["chunks"]) == 3, man["chunks"]
        # 1 clean render passes, word checks active
        r = rv("check")
        assert " 0 FAIL" in r.stdout and "NOT CHECKED" not in r.stdout and "EVIDENCE:" in r.stdout, r.stdout
        nf = round((1.8 + 1.8 + 1.7 + 1.7 + 1.9) * FPS)
        rep = json.load(open(os.path.join(nc, "out", "check", "report.json")))
        assert rep["summary"].startswith(f"{nf}/{nf} frames"), rep["summary"]
        assert rep["evidence"]["status"] == "complete" and rep["evidence"]["index_sha256"], rep["evidence"]
        import hashlib
        assert rep["final"]["sha256"] == hashlib.sha256(open(final, "rb").read()).hexdigest()             == rep["evidence"]["identity"]["final"]["sha256"], (rep["final"], rep["evidence"])
        print("1 clean render: PASS", rep["summary"])
        # 1b a check without the picture evidence is a FAIL, so the manifest gate refuses it
        assert has_fail(rv("check", "--no-stills", ok=(1,)).stdout, "evidence")
        rep = json.load(open(os.path.join(nc, "out", "check", "report.json")))
        assert rep["evidence"]["status"] == "skipped", rep["evidence"]
        print("1b check --no-stills: evidence skipped -> FAIL as expected")
        # 1c the whole check has an overall deadline: when it passes, a current FAIL report replaces the old pass
        assert "overall deadline" in rv("check", "--deadline", "1", ok=(1,)).stdout
        rep = json.load(open(os.path.join(nc, "out", "check", "report.json")))
        assert rep["status"] == "incomplete" and rep["items"][0]["level"] == "FAIL" and "deadline" in rep["summary"], rep
        print("1c check --deadline 1: deadline FAIL report as expected")
        # 2 click in the voice stem at the first cut
        import numpy as np
        vp = os.path.join(nc, "out", "voice.wav")
        shutil.copy(vp, vp + ".bak")
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", vp, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                             capture_output=True, check=True).stdout
        a = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
        a[int(round(1.8 * SR)):int(round(1.8 * SR)) + 3] = 0.9
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                        "-c:a", "pcm_s24le", vp], input=a.tobytes(), check=True)
        assert has_fail(rv("check", "--no-stills", ok=(1,)).stdout, "click")
        shutil.move(vp + ".bak", vp)
        print("2 injected click: FAIL as expected")
        # 3 final one frame short; 3b short mix keeps every frame
        short = os.path.join(nc, "short.mp4")
        run(["ffmpeg", "-v", "error", "-y", "-i", final, "-frames:v", str(nf - 1), "-c:v", "libx264", "-c:a", "copy",
             short], nc)
        assert has_fail(rv("check", "--no-stills", "--final", short, ok=(1,)).stdout, "frames")
        print("3 dropped frame: FAIL as expected")
        mp = os.path.join(nc, "out", "mix.wav")
        shutil.copy(mp, mp + ".bak")
        run(["ffmpeg", "-v", "error", "-y", "-i", mp + ".bak", "-t", f"{nf / FPS - 0.07:.3f}", "-c:a", "pcm_s24le", mp], nc)
        assert "was not made from this edit.edl.json" in rv("mux", ok=(1,)).stderr    # a hand-edited mix is refused
        mjp = mp + ".json"
        mj = json.load(open(mjp))
        st = os.stat(mp)
        mj["mix"] = [st.st_size, st.st_mtime_ns]          # bless the short mix to test the frame-length guard only
        json.dump(mj, open(mjp, "w"))
        rv("mux")
        assert not has_fail(rv("check", "--no-stills", ok=(0, 1)).stdout, "frames")
        shutil.move(mp + ".bak", mp)
        rv("audio")
        rv("mux")
        print("3b short mix keeps every frame (and a hand-edited mix is refused): PASS")
        # 4 missing final
        os.rename(final, final + ".gone")
        assert "final not found" in rv("check", ok=(1,)).stdout
        os.rename(final + ".gone", final)
        print("4 missing final: FAIL as expected")
        # 5 lint: a cut inside a word; 5b missing sequence frame
        bad = dict(E, segments=[{"in": 0.2, "out": 2.0}, {"in": 3.0, "out": 4.0}])
        json.dump(bad, open(os.path.join(d, "bad.edl.json"), "w"))
        r = run([py, os.path.join(SK, "lint_edl.py"), os.path.join(d, "bad.edl.json"),
                 "--words", os.path.join(d, "main.wav.words.json")], d, ok=(1,))
        assert "inside 'two'" in r.stdout, r.stdout
        s1 = os.path.join(d, "graphics", "seq-c", "001.png")
        os.rename(s1, s1 + ".gone")
        assert "sequence incomplete" in run([py, os.path.join(SK, "lint_edl.py"), os.path.join(d, "edit.edl.json")], d, ok=(1,)).stdout
        assert "required graphic file(s) missing" in (rv("video", "--changed", ok=(1,)).stderr + rv("still", "1.0", ok=(1,)).stderr)
        os.rename(s1 + ".gone", s1)
        print("5 cut inside a word + missing sequence frame: FAIL / refuse as expected")

        # ---------- T2 ----------
        parts = lambda: {c["k"]: (c["path"], os.path.getmtime(c["path"])) for c in json.load(open(os.path.join(nc, "out", "chunks.json")))["chunks"]}
        before = parts()
        # T2a move card A from chunk 0 to chunk 2 (and keep it clear of card B)
        E["images"][0]["start"] = 8.3
        save_edl(d, E)
        r = rv("video", "--changed")
        assert "-> 2 of 3 chunk(s)" in r.stdout, r.stdout
        after = parts()
        assert after[1] == before[1] and after[0][0] != before[0][0] and after[2][0] != before[2][0], (before, after)
        ref = tempfile.mkdtemp(prefix="hl_ref_")
        shutil.copytree(nc, os.path.join(ref, "nocapcut"), ignore=shutil.ignore_patterns("out"))
        for f in ("edit.edl.json", "th_ranges.json", "main.wav.words.json"):
            shutil.copy(os.path.join(d, f), ref)
        run([py, "render_mp4.py", "video", "--workers", "3"], os.path.join(ref, "nocapcut"))
        pa, pb = os.path.join(nc, "out", "picture.mp4"), os.path.join(ref, "nocapcut", "out", "picture.mp4")
        for t in (1.0, 8.6):           # old card spot (must be clean now), new spot (must show the card)
            diff = float(np.abs(frame(pa, t) - frame(pb, t)).mean())
            assert diff < 1.5, f"partial vs full render differ at {t}s by {diff}"
        shutil.rmtree(ref, ignore_errors=True)
        print("T2a moved card: 2 of 3 chunks rebuilt, pixels match a full render")
        # T2b edit an older sequence frame (000) in place
        card(os.path.join(d, "graphics", "seq-c", "000.png"), "SEQ 0 NEW", (90, 90, 0, 230))
        r = rv("video", "--changed")
        assert "-> 1 of 3 chunk(s)" in r.stdout, r.stdout
        print("T2b older sequence frame edited: its chunk rebuilt")
        # T2c overlapping cards swap stacking order
        E["images"][2]["start"] = 8.4
        save_edl(d, E)
        rv("video", "--changed")
        E["images"][0], E["images"][2] = E["images"][2], E["images"][0]
        save_edl(d, E)
        r = rv("video", "--changed")
        assert "-> 1 of 3 chunk(s)" in r.stdout, r.stdout
        print("T2c stacking order swap: rebuilt")
        # T2h-k failure injection (audit r3 #1): a crash at encode, at the commit point, right after it, or during a
        # full render must leave a usable generation, and the next run recovers
        import hashlib
        outd = os.path.join(nc, "out")

        def snap():
            m = open(os.path.join(outd, "chunks.json"), "rb").read()
            man = json.loads(m)
            parts_h = {c["path"]: hashlib.sha256(open(c["path"], "rb").read()).hexdigest() for c in man["chunks"]}
            st = os.stat(pa)
            return m, parts_h, [st.st_size, st.st_mtime_ns], man

        def fail_run(stage, *args):
            env = dict(os.environ, HL_FAIL_AT=stage)
            r = subprocess.run([py, "render_mp4.py", "video", *args], cwd=nc, capture_output=True, text=True,
                               timeout=TIMEOUT, env=env)
            assert r.returncode != 0 and f"injected failure at {stage}" in (r.stdout + r.stderr), (stage, r.stdout, r.stderr)
            lock = os.path.join(outd, "render.lock")
            assert not os.path.exists(lock), "lock left behind after a failure"

        E["images"][1]["x"] = 300
        save_edl(d, E)
        m0, ph0, pic0, man0 = snap()
        for stage in ("encode", "concat", "commit"):
            fail_run(stage, "--changed")
            m1, ph1, pic1, _ = snap()
            assert m1 == m0 and ph1 == ph0 and pic1 == pic0, f"{stage}: previous generation not preserved"
            assert pic0 == man0["picture"], "picture no longer matches its manifest"
        print("T2h-j crash at encode / concat / commit: previous generation intact")
        fail_run("after_commit", "--changed")
        man1 = json.load(open(os.path.join(outd, "chunks.json")))
        assert man1["gen"] == man0["gen"] + 1 and [os.stat(pa).st_size, os.stat(pa).st_mtime_ns] != man1["picture"]
        r = rv("video", "--changed")
        assert "re-materialised" in r.stdout, r.stdout
        man2 = json.load(open(os.path.join(outd, "chunks.json")))
        assert [os.stat(pa).st_size, os.stat(pa).st_mtime_ns] == man2["picture"] 
        assert all(os.path.exists(c["path"]) for c in man2["chunks"])
        print("T2k crash between commit and picture swap: next run re-materialises the committed picture")
        m0, ph0, pic0, _ = snap()
        E["segments"][3]["speed"] = 1.1
        save_edl(d, E)
        fail_run("encode", "--changed")             # full fallback that crashes
        m1, ph1, pic1, _ = snap()
        assert m1 == m0 and ph1 == ph0 and pic1 == pic0, "failed full render damaged the previous generation"
        E["segments"][3].pop("speed")
        save_edl(d, E)
        print("T2l failed full render: previous generation intact")
        # T2d nothing changed, picture deleted -> re-concat
        os.remove(pa)
        rv("video", "--changed")
        assert os.path.exists(pa)
        print("T2d missing picture with clean cache: re-concatenated")
        # T2e speed-only change -> full
        E["segments"][4]["speed"] = 1.25
        save_edl(d, E)
        assert "full render" in rv("video", "--changed").stdout
        print("T2e speed change: full render")
        # T2f a part deleted -> full
        os.remove(next(iter(parts().values()))[0])
        assert "full render" in rv("video", "--changed").stdout
        print("T2f missing part: full render")
        # T2g lock
        lock = os.path.join(nc, "out", "render.lock")
        open(lock, "w").write("1")
        assert "another render is running" in rv("video", "--changed", ok=(1,)).stderr
        os.remove(lock)
        print("T2g second writer: refused")
        # M: mux / provenance / mid-render EDL edits (audit r4 #1, #2)
        rv("video", "--changed")
        rv("audio")
        rv("mux")
        r = rv("check", "--no-stills", ok=(0, 1))
        assert not has_fail(r.stdout, "provenance") and "provenance NOT CHECKED" not in r.stdout, r.stdout
        E["images"][1]["y"] = 210
        save_edl(d, E)
        assert "was not made from this edit.edl.json" in rv("mux", ok=(1,)).stderr
        assert "muxed from an older edit.edl.json" in rv("check", "--no-stills", ok=(1,)).stdout
        print("M1 stale mix refused at mux; check FAILs a final from an older EDL")
        env = dict(os.environ, HL_FAIL_AT="after_commit")
        r = subprocess.run([py, "render_mp4.py", "video", "--changed"], cwd=nc, capture_output=True, text=True,
                           timeout=TIMEOUT, env=env)
        assert r.returncode != 0, r.stdout
        rv("audio")
        r = rv("mux")
        assert "re-materialised" in r.stdout, r.stdout
        man = json.load(open(os.path.join(outd, "chunks.json")))
        fin = json.load(open(os.path.join(outd, "final.json")))
        assert fin["gen"] == man["gen"] and fin["picture"] == man["picture"] and fin["verified"], (fin, man)
        r = rv("check", "--no-stills", ok=(0, 1))
        assert not has_fail(r.stdout, "provenance"), r.stdout
        print("M2 crash after commit, then mux: the committed picture is muxed and recorded")
        m0, ph0, pic0, _ = snap()
        mut = dict(E, segments=[dict(sg) for sg in E["segments"]])
        mut["segments"][0]["out"] = 1.9
        json.dump(mut, open(os.path.join(d, "mut.edl.json"), "w"), indent=1)
        E["images"][1]["y"] = 220
        save_edl(d, E)
        env = dict(os.environ, HL_TEST_EDL_REPLACE=os.path.join(d, "mut.edl.json"))
        r = subprocess.run([py, "render_mp4.py", "video", "--changed"], cwd=nc, capture_output=True, text=True,
                           timeout=TIMEOUT, env=env)
        assert r.returncode != 0 and "changed on disk during the render" in (r.stdout + r.stderr), (r.stdout, r.stderr)
        m1, ph1, pic1, _ = snap()
        assert m1 == m0 and ph1 == ph0 and pic1 == pic0, "EDL edited mid-render: previous generation not intact"
        save_edl(d, E)
        print("M3 EDL saved mid-render: refused, previous generation intact")
        # R: audit r5 - in-place file replacements, corrupt provenance, the concat window, missing final
        rv("video", "--changed")
        rv("audio")
        rv("mux")
        assert not has_fail(rv("check", "--no-stills", ok=(0, 1)).stdout, "provenance")
        card(os.path.join(d, "graphics", "card-a.png"), "CARD A v2", (200, 120, 40, 230))       # same path, no EDL edit
        assert has_fail(rv("check", "--no-stills", ok=(1,)).stdout, "provenance")
        assert "older graphics" in rv("mux", ok=(1,)).stderr
        rv("video", "--changed")
        rv("mux")
        assert not has_fail(rv("check", "--no-stills", ok=(0, 1)).stdout, "provenance")
        print("R1 graphic replaced in place: check FAILs, mux refuses until video --changed")
        vw = os.path.join(d, "voice.wav")
        run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(d, "src.mp4"), "-vn", "-ac", "2", "-ar", str(SR),
             "-af", "volume=0.6", "-c:a", "pcm_s16le", vw + ".new.wav"], d)
        os.replace(vw + ".new.wav", vw)
        assert "voice, music or SFX" in rv("check", "--no-stills", ok=(1,)).stdout
        assert "was not made from this edit.edl.json and its current audio files" in rv("mux", ok=(1,)).stderr
        rv("audio")
        rv("mux")
        assert not has_fail(rv("check", "--no-stills", ok=(0, 1)).stdout, "provenance")
        print("R2 voice replaced in place: check FAILs, mux refuses until audio")
        fjp = os.path.join(outd, "final.json")
        good = open(fjp).read()
        open(fjp, "w").write("{")
        r = rv("check", "--no-stills", ok=(1,))
        rep_ = json.load(open(os.path.join(outd, "check", "report.json")))
        assert "corrupt" in r.stdout and any("corrupt" in x["msg"] for x in rep_["items"]), r.stdout
        open(fjp, "w").write(good)
        print("R3 truncated final.json: structured FAIL, report replaced")
        m0, ph0, pic0, _ = snap()
        E["images"][1]["y"] = 230
        save_edl(d, E)
        env = dict(os.environ, HL_TEST_EDL_REPLACE=os.path.join(d, "mut.edl.json"), HL_TEST_EDL_STAGE="after_concat")
        r = subprocess.run([py, "render_mp4.py", "video", "--changed"], cwd=nc, capture_output=True, text=True,
                           timeout=TIMEOUT, env=env)
        assert r.returncode != 0 and "changed on disk during the render" in (r.stdout + r.stderr), (r.stdout, r.stderr)
        m1, ph1, pic1, _ = snap()
        assert m1 == m0 and ph1 == ph0 and pic1 == pic0, "EDL edited after concat: previous generation not intact"
        save_edl(d, E)
        print("R5 EDL saved after concat: refused, previous generation intact")
        rv("check", "--no-stills", ok=(0, 1))
        os.rename(final, final + ".gone")
        rv("check", ok=(1,))
        rep_ = json.load(open(os.path.join(outd, "check", "report.json")))
        assert rep_["final"] is None and rep_["items"][0]["level"] == "FAIL", rep_
        os.rename(final + ".gone", final)
        print("R6 missing final: the previous report is replaced by a FAIL report")
        # V1 per-segment src + video-backed sequence (claude-edits cloud port, 2026-11-08), in its own edit
        d2 = os.path.join(d, "vid")
        g2 = os.path.join(d2, "graphics")
        os.makedirs(g2)
        src2 = os.path.join(d2, "other.mp4")
        run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"smptehdbars=size={W}x{H}:rate={FPS}:duration=3",
             "-c:v", "libx264", "-g", "60", "-pix_fmt", "yuv420p", src2], d2)
        scene = os.path.join(g2, "scene")                                     # no PNG frames, no poster: only scene.mp4
        run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=black:size={W}x{H}:rate={FPS}", "-frames:v", "60",
             "-vf", "geq=lum='16+N*3':cb=128:cr=128",                        # brightness = frame index
             "-c:v", "libx264", "-crf", "10", "-g", "30", "-pix_fmt", "yuv420p", scene + ".mp4"], d2)
        E2 = dict(E, output="vid.mp4",
                  segments=[{"in": 0.2, "out": 2.0}, {"in": 0.5, "out": 1.5, "src": src2}, {"in": 4.2, "out": 5.9}],
                  images=[{"path": os.path.join(scene, "000.png"), "start": 3.3, "duration": 1.0, "x": W / 2, "y": H / 2,
                           "pop": False, "seq": {"dir": scene, "frames": 60}, "kind": "scene"}])
        save_edl(d2, E2)
        json.dump([[0.0, 2.1]], open(os.path.join(d2, "th_ranges.json"), "w"))   # would cover the src piece by time
        nc2 = os.path.join(d2, "nocapcut")
        os.makedirs(nc2)
        shutil.copy(os.path.join(SK, "render_mp4.py"), nc2)
        r = run([py, "-c", "import render_mp4 as r; print(sorted(r.talking_head()))"], nc2)
        assert r.stdout.strip().splitlines()[-1] == "[0]", r.stdout                 # the src piece is never camera
        lint2 = run([py, os.path.join(SK, "lint_edl.py"), os.path.join(d2, "edit.edl.json")], d2, ok=(0, 1)).stdout
        assert "sequence incomplete" not in lint2 and "missing" not in lint2, lint2
        run([py, "render_mp4.py", "video", "--workers", "2"], nc2)
        pic2 = os.path.join(nc2, "out", "picture.mp4")
        t_src = 1.8 + 0.5 + 0.5 / FPS                                            # src piece: output 2.3 s = other.mp4 1.0 s
        dv = np.abs(frame(pic2, t_src) - frame(src2, 1.0 + 0.5 / FPS)).mean()
        dm = np.abs(frame(pic2, t_src) - frame(os.path.join(d, "src.mp4"), 1.0 + 0.5 / FPS)).mean()
        assert dv < 10 and dm > 40, (dv, dm)
        t_sc = 3.3 + 30 / FPS + 0.5 / FPS                                        # scene frame 30
        ds = np.abs(frame(pic2, t_sc) - frame(scene + ".mp4", 30 / FPS + 0.5 / FPS)).mean()
        ds2 = np.abs(frame(pic2, t_sc) - frame(scene + ".mp4", 25 / FPS + 0.5 / FPS)).mean()
        assert ds < 4 and ds2 > 10, (ds, ds2)                                 # the right frame, not a neighbour
        run([py, "render_mp4.py", "audio"], nc2)
        run([py, "render_mp4.py", "mux"], nc2)
        r = run([py, "render_mp4.py", "check", "--no-stills"], nc2, ok=(0, 1))
        assert not has_fail(r.stdout, "frames") and not has_fail(r.stdout, "provenance"), r.stdout
        os.utime(src2, ns=(time.time_ns(), time.time_ns()))                     # an extra source changed: full render
        assert "full render" in run([py, "render_mp4.py", "video", "--changed"], nc2).stdout
        shutil.move(scene + ".mp4", scene + ".mp4.gone")
        assert "sequence incomplete" in run([py, os.path.join(SK, "lint_edl.py"), os.path.join(d2, "edit.edl.json")], d2, ok=(1,)).stdout
        assert "required graphic file(s) missing" in run([py, "render_mp4.py", "video"], nc2, ok=(1,)).stderr
        shutil.move(scene + ".mp4.gone", scene + ".mp4")
        print(f"V1 per-segment src + video-backed scene: PASS (src diff {dv:.1f} vs main {dm:.1f}, scene frame {ds:.1f} vs neighbour {ds2:.1f})")
        print("FIXTURE OK", d if keep else "")
        ok = True
    finally:
        if ok and not keep:
            shutil.rmtree(d, ignore_errors=True)
        elif not ok:
            print("FIXTURE FAILED - evidence kept in", d)


if __name__ == "__main__":
    main()
