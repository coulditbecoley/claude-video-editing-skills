
# I taught Claude how to edit videos and it's INSANE

| | |
|---|---|
| **Channel** | Duncan Rogoff (Learn Claude Code) |
| **Published** | October 21, 2026 |
| **Duration** | 9:05 |
| **Source** | https://www.youtube.com/watch?v=REAOFI534lk |
| **Topic** | A 15-year pro editor's six-job Claude Code editing system, shown in a video that system edited |

> Added to the vault 2026-11-04. YouTube's captions were rate-limited (HTTP 429), so the audio was transcribed locally with Whisper (medium.en) and the video was **watched frame by frame** (218 frames, one every 2.5 s) to analyse the edit itself. The section map below is paraphrased, not a verbatim transcript.
> Promotional: sells a $9/month community (Claude Code Club) and a "video-editor-starter" skill. The cost and token figures are his claims.

---

## Summary

Duncan Rogoff edited client work for brands like Apple, PlayStation and Nissan for 15 years. Here Claude Code edited the whole video, including word captions, motion graphics and cards flying out from behind him, and he never opened a timeline. His core lesson after five months is to **stop asking Claude for a finished video in one shot**. Split the work into **six jobs**, each run separately and each saved into a skill: scripting, editing, design, motion graphics, review and feedback.

The system improves because every round of notes rewrites the instruction that should have prevented the mistake. He says this video took about 600M tokens (~100M Opus for planning and design direction, ~500M Sonnet for building), ~$160 at API prices (covered by his Max 20x plan) and ~6 hours of Claude time. His first AI-edited video took 1.4B tokens and 12 hours; reusable assets roughly halved both.

The video itself is the strongest part. It's a dense, graphics-led edit, worth studying as much as the advice.

## Key Takeaways

### The six jobs (each a separate pass, all in one skill)
1. **Scripting.** Have Claude study videos in your niche that beat their channel's usual views, pull out the hooks and formats, and save them in a reusable hook library. Scripts get written from that library, then read to camera.
2. **Editing.** Whisper word timestamps; keep the **last clean take** of every line; cut retakes, restarts and silences with FFmpeg; list everything removed.
3. **Design.** Screenshot editors you admire and have Claude explain what makes them work (how text enters, how scenes transition), then write design guidelines or mimic them. He points to promptmotion.com, a gallery of Claude-made motion graphics that shows the prompt behind each one.
4. **Beat map, then graphics.** A beat map is a two-column table: *what I say* and *what's on screen*. It must exist before any graphic is built, because changing a plan is cheap and changing a finished graphic is expensive.
   - New rule from his audience: **one idea, one graphic, held long enough to read.** In his previous video nearly every sentence had its own graphic, and viewers said it was too much.
   - Production: sections farmed out to **subagents**; graphics built in code with **HeyGen HyperFrames** (web page to video), which is also how the word-lit captions are made.
   - **Opus / Fable for thinking** (planning, creative direction); **Sonnet for building.**
   - Renders: **at most 4 in parallel.** Nine at once maxed his machine and the agents cancelled each other's work. He renders **overnight**.
   - Drafts render at **half size** (960x540) while he gives notes; full quality only after he approves the cut.
   - Build **one graphic as a web page first**, then a storyboard of the rest; check and fix that before rendering any video.
5. **Review ("arguably the most important").** Claude checks **10 frames per second** for six mistakes:
   - an animation that plays twice;
   - a graphic that flashes for a split second;
   - text that lands too late to read;
   - a graphic sitting on his face;
   - a word said twice in a row;
   - lips drifting from the voice.

   "Check like a person, not like a computer." Hand Claude the three mistakes you always catch in your own videos.
6. **Feedback.** Give notes as you would to a human editor. Claude fixes the cut, then **finds the instruction that should have prevented each note and rewrites it**. On screen: a note "still too loud" becomes `music_mix.py --under 28.5` rewritten to `32.5` in `longform/rules/checklist.md`. "No single prompt made this video; five months of notes did."

### Cost and reuse
- This video: ~600M tokens, ~$160 at API prices, ~6 h of Claude time (not counting his review). First video: 1.4B tokens, ~$445, 12 h.
- Reusing graphics, tools and the skill halved it. **Build a library of reusable assets as you go.**
- Traditional equivalent: script, beat map, storyboard, design, animate, mix audio, sound effects. That took him 3 days to a week as a fast pro.
- He still films every video and makes the final call: "your choices and your taste" are the differentiator.

### How the video is edited (from watching it)

**Structure**
- **Cold open (0:00 to 0:20):** a 0.5 s rapid montage of his graphics, the title card "claude code edited this", then talking head with **phone-shaped cards of his past Shorts flying out from behind him** (depth layering, rotoscoped behind his body).
- Proof beats follow fast: a big "15" (years), Apple and PlayStation game-cover wall, a "2,000" stat.
- **Promise by 0:35:** "six jobs", a numbered 1 to 6 grid, and what you'll get (what to tell Claude, what to check). The cost reveal is teased for the end, an open loop he pays off at 7:10.
- **Honesty beat at 0:40:** "perfect? No." card, then the improvement loop as an orbit diagram.
- **Chapters:** each job opens on a big coloured numeral card ("01 scripting", "02", "03 design", "04 motion graphics", "05 review", "06 feedback"), each numeral in its own colour, matching a colour-coded strip of six job cards that recurs as a progress tracker (0:32, 1:30, 5:47, 6:50).
- **Repeated segment format:** every job ends on an orange-red full-screen **"so try this"** card, with the exact prompt **typing itself into a chat box**. Six times, always the same layout, so viewers learn the rhythm.
- **Ending:** cost receipt cards (first video vs this one, side by side), a "traditional way" pipeline that builds card by card into a 3-day calendar, then the offer, social proof, and a like/subscribe animation over talking head. No long outro.

