# Asgard Agents Day 6 (2026-09-29)

The second learning video, and the first edited with the edit-longform skill from start to finish. It's a single OBS take on the LG at 4K. Coley walks through the agents' Day 6 update: the Obsidian canvas they made, the new Agents Window site (asgardagents.com), Paperclip, and the suspended X account.

- Source: `Projects/Youtube/videos/2026-09-29 12-25-48.mp4`, 565 s, one take. Both mic channels were live.
- Built draft: CapCut "Asgard Agents Day 6 - Edit". `draft_built.json` is the snapshot taken at build time. `verify_draft.py` returned DRAFT OK, and all 4 of the 4 planned transitions landed.
- Working folder: `Projects/Youtube/edits/2026-09-29 Asgard Day 6/`.
- Status: **built, waiting for Coley's review.** He restated it: never export until he has reviewed it manually.

## Measured (metrics.json)

| | Day 6 | Day 1 |
|---|---|---|
| Runtime | 7:07 from 9:25 (75.6% kept) | 8:08 (73.7%) |
| Cuts/min | 15.0, median piece 3.5 s | 19.8, median 2.2 s |
| Zoomed share | 71.3% | 49.3% |
| Graphics | 45, 6.3/min, 12 in the first 60 s | 38, 4.7/min |
| Transitions | 4 | 4 |

**Why these differ:**
- Cuts are fewer because there's barely any talking head (11 s), so there are almost no punch-in splits.
- The zoomed share is higher because the Agents Window walkthrough is one static page, and Claude zoomed each panel as it was named.

If Coley pulls zooms back in review, the fix is a zoom-share cap, not a zoom rule.

## Structure

1. **Hook (0:00).** "This is day six of letting five AI agents run their own meme coin company. Let's see what they're doing." The five portraits sit low across the chest, and the title card "DAY 6 · 5 AI AGENTS · 1 COMPANY" sits above his head. White Flash out.
2. **Intro.** Take 2 of "jump into Obsidian". Take 1 had a 5 s stall mid-sentence. Zoom transition to the screen.
3. **Canvas (0:10).**
   - One zoom per canvas column, each kept inside a stable view. The canvas pans at 117.5, 156-158 and 174.2 s, and every window sits between those pans.
   - Chips 01-04.
   - The punchline is "the X account did get suspended": the music dies, an impact hits, and a red stat card appears. The music comes back on "We have since fixed that".
4. **Agents Window (Swipe Left in, 2:27).** Zooms follow the tour: Odin's card, the ticker, the top stat bar, and the right column.
   - The Chronicle and Treasury got chips and stats, not zooms. The Treasury panel sits under the facecam in the recording, and zooming the Chronicle would balloon the facecam.
5. **Paperclip (Swipe Left in, 5:24), then X.** A zoom on FEN-278, then a zoom on "Your account is suspended". The tab switch is a hard cut, because the speech runs across it with no pause.
6. **The plan and outro.**
   - A 3-step PROGRESS strip: get X back, then pick a platform, then the agents post on their own.
   - The asgardagents.com bookmark card.
   - SUBSCRIBE, then the "who's your favourite?" card with all five portraits, held to the end.
   - Fade to black.

What was cut:
- The dead air before 12.45 s, and the restated intro "In this video, this is day six update...".
- "Okay," and "Up next."
- "You can, we'll start at the top left. So you're looking at the agents window."
- "you know" fillers, the doubled "the. The company", the "I think they have." false start, and "So this is day six."
- Restatements: "So they did find that.", "We're not doing anything.", "Nothing new.", "the newest three tokens".

## New techniques (provisional)

- **`cam_grow` computed, not guessed.** `gen_edl.py` works out where the zoomed copy of the facecam lands. When it's off-frame, the overlay stays at 1.0. When it's inside the frame, the overlay grows just enough to cover it (1.228 on three canvas zooms). The asserts fail if a zoom would put the copy outside the overlay. Verified on a composited still.
- **Zoom centres are clamped** so the frame never shows past the recording's edge.
- **Zoom window edges must sit in silences or removed gaps.** ccut adds 30 ms voice fades at every piece join, so a split mid-word would dip the audio. Three edges were moved into silences after a check.
- **Cards anchored to the margins.** Chips hang off the left at 80 px and logo cards off the right at 3760 px, whatever their width. Fixed-centre cards had overrun the canvas edge.
- **Section chips can run past 03.** This video uses 01-09, one per topic.

## Files here

`gen_edl.py`, `edit.edl.json`, `draft_built.json`, `metrics.json`, `YouTube Post.md`. Graphics (`graphics/render.mjs`), audio, logos and the facecam crop are in the working folder.

## v2 (after Coley's review, same day)

He reviewed v1 without touching it and asked for changes in words. They're recorded in `corrections/2026-09-29 Asgard Agents Day 6.md`, and the new rules are in `taste.md`.

- The screen sections run on one continuous, cursor-following camera, using ccut `path` keyframes from `track_cursor.py`. Speech that crosses a tab switch gets a 0.4 s Swipe.
- 7 more stutter cuts.
- Transition margins widened.
- A calmer exit.

`draft_built.json` is now v2. v1 is kept as `draft_built.v1.json`, and `still.py` renders any output second from the files.
