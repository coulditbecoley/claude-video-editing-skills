# Graphics timing for AI Agents Business Ep 3 (the PaperRows update), exec'd by gen_edl.py.
# Every card lands on the word that names it: T(phrase, hint) is the VOICE second that phrase starts. hl() is a glowing
# gold box on the exact element he's naming (source px measured on the frame at that moment, probe/g/*.jpg via
# hlgrid.py), held only while the page is still. A box placed with a card stays silent so the moment gets one sound.
# Cards say only what the screen says (canvas, Agents Window, site). Sounds: pop on stats, coin on money, swish on chips
# and slides, sparkle on logos, tick on boxes, impact once (the cold open's punchline), boom on the White Flash.
T = lambda phrase, hint: find(phrase, hint)[0]
TE = lambda phrase, hint: find(phrase, hint)[1]
span = lambda a, b, cold=False: round(cut_at(b, cold) - cut_at(a, cold), 3)

# ---- cold open: the new folder drop, the goal, the score so far -------------------------------------------------
t = T("were going to drag it on in here", 371.7)
img("cold-folder", t + 0.25, span(t + 0.25, KEEPS[0][1]) - 0.05, "low", cold=True, pop="in", sound="swish")
t = T("the goal is five paying customers", 248.4)
img("cold-goal", t + 0.1, span(t + 0.1, KEEPS[1][1]) - 0.05, *SLOT_TOP, cold=True, pop="in", sound="swish")
t_four = T("four customers", 317.4)
img("cold-four", t_four, span(t_four, KEEPS[2][1]) - 0.05, *SLOT_TOP, cold=True, pop="in", sound="impact")

# ---- hook (talking head): premise above his head, the five agents across his chest, nothing over the face ---------
t_h = T("five ai agents", 5.5)
t_end = TE("running their own business", 7.6)
img("hook-title", t_h, span(t_h, TE("what they have upgraded", 14.4)) + 0.3, 1920, 250, scale=0.86)
for k, n in enumerate(["odin", "thor", "loki", "mimir", "heimdall"]):
    t0 = t_h + 0.12 * k
    img(f"agent-{n}", t0, span(t0, t_end) + 0.8, 1080 + 420 * k, 1800, scale=0.85, sound=None)   # the title's pop covers the row (Codex #4: a second pop on the same frame doubled it)
img("card-paperrows", T("this business is the paperrows", 9.2), 3.4, 3760 - 980, 1080, scale=0.85, pop="slide_r", sound="sparkle")   # right of his head, clear of the title
img("logo-obsidian", T("come with me into obsidian", 15.4), 3.2, *TOP_R, pop="slide_r", sound="sparkle")

# ---- 01 how it works (the agents' canvas) --------------------------------------------------------------------------
img("flow-pdfcsv", T("they created a bank statement converter", 51.4), 3.8, "auto", scale=0.8)
img("chip-how", T("so how does it work", 65.0), 2.8, *TOP_L, pop="slide_l", sound="swish")
hl((1340, 726, 2370, 1522), 68.04, 2.6, sound=False, mt=68.2)   # re-measured once his scroll settles (66.8-68.0)
img("stat-banks", T("bank statements that are available", 68.1), 3.4)
t = T("the best part is it stays on your computer", 73.1) + 0.3
hl((1413, 706, 2448, 1506), 73.92, 3.4, sound=False, mt=74.1)   # settled frame
img("stat-never", t, 3.6)
hl((1486, 762, 2524, 1562), T("checked against the banks total", 90.6) + 0.3, 3.4)
t = T("if you want it you get a single file", 100.6) + 0.3
hl((1616, 850, 2438, 1486), t, 2.8, sound=False)
img("stat-five", t, 2.8, sound="coin")
img("stat-plan19", T("if you want to", 103.86) + 0.4, 3.8, sound="coin")
t = T("you can open your csv files", 116.7) + 0.3
hl((1306, 725, 2342, 1522), 119.12, 2.8, sound=False, mt=119.3)   # settled frame
img("apps", T("google sheets", 120.9), 3.4, "auto", scale=0.8, sound="sparkle")

# ---- 02 new: drop a whole folder -----------------------------------------------------------------------------------
img("chip-folder", T("and for the update", 127.9), 2.4, *TOP_L, pop="slide_l", sound="swish")
t = T("you can now drop in zip folders", 131.1) + 0.3
hl((1368, 922, 2406, 1770), t, 3.4, sound=False)
img("stat-fifty", t, 3.4, "low")
hl((1336, 820, 2376, 1668), T("everything stays in your browser", 146.9) + 0.3, 3.4)
img("stat-nothing", T("so all the checks are done", 153.4), 3.4)
hl((1448, 802, 2488, 1650), T("it does give you the free overview", 159.6) + 0.4, 3.4)
img("stat-failed", T("because if it fails", 167.4), 3.4)
hl((1394, 788, 2432, 1636), 173.40, 2.8)
t = T("and then you can download them", 176.2) + 0.3
img("stat-zip", t, 3.2)
hl((1478, 766, 2508, 1606), 178.15, 2.8, sound=False, mt=178.27)    # re-measured after his scroll (176.9-178.0)
t = T("this new update for the folder drop in", 186.8) + 0.3
hl((1060, 928, 2560, 1564), t, 3.8, sound=False)
img("stat-bookonly", t, 3.8, sound="coin")
hl((1088, 878, 2900, 1690), T("one bad file never blocks the rest", 201.3) + 0.3, 3.4)
hl((906, 802, 2798, 1600), T("if youre using paper rows on the phone", 215.3) + 0.3, 3.6)

