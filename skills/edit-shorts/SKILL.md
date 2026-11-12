---
name: edit-shorts
description: Cut vertical 9:16 YouTube Shorts / Reels / TikToks from Coley's product-demo and screen-recording content (talking head + screen walkthroughs, e.g. C3 Research, his apps and tools) into ready-to-review CapCut drafts - hook-first, own captions, split screen/facecam layout, transitions, music. Use when Coley asks for Shorts, clips, vertical cuts or short-form from a long-form recording or edit. NOT for trading-card hit / No Bulk break clips (those use edit-video).
---

# Short-form edit (product demos, 9:16 CapCut drafts)

Coley, 2026-10-02: the old short-form skill was built for trading-card hits; "recreate your own short
form edit that represents more of what we are doing now." This is that style. First built on the
C3 Research demo (6 Shorts). Everything here is **provisional** until Coley reviews it; fold his
corrections back into this file.

## Hard rules (inherited, confirmed)

- **Music and SFX must be non-copyright** (Coley, 2026-10-03). Generate an original instrumental bed per video with ElevenLabs Music (matched to length and mood), and save the prompt and the file in the edit's `audio/` folder as provenance. No commercial or unknown-licence tracks. Generate it in Coley's logged-in browser via Claude in Chrome (ElevenLabs Music tool); no API key.

- Never export. Deliver CapCut drafts; Coley reviews and exports. **Exception:** when he asks for Shorts without
  CapCut or as finished videos, render them headless ("Headless Shorts" below) and copy the finals to the OneDrive
  review folder.
- Never modify a CapCut project you didn't build. Never click CapCut's timeline.
- Facecam: never scaled by a zoom, never grown or resized mid-shot.
- No em dashes in on-screen copy. Cards say exactly what the product/report says.
- If Coley is at the PC (GetLastInputInfo < 2-3 min), don't drive CapCut on his screen.

## The style (v2: after Codex's full Shorts audit, all fixes adopted 2026-10-02)

- **Canvas** 2160x3840, 30 fps. **Nothing important below y=2880** (YouTube's bottom UI) or on the right
  rail. Check every overlay's full box, not its centre (`gen_shorts.py` asserts it).
- **Layouts:** talking head = full-frame face crop, face high (v ~0.55). Screen with facecam in the
  recording = split (page 0-1990, facecam full width below). No facecam = full frame at scale >= 3.8,
  which crops the browser chrome and taskbar. Verify facecam on/off boundaries frame by frame.
- **One promise, one visible answer, one next step.** Cold open on the line that delivers the
  Short's idea (reorder clips freely). The hook card is up from frame 0 for 2.6 s and can't replace
  missing context in the voice.
- **Captions (ours):** readable 1-4 word UPPERCASE phrases on a dark pill, one key word in the
  brand accent.
  - Pick words by overlap, each word once, so none are lost or doubled at trims.
  - Never overlapping; a minimum dwell. A short chunk merges into the previous one within a sentence.
  - Normalise names and hyphens (ROBINHOOD, DEXSCREENER, SEVEN-DAY) and drop junk tokens.
  - Placement: on the seam (split), y 2560 (full frame or talking head).
- **Pacing:** pauses over 0.45 s collapse to 0.18 s. No automatic punch on screen shots: crop
  deliberately around what's being explained. Punch alternation only on the talking head.
- **Phone-size legibility:** the thing being demonstrated (token + chain, copy button, pasted
  address, wallet pop-up, "Connected") must read at ~270x480. Reframe per clip.
- **Transitions only on real view changes**, on the switch frame (tab/page), each with a whoosh at
  `peak_at`. Cuts within a step. No swipe just before a real change.
- **One progress system:** a single "2/5 COPY THE ADDRESS" label at the top, never a 5-item strip.
  A wait shows one stage label (y 2560) and "13 MIN, TIME COMPRESSED". Skip stages under 0.6 s.
  Speed badges only when they match.
- **Cards are temporary emphasis:** one at a time, about 3 s, cleared at the next section. Report
  proof uses **faithful excerpts** (real screenshot crops of the report, enlarged), shown over a
  muted, full-frame **evidence hold** (report page, no facecam, so no silent lips) long enough to read (~3-5 s).
- **Accuracy:** "unverified" = not enough evidence. Missing checks are limits, not findings. Say
  "retry credit", not refund. Coley's admin checkout ("Free for admin") is fine to show (his call,
  2026-10-02).
