# Asgard Agents Day 30 (2026-10-23)

The Day 30 update of the five-agent company: the Obsidian "Day 30 - What's New" canvas (scoreboard, follow along, mistakes, behind the scenes, what's next), the Agents Window tour (payroll, reactions, Valhalla, fan polls, C3 Research, PaperRows, the token lock, the sponsor bar), the Sponsor the Hall page, X, and the 24/7 streams on Pump.fun and YouTube.

- Source: `D:/OBS Video/2026-10-23 10-40-36.mp4`, 19:55, one take (track 1 = mic; tracks 2 duplicate / silent).
- Draft: CapCut "Asgard Agents Day 30 - Edit", 15:10 (76% of the take). DRAFT OK, 9 of 9 transitions.
- Working folder: `Projects/Youtube/edits/2026-10-23 Recording 1040/`.
- CapCut kept on the **Spectre** the whole time (Coley, 2026-10-23: "do not move any CapCut or editing portion of the video to my main screen at any time"). The home window and the editor both launch on the LG; `scratchpad/cc_keep_spectre.py` (a 15 ms window watcher) moved each one within a frame or two, and Coley approved that flicker over leaving the draft unopened.

## Coley's brief

"Make improvements upon your last edit and make this one even better, more professional, more fine-tuned transitions, cuts, and animations, and be sure the sound effects are perfectly aligned."

## What was new

- **Frame-exact SFX.** CapCut snaps every clip start and source trim to a whole frame when it opens a draft, so peaks drifted up to 33 ms (measured with `sfx_check.py` against CapCut's own Timelines copy). Fix: every peak target is frame-aligned (`q()`), the animation hit offsets are whole frames (pop 4, slide 3, glow 2), each sample is padded (`audio/pad_sfx.py`) so its loudest 10 ms sits a whole number of frames in, and ccut rounds each start to the nearest frame. Result in CapCut's copy: median 1.7 ms, max 6.7 ms. A sub-frame trim approach failed: CapCut re-snapped the trims on open.
- **Cut edges from energy, not Whisper.** 51 filler/stutter cuts, each edge set at an energy dip (`energy.py` strips), several marked exact where the dip search caught the wrong gap. Two read-throughs of the stitched voice found 9 bad joins (clipped "anything", "came", "sponsorship bar", "They did", "being"; a missed "Um, um" and "um") and two false "uh" cuts that had eaten words.
- **Framing changes hide filler cuts on scrolling pages.** On X he scrolls while talking, so every "um" cut jumped; alternating 1.0 / 1.5x at exactly those cuts makes each jump a camera cut. Same for one canvas cut.
- **Dead air between apps cut out** (about 3.5 min: OBS stingers, loading screens, his YouTube home feed and search history). Transitions sit on those cuts. The sponsor page exits on a cut that skips his browser leaving fullscreen.
- **Highlight boxes measured per moment** (frame grids, `probe/hlgrid_*.jpg`) and held only while the page is still (`hl()` motion guard, min 1.5 s). The canvas scrolls under most lines, so a fixed-layout box would have drifted.
- **Auto card slots.** A card takes the top slot unless a highlight box lives there in its window, else bottom-left anchored clear of the facecam. Long headlines moved detail to the subline so cards stay under 2,500 px.
- **Step strips at 1.45x** (Hiring Hall, Sponsor): at 1.0x they were unreadable.
- **Top-row Window punch-ins at 1.55x:** at 1.5 a top-aligned frame still shows an 18 px sliver of the recorded facecam, and the facecam rule then pulls the frame sideways (Valhalla fell off-frame).
- Music: the series' never-used ElevenLabs variants (Autonomous Division, Nordic Dashboard Ambient, Nordic Dawn Agent). No new bed, because ElevenLabs runs in Coley's browser on the main screen, which he was using.

## Accuracy calls

- "No human involvement" (hook): carded "RUN BY THE AGENTS / After Coley set up the accounts and access".
- PaperRows: "None of the information goes to the agents" and "nothing gets put on their server" cut (the page lists what reaches the server); "STAYS IN YOUR BROWSER" card carries that scope.
- Token: "grab some if you want" kept, "NOT FINANCIAL ADVICE / $ASGARD exists to pay the agents. No promised return." on it. C3 "finds everything necessary": "EVIDENCE, NOT ADVICE".
- "Stale post... a delay in the Asgard agents website" kept, with the canvas's wording carded ("2 STALE POSTS HELD / Until new wording was approved").
- Fan poll "finance tools" carded with its real size (2 votes).

## Measured (v1)

| | v1 |
|---|---|
| Runtime | 15:10 (76% of the take, 3.5 min of it dead air) |
| Segments | 109 |
| Punch-in pieces | 35 |
| Graphics | 136 incl. highlight boxes and the facecam frame |
| SFX | 110, peaks within 6.7 ms of their frames in CapCut's copy |
| Transitions | 9 (White Flash, Snap Zoom, Zoom to Change, 5 Swipe Left, Zoom Transition) |
| Mix | -13.8 LUFS, -1.2 dBTP (offline) |

## v2 (after the Codex audit, `corrections/2026-10-23 Asgard Agents Day 30.md`)

15:04. SFX hits re-read off ccut's saved animation keys (pop 5 frames, glow 6, slide 7, a slide-out swap 0); the stale-post narration that contradicted the canvas cut; Pump.fun feed and chat masked (explicit abuse and token spam); five cards re-worded to the evidence (hook boundary, C3 "evidence report", sponsor review "within 24 hours, card saved with Stripe", "YOUR PDF stays in your browser", suspension "likely"); the sponsor strip says "If approved" and lights Live; the recap closes the opening question ("$66 in checkouts · Not profitable yet"). The voice was re-stitched and transcribed fresh and the mix rebuilt from the final EDL (-13.8 LUFS, -1.2 dBTP). DRAFT OK, 9 of 9 transitions, SFX peaks within 6.7 ms in CapCut's copy.

