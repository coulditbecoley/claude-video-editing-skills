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
2. **Never export or save a video file** (CapCut mode). "I will do the exporting... just conduct
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

**Talking-head videos (confirmed 2026-11-11):** follow the "Talking-head recipe" in `profile/taste.md` and start from
`library/2026-11-09 Claude Edits v5/` (v5 scene engine, pipeline scripts, ElevenLabs SFX kit). Coley called that edit "absolutely perfect".

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
- **Tests (after changing any script here):** `python scripts/qa_lib.py`, `python scripts/lint_edl.py`,
  `python scripts/output_evidence.py --self-test`,
  `uv run scripts/secrets_sweep.py --help`, `node tests/test_fonts.mjs`, `python tests/run_fixture.py` (~75 s on the
  GPU, 24 groups; keeps its temp folder on failure), `python <edit-shorts>/templates/shorts_qa.py --self-test`.
- **QA output is compact:** every FAIL in full, WARNs one line per kind with times; `-v` prints all. Full lists:
  `edit.lint.json`, `out/check/report.json`, `shorts/probe/qa_report.json`. Read those only for the item you're fixing.
- Playwright for rendering graphics: import from
  `file:///~/Code/market-analyzer/node_modules/playwright/index.mjs`.
- **Music and SFX must be non-copyright** (Coley, 2026-10-03). Generate an original instrumental bed per video with ElevenLabs Music (matched to length and mood), and save the prompt and the file in the edit's `audio/` folder as provenance. No commercial or unknown-licence tracks. Generate it in Coley's logged-in browser via Claude in Chrome (ElevenLabs Music tool); no API key.
  The Pixabay beds from the first edits are legacy: don't reuse them for new videos.

## Workflow

