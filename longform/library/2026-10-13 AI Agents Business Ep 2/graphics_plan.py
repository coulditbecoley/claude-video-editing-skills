# Graphics timing for AI Agents Business Ep 2: PaperRows, exec'd by gen_edl.py.
# Every card lands on the word that names it: T(phrase, hint) is the source second that phrase starts.
# hl() is a glowing gold box on the exact screen element he's talking about (source pixels, mapped through the
# piece's punch-in), placed inside a still stretch. Sounds: pop on stats, coin on money, swish on chips and side
# cards, sparkle on logos, tick on highlights, glitch on the skipped check, boom on the two big moments.
import subprocess as _sp
T = lambda phrase, hint: find(phrase, hint)[0]
TE = lambda phrase, hint: find(phrase, hint)[1]
span = lambda a, b, cold=False: round(cut_at(b, cold) - cut_at(a, cold), 3)
GUT_L, GUT_R = 430, 3400            # the site's empty side columns (page content is x 860-2960)
LOWC = (1700, 1880)                 # bottom, left of the facecam

# ---- cold open: their claim over the site, then the scoreboard -------------------------------------------------
img("stat-claim", T("they said hey we can 100", 201) + 0.3, 4.6, *LOWC, scale=0.85, cold=True, sound="pop")
img("score-cold", T("so they have one sale so far", 685.5), 2.1, *LOWC, scale=0.9, cold=True, sound="coin")

# ---- hook (talking head) ----------------------------------------------------------------------------------------
t_h = T("a week ago you and i", 2.5)
img("hook-title", t_h + 0.75, span(t_h + 0.75, TE("all on their own", 10.5)) + 0.4, 1920, 250, scale=0.95, sound="pop")
for k, n in enumerate(["odin", "thor", "loki", "mimir", "heimdall"]):
    t0 = T("five ai agents", 5.0) + 0.1 * k
    img(f"agent-{n}", t0, span(t0, TE("all on their own", 10.5)), 1080 + 420 * k, 1800, scale=0.85, sound="pop" if k == 0 else None)
# Coley (2026-10-13): the Episode 1 thumbnail pops up, with the pop sound, both times he mentions it
EP1_XY = (3130, 800)        # over the shelves, right of his face; he points this way on "go watch it here"
t = T("youve seen the first episode", 12.4)
img("card-ep1", t, span(t, TE("what they created", 17.3)) + 0.3, *EP1_XY, scale=0.85, sound="pop")
img("card-paperrows", T("called paperrows", 28.5), 3.0, *TOP_R, pop="slide_r", sound="sparkle")
img("flow-pdfcsv", T("so it takes your solid pdf", 42), span(T("so it takes your solid pdf", 42), TE("use the data from", 47.8)), 1920, 1800, scale=0.9)

# ---- 01 the Agents Window ------------------------------------------------------------------------------------------
img("chip-window", FIRST_SCREEN + 1.6, 2.8, *TOP_L, pop="slide_l", sound="swish")
t = T("jump into asgardagents com", 80)
img("site-card", t, 3.4, 1920, 1850)
hl((960, 70, 1230, 140), t, 3.4, sound=False)
img("stat-day20", T("weve already finished an update of day 20", 86.3), 3.4, *STAT)
t = T("another business idea", 99)
img("stat-next", t, 3.0, *STAT)
hl((2150, 1370, 2910, 1975), t, 3.0)
t = T("right now theyre all sleeping", 119.8)
img("stat-sleep", t + 0.4, 3.6, 1920, 1850)
hl((50, 510, 1210, 880), t, 3.0)
img("stat-paid", T("the agents now get paid for their time", 133.2), 2.6, *STAT)
img("logo-pumpfun", T("pumpfun", 139.4), 3.0, *TOP_R, pop="slide_r", sound="sparkle")
hl((60, 1640, 1170, 1920), T("asgard token that they created", 137.5), 3.2)
t = T("the company holds", 142.3)
img("stat-holds", t, 3.0, *STAT, sound="coin")
hl((900, 1530, 1200, 1620), t, 3.0, sound=False)
hl((56, 1440, 1180, 1530), T("they get paid per minute", 145.3), 3.6)
t = T("if they hire any other ai agents", 157)
img("stat-hire", t, 3.6, *STAT)
hl((600, 1540, 900, 1610), t, 3.0, sound=False)
hl((1244, 1420, 1700, 1525), T("here for the paperrows business", 168.6), 2.6)
img("stat-rejected", T("rejected four business options", 176.5), 3.2, *STAT)
hl((1244, 1860, 2090, 1936), T("so were going to go in here", 183.7), 4.6)