**Picture**
- **The talking head is mostly a bubble.** Roughly 1 in 6 sampled frames is full-frame talking head. The rest are full-screen graphics with his face in a **round picture-in-picture bubble bottom right** (red ring), so lip sync and presence never drop while the graphic owns the frame.
- When he's full frame, graphics are small cards placed in empty space beside his head (callout cards, money icons, "link in the description" pill, captions only on key phrases).
- **Two backgrounds alternate:** a clean white editorial page and a black page, plus the orange "try this" page and a warm-cream page for the showcase segment. Each segment type has its own background.

**Typography (the signature)**
- Every headline is **bold sans plus one italic serif word in brand red**: "a *cheap* AI edit", "six *jobs*", "raw footage is a *mess*", "last clean *take*", "what *good* looks like", "map *first*", "too *much*", "one idea, one *graphic*", "half *size*", "9 at *once*", "600 million *tokens*", "video editing the *traditional* way", "5 *months* of notes".
- Small monospace tracking labels sit above headlines ("STEP 03 OF 06", "WHISPER · THIS VIDEO", "A GAME PLAN", "RECEIPT").

**Visualising the process literally**
- Diagrams of his own work, not stock: a word-timestamp table scrolling with the spoken word highlighted, three waveform takes with **"KEPT"** on take 3, the beat-map table filling in, nine render cards turning red with "CPU MAX" and X marks, then "four at a time", a "DRAFT 960x540" frame, a 10-frames-per-second filmstrip checking his face, flags for "flashes", "too late" and "lips drifting", his own notes file, and a checklist diff.
- **The audience comment that changed his rule is shown on screen** ("too many graphics too fast, hard to watch").

**Motion**
- Cards fly in with depth and blur, stack, and re-sort.
- Prompts type in character by character.
- Strike-throughs animate ("$160" struck, then "Claude Max 20x").
- Receipts slide in side by side to compare.
- The density follows his new rule: one idea per graphic, held until he moves on, not a new graphic every sentence.

### What to take into our long-form edits (Coley's pipeline)
- **We already do several of these:** word-level Whisper, last-clean-take cuts, coded graphics, a frame-level review, notes folded into skill lessons, overnight renders, worker limits.
- **Worth adopting:**
  1. **A beat map before any graphic.** A "what I say / what's on screen" table reviewed first. Our `graphics_plan.py` is close; make it the explicit first artifact.
  2. **One idea, one graphic, held to read.** Already our "front-load, then one or two per section" rule. His audience data confirms the ceiling.
  3. **A named, colour-coded chapter system** with big numeral cards and a recurring progress strip. Suits the challenge series (teams, rules, builds, results).
  4. **A repeated "try this" segment** with one fixed look. Each series can own one recurring card format viewers learn.
  5. **The face as a round bubble over full-screen graphics.** Keeps lips and presence on screen while a full-frame graphic explains. A better answer to "graphics over the face" than shrinking graphics.
  6. **The signature headline style:** bold sans with one italic accent word. Ours is chrome and gold; the one-accent-word habit transfers.
  7. **Show the process literally.** Turn real data (our agent logs, prices, timers) into diagrams instead of describing it.
  8. **His six review checks** map onto our QA. Add "an animation that plays twice" and "text that lands too late to read" to the frame check.
  9. **Rewrite the rule, not just the cut,** on every note. Our skill lessons do this; make it explicit per note.
  10. **A cost / receipt beat** suits our challenge content (budgets, spend, tokens).
- **Fits our retention data (2026-11-04):** the proof, promise and structure land inside about 35 seconds, with an open loop to the end. Our long-forms lost half their viewers by 30 to 45 seconds.

---

## Section map (paraphrased, with timestamps)

- **0:00** Cold open: Claude edited this whole video (captions, motion graphics, cards from behind him) with no timeline. 15 years editing for Apple, PlayStation, Nissan; this isn't a cheap AI edit.
- **0:21** The copyable part: six jobs, one at a time; what to tell Claude, what to check; costs revealed at the end.
- **0:36** Not perfect; give notes like you would a person. Every video teaches the system, so the next is better, faster, cheaper.
- **0:57** Why six steps: early AI edits looked cheap; five months later, better models and a better system, but the real fix was to stop one-shotting.
- **1:28** The six jobs, saved as a skill; starter kit plug.
- **1:50** Job 1, scripting: a hook-and-format library from outlier videos in your niche. *Try this.*
- **2:18** Job 2, editing: Whisper word timestamps, keep the last clean take, cut with FFmpeg. *Try this.*
- **3:03** Job 3, design: screenshot editors you love, ask what makes them work; promptmotion.com.
- **3:34** Beat map first; the "one idea, one graphic" rule from comments. *Try this.*
- **4:17** Job 4, motion graphics: subagents per section, HyperFrames, Opus to think and Sonnet to build; renders capped at four, overnight, half-size drafts. *Try this.*
- **5:45** Job 5, review: 10 fps self-check for six mistakes. *Try this.*
- **6:15** Job 6, feedback: fix the cut, then rewrite the instruction that caused it. *Try this.*
- **6:45** The whole system recap; he still films and makes the final call.
- **7:05** Cost: ~600M tokens, ~$160 API equivalent, ~6 h; first video 1.4B tokens, 12 h; build reusable assets.
- **7:52** Versus traditional editing: 3 days to a week.
- **8:25** Offer: the starter skill and the community, social proof, like and subscribe.
