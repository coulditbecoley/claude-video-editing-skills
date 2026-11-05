# Music cues for AI Agents Business Ep 2, exec'd by gen_edl.py (uses fill, cut_at, find, KEEPS, TOTAL, edges).
# The series' own ElevenLabs beds (Ep 1), so the show sounds like one show; provenance in Ep 1's audio folder.
t_screen = cut_at(FIRST_SCREEN)                                   # into the Agents Window
t_site = cut_at(SITE[0] + 0.7)                                    # the PaperRows reveal: the bright bed
t_canvas = cut_at(536.5)                                          # the Obsidian canvas
t_dead = cut_at(find("so they have one sale so far", 685.5)[0]) - 0.1   # the punchline: music dies, boom on "one sale"
t_back = cut_at(find("so the bank statement converter has converted", 688)[0])   # v2: a 3 s beat, not 7.5
t_out = cut_at(709.6)                                             # talking-head outro
music += fill(0.0, t_screen, ["intro"], target=-30.0, fade_out=1.0)
music += fill(t_screen, t_site, ["termA"], fade_out=0.8)
music += fill(t_site, t_canvas, ["recap", "termB"], target=-31.5, fade_out=1.0)
music += fill(t_canvas, t_dead, ["termB"], fade_out=0.0)
music += fill(t_back, t_out, ["termA"], fade_out=1.5)
music += fill(t_out, TOTAL, ["outro"], target=-28.5, fade_out=3.0)
