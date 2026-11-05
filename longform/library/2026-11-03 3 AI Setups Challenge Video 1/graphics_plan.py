# Graphics timing for "3 AI Setups Challenge, Video 1", exec'd by gen_edl.py. Every card lands on the word that names
# it: T(phrase, hint) is the source second that phrase starts. All graphics are animated sequences (graphics/
# render_anim.mjs); the SFX peak sits on each one's "hit" frame. One sound per moment: a card placed with another stays
# silent. Chips land 0.65 s after their transition ends (output time).
# Zones: chips top-left; on the sites, cards in the right column above the facecam (the pages' own content sits left and
# centre); on the Obsidian canvas the rule list sits in the empty left margin; in talking head, cards go beside him
# (left or right column) or across his chest, never over his face.
T = lambda phrase, hint, cold=False: find(phrase, hint)[0]
TE = lambda phrase, hint: find(phrase, hint)[1]
span = lambda a, b, cold=False: round(cut_at(b, cold) - cut_at(a, cold), 3)
SC = 0.85


def man_w(n, sc=SC):
    return MAN[n]["w"] * sc


def tl(n, sc=SC):
    return round(60 + man_w(n, sc) / 2), round(200 + MAN[n]["h"] * sc / 2 - 110 * sc)


def right_col(n, y=760, sc=SC):
    """card's right edge 120 px in from the frame (its shadow still inside)"""
    return round(3720 - man_w(n, sc) / 2 + 110 * sc), y


def left_col(n, y=1080, sc=SC):
    return round(160 + man_w(n, sc) / 2 - 110 * sc), y


def zone(n, x0, x1, y, smax=0.85):
    """fit a card inside a measured clear zone x0..x1 (its visible card, not its 110 px padding), right-aligned"""
    sc = round(min(smax, (x1 - x0) / (MAN[n]["w"] - 220)), 3)
    return round(x1 - (MAN[n]["w"] / 2 - 110) * sc), y, sc


def zimg(n, t, d, z, **kw):
    x, y, sc = z
    return img(n, t, d, x, y, scale=sc, **kw)


# measured clear zones on the three sites (4K px, gridded frames probe/site_grid.jpg): Home Year's green area right of
# the planner and its month tabs; First Market Loadout's strip right of the yellow tag; Midnight Workshop's right of the
# envelope. Each one ends above the facecam (y < 1380).
HY, FML, MW = (3020, 3780), (3080, 3790), (2960, 3790)


def chip_after(name, t_voice, z=None):
    """0.65 s after the transition nearest t_voice has finished (placed in OUTPUT time, from the transition itself)"""
    tt, (_, d) = min(TRANSITIONS.items(), key=lambda kv: abs(cut_at(kv[0], cold=False) - cut_at(t_voice)) if kv[0] not in _cold_keys_ else 1e9)
    x, y, sc = (*tl(name), SC) if z is None else z
    img(name, t_voice, 2.6, x, y, scale=sc, sound="swish", vol=0.12, at=cut_at(tt) + d / 2 + 0.65)


_cold_keys_ = {end_of(j) for j in range(COLD_N)}


def at_keep(i, extra=0.0):
    return cut_at(KEEPS[i][0], cold=(KEEPS[i][2] == "cold")) + extra


def seq_swap(names, times, end, pos, sc=SC, sound="tick", first="swish"):
    """a card that relights in place: each version shows from its line to the next (only the first one animates in)"""
    for k, n in enumerate(names):
        a = times[k]
        b = end if k == len(names) - 1 else times[k + 1]
        im = img(n, a, span(a, b), *pos, scale=sc, sound=first if k == 0 else sound, vol=0.12 if k == 0 else 0.08)
        if im and k < len(names) - 1:
            im["noexit"] = True          # the next state takes over in place: no fade between states (Codex #8)


# ---- cold open: three products, then the title ------------------------------------------------------------------------
c0 = KEEPS[0][0]
img("cold-title", c0 + 0.1, span(c0 + 0.1, KEEPS[0][1], cold=True) + 0.05, 1920, 1760, scale=0.9, cold=True, sound="boom", vol=0.18)
for i, (k, n, zz) in enumerate([(1, "cold-paperclip", HY), (2, "cold-hermes", FML), (3, "cold-grok", MW)]):
    a, b = KEEPS[k][0], KEEPS[k][1]
    zimg(n, a + 0.12, span(a + 0.12, b, cold=True) - 0.03, zone(n, zz[0] - (300 if i == 2 else 0), zz[1], 500, 0.8), cold=True, sound="pop" if i == 0 else "tick")

