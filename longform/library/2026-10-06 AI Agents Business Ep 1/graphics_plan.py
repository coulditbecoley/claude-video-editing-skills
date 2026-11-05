# Graphics timing for AI Agents Business Ep 1 (v2, after the Codex audit), exec'd by gen_edl.py.
# Every card lands on the word that names it: T(phrase, hint) is the source second that phrase starts.
T = lambda phrase, hint: find(phrase, hint)[0]
TE = lambda phrase, hint: find(phrase, hint)[1]
PROMPT_AT = (1500, 1850)     # bottom-left, clear of the facecam
ROUND_AT = (1540, 1880)      # the review cards sit bottom-left too, larger than v1's tracker

# cold open
img("stat-nogo", T("affirm nogo", 1249), 3.0, *STAT, cold=True, sound="hit")
img("stat-go", T("go with changes", 1586), 3.2, *STAT, cold=True)
# hook (talking head): the premise above his head, the five agents across his chest
img("hook-title", T("five ai agents starting", 11), round(cut_at(TE("here we go", 19)) - cut_at(T("five ai agents starting", 11)), 3), 1920, 250, scale=0.95)
for k, n in enumerate(["odin", "thor", "loki", "mimir", "heimdall"]):
    t0 = T("starting their own business", 12) + 0.3 * k
    img(f"agent-{n}", t0, round(cut_at(TE("here we go", 19)) - cut_at(t0), 3), 1080 + 420 * k, 1800, scale=0.85, sound="pop" if k == 0 else None)
# 01 the ask
img("chip-ask", T("were in our terminal", 92) + 0.9, 2.6, *TOP_L)
img("logo-claude", T("we do have claude", 93.5), 2.8, *TOP_R)
img("logo-codex", T("and codex open here", 95), 2.6, 3240, 700)
img("prompt-1", T("we are starting a brand new agent run business", 149) + 0.7, -0.7 + round(cut_at(TE("they could conduct now", 170)) - cut_at(T("we are starting a brand new agent run business", 149)), 3), *PROMPT_AT, scale=1.0)
# 02 Claude's first ideas
img("chip-ideas", T("and we have come back with some research", 243) + 0.4, 2.6, *TOP_L)
img("idea-api", T("number one paid data api", 296), 3.6, *STAT)
img("ideas-avoid", T("avoid faceless youtube", 366), 6.5, 3160, 640, scale=1.0)
# 03 enter Codex
img("chip-codex", T("so guys this is where we get codex involved", 413), 2.6, *TOP_L)
img("stat-disagree", T("they do not always agree", 423), 3.0, *STAT)
img("ff-badge", 460.9, 2.0, *TOP_L, sound=None)
img("round-1", T("and the codex audit is complete", 551) + 1.0, 4.0, *ROUND_AT, scale=0.9)
img("stat-zero", T("dont plan for zero humans", 585), 3.0, *STAT)
img("prompt-2", T("this business needs to be 100", 667), round(cut_at(TE("not the business for us", 679)) - cut_at(T("this business needs to be 100", 667)), 3), *PROMPT_AT, scale=1.0)
img("logo-stripe", T("they do have access to a stripe account", 737), 2.6, *TOP_R)
img("round-2", T("sell a fixed price service through stripe", 810) + 0.8, 4.0, *ROUND_AT, scale=0.9)
img("prompt-3", T("lets find something more simple", 955), 2.2, *PROMPT_AT, scale=1.0)
img("round-3", T("codex doesnt launch any of the three as written", 1005) + 1.2, 4.0, *ROUND_AT, scale=0.9)
img("idea-kit", T("first a single kit", 1028), 3.6, *STAT)
img("stat-buyers", T("but nobodys around to buy them yet", 1066), 3.0, *STAT)
img("stat-nogo", T("affirm nogo", 1249), 3.0, *STAT, sound="hit")      # the punchline: music dies here
img("round-4", T("the real problems", 1300), 4.0, *ROUND_AT, scale=0.9)
img("stat-followers", T("nine followers total", 1309), 3.2, *STAT)
img("stat-cost", T("3 000 of model usage", 1343), 3.6, *STAT)
img("prompt-4", T("these business ideas seem convoluted", 1464), round(cut_at(TE("taken care of by myself", 1512)) - cut_at(T("these business ideas seem convoluted", 1464)), 3), *PROMPT_AT, scale=1.0)
img("stat-go", T("codex verdict is a go with changes", 1586) + 1.0, 3.0, *STAT)
img("round-5", T("codex says one small converter", 1595) + 1.0, 4.0, *ROUND_AT, scale=0.9)
img("idea-converter", T("the converter runs entirely", 1611), 3.6, *STAT)
img("stat-conditions", T("so tech statements and csvs only at first", 1629), 3.6, *STAT)
# 04 Paperclip
img("chip-paperclip", T("all right so we are in paperclip now", 1895) + 1.6, 2.6, *TOP_L)
img("logo-paperclip", T("we are in paperclip now", 1896) + 1.0, 3.0, *TOP_R)
img("stat-odin", T("odin run failed", 1942), 3.0, *STAT)
img("stat-odin-back", T("looks like were going again", 1995), 2.6, *STAT)
img("card-paperrows", T("business name of paper rose", 2036) + 1.2, 3.6, *TOP_R)
# 05 the plan, build underway (the canvas)
img("chip-plan2", T("lets do a quick overview", 2066) + 1.6, 2.6, *TOP_L)
img("formats", T("so google sheets and excel", 2096), 3.6, 2860, 560, scale=0.8)
img("stat-private", T("the best part is it stays private", 2101), 3.4, *STAT)
img("stat-price", T("you pay five bucks per report", 2117), 3.2, *STAT)
img("roles", T("heres whos doing what", 2124), 9.0, 1500, 1750, scale=0.9)
img("stat-test", T("first 30 days is going to be a good test", 2168), 2.3, *STAT)
# outro (talking head): one card at a time, nothing over the face
img("comment-card", T("were going to keep everything in view", 2222), 4.5, *LOW, scale=0.85)
img("cta-subscribe", T("please subscribe", 2249), 2.6, 1920, 1760)
