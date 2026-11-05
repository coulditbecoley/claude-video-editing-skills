# Graphics timing for Asgard Agents Day 35, exec'd by gen_edl.py.
# Every card lands on the word that names it: T(phrase, hint) is the source second that phrase starts.
# hl() is a glowing gold box on the exact screen element he's reading (source px, measured on gridded frames at that
# moment, probe/g/sheet_*.jpg), held only while the page under it is still. A box placed with a card stays silent so
# the moment gets one sound. img(..., "auto") puts the card top-centre unless a box lives there, else bottom-left.
# Sounds: pop on stats, coin on money, swish on chips and slides, sparkle on logos, tick on boxes, boom/impact once.
T = lambda phrase, hint: find(phrase, hint)[0]
TE = lambda phrase, hint: find(phrase, hint)[1]
span = lambda a, b, cold=False: round(cut_at(b, cold) - cut_at(a, cold), 3)
LOWA = (1660, 1810)        # bottom-left, clear of the facecam (step strips at 1.45x)
# every box was measured on the gridded frame at phrase start + 0.4 s of picture (hlgrid4.py, hl_mt.json): that frame
# is the box's measurement time (mt), so a page that scrolled since is caught instead of a box landing off its card
import json as _json
_MT = {float(k): v for k, v in _json.loads((HERE / "hl_mt.json").read_text()).items()}
_hl = hl
def hl(rect, t, d, color=GOLD, sound=True, mt=None, fixed=False):
    if mt is None and not fixed:
        k = min(_MT, key=lambda x: abs(x - t))
        if abs(k - t) < 1.0:
            mt = _MT[k]
    return _hl(rect, t, d, color=color, sound=sound, mt=mt, fixed=fixed)

# ---- cold open: the World, then the money -------------------------------------------------------------------------
t = T("as you can see this is them at work", 798.5)
img("cold-world", t, span(t, KEEPS[0][1], cold=True) - 0.15, *SLOT_TOP, cold=True, pop="in", sound="swish")
t = T("741", 632.1) - 0.1
img("cold-741", t, span(t, KEEPS[1][1], cold=True) - 0.1, *SLOT_TOP, cold=True, pop="in", sound=None)   # the impact on the dead stop carries it

# ---- hook (talking head): premise above his head, the agents across his chest, the three questions -------------
t_h = T("day 35 of watching", 3.6)
t_end = TE("run their own business", 8.5)
img("hook-title", t_h + 1.1, span(t_h + 1.1, t_end) + 0.35, 1920, 250, scale=0.86, vol=0.12)   # quieter: it lands on a loud "Day 35" (mix peaked -0.6 dBTP)   # clear of the White Flash
for k, n in enumerate(["odin", "thor", "loki", "mimir", "heimdall"]):
    t0 = T("five ai agents", 5.8) + 0.12 * k
    img(f"agent-{n}", t0, span(t0, t_end) + 0.35, 1080 + 420 * k, 1800, scale=0.85, sound="pop" if k == 0 else None)
QS = [T("see if theyre profitable", 21.0), T("see how much money", 22.7), T("what they are going to do next", 29.8),
      TE("what they are going to do next", 29.8) + 0.6]
for k in range(3):
    pop = "slide_up_in" if k == 0 else ("slide_up_out" if k == 2 else False)
    img(f"hook-q{k + 1}", QS[k], span(QS[k], QS[k + 1]), 1920, 1880, scale=0.8, pop=pop, sound="swish" if k == 0 else "tick")
img("logo-obsidian", T("obsidian canvas", 33.5), 3.0, *TOP_R, pop="slide_r", sound="sparkle")

# ---- the canvas intro: the council ---------------------------------------------------------------------------------
hl((990, 800, 3010, 1395), T("the agents theyre still the same", 72.2) + 0.2, 5.2)

# ---- 01 the Day 35 scoreboard -------------------------------------------------------------------------------------
t = T("they have created", 86.4)
img("chip-score", t, 2.8, *TOP_L, pop="slide_l", sound="swish")
hl((1432, 940, 2032, 1240), t + 0.4, 3.4)
img("stat-world", T("free roam camera", 95.3), 3.6)
t = T("a guarded chat", 140.38)
hl((1592, 988, 2352, 1380), t + 0.2, 3.4, sound=False)
img("stat-guard", t + 0.2, 3.6)
t = T("fees counted", 163.98)
hl((1620, 1000, 2380, 1380), t + 0.2, 3.4, sound=False)
img("stat-fees", t + 0.2, 3.6)
t = T("the asgard agents the holders", 179.16)
hl((1764, 960, 2528, 1360), 182.45, 3.4, sound=False, mt=182.67)   # he scrolls inside the "the holders" cut
img("stat-yoursay", t + 0.2, 3.6)

