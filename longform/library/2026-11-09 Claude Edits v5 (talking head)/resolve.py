"""v5 step 1: order the pieces, map every kept word onto the v5 timeline, and resolve graphics/beats.py into slots.
Writes work/v5_segments.json, work/v5_words.json, graphics/slots.json and graphics/SPEC_<grp>.md (builder specs).
Run again after any change to beats.py or base.edl.json. gen_edl.py reads these files."""
import json, os, re, sys
sys.path.insert(0, 'graphics')
from beats import BEATS

FPS = 60
q = lambda t: round(t * FPS) / FPS                     # everything on the 60 fps grid
base = json.load(open('base.edl.json'))
SEGS = base['segments']
dur = lambda s: s['out'] - s['in']
import re as _re
sid = lambda s: _re.sub(r'(?<=\d)[ab]$', '', s.get('id', '').split('.')[0])

# ---- v5 order of the opening: a2, a6, cold insert, a1, a3, a4, a4b, a5, then everything else as in v4 ----
cold = [s for s in SEGS if s.get('kind') == 'insert' and 'cold' in s.get('src', '')]
grp = lambda *ids: [s for s in SEGS if sid(s) in ids]
opening = grp('a2') + grp('a6') + cold + grp('a1') + grp('a3') + grp('a4') + grp('a4b') + grp('a5')
used = {id(s) for s in opening}
ORDER = opening + [s for s in SEGS if id(s) not in used]
assert len(ORDER) == len(SEGS)
t = 0.0
TL = []
for s in ORDER:
    name = s.get('id') or ('cold' if s in cold else 'duck' if s.get('kind') == 'insert' else s.get('kind'))
    TL.append({'name': name, 't0': round(t, 4), 't1': round(t + dur(s), 4), 'seg': s}); t += dur(s)
TOTAL = t
json.dump({'total': TOTAL, 'items': [{k: v for k, v in it.items() if k != 'seg'} | {'in': it['seg']['in'], 'out': it['seg']['out'], 'kind': it['seg'].get('kind')} for it in TL]},
          open('work/v5_segments.json', 'w'), indent=1)
T0 = {it['name']: it['t0'] for it in TL}
SEGIN = {it['name']: it['seg']['in'] for it in TL}

# ---- words on the v5 timeline ----
W = []
TALK = [it for it in TL if it['seg'].get('kind') == 'talk']
for w in json.load(open('work/words_timeline.json'))['words']:
    mid = (w['src_s'] + w['src_e']) / 2
    hit = [it for it in TALK if it['seg']['in'] - 0.03 <= mid <= it['seg']['out'] + 0.03 and it['name'].startswith(w['seg'].split('.')[0][:2])]
    if not hit:
        continue                                   # trimmed away (audit/V5 JOINS.md, V5 SWEEP.md)
    it = hit[0]; off = it['t0'] - it['seg']['in']
    W.append({'w': w['w'], 's': round(max(w['src_s'], it['seg']['in']) + off, 3), 'e': round(min(w['src_e'], it['seg']['out']) + off, 3), 'seg': it['name']})
W.sort(key=lambda w: w['s'])
json.dump(W, open('work/v5_words.json', 'w'))
norm = lambda x: re.sub(r"[^a-z0-9$']", '', x.lower())
NW = [norm(w['w']) for w in W]


def find(phrase, after=0, before=None):
    """index range (i, j) of the phrase's words, first match at or after word index `after`"""
    toks = [norm(x) for x in phrase.split()]
    for i in range(after, (before or len(W)) - len(toks) + 1):
        if NW[i:i + len(toks)] == toks:
            return i, i + len(toks) - 1
    raise KeyError(f'phrase not found after word {after}: {phrase!r}')


def item(name):
    return [it for it in TL if it['name'] == name][0]


# ---- resolve beats ----
SLOTS = []
cur = 0
LAUNCH = 3.6
for b in BEATS:
    s = {'id': b['id'], 'kind': b['kind'], 'acc': b.get('acc', 'gold'), 'grp': b.get('grp'), 'brief': b.get('brief', ''), 'ins': b.get('ins', [])}
    if b['kind'] == 'launch':
        i, _ = find(b['before'], cur)
        s.update(start=q(W[i]['s'] - 0.35), dur=LAUNCH, n=b['n'], scene=f"launch@{b['n']}")
    elif b['a'].startswith('@'):
        it = item(b['a'][1:]); s.update(start=q(it['t0']), dur=q(it['t1'] - it['t0']), insert=it['name'])
    else:
        i, _ = find(b['a'], cur)
        if b['b'] == '@end':
            end = TOTAL
        else:
            _, j = find(b['b'], i); end = W[j]['e'] + b.get('tail', 0.2 if b['kind'] == 'full' else 0.7); cur = j
        st = W[i]['s'] - b.get('lead', 0.15 if b['kind'] == 'full' else 0.0)
        s.update(start=q(st), dur=q(end - st), i=i)
        if b['kind'] == 'chips':
            s['chips'] = []
            for ph, text in b['chips']:
                k, _ = find(ph, i)
                s['chips'].append({'t': round(max(0.05, W[k]['s'] - 0.12 - s['start']), 3), 'text': text})
    SLOTS.append(s)

