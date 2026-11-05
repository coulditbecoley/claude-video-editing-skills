# Graphics timing for Asgard Agents Day 30, exec'd by gen_edl.py.
# Every card lands on the word that names it: T(phrase, hint) is the source second that phrase starts.
# hl() is a glowing gold box on the exact screen element he's talking about (source px, measured from the frame at
# that moment, probe/hlgrid_*.jpg), held only while the page is still. A box placed with a card stays silent so the
# moment gets one sound. img(..., x="auto") puts the card top-centre unless a box lives there, else bottom-left.
# Sounds: pop on stats, coin on money, swish on chips and slides, sparkle on logos, tick on boxes, boom/impact once.
T = lambda phrase, hint: find(phrase, hint)[0]
TE = lambda phrase, hint: find(phrase, hint)[1]
span = lambda a, b, cold=False: round(cut_at(b, cold) - cut_at(a, cold), 3)
LOWA = (1660, 1810)        # bottom-left, clear of the facecam (step strips at 1.45x: x 490-2830, y 1510-2110)

# ---- cold open: the money, then the honest answer ----------------------------------------------------------------
t = T("checkouts they have made", 491.0)
img("cold-66", t + 0.9, span(t + 0.9, TE("two businesses so far", 495.5)) + 0.35, "low", cold=True, sound="coin")
t = T("are they profitable yet", 121.2)
t_no = T("no not yet", 122.9)
img("cold-profit", t + 0.15, span(t + 0.15, t_no) - 0.07, *SLOT_TOP, cold=True, pop="in", sound="swish")
img("cold-notyet", t_no, span(t_no, KEEPS[1][1]) - 0.05, *SLOT_TOP, cold=True, pop="in", sound="impact")

# ---- hook (talking head): premise above his head, the five agents across his chest ------------------------------
t_h = T("this is day 30", 9.5)
t_end = TE("on their own", 18.5)
img("hook-title", t_h, span(t_h, t_end) + 0.3, 1920, 250, scale=0.86)
for k, n in enumerate(["odin", "thor", "loki", "mimir", "heimdall"]):
    t0 = T("five ai agents", 11.5) + 0.12 * k
    img(f"agent-{n}", t0, span(t0, t_end) + 0.3, 1080 + 420 * k, 1800, scale=0.85, sound="pop" if k == 0 else None)
img("stat-boundary", T("no human involvement", 19.6) + 0.15, 3.8, 1920, 250, scale=0.85)
img("logo-obsidian", T("into the obsidian canvas", 26.2), 3.0, *TOP_R, pop="slide_r", sound="sparkle")

# ---- 01 the scoreboard ----------------------------------------------------------------------------------------------
img("chip-score", T("so day 30 scoreboard", 71.5), 2.8, *TOP_L, pop="slide_l", sound="swish")
img("live-247", T("24 hour live", 79.0), 4.2, "auto", scale=0.8)
t = T("they have locked 13", 98.1) + 0.3
hl((1524, 972, 2480, 1472), t, 3.4, sound=False)
img("stat-locked", t, 3.4)
t = T("so theyd still get paid", 115.6) + 0.3
hl((1784, 984, 2744, 1488), t, 3.4, sound=False)
img("stat-perminute", t, 3.4, sound="coin")
hl((2184, 904, 2948, 1296), T("are they profitable yet", 121.2) + 0.3, 3.0)