- **Endings:** payoff first, then that Short's own closing line + site (`cta-sN`), in the last 1.6 s.
  No identical sales card. Every overlay is clamped to the picture (an overlay past the last clip
  shows over black).
- **Sound:** one bed ~13 dB under the voice, lifted to about -21 LUFS under a muted wait. Impact (no pop) on the
  payoff excerpt, pop on cards, whoosh into a speed-up.

## Workflow

1. Long-form edit folder first (voice WAV, literal transcript, silences, facecam crop, brand cards). Cut from the
   source the long-form intake chose (edit-longform step 1: the frame-rate check, then the secrets sweep's printed
   `EDIT SOURCE:`); if there is no long-form edit, run those two steps here first.
2. Copy `templates/gen_shorts.c3-demo.py` to `<edit>/shorts/gen_shorts.py`. Write `SHORTS` (pieces by
   word start times; `end=`/`Sx` where an energy check moved an edge), `CARDS`, `CAM_OFF`.
3. Copy `render_shorts.mjs` (hook titles, end card) and `render_captions.mjs` into `<edit>/graphics/`.
4. `python gen_shorts.py` renders the caption PNGs and writes the `sN.edl.json` files.
5. Verify every Short before building:
   - `verify_voice.py sN.edl.json`, then a literal transcription. Read it end to end.
   - Check suspicious edges by RMS energy (20-50 ms steps) and isolated snippet transcription, with
     and without a disfluency prompt.
   - `still_v.py sN <seconds...>`: contact sheets of the hook, split, full-frame, cards and end card.
   - **4-second test (channel retention data, 2026-11-04):** read each Short's first 6 s of transcript. The promise
     and its first payoff (the number, the result, the surprise) must both be spoken by 4 s. Reorder or trim until
     there's no drawn-out word, setup clause or unexplained term before 6 s. Prefer under 20 s when the story fits.
8. About 7 days after a batch posts, run `%USERPROFILE%\Projects\Youtube\retention\yt_analytics.py videos 30`
   and `retention <IDs>` (free). Find where each curve drops, match it to the Short's timeline and transcript,
   and add a rule here only when a pattern repeats across Shorts.
6. `uv run ccut build sN.edl.json` for each. Then `verify_draft.py "<title>" sN.edl.json` (DRAFT OK),
   and check that the transition count matches the EDL.
7. New drafts appear after a CapCut restart. Tell Coley the titles, runtimes and hooks.

## Headless Shorts (no CapCut; 3 AI Setups Challenge, 2026-11-04)

1. Copy `templates/gen_shorts.0939.py` and `templates/render_shorts.0939.py` to `<edit>/shorts/` as `gen_shorts.py` /
   `render_shorts.py`. `gen_shorts.py` writes one `sN.json` spec per Short (segments with in/out/speed/mute, offsets,
   images, captions, sfx, bed, voice).
2. `python <skill>/templates/shorts_qa.py --lint` (in `<edit>/shorts/`) before rendering: the long-form lint through
   a spec adapter (against `../main.wav.words.json`), plus offsets, timeline bounds, captions (dwell 0.3 s, overlaps)
   and Shorts floors (FAIL < 0.5 s, WARN < 1.0 s). Details: `shorts_qa.py` docstring.
3. `python render_shorts.py captions`, then `python render_shorts.py render all` (mux pads audio and pins frames).
4. `python <skill>/templates/shorts_qa.py` (no flag = final acceptance): the exact final per spec title (missing =
   FAIL), the long-form deliverable contract, voice clicks per cut, `probe/qa_sheet.jpg`. Exit 1 on any FAIL; same
   3-pass cap as long-form, then hand over the open items.

