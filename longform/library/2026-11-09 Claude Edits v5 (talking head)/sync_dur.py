"""Set each built scene's data-dur to its slot (slots.json is the truth). Prints every change; a change over 3 frames needs the builder."""
import json, re, os
for s in json.load(open('graphics/slots.json'))['slots']:
    if s['kind'] not in ('full', 'over'): continue
    p = f"graphics/scenes/{s['id']}.html"
    if not os.path.exists(p): print('MISSING', s['id']); continue
    h = open(p, encoding='utf-8').read(); m = re.search(r'data-dur="([\d.]+)"', h)
    if abs(float(m.group(1)) - s['dur']) > 1e-4:
        print(f"{s['id']}: {m.group(1)} -> {s['dur']:.4f}{'  CHECK TIMING' if abs(float(m.group(1)) - s['dur']) > 0.051 else ''}")
        open(p, 'w', encoding='utf-8').write(h.replace(m.group(0), f'data-dur="{s["dur"]:.4f}"', 1))