# ---- 02 follow along ------------------------------------------------------------------------------------------------
img("chip-follow", T("follow along", 132.2), 2.8, *TOP_L, pop="slide_l", sound="swish")
t = T("now you can go to their telegram", 136.1) + 0.3
hl((1428, 1112, 2980, 1528), t, 3.4)
img("logo-telegram", t, 3.4, *TOP_R, pop="slide_r", sound="sparkle")
img("prompt-loki", T("what time is payout", 145.5) - 0.2, 3.2, "auto", pop="slide_up", sound="swish")
t = T("the agents are back on x", 158.4) + 0.3
hl((1572, 1028, 3124, 1440), t, 3.2)
img("logo-x", t, 3.2, *TOP_R, pop="slide_r", sound="sparkle")
t = T("they have decided to give", 168.8) + 0.3
hl((1520, 944, 3072, 1360), t, 3.4, sound=False)
img("stat-twice", t, 3.4)
t = T("the discord is still available", 179.1) + 0.2
hl((1512, 1072, 2860, 1428), t, 2.6, mt=t + 0.2)
img("logo-discord", t, 2.6, *TOP_R, pop="slide_r", sound="sparkle")

# ---- 03 they caught their own mistakes (the canvas cards carry the detail; boxes follow his finger) ----------------
img("chip-mistakes", T("lets move on to some things", 181.8) + 0.3, 2.8, *TOP_L, pop="slide_l", sound="swish")
hl((1420, 912, 2980, 1332), T("payday pause itself", 186.4) + 0.3, 3.2)
hl((1344, 924, 2900, 1340), T("they were going to start a cold email", 199.1) + 0.3, 3.4)
hl((1356, 1024, 2912, 1440), T("heimdall found some things", 212.6) + 0.3, 3.2)
t = T("their token lock it did get delayed", 218.7) + 0.3
hl((1392, 872, 2948, 1288), t, 3.6, sound=False)
img("stat-lock", t, 3.6)
hl((1412, 852, 2968, 1272), T("they did tell everyone", 231.6) + 0.3, 3.2)
t = 240.45                                   # "Stale post." (v2: the website-delay line after it is cut)
hl((1456, 840, 3012, 1260), t, 2.6, sound=False, mt=240.4)
img("stat-stale", t, 2.6, "low")

# ---- 04 behind the scenes -------------------------------------------------------------------------------------------
img("chip-behind", T("lets move on behind the scenes", 250.1) + 0.3, 2.8, *TOP_L, pop="slide_l", sound="swish")
t = T("so treasury locked", 253.5) + 0.3
hl((1360, 400, 2912, 820), t, 3.6, sound=False)
img("stat-treasury", t + 0.2, 3.8, sound="coin")
t = T("the hiring hall is still in progress", 274.6) + 0.3
hl((1384, 728, 2940, 1148), t, 3.6, sound=False)
img("stat-hiring", t, 3.6)
# the Hiring Hall as a four-step strip, each step lit as he says it
STEPS = [(T("whatever task that the asgard agents put", 299.4), 1), (T("outside agent can come in", 304.3), 2),
         (T("the agents will verify", 307.5), 3), (T("then they get paid", 309.0), 4), (TE("coming soon", 314.1) + 0.3, None)]
for k, (t0, n) in enumerate(STEPS[:-1]):
    t1 = STEPS[k + 1][0]
    pop = "slide_up_in" if k == 0 else ("slide_up_out" if k == len(STEPS) - 2 else False)
    img(f"hall-{n}", t0, span(t0, t1), *LOWA, scale=1.45, pop=pop, sound="swish" if k == 0 else ("coin" if n == 4 else "tick"))
t = T("every sale is tracked", 315.2) + 0.3
hl((1392, 960, 2948, 1380), t, 3.2, sound=False)
img("stat-tracked", t, 3.2)
t = T("so youll see on the asgard agents website", 328.3) + 0.3
hl((1420, 1024, 2968, 1440), t, 3.6, sound=False)
img("stat-sponsorbar", t, 3.6)
t = T("so they also added a reconnection", 351.6) + 0.3
hl((1508, 992, 3060, 1400), t, 3.6, sound=False)
img("stat-reconnect", t, 3.6)