## Cloud mode (RunPod)

Headless Shorts can render on a RunPod pod instead of the PC: `py cloud.py send ... --make shorts`, then `up`. The full procedure, costs and pitfalls are in the edit-longform skill, section "Cloud mode". The pilot's Short 1 passed `shorts_qa` with 0 FAIL on the pod. Titles containing `$` or `,` arrive under their real names through transfer copies.
- When re-rendering one Short, run `shorts_qa.py <n>` with its number. With no number it checks every `sN.json` and overwrites `probe/qa_report.json` (missing finals become FAILs). The pod agent proposed this lesson in acceptance run E, 2026-11-06.

## Lessons (2026-10-23, Asgard Agents Day 30 Shorts)

- In the split layout, the screen band picked up the Windows taskbar and the recorded facecam (a double face). Every band must stay above the taskbar (y < 2088 source px; fullscreen apps are exempt) and left of the recorded facecam box, unless the band ends above it. `frame_for` asserts this. Fix a failing focus by shifting u or raising the scale, never by loosening the assert.
- Watch for page-load flashes: clicking a link showed 1.1 s of grey. Cover them with a still of the loaded page, framed as the piece frames it (`COVERS`, `cover_png`). Put the still first in `images` so it lands on the lowest image track, under the captions.
- Lip sync carries over from the long-form: each piece takes its section's `av_offset`, and no piece may span a sync edge.
- (Codex audit) Captions turned "$66" into SIX DOLLARS. Whisper's number words need `FIX_AT`, a fix keyed by the word's start time (an empty string drops the word), and a fixed word is always captioned. `KEEP_LOWP` keeps real low-confidence words ("24 seven," at p 0.04).
- When a primed pass hears "uh" at a join, transcribe the UNCUT source across it as a control. Here the control read "about, uh, it will": the filler was in the recording, fused into the next word. Cut the clause and let the card carry its fact.
- The 2004 px facecam leaves 78 px side margins where the screen shows through below the seam. Cover them with black bars rather than scaling the cam to full width, which puts the mouth at ~2870.
- Cards and CTAs: max 1660 px wide, centred at x 1000 (`RAIL_CX`), so nothing runs into the right rail.
- Re-transcribe the QA WAVs after the final build and bind each transcript to its WAV hash. An auditor rejected a stale transcript as evidence.
- `mixcheck.py <edl> <voice wav>` mixes offline. Measure with `ebur128=peak=true`, and trim the bed (-27.5 LUFS target) when the true peak reaches -1.0.

## Lessons (2026-10-07, AI Agents Business Shorts, Codex audit)

- The facecam's eyes AND mouth must sit above y=2880. Crop with no headroom and scale it so the mouth lands at about 2830, rather than a full-width box with the face low.
- Pieces can be written as phrases (`S(start words, end words, hint)`, snapped to silences); see `edits/2026-10-06 Recording 1105/shorts/gen_shorts.py`.
- Captions: enforce 4 words or fewer and one gold word AFTER the fixes are tokenized. A word needs 0.12 s inside its piece. Keep captions at 1700 px wide or less, centred 80 px left (the right rail).
- Cards clear at any later scene change. An impact lands on the spoken verdict, even under the hook.
- Whooshes peak 0.12 s before the cut at 0.2. Measure the full mix (peak under -1 dBFS).
- Never claim more than the clip shows: "goal", "plan, build underway", "got stuck" (not "crashed").

## Lessons (2026-10-02, C3 Shorts)

- Whisper word ends run long. Two edges carried an "um"/"uh" that only isolated snippets exposed
  ("unverified, um, information"; "uh, the reason").
- A start-time lookup that matches the wrong word drops a line silently ("Let me help you out" at 4.56
  vs 4.58). Always read the stitched transcript.
- The end hold ran into the next sentence ("verdict unverified, so we're not gonna"). It is now
  capped at the next word's start.
