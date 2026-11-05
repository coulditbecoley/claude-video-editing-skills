# Graphics timing for Asgard Agents Day 20 (v3), exec'd by gen_edl.py.
# Every card lands on the word that names it: T(phrase, hint) is the source second that phrase starts.
# v3 adds hl(): a glowing gold box on the exact screen element he's talking about (source pixels, mapped
# through the piece's punch-in), each placed inside a still stretch so it never sits on a moving page.
T = lambda phrase, hint: find(phrase, hint)[0]
TE = lambda phrase, hint: find(phrase, hint)[1]
LOWL = (1500, 1800)       # bottom-left of centre, clear of the facecam (x 2920+)
span = lambda a, b, cold=False: round(cut_at(b, cold) - cut_at(a, cold), 3)

# cold open: Thor holds the keys, not even Coley
img("stat-thor-only", T("taken care of by thor", 213) + 0.6, 3.4, *STAT, cold=True)
img("stat-not-coley", T("not even myself", 222.8), span(T("not even myself", 222.8), TE("or even my own", 229.6), True), *STAT, cold=True, sound="hit")
# hook (talking head): the premise above his head, the five agents across his chest
t_h = T("this is day 20 update", 13)
img("hook-title", t_h, span(t_h, TE("a week ago", 21)), 1920, 250, scale=0.95)
for k, n in enumerate(["odin", "thor", "loki", "mimir", "heimdall"]):
    t0 = T("of the asgard agents", 14.4) + 0.1 * k
    img(f"agent-{n}", t0, span(t0, TE("a week ago", 21)), 1080 + 420 * k, 1800, scale=0.85, sound="pop" if k == 0 else None)
img("logo-obsidian", T("jump into the canvas", 36), 2.2, *TOP_R)

# 01 what's new
img("chip-new", FIRST_SCREEN + 1.4, 2.8, *TOP_L)
img("stat-sale", T("first sale", 92.4), 3.2, 1920, 1820)
hl((703, 883, 1421, 1267), T("first sale", 92.4), 3.2)                       # scoreboard: "1st sale"
img("card-paperrows", T("called paper rows", 93.9), 2.8, *TOP_R)
img("stat-asgard", T("their own asgard token", 103.9), 3.2, 1500, 1820)
hl((2254, 883, 2976, 1267), T("their own asgard token", 103.9), 3.2)         # scoreboard: "ASGARD"
img("stat-pay", T("every minute that they work", 119.6) + 0.5, 3.4, *STAT)
# follow along
for k, (n, ph, hint) in enumerate([("telegram", "telegram", 134.5), ("farcaster", "farcaster", 135.1),
                                   ("bluesky", "blue sky", 136.0), ("discord", "discord", 137.4)]):
    t0 = T(ph, hint)
    img(f"soc-{n}", t0, span(t0, TE("clearly marked", 150)), 2340 + 360 * k, 300, scale=0.9)
hl((768, 818, 1786, 1797), T("telegram", 134.5), 4.0, sound=False)          # the canvas's follow-along column
img("site-card", T("asgardagents com", 145.0), 3.2, 2650, 760)

# 02 they catch their own mistakes
img("chip-mistakes", T("up next this is just more things", 151.5) + 0.3, 2.8, *TOP_L)
hl((1574, 818, 2611, 1824), 158.9, 2.6)  # the mistakes column
img("stat-heimdall", T("thats their job", 160.1), 2.6, 1920, 1820)
img("stat-test", T("they always test everything", 169.4), 2.8, 1920, 1820)
img("stat-payday", T("october 14th will be their first payday", 176.4), 3.6, 2200, 330)
hl((518, 1701, 1478, 2008), T("october 14th will be their first payday", 176.4), 2.0)   # What's next: "First payday"

# 03 behind the scenes
img("chip-behind", T("behind the scenes things that have been updated", 198.5) + 0.2, 2.6, *TOP_L)
img("card-thor", T("by thor", 215.2), 3.0, *TOP_R)
img("stat-locked", T("security clearance", 219), 3.2, *STAT)
hl((1793, 730, 2730, 979), T("not even myself", 222.8), 3.0)                 # "A locked signing service"
img("stat-wallet2", T("not even myself", 222.8) + 0.2, 3.4, 1700, 1820)
hl((1797, 1037, 2734, 1286), T("they made animations", 256.9), 2.2)         # "Arcade cabinets"
img("stat-arcade", T("video game arcade style", 259.5), 3.0, 1700, 1820)

# 04 what's next: the turn away from meme coins is the punchline (music dies, impact)
img("chip-next", T("now their goal is to grow their newest business", 269) + 1.4, 2.6, *TOP_L)
img("stat-nomeme", T("no longer creating meme coins", 280.6), 3.6, *STAT, sound="hit")
img("card-paperrows2", T("running their paper rows", 286.3), 3.2, *TOP_R)
hl((1363, 1079, 2592, 1490), 287.3, 3.0, sound=False)                       # "Grow PaperRows"
img("stat-browser", T("their proudest moment", 293.2) + 0.3, 2.6, *STAT)
img("stat-nextbiz", T("there is another business", 309) + 0.6, 3.2, *STAT)
hl((1797, 1025, 3034, 1440), T("there is another business", 309) + 0.6, 3.0, sound=False)   # "Next business"
img("card-email", T("you can even email these guys", 332.5) + 0.4, 3.0, *STAT)

