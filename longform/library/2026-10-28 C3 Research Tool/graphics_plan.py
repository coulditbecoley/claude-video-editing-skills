# Graphics timing for "C3 Research: the AI agents' token audit tool", exec'd by gen_edl.py.
# Every card lands on the word that names it: T(phrase, hint) is the source second that phrase starts.
# hl() is a glowing lime box on the exact screen element he's reading (source px, measured on gridded frames at that
# picture time, probe/g1 and probe/g2; mt = the measured picture second), held only while the page under it is still.
# A box placed with a card stays silent so the moment gets one sound. Chips land 0.75 s after their transition.
# Full-frame pages (the landing page, the request form, the affiliate page) take their cards in the empty left
# column (x < 780), sliding in from that side (Ep 2 rule). Sounds: pop on stats, coin on money, swish on chips and
# slides, sparkle on logos, tick on boxes and step changes, impact once (the cold open's dead stop).
T = lambda phrase, hint: find(phrase, hint)[0]
TE = lambda phrase, hint: find(phrase, hint)[1]
span = lambda a, b, cold=False: round(cut_at(b, cold) - cut_at(a, cold), 3)
LEFT = (380, 1150)          # the left column of the c3research.io pages
SC_L = 0.85
CHIP_D = 2.4
LIME = (204, 255, 0)
tr_at = lambda p: next(v for (pp, *_), v in zip(SCENES, SCENE_AT) if abs(pp - p) < 0.01)   # voice second of a page change

def chip_after(name, t_voice, extra=None):
    """a chapter chip 0.65 s after its transition has finished (qa.py: start > cut + duration + 0.6)"""
    d = next((dd for tt, (_, dd) in TRANSITIONS.items() if abs(tt - t_voice) < 0.6), 0.0)
    img(name, t_voice, CHIP_D, *TOP_L, pop="slide_l", sound="swish",
        at=cut_at(t_voice) + (extra if extra is not None else d + 0.65))   # placed in OUTPUT time: a cut right after the
    # transition would otherwise pull it back into the transition

def seq(names, times, end, pos, scale=SC_L, side="slide_l", vol=None):
    """A card that swaps its lit step in place: slides in on the first, plain swaps (tick) after, slides out last."""
    for k, n in enumerate(names):
        last = k == len(names) - 1
        pop = f"{side}_in" if k == 0 and not last else (f"{side}_out" if last and k else (side if k == 0 else False))
        a, b = times[k], (end if last else times[k + 1])
        img(n, a, span(a, b), *pos, scale=scale, pop=pop, sound="swish" if k == 0 else "tick", vol=vol if k == 0 else 0.07)

# ---- cold open: the report's deep dive, then the unverified tags ------------------------------------------------
t = T("this is a very deep dive", 285.0)
img("cold-deep", t + 0.15, span(t + 0.15, KEEPS[0][1], cold=True) - 0.1, *SLOT_TOP, cold=True, pop="in", sound="swish")
t_tags = T("it will give you unverified tags", 298.5)
t_scam = T("doesnt mean scam", 302.3)
img("cold-tags", t_tags + 0.3, span(t_tags + 0.3, t_scam - 0.25, cold=True), *SLOT_TOP, cold=True, pop="in", sound="tick")
img("cold-scam", t_scam - 0.25, span(t_scam - 0.25, KEEPS[1][1], cold=True) - 0.1, *SLOT_TOP, cold=True, pop="in", sound=None)   # the impact carries it