- The end card collided with a closing punchline card. The end card sits at y ~700, cards at ~1300.
- (v2 audit) Overlays past the last clip render over black (verdict card, 1 s). Clamp everything.
- (v2 audit) `verify_draft.py` matched the voice track by segment count and picked an SFX track. It now
  matches by the voice file.
- Fixing a filler can eat a word ("pop up anyone"). Check each fix by isolated transcription with and
  without a disfluency prompt, and find the edge by 20 ms RMS.

## Posting (Codex, adopted)

Order: Short 6 (7-day window), 4 (bonding curve), 5 (what "unverified" means), 2 (how-to), 1 (overview).
Short 3 only as the result-led recut. Never claim "safe", "rug detected" or guaranteed outcomes.

## Lessons (2026-10-24, PaperRows Shorts from AI Agents Business Ep 3, two Codex audit rounds)

- A whole-take mouth percentile isn't enough. Measure the lower lip on every KEPT facecam frame (`shorts/mouth_check.py`, 5 fps, landmarks 14/17 through the cam_overlay placement). Here the fix was seam 1880 and scale 2.5 (worst lip 2806 against 2880), not a smaller crop.
- A deep punch-in (Excel at 4x) fills the canvas below the facecam too: a full-width black bar sits under the cam on every Short.
- Hard-cut flags (`cut_sfx`) must be stripped from later sub-pieces like `tr`; otherwise every filler cut gets the sound.
- Caption dwell is measured on SCREEN time (start to next start), not speech time: merge within 4 words, borrow up to 0.2 s from a neighbour, or let the last caption run into the silence. Every caption gets a gold word; a caption under 0.5 s appears without the pop.
- `at()` must prefer the piece that contains a time over a neighbour within tolerance (a step label jumped to the end of the previous piece).
- A Short's payoff can't fit as its own card when it's the last line: put it in the closing card and land that card with the impact.
- Page loads and the narrator's late pans get a cover still taken from the settled frame; a moving swipe can't sit under a static cover, so use a hard cut plus a quiet swipe sound.
- A new out-point earlier than the long-form's edge needs an energy check: "CSV" was clipped by 0.4 s (Codex).
- A feature that's plan-gated needs the plan on screen in a standalone Short.

## Lessons (2026-11-04, 3 AI Setups Challenge Shorts, rendered without CapCut, 10 polish rounds + 2 Codex audits)

