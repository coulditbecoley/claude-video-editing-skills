"""Rewrite absolute paths inside an edit's JSON files when the edit moves to another root (PC -> RunPod pod).

    python rebase_paths.py --map "C:\\Users\\you\\Projects\\Youtube\\edits\\X=/workspace/edits/X" \
                           --map "D:/edits/0939=/workspace/edits/X/src" <json files or dirs> [--dry-run] [--no-verify]
                           [--allow-root /opt/models]
    python rebase_paths.py --self-test

What it does
  Rewrites string values AND dict keys (music cues and voice maps use paths as keys) that sit under a mapped source
  root. Paths can be drive paths in either slash style (C:\\a, c:/a), UNC (\\\\srv\\share\\a), POSIX (/a) or file:///
  URLs of any of those; the output keeps the input's form (URL stays URL). Drive and UNC roots match
  case-insensitively, POSIX roots case-sensitively. Re-running with the same maps is a no-op that still verifies.

Maps must be disjoint: a destination under a source root is refused (a re-run would migrate it again); an identical
OLD=NEW pair is allowed and just verifies. A string only counts as changed if its text changes.

It fails (exit 1, and writes NOTHING, for the whole batch) when any selected file:
  - isn't valid JSON (UTF-8, BOM allowed),
  - holds an absolute path that is under no source root, destination root or --allow-root (never guessed by name),
  - would escape its root through "..",
  - points (under a destination or --allow-root) at a path that doesn't exist here, or whose resolved location
    (symlinks/junctions followed) leaves its root. --no-verify skips both checks, e.g. when rewriting before
    upload; then re-run with verification on the target machine before the job starts.
Writes are staged to <file>.rebase-tmp and swapped in with os.replace; if a swap fails midway, the files already
swapped are restored from their backups. The first rewrite of a file keeps the original as <name>.pre-rebase.json.

Scope: path text + existence + containment. Content integrity (sizes, hashes, sequence frame counts) is checked by
the transfer manifest (cloud INPUTS.json, M4) before a job starts, not here.
"""
import argparse, json, os, posixpath, re, shutil, sys
from pathlib import Path

URL = "file://"
DRIVE = re.compile(r"^[A-Za-z]:/")


def classify(s):
    """-> (kind, body, was_url) with body using '/' separators, or None if s isn't an absolute path.
    kind: 'drive' (C:/x), 'unc' (//srv/share/x), 'posix' (/x)."""
    was_url = s.startswith(URL)
    t = s[len(URL):] if was_url else s
    if was_url:
        if t.startswith("/") and DRIVE.match(t[1:].replace("\\", "/")):     # file:///C:/x
            t = t[1:]
        elif not t.startswith("/"):                                          # file://server/share/x
            t = "//" + t
    t = t.replace("\\", "/")
    if DRIVE.match(t):
        return "drive", t, was_url
    if t.startswith("//") and len(t) > 2 and t[2] != "/":
        return "unc", t, was_url
    if t.startswith("/"):
        return "posix", t, was_url
    return None


def serialize(kind, body, as_url):
    if not as_url:
        return body
    return URL + ("/" + body if kind == "drive" else body[1:] if kind == "unc" else body)


def fs_path(kind, body):
    return body if kind != "unc" else "\\\\" + body[2:].replace("/", "\\") if os.name == "nt" else body


def parse_root(r):
    c = classify(r.strip())
    if not c:
        raise SystemExit(f"root must be absolute: {r!r}")
    kind, body, _ = c
    body = body.rstrip("/") or "/"
    return kind, body


def under(kind, body, root):
    rk, rb = root
    if rk != kind:
        return None
    a, b = (body.lower(), rb.lower()) if kind in ("drive", "unc") else (body, rb)
    if a == b:
        return ""
    if b == "/":                                     # POSIX filesystem root: every absolute POSIX path is below it
        return body
    if a.startswith(b + "/"):
        return body[len(rb):]
    return None


def same_root(a, b):
    """Equal roots under the matching rules (drive/UNC case-insensitive, POSIX exact)."""
    return a[0] == b[0] and under(a[0], a[1], b) == ""


