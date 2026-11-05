# Coley's long-form editing taste

This is the profile the edit-longform skill reads before every edit. Each rule carries its evidence: the video, the date, and whether it's **confirmed** (Coley said it or corrected toward it) or **provisional** (Claude chose it and Coley hasn't pushed back yet).

- **Accepted**: Claude chose it and Coley shipped it unchanged. It's the default, but a correction overrides it.
- A provisional rule becomes accepted once it survives a diff with no correction. It becomes confirmed when Coley states it or corrects toward it.
- A rule is rewritten when a correction contradicts it.
- A confirmed rule always beats a provisional one.

## Hard rules (confirmed)

| Rule | Evidence |
|---|---|
| No captions or subtitles on long-form. On-screen words come only from graphics | Asgard Day 1, 2026-09-25, stated |
| The facecam is never cropped, scaled or broken by a zoom. Overlay the cropped cam over zoomed pieces | Asgard Day 1, 2026-09-25, corrected |
| Audio and picture must be frame-locked. Verify from files, never by clicking the CapCut timeline | Asgard Day 1, 2026-09-25, corrected (0:19-0:35) |
| The voice lines up with his mouth, not just with the source file: the OBS webcam lags the mic (about 100 ms on Day 30) and the voice chain adds 25 ms. Measure lip sync on every recording (MediaPipe lip landmarks vs voice loudness, band-passed 2-8 Hz, pooled windows) and correct it with SYNC, within a frame | Day 30, 2026-10-23, corrected ("the face cam and the audio speech... do not line up... make it perfect") |
| Claude never exports or saves video files. Deliver a CapCut draft for Coley to review and export | Asgard Day 1, 2026-09-25, stated |
| Never modify a CapCut project Claude didn't build | 2026-09-25, standing |
| Facecam sits bottom-right, rounded, in the tight 4:3 crop Coley set in OBS | OBS setup, 2026-09-25, set by Coley |
| No stutters survive: doubled words, "you know", "um", restarts ("there, the"). Hunt them with a disfluency-primed transcription and a diff of two literal passes, not the default pass | Day 6, 2026-09-29, stated ("cut out any stutters") |
| No speech clipped at a transition: at least 0.35 s after the last word and 0.25 s before the first | Day 6, 2026-09-29, stated ("transition talking cutoffs") |
| No cursor tracker: no cursor-following camera, no cursor highlight ring. Zooms are aimed at the element being discussed (supersedes the Day 6 cursor-follow rule) | 2026-10-01 C3 Research edit, stated ("Do not use the cursor tracker. Remove it completely.") |
| One continuous camera on screen sections. A push that restarts at every cut reads as a glitch | Day 6, 2026-09-29, corrected (6:10 error, choppy exit) |
| A tab or app switch mid-sentence gets a short Swipe (0.4 s) on continuous audio, never a cut through the pause right after it | Day 6, 2026-09-29, corrected (6:10) |
| The exit is calm: few cuts, pauses over 0.6 s only, no zoom moves, a 1.2 s fade | Day 6, 2026-09-29, corrected ("a bit choppy") |
| Music and SFX are non-copyright only: an original ElevenLabs Music bed per video, with the prompt kept as provenance | 2026-10-03, stated |
| Landing or overview pages play full-frame: no zoom, no push, few cuts (pauses only over 1.2 s, and only while the page is still) | C3 Demo, 2026-10-01, stated ("I want to see the full landing page the entire time") |
| Wallet connect and payment play full-frame, so the viewer sees it actually connect | C3 Demo, 2026-10-01, stated |
| A transition and its whoosh land on the real screen change (the click or tab frame), never on a cut near it | C3 Demo, 2026-10-01, corrected (the tap into Request Research) |
| Never cut a pause while the screen is moving. Cut only its still stretch. A speech cut that still jumps gets a 0.3 s Dissolve | C3 Demo, 2026-10-01, corrected ("transitions and timing versus the actual video") |
| A logo tile must read as the brand at a glance: the mark on its brand colour, never a bare colour block | C3 Demo, 2026-10-01, corrected (Base tile) |
| The facecam overlay is one fixed size, never grows. Where the facecam is in the shot: no slow push, zooms snap in (punch-in) at 1.5x or more and aim so the recording's own copy is off-frame | C3 Demo v3, 2026-10-01, Codex audit adopted ("make your best recommended choices") |
| On-screen result cards say exactly what the product says (unverified = not enough evidence, not "failed") | C3 Demo v3, 2026-10-01, Codex audit adopted |
| Narration that contradicts the screen gets cut, and the screen's own wording goes on a card. Check spoken facts (day numbers, figures) against the screen | Day 13, 2026-10-06, Codex audit adopted ("until the new story is ready" against the card's "confirmed on chain"; "day 11" in a Day 13 video) |
| A repair dissolve only where the framing is the same on both sides of the cut. A framing change already reads as a deliberate camera cut | Day 13, 2026-10-06, Codex audit adopted (dissolves doubled dense canvas text) |
| An unbuilt or conditionally approved product is shown as the plan (build underway), never as available. Absolute claims in the narration ("no humans") are qualified by the real boundary in the cut | AI Agents Business Ep 1, 2026-10-06, Codex audit adopted |
| A status card lands when the status appears on screen, never ahead of it | AI Agents Business Ep 1, 2026-10-06, Codex audit adopted (Odin's recovery card) |
| Terminals play full frame: no punch-in on a terminal pane. A zoom that cuts off any of the text being read is worse than no zoom (supersedes the Ep 1 v2 static 1.5x Claude-pane frame) | AI Agents Business Ep 1 v3, 2026-10-07, corrected by Coley ("the zoom cuts off some of the text from the Claude terminal... it may just be easier to remove the zoom") at 1:40, 3:00, 3:56, 4:31, 6:23 |
| Fast-forward a long wait (a loading screen) at about 40x with voice muted, keeping his narration before it at normal speed | C3 Demo, 2026-10-01, requested (v1 kept narration at 1x; not yet contradicted) |
| Work happens on the monitor Coley names (Day 20, Day 30: the Spectre). Never leave CapCut or a browser on a screen he excluded; nothing ever on his main LG. CapCut windows that launch on the LG are snapped to the Spectre by a watcher (cc_keep_spectre.py) the instant they appear | Day 20, 2026-10-13, stated ("keep it on the Spectre screen"); Day 30, 2026-10-23, stated ("do not move any CapCut or editing portion of the video to my main screen at any time") and chose the instant snap-back |
| Cut only pauses, ums, stutters, restarts and true repeats. Every line that carries information stays, even when an audit calls it slow (supersedes the Day 20 Codex trims and the Ep 1 "one idea per round" trims) | Day 20 v2, 2026-10-13, corrected ("a lot of transitions cut off valuable information... only cut out pauses and ums and unimportant information") |
| No repair dissolves on speech cuts. Transitions only on real scene changes, inside a pause | Day 20 v2, 2026-10-13, corrected (same note) |

## Structure (accepted)

| Rule | Evidence |
|---|---|
| Cold open on the stakes (the losses, the deadline) ahead of the talking-head hook, about 10-15 s, then White Flash | Day 13, 2026-10-06, Codex audit (#3); shipped unchanged |
| A short recap card before the next-series or subscribe CTA | Day 13, 2026-10-06, Codex audit (#12); shipped unchanged |

## Pacing (accepted)

| Rule | Value | Evidence |
|---|---|---|
| Collapse pauses | over 0.4 s becomes 0.24 s | Asgard Day 1, accepted |
| Cut density | about 20 cuts/min, median piece about 2.2 s | Asgard Day 1 metrics, accepted |
| Footage kept | about 74% of a clean single take | Asgard Day 1 metrics, accepted |
| Cut restatements, stumbles, false starts, filler ("All right.", "So, yeah") | always, but only true repeats: an example or a new detail is not a restatement (Day 20, confirmed) | Asgard Day 1, accepted |
| Keep deliberate rhetorical repetition | always | Asgard Day 1, accepted |
| Hook first: the strongest "I did X" line opens the video | always | Asgard Day 1, accepted |

## Framing (accepted)

| Rule | Value | Evidence |
|---|---|---|
| Talking-head cuts alternate scale | 1.0 and 1.12 | Asgard Day 1, accepted |
| Zoom onto small screen text being discussed | 1.4-1.6 with 0.6 s ramps and a 5% drift while holding | Asgard Day 1, accepted |
| Share of runtime that is zoomed | about 50% | Asgard Day 1 metrics, accepted |
| Still screen shots over 6 s get a push | retired 2026-10-06: CapCut 9.2 doesn't animate keyframes on video clips, so zooms are static punch-ins | Asgard Day 1, accepted; Day 13 lesson 1 |

## Transitions (accepted)

| Rule | Evidence |
|---|---|
| Only at section changes, about 4-5 per 8 minutes | Asgard Day 1, accepted |
| White Flash out of the hook, Zoom between camera and screen, Swipe Left between apps | Asgard Day 1, accepted |
| Whoosh (0.38) peaks on the cut | Asgard Day 1, accepted |
| At least the transition's duration of footage on both sides, or CapCut drops it | Asgard Day 1 defect |

## Graphics (accepted)

| Rule | Value | Evidence |
|---|---|---|
| Density | about 4.7/min overall, front-loaded (10 in the first 60 s) | Asgard Day 1 metrics, accepted |
| On screen | median 3.4 s, never under 1.5 s | Asgard Day 1, accepted |
| Style | dark glass cards, gold and cyan accents, no em dashes | Asgard Day 1, accepted |
| Company logo | on first mention, official mark only | requested 2026-09-25 ("pop-ups of companies I mentioned") |
| Pop sound on every graphic | 0.3 volume | requested 2026-09-25 |
| Zones | logos top-right, chips top-left, stats top-centre, strips bottom-left, nothing over the face | Asgard Day 1, accepted |
| Components | HOOK_TITLE, portrait row, logo card, section chip, STAT_PUNCH, PROGRESS_STEPS, VS_SPLIT, IMAGE_CARD, handle + SUBSCRIBE | Asgard Day 1, accepted |

## Sound (accepted)

| Rule | Value | Evidence |
|---|---|---|
| Voice | -14 LUFS, peak under -1 dB, cleaned (highpass, denoise, compression), 30 ms fades | Asgard Day 1, accepted |
| Music | new bed per section, about -30 LUFS (20 dB under the voice), louder in the intro and outro | Asgard Day 1, accepted |
| Punchline | music cuts dead plus an impact hit, once per video | Asgard Day 1, accepted |
| End | fade to black over about 0.45 s | Asgard Day 1, accepted |

## Accuracy (provisional, Day 20 Codex audit)

| Rule | Evidence |
|---|---|
| Privacy or data claims follow the product page's own scope; a broader line is cut and the page's wording carded | Day 20, 2026-10-13 ("none of your data reaches any server" against the page's browser/server table) |
| No absolute accuracy or autonomy guarantees; show the human boundary including setup and access | Day 20, 2026-10-13 |
| Scheduled things carded in future tense ("payout Oct 14", "the plan") | Day 20, 2026-10-13 |
| A talking-head piece under 1.2 s keeps the previous framing (no half-second flash) | Day 20, 2026-10-13 |
| A pause containing a screen switch is never collapsed; the swipe lands in it | Day 20, 2026-10-13 |

## Visual layer (provisional, Day 20 v3)

| Rule | Evidence |
|---|---|
| A glowing gold box on the exact screen element he names, mapped through the punch-in, only while the page is still | Day 20 v3, 2026-10-13, Claude's choice for "improve it drastically" |
| A thin gold frame on the recorded facecam through screen sections, fading in after each transition | Day 20 v3, 2026-10-13 |
| Chapter chips get the same whoosh as transitions, quieter (0.12) | Day 20 v3, 2026-10-13 |
| One mid-video subscribe nudge where he mentions the series | Day 20 v3, 2026-10-13 |
| Cards on a full-frame landing page sit in its empty side columns and slide in from that side | Ep 2, 2026-10-13, Claude's choice ("more professional") |
| A synthesized SFX kit with one job per sound: swipe for tab changes, air whoosh for camera changes, swish for chips, tick for highlights, coin for money, sparkle for logos, boom for the two big moments, risers into reveals | Ep 2, 2026-10-13, Claude's choice ("better sound effects"); not yet heard by Coley |
| A "not checked" or limited result is carded with the screen's own reason, never with a failure sound | Ep 2, 2026-10-13, Codex audit adopted |
| Personal details in OS dialogs and payment pages are blurred | Ep 2, 2026-10-13, Claude + Codex |

## Mix (provisional)

| Rule | Value | Evidence |
|---|---|---|
| True peak of the full mix | under -1 dBTP (the Asgard export hit 0.0) | Asgard Day 1 export check |

## Precision (provisional, Day 30)

| Rule | Evidence |
|---|---|
| Every SFX peak lands on its animation's hit frame (pop 4 frames in, slide 3, glow 2, whoosh on the cut), frame-exact in CapCut's own timeline (padded samples, frame-aligned targets; `sfx_check.py` under 7 ms) | Day 30, 2026-10-23, Claude's answer to "be sure the sound effects are perfectly aligned" |
| Cut edges come from energy dips, each join re-heard in the stitched voice; a filler fused to a word stays | Day 30, 2026-10-23, Claude's choice ("more fine-tuned cuts") |
| A filler cut on a scrolling page gets a framing change on that cut, so the jump reads as a camera cut | Day 30, 2026-10-23, Claude's choice |
| Dead air between apps (navigation, loading screens, his own feeds) is cut; the app transition sits on that cut | Day 30, 2026-10-23, Claude's choice |
| Highlight boxes held only while the page under them is still | Day 30, 2026-10-23, Claude's choice |


## Sync and pacing (provisional, Day 35)

| Rule | Evidence |
|---|---|
| Lip sync per kept unit, any whole-frame lag: each unit gets the lag that best matches its own mouth and voice (60 fps track), smoothed across neighbours, edges in the cuts (`lip_units.py`). The webcam lag can drift through in-between values, not only jump between two | Day 35, 2026-10-28, Claude's answer to "be sure the face lines up with the voice" (lag drifted 85-435 ms in one take) |
| A pause he scrolls through on a page plays as a quick muted fast-forward (~0.35 s), never as dead air and never as a jump cut | Day 35, 2026-10-28, Claude's choice for "skip... long spaces" |
| On moving footage (the 3D World, X scrolling) a pause over 0.5 s is cut and the framing flips wide / 1.5x on that cut | Day 35, 2026-10-28, Claude's choice (extends the Day 30 framing-change rule) |
| Music "slight... nice and comforting": calm beds about 20 dB under the voice in the body (-34 LUFS against -14), -31 in the hook and outro | Day 35, 2026-10-28, stated by Coley ("not too loud to where it overtakes the speaker") |
| Light Leaks for the one big reveal (into the 3D World) | Day 35, 2026-10-28, Claude's choice ("more high-quality transitions") |

## Sound, transitions and accuracy (provisional, C3 tool video)

| Rule | Evidence |
|---|---|
| Music is pre-mixed into one stem that ducks under the voice (sidechain on the edited voice, ~6 dB): about 21 dB under him while he talks, swelling to about -27 dB in gaps and transitions. A new bed per big section | C3 tool video, 2026-10-28, Claude's answer to "a better job on background music and audio placement"; pane 2 measured the separation and kept it |
| A click that blanks the page: the transition lands on the click frame and a still of the settled page swaps in when the transition ends, held until the live page matches | C3 tool video, 2026-10-28, Claude's choice; pane 2 found no glitch in the composites |
| On full-frame pages (landing, request form, affiliate page) cards sit in the empty left column and show the page's own steps, swapping the lit step in place (a slide-in swish, then soft ticks) | C3 tool video, 2026-10-28, Claude's choice; pane 2 asked for quieter swaps (adopted) |
| A result headline never reassures: "Unverified: not enough evidence. Not proof of a scam. Not proof it's safe", never "Unverified is not a scam" | C3 tool video, 2026-10-28, pane 2 audit adopted |
| A qualifier card stays on screen through the whole claim it qualifies, and comes back when the claim is repeated | C3 tool video, 2026-10-28, pane 2 audit adopted |
| Absolute completeness or safety lines ("find all the secrets", "no rug") are cut when the cut is clean; relative ones ("safer", "safe and secure") get an "evidence and limits, not a safety guarantee" card | C3 tool video, 2026-10-28, pane 2 audit adopted |
| No celebratory sound (coin, impact) under an earnings or safety condition; one sound per point | C3 tool video, 2026-10-28, pane 2 audit adopted |

## Rendered edits (provisional, 3 AI Setups Challenge Video 1)

| Rule | Evidence |
|---|---|
| Graphics are animated sequences (staggered word reveals, overshoot pops, typed URLs, a filling timer), not static cards with a generic pop | 2026-11-03, Claude's answer to "do better on animations... pop-ups"; Codex audit tuned it |
| A long silent build stretch becomes a short muted time-lapse (about 10 s) with a timer card, so the agents are seen working without dead air | 2026-11-03, Claude's answer to "cut out any wasted time, but leave in some clips of the agent's building" |
| Claims about autonomy, budget and timing follow the project's own build log; work done after a deadline is disclosed on screen where the footage shows it | 2026-11-03, Codex audit adopted (#1-#3, #19) |
| Cards on full-frame sites sit in clear zones measured per shot | 2026-11-03, Codex audit adopted (#7) |

## Retention (provisional, channel data 2026-11-04)

- Evidence: YouTube Analytics retention curves for 30 Days (HLMzde5qxuI), Day 35 (HsGkJlaU3Ic) and Day 1 (3rYU-9nwJk8).
  About half the viewers were gone by 30 to 45 s; big drops at roughly 9, 18 and 27 s; 14 to 29% average viewed;
  all below YouTube's median for similar videos (relativeRetentionPerformance 0.24 to 0.39).
- Rule: result or stakes in the first 10 s, a concrete reason to stay by 30 s, the strongest material in the first 2 to 3 minutes.
- Re-check each new long-form at day 7 with `Projects/Youtube/retention/yt_analytics.py retention <ID>`.

## Structure and graphics (provisional, from Duncan Rogoff's six-job edit, Wiki note 2026-11-04)

- Beat map first: a "what I say / what's on screen" table is the first graphics artifact, checked before anything is built.
- One idea, one graphic, held long enough to read. His audience pushed back on a graphic per sentence.
- Chapters: big numeral cards ("01 THE RULES") plus a recurring colour-coded progress strip; one fixed recurring segment card per series.
- When a graphic needs the full frame, keep the face on screen as a round bubble (bottom right, clear of the duration badge) instead of cutting it.
- Show the real process as diagrams (logs, prices, timers, receipts) rather than describing it.
- Headline habit: one accent word per headline in the accent colour or style (ours: gold on chrome).
- (Nate Herk, Wiki 2026-11-04) Write every graphics-plan beat as "when he says X, show Y at <zone>, because <why>". Standing legibility rule: a card or scrim behind every element. Show the real artifact on screen at the word that claims it. Second source for the face-in-a-round-bubble layout while big cards explain.
- (Albert Olgaard, Wiki 2026-11-04) "Coming up" preview card by 0:30; automatic blur of secrets found by OCR; screen card + tall camera card layout for full-screen demos; dot-stepper explainers; chapter-by-chapter review renders. Skip his re-export-through-CapCut metadata tip (unproven, and no CapCut).