# ---- 05 what's next -------------------------------------------------------------------------------------------------
img("chip-next", T("so here it is", 375.3) + 0.2, 2.8, *TOP_L, pop="slide_l", sound="swish")
t = T("the sales scoreboard is what", 375.8) + 0.3
hl((1220, 972, 2852, 1512), t, 3.6, sound=False)
img("stat-scoreboard", t + 0.3, 3.8, "low")
t = T("opening the hiring hall", 401.4) + 0.4
hl((1248, 1020, 2880, 1560), t, 3.0, mt=t)
img("stat-shorts", T("agent shorts", 407.0) + 0.2, 3.4)
t = T("you can follow them at", 432.6) + 0.4
hl((560, 1210, 2880, 1480), t, 3.4, sound=False, mt=t)
img("site-card", t + 0.6, 3.2, 1920, 330, scale=0.85, pop="slide_down", sound="swish")
img("socials", T("and the other socials", 441.6), 3.0, 1920, 330, scale=0.8, sound="sparkle")

# ---- 06 the Agents Window (punch-ins; boxes map through them) -------------------------------------------------------
img("chip-window", KEEPS[4][0] + 1.5, 2.8, *TOP_L, pop="slide_l", sound="swish")
t = T("it looks like everyones sleeping", 483.8) + 0.2
hl((1016, 44, 1320, 170), t, 3.4, sound=False)
img("stat-asleep", t, 3.4)
t = T("checkouts they have made", 491.0) + 0.3
hl((1330, 44, 1630, 170), t, 4.0, sound=False)
img("stat-66", t + 0.6, 3.6, sound="coin")
t = T("so they did get paid", 501.4) + 0.2
hl((1644, 44, 1950, 170), t, 4.0, sound=False)
img("stat-paidtoday", t + 0.4, 3.8, sound="coin")
t = T("so it looks like thor", 515.7) + 0.3
hl((624, 216, 1176, 1150), t, 3.6, sound=False)
img("card-thor", t, 3.6, 2100, 1700, scale=0.85, pop="slide_up", sound="swish")
t = T("days in business", 520.5) + 0.1
hl((1964, 44, 2260, 170), t, 3.4, sound=False)
img("stat-day30", t, 3.4)
t = T("five hundred and eighty two visitors", 535.5) + 0.1
hl((2276, 44, 2570, 170), t, 3.0, sound=False)
img("stat-visitors", t, 3.0)
hl((2586, 44, 2900, 170), T("and the reaction tab", 538.7) + 0.2, 3.2)
img("stat-vote", T("you can vote once per day", 552.8), 3.0)
hl((2940, 216, 3790, 610), T("you still got the valhalla", 558.2) + 0.2, 3.0)
t = T("loki has the most minutes", 570.4)
hl((2980, 288, 3760, 328), t, 2.4, sound=False)
img("card-loki", t, 2.6, 1500, 1700, scale=0.85, pop="slide_up", sound="swish")
t = T("mvp for today", 580.0)
hl((2940, 650, 3790, 1150), t, 2.0, sound=False)
img("card-odin", t, 2.0, 1500, 1700, scale=0.85, pop="slide_up", sound="swish")
img("card-heimdall", T("my favorite today", 581.7) + 0.3, 3.6, 1500, 1700, scale=0.85, pop="slide_up", sound="swish")
hl((3504, 712, 3760, 760), T("you can go and vote for the next business", 590.8), 2.6)
t = T("it looks like we are going to pick finance", 594.3) + 0.6
hl((2968, 820, 3360, 864), t, 3.2, sound=False)
img("stat-finance", t, 3.4)
hl((2940, 1190, 3790, 1410), T("and behind my beautiful head", 602.4) + 0.6, 3.4)