Work in `%USERPROFILE%\Projects\Youtube\edits\<date> <topic>\`.

**Session memory:** copy `templates/project.md` to `<edit>/project.md`; on start, read it and state the last session
in one sentence; append one dated block per session (provisional, video-use).

### 1. Inventory and watch
- List the source clips (the CapCut project Coley set up tells you which recordings belong
  together; read its `draft_content.json`, don't edit it).
- Contact-sheet frames (one every 30 s) to learn the structure: talking head vs screen,
  where the facecam sits, which apps are shown.
- Multiple short clips of the same line are retakes: keep the complete one.
- **Frame rate:** `python <skill>/scripts/qa_lib.py cadence <clip>` (decoded timestamps, first 120 s). Only if it
  says VFR, conform once (`ffmpeg -i in.mp4 -vf fps=60 -c:v hevc_nvenc -cq 17 -c:a copy in.cfr.mp4`) and edit that.
- **Secrets sweep, every clip with screen footage:** `uv run <skill>/scripts/secrets_sweep.py <clip> --apply` (GPU OCR,
  ~1.3 min per minute of 4K; start it in the background; a repeat on the unchanged clip reuses the completed scan). **Edit the file it prints as `EDIT SOURCE:`**; exit 2 means
  secrets were found without `--apply`. It samples every 2 s, so still eyeball terminal, `.env` and dashboard shots.
- Graphics renderers throw when a `WEB_FONTS` face didn't load; keep `WEB_FONTS` in step with the CSS `@import`.

### 2. Transcribe (word level, twice)
```
python <skill>/scripts/transcribe_words.py --gpu --prompt "Paperclip, Claude Code, Codex, ..." <clips>
python <skill>/scripts/transcribe_words.py --gpu --literal <main clip>
```
Run with the GPU Python (faster-whisper + `nvidia-cublas-cu12` + `nvidia-cudnn-cu12==9.*`, e.g. the gpuw venv);
`--gpu` = medium.en float16, long takes chunked at silences. Without a GPU: drop `--gpu` and run via `uv run python`
from `capcut-cli` (small int8, slow). Outputs are cached: an unchanged clip with the same settings is skipped.
The literal pass exposes flubs the default hides. Whisper word end times run long on drawn-out words, so snap every
cut to a real silence, not a word time. Find fillers with `sweep_gpu.py`, `islands.py` and `firstword.py`
(`edits/2026-10-28 Recording 1133/`), place every edge on `runs.py` (10 ms sound/quiet runs), re-hear every changed join.
**Cut gaps (provisional, video-use):** >= 400 ms silence is clean; 150-400 ms only after a re-hear; under 150 ms only if
a re-hear proves it, else move to a real gap. Snap pads ~50 ms before / 80 ms after kept words (plain cuts only; the
confirmed 0.35 / 0.25 s transition clearances still apply).

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
- **End:** fade to black over the last ~0.45 s via a black PNG overlay with `pop: "fade"`. Hold at least 1 s of
  picture after the last spoken word before that fade starts, so the ending never feels clipped.
- **Never shadow `W, H`** (canvas) in the script: a loop variable named `H` once built a
  3840x1 canvas. ccut now refuses resolutions under 16 px.

### 5. Graphics (bounded component set, landed on the spoken word)
**Read `motion-style.md` first (confirmed 2026-11-06).** It sets the house style: about half the runtime is full-screen motion
graphics, plus an animated chapter map, count-ups, rings, re-typeset tables, drawn-on charts, lit icon rows and lower-third chips.
Where it conflicts with the component list below, it wins.
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
- **Lint (both modes): `python <skill>/scripts/lint_edl.py edit.edl.json`** must exit 0 before any build or render.
  It FAILs invalid timing, missing files (incl. every sequence frame), a cut inside a word (transcript AND waveform
  agree), graphics under 1.5 s visible (taste.md; accents 0.5 s) or never on screen, SFX outside the timeline. It WARNs
  short joins, the 0.35 / 0.25 s transition clearances, readable floors (read 3 / card 5 / diagram 8 s, provisional),
  graphics entering or leaving inside a transition, < 1 s from the last word to the closing fade, and NOT CHECKED when
  voice or transcript is missing. Rules and transcript precedence: `lint_edl.py` docstring. Fix every FAIL; decide
  each WARN group.
- Layout audit in code: overlapping graphic boxes, graphics over the face or the facecam, music gaps.
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
2. **Write `<edit>/th_ranges.json` first:** `[[src_start, src_end], ...]`, the camera-only (talking-head) stretches
   of the source, read off the contact sheet. Those pieces get the face grade and slow push; `[]` means none.
   `video` and `still` stop with an explicit error when it's missing. It is a grading hint only, never proof that a
   frame has no on-screen text.
3. `python <skill>/scripts/lint_edl.py ../edit.edl.json` (step 6) must exit 0.
4. `python render_mp4.py still 13.2 52.8 93.5 ...`: render frames at every transition, every zoom
   with the facecam and every page cover, then tile them into a sheet and look at it before the full render.
5. `python render_mp4.py video --workers 6` (background, ~5x realtime at 4K60; ~45 s chunks so `--changed` rebuilds
   little), then `audio`, then `mux`. `--from S
   --to S` re-renders one stretch for testing. Renders are generation-safe (a failed run never damages the last good
   picture), `audio` records every input it mixed, and `mux` refuses a stale mix or picture and records provenance in
   `out/final.json`. Details: the "partial re-render" and `cmd_mux` comments in `render_mp4.py`. A crash can leave
   `out/render.lock`: confirm no python render is running, delete it, re-run.
6. **`python render_mp4.py check`** checks the deliverable `mux` wrote: provenance, exact frames, 4K60, AAC 48 kHz,
   -14 LUFS / <= -1 dBTP, clicks at every cut on the voice stem, the full lint. Writes `out/check/report.json`,
   `cuts_NN.jpg` (4 frames per cut, ~1 s per cut) and `samples.jpg`; exits 1 on any FAIL. `--no-stills` for a ~20 s
   re-check (it skips the picture evidence below, so it always FAILs "picture evidence not complete"; the check
   that goes with a delivery must run without it). Click
   flags are heuristic.
   **Picture evidence (added 2026-11-08, `scripts/output_evidence.py`, run by `check`, ~6 to 7 min at 13 min 4K60 with
   CUDA decode and 8 CPU workers; CPU-only decode measured 16.6 min on Coley's 20-thread PC, of which decode 13.1 min: the ~10 min CPU target is
   NOT met and the pod's CPU budget is unmeasured. `check --deadline S` (default 3600) is a fail-closed PARENT
   deadline: when it passes, check writes a deadline FAIL report and exits; it does not reap child ffmpeg or
   process-pool workers (they finish their own bounded work), and standalone `output_evidence.py` has no hard deadline
   of its own (a blocked hash thread can outlive a failed run). Not proof of whole-process-tree cleanup):** reads the final itself, never the EDL's intent. Needs CFR 60 that agrees with the
   EDL, verified from every packet's presentation timestamp (anything else, including a dropped frame or jitter, is
   a FAIL). Admission allows 5% per interval and under half a frame of drift, a temporary policy for render_mp4's
   concat joins (one 251/246-tick interval each). Concat writes an exact 60 fps grid since 2026-11-08 (M-S6;
   `render_mp4.py` refuses to commit otherwise), so finals rendered from then on can be held to time-base quantization;
   tightening the admission policy in `output_evidence.py` is still open. Frame
   cells (flash sheets, cut sheets) are picked by each decoded frame's own timestamp, so they stay exact on such files. The EDL and override bytes it measured, and the final's sha256, are bound into the packet; an input that
   changes during the run is refused. Any failure or timeout leaves a `status: failed` report with a FAIL, never an old
   pass; `check`'s report.json carries `evidence.status` (complete / failed / skipped) and `evidence.index_sha256`.
   FAILs on:
   - **every brief near-white flash**, declared White_Flash or not (claude-edits g3 532.80 and 706.68 were declared
     White_Flash transitions and were rejected). `flash_NN.jpg` shows it by decoded frame index (before, onset, peak,
     decay, after).
   - **every graphic whose SHARP, COMPLETE display is under its floor:** line 3 s, card 5 s (WARN under 7),
     table/chart/diagram 8 s, measured every 0.25 s from the moment the frame stops changing to the exit, not from
     scene length. Unmeasurable or mostly-moving holds FAIL too. Set `"kind"` (read, card, diagram, accent) on each EDL
     image; without it, name tokens decide (table/chart/ret = diagram, map/logo/chip = accent), else full-screen = card,
     overlay = read. Any change counts, so an emphasis step also reads as "still changing" (false positives below).
   Thresholds are tuned on claude-edits v3/v4 against the PC audits (retention 5.63 s v3 / 8.63 s v4, privacy footer
   2.02 / 5.52, disclosure 1.88 / 5.38). Writes `out/check/evidence/` (built in a temp folder, swapped in only when
   complete): `flash_NN.jpg`, `overview_NN.jpg` (every 10 s), `scenes_NN.jpg` (entry, mid, exit of every graphic),
   `settled_NN.jpg` (each graphic complete, 960 px), `hold_GNN.jpg` (0.25 s strips of flagged graphics), `frames.md`
   naming every cell, `index.json` (every sheet's sha256 plus final, EDL, overrides and generator hashes) and
   `images.txt` (exactly the sheets to attach). The report's first line (`top`, printed as `TOP:`) gives the counts
   and the worst hold shortfalls. Standalone: `python output_evidence.py <final> <edl>`.
7. **Codex adjudicates the evidence FIRST, then you fix.** Don't re-render for a hold FAIL until Codex has looked at its
   strip: many are emphasis steps, not late content. Attach exactly the indexed sheets, one `-i` per file, prompt from
   stdin (so `-i` can't swallow it):
   ```bash
   EV=out/check/evidence
   codex exec --sandbox read-only --skip-git-repo-check -C <edit> $(sed "s|^|-i $EV/|" $EV/images.txt) \
     --output-last-message audit/R<n>.md - < audit/BRIEF.R<n>.md
   ```
   The brief gives `frames.md`, the `EVIDENCE INDEX` hash, the narration claim behind each graphic, and asks Codex,
   per flash and per hold FAIL (by `flash_NN` / `G<id>`), for a verdict: **real** (content arrives late or the flash
   is a defect) or **false positive** (content complete earlier; only emphasis moves, or presenter motion behind a
   static line), with the sheet and time it judged from. Plus: does each illustration match its claim, readable text,
   clipping or overlap, dashes. Codex reading the EDL or the report is not this audit: the claude-edits code
   illustration passed text review twice and failed on sight.
   Then: fix the confirmed real ones (finish the build earlier, cover or remove the flash), and record each confirmed
   false positive in `evidence_overrides.json` next to the EDL (not in the EDL, which would force a re-render):
   `{"hold_ok": {"43": {"reason": "...", "audit": "R2"}}, "flash_ok": {"7.950": {"reason": "...", "audit": "R2"}}}`
   (graphic id / transition cut time; an object with reason and the adjudicating round, or it is ignored and the
   FAIL stands). Re-run `check`; the final audit note must end with this block (Codex writes it; never edit it):
   `EVIDENCE INDEX: <index_sha256 of that check>`, `PICTURE VERDICT: SHIP`, `SHEETS VIEWED: <n>/<n>` (n = lines in
   images.txt), `BLOCKING FINDINGS: 0`, and one `OVERRIDE <key> AGREE` per entry of index.json `overrides.applied`
   (`hold_ok:G43`, `flash_ok:7.950`). Spec: cloud-backstop `audits/INTERFACE_DEVIATIONS_PC.md` item 32.
   Regression examples (claude-edits v4, adjudicated in FIRST-PASS QA AUDIT R1):
   - G43 s33_table (497.77-515.77), "2.02 s": **false positive**: rows and footer complete from about 501.75; a gold
     highlight moves between finished rows.
   - G52 s42_dur (649.44-665.94), "2.44 s": **false positive**: the restoration qualifier is up by about 657.75; later
     row highlights change the frame without adding content.
   - G55 c08_k1 (706.68-714.50), "0.20 s": **false positive**: the same short line is up from about 707.25; presenter
     motion behind it.
   - G06 s03_agents (32.54-43.54), "0.79 s": **real**: the return arrow and "Then Claude fixes them" arrive near the
     end. Reveal them earlier.
8. **Self-eval loop:** look at the sheets and the report's `review_windows`, fix, then `video --changed` (rebuilds only
   chunks whose graphics changed; any timing/source/renderer change falls back to a full render), `audio` + `mux`,
   `check`. At most 3 passes, then hand Coley the open items with times. Cross-correlate the final audio against
   `qa_voice.wav` at ~20 checkpoints (0 ms lag expected).
   **Known limits (state them in the hand-over):** `check` passing doesn't certify editorial quality, kept words,
   mouth sync or privacy (OCR, clicks, sheets and cadence are sampled); NOT CHECKED items can sit under exit 0; file
   identity is size + mtime; crash recovery is proven for raised errors, not power loss. Listen to and look at every
   flagged join, transition, the hook and the closing fade on the final.
9. Keep the part files until Coley signs off (a later partial re-render needs them), then delete them.
   **Copy the final MP4 to `%USERPROFILE%\OneDrive\Projects\YT Videos\Video`** for review (Coley, every time), and
   put the `CHECK:` summary line in the hand-over note.

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

## Cloud mode (RunPod; built and piloted 2026-11-05)

Use it when Coley wants an edit or render to run off his PC. Rendered MP4 mode and headless Shorts run the same way on a
RunPod GPU pod, and the finals come back to the review folder. Code: `%USERPROFILE%\Projects\VideoEditor\cloud\`
(`cloud.py`, full log and design in `BUILD.md`). Image: `%USERPROFILE%\Projects\video-pod` (CI builds it, and `cloud\IMAGE`
pins the digest). Credentials live in `VideoEditor\.env.txt`: read them by name only, never print values.

```
cd %USERPROFILE%\Projects\VideoEditor\cloud
py cloud.py ctx                                   # once per skill change: bundle skills/context, gitleaks, upload
py cloud.py send <take1.mp4> [take2.mp4] --job <name> --make longform|shorts|both --edit-dir "<edit folder>" --notes "..."
py cloud.py up <name> [--budget 4] [--deadline 6]  # Secure GPU, EU-RO-1; pod self-terminates
py cloud.py status                                # pods, jobs, state, spend
py cloud.py ssh <name>                            # tmux: Claude on the pod; logs in /workspace/edits/<name>/logs
```

The "VideoPod Tick" task (every 10 min while Coley is logged on) pulls each DONE generation into the review folder
(`<job> - <file>` / `<job> (vN) - <file>`) and evidence to `edits\cloud-<job>\g<n>\`. It writes PULLED, and the pod's
watchdog then removes the pod. `py cloud.py pull <name>` does the same by hand.

On the pod (Claude reads `/workspace/ctx/current/POD_CLAUDE.md`): edit as usual, then
`pod.py begin <g>` → render → QA (render check `report.json` / `shorts_qa`) → final Codex audit note →
`pod.py manifest <g> --review <finals> --qa <reports> --audit <note>` → `pod.py done <g>`. A generation the PC can't
deliver is settled by the PC (`cloud.py reject`); the pod never undoes a generation. It writes RESUME.md and stops.

What the pilot measured (0939, 22.3 min 4K60 + 1 Short):
- **Cost and speed.** RTX 4090 Secure at $0.89/h: video 39 min, about 52 min all in. The PC takes about 3 h.
  Rendering is CPU-bound, so the cgroup CPU quota matters more than the GPU. Workers = half the quota, at most 8
  (a consumer 4090 caps NVENC sessions). `video --workers auto` computes half the effective quota (cgroup path and
  affinity) but doesn't apply the cap of 8: on a quota above 17 CPUs, pass `--workers 8`.
- **Upload.** 12 GB of takes uploads quickly. Thousands of small edit files are slow (about 54 min, per-file overhead).
  Send only what the job needs.
- **Names.** RunPod S3 returns 404 on pod-written files named with `,` `$` `&` `+`. The manifest sends those as
  safe-named transfer copies, and the PC restores the real name. Filenames still can't contain `\ : * ? " < > |`.
