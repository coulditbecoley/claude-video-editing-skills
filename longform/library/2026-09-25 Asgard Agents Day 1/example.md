# Asgard Agents Day 1 (2026-09-25)

The first learning video. It's a long-form YouTube talking head plus screen walkthrough, recorded in OBS on the LG at 4K. Coley introduces five AI agents that run an X account inside Paperclip on a $50 budget.

- Sources:
  - `Projects/Youtube/videos/2026-09-25 12-34-31.mp4`: the main take, 650 s.
  - `12-46-15.mp4`: the outro, take 2 of 2.
- Built draft: CapCut "Asgard Agents Day 1 - Edit" (ccut, from `gen_edl.py`). `draft_built.json` is the snapshot taken at build time.
- Status: **shipped unchanged.** Coley exported Claude's draft with zero edits to `OneDrive/Projects/YT Videos/Complete/Asgard Agents Day 1 .mp4` (sync verified, -14.0 LUFS, true peak 0.0 dBFS). See `corrections/2026-09-25 Asgard Agents Day 1.md`.

## Measured (tools/analyze_draft.py, metrics.json)

| | |
|---|---|
| Runtime | 8:08 (487.8 s) from 661.7 s of raw footage |
| Main source kept | 73.7% (479.4 of 650.2 s). Outro: 8.4 of 11.5 s |
| Pieces | 162, which is 19.8 cuts/min |
| Piece length | median 2.2 s, p10 0.77 s, p90 6.73 s |
| Reframing | 9 punch-ins plus 44 keyframed zoom pieces; zoomed for 49.3% of the runtime |
| Transitions | 4 in the draft (5 were planned, see Known defects) |
| Graphics | 38 PNGs: 4.67/min, 10 in the first 60 s, median 3.4 s on screen |
| Text layers | 0 (no captions) |
| Music | 7 bed clips at 0.076-0.14 volume (about -30 LUFS, 20 dB under the voice) |
| SFX | 31 clips: pops at 0.3, whooshes at 0.38, impact at 0.5 |
| Voice | processed WAV on its own track; all camera audio muted |

## Structure

The story order is set by SPANS in `gen_edl.py`:

1. **Cold open (0:00-0:10).** "I gave five AI agents..." Portrait row of all five agents, the X logo, then the HOOK_TITLE "5 AI AGENTS · $50 · 1 JOB" on the words "one job". White flash out.
2. **Context (0:10-0:33).** "...inside the Paperclip AI workforce", with the Paperclip logo on its first mention. It then goes to "I'm going to show you how we've set up... Let's go." A Zoom transition moves from camera to screen.
3. **The canvas (Obsidian).**
   - The council, zoomed 1.4 onto the agent cards as each is named.
   - The daily loop, with a PROGRESS_STEPS strip that lights up step by step.
   - The rules panel, zoomed 1.5, with stat punches for bank, max, fees and "broke".
   - Music cuts dead on "this entire experiment is over", with an impact hit.
4. **Paperclip (Swipe Left in).** Section chip and logo, then a VS_SPLIT explaining why the council is split across providers. A 1.6 zoom on the blocked column.
5. **X account.**
   - The Swipe Left into it was planned but is missing.
   - Chip, a 1.6 zoom on the banner and avatar, and the $BULK and $EMU coin cards.
   - The "Day 1" stat.
6. **Outro (Zoom transition in).** SUBSCRIBE card plus the @handle card, then a 0.45 s fade to black.

What was cut:
- A false start at 78 s.
- The "inappropriate" stumble.
- "All right."
- "So, yeah, here's this and".
- The partial first outro take.
- Lines that restate the one next to them (semantic CUTS).
- Pauses over 0.4 s were collapsed to 0.24 s.

## Tastes Coley confirmed (his words, this video)

- **No captions on long-form.** "This video is long form, not short form. There should not be any captions."
- **The facecam stays whole.** A zoom must never crop or balloon it ("breaks up my face cam"). The fix was a cropped-facecam overlay laid over every zoom piece.
- **Sync is sacred.** He spotted a 0:19-0:35 audio and picture misalignment and wanted it fixed exactly.
- **He exports and reviews.** "I no longer want you to save or export videos until I have reviewed it."
- **Direction approved.** He accepted the overall style (graphics, logos, pops, transitions, music) and asked for the long-form skill to be built from it.
- **Facecam look (from the OBS work the same day).** Bottom-right, rounded corners, a tight 4:3 crop that he set himself.

## Techniques Claude chose (still provisional until Coley's diff)

- **Pacing:** 0.4 s max gap, collapsed to 0.24 s. Semantic dedup cuts. Keep deliberate rhetorical repetition.
- **Talking-head punch-ins:** alternate 1.0 and 1.12 on every talking-head cut, to hide jump cuts.
- **Screen zooms:**
  - Scale 1.4-1.6, centred on the element being discussed.
  - 0.6 s ramps.
  - One continuous move across all the pieces of a window, with a 5% drift while holding.
- **Plain screen pieces:** anything over 6 s gets a 1.0 to 1.035 push.
- **Transitions at section changes only:**
  - White Flash out of the hook.
  - Zoom camera to screen.
  - Swipe Left between apps.
  - Each one gets a whoosh with its peak landed on the cut.
- **Graphics:**
  - Dark glass cards with gold and cyan accents.
  - Real logos only (official sites or Simple Icons).
  - Placement zones: logos top-right, chips top-left, stats top-centre, strips bottom-left.
  - Front-loaded, then one or two per section.
  - A pop sound on each graphic.
- **Music:**
  - A new bed per section, chained with fades, at -30 LUFS (-28 in the intro, -26 in the outro).
  - A dead stop on the punchline, once.
- **Voice:** highpass, afftdn, compressor, stereo, two-pass loudnorm to -14 LUFS with a -1.5 dB peak, and 30 ms fades on every cut.
- **End:** fade to black on a PNG overlay (not an opacity keyframe).

## Known defects (for the next pass)

- **The Paperclip to X Swipe Left (source 577.8 s) never landed in the draft.**
  - The EDL has it on the 575.185-577.8 piece, but the built draft has no transition there.
  - The next piece is only 0.135 s long (577.8-577.935), which is shorter than the 0.6 s transition, so it was probably dropped silently.
  - Rule: a transition needs at least its own duration of footage on both sides. Check that the transitions in the draft match the EDL.
- **Enhance voice was lost.** Coley had applied it to the voice clips, and the rebuild cleared it. The processed WAVs don't need it, but he may want it back.

## Files here

- `gen_edl.py`: every decision, in code (the most reusable part).
- `edit.edl.json`: the EDL it wrote.
- `draft_built.json`: the baseline for diffing.
- `metrics.json`: the analyzer output.
- `YouTube Post.md`: title, description, chapters, tags.
- Working folder with the graphics, audio and facecam crop: `Projects/Youtube/edits/2026-09-25 Paperclip/`.