def trees_intersect(a, b):
    """True if root a and root b share any path (equal, a inside b, or b inside a)."""
    return under(a[0], a[1], b) is not None or under(b[0], b[1], a) is not None


def safe_rest(rest):
    """Normalize the part below a root; None if it climbs out with '..'."""
    if not rest:
        return ""
    depth = 0
    for part in rest.split("/"):
        depth += -1 if part == ".." else 0 if part in ("", ".") else 1
        if depth < 0:
            return None
    return posixpath.normpath(rest)


class Plan:
    def __init__(self, maps, allow):
        movers = [s for s, d in maps if not same_root(s, d)]           # identity maps never transform anything
        for s, d in maps:
            if same_root(s, d):
                continue
            for src in movers:
                if trees_intersect(d, src):
                    raise SystemExit(f"destination {d[1]} overlaps source root {src[1]} (equal, inside or containing "
                                     "it): a re-run could migrate paths again. Use disjoint roots; an identical OLD=NEW "
                                     "pair is allowed.")
        self.maps = sorted(maps, key=lambda m: -len(m[0][1]))       # longest source root wins
        self.dests = [d for _, d in maps]
        self.allow = allow

    def rebase(self, s, where, out):
        """Return the new string; record problems/targets in `out`."""
        c = classify(s)
        if not c:
            return s
        kind, body, was_url = c
        for src, dst in self.maps:
            rest = under(kind, body, src)
            if rest is None:
                continue
            r = safe_rest(rest)
            if r is None:
                out["escape"].append((where, s))
                return s
            if same_root(src, dst):                                  # identity map: verify only, keep the text
                out["targets"].append((where, kind, body, dst))
                return s
            nk, nb = dst[0], (dst[1].rstrip("/") + r) if dst[1] != "/" else (r or "/")
            out["targets"].append((where, nk, nb, dst))
            new = serialize(nk, nb, was_url)
            out["changed"] += new != s                               # identity maps verify but never rewrite
            return new
        for root in self.dests + self.allow:                         # already rebased, or explicitly allowed
            rest = under(kind, body, root)
            if rest is not None:
                if safe_rest(rest) is None:
                    out["escape"].append((where, s))
                else:                                                # allowed roots are verified too
                    out["targets"].append((where, kind, body, root))
                return s
        out["unmapped"].append((where, s))
        return s


def walk(x, plan, out, path="$"):
    if isinstance(x, str):
        return plan.rebase(x, path, out)
    if isinstance(x, list):
        return [walk(v, plan, out, f"{path}[{i}]") for i, v in enumerate(x)]
    if isinstance(x, dict):
        res = {}
        for k, v in x.items():
            nk = walk(k, plan, out, f"{path}.<key {k}>") if isinstance(k, str) else k
            if nk in res:
                out["collision"].append((path, nk))
            res[nk] = walk(v, plan, out, f"{path}.{k}")
        return res
    return x


def files_in(targets):
    seen = set()
    for t in targets:
        p = Path(t)
        cands = (sorted(q for q in p.rglob("*.json") if not q.name.endswith((".pre-rebase.json", ".rebase-tmp"))
                        and "node_modules" not in q.parts) if p.is_dir() else [p])
        for q in cands:
            k = os.path.normcase(str(q.resolve()))
            if k not in seen:
                seen.add(k)
                yield q