# ---- 02 follow along -----------------------------------------------------------------------------------------------
t = T("we just spoke about their new 3d world", 207.9)
img("chip-follow", t, 2.8, *TOP_L, pop="slide_l", sound="swish")
hl((1260, 848, 2496, 1184), t + 0.4, 3.2, mt=209.67)
img("url-world", 212.95, 3.6, 1920, 330, scale=0.8, pop="slide_down", sound="swish")
t = T("they did make an update to a real weather", 220.8)
hl((1328, 1000, 2560, 1328), t + 0.2, 3.4, sound=False, mt=222.67)
img("stat-weather", t + 0.2, 3.8)
t = T("they added buy alerts", 234.1)
hl((1448, 1008, 2680, 1340), t + 0.2, 3.4, sound=False)
img("tile-buys", t + 0.3, 3.6, 1920, 330, scale=0.72, sound="sparkle")
t = T("posts on discord", 243.7)
hl((1508, 980, 2740, 1300), t + 0.2, 3.4, sound=False)
img("logo-discord", t + 0.2, 3.4, *TOP_R, pop="slide_r", sound="sparkle")
t = T("videos they did create", 258.9)
hl((1448, 1280, 2680, 1608), t + 0.2, 3.4, sound=False, mt=260.70)
img("stat-short", t + 0.2, 3.8)

# ---- 03 they caught their own mistakes -----------------------------------------------------------------------------
img("chip-mistakes", T("here are some mistakes", 271.9) + 0.1, 2.8, *TOP_L, pop="slide_l", sound="swish")
t = T("so they stopped an early leak", 275.9)
hl((1352, 800, 2588, 1120), t + 0.2, 3.6, sound=False)
img("card-heimdall", T("hemdall found it", 280.5), 3.4, *TOP_R, pop="slide_r", sound="sparkle")
t = T("no made up answers", 289.2)
hl((1340, 900, 2572, 1220), t + 0.2, 3.4, sound=False)
img("stat-madeup", T("but he will only give you information", 295.8), 4.2)   # on the claim it qualifies (Codex #3)
t = T("warnings arent scams", 311.3)
hl((1320, 848, 2548, 1172), t + 0.2, 3.4, sound=False)
img("stat-warnings", t + 0.2, 3.6)
t = T("more isnt better", 338.9)
hl((1320, 848, 2548, 1180), t + 0.2, 3.4, sound=False)
img("stat-more", T("they said right now", 366.5), 3.4)
t = T("the hall yes the hall", 376.0)
hl((1340, 1000, 2568, 1328), t + 0.2, 3.4, sound=False)
img("stat-hall", T("so that is coming soon", 394.5), 4.0)   # on "finished any day now" (Codex #3)

# ---- 04 behind the scenes ------------------------------------------------------------------------------------------
img("chip-behind", T("behind the scenes", 400.2), 2.8, *TOP_L, pop="slide_l", sound="swish")
t = T("the agents did go out and apply", 403.5)
hl((1360, 912, 2600, 1232), t + 0.2, 3.6, sound=False, mt=405.40)
img("stat-listing", T("for example jupiter", 415.7), 3.8)
t = T("paid in asgard", 429.9)
hl((1468, 948, 2700, 1272), t + 0.2, 3.6, sound=False, mt=432.00)
img("stat-payasgard", t + 0.2, 4.0, sound="coin")
t = T("so the asgard token is getting its first utility", 444.0)
img("stat-utility", t, span(t, TE("the agents provide", 452.8)) + 0.6)   # held through the whole availability claim (Codex v2 #2)   # "can be used to pay": not live yet (Codex #3)
t = T("they decided to not flood", 457.8)
hl((1500, 860, 2732, 1180), t + 0.2, 3.6, sound=False, mt=459.70)
img("stat-onepost", T("one business post per day", 469.1), 3.6)
t = T("track by channel", 492.3)
hl((1540, 868, 2768, 1192), t + 0.2, 3.6, sound=False)
img("stat-tracked", t + 0.2, 3.8)
t = T("a faster agent window", 508.6)
hl((1380, 800, 2900, 1220), t + 0.2, 3.6, sound=False, mt=511.00)
img("stat-faster", t + 0.2, 3.8)
hl((1408, 940, 2968, 1352), T("they did integrate loki to telegram", 527.5) + 0.2, 3.0)
PR = [T("you can now just say loki", 531.8), T("or loki how much did you make", 534.5), T("or loki what are the agents coming up", 537.2),
      TE("or loki what are the agents coming up", 537.2) + 0.5]
