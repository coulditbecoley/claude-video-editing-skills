"""Measure a CapCut draft: what an edit actually did, as numbers.

usage: python analyze_draft.py <draft folder or draft_content.json> [--out metrics.json]

Works on any CapCut draft (one Coley edited by hand or one ccut built), because it
reads only CapCut's own draft_content.json. Prints a readable summary and writes
metrics JSON for the library / profile.

What it measures
- runtime, canvas, fps
- main track: pieces, cuts per minute, piece length distribution, how much of the
  source was kept, speed changes, gaps
- reframing: punch-ins (static scale), keyframed zooms, share of runtime zoomed
- transitions: names, durations, where
- overlays: photo graphics / video overlays per track, density (first 60 s vs rest),
  on-screen durations
- text: text layers (captions or titles) and their count
- audio: tracks classified as voice (parallel to main), music (long beds), sfx (short hits),
  with volumes; clip fades
- effects / filters / adjustments present
"""
import json
import statistics as st
import sys
from pathlib import Path

US = 1_000_000


def load(p):
    p = Path(p)
    if p.is_dir():
        p = p / "draft_content.json"
    return json.loads(p.read_text(encoding="utf-8")), p


def q(vals, k):
    if not vals:
        return None
    vals = sorted(vals)
    return round(vals[min(len(vals) - 1, int(k * len(vals)))], 2)


def analyze(d):
    mats = {m["id"]: m for m in d["materials"].get("videos", [])}
    amats = {m["id"]: m for m in d["materials"].get("audios", [])}
    total = d.get("duration", 0) / US
    out = {"runtime_s": round(total, 2), "canvas": [d["canvas_config"]["width"], d["canvas_config"]["height"]],
           "fps": d.get("fps")}
    vtracks = [t for t in d["tracks"] if t["type"] == "video"]
    atracks = [t for t in d["tracks"] if t["type"] == "audio"]
    ttracks = [t for t in d["tracks"] if t["type"] == "text"]
    main = vtracks[0] if vtracks else {"segments": []}

    # --- main track ---
    segs = main["segments"]
    lens = [s["target_timerange"]["duration"] / US for s in segs]
    src_by_mat = {}
    for s in segs:
        m = mats.get(s["material_id"], {})
        src_by_mat.setdefault(m.get("path", "?"), []).append(
            (s["source_timerange"]["start"] / US, (s["source_timerange"]["start"] + s["source_timerange"]["duration"]) / US))
    kept = {}
    for path, rs in src_by_mat.items():
        dur = mats_dur = next((m["duration"] / US for m in mats.values() if m.get("path") == path), None)
        used = sum(b - a for a, b in rs)
        kept[Path(path).name] = {"pieces": len(rs), "used_s": round(used, 1),
                                 "source_s": round(dur, 1) if dur else None,
                                 "kept_pct": round(100 * used / dur, 1) if dur else None}
    gaps = []
    for a, b in zip(segs, segs[1:]):
        g = b["target_timerange"]["start"] - (a["target_timerange"]["start"] + a["target_timerange"]["duration"])
        if g > US // 30:
            gaps.append(round(g / US, 2))
    speeds = [s.get("speed", 1.0) for s in segs if abs(s.get("speed", 1.0) - 1) > 1e-3]
    out["main"] = {"pieces": len(segs), "cuts_per_min": round(60 * max(0, len(segs) - 1) / total, 1) if total else None,
                   "piece_s": {"median": q(lens, .5), "p10": q(lens, .1), "p90": q(lens, .9)},
                   "sources": kept, "speed_changes": len(speeds), "gaps": gaps}

    # --- reframing ---
    punch, zoom_pieces, zoom_time = 0, 0, 0.0
    for s in segs:
        sc = s.get("clip", {}).get("scale", {}).get("x", 1.0)
        kf = [k for k in s.get("common_keyframes", []) if k["property_type"] in ("KFTypeScaleX", "UNIFORM_SCALE")]
        vals = [v for k in kf for x in k["keyframe_list"] for v in x["values"]]
        if kf and (max(vals) > 1.02):
            zoom_pieces += 1
            zoom_time += s["target_timerange"]["duration"] / US
        elif sc > 1.02:
            punch += 1
            zoom_time += s["target_timerange"]["duration"] / US
    out["reframe"] = {"punch_in_pieces": punch, "keyframed_zoom_pieces": zoom_pieces,
                      "zoomed_pct_of_runtime": round(100 * zoom_time / total, 1) if total else None}

    # --- transitions ---
    tr = {t["id"]: t for t in d["materials"].get("transitions", [])}
    tlist = []
    for s in segs:
        for ref in s.get("extra_material_refs", []):
            if ref in tr:
                tlist.append({"name": tr[ref]["name"], "at_s": round((s["target_timerange"]["start"] + s["target_timerange"]["duration"]) / US, 1),
                              "dur_s": round(tr[ref]["duration"] / US, 2)})
    out["transitions"] = tlist

    # --- overlays (every video track after main) ---
    ov = []
    for t in vtracks[1:]:
        for s in t["segments"]:
            m = mats.get(s["material_id"], {})
            ov.append({"t": s["target_timerange"]["start"] / US, "dur": s["target_timerange"]["duration"] / US,
                       "kind": m.get("type"), "name": m.get("material_name") or Path(m.get("path", "")).name,
                       "animated": bool(s.get("common_keyframes"))})
    photos = [o for o in ov if o["kind"] == "photo"]
    vids = [o for o in ov if o["kind"] != "photo"]
    first60 = [o for o in photos if o["t"] < 60]
    out["overlays"] = {"graphics": len(photos), "video_overlays": len(vids),
                       "graphics_per_min": round(60 * len(photos) / total, 2) if total else None,
                       "graphics_first_60s": len(first60),
                       "graphic_on_screen_s": {"median": q([o["dur"] for o in photos], .5), "p90": q([o["dur"] for o in photos], .9)},
                       "animated_share": round(sum(o["animated"] for o in photos) / len(photos), 2) if photos else None,
                       "names": sorted({o["name"] for o in photos})}

    # --- text ---
    texts = [s for t in ttracks for s in t["segments"]]
    out["text"] = {"layers": len(texts), "tracks": len(ttracks)}

    # --- audio ---
    main_starts = {round(s["target_timerange"]["start"] / US, 2) for s in segs}
    at = []
    for t in atracks:
        ss = t["segments"]
        if not ss:
            continue
        starts = {round(s["target_timerange"]["start"] / US, 2) for s in ss}
        dur = [s["target_timerange"]["duration"] / US for s in ss]
        vols = [s.get("volume", 1.0) for s in ss]
        if len(starts & main_starts) > 0.8 * len(ss) and len(ss) > 3:
            kind = "voice"
        elif st.median(dur) > 20:
            kind = "music"
        else:
            kind = "sfx"
        names = sorted({Path(amats.get(s["material_id"], {}).get("path", "?")).name for s in ss})
        at.append({"kind": kind, "clips": len(ss), "median_len_s": round(st.median(dur), 2),
                   "volume": {"min": round(min(vols), 3), "max": round(max(vols), 3)}, "files": names[:12]})
    out["audio"] = at
    muted_main = sum(1 for s in segs if s.get("volume", 1.0) == 0)
    out["audio_notes"] = {"main_video_muted_pieces": muted_main}

    # --- effects / filters ---
    m = d["materials"]
    out["effects"] = {k: len(m.get(k, [])) for k in ("video_effects", "effects", "filters", "adjust_masks", "masks", "material_animations", "audio_fades") if m.get(k)}
    return out