# ---- 02 PaperRows: the site (full frame; cards in the side columns) ------------------------------------------------
img("chip-paperrows", SITE[0] + 2.0, 2.8, *TOP_L, pop="slide_l", sound="swish")
img("side-their", T("they did all of this work", 196.4), 4.4, GUT_L, 1050, scale=0.85, pop="slide_l", sound="swish")
hl((860, 530, 1560, 1040), T("you choose the pdf", 230.8), 3.2)
img("side-browser", T("it reads that information inside", 234.2), 4.2, GUT_L, 1050, scale=0.85, pop="slide_l", sound="swish")
t = T("you can see the statement before", 253.1)
hl((1560, 530, 2260, 1040), t, 2.4)
img("side-preview", t, span(t, TE("you just pay for it", 260.0)) + 0.3, GUT_R, 760, scale=0.85, pop="slide_r", sound="swish")
hl((2260, 530, 2956, 1040), T("you just pay for it", 259.8), 1.6)
img("side-proud", T("their biggest achievement", 276.8), 5.0, GUT_R, 760, scale=0.85, pop="slide_r", sound="swish")
hl((858, 610, 1636, 800), T("your statements stay on your computer", 285.9), 2.6)
hl((860, 980, 1906, 1406), 308.25, 9.0)                                 # "So PDF and its names never get shared"
t = T("so what reaches the agents", 318.3)
hl((1906, 980, 2956, 1406), t, 12.0)
img("side-reaches", t + 0.3, 6.0, GUT_L, 1150, scale=0.85, pop="slide_l", sound="swish")
hl((860, 764, 1534, 1454), T("you can preview the statement for free", 358.6), 3.4)
img("formats", T("put it in excel google sheets", 366.2), 3.6, GUT_R, 760, scale=0.68, pop="slide_r", sound="sparkle")
hl((1572, 760, 2244, 1444), T("if you just want it once", 372.2), 2.2)
t = T("if youd like to sign up", 374.6)
hl((2282, 764, 2956, 1454), t, 4.0)
img("side-price", t, 5.0, GUT_L, 1100, scale=0.85, pop="slide_l", sound="coin")
t = T("you can also email the customer service agents", 401.0)
hl((2500, 1750, 2870, 1840), t, 4.0)
img("side-support", t, 5.0, GUT_L, 1100, scale=0.85, pop="slide_l", sound="swish")
hl((2570, 1940, 2930, 2025), T("created by asgard agents", 411.0), 2.8)

