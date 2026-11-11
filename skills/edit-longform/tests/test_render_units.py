"""Unit checks for render_mp4.py helpers that need no GPU (M-S6, 2026-11-08).

    python test_render_units.py

  Q  _cpu_quota: v2 / v1 quota, nested cgroup and tighter ancestor, affinity smaller than quota, unlimited, no cgroup
     (Windows), invalid values; --workers validation and auto
  V  video-backed sequence: cached decoded frame never written, repeats / seeks exact
  O  a source frame repeated by the lip-sync map (or a held last frame) composites like a fresh copy of the pristine
     decode: semi-transparent cover + overlay used to blend twice on the repeat (audit R1 #3)
"""
import importlib.util, json, os, shutil, sys, tempfile
import numpy as np, cv2

SK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")
W, H = 64, 36


def load(d):
    """render_mp4.py in a minimal temp edit (the module reads <edit>/edit.edl.json at import)."""
    cv2.imwrite(os.path.join(d, "cover.png"), np.dstack([np.full((H, W, 3), (0, 0, 255), np.uint8), np.full((H, W), 100, np.uint8)]))
    cv2.imwrite(os.path.join(d, "card.png"), np.dstack([np.full((10, 20, 3), 255, np.uint8), np.full((10, 20), 128, np.uint8)]))
    img = lambda n, **k: dict({"path": os.path.join(d, n), "start": 0.0, "duration": 2.0, "x": W / 2, "y": H / 2}, **k)
    edl = {"source": "none.mp4", "resolution": [W, H], "voice": {"none.mp4": "none.wav"}, "music": [], "sfx": [],
           "segments": [{"in": 0.0, "out": 2.0}],
           "images": [img("cover.png", pop=False, under=True), img("card.png", pop=False), img("card.png", y=8, pop=True)]}
    json.dump(edl, open(os.path.join(d, "edit.edl.json"), "w"))
    os.makedirs(os.path.join(d, "nocapcut"))
    shutil.copy(os.path.join(SK, "render_mp4.py"), os.path.join(d, "nocapcut", "render_mp4.py"))
    spec = importlib.util.spec_from_file_location("render_mp4_t", os.path.join(d, "nocapcut", "render_mp4.py"))
    R = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(R)
    return R


def tree(d, files):
    for rel, txt in files.items():
        os.makedirs(os.path.dirname(os.path.join(d, rel)), exist_ok=True)
        open(os.path.join(d, rel), "w").write(txt)


def test_quota(R, d):
    def q(name, files, proc, aff=48):
        root = os.path.join(d, name)
        tree(root, files)
        pf = os.path.join(root, "proc_cgroup")
        if proc is not None:
            open(pf, "w").write(proc)
        return R._cpu_quota(root=root, proc=pf, affinity=aff)
    assert q("v2root", {"cpu.max": "1360000 100000\n"}, "0::/\n") == 13.6
    assert q("v1", {"cpu/cpu.cfs_quota_us": "600000\n", "cpu/cpu.cfs_period_us": "100000\n"}, "4:cpu,cpuacct:/\n") == 6
    assert q("v1named", {"cpu,cpuacct/k/c/cpu.cfs_quota_us": "300000", "cpu,cpuacct/k/c/cpu.cfs_period_us": "100000"},
             "4:cpu,cpuacct:/k/c\n") == 3
    # combined v1 mount with no cpu alias: its own root quota, and an unlimited child under a capped combined root
    assert q("v1comb", {"cpu,cpuacct/cpu.cfs_quota_us": "200000", "cpu,cpuacct/cpu.cfs_period_us": "100000"},
             "4:cpu,cpuacct:/\n") == 2
    assert q("v1combchild", {"cpu,cpuacct/cpu.cfs_quota_us": "200000", "cpu,cpuacct/cpu.cfs_period_us": "100000",
                             "cpu,cpuacct/k/cpu.cfs_quota_us": "-1", "cpu,cpuacct/k/cpu.cfs_period_us": "100000"},
             "4:cpu,cpuacct:/k\n") == 2
    # nested: leaf allows 8, an ancestor caps at 2.5
    assert q("nested", {"cpu.max": "max 100000", "a/cpu.max": "250000 100000", "a/b/cpu.max": "800000 100000"},
             "0::/a/b\n") == 2.5
    assert q("leaf", {"a/cpu.max": "max 100000", "a/b/cpu.max": "150000 100000"}, "0::/a/b\n") == 1.5
    assert q("affinity", {"cpu.max": "1360000 100000"}, "0::/\n", aff=2) == 2          # affinity tighter than quota
    assert q("unlimited", {"cpu.max": "max 100000", "cpu/cpu.cfs_quota_us": "-1", "cpu/cpu.cfs_period_us": "100000"},
             "0::/\n", aff=20) == 20
    assert q("nocgroup", {}, None, aff=12) == 12                                       # Windows / no /proc
    assert q("invalid", {"cpu.max": "100000 0", "a/cpu.max": "abc 100000", "b/cpu.max": "-5 100000"}, "0::/a\n1::\n", aff=7) == 7
    assert q("hostpath", {"cpu.max": "400000 100000"}, "0::/host/only/path\n") == 4    # invisible host path skipped
    assert R._cpu_quota(root=os.path.join(d, "missing"), proc=os.path.join(d, "missing", "p")) >= 1   # real affinity
    assert R._workers([]) == 4 and R._workers(["--workers", "3"]) == 3 and R._workers(["--workers", "auto"]) >= 1
    for bad in (["--workers", "0"], ["--workers", "-2"], ["--workers", "x"], ["--workers"]):
        try:
            R._workers(bad)
            raise AssertionError(f"{bad} accepted")
        except SystemExit:
            pass
    print("Q cpu quota / workers: PASS")