- **Parity.** A pod render matched a PC render of the same EDL frame for frame (SSIM 0.99+), with audio at 0 ms.
  Lip-sync windows with r < 0.3 are noise: check frames, not lag numbers.
- **Accepted 2026-11-06** (unattended runs, Codex PASS): revisions, delivery, the ctx-delta round trip, checkpoint at
  budget stop, and cost caps all work. Codex is signed in on the volume (2026-11-06), so on-pod audits are real Codex audits; if
  `codex login status` ever says logged out, the audit is a self-review and must say so. Never raise the budget or change account settings without asking.
- **Operations.** EU-RO-1 Secure stock can be empty for a while: `up` refuses cleanly, so retry later. A bad host
  (no CUDA) fails the boot smoke test and removes itself; relaunch. A generation the PC can't deliver:
  `py cloud.py reject <job> <reason>`, then the pod's next `begin`. Review staged context changes in
  `cloud\ctx-staging\<job>\g<n>` and fold the good ones into the skills.

Lessons from the claude-edits cloud run (2026-11-08, folded in from its staged CLOUD_NOTES):
- **Full-screen opaque scenes go in as video.** Render the scene PNGs in batches, encode `out/<id>.mp4` next to the
  sequence folder (`libx264 -crf 10 -g 30 -pix_fmt yuv420p`), delete the PNGs. A `seq` whose `dir` has a sibling
  `<dir>.mp4` is read from the video by `render_mp4.py` and checked by `lint_edl.py` (frame count). 40 scenes took
  about 2 GB instead of about 60 GB. Video has no alpha: keep PNG + alpha for anything that overlays the picture.
- **Memory.** The pod cgroup is 62 GB. The old per-worker sprite caches (60 sprites / 120 premultiplied, 4K each)
  OOM-killed 8 workers; the only log line was ffmpeg's "Broken pipe". The caps are now 8 / 24 and 6 workers used about
  25 GB. On an unexplained "Broken pipe", check `memory.events` (oom_kill) before anything else.
- **Codex from a background shell:** always give `codex exec` a stdin (`- < brief.md`, or `< /dev/null` when the
  prompt is an argument). Without one it hangs on "Reading additional input from stdin".
- **`check` imports `qa_lib` / `lint_edl` from `LF_SCRIPTS`**: when testing a patched copy of either on the pod, point
  `LF_SCRIPTS` at the folder holding the patched copy, or `check` runs the old one.

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
| `seq` | image | `{dir, frames}` 60 fps animation: `dir/000.png...` (alpha), or for an opaque full-frame scene a sibling `<dir>.mp4` (render_mp4 only; no alpha, `path` and PNGs not needed; lint checks its frame count) |
| `src` | segment | render_mp4 only: this piece's picture comes from another recording (B-roll, a second take); never graded as talking head; the voice still follows `in`/`out` of the main voice |
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
