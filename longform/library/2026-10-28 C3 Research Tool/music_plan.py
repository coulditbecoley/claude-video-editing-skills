# Music cues for "C3 Research: the AI agents' token audit tool", exec'd by gen_edl.py (uses bed, cut_at, find, KEEPS,
# TOTAL, T_COLD_END, SCENE_AT). The series' own ElevenLabs Music originals (audio/music-provenance.md), one bed per
# stretch, each change on a chapter boundary where its transition whoosh masks the crossfade.
# Coley (Day 35): "slight... not too loud to where it overtakes the speaker... nice and comforting". These targets are
# the bed level in the GAPS; mix_stem.py then ducks the chain about 6 dB under his voice (sidechain on qa_voice.wav),
# so under speech the beds sit near -34 LUFS (20 dB under the -14 voice, as on Day 35) and swell back between lines
# and through the transitions. The cold open stops dead on "doesn't mean scam" under the impact; that line and its
# follow-up play in silence and the riser carries them into the White Flash.
def cue(name, at, end, target, fi=1.0, fo=1.0, offset=None):
    c = bed(name, at, end, target, offset=offset)
    c["fade_in"], c["fade_out"] = fi, fo
    return c
T_ = lambda ph, h, cold=False: cut_at(find(ph, h)[0], cold)
t_scam = T_("doesnt mean scam", 302.3, cold=True) - 0.05
t_hook = cut_at(KEEPS[2][0])
t_window = cut_at(KEEPS[3][0])
t_tool = cut_at(SCENE_AT[0])                       # the Swipe onto c3research.io
t_report = cut_at(SCENE_AT[3])                     # the Light Leaks into the ASGARD report
t_aff = cut_at(SCENE_AT[6])                        # the Swipe onto the affiliate page
t_out = cut_at(KEEPS[7][0])
music += [cue("cold", 0.0, t_scam, -26.5, fi=0.3, fo=0.0),
          cue("hook", t_hook - 0.3, t_window, -27.5, fi=0.5, fo=0.8),
          cue("window", t_window - 0.2, t_tool + 0.3, -29.0, fi=0.6, fo=0.7),
          cue("tool", t_tool - 0.2, t_report + 0.4, -29.0, fi=0.6, fo=0.9),
          cue("report", t_report - 0.3, t_aff + 0.3, -29.0, fi=0.8, fo=0.8),
          cue("aff", t_aff - 0.2, t_out + 0.2, -29.0, fi=0.6, fo=0.8),
          cue("outro", t_out - 0.3, TOTAL, -27.5, fi=0.6, fo=3.0)]