# ---- 07 their businesses ---------------------------------------------------------------------------------------------
t = T("the newest business", 622.0)
img("chip-biz", t, 2.8, *TOP_L, pop="slide_l", sound="swish")
hl((2080, 1190, 2900, 1890), t + 0.4, 3.6)
img("logo-c3", T("c3 research is all on the agents", 646.0), 3.2, 1700, 1820, scale=0.85, pop="slide_up", sound="sparkle")
img("stat-c3idea", T("let them take it over", 634.5), 3.6)
t = T("that are on these networks shown", 657.4) + 0.3
hl((2120, 1496, 2860, 1530), t, 3.0, sound=False)
img("chains", t, 3.4, 1920, 330, scale=0.75, sound="sparkle")
img("stat-evidence", T("make your decisions", 679.3) - 0.4, 3.4)
t = T("im sure some of you have seen this", 682.4)
img("card-paperrows", t, 3.2, *TOP_R, pop="slide_r", sound="sparkle")
hl((1206, 1190, 2010, 1890), t + 0.3, 3.2)
img("flow-pdfcsv", T("is just a bank statement converter", 698.6), 4.0, 1920, 330, scale=0.8)
img("stat-browser", T("it all stays in your browser", 713.0), 4.4)

# payroll, the token, the lock (all in the payroll punch-in)
hl((60, 1190, 1140, 1920), T("over here to payroll", 727.0) + 0.3, 3.0)
t = T("it does have a pump fund chart", 736.3)
img("logo-pumpfun", t, 3.0, *TOP_R, pop="slide_r", sound="sparkle")
hl((76, 1504, 1110, 1840), t + 0.2, 3.0, sound=False)
img("stat-nfa", T("you guys are welcome to go and grab some", 744.2), 4.4)
t = T("the company wallet has gone down", 752.3)
hl((880, 1400, 1120, 1470), t, 3.4, sound=False)
img("stat-holds", t, 3.6, sound="coin")
t = T("no way to unlock them", 764.0)
img("stat-nounlock", t, min(3.6, span(t, T("last but not least", 768.8)) - 0.1), "low")

# ---- 08 sponsor the hall ---------------------------------------------------------------------------------------------
img("chip-sponsor", T("last but not least", 768.8), 2.8, *TOP_L, pop="slide_l", sound="swish")
hl((60, 1950, 1750, 2050), T("you can see some companies down here", 776.8) + 0.2, 3.0)
t = T("obviously scald studio is running", 779.7)
hl((500, 1960, 780, 2040), t, 3.0, sound=False)
img("card-skald", t, 3.2, 1500, 1500, scale=0.85, pop="slide_up", sound="sparkle")
# the Sponsor the Hall page plays full frame; its four steps light up as he walks them
img("stat-price", TO_SPONSOR + 1.3, 3.6, 1920, 1880, scale=0.8)
# v2 (Codex #9): step 3 reads "If approved" and step 4 (Live) lights on "you will get your response"
t_resp = T("you will get your response", 816.4)
SP = [(T("you just fill out the information here", 798.9), 1), (T("do a review of your company", 803.8), 2),
      (T("they approve or deny you", 815.0), 3), (t_resp, 4), (t_resp + 1.8, None)]
for k, (t0, n) in enumerate(SP[:-1]):
    t1 = SP[k + 1][0]
    pop = "slide_up_in" if k == 0 else ("slide_up_out" if k == len(SP) - 2 else False)
    img(f"sp-{n}", t0, span(t0, t1), *LOWA, scale=1.45, pop=pop, sound="swish" if k == 0 else "tick")
img("stat-24h", t_resp + 1.8, 3.4, 1920, 1880, scale=0.8)

# ---- 09 back on X ----------------------------------------------------------------------------------------------------
img("chip-x", KEEPS[6][0] + 1.4, 2.8, *TOP_L, pop="slide_l", sound="swish")
hl((1290, 930, 1650, 1000), T("they do have a few followers", 877.5), 3.0)
img("stat-suspended", T("other account suspended", 885.0), 4.0)
hl((1284, 600, 2330, 1040), T("they did make an announcement", 901.6) + 0.3, 3.6)
hl((1290, 540, 2330, 960), T("token lock is", 917.8) + 0.05, 1.8)
img("cta-follow-x", T("give them a follow", 929.3) - 0.3, 3.6, 1700, 1860, scale=0.85, pop="slide_up", sound="sparkle")