for k in range(3):
    pop = "slide_down_in" if k == 0 else ("slide_down_out" if k == 2 else False)
    img(f"prompt-{k + 1}", PR[k], span(PR[k], PR[k + 1]), 1920, 330, scale=0.85, pop=pop, sound="swish" if k == 0 else "tick")

# ---- 05 what's next ------------------------------------------------------------------------------------------------
img("chip-next", T("up next here we go", 547.8), 2.8, *TOP_L, pop="slide_l", sound="swish")
t = T("the agents came up with the posting carousel", 551.4)
hl((972, 1048, 2268, 1480), t + 0.2, 3.6, sound=False)
img("stat-team", t + 0.2, 3.8)
t = T("pay in asgard yes", 563.8)
hl((1308, 1080, 2600, 1512), t + 0.2, 3.4, sound=False)
img("stat-paynext", T("they are now implementing", 566.4), 3.8, sound="coin")
t = T("opening the hiring hall", 574.1)
hl((1520, 1120, 2820, 1540), t + 0.2, 3.6, sound=False)
img("stat-hallnext", t + 0.2, 3.8)
t = T("as always this is how you can find the agents", 591.6)
img("site-card", T("theazgardagent com", 595.0), 3.0, 1920, 330, scale=0.8, pop="slide_down", sound="swish")
img("socials", T("you got them on x", 599.4), 3.6, 1920, 330, scale=0.75, sound="sparkle")

# ---- 06 the Agents Window ------------------------------------------------------------------------------------------
img("chip-window", KEEPS[4][0] + 1.3, 2.8, *TOP_L, pop="slide_l", sound="swish")
t = T("you can see we got loki working right now", 619.1)
hl((1240, 432, 1820, 1220), t + 0.2, 3.6, sound=False, fixed=True)
img("card-loki", t + 0.2, 3.6, *TOP_R, pop="slide_r", sound="sparkle")
t = T("this is the amount", 630.0)
hl((1220, 220, 1505, 382), t + 0.4, 4.0, sound=False, fixed=True)
img("stat-741", T("741", 632.1), 4.2, "low", sound="coin")
t = T("as you can see at the bottom left", 646.1)
hl((60, 1560, 1160, 1800), t + 0.3, 3.4, sound=False, fixed=True)
img("stat-nfa", T("theyre not here to pump", 653.0), 4.2)
hl((1220, 220, 1505, 382), T("the creator fees from trading", 665.2) + 0.3, 3.2, fixed=True)
img("stat-buyplan", T("theyre going to burn half of it", 689.7), 3.4)
t = T("so really their plan was to grow the floor", 693.2)
img("stat-noprice", t, span(t, TE("really is their idea", 700.6)) + 0.5)   # through "...really, is their idea" (Codex v2 #2)   # (Codex #3)
hl((2440, 220, 2740, 382), T("you can see the agent world icon", 718.5) + 0.4, 3.4, fixed=True)

# ---- 07 the Agents World (World footage moves; cards only, no boxes) --------------------------------------------
img("chip-world", KEEPS[5][0] + 1.9, 2.8, *TOP_L, pop="slide_l", sound="swish")   # after the 0.8 s Light Leaks
img("stat-camera", T("you do have a full camera view", 807.5), 3.4)
img("card-loki-food", T("look loki is headed to get some food", 814.7), 3.2, *TOP_R, pop="slide_r", sound="sparkle")
img("stat-workstation", T("this is lokis workstation", 826.8), 3.6)
img("stat-follow", T("you can also click these icons", 843.4), 3.8)
img("vitals", T("they do have health food water", 856.6), 4.4, 1920, 330, scale=0.85)
img("stat-draft", T("this is a rough draft", 880.0), 3.6)
img("quote-mimir", T("mimir says its 66 degrees out", 920.0), 3.4, *TOP_R, pop="slide_r", sound="sparkle")
img("stat-bifrost", T("right now the bifrost bridge is down", 944.3), 3.8)
img("stat-goal", T("their goal is always going to be", 959.1), 4.0)
img("url-world", T("if you ever want to come to agents world", 978.3), 2.4, 1920, 330, scale=0.8, pop="slide_down", sound="swish")

