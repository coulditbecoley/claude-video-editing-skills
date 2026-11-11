"""Slots are FROZEN as the builders timed them (work/slots.before_a2.json = resolve.py output of 19:30). Later cut
changes are applied as time shifts, not by re-resolving (a rebuilt transcript moves word starts by up to 0.6 s, which
would silently desync every scene's reveals). Each entry: (timeline time of the cut in the frozen timeline, seconds removed)."""
import json
FPS = 60; q = lambda t: round(t * FPS) / FPS
CUTS = [(13.75, 0.87),            # a2.0 out 26.370 -> 25.500: the "uh" after "CapCut" (audit/V5 JOINS.md)
        # audit/V5 SWEEP.md, 8 fillers (its v5 times + 0.87 = frozen-timeline times)
        (84.09, 0.300), (246.79, 0.410), (317.14, 0.300), (403.49, 0.797), (501.09, 0.400), (508.70, 0.290), (639.90, 0.930), (731.11, 0.532),
        (441.24, 0.555),
        (349.32, 0.072)]         # f2b.0a removed, 'more [you] shorts' (audit/V5 LINT CUTS.md)
#         # g7 split, 'uh, it would' (audit/V5 VOICE FINAL.md): the tail of s28_claim
d = json.load(open('work/slots.before_a2.json')); W = json.load(open('work/v5_words.json'))
total = json.load(open('work/v5_segments.json'))['total']
for s in d['slots']:
    a, b = s['start'], s['start'] + s['dur']
    a0 = a
    for t, k in sorted(CUTS):
        if a0 >= t - 1e-6: a -= k; b -= k
        elif s['start'] + s['dur'] > t:         # the cut is inside this slot: it gets shorter
            b -= k; print(f"  cut inside {s['id']} at local {t - a0:.2f} s, -{k}")
            for c in s.get('chips', []):
                if c['t'] > t - a0: c['t'] = round(c['t'] - k, 3)
    s['start'], s['dur'] = q(a), q(b - a); s['frames'] = round(s['dur'] * FPS)
    s['words'] = [[w['w'], round(w['s'] - s['start'], 2)] for w in W if s['start'] - 4.0 <= w['s'] < s['start'] + s['dur'] + 0.5]
last = max(d['slots'], key=lambda s: s['start']); last['dur'] = q(total - last['start']); last['frames'] = round(last['dur'] * FPS)
ch = sorted([s for s in d['slots'] if s['kind'] == 'chips'], key=lambda s: s['start'])
for a, b in zip(ch, ch[1:]):               # two chip rows never overlap (audit/PRERENDER R1.md #5)
    if a['start'] + a['dur'] > b['start']: a['dur'] = q(b['start'] - a['start']); a['frames'] = round(a['dur'] * FPS); print('  chip clamp', a['id'], a['dur'])
d['total'] = total
json.dump(d, open('graphics/slots.json', 'w'), indent=1)
full = [s for s in d['slots'] if s['kind'] in ('full', 'launch', 'over')]
print(f"total {total:.3f}  full-screen {100 * sum(s['dur'] for s in full) / total:.1f}%  s01 {d['slots'][1]['dur']:.4f}")
