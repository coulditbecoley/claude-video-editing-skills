# Music cues for AI Agents Business Ep 3, exec'd by gen_edl.py (uses fill, cut_at, find, KEEPS, TOTAL).
# The series' own ElevenLabs beds (provenance in audio/music-provenance.md), the variants neither Day 30 nor Ep 2 used
# where there is one. A new bed per section; the cold open's punchline ("four customers") cuts the music dead under the
# impact, and the hook brings it back after the White Flash.
t_dead = cut_at(find("four customers", 317.4)[0], cold=True) - 0.08    # the punchline
t_hook = cut_at(KEEPS[COLD_N][0])                                       # the hook, right after the White Flash
t_canvas = cut_at(KEEPS[4][0])                                          # into the Obsidian canvas
t_window = cut_at(KEEPS[5][0])                                          # the Agents Window, the site, Excel, feedback
t_out = cut_at(KEEPS[9][0])                                             # talking-head outro
music += fill(0.0, t_dead, ["intro"], target=-30.5, fade_out=0.0)
music += [dict(c, start_offset=round(c["start_offset"] + 14.0, 3)) for c in fill(t_hook, t_canvas, ["intro"], target=-30.5, fade_out=0.8, fade_in=0.4)]
music += fill(t_canvas, t_window, ["canvas"], target=-32.0, fade_out=0.8)
music += fill(t_window, t_out, ["demo"], target=-32.0, fade_out=1.2)
music += fill(t_out, TOTAL, ["outro"], target=-28.5, fade_out=3.0)
