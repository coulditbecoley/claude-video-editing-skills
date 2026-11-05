# Music cues for Asgard Agents Day 30, exec'd by gen_edl.py (uses fill, cut_at, find, KEEPS, TOTAL).
# The series' own ElevenLabs beds (provenance in audio/music-provenance.md); the never-used variants carry the
# hook (Autonomous Division), the Window (Nordic Dashboard Ambient) and the outro (Nordic Dawn Agent).
# A new bed per section; the punchline "No, not yet." cuts the music dead under the impact, back on "Stick around".
t_canvas = cut_at(KEEPS[3][0])                                         # into the Obsidian canvas
t_dead = cut_at(find("no not yet", 122.9)[0]) - 0.08                   # the punchline
t_back = cut_at(find("stick around", 125.0)[0]) - 0.05
t_window = cut_at(KEEPS[4][0])                                         # the Agents Window
t_x = cut_at(KEEPS[6][0])                                              # X, Pump.fun, YouTube
t_out = cut_at(KEEPS[9][0])                                            # talking-head outro
music += fill(0.0, t_canvas, ["intro"], target=-30.0, fade_out=0.8)
music += fill(t_canvas, t_dead, ["canvas"], fade_out=0.0)
music += fill(t_back, t_window, ["canvas", "term"], fade_out=0.8, fade_in=0.6)
music += fill(t_window, t_x, ["window", "window2"], fade_out=0.8)
music += fill(t_x, t_out, ["recap"], target=-31.5, fade_out=1.2)
music += fill(t_out, TOTAL, ["outro"], target=-28.5, fade_out=3.0)