# ---- hook (talking head; his face sits centre, x 1500-2300) ------------------------------------------------------------
TR = [T("grok", 2.9), T("hermes agent", 4.2), T("and paperclip ai", 5.2), TE("head to head", 7.5) + 0.6]
seq_swap(["team-1", "team-2", "team-3"], TR[:3], TR[3] + 1.2, (1920, 1830), sc=0.82, sound="pop", first="pop")
t = T("five ai agents on each team", 18.3)
img("agents-5", t, span(t, TE("on their own", 24.5)) + 0.4, *right_col("agents-5", 1000, 0.62), scale=0.62, sound="sparkle")
t = T("and run it 100", 22.3)
img("qual-goal", t, span(t, TE("ready to roll", 43.5)) + 0.3, *left_col("qual-goal", 1000, 0.95), scale=0.95, sound="tick", vol=0.08)
t = T("very little human interaction", 54.0)
img("stat-human", t, span(t, TE("their machine is running", 61.5)) + 0.2, 1920, 1820, scale=0.72, sound="pop")

# ---- 01 the kit ------------------------------------------------------------------------------------------------------
chip_after("chip-01", KEEPS[5][0])
t = T("we are over on the asgardagents", 110.8)
img("url-asgard", t + 1.2, 3.6, *right_col("url-asgard", 600, 0.8), scale=0.8, sound="type", vol=0.1)
t = T("five ai agents that are business savvy", 141.0)
img("stat-kit", t, span(t, TE("in their learning system", 154.5)) + 0.3, *right_col("stat-kit", 760, 0.7), scale=0.7)

# ---- 02 Paperclip ------------------------------------------------------------------------------------------------------
t = T("set up paperclipai", 180.5) if any(w[0] == "paperclipai" for w in WORDS) else T("set up", 181.0)
chip_after("chip-02", t)
t = T("this is what it looks like when you set up", 187.4)
img("lower-paperclip", t, span(t, TE("complete the questionnaire", 195.0)) + 0.5, *right_col("lower-paperclip", 760, 0.8), scale=0.8, sound="whoosh", vol=0.1)

# ---- 03 the rules (the Obsidian overview; the rule list in the left margin) --------------------------------------------
chip_after("chip-03", KEEPS[8][0])
LC = (round(160 + 1066 * 0.68 / 2 - 110 * 0.68), 1100)
t = T("six hours to build a business", 285.0)
img("rule-1", t, 6.0, *LC, scale=0.68, sound="swish", vol=0.12)
t = T("and at the end i will assist them", 288.3)
img("qual-human", t, span(t, TE("but that will be it", 293.5)) + 1.2, *right_col("qual-human", 330, 0.85), scale=0.85, sound="tick", vol=0.08)
RT = [T("every one of them will have exactly six hours", 345.9), T("it must be a digital download", 359.5), T("they will get a 100 budget", 372.5),
      T("so the digital download can only be", 393.5), T("theres no top ups", 407.2), T("honest marketing", 412.0)]
seq_swap([f"rule-{i}" for i in range(1, 7)], RT, TE("the old fashioned way", 418.0) + 0.3, LC, sc=0.68)
BT = [T("a live website", 428.0), T("a checkout", 431.5), T("auto delivery", 436.3), T("autopilot", 443.0)]
seq_swap([f"build-{i}" for i in range(1, 5)], BT, TE("in 30 days", 460.5) + 0.3, LC, sc=0.68)
t = T("at six hours no matter what", 493.0)
img("stat-deadline", t, span(t, TE("out of the running", 503.7)) + 0.3, *right_col("stat-deadline", 640, 0.7), scale=0.7, sound="impact", vol=0.13)
t = T("go ahead and subscribe now", 515.5)
img("subscribe", t, 3.4, *right_col("subscribe", 300, 0.66), scale=0.66, sound="pop")
ST = [T("obviously sales is very important", 524.5), T("their profit", 530.5), T("how much help did i give them", 550.0)]
seq_swap(["score-1", "score-2", "score-3"], ST, TE("all by itself", 563.5) + 0.3, *[right_col("score-1", 760, 0.62)], sc=0.62)