# ---- 08 their businesses (back on the Window) ----------------------------------------------------------------------
t = KEEPS[6][0]
img("chip-biz", t + 1.3, 2.8, *TOP_L, pop="slide_l", sound="swish")
hl((1248, 1272, 2100, 1800), T("they have you covered with paper rows", 999.6), 2.6, sound=False, fixed=True)
img("card-paperrows", T("they have you covered with paper rows", 999.6), 2.8, *TOP_R, pop="slide_r", sound="sparkle")
img("logo-c3", T("be sure to use their c3 research tool", 1009.5), 3.2, 1700, 330, scale=0.75, pop="slide_down", sound="sparkle")
img("stat-c3", T("it is an agent tool", 1012.5), 4.4, "low")
t = T("the sponsor tab is still below", 1034.4)
hl((40, 1860, 1560, 1940), t + 0.2, 3.2, sound=False, fixed=True)
img("stat-sponsor", t + 0.2, 3.2)
t = T("they have had", 1037.9)
hl((2132, 220, 2420, 382), t + 0.2, 3.4, sound=False, fixed=True)
img("stat-visitors", t + 0.4, 3.4, "low")

# ---- 09 X ----------------------------------------------------------------------------------------------------------
img("chip-x", KEEPS[7][0] + 1.3, 2.8, *TOP_L, pop="slide_l", sound="swish")
img("logo-x", KEEPS[7][0] + 1.6, 3.2, *TOP_R, pop="slide_r", sound="sparkle")
t = T("they did pin the asgard treasury lock", 1056.8)
hl((1300, 620, 2340, 1040), t + 0.3, 3.6, sound=False)
img("stat-lock", t + 0.3, 3.8, "low")
# his click into the buyback post blanks the page for ~0.5 s (picture 1065.1-1065.7), under "...buyback" (this unit's
# lip shift is 0.47 s): a still of the settled profile page covers it, then a hard cut onto the post with a soft swipe
cover("cover-xclick", 1065.0, 1064.63, 1065.75)   # to the end of the piece: 1065.62 left one loading frame (Codex v2 #1)
images[-1]["duration"] = round(images[-1]["duration"] + 2 / FPS, 4)   # the cut lands between frames (817.717) and CapCut
# snaps it either way: run the cover a frame past it so the last loading frame is covered whichever way it rounds
sfx.append({"path": str(AUD / "sfx-swipe.wav"), "peak_at": q(cut_at(1067.05)), "volume": 0.12})
img("stat-500", 1067.2, 4.0, "low", sound="coin")     # "They have decided" starts 1067.15 (the word time is early)
BS = [T("theyre going to burn half and lock half", 1072.9), TE("theyre going to burn half and lock half", 1072.9) + 0.4]
img("buy-2", BS[0] + 0.5, span(BS[0] + 0.5, BS[1] + 0.8), *LOWA, scale=1.45, pop="slide_up_in", sound="swish")
img("buy-3", BS[1] + 0.8, 2.6, *LOWA, scale=1.45, pop="slide_up_out", sound="tick")
img("stat-onetime", T("this is what they decided", 1080.2) + 0.6, 4.0)
img("stat-wallets", T("because i dont do it for them", 1100.8), 4.2, "low")
t = T("here is the carousel post", 1122.1)
hl((1300, 460, 2340, 1800), t + 0.3, 3.6, sound=False)
img("stat-carousel", t + 0.3, 3.8, "low")
t = T("here is the post asking for the communitys feedback", 1144.2)
hl((1300, 740, 2340, 1680), t + 0.4, 4.0, sound=False)
img("stat-feedback", T("they want your feedback", 1148.7), 4.0)   # top: "low" covered the post's artwork (Codex #7)

# ---- outro (talking head): recap before the ask, nothing over the face ------------------------------------------
img("stat-recap", T("that is day 35s update", 1170.8) + 1.15, 5.0, 1920, 250, scale=0.85)   # after the Zoom Transition
img("stat-newbiz", T("they also have a new business idea", 1191.4), 3.6, 1920, 250, scale=0.8)
img("cta-subscribe", T("be sure to subscribe", 1210.8) - 0.2, 2.1, 1920, 1850, scale=0.8)
t = T("hit the like button", 1212.8) + 0.2
img("site-card", t, round(TOTAL - 1.3 - cut_at(t), 3), 1920, 1850, scale=0.85, pop="slide_up", sound="swish")

# ---- the big moments: the White Flash out of the cold open gets a riser and a boom; the cold open's money line is
# the punchline (the music cuts dead under it, music_plan.py)
sound_at("boom", cut_at(T_COLD_END, cold=True), 0.22)
sfx.append({"path": str(AUD / "sfx-riser.wav"), "peak_at": q(cut_at(T_COLD_END, cold=True)), "volume": 0.10})
sound_at("impact", cut_at(T("741", 632.1), cold=True) - 0.05, 0.17)   # on the dead stop of the bed (music_plan.py)