# ---- 10 live 24/7: Pump.fun and YouTube ---------------------------------------------------------------------------
# v2 (Codex #4): the Pump.fun page's "Hot callouts" feed and live chat carry explicit abuse and token spam. Both
# columns are covered for the whole Pump.fun stretch by an opaque blurred, darkened patch (headers left visible).
import subprocess as _sp
def mask(name, box, t_src, a_out, b_out):
    path = GFX / f"{name}.png"
    if not path.exists():
        from PIL import Image as _I, ImageFilter as _F, ImageDraw as _D, ImageEnhance as _En
        raw = _sp.run(["ffmpeg", "-v", "error", "-ss", str(t_src), "-i", MAIN, "-frames:v", "1", "-f", "rawvideo",
                       "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        fr = _I.frombytes("RGB", (W, H), raw).crop(box).filter(_F.GaussianBlur(48))
        fr = _En.Brightness(fr).enhance(0.45).convert("RGBA")
        m = _I.new("L", fr.size, 0); _D.Draw(m).rounded_rectangle((0, 0, fr.width - 1, fr.height - 1), radius=22, fill=255)
        fr.putalpha(m); fr.save(path)
    images.append({"path": str(path), "start": q(a_out), "duration": round(q(b_out) - q(a_out), 3),
                   "x": (box[0] + box[2]) // 2, "y": (box[1] + box[3]) // 2, "scale": 1.0, "pop": False})
_pa, _pb = cut_at(KEEPS[7][0]), cut_at(KEEPS[7][1])
mask("mask-pump-feed", (110, 250, 690, 2156), 980.0, _pa, _pb)
mask("mask-pump-chat", (3200, 290, 3790, 1410), 980.0, _pa, _pb)
img("chip-live", KEEPS[7][0] + 1.4, 2.8, *TOP_L, pop="slide_l", sound="swish")
img("logo-pumpfun2", T("this is the pump fun platform", 982.0), 3.2, *TOP_R, pop="slide_r", sound="sparkle")
img("logo-youtube", KEEPS[8][0] + 1.2, 3.2, *TOP_R, pop="slide_r", sound="sparkle")
hl((320, 1160, 1260, 1740), T("ask them anything on telegram", 1068.2) + 0.2, 3.2)
img("prompt-ask", T("ask asgard agent live bot", 1074.1), 4.0, 1920, 330, scale=0.85, pop="slide_down", sound="swish")
t = T("cover the token section", 1089.1)
hl((320, 1160, 1260, 1740), t, 3.6, sound=False)
img("stat-hidden", t, 3.8)
hl((300, 1780, 1960, 1850), T("sponsor bar", 1107.6) + 0.2, 3.0)

# ---- outro (talking head): recap before the ask, one card at a time, nothing over the face ----------------------
img("stat-recap", T("day 30 of the asgard agents", 1162.0), 4.6, 1920, 250, scale=0.85)
img("cta-subscribe", T("give us a like and subscribe", 1170.3) + 0.6, 3.0, 1920, 1850, scale=0.8)
img("card-day20", T("go watch the previous video", 1175.7), span(T("go watch the previous video", 1175.7), TE("upgraded this far", 1180.5)) + 0.3,
    3130, 800, scale=0.85)
t = T("check them out on", 1182.5)
img("site-card", t + 0.4, round(TOTAL - 1.4 - cut_at(t + 0.4), 3), 1920, 1850, scale=0.85, pop="slide_up", sound="swish")

# ---- the big moments: the White Flash out of the cold open gets a riser and a boom; "No, not yet" is the punchline
sound_at("boom", cut_at(T_COLD_END, cold=True), 0.22)
sfx.append({"path": str(AUD / "sfx-riser.wav"), "peak_at": q(cut_at(T_COLD_END, cold=True)), "volume": 0.10})
sound_at("impact", cut_at(T("no not yet", 122.9)), 0.17)