def summary(x):
    L = [f"runtime {x['runtime_s']}s ({x['runtime_s']/60:.2f} min), canvas {x['canvas'][0]}x{x['canvas'][1]} @ {x['fps']}fps"]
    mm = x["main"]
    L.append(f"main: {mm['pieces']} pieces, {mm['cuts_per_min']} cuts/min, piece median {mm['piece_s']['median']}s (p10 {mm['piece_s']['p10']}, p90 {mm['piece_s']['p90']})")
    for k, v in mm["sources"].items():
        L.append(f"  source {k}: {v['pieces']} pieces, kept {v['used_s']}s of {v['source_s']}s ({v['kept_pct']}%)")
    r = x["reframe"]
    L.append(f"reframe: {r['punch_in_pieces']} punch-ins, {r['keyframed_zoom_pieces']} keyframed zoom pieces, zoomed {r['zoomed_pct_of_runtime']}% of runtime")
    L.append(f"transitions: {len(x['transitions'])} " + ", ".join(f"{t['name']}@{t['at_s']}s" for t in x["transitions"]))
    o = x["overlays"]
    L.append(f"graphics: {o['graphics']} ({o['graphics_per_min']}/min, {o['graphics_first_60s']} in first 60s), median on screen {o['graphic_on_screen_s']['median']}s, video overlays {o['video_overlays']}")
    L.append(f"text layers: {x['text']['layers']}")
    for a in x["audio"]:
        L.append(f"audio {a['kind']}: {a['clips']} clips, median {a['median_len_s']}s, volume {a['volume']['min']}-{a['volume']['max']}")
    L.append(f"main video muted pieces: {x['audio_notes']['main_video_muted_pieces']}; effects/filters: {x['effects']}")
    return "\n".join(L)


if __name__ == "__main__":
    d, p = load(sys.argv[1])
    x = analyze(d)
    print(summary(x))
    if "--out" in sys.argv:
        Path(sys.argv[sys.argv.index("--out") + 1]).write_text(json.dumps(x, indent=1), encoding="utf-8")
