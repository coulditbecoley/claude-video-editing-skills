# C3 Research Demo (2026-10-01)

The third learning video, and the first one that isn't Asgard Agents. Coley demos C3 Research, the AI token-audit tool: the landing page, Request Research, picking a token on DexScreener, paying, the loading screen, the finished report, the research library, and an outro. It's a single OBS take on the LG at 4K.

- Source: `Projects/Youtube/videos/2026-10-01 10-19-41.mp4`, 22:35, one take. Both mic channels were live.
- Built draft: CapCut "C3 Research Demo - Edit". `verify_draft.py` returned DRAFT OK, and all 5 of the 5 planned transitions landed.
- Working folder: `Projects/Youtube/edits/2026-10-01 Edit/`.
- Status: **built, waiting for Coley's review.**

## Coley's brief

"Keep [the loading screen] in the video but fast forward through it so people can watch it load. Hit load and then when I come back in to talk that's when you start it back up in normal speed."

- His narration over the loading screen (5:11-5:44, "we're going to fast forward through this...", the bonding-curve warning) stays at normal speed. The 40x starts on "I'll see you then" (344.0) and ends 0.5 s before "And we are back" (1141.55).
- **Check in review:** he may have meant the 40x to start right at "pay" (311), with the narration sped up too.

Also stated mid-edit: "Do not use the cursor tracker. Remove it completely." It's now a confirmed rule in taste.md.

## Measured (metrics.json)

| | C3 Demo | Day 6 | Day 1 |
|---|---|---|---|
| Runtime | 5:39 from 22:35 | 7:07 from 9:25 | 8:08 |
| Cuts/min | 16.3, median piece 2.6 s | 15.0, median 3.5 s | 19.8, median 2.2 s |
| Zoom windows | 36% of runtime | 71% | 49% |
| Graphics | 44, 7.8/min, 10 in the first 60 s | 45, 6.3/min | 38, 4.7/min |
| Transitions | 5 | 4 (6 in v2) | 4 |

`analyze_draft.py` reports "zoomed 92.7%" and "kept 82.4%", and both mislead. The first counts every keyframed piece, including the slow push. The second counts the 798 s played at 40x as kept.

## Structure

1. **Hook (0:00).** "Are you tired of the Robinhood rugs? ... Come with me." Red "TIRED OF THE RUGS?" title, the C3 Research card, and an "AI AGENTS AUDIT ANY CA" card on the chest. Zoom Transition into the site.
2. **01 The site (0:19).** A hero zoom and a Request Research button zoom. Swipe Left to the request page.
3. **02 Request research (0:42).** Zooms on $19 and the chain picker. Cards for $19, hours saved, unbiased, and a chain row (Ethereum, Base, Solana, Robinhood). A 0.4 s Swipe on the mid-sentence tab switch to DexScreener.
4. **03 Pick a token (1:16).** Only the clean take is kept (the three aborted ones and "Oh my God" are cut). Orbio, a CA zoom, a Swipe back to C3, then paste, chain and pay zooms. A 5-step PROGRESS strip runs bottom-left from "find a token" to "agents research".
5. **Pay (1:41).** About 48 s of failed wallet connecting is cut ("Connect your wallet... What?"). Phantom card on the confirm pop-up.
6. **04 The agents go to work (1:54).** The loading narration plays at normal speed, with the camera held on the ring, stage name and elapsed timer.
7. **Fast forward (2:24-2:44).** 798 s at 40x, so 19.9 s. The voice is muted and the bed jumps to -20 LUFS. A "FAST FORWARD 40x" badge, plus a 5-stage strip that mirrors the page's own stages (read off frames at 15 s resolution). A riser lands on the White Flash out.
8. **05 The report (2:54).** "REPORT READY: about 13 minutes". Punchline: "verdict unverified". The music cuts dead and an impact hits. Then the claim matrix and unknowns zooms, plus "AI AGENTS DO NOT PLAY".
9. **06 Research library (4:03).** Public for 7 days, prepare a fresh review.
10. **Outro (4:50).** Calm pacing, no zooms. The X profile and @C3ResearchAI card, then OBS's own crossfade to the talking head (kept, no added transition). Want another chain, subscribe, affiliate program, then a 1.2 s fade.

What was cut:
- Stutters: "It is, um,", "uh," before "website", "you You", "back, back", "if If", "complete, complete", "and they,", "you know,", "And yeah,".
- Restatements: "all of these answers", and the second "download it as a PDF".
- Stray words: "it.", and "So there you go. Yeah,".

## New techniques (provisional)

- **Fast-forward piece.** A ccut segment with `speed: 40` and `mute: true` (`mute` is new in ccut: the piece gets no voice-track audio). The facecam split at 350.5 s keeps the cam overlay off the stretch where he's away. `verify_voice.py` and `verify_draft.py` now handle speed and mute.
- **Cam overlay only where the facecam is in the recording.** `cam_on.json` measures the facecam box at 2 fps (std > 18). The camera keeps the zoomed facecam copy off-frame only on those pieces. Elsewhere it just clamps to the picture.
- **Brand accent follows the product.** Lime #CCFF00 (C3 brand) replaced Asgard gold on the same dark glass cards.
- **Stutters the source passes hid** ("you know" inside a 1.1 s Whisper word, "and they,") turned up only in the literal pass of the stitched `qa_voice.wav`. Isolated join snippets then set the cut points.

## Files here

`gen_edl.py`, `edit.edl.json`, `draft_built.json`, `metrics.json`, `qa.py` (pre-build checks), `still.py` (now speed-aware). The graphics (`graphics/render.mjs`), logos, audio and facecam crop are in the working folder.

## v2 (after Coley's review, same day)

He reviewed v1 without editing it and gave notes in words: `corrections/2026-10-01 C3 Research Demo.md`.

- The landing page and the wallet phase play full-frame.
- The tap into Request Research gets a Swipe and whoosh on its own frame (60.467).
- The Base tile shows Base's white Square mark on Base blue.
- Polish pass:
  - Pause cuts happen only across still screen (`frames.npz`).
  - The 10 speech cuts that still jump get a 0.3 s Dissolve.
  - Transitions sit on each real page or tab change: tap, DexScreener, C3, Read report (the blank page is cut), the library, X.
  - Chips land after their page change, and a whoosh plays into the 40x.
- Result: 64 pieces (from 93), 5:58 (from 5:39), 18 transitions.

`draft_built.json` is now v2. v1 is kept as `draft_built.v1.json`.