# ---- hook (talking head): premise above his head, the three things it reads across his chest -------------------
t_h = T("this is a meme coin", 2.1)
img("hook-title", t_h + 1.0, span(t_h + 1.0, TE("assist you in your aping", 8.5)) + 0.35, 1920, 250, scale=0.86, vol=0.14)
img("logo-c3", T("the c3 research audit tool", 12.72), 3.4, *TOP_R, pop="slide_r", sound="sparkle")
QS = [T("their website", 28.3), T("their social media accounts", 30.0), T("their contract address", 32.6), TE("their contract address", 32.6) + 0.7]
seq(["hook-q1", "hook-q2", "hook-q3"], QS[:3], QS[3], (1920, 1880), scale=0.8, side="slide_up")
t = T("all you have to do", 34.5)
img("stat-paste", t, span(t, TE("for you in a nice clean report", 41.0)) + 0.2, 1920, 280, scale=0.82)
t = TE("for you in a nice clean report", 41.0) + 0.3
img("stat-nfa", t, span(t, T("come with me", 43.5)) + 0.4, 1920, 280, scale=0.72, pop="slide_down", sound="swish", vol=0.1)

# ---- 01 the Agents Window ---------------------------------------------------------------------------------------
chip_after("chip-agents", KEEPS[3][0], 0.6 + 0.65)
hl((40, 296, 2912, 1228), T("these are actually the ai agents", 69.8) + 0.2, 3.6, fixed=True)
img("stat-email", T("email them", 78.9) - 0.4, 3.4)
t = T("into their agent world", 90.6)
hl((2370, 44, 2640, 260), t, 2.6, sound=False, fixed=True)
img("stat-world", t, 3.0)
hl((50, 1264, 1150, 1880), T("their own token", 95.38), 1.6, fixed=True)
hl((1190, 1264, 2000, 1860), T("their other businesses", 96.82), 1.6, fixed=True)
hl((50, 1916, 1750, 2004), T("their sponsorship bar", 98.2), 2.4, fixed=True)
img("url-window", T("on the asgardagents", 100.3), 3.0, 1920, 330, scale=0.8, pop="slide_down", sound="swish")
hl((2060, 1264, 2890, 1860), T("this is a video about", 105.4), 2.9, fixed=True)

# ---- 02 the tool: the landing page plays full-frame -------------------------------------------------------------
# the "Try it" click blanks the page for ~3 s (picture 109.2-112.2): a still of the settled landing page covers it,
# swapped in at the end of the Swipe so the swipe itself shows (the loading reads as the page finishing its load)
v_land = tr_at(109.2)
cover("cover-landing", 112.25, v_land + 0.2, 112.2)
chip_after("chip-tool", KEEPS[4][0], 0.3)   # no transition here (the Swipe was 6 s earlier)
img("stat-independent", T("assist you in your investigation", 118.4), 4.0, *TOP_R, pop="slide_r")
ST = [T("start with an address", 140.6), T("it follows the evidence", 142.0), T("spits out a report", 143.4), TE("when it is done", 146.6) + 0.2]
seq(["steps-1", "steps-2", "steps-3"], ST[:3], ST[3], LEFT)
TG = [T("confirmed", 147.8), T("not established", 148.6), T("unverified", 149.6), TE("as the tag on the information", 152.5) + 0.3]
seq(["tags-1", "tags-2", "tags-3"], TG[:3], TG[3], LEFT)
img("stat-7days", T("for seven days", 160.6), 4.6, *TOP_R, pop="slide_r")
img("logo-x", T("follow along on x", 173.7), 3.6, *TOP_R, pop="slide_r", sound="sparkle")

# Boxes dropped because the page scrolls under them (no 1.5 s still run): the DexScreener line (205.6), the price
# (233.3), the claim-matrix UNVERIFIED row (298.7) and the rugcheck line (331.9); their cards and punch-ins carry them.
# ---- 03 request a report: the form plays full-frame (wallet and payment, confirmed) ------------------------------
chip_after("chip-request", tr_at(191.0))
RQ = [T("you just find any token", 192.84), T("choose how you would like to pay", 210.1), T("hit the pay button", 232.6),
      T("once that research is complete", 236.2), tr_at(242.183) - 0.35]
