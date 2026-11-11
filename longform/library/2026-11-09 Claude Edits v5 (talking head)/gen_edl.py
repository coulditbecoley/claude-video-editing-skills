"""v5 step 2: build edit.edl.json from base.edl.json (the audited v4 cut), work/v5_segments.json and graphics/slots.json
(both written by resolve.py), the rendered scenes in D:/edits/claude-edits-v5/gfx (manifest.json) and the ElevenLabs
kit in audio/sfx/n. Sounds inside a scene come from the scene's own <script id="cues"> list."""
import json, os, re

ROOT = os.path.abspath('.').replace('\\', '/')
GFX = 'D:/edits/claude-edits-v5/gfx'
CW, CH = 3840, 2160                       # canvas (never name these W, H: lessons 2026-09-25 #3)
FPS = 60
base = json.load(open('base.edl.json'))
order = json.load(open('work/v5_segments.json'))
slots = json.load(open('graphics/slots.json'))['slots']
man = json.load(open(f'{GFX}/manifest.json')) if os.path.exists(f'{GFX}/manifest.json') else {}
TOTAL = order['total']
byname = {}
for s in base['segments']:
    byname[s.get('id') or ('cold' if 'cold' in s.get('src', '') else 'duck' if s.get('kind') == 'insert' else s['kind'])] = s

# ---- segments in v5 order, plain framing: alternate 1.0 / 1.10 on talking-head cuts, reset at each chapter ----
full = sorted([s for s in slots if s['kind'] in ('full', 'launch', 'over')], key=lambda s: s['start'])
covered = lambda a, b: any(f['start'] - 1e-6 <= a and b <= f['start'] + f['dur'] + 1e-6 for f in full)
S, flip, prev_ch = [], 0, None
for it in order['items']:
    s = dict(byname[it['name']]); s.pop('transition', None); s.pop('frame', None)
    if s.get('kind') == 'talk':
        ch = re.match(r'[a-z]+', it['name']).group(0)[0]
        d = it['t1'] - it['t0']
        if ch != prev_ch: flip = 0
        elif d >= 1.2 and not covered(it['t0'], it['t1']): flip ^= 1      # never change framing under a scene: it shows at the exit
        if flip: s['frame'] = {'scale': 1.10, 'x': 0.0, 'y': 0.0}
        prev_ch = ch
    S.append(s)

images, sfx = [], []
N = lambda n: f'{ROOT}/audio/sfx/n/{n}.wav'
VOL = {'tick': .22, 'light': .30, 'pop': .16, 'count': .22, 'type': .16, 'draw': .20, 'strike': .26, 'wrong': .24, 'right': .24, 'impact': .34,
       'slide': .22, 'scan': .16, 'whoosh_in': .20, 'whoosh_out': .12, 'swell': .26, 'riser': .16}
q = lambda t: round(round(t * FPS) / FPS, 4)


def cue(name, t, vol=None):
    if 0 <= t < TOTAL - 0.2:
        sfx.append({'path': N(name), 'start': q(t), 'volume': vol if vol is not None else VOL[name]})


