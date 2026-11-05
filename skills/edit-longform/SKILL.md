---
name: edit-longform
description: "Edit Coley's long-form YouTube videos (talking head plus screen walkthroughs, recorded in OBS into Projects\\Youtube\\videos) into a finished, ready-to-review CapCut draft, the way the Wiki's AI Video Editing notes describe - word-level transcript cuts, component graphics landed on exact words, real logos, sound design, verified sync. Use when Coley asks to edit, cut or polish a YouTube / long-form video, or points at an OBS recording for YouTube. NOT for short-form TCG card / No Bulk / Shorts edits - those use the edit-video skill. No captions. Default deliverable is a CapCut draft (Coley exports); when he asks for it without CapCut or as a finished video, render the 4K60 MP4 yourself (Rendered MP4 mode)."
---

# Long-form YouTube edit (CapCut draft)

Turns an OBS recording (plus any extra takes) into a polished CapCut draft for
Coley to review and export. Built from `Wiki/AI Video Editing — Index.md` and the
first real edit with it: "Asgard Agents Day 1", 2026-09-25
(`%USERPROFILE%\Projects\Youtube\edits\2026-09-25 Paperclip\`, the worked example
for everything below).

**This is not the `edit-video` skill.** That one is Coley's short-form TCG
card workflow (vertical, CapCut Generate-captions, price overlays). Keep them
separate; don't cross rules between them.

## Hard rules (Coley's words, all 2026-09-25)

1. **No captions.** "This video is long form, not short form. There should not be
   any captions in this video." Words on screen come only from the graphics.
2. **Never export or save a video file.** "I will do the exporting... just conduct
   the editing and then leave it for me to review manually." The deliverable is a
   CapCut draft plus a short note. Don't click Export, don't render mp4s.
   **Exception:** when Coley asks for the edit without CapCut, or for a finished or rendered
   video, use "Rendered MP4 mode" below. He approved that result on 2026-10-29 ("This is great work").
3. **Never modify a CapCut project you didn't build** (his "0925", "0823" and so
   on). Build a new draft named `<Topic> - Edit`.
4. **Never click CapCut's timeline** to seek or inspect. A click near a clip edge
   silently trims it (this broke lip sync once). Verify from files instead.
5. Screen control of CapCut takes over his monitor. If he is actively using the
   PC, wait for idle (see CapCut operation) or ask.

## Taste profile (read first, every edit)

`%USERPROFILE%\Projects\VideoEditor\LongForm\` is where this skill learns (map in its `README.md`).
- Before deciding anything, read `profile/taste.md`. Confirmed rules beat everything below;
  provisional rules are defaults. Skim the latest `library/*/example.md` and `lessons/lessons.md`.
- Right after building, copy the draft's `draft_content.json` to
  `library/<date> <title>/draft_built.json`, along with `gen_edl.py`, `edit.edl.json` and an `example.md`.
  Then run `tools/analyze_draft.py --out metrics.json` and `tools/aggregate.py`.
- When Coley has reviewed it, run `tools/diff_drafts.py` against the live draft, save the result to
  `corrections/`, and fold each change into `taste.md` with its evidence.

## Tools

- `ccut` at `%USERPROFILE%\Code\capcut-cli` (`uv run ccut build <edl.json>`), built on
  pycapcut. EDL schema in `src/ccut/edl.py`; features this skill relies on are
  listed under "EDL features".
- Style profile: `capcut-cli/profiles/youtube.md` (pacing, overlays, sound, verification).
  Teaching notes: `FenrirVault/Projects/CapCut CLI/Teaching/` (Lesson notes win over the profile).
- Scripts in this skill's `scripts/` folder, templates in `templates/`.
- Playwright for rendering graphics: import from
  `file:///~/Code/market-analyzer/node_modules/playwright/index.mjs`.
- **Music and SFX must be non-copyright** (Coley, 2026-10-03). Generate an original instrumental bed per video with ElevenLabs Music (matched to length and mood), and save the prompt and the file in the edit's `audio/` folder as provenance. No commercial or unknown-licence tracks. Generate it in Coley's logged-in browser via Claude in Chrome (ElevenLabs Music tool); no API key.
  The Pixabay beds from the first edits are legacy: don't reuse them for new videos.

## Workflow

Work in `%USERPROFILE%\Projects\Youtube\edits\<date> <topic>\`.

### 1. Inventory and watch
- List the source clips (the CapCut project Coley set up tells you which recordings belong
  together; read its `draft_content.json`, don't edit it).
- Contact-sheet frames (one every 30 s) to learn the structure: talking head vs screen,
  where the facecam sits, which apps are shown.
- Multiple short clips of the same line are retakes: keep the complete one.
- **Frame rate check:** `ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate,avg_frame_rate -of csv=p=0 <clip>`.
  If the two differ, the clip is variable frame rate (OBS under load) and cuts can land a frame or more off. Conform it
  first (`ffmpeg -i in.mp4 -vf fps=60 -c:v hevc_nvenc -cq 17 -c:a copy in.cfr.mp4`) and edit the CFR copy.
- **Secrets sweep, every clip with screen footage:** `uv run <skill>/scripts/secrets_sweep.py <clip> --apply` OCRs a frame
  every 2 s, flags keys, tokens and `KEY=value` lines, and writes `<clip>.redacted.mp4` with those boxes blurred over
  their time spans. Edit the redacted copy (Shorts inherit it). Use `--every 1` for fast scrolling. It's sampled, so still
  look at every terminal, `.env` or dashboard shot in the contact sheet. Cost: up to about 2 min per minute of busy footage
  (CPU OCR; still screens are skipped), so start it in the background at intake. `--cpu` if there's no NVIDIA decode.
  Related: the graphics renderers (`render.mjs`, Shorts' `render_shorts.mjs` / `render_captions.mjs`) now throw if a web
  font didn't load (`assertFonts`) instead of silently using a lookalike. Older copies in past edit folders don't have it.
  (From Jason Cooperson's Claude Video Editor page, 2026-11-04.)

### 2. Transcribe (word level, twice)
From `capcut-cli`:
```
uv run python <skill>/scripts/transcribe_words.py --prompt "Paperclip, Claude Code, Codex, ..." <clips>
uv run python <skill>/scripts/transcribe_words.py --literal <main clip>
```
The literal pass exposes flubs the default hides. Whisper word end times run long
on drawn-out words ("work... force"), so snap every cut to a real silence, not a word time.
**Since Day 35 (2026-10-28), run it on the GPU** (CPU Whisper starved for an hour): `edits/2026-10-28 Recording 1133/`
`transcribe_gpu.py` + `sweep_gpu.py` (medium.en, float16) from a venv with `faster-whisper nvidia-cublas-cu12
"nvidia-cudnn-cu12==9.*" "av<14"` and `gpuw_boot.py` on PYTHONPATH. Find fillers with the sweep, `islands.py` and
`firstword.py`, place every edge on `runs.py` (10 ms sound/quiet runs), and re-hear every changed join.

### 3. Voice
- Per-channel `astats` check first; then `scripts/process_voice.sh <clip> audio/voice-<name>.wav`
  for every clip. It lands at -14.0 LUFS, -1.5 dB peak. The draft plays these WAVs on
  a voice track and mutes the camera audio.
- Silence maps on the cleaned voice: `silencedetect=n=-40dB:d=0.2`.
- **Lip sync (Day 30, confirmed):** the OBS webcam picture lags the mic (about 100 ms) and afftdn
  delays the cleaned voice about 25 ms. Measure before editing with `edits/2026-10-23 Recording 1040/`
  `lipsync_mp.py` + `lip_scan.py` + `lip_analyze.py` (MediaPipe venv; cross-correlate cleaned vs raw
  voice for the chain delay). The lag can CHANGE mid-recording: track the whole take (`lip_track_full.py`),
  map it with `lip_timeline.py`, and set per-section whole-frame shifts in `sync_sections.json` (ccut `av_offset`;
  section edges inside cuts). Verify per section with `lip_verify.py` and in CapCut's Timelines copy. Target: within a frame.
  **Since Day 35, sync per kept unit:** the lag can drift through in-between values (85-435 ms in one take). Track the whole
  take at 60 fps (`edits/2026-10-28 Recording 1133/lip_anchor_cam.py`: GPU decode with the crop in the decoder, frames
  streamed, 20 s chunks, 3-4 workers), then `lip_units.py` gives every unit its own whole-frame lag, smoothed across
  neighbours, and writes `sync_sections.json`. Spot-check overridden or weak units with `lip_local60.py`.

### 4. Decide the edit (in code: copy `templates/gen_edl.asgard-day1.py` to `gen_edl.py`)
- **Story spans** (source in/out) from the transcript: hook first (the strongest "I did X,
  let's see what happened" line), then context, sections, outro. Drop restarts, false
  starts, duplicate sign-offs and partial takes.
- **Pacing:** pauses over 0.4 s collapse to 0.24 s (`MAX_GAP, KEEP`). Long-form standard
  from the wiki (Jowett: 0.2 s).
- **Semantic cuts** (`CUTS`): lines that restate their neighbour, stumbles, doubled words.
  Keep deliberate rhetoric ("I do not post, I do not comment, I do not reply").
- **Dedup check:** flag any 2+ word run repeating within ~12 words across phrase boundaries.
- **Punch-ins** alternate 1.0 / 1.12 on talking-head cuts (split at sentence gaps for more).
- **Zooms** on screen sections where small 4K text is being discussed: scale 1.4-1.6 centred
  on the element. Check the zoom view keeps the whole element in frame (the council row needed
  1.4, not 1.6). **Since CapCut 9.2 (2026-10-06) a zoom is a punch-in:** split the piece at the
  window's edges and give the zoomed piece a static `frame`. Keyframed ramps, drifts and camera
  `path`s don't animate on video clips any more (see Known not to work). The worked example is
  `edits/2026-10-06 AI Agents/gen_edl.py` (`ZOOMS`, `frame_of`).
- **Facecam over zooms:** zooming the screen balloons and crops the recorded facecam.
  Crop the facecam box out of the recording once (`ffmpeg crop=w:h:x:y`, same timing) and
  lay it over every zoom piece at its original box (`cam_overlay`). Aim zooms so the zoomed
  facecam falls off-frame; where it can't (a wide target), grow the overlay (~1.2x, anchored
  top-left) to cover it. Measure the box from a frame, don't guess.
- **Still-shot drift:** retired with CapCut 9.2 (keyframes don't animate on video clips). Long
  still shots get a punch-in on what's being discussed instead.
- **Transitions** only at section changes, placed in removed pauses: White_Flash out of the
  hook, Zoom_Transition camera to screen and back, Swipe_Left between apps. Chips and pop-ups
  start 0.7 s after a transition, never during it.
- **Music:** a new bed per section, chained with fades to fill it, ~20 dB under the voice
  (Pixabay beds are about -8 LUFS; `volume = 10 ** ((-30 - lufs) / 20)`, -27 to -26 under
  talking head). Cut it dead on the punchline line once, with an impact hit.
  **Since 2026-10-28, duck it:** `edits/2026-10-28 Recording 1208/mix_stem.py` renders the cues into one stem
  sidechain-compressed on `qa_voice.wav` (~21 dB under speech, ~-27 dB in gaps); gen_edl swaps the cues for the
  stem only while its length matches the timeline. Regenerate qa_voice, the stem and the review mix after any change.
- **SFX:** pop on every graphic (0.3), whoosh with `peak_at` on every transition (0.38),
  impact on the big stat (0.5). Keep export peaks under -1 dB.
- **SFX frame-exact (Day 30):** CapCut snaps clip starts and trims to whole frames on open. Use
  frame-aligned `peak_at` targets on each animation's hit frame (pop 4 frames in, slide 3, glow 2,
  whoosh on the cut), pad samples with `edits/2026-10-23 Recording 1040/audio/pad_sfx.py`, and check
  CapCut's Timelines copy with that folder's `sfx_check.py` (aim: under 7 ms).
- **End:** fade to black over the last ~0.45 s via a black PNG overlay with `pop: "fade"`.
- **Never shadow `W, H`** (canvas) in the script: a loop variable named `H` once built a
  3840x1 canvas. ccut now refuses resolutions under 16 px.

### 5. Graphics (bounded component set, landed on the spoken word)
Copy `templates/render.mjs` into `graphics/` and edit its asset list. The components:
- **HOOK_TITLE**: the premise as one line ("5 AI AGENTS · $50 · 1 JOB"), on the payoff word.
- **Portrait row / IMAGE_CARD**: real assets (agent portraits, coin logos from the project's
  own files), staggered pops on the line that names them.
- **Logo pop-ups**: every company named, on its first mention. Official marks only
  (the company's own site, or Simple Icons via jsdelivr). A card = tile + name + one-line role.
- **Section chips** "01 THE COUNCIL", top-left.
- **STAT_PUNCH** callouts for numbers and rules, top-centre.
- **PROGRESS_STEPS** strip for a process walkthrough, current step lit as he reaches it.
- **VS_SPLIT** for a comparison he explains.
- **Handle card + SUBSCRIBE** in the outro.
Density: front-load (a graphic every few seconds in the first 40 s), then one or two per
section. Layout zones: logos top-right, chips top-left, stats top-centre, strips bottom-left
clear of the facecam, nothing over the face in talking-head shots. Dark glass cards, gold
and cyan accents (match the channel's brand). No em dashes in on-screen copy.

### 6. Verify before building
- `python <skill>/scripts/verify_voice.py edit.edl.json qa_voice.wav`, then the literal
  transcription of `qa_voice.wav`. Read it end to end: every join must read naturally, no
  chopped words, no leftover retakes. Re-transcribe any doubtful join in isolation.
- Layout audit in code: overlapping graphic boxes, graphics over the face or the facecam,
  graphics shorter than 1.5 s, graphics during transitions, music gaps.
- **Opening audit (channel retention data, 2026-11-04):** all three long-forms checked lost about half their
  viewers in the first 30 to 45 s, with drops at roughly 9, 18 and 27 s, and averaged 14 to 29% viewed. Read the
  first 45 s of transcript: the result or stakes stated in the first 10 s, a concrete reason to keep watching by
  30 s, no setup, intro or recap before that. Put the strongest footage and the payoff in the first 2 to 3 minutes.
- **Frame review checks (Duncan Rogoff's six, Wiki 2026-11-04):** an animation that plays twice, a graphic that flashes
  for a split second, text that lands too late to read, a graphic on the face, a word said twice in a row, lip drift.
  For every note Coley gives, also rewrite the rule or script value that should have prevented it.

### 7. Build, open, check
- `uv run ccut build <dir>/edit.edl.json` with CapCut **fully quit** (a draft rebuilt under
  a running CapCut often won't open, and new drafts only appear after a restart).
- Launch CapCut, open the draft (see CapCut operation), confirm the title bar reads the
  draft name, then `python <skill>/scripts/verify_draft.py "<draft name>" edit.edl.json`.
  It must print DRAFT OK.
- Look at graphics by rendering stills yourself from the source plus the PNGs, or ask Coley.
  Never scrub CapCut's timeline.

### 8. Hand over
- Leave the draft open at 0:00. Tell Coley what the edit does in plain words (runtime,
  cuts, graphics, sound) and anything to check.
- Write `YouTube Post.md` (title options, description with chapters from the EDL mapping,
  tags, thumbnail idea, end-screen note).
- If he later sends back an export to check, `scripts/verify_export.py <file>` (run in the
  edit folder) frame-matches picture sync and cross-correlates the voice.
- About 7 days after it posts, pull its retention curve (`%USERPROFILE%\Projects\Youtube\retention\yt_analytics.py
  retention <ID>`, free), match the drops to the EDL's pieces, and fold repeated patterns into `profile/taste.md`.

## Rendered MP4 mode (no CapCut; approved 2026-10-29)

Use this mode when Coley asks for the edit without CapCut, or for a finished or rendered video. Steps 1 to 6 don't change:
the `edit.edl.json` is still the source of truth. Instead of `ccut build`, render it yourself. Worked example:
`edits/2026-10-28 Recording 1208/nocapcut/` ("C3 Research Tool", 8:00 at 4K60, rendered in about 40 minutes with 6 workers).

1. Copy `scripts/render_mp4.py` to `<edit>/nocapcut/`. It reads `../edit.edl.json` and follows ccut's
   semantics: the voice plays from `in - av_offset`, frame x/y are in half-canvas units, image x/y are the canvas-pixel
   centre, `peak_at` puts the sample's loudest 10 ms on the cut, and transitions are centred on the cut.
2. **Check the talking-head detector first.** `talking_head()` marks a piece as camera when the mean of a
   480 px thumbnail is over 55. That suits a lit room against dark app pages. Look at `talking_head.json` and
   delete it to re-detect if the brightness balance is different.
3. `python render_mp4.py still 13.2 52.8 93.5 ...`: render frames at every transition, every zoom
   with the facecam and every page cover, then tile them into a sheet and look at it before the full render.
4. `python render_mp4.py video --workers 6` (in the background, about 5x realtime at 4K60), then `audio`, then `mux`.
   Use `--from S --to S` to re-render one stretch when testing.
5. Verify the result:
   - ffprobe the frame count (it must equal NF).
   - Cross-correlate the final audio against `qa_voice.wav` at about 20 checkpoints (0 ms lag expected).
   - Run ebur128: -14 LUFS, peak under -1 dB.
   - Build a contact sheet from the finished MP4 (grab frames one at a time; xstack with drawtext crashes on fontconfig).
6. Delete the part files, then **copy the final MP4 to `%USERPROFILE%\OneDrive\Projects\YT Videos\Video`**
   for review (Coley, every time).

What the renderer adds over CapCut (keep these):
- **60 fps** output from the 60 fps source.
- **A 3% slow push on talking-head pieces**, with an eased 0.35 s framing change only on contiguous
  (non-jump) joins.
- **An S-curve grade and vignette** on talking head only. Screens stay untouched so the text stays sharp.
- **A fixed-size facecam on zooms**, taken from the unzoomed frame with a rounded 34 px mask, never grown or cropped.
- **Custom transitions**, each with its far side held on an edge frame:
  - White_Flash: an exposure bloom.
  - Swipe: a motion-blurred whip at quarter resolution.
  - Zoom: a radial zoom blur.
  - Light_Leaks: a procedural warm leak, screen-blended at 0.6·sin^1.3, computed at 1/8 resolution.
- **Full-frame page covers** (pop False, canvas size) drawn as part of the picture, before the
  transitions, so they move with them. Drawn on top, their facecam hole showed as a grey box.
- **Graphics on a spring** with a damped overshoot, timed so the hit lands on the SFX offset (pop 0.133 s,
  slide 0.100 s, glow 0.067 s). Slides get motion blur.
- **Sample-exact audio:**
  - The voice is placed per segment, with 30 ms equal-power fades at real cuts only.
  - The music stem goes under it.
  - SFX are placed by `peak_at`.
  - It's mastered with a two-pass loudnorm (linear) to -14 LUFS / -1 dBTP, written as 24-bit `mix.wav`, then AAC 320k.

Performance on Windows:
- Read raw frames with `readinto` and `bufsize=0` into preallocated numpy buffers. Default pipe reads crawl at about 33 KB each.
- Decode on CUDA, but convert colour in ffmpeg swscale with BT.709 pinned (`in_color_matrix=bt709:in_range=tv`).
  `scale_cuda` can't output RGB, and cv2's YUV conversion is BT.601.
- Blend premultiplied sprites with cv2 (`multiply`/`add`), cropped to their alpha box and cached when static.
  Float numpy blends take 110 ms a frame, the cv2 version 7 ms.
- Encode with hevc_nvenc (p6, hq, vbr, cq 17, maxrate 160M, AQ, -g 120, BT.709 tags), using parallel
  chunk workers split at piece boundaries, then concat with `-c copy`.
- Never `capture_output` a raw multi-frame decode: 4 s of 4K is 8 GB.
- Grabbing single frames from OBS's long GOP takes about 3 s each, so cache anything measured per frame.

## EDL features (ccut, beyond cuts)

| key | where | what |
|---|---|---|
| `voice` | top | `{source video: processed wav}`; voice track cut in lockstep, camera muted, 30 ms fades (`voice_fade`) |
| `frame` | segment | static reframe `{scale, x, y}` (punch-ins, zoom holds) |
| `zoom` | segment | `{scale, x, y, ramp, in, out}` keyframed push in/out; x/y in half-canvas units: `x=(0.5-u)*2*s`, `y=(v-0.5)*2*s` |
| `drift` | segment | `{s0, s1, x0, y0, x1, y1}` slow continuous push |
| `cam_overlay` | segment | `{rect, clip, k0 or keys}` pre-cropped facecam clip laid over the piece |
| `transition` | segment | `{name, duration}` into the next piece (Pro ones need CapCut Pro; he has it) |
| `images` | top | PNG at canvas px `x, y`, `scale`, `pop` = true / "in" / "out" / "fade" / false |
| `sfx` | top | `start` or `peak_at` (lands the sample's loudest point on a cut) |
| `music` | top | cues `{path, at, start_offset, duration, volume, fade_in, fade_out}` |

Known not to work: **keyframes on video segments in CapCut 9.2+** (2026-10-06: the clip holds its LAST
keyframe for its whole length, so `zoom`, `path` and `drift` don't animate; split zooms into pieces with a
static `frame` instead; image-overlay pops and fades still animate), pycapcut **masks** (built fine, ignored by CapCut's renderer, so an
overlay became full-frame), keyframed **opacity on the main video track** (suspect; use a
black PNG overlay for fades), anything captured-animation-based without a blueprint.

## CapCut operation (Windows, multi-monitor)

- Screenshots: `scripts/capcut_grab.py <out.jpg>` (per-monitor DPI aware; saves the CapCut
  window at 1/3 scale, prints its rect). Multiply screenshot coords by 3 and add the rect origin.
- Clicks: `scripts/capcut_click.py [dbl] X Y` (physical pixels; refuses a point outside CapCut's visible windows, 2026-10-28; refuses unless CapCut is
  foreground). Open a home-screen tile with `capcut_click.py dbl X Y` (a real double-click; Day 35:
  `capcut_drive.py dblclick` is two single clicks 0.55 s apart and only selects the tile). Home tiles sort by
  last edit; locate by screenshot every time. The editor ignores `taskkill` without /F; close it from Menu.
- The home window opens on the Ark or the LG depending on the last session; the editor opens
  maximized on the LG. **Coley wants nothing on his main LG (2026-10-23).** Before launching CapCut
  or opening a draft, start `scripts/cc_keep_spectre.py` (a 15 ms watcher that snaps any CapCut window
  to the Spectre, maximized; he approved the brief flicker). Moving once that way is stable; dragging
  between monitors froze it once.
- Menu (180,30 on the LG editor) → "Back to home page" / "Quit". Quitting shows "A task is in
  progress" (a background update download): confirm OK. Only OK dialogs you recognise.
- Before any click sequence, confirm which project is open (title bar or `.locked` file in
  the drafts folder). Misplaced clicks have opened his other projects and created empty
  ones ("0925 (1)", "0925 (2)").
- He watches videos and works on the LG. Idle check: `GetLastInputInfo`; wait for 2-3 min
  idle or for him to say go.

## Craft rules from top AI-edited videos (2026-11-04; Wiki: AI Video Editing)

Distilled from Duncan Rogoff ("I taught Claude how to edit videos") and Nate Herk ("Opus 5.5 Just Changed Video
Editing Forever"), both watched frame by frame. Provisional until Coley confirms; his confirmed rules in `taste.md` win.

1. **Beat map before any graphic.** First artifact is a table: what he says | what's on screen | where | why. Write each
   beat as "when he says X, show Y at <zone>, because <why>". Check it before building anything.
2. **One idea, one graphic, held long enough to read.** Not a graphic per sentence (Rogoff's audience rejected that).
3. **Prove it at the word.** When the voice claims something, show the real artifact on screen right then:
   screenshot, recording, log, price, timer. Turn real process data into diagrams instead of describing it.
4. **Legibility is a standing rule.** A card, glass panel or scrim behind every element; graphics in zones off the face.
5. **The face never leaves.** When a graphic needs the full frame, keep him on screen as a round bubble (bottom right,
   clear of the duration badge). Two independent creators use this layout.
6. **A chapter system viewers learn.** Big numeral cards ("01 THE RULES") with a recurring progress strip, and one fixed
   recurring segment card per series (same look every time).
7. **Headline habit.** One accent word per headline in the accent style (ours: gold on chrome).
8. **Open on the result.** The payoff or the finished thing first, then the setup; promise and structure on screen by ~35 s,
   with an open loop paid off at the end (matches our retention data: half the viewers gone by 30 to 45 s).
9. **Leave room for the model's own touches,** then keep or cut them at review.
10. **Style from an example.** When Coley admires an edit, break it down (timing map, beat grid, type and colour, structure)
    and save it to `LongForm/library/` or a profile entry before imitating it.
11. **Drafts at half size** for review; full 4K only after approval. Renders capped at 4 to 6 workers, overnight.
12. **Self-review before handing over:** render, look at frames, fix, repeat (the six frame checks above), so Coley
    sees the fifth version, not the first. Every note he gives also rewrites the rule or value that caused it.
13. **A "Coming up" card in the first 30 s** with 2 or 3 preview frames of the payoff moments (Albert Olgaard).
14. **Blur secrets in the render, don't just flag them.** Every API key, token, email or handle the privacy OCR finds
    gets a tracked blur box for its whole on-screen span; re-run the OCR on the render to prove nothing leaks.
15. **Screen-share layout option:** a rounded screen card beside a tall camera card (white or brand page) when the whole
    screen matters and a cam overlay would cover content. Dot-stepper explainers (one short label per step) for process
    sections. Render and review long-forms chapter by chapter before the full 4K pass.

## Lessons log (add to it after every edit)

- 2026-09-25 Asgard Agents Day 1: first edit. Captions were wrong for long-form; zooms
  cropped the facecam (fixed with the cropped-cam overlay); a timeline click desynced 0:19;
  the `H` shadow bug hung exports; exporting is Coley's job. The Paperclip to X Swipe Left was
  dropped because the piece after it was 0.135 s: leave at least the transition's duration on
  both sides, and check the draft's transition count against the EDL.
- Full lessons list: `VideoEditor/LongForm/lessons/lessons.md`.
