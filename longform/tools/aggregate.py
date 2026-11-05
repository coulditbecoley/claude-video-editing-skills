"""Roll every library/*/metrics.json into profile/metrics.json (one row per video).

usage: python tools/aggregate.py   (from the VideoEditor folder)
"""
import json
import pathlib

vids = []
for m in sorted(pathlib.Path("library").glob("*/metrics.json")):
    x = json.loads(m.read_text(encoding="utf-8"))
    vids.append({"video": m.parent.name, "runtime_s": x["runtime_s"], "cuts_per_min": x["main"]["cuts_per_min"],
                 "piece_median_s": x["main"]["piece_s"]["median"], "zoomed_pct": x["reframe"]["zoomed_pct_of_runtime"],
                 "transitions": len(x["transitions"]), "graphics_per_min": x["overlays"]["graphics_per_min"],
                 "graphics_first_60s": x["overlays"]["graphics_first_60s"], "text_layers": x["text"]["layers"]})
pathlib.Path("profile/metrics.json").write_text(json.dumps({"videos": vids}, indent=1), encoding="utf-8")
print(f"{len(vids)} videos -> profile/metrics.json")