missing = []
for s in slots:
    if s['start'] + s['dur'] >= TOTAL - 0.01: s['noexit'] = True      # the last scene holds under the closing fade to black (audit/R1.md G71)
    sid = s['id'] if s['kind'] != 'launch' else f"launch_{s['n']}"
    m = man.get(sid)
    if not m or m['frames'] != s['frames']:        # not rendered, or rendered for an older slot length
        missing.append(sid); continue
    im = {'path': f'{GFX}/{sid}.mp4' if not m['alpha'] else f'{GFX}/{sid}/000.png', 'start': s['start'], 'duration': s['dur'], 'x': CW // 2, 'y': CH // 2,
          'scale': 1.0, 'pop': False, 'seq': {'dir': f'{GFX}/{sid}', 'frames': m['frames']},
          'kind': 'accent' if s['kind'] in ('chips', 'launch') else 'card'}
    if m.get('clip'):                              # a clipped overlay: the PNG is only that box, so centre it there
        c = m['clip']; im['x'] = int(c['x'] + c['w'] / 2); im['y'] = int(c['y'] + c['h'] / 2)
    if s.get('noexit'): im['noexit'] = True
    if s.get('noenter') or m['alpha']: im['noenter'] = True
    images.append(im)
    # sounds
    if s['kind'] == 'chips':
        for c in s['chips']: cue('pop', s['start'] + c['t'] + 0.05)
    elif s['kind'] == 'launch':
        cue('swell', s['start'] + 0.05); cue('light', s['start'] + 0.95)
    else:
        if not s.get('noenter'): cue('whoosh_in', s['start'] - 0.12)
        else: cue('slide', s['start'], 0.14)
        if not s.get('noexit') and s['kind'] == 'full': cue('whoosh_out', s['start'] + s['dur'] - 0.34)
        html = f'graphics/scenes/{sid}.html'
        mm = re.search(r'<script type="application/json" id="cues">(.*?)</script>', open(html, encoding='utf-8').read(), re.S) if os.path.exists(html) else None
        for c in (json.loads(mm.group(1)) if mm else []):
            if c['s'] in VOL and 0.25 < c['t'] < s['dur'] - 0.3: cue(c['s'], s['start'] + c['t'])
    # an insert shown through a hole: scale the insert's picture into the hole
    if s['kind'] == 'over' and m.get('hole'):
        h = m['hole']; sc = h['w'] / CW
        seg = S[[i for i, it in enumerate(order['items']) if it['name'] == s['insert']][0]]
        seg['frame'] = {'scale': round(sc, 5), 'x': round((h['x'] + h['w'] / 2 - CW / 2) / (CW / 2), 5), 'y': round(-(h['y'] + h['h'] / 2 - CH / 2) / (CH / 2), 5)}
# one sound per moment: drop a cue within 90 ms of a louder one
sfx.sort(key=lambda x: x['start'])
keep = []
for c in sfx:
    if keep and c['start'] - keep[-1]['start'] < 0.09:
        if c['volume'] > keep[-1]['volume']: keep[-1] = c
        continue
    keep.append(c)
sfx = keep
# no kit sound over an insert: it plays its own soundtrack (audit/PRERENDER R1.md #1)
INS = [(it['t0'], it['t1']) for it in order['items'] if byname[it['name']].get('kind') == 'insert']
sfx = [c for c in sfx if not any(a - 0.8 < c['start'] < b for a, b in INS)]
# the inserts' own audio
for it in order['items']:
    seg = byname[it['name']]
    if seg.get('kind') == 'insert':
        wav = seg['src'].rsplit('.', 1)[0] + '.wav'
        assert os.path.exists(wav), wav
        sfx.append({'path': wav, 'start': q(it['t0']), 'volume': 1.0})
images.append({'path': f'{ROOT}/graphics/assets/black-4k.png', 'start': round(TOTAL - 0.55, 3), 'duration': 0.55, 'x': CW // 2, 'y': CH // 2, 'pop': 'fade', 'kind': 'accent'})
music = []
if os.path.exists('audio/music-stem.wav'):
    music = [{'path': f'{ROOT}/audio/music-stem.wav', 'at': 0.0, 'start_offset': 0.0, 'duration': round(TOTAL, 3), 'volume': 1.0}]
edl = {'project': 'Claude Edits My YouTube Videos v5', 'source': base['source'], 'resolution': [CW, CH], 'fps': FPS, 'voice': base['voice'],
       'voice_fade': base.get('voice_fade', 0.03), 'output': 'Claude Edits My YouTube Videos v5 - 4K60.mp4', 'segments': S, 'images': images, 'sfx': sfx,
       'music': music, 'words': f'{ROOT}/work/lint_words.json'}
json.dump(edl, open('edit.edl.json', 'w'), indent=1)
cov = sum(f['dur'] for f in full)
print(f'{len(S)} segments, {TOTAL:.3f}s, {len(images)} images, {len(sfx)} sfx, full-screen {100 * cov / TOTAL:.1f}%; scenes not rendered yet: {missing or "none"}')