def test_repeat(R):
    rng = np.random.default_rng(3)
    p = R.P[0]
    comp = lambda s, k: R.draw_images(R.frame_for(p, s, k / 60, set()), k / 60)
    a, b = (rng.integers(0, 256, (H, W, 3), dtype=np.uint8) for _ in range(2))
    pristine = [a.copy(), a.copy(), a.copy(), b.copy(), b.copy()]
    want = [comp(x.copy(), k) for k, x in enumerate(pristine)]
    got = [comp(s, k) for k, s in enumerate(R._own(iter([a, a, a, b, b])))]      # same objects, as the decoder yields
    for k, (g, w) in enumerate(zip(got, want)):
        assert np.array_equal(g, w), f"frame {k} differs from compositing the pristine source"
    c2 = rng.integers(0, 256, (H, W, 3), dtype=np.uint8)
    ref = comp(c2.copy(), 1)
    bug = [comp(s, k) for k, s in enumerate([c2, c2])][1]                       # the pre-fix path: no _own
    assert not np.array_equal(bug, ref), "test can't see the bug: a raw repeat should double-blend"
    x, y = rng.integers(0, 256, (2, H, W, 3), dtype=np.uint8)
    out = list(R._own(iter([x, y])))
    assert out[0] is x and out[1] is y, "_own must not copy frames that don't repeat"
    print("O repeated source frame composites from the pristine decode: PASS")


def test_video_seq(R, d):
    """A video-backed sequence (<dir>.mp4): the cached decoded frame is never written by compositing, repeats and
    backwards seeks give the same pixels, and an opaque full-canvas scene replaces the picture exactly."""
    import subprocess
    sd = os.path.join(d, "scene")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=s={W}x{H}:r=60", "-frames:v", "10",
                    "-pix_fmt", "yuv444p", "-c:v", "libx264", "-crf", "0", sd + ".mp4"], check=True)
    im = {"path": sd + ".png", "start": 0.0, "duration": 1.0, "x": W / 2, "y": H / 2, "noexit": True,
          "seq": {"dir": sd, "frames": 10}}
    saved = list(R.IMAGES)
    R.IMAGES[:] = [im]
    try:
        assert R.seq_video(im["seq"]) == sd + ".mp4" and R.seq_video({"dir": sd + "x"}) is None
        v = sd + ".mp4"
        ref = R.vid_frame(v, 3).copy()
        R.SPR.clear(); R.PM.clear()
        rng = np.random.default_rng(5)
        a = rng.integers(0, 256, (H, W, 3), dtype=np.uint8)
        outs = [R.draw_images(s, 3 / 60) for s in R._own(iter([a, a, a]))]          # repeated source, drawn in place
        outs.append(R.draw_images(R.draw_images(rng.integers(0, 256, (H, W, 3), dtype=np.uint8), 3 / 60), 3 / 60))
        assert np.array_equal(R.VID[v][2], ref), "compositing wrote into the cached video frame"
        for o in outs:
            assert np.array_equal(o, ref), "opaque video scene must replace the picture exactly"
        R.vid_frame(v, 7)
        assert np.array_equal(R.vid_frame(v, 3), ref), "seek back to frame 3 gave different pixels"
        R.SPR.clear(); R.PM.clear()
        assert np.array_equal(R.draw_images(np.zeros((H, W, 3), np.uint8), 7 / 60), R.vid_frame(v, 7))
    finally:
        R.IMAGES[:] = saved
        for st in R.VID.values():
            st[0].release()
        R.VID.clear()
    print("V video-backed sequence: cached frame untouched, repeats and seeks exact: PASS")


if __name__ == "__main__":
    d = tempfile.mkdtemp(prefix="render_units_")
    try:
        R = load(d)
        test_quota(R, d)
        test_repeat(R)
        test_video_seq(R, d)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print("UNITS OK")
