# Music cues for "3 AI Setups Challenge, Video 1", exec'd by gen_edl.py (uses bed, cut_at, KEEPS, TOTAL, end_of).
# The series' own ElevenLabs Music originals (audio/music-provenance.md): Claude in Chrome couldn't load ElevenLabs
# (the page never finished loading in the automation tab), so no new bed was generated for this video.
# Targets are the bed level in the GAPS; mix_stem.py ducks the chain ~6 dB under his voice (sidechain on qa_voice.wav).
# Each bed change sits on a section transition, so its whoosh masks the crossfade.
def chain(names, at, end, target, fi=0.8, fo=1.0, offs=None):
    t, k = at, 0
    while end - t > 1.0 and k < len(names):
        off = (offs or {}).get(k, 0.0)
        c = bed(names[k], t, end, target, offset=off)
        c["fade_in"] = fi if k == 0 else 1.5
        c["fade_out"] = 1.5
        if c["duration"] < 2.0:
            break
        music.append(c); t += c["duration"] - 1.5 if t + c["duration"] < end - 0.1 else c["duration"]; k += 1
    if music:
        music[-1]["fade_out"] = fo
o = lambda i: cut_at(KEEPS[i][0], cold=(KEEPS[i][2] == "cold"))
e = lambda i: cut_at(end_of(i), cold=(KEEPS[i][2] == "cold"))
t_hook, t_kit, t_obs, t_back, t_mont, t_six, t_site, t_prices, t_out = o(4), o(5), o(8), o(9), o(12), o(16), o(17), o(20), o(21)
t_herm, t_grok = o(18), o(19)
chain(["punch"], 0.0, t_hook, -25.0, fi=0.2, fo=0.35, offs={0: 4.0})
chain(["intro"], t_hook - 0.2, t_kit + 0.4, -27.0, fi=0.6, fo=0.9)
chain(["window"], t_kit - 0.3, t_obs + 0.4, -29.0, fi=0.8, fo=0.9)
chain(["canvas", "termb"], t_obs - 0.3, t_back + 0.4, -30.0, fi=0.8, fo=0.9)
chain(["terma"], t_back - 0.3, t_mont + 0.3, -29.0, fi=0.8, fo=0.6)
chain(["punch"], t_mont - 0.4, t_six + 0.3, -23.5, fi=0.4, fo=0.6, offs={0: 18.0})     # the time-lapse: no voice, lifted
chain(["recap"], t_six - 0.3, t_site + 0.4, -28.0, fi=0.8, fo=0.9)
chain(["canvasa"], t_site - 0.4, t_herm + 0.4, -30.0, fi=0.9, fo=0.9)
chain(["termb"], t_herm - 0.3, t_grok + 0.4, -30.0, fi=0.8, fo=0.9, offs={0: 54.0})
chain(["window", "terma"], t_grok - 0.3, t_prices + 0.3, -30.0, fi=0.8, fo=0.9, offs={1: 170.0})
chain(["recap", "outro"], t_prices - 0.3, TOTAL, -28.0, fi=0.8, fo=3.0, offs={0: 60.0})