# ---- tidy the full-screen layer: launchers push the scene after them; near-gaps close; no face flashes ----
full = [s for s in SLOTS if s['kind'] in ('full', 'launch', 'over')]
full.sort(key=lambda s: s['start'])
for a, b in zip(full, full[1:]):
    ea = a['start'] + a['dur']
    if b['start'] < ea:                       # overlap: the later scene starts when the earlier one ends
        if a['kind'] == 'launch' or b['kind'] != 'launch':
            b['dur'] = q(b['start'] + b['dur'] - ea); b['start'] = q(ea)
        else:                                 # a scene running into a launcher: the scene ends at the launcher
            a['dur'] = q(b['start'] - a['start'])
    elif b['start'] - ea < 1.5:               # a face flash under 1.5 s: hold the earlier scene to the next one
        a['dur'] = q(b['start'] - a['start'])
for a, b in zip(full, full[1:]):
    if abs(a['start'] + a['dur'] - b['start']) < 1e-6:
        a['noexit'] = True; b['noenter'] = True
# chips never sit under a full-screen scene: trim or drop
for c in [s for s in SLOTS if s['kind'] == 'chips']:
    for f in full:
        f0, f1 = f['start'], f['start'] + f['dur']
        if c['start'] < f1 and c['start'] + c['dur'] > f0:
            if c['start'] >= f0: c['start'] = q(f1)
            else: c['dur'] = q(f0 - c['start'] - 0.05)
    c['chips'] = [x for x in c.get('chips', []) if x['t'] < c['dur'] - 1.2]
ch = sorted([s for s in SLOTS if s['kind'] == 'chips'], key=lambda s: s['start'])
for a, b in zip(ch, ch[1:]):                      # two chip rows never share the lower third
    if a['start'] + a['dur'] > b['start'] - 0.2: a['dur'] = q(b['start'] - 0.2 - a['start'])
for s in SLOTS:
    s['frames'] = round(s['dur'] * FPS)
    s['words'] = [[w['w'], round(w['s'] - s['start'], 2)] for w in W if s['start'] - 4.0 <= w['s'] < s['start'] + s['dur'] + 0.5]
    assert s['dur'] > 1.4 or s['kind'] == 'chips', (s['id'], s['dur'])
json.dump({'total': TOTAL, 'slots': SLOTS}, open('graphics/slots.json', 'w'), indent=1)

# ---- report + builder specs ----
cov = sum(s['dur'] for s in full)
print(f'total {TOTAL:.3f}s  full-screen {cov:.1f}s = {100 * cov / TOTAL:.1f}%  slots {len(SLOTS)}')
edges = sorted([(s['start'], s['start'] + s['dur'], s['id']) for s in full])
prev = 0.0
for a, b_, n in edges:
    if a - prev > 20: print(f'  face-only {prev:.1f} to {a:.1f} ({a - prev:.1f}s) before {n}')
    prev = b_
for s in SLOTS:
    print(f"{s['start']:7.2f} {s['dur']:6.2f} {s['kind']:6} {s['id']}{' noexit' if s.get('noexit') else ''}")


def narr(s):
    out, line = [], ''
    for w, t_ in s['words']:
        line += f'{w}[{t_:.1f}] '
        if len(line) > 110: out.append(line); line = ''
    return '\n'.join('    ' + l for l in out + [line])


for g in sorted({s['grp'] for s in SLOTS if s.get('grp') and s['grp'] != 'done'}):
    L = [f'# Scene specs, group {g}', '', 'Read `SCENES.md` first. Scene-local seconds. `word[t]` = the moment that word starts (negative = before the scene, '
         'spoken under the previous shot).', '']
    for s in [s for s in SLOTS if s.get('grp') == g]:
        ins = ', '.join(f'`D:\\edits\\claude-edits\\job\\inserts\\{i}`' for i in s['ins']) or 'none'
        L += [f"## {s['id']}  (`scenes/{s['id']}.html`)", f"- `data-dur=\"{s['dur']:.4f}\"` ({s['frames']} frames), accent: {s['acc']}, kind: {s['kind']}"
              + (', ALPHA overlay (`<body class="alpha" data-nopush="1">`) with a `.hole`' if s['kind'] == 'over' else ''),
              f'- inserts: {ins}', '- build: ' + ' '.join(s['brief'].split()), '- narration:', narr(s), '']
    open(f'graphics/SPEC_{g}.md', 'w', encoding='utf-8').write('\n'.join(L))