# ---- 04 three teams ------------------------------------------------------------------------------------------------------
chip_after("chip-04", SCENE_AT[2])
t = T("odin here should be our orchestrator", 598.3)
img("stat-odin", t, span(t, TE("he is the lead", 600.8)) + 0.6, *right_col("stat-odin", 760, 0.66), scale=0.66)
t = T("were running claude opus", 602.0)
img("lower-paperclip", t, span(t, TE("for all agents", 611.5)) + 0.2, *right_col("lower-paperclip", 1100, 0.8), scale=0.8, sound="whoosh", vol=0.1)
t = T("all right we are in hermes", 635.6)
img("lower-hermes", t + 0.9, span(t + 0.9, TE("speedrun this", 643.0)) + 0.2, *right_col("lower-hermes", 760, 0.8), scale=0.8, sound="whoosh", vol=0.1)
t = T("hermes agent and grok", 645.0)
img("lower-grok", t + 0.6, span(t + 0.6, TE("what their job is", 657.8)), *right_col("lower-grok", 1100, 0.8), scale=0.8, sound="whoosh", vol=0.1)
t = T("you can see all three platforms", 678.3)
img("team-3", t, span(t, TE("obviously running grok", 692.0)) + 0.2, 1700, 1820, scale=0.72, sound="pop")
t = T("fire off these prompts", 697.6)
img("stat-go", t, span(t, TE("with the same rules", 703.5)) + 0.4, *right_col("stat-go", 760, 0.68), scale=0.68)

# ---- 05 the build: the clock spans the whole time-lapse ----------------------------------------------------------------
t0 = at_keep(12)
img("clock", 0, round(at_keep(16) - t0 - 0.75 - 0.35, 3), 1920, 1080, scale=0.9, sound="riser", vol=0.1, at=t0 + 0.75)

# ---- 06 six hours later (talking head, part B: face centre) ------------------------------------------------------------
chip_after("chip-06", KEEPS[16][0])
t = T("i would say paperclip and grok", 1285.1)
t2 = T("those have to be done by myself", 1310.0)
img("disclose-touch", t, span(t, t2), *left_col("disclose-touch", 1080, 0.9), scale=0.9, sound="tick", vol=0.1)
img("disclose-polish", t2, span(t2, end_of(16)) - 0.3, *left_col("disclose-polish", 1080, 0.9), scale=0.9, sound="tick", vol=0.08)

# ---- 07 Home Year (Paperclip) --------------------------------------------------------------------------------------------
chip_after("chip-07", KEEPS[17][0])
t = T("here we are in the business", 1324.0)
zimg("url-paperclip", t + 2.6, 3.8, zone("url-paperclip", *HY, 420, 0.8), sound="type", vol=0.1)
t = T("this was designed all by claude code", 1336.8)
zimg("pill-post", t, span(t, TE("claude code opus 5 5", 1338.5)) + 1.5, zone("pill-post", *HY, 420, 0.8), sound="tick", vol=0.08)
t = T("its a printable pdf", 1361.8)
zimg("stat-zip", t, span(t, TE("all these things", 1370.0)) + 0.3, zone("stat-zip", *HY, 520, 0.7))
t = T("all you do is buy it for 12", 1373.0)
im = zimg("prod-paperclip", t, span(t, TE("downloadable checklist it looks like", 1384.0)) + 0.3, zone("prod-paperclip", *HY, 560, 0.7), sound=None)
sound_at("coin", im["start"] + 0.72, 0.12)          # on the price, not the empty card (Codex #14)
t = T("the link works for 168 hours", 1439.0)
zimg("stat-168", t, span(t, TE("they could have said days", 1446.4)) + 0.6, zone("stat-168", 2900, 3780, 520, 0.7))
t = T("that is home year by paperclip", 1525.5)
zimg("sum-paperclip", t, span(t, end_of(17)) - 0.35, zone("sum-paperclip", 2900, 3780, 620, 0.85), sound="whoosh", vol=0.08)

