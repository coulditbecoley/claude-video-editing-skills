"""v5 beat map. One entry per graphic. Anchors are spoken phrases (matched on normalised words, searched forward from the
previous beat), so timing follows the words, not typed numbers.

kind:  full  = opaque full-screen scene (face cut away, narration continues)
       chips = lower-third chips over the talking head (alpha overlay), one chip per item in `chips`
       launch= the chapter launcher (4 s) at a chapter change, `n` = step lit
       over  = alpha overlay on a demonstration insert
a/b:   phrase where the slot starts / phrase whose LAST word ends the slot.  lead/tail: seconds added before/after.
ins:   insert folder(s) under D:/edits/claude-edits/job/inserts the builder must read (NOTES.md first).
brief: what to build. "when he says X, show Y, because Z".
"""
G = 'gold'; C = 'cyan'; R = 'red'
BEATS = [
 # ---------------- 1. hook (order in v5: a2, a6, cold insert, a1, a3..a5) ----------------
 dict(id='c00_hook', kind='chips', a="i've been editing", b='since september', chips=[("i've been editing", 'Edited by Claude'), ('since september', 'Since September')]),
 dict(id='s01_stack', kind='full', a='claude does the cuts', b='of that sort', tail=0.15, acc=G, grp='A',
      brief="""The claim, as a lit icon row then a strike. Four big icon tiles in a row, dim at first: CUTS (scissors), GRAPHICS
      (layers), MUSIC (waveform), RENDER (film/play). Each lights on its word ("the cuts", "the graphics", "the music", "renders it"), with a
      dotted connector drawing between lit tiles; small kicker above: "Claude does". When he says "I don't even use any editing
      software like CapCut, DaVinci": the row slides up/shrinks and two app tiles appear (CapCut and DaVinci Resolve, official marks
      from Simple Icons, on their brand colours) and each gets a red strike/slash and dims on its name. End state headline:
      "No editing software." Because: this is the hook, it must read in one glance and prove the scope."""),
 dict(id='s02_coming', kind='full', a="i'll show you how", b='new channel', lead=0.1, tail=0.3, acc=G, grp='A', ins=['19-retention-curves', '21-day1-captions-3840x1'],
      brief=""""Coming up" card. Kicker "In this video". Three tilted floating .frame previews side by side, each lit on its phrase:
      1 "How it works" (a mini of the 8-step launcher: 8 small tiles), 2 "The mistakes" (the thin 3840 x 1 line, labelled "3840 x 1"),
      3 "The real retention numbers" (a small real retention curve drawn on, from assets/retention.js, Day 1). Labels under each frame.
      Because: a concrete reason to stay, by 0:30.
      AUDIT R1: the retention preview carries the small line "YouTube Analytics, data to Nov 4 2026"."""),
 dict(id='o01_cold', kind='over', a='@cold', acc=G, grp='A', ins=['01-cold-open'],
      brief="""Overlay for the 7.95 s demonstration insert (it plays its own sound; first the RAW take with a false start and a long
      pause, then CLAUDE'S EDIT of the same line). The insert picture shows through a big rounded hole (a .frame-style glowing border)
      centred, about 1500 px wide, on the dark stage. A .pill on the top edge: "RAW RECORDING" (red accent) for the first part, switching to
      "CLAUDE'S EDIT" (gold) at the switch time given in the spec. A small .label under the frame during the raw part:
      "Pause shortened here" ONLY if the spec says the pause was compressed. Bottom source line: "3 AI Setups Challenge, Video 1".
      Because: the viewer must know which clip is which without being told."""),
 dict(id='c01_clips', kind='chips', a='the first clip is', b='gave it notes', chips=[("the first clip", "Clip 1: what I recorded"), ("the second", "Clip 2: what Claude made"), ("i reviewed", "I review, I give notes")]),
 dict(id='s03_agents', kind='full', a='i also have a second', b='fix those', tail=0.6, acc=C, grp='A',
      brief="""Two agents, one loop. Two large .ico tiles: Claude (Anthropic's Claude mark, official, from Simple Icons "claude"; if
      missing use "anthropic") labelled "Claude  edits", and Codex (OpenAI mark, Simple Icons "openai") labelled "Codex  reviews". An arc
      arrow draws from Claude to Codex on "look through the edit"; three small chips appear under Codex on their words: "mistakes",
      "cut off clips", "voice"; then the RETURN arc draws from Codex back to Claude with the caption "Claude fixes them" on "goes back".
      The return arrow and caption must be on screen at least 3 s before the scene ends (v4 failed this: it arrived at the very end).
      AUDIT R1: the slot is extended past "fix those" so the completed loop holds; still draw the return arc as early as "then it goes back"."""),
 # ---------------- 2. why ----------------
 dict(id='c10_new', kind='chips', a="you're new here", b='on their own', chips=[('this channel', 'AI agents running real businesses')]),
 dict(id='s04_pile', kind='full', a='editing is not something', b="didn't want to do", tail=0.2, acc=G, grp='A',
      brief="""The analogy, built: recordings piling up unedited. A macOS-style .win titled "OBS Recordings" with video file tiles
      (thumbnail placeholder + filename like "2026-09-17 19-39-12.mkv", real OBS-style names, no personal paths) dropping in one by
      one into a grid, each with a small grey "not edited" badge and a counter "Waiting to be edited: N" counting up. On "so of course
      I've been having Claude handle it" do nothing yet (that is the next beat). Because: show the problem instead of saying it."""),
 dict(id='c05_loop', kind='chips', a='the setup is pretty simple', b='any at all', chips=[('claude does the edit', 'Claude edits'), ('i review it', 'I review'), ('give it notes', 'I give notes')]),
 dict(id='c11_human', kind='chips', a='similar to a human editor', b='do it with claude', chips=[("human editor", "Same notes I'd give a human editor")]),
 dict(id='s06_wall', kind='full', a='12 long videos', b='behind them', lead=0.1, tail=0.25, acc=G, grp='A', ins=['02-library-wall'],
      brief="""Big italic count-up "12" (0 to 12) with "long-form edits since September" beside it, over a wall of the 12 real titles
      as small glass cards (date + title from titles.md, drop the bracketed dates from the titles) in a 4 x 3 grid that blurs in
      staggered and drifts slowly. Do NOT show a Shorts count (unknown).
      AUDIT R1: the wording must be "12 long-form projects" (not "edits", not a publication count)."""),
 # ---------------- 3. setup ----------------
 dict(id='s07_drop', kind='full', a='i record on obs', b='video is about', tail=0.2, acc=G, grp='B',
      brief="""Recreated UI, not a screenshot. Left: an .ico tile with the OBS mark (Simple Icons "obsstudio") and a file chip
      "recording.mp4" that slides right into: a recreated dark terminal .win titled "Claude Code" with a prompt line where the text
      types in at the word "drop the file": `edit this video. It's about how Claude edits my YouTube videos.` then a dim status line
      "Reading the edit-longform skill..." Because: the reference recreates UI for "paste this into Claude" moments.
      AUDIT R1: carry a visible .label "Illustration" (this is a recreated terminal, not a captured run)."""),
 dict(id='c12_pc', kind='chips', a='so claude takes it', b='for yourself', chips=[('my pc', 'Runs on my PC'), ('github', 'The skill is on GitHub, link below')]),
 dict(id='s08_skill', kind='full', a="it's really pacing", b='do either', tail=0.2, acc=G, grp='B', ins=['03-skill-lines'],
      brief="""The skill file. A tall .win "edit-longform / SKILL.md" with REAL lines from skill_lines.md (paths masked), in .mono,
      scrolling slowly. As he lists them, a marker sweep highlights one real line each and a matching .chip appears in a column on the
      right: "Pacing", "Graphics", "Music level", "Where music comes from", "Never allowed". Headline: "One long instruction file".
      AUDIT R1: use allowlisted excerpts only; mask personal paths as ~ and show no emails or handles.
      SLOT NOTE: the slot now starts at "It's really pacing"; the headline and the file are on screen from t=0."""),
 dict(id='s09_map', kind='full', a="i'll walk you through", b='actually watched', tail=0.2, acc=G, grp='B',
      brief="""The whole map, once: the launcher window (same look as scenes/launch.html, reuse its markup and CSS) but flat-on and
      larger, with all 8 tiles readable and none lit: Transcribe, Cut, Plan, Graphics, Sound, Review, Render, Learn. Tile 1 lights on
      "starting with the transcript"; tile 8 "Learn" lights on "analytics" with a small caption "then the analytics go back in".
      AUDIT R1: after the Render tile add a small return badge "Check the rendered video" (the review happens on the edit files before the render AND on the output after). The Learn caption must read as Coley-initiated: "I give it the analytics".
      SLOT NOTE: this scene replaces the first launcher: tile 1 "Transcribe" must be lit and clear by the end (it cuts straight to the word-timestamps scene)."""),
 # ---------------- 4. transcribe + cut ----------------
 dict(id='s10_words', kind='full', a='first it runs whisper', b='like a document', tail=0.25, acc=G, grp='B', ins=['04-word-timestamps-retake'],
      brief="""Word timestamps. Big transcript line(s) from the real words JSON (the "It's time to put Grok Bot, Hermes Agent and
      Paperclip AI head to head" sentence) where every word sits in its own small glass cell with its real start time under it in .mono
      ("8.56", "8.72"...). A playhead sweeps and each word lights in turn. Kicker: "Whisper, on the graphics card". Then on "like a
      document" a text cursor appears and selects two words (selection highlight) to show editing-as-text.
      AUDIT R1: label it "Transcript timestamps, Challenge Video 1" and use the ACTUAL values from the words JSON (the numbers in this brief are examples). NOTES warns Whisper merged the false start: this is a transcript illustration, do not imply verified audio alignment."""),
 dict(id='launch_2', kind='launch', n=2, before='then it runs through'),
 dict(id='s11_retake', kind='full', a='then it runs through', b='cleans those up', tail=0.25, acc=G, grp='B', ins=['04-word-timestamps-retake', '01-cold-open'],
      brief="""A real retake being cut. Transcript line on a .paper card: "It's time. [5 s pause] It's time to put Grok Bot, Hermes
      Agent and Paperclip AI head to head". On "mess up or start again" the first "It's time." gets a red strike; on "tightened up" the
      "5 s pause" block collapses to a thin tick; the clean sentence remains and gets a subtle gold underline. A small waveform strip
      under the text mirrors it (the false-start blob and the silent gap are removed, the rest slides left). Label: "Real retake,
      Challenge Video 1".
      AUDIT R1: use the corrected (voice-energy) timings from NOTES for the false start and the pause."""),
 dict(id='s12a_discord', kind='full', a='the transcript heard me', b='the repeat', tail=0.1, acc=R, grp='C', ins=['05-discord-waveform'],
      brief="""What the transcript heard. Centre: a transcript chip row with word cells "...on  Discord  Discord" (the second one
      flagged red with a "repeat?" tag) and its timestamps. On "so Claude cut it" a red cut bracket closes over the second
      "Discord". Headline: "The transcript heard it twice". Label "Reconstruction" (the bad cut is rebuilt, see NOTES boundary)."""),
 dict(id='s12b_wave', kind='full', a='only said it once', b='the chord part', tail=0.3, acc=R, grp='C', ins=['05-discord-waveform'],
      brief="""What was actually said. A big real waveform of the word "Discord" drawn from the WAV in the insert (compute peaks with
      ffmpeg or python into a JS array; x axis in ms), with the short closure gap (247.45 to 247.50 s per NOTES) shaded and a callout
      "the K sound, not a pause". Letters under the wave: "Dis" | "cord". On "cut off the cord part" the right half ("cord") greys out
      with a red strike and the "Reconstruction" label is visible from the start. Hold complete >= 4 s."""),
 dict(id='c13_rule', kind='chips', a="now there's a rule", b='removing anything', chips=[('checks the actual audio', 'New rule: check the audio around the cut'), ('repeated a word', 'Doubled word? Check it alone first')]),
 dict(id='s14_lag', kind='full', a='my webcam picture', b='back and forth', tail=0.3, acc=C, grp='C', ins=['06-d35-lag-chart'],
      brief="""The webcam lag chart from the REAL Day 35 lip-sync data (lip_units.txt / lip_timeline; low-confidence points faded). X =
      minutes into the recording, Y = lag in ms. The line/points draw on at "the delay moves around"; two italic count-ups land on
      their numbers: "85 ms" and "400+ ms" (check the exact measured min/max in NOTES; use what the data supports and what he says:
      "from 85 milliseconds to over 400"). First beat (on "runs behind my microphone"): two stacked bars, "Microphone" and "Webcam",
      the webcam bar offset to the right by a "~0.1 s" gap. Complete 8 s before the end if the slot allows.
      AUDIT R1: plot lip_units RAW measured lag only, fade the WEAK units, do not mix in the applied-shift series. 85 ms is his spoken example, the measured minimum is about 67 ms: label the low figure "about 85 ms" only as "typical low" or show the measured range from the data. If the chart cannot hold 8 s complete, draw the whole chart early and only LIGHT the two numbers on their words."""),
 dict(id='s15_sync', kind='full', a='so claude tracks my mouth', b='within one frame', tail=0.3, acc=C, grp='C', ins=['07-d35-face-sync'],
      brief="""Fixing it. Two .frame face crops side by side from the insert (BEFORE "picture late" and AFTER "lined up"; real crops, see
      NOTES for which files and that these are face-only). Under each a mouth-opening curve and the voice loudness curve; in BEFORE
      they are offset (417 ms per NOTES), in AFTER the mouth curve slides onto the voice curve at "shifts the picture to match".
      Pill on each frame. Caption: "Target: within one frame". Label "Illustration" for the curves if they are not the measured ones."""),
 dict(id='c13_check', kind='chips', a='i still check it myself', b='straight away', chips=[("check it myself", "I still check lip sync myself")]),
 # ---------------- 5. graphics ----------------
 dict(id='launch_3', kind='launch', n=3, before='next is the graphics'),
 dict(id='s16_plan', kind='full', a='before it builds anything', b="shouldn't be", tail=0.3, acc=G, grp='D', ins=['08-c3-plan-rows'],
      brief="""The plan table, re-typeset large (.tbl): columns "When I say", "Show", "Why". Two REAL rows from the C3 plan (the C3 logo
      card and the paste stat; real wording from the insert), animated in one row at a time; the "Why" cell of each lights on "what
      each graphic is doing there". On "if it can't say why it's there" a third ghost row with an empty Why cell appears and is struck
      out. Headline: "Every graphic needs a reason".
      AUDIT R1: insert 08 holds Python img/T/TE calls, not a table. Title the table "Summary of the original C3 plan" from the first frame, mark the Why text as our summary, and mark the empty-Why ghost row "Illustration". Or show the real code rows with short commentary beside them."""),
 dict(id='s17_qual', kind='full', a='the card explaining it', b='sentence is done', tail=0.3, acc=C, grp='D', ins=['09-c3-qualifier'],
      brief="""Qualifier timing as two bars on a time axis. Top bar "The sentence" (cyan). Under it "Card, first version" (red) that ends
      BEFORE the sentence does, with the gap marked; then "Card, now" (gold) that runs past the end of the sentence. Real numbers from
      NOTES (sentence end, old end derived, new end) as small labels; the old end is "derived" per NOTES, label it so. The real card
      PNG sits small above as the thing being timed. Headline: "A limit, not a promise". Bars draw at "disappearing before I finished"
      and "has to stay up".
      SLOT NOTE: the slot now starts at "the card explaining it"; headline on from t=0."""),
 dict(id='launch_4', kind='launch', n=4, before='cards themselves'),
 dict(id='s18_html', kind='full', a='cards themselves', b='for the video', tail=0.2, acc=G, grp='D',
      brief="""HTML to frames to video, demonstrated live. Left: a code .win with 6 short lines of real-looking HTML/CSS for a card
      (.code styling), typing in. Centre: the card that code makes, rendered live (a small glass card with a count-up). Right: a film
      strip of 5 frames of that same card at different animation moments, sliding. Three step pills over them: "1 Design it like a web
      page", "2 Animate it", "3 Save every frame". Label "Illustration"."""),
 dict(id='s19_three', kind='full', a='name a company', b='slides in', lead=0.1, tail=0.4, acc=G, grp='D', ins=['10-logo-number-chip'],
      brief="""Three live examples inside one big .frame (a dark mock of a video frame with a blurred face placeholder silhouette, NOT a
      real person): on "the real logo comes in" a logo card lands top-right (C3 logo PNG from the insert); on "pops up big" a big
      number lands top-centre (use the insert's real stat wording); on "section label slides in" a chapter chip slides in top-left
      ("02 THE TOOL" per insert). Each gets a small step pill naming it: "Logo", "Number", "Section label"."""),
 dict(id='c14_face', kind='chips', a='tell it to keep', b="what i'm saying", chips=[('off my face', 'Off my face'), ('time them', 'Timed to the word')]),
 dict(id='s20_day13', kind='full', a="i'd say day 11", b='the wrong one', lead=0.1, tail=0.3, acc=G, grp='D', ins=['11-day13-hook'],
      brief="""Day 11 or Day 13. A .paper transcript card with the real raw line: "Today we're going to update you on day 11 of the 5 AI
      Agents..." where "day 11 of" gets a red strike on "cut out day 11". Beside it the REAL Day 13 hook card PNG from the insert in a
      .frame with pill "The real card". Follow the NOTES accuracy flag exactly: small line "The first version cut 'day 11 of'. The
      shipped version dropped the whole sentence." visible from the card's entrance."""),
 # ---------------- 6. sound ----------------
 dict(id='launch_5', kind='launch', n=5, before='use 11 labs'),
 dict(id='s21_eleven', kind='full', a='use 11 labs', b='your browser', tail=1.0, acc=G, grp='E', ins=['12-elevenlabs-prompt'],
      brief="""ElevenLabs. Logo tile (official ElevenLabs mark, Simple Icons "elevenlabs") + name large. Below: a prompt box where the
      REAL Day 13 prompt (from the insert, shortened with an ellipsis if needed, never reworded) types in, and under it a waveform bar
      row that fills left to right like a track being generated. Two small chips on "API or MCP": "API", "MCP".
      AUDIT R1: the filling waveform is a simulation: .label "Illustration" on it."""),
 dict(id='c15_tracks', kind='chips', a='some videos get brand new', b='making more', chips=[("brand new tracks", "New track"), ("reuse tracks", "Or reuse one from the series")]),
 dict(id='c22_starter', kind='chips', a='back in october', b='more music', chips=[('upgrade', 'Oct 2026: I upgraded from the Starter plan'), ('more music', "Check your own plan's terms")]),
 dict(id='s23_duck', kind='full', a='turns the music down', b='better experience', tail=0.2, acc=G, grp='E', ins=['13-ducking-ab'],
      brief="""Ducking explained. One wide lane diagram: a "Voice" lane with speech blocks, and a "Music" lane drawn as a level line
      that dips under each speech block and rises in the gaps (draws on at "turns the music down ... back up in gaps"). Small
      measured figure from NOTES: "about 6.7 dB lower under speech". Headline: "Music ducks under the voice"."""),
 dict(id='o02_duck', kind='over', a='@duck', acc=G, grp='E', ins=['13-ducking-ab'],
      brief="""Overlay for the 9 s audio demonstration insert (own sound: A then B; exact switch time in the spec). Full opaque scene:
      two big panels "A  Not ducked" (with .label "Reconstruction") and "B  Ducked (the real mix)"; the active one is lit and has a
      moving playhead across a level drawing (voice blocks + music line; in A the music line stays flat/high, in B it dips). Kicker:
      "Listen: same voice, same output level". Because: the viewer must know which they are hearing.
      AUDIT R1: label B "B: real ducked music stem + same voice" (not "the real mix") and A "A: not ducked" + "Reconstruction". Same voice, same output gain. The level drawing is an "Illustration" unless derived from the actual WAVs in the insert (preferred: compute envelopes from the A and B files)."""),
 dict(id='c24_sfx', kind='chips', a='it does a very good job', b='other things', chips=[('lining up', 'Sounds land on the animation frame')]),
 # ---------------- 7. review ----------------
 dict(id='launch_6', kind='launch', n=6, before="then there's a review"),
 dict(id='s25_review', kind='full', a='so i have codex', b='mouth movements', tail=0.2, acc=C, grp='F',
      brief="""Codex reviews the finished edit. Left: a .frame "Claude's edit" (a mock video frame with timeline strip). Right: a
      checklist panel "Codex review" whose items tick or flag on their words: "Fixes", "Recommended upgrades", "Audio alignment",
      "Mouth sync". A scan line sweeps the frame as the list fills.
      AUDIT R1: title the review "Edit files and preview review" (it happens before the render; the output is checked again after). Carry a visible .label "Illustration" on the mock frame."""),
 dict(id='c16_two', kind='chips', a='it does catch real stuff', b="that you'd create", chips=[("two different models", "Use two different models"), ("get that review", "One edits, one reviews")]),
 dict(id='s27_ten', kind='full', a='the challenge video', b='stopped the render', tail=0.5, acc=C, grp='F', ins=['15-ten-must-fix'],
      brief=""""10 must-fix". Huge italic count-up 0 to 10 with "must-fix findings" and the source "Codex audit, Challenge Video 1",
      then a two-column list of the REAL ten titles (short, from the audit lines in the insert; verbatim or trimmed, never reworded
      into new claims) blurring in fast. A render progress bar at the top labelled "First render running" stops and shows "Render
      stopped" on "we stopped the render". Complete >= 5 s.
      AUDIT R1: heading must say "10 must-fix findings in the initial review" and item 4 keeps its RESOLVED status (insert 15 requires both)."""),
 dict(id='s28_claim', kind='full', a='for example in the video', b='technically not', tail=0.3, acc=C, grp='F', ins=['16-disclosure'],
      brief="""What was said vs what the log says. Two columns in .frames: "What I said" with the real line ("...did everything
      completely on their own", from NOTES) and "The build log" with 2 or 3 real logged human touches (from the insert; verbatim). A
      cyan "Codex" tag draws a connector between them and stamps "Technically not". Follow the NOTES accuracy flag.
      AUDIT R1: quote the retained line exactly as insert 16 has it: "I would say Paperclip and Grok Bot did everything on their own." (no "completely"). Verbatim log lines only, masked."""),
 dict(id='s29_disc', kind='full', a='it would inform me', b='correct information', tail=0.5, acc=C, grp='F', ins=['16-disclosure'],
      brief="""The fix: the REAL disclosure card from the Challenge video (PNG or frame from the insert) in a .frame with pill "The
      disclosure that shipped", and beside it the cut line "I did not have to do anything" with a strike. Footer from the entrance:
      "The cut came first. Codex then asked for the fuller disclosure." (required wording, must hold >= 5 s)."""),
 dict(id='s30_stale', kind='full', a='on that same video', b='called that too', tail=0.4, acc=C, grp='F', ins=['17-stale-audio'],
      brief="""Stale audio. Two stacked timelines, "The edit (new)" and "Audio it checked against (old)", identical at first; on "moved
      everything after about three and a half seconds" the new one's blocks slide right by a marked "3.5 s" (count-up to 3.5). A music
      lane under the old one shows ducks that no longer line up with the new speech blocks (highlight the mismatches red) on "ducking
      to speech that wasn't even there". Final beat on "make sure that the lengths match": both lanes get a length readout that goes
      green and equal. Label "Illustration, numbers from the audit".
      AUDIT R1: insert 17: the divergence is at about 08:22 on the v1 timeline, where the old QA voice ran 3.551 s early afterwards. Keep the earlier blocks aligned and shift only the region after 08:22. Card: "From about 08:22, the old check audio was 3.551 s early". Attribute to "v1 timeline, Challenge Video 1".
      SLOT NOTE: the slot ends at "Codex caught that too"; drop the final "lengths match" beat (it is a chip on the face afterwards)."""),
 # ---------------- 8. render ----------------
 dict(id='c30_rebuild', kind='chips', a='anytime the edit changes', b='checks anything', chips=[('rebuild those files', 'Edit changed? Rebuild the check files'), ('make sure', 'Lengths must match')]),
 dict(id='launch_7', kind='launch', n=7, before="once it's all fixed"),
 dict(id='s32_render', kind='full', a='but now everything', b='no editing tool', lead=0.1, tail=0.2, acc=G, grp='G',
      brief="""Then and now. Left tile (dimming): "Before: CapCut draft, I exported" with the CapCut mark struck. Right (hero): giant
      "4K" and "60 fps" in italic numerals with count-ups (0 to 4, 0 to 60) inside a .frame, a render progress bar filling under them,
      caption "Rendered by Claude, on my PC". Label "Illustration" on the progress bar.
      SLOT NOTE: the slot starts at "But now everything is taken care of": skip the "Before: CapCut" tile, go straight to the 4K / 60 fps hero."""),
 dict(id='s33_table', kind='full', a="it's not fast", b='around three hours', lead=0.1, tail=0.4, acc=G, grp='G', ins=['18-render-cards'],
      brief="""Render times, re-typeset table (.tbl), two rows only: "8 minute video  |  about 40 min" and "22 minute video (the
      challenge)  |  about 3 hours". Each row lights on its sentence; the time cells are big italic. .label "Recorded estimates,
      earlier videos" visible from the start. No other rows, no claims about this video."""),
 dict(id='c17_night', kind='chips', a='leave it running overnight', b='trying to edit', chips=[("overnight", "Runs overnight")]),
 dict(id='s34_repair', kind='full', a="it didn't render the whole", b='instead of another', tail=1.3, acc=G, grp='G', ins=['18-render-cards'],
      brief="""Fix only the opening. One long bar = the whole 22 min video. The first small slice glows gold ("re-rendered") while the
      rest is hatched grey ("already rendered, kept"); a seam marker with a tick ("seam checked"). Then two big numbers side by side
      with count-ups: "15 min" (gold) vs "3 hours" (struck, dim). Label "Recorded estimate". Headline: "Fix the opening, keep the rest"."""),
 # ---------------- 9. retention ----------------
 dict(id='launch_8', kind='launch', n=8, before='i also checked how'),
 dict(id='s35_ret_long', kind='full', a='the long videos need work', b='most of each video', lead=0.1, tail=0.3, acc=G, grp='G', ins=['19-retention-curves'],
      brief="""ALREADY BUILT as the worked example for charts (scenes/s35_ret_long.html): three real audience curves over the first 2
      minutes with the half-gone times 24 s / 45 s / 47 s. EXTEND it, keep its look: set data-dur to this slot, and add the second
      kind of evidence for "YouTube's own score puts them below the median ... for most of each video": on the word "YouTube's own
      score" the first chart shrinks/slides left (or cross-fades) and a second panel appears: relativeRetentionPerformance (third
      column in assets/retention.js) across the whole video (x = share of the video, 0 to 100%) for the same three videos, with a
      dashed reference line at 0.5 labelled "0.5 = median for similar-length videos" and the three lines mostly under it. Never
      label the audience chart's 50% line as a median. He says "inside the first five minutes"; the headline "Half the viewers are
      gone in under a minute" is the supported, stronger fact: keep it. Both panels complete early; hold."""),
 dict(id='s36_ret_short', kind='full', a='the shorts showed something', b='all of them', tail=0.4, acc=R, grp='G', ins=['19-retention-curves'],
      brief="""Five Shorts curves on a SECONDS axis (each plotted to its real length, data in assets/retention.js, ids and lengths in
      the insert NOTES), values above 100% kept. The 4 to 6 s window is a shaded red band that lights on "between four and six
      seconds" with a callout "All five drop here". Lines draw on staggered. Tag: "YouTube Analytics, data to Nov 4 2026". Same chart
      styling as s35_ret_long (read it first). Complete 8 s before the end if the slot allows; do not add reasons for the drop.
      AUDIT R1: if 8 s complete is not possible in the slot, draw all five lines and the band early and only LIGHT the band and callout on the words."""),
 dict(id='s37_best', kind='full', a='of those five', b='same spot', lead=0.1, tail=3.2, acc=G, grp='G', ins=['19-retention-curves', '14-sixty-six-caption'],
      brief="""The best one. Left: a portrait .frame (9:16) with the real fixed "$66" caption frame from insert 14, pill "17 second
      Short". Right: a progress ring filling to 72% with italic count-up "72%" and "viewed on average" (71.96% per r1_summary), and
      under it a small curve of that Short with the same 4 to 6 s dip marked "still dips here".
      AUDIT R1: scope line: "Best of these five by average % viewed". 71.96% comes from the Nov 5 rolling 60 day report; the curve is Nov 4 lifetime data: caption each. The $66 is a caption, not earnings or a price. Slot extended so the ring holds."""),
 dict(id='s38_rules', kind='full', a='for shorts the payoff', b='at the beginning', tail=0.5, acc=G, grp='G', ins=['20-retention-rules'],
      brief="""The rules that changed, as two .paper cards with serif type and REAL rule text from the insert (verbatim, trimmed with
      ellipses only): "Shorts" card (payoff by 4 s) lights with a marker sweep on "first four seconds"; "Long videos" card (result or
      stakes right away) on "stakes clear right away". Footer from the start: "Adopting a rule is not proof it worked." """),
 dict(id='c18_credit', kind='chips', a='coming up card', b='another youtuber', chips=[('borrowed that', 'Coming up card: idea from Albert Olgaard')]),
 # ---------------- 10. mistakes ----------------
 dict(id='s39_caps', kind='full', a='the very first video', b="didn't want them", lead=0.1, tail=2.6, acc=R, grp='H', ins=['21-day1-captions-3840x1'],
      brief="""Captions on a long video. A .frame with the real final Day 1 frame from the insert and a rebuilt caption line over it
      ("WORDS ON SCREEN LIKE THIS" style, generic), which gets crossed with a red X on "didn't want them". .label "Reconstruction"
      from the start (the captioned draft was not kept). Right: the rule on a .paper card: "No captions on long-form."
      AUDIT R1: slot extended over the next sentence so the card holds 5 s complete; put the X on early ("had captions") rather than on the last word."""),
 dict(id='s40_click', kind='full', a='in the same first edit', b='off in the timeline', lead=0.15, tail=0.3, acc=R, grp='H',
      brief="""The timeline click. A recreated editor timeline (generic, not CapCut's UI or logo): two clip blocks on a video lane and
      an audio lane under them. A cursor moves to a clip edge and clicks; the edge snaps inward (clip trims) and everything after
      shifts so the audio lane no longer lines up (red offset marker "lip sync off"). Then the rule on a small paper strip:
      "Never click the timeline. Check from the files." Label "Illustration"."""),
 dict(id='s41_line', kind='full', a='it named a variable', b='pixel tall', tail=0.7, acc=R, grp='H', ins=['21-day1-captions-3840x1'],
      brief="""3840 x 1. Top: a short code .win showing the collision with the SAME identifier on both lines (required): `H = 2160   #
      video height` then `for H in rows:   # oops, H reused` and `canvas = (W, H)   # 3840 x 1`. .label "Schematic". Then on "one pixel
      tall" the code slides up and a 16:9 outline frame collapses vertically into a single glowing thin line across the screen with
      big italic "3840 x 1". Then an export bar that sticks at "30%". The finished explanation must be complete >= 5 s.
      SLOT NOTE: the slot ends just after "one pixel tall": no export bar (that line plays on the face)."""),
 dict(id='c41_hang', kind='chips', a='then the export kept', b='it was broken', chips=[('hanging', 'Exports hung at 30%')]),
 dict(id='c42_over', kind='chips', a='one edit codex pushed', b='claude and codex', chips=[('back and forth', 'A review can go too far')]),
 dict(id='s42_dur', kind='full', a='minute video came down', b='explained in the video', lead=1.4, tail=0.3, acc=R, grp='H', ins=['22-day20-durations'],
      brief="""Over-reviewing. Three big duration numerals in a row with bars under them whose lengths match: "8:26 first edit",
      "6:32 after the cuts" (red, shrinking), "11:06 final" (gold, growing), each landing on its beat ("eight minute video", "down to
      six", then the restoration). Under the middle one, chips of what was cut (from the insert: roadmap, hiring example, backstory,
      explanations; real items only). Footer from the start: "Then the cut parts were restored: 11:06 final".
      SLOT NOTE: the slot starts at "An eight minute video came down to six": all three durations must be visible early (dim), lighting in order."""),
 dict(id='c19_only', kind='chips', a='so i told it to only', b='conveyed previously', chips=[('pauses', 'Cut pauses'), ('umms', 'Cut ums'), ('information that has', 'Cut true repeats only')]),
 dict(id='s43_blur', kind='full', a='what it also does', b='blurs it', tail=0.3, acc=G, grp='H', ins=['23-ep2-blur'],
      brief="""Private details. A recreated generic screen mock in a .frame (file picker rows and a payment form, all dummy text) where
      a scan line passes and blur boxes with gold outlines land on the sensitive fields (folder name, email, card). Do not show any
      real personal data; the insert has privacy-checked crops if a real frame is wanted. Footer from the start: "Private details can
      still be missed. Review the render."
      AUDIT R1: dummy UI only, or the named protected crops; never the full payment frame."""),
 # ---------------- 11. close ----------------
 dict(id='s44_github', kind='full', a='it is in the github repo', b='try it out', tail=0.4, acc=G, grp='H', ins=['24-github-card'],
      brief="""GitHub. Official GitHub mark tile, and a big address bar where the URL types in:
      github.com/coulditbecoley/claude-video-editing-skills. Three chips: "MIT licence", "Free", "Link in the description". Small
      honest line: "Built around my setup: Windows, OBS, an NVIDIA card."
      AUDIT R1: README excerpts must be allowlisted lines, no paths or emails.
      SLOT NOTE: chips here: "Link in the description" only (MIT and Free are said on the face after the scene)."""),
 dict(id='c44_mit', kind='chips', a='it is mit licensed', b='it is free', chips=[('mit licensed', 'MIT licence'), ('it is free', 'Free')]),
 dict(id='s44b_need', kind='full', a="it's just a skill", b='have to pay', lead=0.1, tail=0.3, acc=G, grp='H', ins=['24-github-card'],
      brief="""What you need, as a calm static checklist from the repo README (allowlisted lines only): four .tile rows that blur in once
      and then hold: "Windows", "OBS recording", "An NVIDIA graphics card", "Claude Code". Small line: "Built around my setup. Adapt it
      to yours." No slogans, no animation after the entrance."""),
 dict(id='c45_cta', kind='chips', a='if this video was helpful', b='love to hear it', chips=[('leave a comment', 'Comment: how did it work for you?'), ('updated', 'Tell me what to improve')]),
 dict(id='s46_end', kind='full', a='like the video', b='@end', acc=G, grp='H',
      brief="""End card. Left: big "Subscribe" pill in gold with the channel handle from the v4 YouTube Post file (ask the orchestrator
      if unknown; do not guess a handle), right: two empty rounded 16:9 slots labelled "Watch next" for YouTube's end-screen elements
      (leave them clean and dark; the real elements are added in YouTube Studio). Calm: one entrance, then still."""),
]
