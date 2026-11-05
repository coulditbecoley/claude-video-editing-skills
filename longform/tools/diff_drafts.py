"""What did Coley change? Diff a draft Claude built against the same draft after
Coley edited it in CapCut. Every change is a teaching signal.

usage: python diff_drafts.py <baseline draft_content.json> <edited draft folder or json> [--out corrections/<date> <name>.md]

Snapshot the baseline right after building (library/<video>/draft_built.json), let
Coley edit in CapCut, then diff against the live draft. Reports:
- main-track pieces removed / added / trimmed (in and out points, in frames)
- overlays (graphics, cam overlays) removed / added / moved in time / resized / repositioned
- audio clips removed / added, volume changes
- transitions changed, text layers added, new effects or filters
Turn each finding into a rule in profile/taste.md (with the date and video as evidence).
"""
import json
import sys
from pathlib import Path

US, FR = 1_000_000, 1_000_000 / 30


def load(p):
    p = Path(p)
    return json.loads((p / "draft_content.json" if p.is_dir() else p).read_text(encoding="utf-8"))


def key_items(d):
    mats = {}
    for kind in ("videos", "audios", "texts"):
        for m in d["materials"].get(kind, []):
            mats[m["id"]] = m
    items = []
    for ti, t in enumerate(d["tracks"]):
        for s in t["segments"]:
            m = mats.get(s["material_id"], {})
            name = m.get("material_name") or Path(m.get("path", "")).name or m.get("type", "?")
            if t["type"] == "text":
                try:
                    name = json.loads(m.get("content", "{}")).get("text", name)[:40]
                except Exception:
                    pass
            items.append({"track": t["type"] + ("-main" if ti == 0 and t["type"] == "video" else ""),
                          "name": name, "t": s["target_timerange"]["start"], "dur": s["target_timerange"]["duration"],
                          "src": (s.get("source_timerange") or {}).get("start"),
                          "srcdur": (s.get("source_timerange") or {}).get("duration"),
                          "vol": s.get("volume"), "clip": s.get("clip"),
                          "tr": [r for r in s.get("extra_material_refs", [])]})
    return items


def match(a_items, b_items):
    """Pair items by track + name + nearest source/target time."""
    used, pairs, removed = set(), [], []
    for a in a_items:
        best, bd = None, None
        for j, b in enumerate(b_items):
            if j in used or b["track"] != a["track"] or b["name"] != a["name"]:
                continue
            ref_a = a["src"] if a["src"] is not None and a["track"] == "video-main" else a["t"]
            ref_b = b["src"] if b["src"] is not None and b["track"] == "video-main" else b["t"]
            dist = abs(ref_a - ref_b)
            if dist < 3 * US and (bd is None or dist < bd):
                best, bd = j, dist
        if best is None:
            removed.append(a)
        else:
            used.add(best)
            pairs.append((a, b_items[best]))
    added = [b for j, b in enumerate(b_items) if j not in used]
    return pairs, removed, added


def fmt_t(us):
    return f"{us / US:7.2f}s"


def diff(a, b):
    A, B = key_items(a), key_items(b)
    pairs, removed, added = match(A, B)
    L = []
    for x in removed:
        L.append(f"- REMOVED {x['track']:10} {x['name']} at {fmt_t(x['t'])} ({x['dur'] / US:.2f}s)")
    for x in added:
        L.append(f"- ADDED   {x['track']:10} {x['name']} at {fmt_t(x['t'])} ({x['dur'] / US:.2f}s)")
    for x, y in pairs:
        ch = []
        if x["src"] is not None and y["src"] is not None and abs(x["src"] - y["src"]) > FR / 2:
            ch.append(f"in-point {(y['src'] - x['src']) / FR:+.0f} frames")
        if abs(x["dur"] - y["dur"]) > FR / 2:
            ch.append(f"length {(y['dur'] - x['dur']) / US:+.2f}s")
        if x["track"] != "video-main" and abs(x["t"] - y["t"]) > FR / 2:
            ch.append(f"moved {(y['t'] - x['t']) / US:+.2f}s")
        if x["vol"] is not None and y["vol"] is not None and abs(x["vol"] - y["vol"]) > 1e-3:
            ch.append(f"volume {x['vol']:.3f} -> {y['vol']:.3f}")
        if x["clip"] and y["clip"]:
            sx, sy = x["clip"]["scale"]["x"], y["clip"]["scale"]["x"]
            if abs(sx - sy) > 1e-3:
                ch.append(f"scale {sx:.3f} -> {sy:.3f}")
            tx, ty = x["clip"]["transform"], y["clip"]["transform"]
            if abs(tx["x"] - ty["x"]) > 1e-3 or abs(tx["y"] - ty["y"]) > 1e-3:
                ch.append(f"position ({tx['x']:.3f},{tx['y']:.3f}) -> ({ty['x']:.3f},{ty['y']:.3f})")
        if ch:
            L.append(f"- CHANGED {x['track']:10} {x['name']} at {fmt_t(x['t'])}: " + ", ".join(ch))
    for kind in ("transitions", "effects", "video_effects", "filters", "adjust_masks", "audio_effects"):
        na, nb = len(a["materials"].get(kind, [])), len(b["materials"].get(kind, []))
        if na != nb:
            names = sorted({m.get("name", "?") for m in b["materials"].get(kind, [])} - {m.get("name", "?") for m in a["materials"].get(kind, [])})
            L.append(f"- {kind}: {na} -> {nb}" + (f" (new: {', '.join(names)})" if names else ""))
    if a.get("duration") != b.get("duration"):
        L.append(f"- runtime {a['duration'] / US:.2f}s -> {b['duration'] / US:.2f}s")
    return L


if __name__ == "__main__":
    a, b = load(sys.argv[1]), load(sys.argv[2])
    lines = diff(a, b)
    text = "\n".join(lines) if lines else "no differences"
    print(text)
    if "--out" in sys.argv:
        Path(sys.argv[sys.argv.index("--out") + 1]).write_text("# Corrections\n\n" + text + "\n", encoding="utf-8")