seq(["req-1", "req-2", "req-3", "req-4"], RQ[:4], RQ[4], LEFT)
t = T("ethereum", 196.0)
hl((1130, 1075, 1900, 1180), t, 3.0, sound=False, mt=196.97)
img("chains", t - 0.2, 3.6, *TOP_R, scale=0.78, pop="slide_r", sound="sparkle")
t = T("deckscreener", 206.0)
img("logo-dex", t - 0.4, 3.2, *TOP_R, pop="slide_r", sound="sparkle")
hl((1140, 1585, 2235, 1640), T("credit card", 215.6) + 0.2, 1.8, mt=216.67)
img("logo-stripe", T("stripe", 217.1) - 0.1, 3.2, *TOP_R, pop="slide_r", sound="sparkle")
img("stat-card", T("you can use a credit card", 224.5), 3.8, *TOP_R, pop="slide_r")
t = T("pay button", 232.8)
img("stat-19", t - 0.2, 3.4, *TOP_R, pop="slide_r", sound="coin")

# ---- 04 the research library -----------------------------------------------------------------------------------
chip_after("chip-library", tr_at(242.183))
img("stat-library", T("you can see some audits", 244.4), 3.6, *TOP_R, pop="slide_r")

# ---- 05 inside a report (Light Leaks in on the "uh" cut) --------------------------------------------------------
chip_after("chip-report", 250.45, 1.45)   # the Light Leaks sits on the 250.45 cut
img("card-asgard", T("this is the actual agents token", 253.0), 2.3, *TOP_R, pop="slide_r", sound="sparkle")
t = T("download it as a pdf", 255.9)
hl((1120, 1340, 1520, 1430), t + 0.2, 2.6, sound=False, mt=256.7)
img("card-pdf", t, 3.4, *TOP_R, pop="slide_r")
hl((1100, 770, 1400, 870), T("you can see the network", 268.8), 1.6, mt=270.43)
hl((1650, 770, 2200, 880), T("the contract address", 270.4), 1.6, mt=270.43, sound=False)   # one tick per row: the
# three land 0.8-1.6 s apart and a tick each read as clutter; the completion date box was skipped (he scrolls at 271.6)
hl((1090, 870, 1490, 1710), T("go down to the index", 274.0), 3.2, mt=275.63)
t = T("it will give you unverified tags", 298.5)
img("cold-tags", t + 0.3, 2.8, *SLOT_TOP, pop="in", sound="tick")
img("stat-unverified", T("doesnt mean scam", 302.3) - 0.2, 4.6)
img("logo-rug", T("rug check here", 314.6) - 0.1, 3.4, *TOP_R, pop="slide_r", sound="sparkle")
t = T("here we go rug check", 331.7)
img("stat-rug", t + 0.2, 2.6, sound=None)   # the RugCheck logo already sparkled; one sound per point
img("stat-live", T("while it is live", 337.1), 3.6)

# ---- 06 a fresh review ----------------------------------------------------------------------------------------
chip_after("chip-fresh", tr_at(354.9))
t = T("that its older than seven days", 357.9)
hl((1090, 1110, 2730, 1350), t, 3.0, sound=False, mt=359.2)
img("stat-outdated", t + 0.5, 3.4, 1900, 1890, scale=0.75, pop="slide_up")   # low: top-right covered "HOOKR" on the punch-in
hl((1120, 1380, 1520, 1480), 361.30, 2.4, mt=362.43)   # the piece before ends at the "a, a" cut (360.99)
t = T("it just takes the same token address", 363.6)
hl((1120, 1490, 2140, 1570), t + 0.3, 3.4, sound=False, mt=362.43)
img("stat-rerun", t, 5.0, 1900, 1890, scale=0.75, pop="slide_up")
img("stat-rerun", T("you can get a refresh", 373.6), span(T("you can get a refresh", 373.6), TE("is already there if you would like", 376.2)) - 0.1,
    1920, 330, scale=0.8, sound=None)   # v2 (Codex #4): back on screen for the spoken "refresh"