Worked example: `edits/2026-11-03 Recording 0939/shorts/` (`gen_shorts.py`, `render_shorts.py`, `callouts.py`, `probe/`; `qa_round.py` is superseded by `templates/shorts_qa.py`).
- Frame 0 must carry the finished hook title (start the hook's PNG sequence ~44 frames in, full alpha). Motion comes from a 7% camera punch easing out over 0.4 s and a title slam, with the hit SFX on frame ~1. A whole-frame shake was too much (Codex): dropped.
- Captions: Whisper stretches word ENDS across pauses. Pick words by overlap, but at real source jumps a word must START inside the piece (0.15 s grace at the head, none in the last 0.12 s). Pause-collapse joins (the gap is a real silence) count as contiguous. Fix the rest with explicit keep/add entries keyed to source times, checked by isolated snippets plus 10 ms energy. Highlight the spoken word gold (one PNG per word state).
- The voice chain (compression) can expose quiet fillers the earlier transcript missed ("so the, you know, the project"). Re-transcribe after any mix change. A local cut must start inside the preceding silence, or that pause escapes the collapse.
- Transitions: refine every detected change to 60 fps. A reframe on the same page is a clean cut with a 3.5% settle, not a swipe. A vertical scroll is not a page change (keep an exclusion list). Transitions move only the screen band. The face band never moves (no push, grade only).
- One continuous push per run of contiguous same-framing pieces, never restarted at pause cuts.
- Cards: a soft dark backing under the glass, `text-wrap: balance` on sublines, a spring settle in, a lift-and-fade out, one light sweep. The one-slot rule must not force overlap (no `max(0.3, ...)` clamp).
- OCR-located price rings (`callouts.py`, RapidOCR in the gpuw venv): only when the word is a price ($N, "N bucks"), never while a card covers the band, clamped to the picture piece.
- Price/stat states anchor to the caption word times, not raw Whisper source times (they were 1 s off).
- Hold the screen band on its first frame (`hold`) to hide an accidental context menu; the live face continues below.
- Disclose test mode where buying is described, label teams on result shots, label BEFORE/AFTER the build when footage jumps in time.
- SFX: an ElevenLabs v3 kit (`audio/el-sfx/kit`), levelled against speech RMS: hit -9 dB, swooshes -15, ticks -19, end whoosh -16, price pop -10. Brave asks where to save: answer its "elevenlabs.io wants to save" dialog with `scratchpad/save_dlg.ps1`. Press Escape before each row's download menu, or the click lands on the previous menu's MP3 item.

## Lessons (2026-11-04, first channel data via vidIQ; small numbers, treat as direction)

- Shorts lose most viewers in the first seconds: engaged views were only 30-41% of views on all 4 Asgard Shorts checked. Frame 0 and the first spoken line carry the Short.
- Viewers who stay watch most of it: 46-72% average viewed. The best one ("Made $66", 17 s, a concrete number in the title and hook) had 72% and the most views; the 24-28 s ones sat at 46-49%. Prefer under 20 s when the story fits.
- Long-forms hold 18-27% average viewed (about 3 minutes of a 15). Put the payoff and the strongest material in the first 2-3 minutes.
- Per-second retention comes from the YouTube Analytics API (`Projects/Youtube/retention/yt_analytics.py retention <ID>`, free; vidIQ returned empty curves). On all 5 Asgard Shorts viewers held (replays above 100%) until about 4 s, then fell off a cliff between 4 and 6 s, right where the first sentence ended without a payoff: a drawn-out word ("so... far"), filler setup ("an opportunity for outside AI agents"), or jargon ("payday paused itself, catch-up"). The best one ("Made $66") stated the number in the first 2 s and still held 114% at 4 s. Rule: the promise AND its first payoff land inside 4 s; no slow word, setup clause or unexplained term before 6 s.
- All 5 sat below YouTube's similar-Shorts median (relativeRetentionPerformance 0.17 to 0.46, where 0.5 = median). Long-forms lose half their viewers in the first 30 to 45 s (drops at 9, 18 and 27 s).

## Craft rules from top AI-edited videos (2026-11-04; Wiki: AI Video Editing)

- **From video-use (provisional, 2026-11-04):** same cut-gap safety, `lint_edl.py` and `project.md` session memory (`edit-longform/templates/project.md`) as edit-longform
  (silence of 400 ms or more = clean cut, 150 to 400 ms = re-hear first, under 150 ms = don't cut). Its readable-duration
  floors are long-form numbers; Shorts keep their own faster pacing.

- Same planning rules as edit-longform's "Craft rules" section: a beat map first (say | show | where | why), one idea
  per card, real proof at the word, a card or scrim behind every element, the model's own touches kept or cut at review.
- **Fast-paced pattern worth testing (Nate Herk's Reel):** the finished result in frame 0 with a face bubble, then face and
  B-roll alternating every 1 to 2 s, a step tracker filling up ("3/7"), word caption on the seam, a closing payoff shot.
- **Music on the beat:** for a reel or montage, cut on a BPM grid (his showreel skill used 128 BPM).
- **Hooks from outliers:** before scripting or cutting, pull 3 overperforming Shorts in the niche (vidIQ `outliers`, 5 credits,
  or YouTube search) and note their first-4-second hook pattern.

## Graphic band design reference (2026-11-12)

For any Short with a graphic band or full-screen graphic scene, read `../edit-longform/motion-style.md`, "Reference 3" (Hidden
launch promo): fixed layout, one UI card that performs the claim through timed states, button colour as state, subline last,
glitch cut and ticker tapes only at real section changes. Copy the grammar, never the brand; our palette.
