# Music cues for Asgard Agents Day 20, exec'd by gen_edl.py (uses fill, cut_at, find, KEEPS, TOTAL).
t_screen = cut_at(FIRST_SCREEN)                                   # into the canvas
t_dead = cut_at(find("no longer creating meme coins", 280.6)[0])     # the punchline: music dies, impact
t_back = cut_at(find("theyre going to live on their ecosystem token", 282.5)[0])
t_site = cut_at(PAPERROWS_CLICK)                                  # PaperRows: the bright launch bed
t_win2 = cut_at(find("so lets get back here to the agent window", 666)[0])
t_out = cut_at(OBS_TO_CAM)                                        # talking-head outro
music += fill(0.0, t_screen, ["day20"], target=-30.5, fade_out=1.0)
music += fill(t_screen, t_dead, ["termA"], fade_out=0.0)
music += fill(t_back, t_site, ["termB"], fade_out=0.8)
music += fill(t_site, t_win2, ["recap"], target=-32.0, fade_out=0.8)
music += fill(t_win2, t_out, ["termA"], fade_out=1.5)
music += fill(t_out, TOTAL, ["outro"], target=-29.0, fade_out=3.0)