img("recap-tool", T("that is the tool in a nutshell", 379.4), 2.6, 1920, 330, scale=0.85, pop="slide_down", sound="swish")

# ---- 07 the affiliate program: full-frame page, cards in the left column ------------------------------------------
chip_after("chip-affiliate", tr_at(386.4))
AF = [T("you can apply to become an affiliate", 404.1), T("you just share your link", 415.1),
      T("you make money on every single report", 419.6), TE("from your link or qr code", 424.5) + 0.6]
seq(["aff-1", "aff-2", "aff-3"], AF[:3], AF[3], LEFT)
hl((980, 950, 1860, 1140), AF[0] + 0.3, 2.6, sound=False, mt=406.1)
hl((980, 1020, 1860, 1200), 416.30, 2.6, sound=False, mt=416.67)   # after his scroll
hl((980, 1090, 1860, 1260), AF[2] + 0.3, 2.8, sound=False, mt=422.27)
img("stat-approve", T("the agents will approve or deny", 407.9), 4.0, *TOP_R, pop="slide_r")
img("stat-commission", T("you make money on every single report", 419.6) + 0.4, 4.6, *TOP_R, pop="slide_r")   # no coin under an earnings condition
t = T("because you dont really know the facts", 442.3)
img("stat-claims", t, span(t, TE("this tool will tell you that", 446.5)) + 0.5, *TOP_R, pop="slide_r")   # v2 (Codex #4): through the claim

# ---- 08 follow on X: the X piece opens on its loading skeleton; a still of the loaded profile swaps in at the end of
# the Swipe and holds until the live page matches it (picture 461.5-461.9 is still)
cover("cover-x", 461.7, KEEPS[6][0] + 0.23, 461.88)
chip_after("chip-x", KEEPS[6][0], 0.45 + 0.65)
img("stat-news", T("you will get these all day every day", 476.3), 3.6)
img("logo-x", T("be sure to follow c3 research on x", 483.9), 3.4, *TOP_R, pop="slide_r", sound="sparkle")

# ---- outro (talking head): nothing over the face; a calm exit --------------------------------------------------
img("stat-goal", T("in their main goal of becoming profitable", 517.2), 2.5, 1920, 250, scale=0.8)
img("url-c3", T("check out the c3 research tool", 520.5), 3.4, 1920, 250, scale=0.8, pop="slide_down", sound="swish")
t = T("become an affiliate or at least sign up", 532.6)
img("stat-affiliate", t, span(t, TE("its passive for you", 544.4)) - 0.05, 1920, 250, scale=0.8)   # v2 (Codex #4): through "paid for each report... passive"
for a_, b_ in ((T("a safe and secure tool", 527.0), TE("meme coin token audits", 531.0)),
               (T("agents are providing a service", 546.4), TE("lots of money and time", 551.5))):
    img("stat-limits", a_, span(a_, b_) + 0.2, 1920, 250, scale=0.8, sound=None)   # v2 (Codex #3): "safe and secure", "safer"
img("cta-subscribe", T("go ahead and subscribe", 556.0), 2.6, 1920, 1850, scale=0.8)
t = T("go check out the agents window update", 558.5)
img("thumb-day35", t, round(TOTAL - 1.4 - cut_at(t), 3), 3010, 640, scale=0.62, pop="slide_r", sound="swish")

# ---- the big moments: the cold open's "doesn't mean scam" is the punchline (the music stops dead under it,
# music_plan.py); the White Flash out of it gets a riser and a boom
sound_at("impact", cut_at(t_scam, cold=True) - 0.05, 0.17)
sound_at("boom", cut_at(T_COLD_END, cold=True), 0.22)
sfx.append({"path": str(AUD / "sfx-riser.wav"), "peak_at": q(cut_at(T_COLD_END, cold=True)), "volume": 0.10})