# ---- 03 the demo -----------------------------------------------------------------------------------------------------
def blur_at(name, box, t_src, a_src, b_src):
    """A blurred patch over a personal detail, cut from a still frame, shown from a_src to b_src (source)."""
    path = GFX / f"{name}.png"
    if not path.exists():
        from PIL import Image as _I, ImageFilter as _F, ImageDraw as _D
        raw = _sp.run(["ffmpeg", "-v", "error", "-ss", str(t_src), "-i", MAIN, "-frames:v", "1", "-f", "rawvideo",
                       "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        fr = _I.frombytes("RGB", (W, H), raw).crop(box).filter(_F.GaussianBlur(22)).convert("RGBA")
        m = _I.new("L", fr.size, 0); _D.Draw(m).rounded_rectangle((0, 0, fr.width - 1, fr.height - 1), radius=14, fill=255)
        fr.putalpha(m); fr.save(path)
    a, b = cut_at(a_src), cut_at(b_src)
    images.append({"path": str(path), "start": round(a, 3), "duration": round(b - a, 3),
                   "x": (box[0] + box[2]) // 2, "y": (box[1] + box[3]) // 2, "scale": 1.0, "pop": False})

# v2 (Codex #4): the file picker's account name, folder list and breadcrumb path
blur_at("blur-picker-nav", (20, 200, 290, 985), 424.0, 423.2, 425.55)
blur_at("blur-picker-path", (240, 66, 1230, 122), 424.0, 423.2, 425.55)
img("chip-demo", T("so up next were going to give a demo", 418.9) + 0.3, 2.8, *TOP_L, pop="slide_l", sound="swish")
STEPS = [(T("lets click on choose a statement", 422.3), 1), (T("it already has read", 427.4), 2),
         (T("here is the layout", 442.3), 3), (T("all you do is unlock statement", 463.7), 4),
         (T("once youve paid you download it", 482.5), 5), (TO_EXCEL - 0.05, None)]
for k, (t0, n) in enumerate(STEPS[:-1]):
    t1 = STEPS[k + 1][0]
    pop = "slide_l_in" if k == 0 else ("slide_l_out" if k == len(STEPS) - 2 else False)
    img(f"steps-{n}", t0, span(t0, t1), GUT_L, 1000, scale=0.95, pop=pop, sound="swish" if k == 0 else "tick")
hl((900, 690, 2010, 745), 431.4, 2.6)                                   # "7 passed, 1 not checked"
# v2 (Codex #1): the screen says why the check didn't run; card its wording, no glitch (not checked is not failed)
t = T("so it just skipped the check here", 435.0)
hl((900, 1010, 1760, 1090), t, 3.0)
img("side-notchecked", t + 0.4, 4.6, 3380, 900, scale=0.85, pop="slide_r", sound="swish")
hl((2640, 660, 2920, 2000), T("so you can see expenses and income", 444.9), 3.4)
hl((1250, 660, 2600, 2000), T("it gives you where it came from", 451.3), 3.2)
hl((2128, 588, 2568, 652), 466.2, 2.4)                                   # Unlock this statement, $5
img("logo-stripe", TO_STRIPE + 1.2, 3.6, 1250, 1700, scale=0.85, pop="slide_up", sound="sparkle")
hl((1070, 380, 1290, 520), 472.1, 3.0)                                   # $5.00 on Stripe
img("logo-excel", TO_EXCEL + 1.2, 3.2, *TOP_R, pop="slide_r", sound="sparkle")
hl((880, 480, 1210, 1980), T("you can see theres the first amounts", 509.4), 3.0)

# Coley's email and saved card on the Stripe page: blurred patches cut from the still checkout frame
def blur_patch(name, box, t_src=475.0):
    path = GFX / f"{name}.png"
    if not path.exists():
        from PIL import Image as _I, ImageFilter as _F, ImageDraw as _D
        raw = _sp.run(["ffmpeg", "-v", "error", "-ss", str(t_src), "-i", MAIN, "-frames:v", "1", "-f", "rawvideo",
                       "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        fr = _I.frombytes("RGB", (W, H), raw).crop(box).filter(_F.GaussianBlur(22)).convert("RGBA")
        m = _I.new("L", fr.size, 0); _D.Draw(m).rounded_rectangle((0, 0, fr.width - 1, fr.height - 1), radius=18, fill=255)
        fr.putalpha(m); fr.save(path)
    a, b = cut_at(471.6), cut_at(FROM_STRIPE)
    images.append({"path": str(path), "start": round(a, 3), "duration": round(b - a, 3),
                   "x": (box[0] + box[2]) // 2, "y": (box[1] + box[3]) // 2, "scale": 1.0, "pop": False})
blur_patch("blur-email", (2200, 425, 2620, 500))
blur_patch("blur-card", (2300, 750, 2700, 845))

# ---- 04 the canvas -----------------------------------------------------------------------------------------------
img("chip-canvas", T("now were in the obsidian canvas", 537) + 0.9, 2.8, *TOP_L, pop="slide_l", sound="swish")
img("logo-obsidian", T("now were in the obsidian canvas", 537) + 1.2, 3.0, *TOP_R, pop="slide_r", sound="sparkle")
hl((1360, 652, 2372, 1432), 573.2, 4.2)                                   # "It stays on your computer"
hl((1428, 668, 2440, 1448), T("check against the banks total", 590.8), 4.4)
img("roles", T("heres the guys that work on it", 613.7), 6.0, 1920, 330, scale=0.95)
t = T("so i had to set up the stripe account", 629.3)
img("stat-human", t, 4.0, *STAT)
hl((932, 1152, 2392, 1512), 630.0, 5.0)                                   # "The human: sets up accounts..."
img("stat-goal", T("their goal is five paying customers", 641.3), 4.4, *STAT)
hl((1144, 1168, 2988, 1624), 645.0, 5.0)                                  # "The goal: ... zero human help"
t = T("so far as of october 13th", 675)
img("score", t + 0.3, span(t + 0.3, TE("one sale so far", 687.0)) + 0.6, *STAT, sound="pop")
hl((1344, 1220, 2808, 1580), t + 0.2, 6.0, sound=False)
t_sale = T("so they have one sale so far", 685.5)
sound_at("boom", cut_at(t_sale))
sound_at("coin", cut_at(T("one sale so far", 686.0)))
img("site-paperrows", T("if you need the service", 695.0), 3.6, *TOP_R, pop="slide_r", sound="swish")

# ---- outro (talking head) ----------------------------------------------------------------------------------------
t = T("be sure to check out the first video", 710.7)
img("card-ep1", t, span(t, TE("in this series episode", 712.5)) + 0.25, *EP1_XY, scale=0.85, sound="pop")
img("stat-ep3", T("were going to do a check in", 713.2), 4.0, 1920, 250)
# v2 (Codex #2): "completely no human involvement" gets the real boundary on screen
img("stat-boundary", T("completely no human involvement", 722.6), 3.6, 1920, 250)
img("stat-recap", T("these guys are running it all on their own", 726.9), 5.0, 1920, 250)
t = T("please subscribe", 743.6)
img("cta-subscribe", t, round(TOTAL - 0.5 - cut_at(t), 3), 1920, 1850, sound="pop")

# chips and big moments also get the soft swish; the White Flash gets a boom, risers lead into the two reveals
sound_at("boom", cut_at(T_COLD_END, cold=True) - 0.02, 0.22)
for t_cut, vol in [(cut_at(T_COLD_END, cold=True), 0.10), (cut_at(end_before(SITE_CLICK)), 0.11)]:
    sfx.append({"path": str(AUD / "sfx-riser.wav"), "peak_at": round(t_cut - 0.04, 3), "volume": vol})
