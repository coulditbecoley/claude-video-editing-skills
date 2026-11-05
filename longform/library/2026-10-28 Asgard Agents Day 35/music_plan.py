# Music cues for Asgard Agents Day 35, exec'd by gen_edl.py (uses bed, cut_at, find, KEEPS, TOTAL, T_COLD_END).
# Coley (2026-10-28): "a slight background music, but not too loud to where it overtakes the speaker... nice and
# comforting". So the beds sit about 20 dB under the voice (-34 LUFS against -14) through the body, a little higher
# only where he isn't over a busy screen (-31 in the hook and outro). The series' own ElevenLabs originals, the calmer
# ones (provenance in audio/music-provenance.md).
# Round 2 (Codex #8): the cold-open bed stops dead on "$741.12" under the impact, the money line plays in silence and
# the riser carries it into the White Flash; each bed change sits on a chapter boundary (its chip's swish masks the
# fade), so no section dips mid-way.
def cue(name, at, end, target, fi=1.0, fo=1.0, offset=None):
    c = bed(name, at, end, target, offset=offset)
    c["fade_in"], c["fade_out"] = fi, fo
    return c
T_ = lambda ph, h, cold=False: cut_at(find(ph, h)[0], cold)
t_741 = T_("741", 632.1, cold=True) - 0.05                  # the money: the bed stops dead here
t_hook = cut_at(KEEPS[2][0])
t_canvas = cut_at(KEEPS[3][0])
t_ch3 = T_("here are some mistakes", 271.9)                 # 03 they caught their own mistakes
t_ch5 = T_("up next here we go", 547.8)                     # 05 what's next
t_window = cut_at(KEEPS[4][0])
t_world = cut_at(KEEPS[5][0])
t_world2 = T_("lets go and see what everyone else is", 840.9)
t_biz = cut_at(KEEPS[6][0])
t_out = cut_at(KEEPS[8][0])
music += [cue("cold", 0.0, t_741, -30.0, fi=0.4, fo=0.0),
          cue("hook", t_hook, t_canvas, -31.0, fi=0.6, fo=0.8),
          cue("canvas", t_canvas, t_ch3, -34.0),
          cue("canvas2", t_ch3, t_ch5, -34.0),
          cue("canvas", t_ch5, t_window, -34.0, offset=172.0, fo=0.8),
          cue("window", t_window, t_world, -34.0, fo=0.6),
          cue("world", t_world, t_world2, -33.0),
          cue("world2", t_world2, t_biz, -33.0, fo=0.8),
          cue("biz", t_biz, t_out, -34.0),
          cue("outro", t_out, TOTAL, -31.0, fo=3.0)]