# ---- 03 who runs it --------------------------------------------------------------------------------------------------
t = T("you guys know whos working", 227.9)
img("chip-who", t, 2.8, *TOP_L, pop="slide_l", sound="swish")
hl((968, 896, 3408, 1414), t + 0.4, 3.4, sound=False)
t = T("this is the stripe account", 239.3)
img("logo-stripe", t, 3.6, *TOP_R, pop="slide_r", sound="sparkle")
hl((898, 1094, 2398, 1466), t + 0.3, 3.6, sound=False)
t = T("the goal is five paying customers", 248.3) + 0.3
hl((1232, 1112, 2732, 1482), t, 3.2, sound=False)
img("cold-goal", t, 3.2)

# ---- 04 the Agents Window (punch-ins; boxes map through them) -------------------------------------------------------
img("chip-window", KEEPS[5][0] + 1.3, 2.8, *TOP_L, pop="slide_l", sound="swish")
img("stat-agentrun", T("i do not do anything", 285.6), 4.2)
img("site-card", T("if you want to come to this window", 292.9) + 0.6, 3.2, 1920, 330, scale=0.85, pop="slide_down", sound="swish")
t = T("so if you want to get a sponsorship down here", 301.9) + 0.3
hl((48, 1940, 1750, 2056), t, 3.2, sound=False, mt=304.07)   # measured on the settled frame (his hover glows the tile)
img("stat-sponsor", t, 3.2)
hl((1206, 1200, 2000, 1890), T("as you can see right now so far", 315.0) + 0.3, 3.6)
img("stat-four", T("four customers", 317.4), 3.4, sound="coin")
t = T("you can see their total income at the top here", 327.7) + 0.3
hl((1336, 44, 1640, 176), t, 3.4, sound=False)
img("stat-66", t + 1.4, 3.6, "low", sound="coin")

# ---- 05 the folder drop, live ------------------------------------------------------------------------------------
img("chip-live", T("so i have some demo statements", 364.5) + 0.2, 2.8, *TOP_L, pop="slide_l", sound="swish")
hl((860, 390, 2956, 1190), T("you can see bank of america", 376.7) + 0.3, 3.8, sound=False)
img("stat-passed", T("all checks did pass", 381.0), 3.4, "auto")
hl((906, 1570, 1372, 1644), T("you can download the statements", 396.3) + 0.3, 2.4)

# ---- 06 the CSV in Excel -----------------------------------------------------------------------------------------
img("chip-excel", KEEPS[7][0] + 1.3, 2.8, *TOP_L, pop="slide_l", sound="swish")
img("logo-excel", T("this is the bank of america statement", 435.6), 3.4, *TOP_R, pop="slide_r", sound="sparkle")
img("stat-csv", T("but it does import as a csv", 443.1), 3.4, "low")
img("logo-sheets", T("google sheets", 466.4), 3.2, *TOP_R, pop="slide_r", sound="sparkle")

# ---- 07 send feedback ----------------------------------------------------------------------------------------------
img("chip-feedback", T("one last thing", 481.5) + 0.85, 2.8, *TOP_L, pop="slide_l", sound="swish")
hl((2364, 34, 2500, 104), T("there is a feedback section", 486.24) + 0.3, 2.0)
t = T("it goes directly to the agents", 507.1) + 0.3
hl((1426, 480, 2852, 1780), t, 3.4, sound=False)
img("stat-agentsread", t, 3.4, 720, 1150, scale=0.55)   # the empty column left of the form
t = T("please do that in the help tab", 517.5)
img("prompt-help", t, 3.6, "low", pop="slide_up", sound="swish")
hl((2364, 34, 2500, 104), t + 0.3, 2.4, sound=False)

# ---- outro (talking head): recap, the share ask, subscribe; nothing over the face ---------------------------------
img("stat-recap", T("that is the update on the", 536.2) + 0.9, 4.6, 1920, 250, scale=0.85)
img("share-card", T("if you know any accountants or bookkeepers that could use a system", 574.5) + 0.2, 3.6, 1920, 250, scale=0.85)
img("url-paperrows", T("feel free to share it", 578.4), 3.8, 1920, 1850, scale=0.8, pop="slide_up", sound="swish")
img("cta-subscribe", T("please like subscribe", 623.0), 3.0, 1920, 1850, scale=0.8)
t = T("thats all for the paperrows update", 620.1) + 0.4
img("site-card", t, round(TOTAL - 1.4 - cut_at(t), 3), 1920, 250, scale=0.85, pop="slide_down", sound="swish")

# ---- the big moments: "four customers" is the punchline (impact, music dead); the White Flash gets a boom ---------------
sound_at("boom", cut_at(T_COLD_END, cold=True), 0.18)
sfx.append({"path": str(AUD / "sfx-riser.wav"), "peak_at": q(cut_at(T_COLD_END, cold=True)), "volume": 0.08})