def analyse(f, plan, verify):
    out = {"changed": 0, "targets": [], "unmapped": [], "escape": [], "collision": [], "missing": [], "outside": [],
           "error": None}
    try:
        raw = Path(f).read_bytes()
        data = json.loads(raw.decode("utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        out["error"] = f"{type(e).__name__}: {e}"
        return None, out
    new = walk(data, plan, out)
    out["raw"] = raw                                                 # this run's preimage, for rollback
    if verify:
        out["missing"] = sorted({serialize(k, b, False) for _, k, b, _r in out["targets"] if not os.path.exists(fs_path(k, b))})
        out["outside"] = sorted({serialize(k, b, False) for _, k, b, r in out["targets"]
                                 if os.path.exists(fs_path(k, b)) and not inside(fs_path(k, b), fs_path(*r))})
    return new, out


def inside(path, root):
    """True if path, with symlinks/junctions resolved, stays under root (also resolved)."""
    rp, rr = os.path.realpath(path), os.path.realpath(root)
    return os.path.normcase(rp) == os.path.normcase(rr) or os.path.normcase(rp).startswith(os.path.normcase(rr).rstrip("\\/") + os.sep)


def problems(o):
    return o["error"] or o["unmapped"] or o["escape"] or o["collision"] or o["missing"] or o["outside"]


def commit(staged):
    """staged: [(path, new json, preimage bytes read by this run)]. All-or-nothing against ordinary exceptions
    (not power loss). Rollback restores each swapped file to THIS run's preimage, never to the long-lived
    .pre-rebase.json. If a rollback write itself fails, the preimage is left as <file>.rebase-recover and reported."""
    tmps, done = [], []
    try:
        for f, new, pre in staged:
            tmp = Path(str(f) + ".rebase-tmp")
            tmp.write_text(json.dumps(new, indent=1, ensure_ascii=False), encoding="utf-8")
            tmps.append((f, tmp, pre))
        for f, tmp, pre in tmps:
            bak = Path(f).with_name(Path(f).stem + ".pre-rebase.json")
            if not bak.exists():
                bak.write_bytes(pre)                                   # first-ever original, kept for the record
            os.replace(tmp, f)
            done.append((f, pre))
    except Exception:
        unrecovered = []
        for f, pre in done:
            try:
                Path(f).write_bytes(pre)
            except OSError:
                Path(str(f) + ".rebase-recover").write_bytes(pre)
                unrecovered.append(str(f))
        for _, tmp, _pre in tmps:
            if tmp.exists():
                tmp.unlink()
        if unrecovered:
            print("ROLLBACK INCOMPLETE; restore from .rebase-recover: " + ", ".join(unrecovered))
        raise


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("targets", nargs="*")
    ap.add_argument("--map", action="append", default=[])
    ap.add_argument("--allow-root", action="append", default=[])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-verify", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.map or not a.targets:
        ap.error("need --map and at least one target")
    maps = []
    for m in a.map:
        old, sep, new = m.rpartition("=")
        if not sep or not old or not new:
            ap.error(f"bad --map {m!r}: want OLD=NEW")
        maps.append((parse_root(old), parse_root(new)))
    plan = Plan(maps, [parse_root(r) for r in a.allow_root])
    results = [(f, *analyse(f, plan, not a.no_verify)) for f in files_in(a.targets)]
    if not results:
        print("FAIL no JSON files found")
        return 1
    bad = 0
    for f, _, o in results:
        flag = "FAIL" if problems(o) else "OK"
        bad += flag == "FAIL"
        if o["changed"] or flag == "FAIL":
            print(f"{flag} {f}: {o['changed']} rewritten")
        if o["error"]:
            print(f"   INVALID {o['error']}")
        for label in ("unmapped", "escape", "collision"):
            for w, s in o[label][:20]:
                print(f"   {label.upper()} {w}: {s}")
        for s in o["missing"][:20]:
            print(f"   MISSING {s}")
        for s in o["outside"][:20]:
            print(f"   OUTSIDE-ROOT (resolves elsewhere) {s}")
    if bad:
        print(f"FAIL ({bad} file(s) with problems; nothing written)")
        return 1
    staged = [(f, new, o["raw"]) for f, new, o in results if o["changed"]]
    if a.dry_run:
        print(f"OK dry run: {len(staged)} file(s) would change")
    else:
        commit(staged)
        print(f"OK {len(staged)} file(s) rewritten")
    return 0


def self_test():
    import tempfile
    from unittest import mock
    P = lambda *m, allow=(): Plan([(parse_root(a), parse_root(b)) for a, b in m], [parse_root(r) for r in allow])
    def rb(s, plan):
        o = {"changed": 0, "targets": [], "unmapped": [], "escape": [], "collision": [], "missing": []}
        return plan.rebase(s, "$", o), o
    p = P((r"C:\Users\you\Projects\Youtube\edits\E", "/workspace/edits/E"), ("D:/edits/0939", "/workspace/edits/E/src"))
    assert rb(r"C:\Users\you\Projects\Youtube\edits\E\audio\pop.wav", p)[0] == "/workspace/edits/E/audio/pop.wav"
    assert rb("c:/users/you/projects/youtube/edits/e/graphics/out/a.png", p)[0] == "/workspace/edits/E/graphics/out/a.png"
    assert rb("D:/edits/0939/src.mp4", p)[0] == "/workspace/edits/E/src/src.mp4"
    s, o = rb("D:/edits/09391/src.mp4", p); assert s == "D:/edits/09391/src.mp4" and o["unmapped"]      # prefix, not a root
    assert rb("file:///C:/Users/you/Projects/Youtube/edits/E/x.mjs", p)[0] == "file:///workspace/edits/E/x.mjs"
    assert rb("pop", p)[0] == "pop" and rb("audio/pop.wav", p)[1]["changed"] == 0                          # relative kept
    # rerun on already-rebased text: unchanged, counted as a target for verification, not unmapped
    s, o = rb("/workspace/edits/E/audio/pop.wav", p); assert s == "/workspace/edits/E/audio/pop.wav" and len(o["targets"]) == 1 and not o["unmapped"]
    s, o = rb("file:///workspace/edits/E/x.mjs", p); assert not o["unmapped"] and o["targets"]
    # POSIX roots are case-sensitive; an unknown POSIX root is unmapped
    s, o = rb("/Workspace/edits/E/a", p); assert o["unmapped"]
    # UNC both styles, URL map roots, Windows destinations and reruns
    q = P((r"\\nas\share\E", "D:/E2"), ("file:///C:/old", "file:///workspace/E"))
    assert rb(r"\\NAS\share\E\a.wav", q)[0] == "D:/E2/a.wav"
    assert rb("//nas/share/E/b.wav", q)[0] == "D:/E2/b.wav"
    assert rb("file:///C:/old/x", q)[0] == "file:///workspace/E/x"
    s, o = rb("D:/E2/a.wav", q); assert s == "D:/E2/a.wav" and not o["unmapped"]                       # rerun to drive dest
    # traversal is refused, even under a destination root
    s, o = rb("D:/edits/0939/../outside.wav", p); assert o["escape"] and s == "D:/edits/0939/../outside.wav"
    s, o = rb("/workspace/edits/E/../../x", p); assert o["escape"]
    # allow-root
    s, o = rb("/opt/models/face.task", P(("D:/a", "/b"), allow=["/opt/models"])); assert not o["unmapped"]
    # keys and collisions
    o = {"changed": 0, "targets": [], "unmapped": [], "escape": [], "collision": [], "missing": []}
    out = walk({"voice": {"D:/edits/0939/src.mp4": r"C:\Users\you\Projects\Youtube\edits\E\audio\v.wav"}}, p, o)
    assert out["voice"] == {"/workspace/edits/E/src/src.mp4": "/workspace/edits/E/audio/v.wav"} and o["changed"] == 2
    o = {"changed": 0, "targets": [], "unmapped": [], "escape": [], "collision": [], "missing": []}
    walk({"D:/edits/0939/a": 1, "/workspace/edits/E/src/a": 2}, p, o); assert o["collision"]
    with tempfile.TemporaryDirectory() as d:
        D = Path(d); root = d.replace("\\", "/")
        (D / "a.wav").write_bytes(b"x")
        f1, f2 = D / "e1.json", D / "e2.json"
        # 1 happy path + backup + idempotent rerun (verifies, writes nothing new)
        f1.write_text(json.dumps({"p": "D:/edits/0939/a.wav"}))
        assert main(["--map", f"D:/edits/0939={root}", str(f1)]) == 0
        assert json.loads(f1.read_text())["p"] == root + "/a.wav" and (D / "e1.pre-rebase.json").exists()
        m1 = f1.stat().st_mtime_ns
        assert main(["--map", f"D:/edits/0939={root}", str(f1)]) == 0 and f1.stat().st_mtime_ns == m1
        # 2 batch: second file bad -> NOTHING written to the first
        f1.write_text(json.dumps({"p": "D:/edits/0939/a.wav"})); (D / "e1.pre-rebase.json").unlink()
        f2.write_text(json.dumps({"p": "Q:/unmapped.wav"}))
        assert main(["--map", f"D:/edits/0939={root}", str(f1), str(f2)]) == 1
        assert json.loads(f1.read_text())["p"] == "D:/edits/0939/a.wav" and not (D / "e1.pre-rebase.json").exists()
        # 3 malformed explicit JSON fails (and BOM is accepted)
        f2.write_text("{broken")
        assert main(["--map", f"D:/edits/0939={root}", str(f2)]) == 1
        f2.write_bytes(b"\xef\xbb\xbf" + json.dumps({"p": "D:/edits/0939/a.wav"}).encode())
        assert main(["--map", f"D:/edits/0939={root}", "--dry-run", str(f2)]) == 0
        # 4 missing target fails; --no-verify allows it
        f2.write_text(json.dumps({"p": "D:/edits/0939/missing.wav"}))
        assert main(["--map", f"D:/edits/0939={root}", str(f2)]) == 1
        assert main(["--map", f"D:/edits/0939={root}", "--no-verify", "--dry-run", str(f2)]) == 0
        # 5 a failure during the swap phase rolls back the files already swapped
        f1.write_text(json.dumps({"p": "D:/edits/0939/a.wav"})); (D / "e1.pre-rebase.json").unlink(missing_ok=True)
        f2.write_text(json.dumps({"q": "D:/edits/0939/a.wav"})); (D / "e2.pre-rebase.json").unlink(missing_ok=True)
        real = os.replace
        calls = []
        def flaky(a_, b_):
            calls.append(b_)
            if len(calls) == 2:
                raise OSError("injected")
            return real(a_, b_)
        with mock.patch("os.replace", flaky):
            try:
                main(["--map", f"D:/edits/0939={root}", str(f1), str(f2)])
                raise AssertionError("injected failure not raised")
            except OSError:
                pass
        assert json.loads(f1.read_text())["p"] == "D:/edits/0939/a.wav", "first file not rolled back"
        assert json.loads(f2.read_text())["q"] == "D:/edits/0939/a.wav"
        assert not list(D.glob("*.rebase-tmp")), "temp files left behind"
        # 6 a directory with no JSON fails loudly
        (D / "empty").mkdir()
        assert main(["--map", f"D:/edits/0939={root}", str(D / "empty")]) == 1
        # 7 stale first-ever backup must NOT be used for rollback (round-2 finding)
        f1.write_text(json.dumps({"revision": "current", "p": "D:/edits/0939/a.wav"}))
        (D / "e1.pre-rebase.json").write_text(json.dumps({"revision": "stale"}))
        f2.write_text(json.dumps({"q": "D:/edits/0939/a.wav"}))
        for fail_at in (1, 2):
            pre1, pre2 = f1.read_bytes(), f2.read_bytes()
            calls.clear()
            def flaky2(a_, b_, n=fail_at):
                calls.append(b_)
                if len(calls) == n:
                    raise OSError("injected")
                return real(a_, b_)
            with mock.patch("os.replace", flaky2):
                try:
                    main(["--map", f"D:/edits/0939={root}", str(f1), str(f2)])
                    raise AssertionError("injected failure not raised")
                except OSError:
                    pass
            assert f1.read_bytes() == pre1 and f2.read_bytes() == pre2, f"rollback lost this run's preimage (fail at {fail_at})"
        assert json.loads((D / "e1.pre-rebase.json").read_text()) == {"revision": "stale"}
        # 8 identity map: verifies, writes nothing, no backup
        f3 = D / "e3.json"; f3.write_text(json.dumps({"p": f"{root}/a.wav", "w": f"{root}\\a.wav".replace("/", "\\")}))
        m3 = f3.stat().st_mtime_ns
        assert main(["--map", f"{root}={root}", str(f3)]) == 0 and f3.stat().st_mtime_ns == m3
        assert not (D / "e3.pre-rebase.json").exists()
        # 9 allowed roots are verified: a missing file under --allow-root fails
        f3.write_text(json.dumps({"p": f"{root}/nope.wav", "q": "D:/edits/0939/a.wav"}))
        assert main(["--map", f"D:/edits/0939={root}", "--allow-root", root, "--dry-run", str(f3)]) == 1
        # 10 a junction/symlink under a root that resolves outside it fails verification
        outside = Path(tempfile.mkdtemp()); (outside / "x.wav").write_bytes(b"x")
        link = D / "link"
        try:
            if os.name == "nt":
                import subprocess
                subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside)], check=True, capture_output=True)
            else:
                link.symlink_to(outside, target_is_directory=True)
            f3.write_text(json.dumps({"p": "D:/edits/0939/link/x.wav"}))
            assert main(["--map", f"D:/edits/0939={root}", "--dry-run", str(f3)]) == 1, "escape via link not caught"
        finally:
            if link.exists():
                os.rmdir(link) if os.name == "nt" else link.unlink()
            shutil.rmtree(outside, ignore_errors=True)
    # overlap and root-boundary rules
    try:
        Plan([(parse_root("D:/old"), parse_root("D:/old/new"))], []); raise AssertionError("nested map accepted")
    except SystemExit:
        pass
    Plan([(parse_root("D:/old"), parse_root("D:/old"))], [])           # identity is allowed
    Plan([(parse_root("D:/old"), parse_root("d:/OLD"))], [])           # case-equivalent drive identity is allowed
    Plan([(parse_root("D:/a"), parse_root("/w/a")), (parse_root("D:/b"), parse_root("D:/b"))], [])   # mover + identity
    Plan([(parse_root("D:/a"), parse_root("/w/a")), (parse_root("D:/a/sub"), parse_root("/w/s"))], [])  # nested sources, disjoint outputs
    Plan([(parse_root(r"C:\U\E"), parse_root("/workspace/edits/E")),            # the real pilot map pair
          (parse_root("D:/edits/0939"), parse_root("/workspace/edits/E/src"))], [])
    for bad in ([("D:/A", "D:/B"), ("D:/B", "D:/C")],                 # chain A->B, B->C
                [("D:/A", "D:/B"), ("D:/B", "D:/A")],                 # cycle
                [("D:/A", "d:/b"), ("D:/B", "D:/C")],                 # case-equivalent chain
                [(r"\\nas\s\A", r"\\NAS\S\B"), ("//nas/s/b", "D:/x")],   # UNC chain, mixed case/slashes
                [("D:/A", "D:/B/sub"), ("D:/B", "D:/C")],             # destination under another source
                [("D:/A", "D:/B"), ("D:/B/sub", "D:/C")],             # destination CONTAINS another source (R4)
                [("D:/A", "D:/B"), ("D:/B", "D:/B2"), ("D:/Q", "D:/Q")]):   # chain with an unrelated identity map
        try:
            Plan([(parse_root(a), parse_root(b)) for a, b in bad], []); raise AssertionError(f"accepted {bad}")
        except SystemExit:
            pass
    o = {"changed": 0, "targets": [], "unmapped": [], "escape": [], "collision": [], "missing": []}
    assert Plan([(parse_root("/"), parse_root("D:/new"))], []).rebase("/a.wav", "$", o) == "D:/new/a.wav"
    o = {"changed": 0, "targets": [], "unmapped": [], "escape": [], "collision": [], "missing": []}
    Plan([(parse_root("D:/x"), parse_root("D:/y"))], [parse_root("/")]).rebase("/opt/a", "$", o); assert not o["unmapped"]
    print("self-test OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