# ---- 08 First Market Loadout (Hermes) --------------------------------------------------------------------------------------
chip_after("chip-08", KEEPS[18][0], zone("chip-08", *FML, 230, 0.7))         # the hero headline owns the top-left
t = T("this is going to be the hermes project", 1542.0)
zimg("url-hermes", t + 1.6, 3.8, zone("url-hermes", *FML, 520, 0.8), sound="type", vol=0.1)
t = T("hermes went with 9", 1580.4)
im = zimg("prod-hermes", t, span(t, TE("for the sale", 1582.6)) + 2.0, zone("prod-hermes", *FML, 640, 0.7), sound=None)
sound_at("coin", im["start"] + 0.72, 0.12)
t = T("this is an unfinished", 1713.0)
zimg("stat-test", t, span(t, TE("activate stripe", 1718.4)) + 0.4, zone("stat-test", *FML, 520, 0.7), sound="tick", vol=0.1)
t = T("so that is hermes", 1723.8)
zimg("sum-hermes", t, span(t, end_of(18)) - 0.35, zone("sum-hermes", *FML, 640, 0.85), sound="whoosh", vol=0.08)

# ---- 09 Midnight Workshop (Grok Bot) --------------------------------------------------------------------------------------
chip_after("chip-09", KEEPS[19][0], (*tl("chip-09", 0.62), 0.62))
t = T("and here we are on the grok project", 1735.3)
zimg("url-grok", t + 1.0, 3.8, zone("url-grok", *MW, 420, 0.8), sound="type", vol=0.1)
t = T("one time payment", 1786.0)
im = zimg("prod-grok", t - 0.6, span(t - 0.6, TE("no refunds it says", 1795.5)) + 0.5, zone("prod-grok", *MW, 600, 0.75), sound=None)
sound_at("coin", im["start"] + 0.72, 0.12)
t = T("12 hint cards", 1851.5)
zimg("stat-puzzles", t, span(t, TE("two for each puzzle", 1854.0)) + 1.2, zone("stat-puzzles", *MW, 520, 0.7))
t = T("so grok came up with a holiday escape room", 1894.5)
zimg("sum-grok", t, span(t, end_of(19)) - 0.35, zone("sum-grok", *MW, 620, 0.85), sound="whoosh", vol=0.08)

# ---- 10 the verdict and the outro ------------------------------------------------------------------------------------------
PT = [T("so paperclip 12", 1908.1), T("hermes went with nine", 1913.8), T("and grok went with nine", 1914.9)]
seq_swap(["price-1", "price-2", "price-3"], PT, TE("opus wants more money", 1922.0) + 0.4, (1920, 1080), sc=0.8, sound="coin", first="coin")
t = T("i guess we will see in 30 days", 1927.5)
img("recap", t, span(t, TE("trying to sell", 1945.0)), 1920, 1830, scale=0.74, sound="whoosh", vol=0.1)
t = T("each one will have live payments", 1986.6)
img("qual-test", t, span(t, TE("fully functional", 1996.5)) + 0.3, *left_col("qual-test", 1000, 0.95), scale=0.95, sound="tick", vol=0.08)
t = T("go ahead and like and subscribe", 1998.0)
img("subscribe", t, span(t, TE("30 day video coming up", 2004.0)) + 0.6, left_col("subscribe", 1080, 0.62)[0], 1700, scale=0.62, sound="pop")
t = T("remember these were completely made", 2012.6)
img("disclose-polish", t, span(t, TE("for the domain", 2024.5)) + 0.6, *left_col("disclose-polish", 880, 0.9), scale=0.9, sound="tick", vol=0.08)
t = T("they only spent 1208 each", 2021.0) if any(w[0] == "1208" for w in WORDS) else T("they only spent", 2021.0)
img("stat-domains", t, span(t, TE("for the domain", 2024.5)) + 0.6, *left_col("stat-domains", 1560, 0.72), scale=0.72, sound=None)

# ---- masks: third-party X handles in Grok Bot's old chat (picture 645-662) -----------------------------------------------
# the window is open from picture 648.8 to 664.2 (frames5 region mean); the patch covers the message column only
mask("mask-grokchat", (2540, 300, 3600, 1420), 652.0, 648.7, 664.4)
