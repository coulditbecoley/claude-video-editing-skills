"""audio/music-stem.wav: stored ElevenLabs beds (Coley's originals, see audio/music-provenance.md) chained by chapter,
silent under the two demonstration inserts, sidechain-ducked on qa_voice_v5.wav. Re-run after ANY cut change."""
import json, subprocess, wave, numpy as np
SR = 48000
B = '~/Projects/Youtube/edits/2026-10-28 Recording 1133/audio/'
order = json.load(open('work/v5_segments.json')); TOTAL = order['total']
with wave.open('qa_voice_v5.wav') as w: qa = w.getnframes() / w.getframerate()
assert abs(qa - TOTAL) < 0.02, f'qa_voice_v5.wav is {qa:.3f}s but the EDL is {TOTAL:.3f}s: re-run verify_voice first'
_sl = {x['id']: x['start'] for x in json.load(open('graphics/slots.json'))['slots']}       # sections follow the chapters
SECTIONS = [(0.0, 'el-intro-b.mp3'), (_sl['c10_new'], 'el-window-b.mp3'), (_sl['s10_words'], 'el-canvas-a.mp3'), (_sl['launch_3'], 'el-canvas-b.mp3'),
            (_sl['launch_6'], 'el-canvas-a.mp3'), (_sl['launch_7'], 'el-window-b.mp3'), (_sl['s39_caps'] - 2.5, 'el-canvas-b.mp3'), (_sl['s44_github'] - 2.5, 'el-outro-b.mp3')]
def ld(p): return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-map', '0:a', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32).reshape(-1, 2)
n = int(TOTAL * SR); bed = np.zeros((n, 2), np.float32); X = int(2.0 * SR)          # 2 s crossfades between sections
for k, (st, fn) in enumerate(SECTIONS):
    en = SECTIONS[k + 1][0] if k + 1 < len(SECTIONS) else TOTAL
    a = max(0, int(st * SR) - (X // 2 if k else 0)); b = min(n, int(en * SR) + (X // 2 if k + 1 < len(SECTIONS) else 0)); L = b - a
    M = ld(B + fn); M = M / (np.sqrt(np.mean(M ** 2)) + 1e-9) * 0.05            # equal RMS per bed before the chain
    if len(M) < L: M = np.vstack([M] * int(np.ceil(L / len(M))))
    seg = M[:L].copy(); f = min(X, L // 2)
    seg[:f] *= np.linspace(0, 1, f)[:, None]; seg[-f:] *= np.linspace(1, 0, f)[:, None]
    bed[a:b] += seg
for it in order['items']:                                                          # the inserts play their own sound
    if it['kind'] == 'insert':
        a, b, g = int(it['t0'] * SR), int(it['t1'] * SR), int(0.3 * SR)
        bed[a - g:a] *= np.linspace(1, 0, g)[:, None]; bed[a:b] = 0; bed[b:b + g] *= np.linspace(0, 1, len(bed[b:b + g]))[:, None]
bed[-int(1.2 * SR):] *= np.linspace(1, 0, int(1.2 * SR))[:, None]
def wr(p, x):
    with wave.open(p, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())
wr('work/bed_raw.wav', bed)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'work/bed_raw.wav', '-af', 'loudnorm=I=-27:TP=-3:LRA=11', '-ar', str(SR), 'work/bed_norm.wav'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'work/bed_norm.wav', '-i', 'qa_voice_v5.wav', '-filter_complex',
                '[0:a][1:a]sidechaincompress=threshold=0.05:ratio=2.2:attack=40:release=450:knee=4:makeup=1,apad=whole_dur=%.4f[o]' % TOTAL,
                '-map', '[o]', '-t', '%.4f' % TOTAL, '-ar', str(SR), '-c:a', 'pcm_s24le', 'audio/music-stem.wav'], check=True)
json.dump({'total': TOTAL, 'sections': SECTIONS, 'beds_from': B}, open('audio/music-stem.json', 'w'), indent=1)
print('music-stem.wav written', TOTAL)
