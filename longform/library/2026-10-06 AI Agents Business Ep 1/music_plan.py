# Music cues for AI Agents Business Ep 1, exec'd by gen_edl.py (uses fill, cut_at, find, KEEPS, TOTAL, T_* edges).
t_term = cut_at([k for k in KEEPS if k[2] == "screen"][0][0])                          # into the terminal
t_dead = cut_at(find("affirm nogo", 1249)[0])         # round 5 "Codex verdict is a firm no-go": music dies, impact
t_back = cut_at(find("the real problems", 1300)[0])     # v2: the web-review line is cut; music returns on "the real problems"
t_clip = cut_at(KEEPS[[k[1] for k in KEEPS].index(T_TERM_END) + 1][0])   # Paperclip
t_out = cut_at(KEEPS[-1][0])                          # talking-head outro
music += fill(0.0, t_term, ["intro"], target=-29.0, fade_out=1.0)
music += fill(t_term, t_dead, ["termA", "termB"], fade_out=0.0)
music += fill(t_back, t_clip, ["termB", "termA"], fade_out=1.0)
music += fill(t_clip, t_out, ["recap"], target=-29.0, fade_out=1.5)
music += fill(t_out, TOTAL, ["outro"], target=-28.5, fade_out=3.0)