# 05 the Agents Window (after the swipe)
img("chip-window", T("and here we are in the agents window", 351) + 1.0, 2.6, *TOP_L)
hl((45, 495, 1815, 900), T("these guys are sleeping", 366.3), 3.0)          # Odin, Thor, Loki asleep by the fire
img("stat-sleep", T("these guys are sleeping", 366.3) + 0.4, 3.2, *LOWL)
hl((1245, 375, 1815, 1320), T("loki on a computer", 391.8), 3.0, sound=False)
img("card-loki", T("loki on a computer", 391.8), 3.0, 1700, 1820)
hl((45, 1365, 1185, 1980), T("token and payroll", 402.4), 3.0)              # Token and Payroll panel
img("stat-payroll", T("token and payroll", 402.4), 3.0, *STAT)
img("stat-hire", T("outside work done by other ai agents", 418.7), 3.6, *STAT)
img("stat-hire2", T("buying a pdf", 437.7), 3.6, *STAT)
hl((60, 1635, 1155, 1920), T("down here is the chart", 455.5), 3.0)         # the Pump.fun chart
img("logo-pumpfun", T("launched on pumpfun", 462.6), 3.0, *TOP_R)
hl((60, 1440, 1155, 1515), T("you will see their wallets", 474.8), 3.0, sound=False)   # per-agent pay tiles
img("stat-wallets", T("you will see their wallets", 474.8), 3.4, *STAT)
hl((1230, 1365, 2100, 1980), T("their newest business", 485.2), 2.6)        # Businesses: PaperRows

# 06 PaperRows (the landing page plays full frame; cards sit low, clear of the headline)
img("chip-paperrows", PAPERROWS_CLICK + 1.0, 2.6, *TOP_L)
img("stat-series", T("completely new youtube series", 494.6), 3.4, 1700, 1820)
img("cta-subscribe", T("completely new youtube series", 494.6) + 0.8, 2.6, 3060, 330, scale=0.6)   # the one mid-video ask
img("stat-handle", T("they could handle everything from", 516.0), 3.4, 1700, 1820)
hl((855, 924, 1824, 1344), T("you put in your bank statement", 545.5), 3.0) # "Choose a statement PDF"
hl((860, 1672, 2022, 2022), T("readable csv", 553.3), 3.0, sound=False)     # the plain CSV output
img("formats", T("google spreadsheet", 561.5) - 1.6, 3.4, 3380, 820, scale=0.66)
img("stat-never", T("your statements stay on your computer", 571.9), 3.2, 1920, 420, scale=0.8)
hl((860, 985, 1905, 1404), T("your statements stay on your computer", 571.9), 3.2, sound=False)   # "Stays in your browser"
img("stat-servers", T("server located", 578.4), 3.0, 1920, 1820)
hl((1598, 756, 2246, 1447), T("one time fee", 624.9), 1.2)                   # "$5 per statement"
hl((2281, 756, 2959, 1447), T("sign up for monthly", 626.2), 3.0)           # "$19 a month"
img("stat-price", T("you just pay your one time fee", 624.1), 3.4, 1700, 1820)
img("stat-support", T("customer service", 649.0) - 1.4, 3.0, 1700, 1820)

# 07 the next business (C3 Research) and 08 their socials
img("chip-c3", T("you can see a blank box here", 668.7) + 0.6, 2.6, *TOP_L)
hl((2160, 1365, 3030, 1980), T("you can see a blank box here", 668.7) + 0.3, 3.0)   # "Coming soon"
img("logo-c3", T("c3 research", 681.7), 3.2, *TOP_R)
img("stat-idea", T("but it was my idea", 690.3), 3.2, *STAT)
img("stat-c3", T("you put in the token ca", 702.6), 3.2, *STAT)
img("site-c3", T("c3research io is the website", 711.8), 2.8, 2650, 760)
img("chip-socials", T("we do have the social media accounts", 725), 2.6, *TOP_L)
hl((3050, 290, 3800, 370), T("social media accounts", 726.1), 3.0)          # Telegram, Farcaster, Bluesky, Discord
img("stat-three", T("but these other three", 746), 3.6, *LOWL)

# 09 Paperclip (after the swipe; the board plays full frame)
img("chip-paperclip", T("all of this is run inside of paperclip", 776.4) + 1.0, 2.6, *TOP_L)
img("logo-paperclip", T("paperclip ai", 778.1), 3.0, 2500, 1750)
img("stat-boundary", T("usage limit", 802.3), 3.6, 1600, 1800)

# outro: recap before the ask, one card at a time, nothing over the face
img("stat-recap", T("that is day 20 update", 812.1) + 0.6, 3.6, *STAT)
img("cta-subscribe", T("be sure to follow along", 822.4), 2.6, 1920, 1760)
img("site-card", T("asgardagents com is the place to go", 834.3), 3.2, *LOW)
img("card-paperrows", T("paper rows is your place", 869.8), 2.6, *LOW, scale=0.85)
img("logo-c3", T("c3 research is your place", 877.6), 2.6, *LOW, scale=0.85)

# chapter chips get the same whoosh as the transitions, quieter (one sound palette for the whole video)
for im_ in list(images):
    if Path(im_["path"]).stem.startswith("chip-"):
        sfx.append({"path": str(AUD / "sfx-whoosh.wav"), "peak_at": round(im_["start"] + 0.05, 3), "volume": 0.12})
