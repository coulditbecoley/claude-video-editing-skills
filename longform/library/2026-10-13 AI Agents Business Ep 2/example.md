# AI Agents Business Ep 2: PaperRows (2026-10-13)

Episode 2 of the series where five AI agents pick and run a business: the reveal of PaperRows (bank statement PDF to CSV), a live demo through Stripe checkout and Excel, the Obsidian "PaperRows Simple Map" canvas, and the first sale. Built with the edit, Codex audit (Herdr, Editor tab, pane 2), re-edit loop.

- Source: `D:/OBS Video/2026-10-13 13-51-49.mp4`, 12:32, one take (a 17 s false start, `13-51-24.mp4`, unused).
- Draft: CapCut "AI Agents Business Ep 2 - Edit". v1 11:15 (89.7% of the take; DRAFT OK, 9 of 9 transitions).
- Working folder: `Projects/Youtube/edits/2026-10-13 Recording 1351/`.
- CapCut kept on the **Spectre**: the home window launched on the Arc and the editor on the LG; each was moved with SetWindowPos (`scratchpad/cc_spectre.py` pattern) before anything else.

## Coley's brief

"Make a huge leap from your last edits. Be more professional, more viral, put in better sound effects and better transitions, and do not cut off any appropriate information." Work only on the screen CapCut is on.

## What was new

- **Cuts only for pauses, ums, stutters and restarts** (Day 20 confirmed rule): 9 stutter cuts, each confirmed in an isolated snippet ("turn turn" was a Whisper artifact and stayed). Keeps run continuous across his canvas pans and page scrolls so only still pauses are cut; a pause cut whose ends still differ (`jump > 2.0`) stays in, and the still run starts 0.2 s after motion stops.
- **Narration against the screen**: "So no data reaches a server or the agents themselves" is cut because the page's own table lists what reaches the server; he explains that table himself right after.
- **Privacy**: his email and saved card on the Stripe checkout are covered with blurred patches cut from the still frame.
- **Synthesized SFX kit** (`synth_sfx.py`, numpy/scipy, no samples): air whoosh, swipe, soft swish, riser, sub boom, tick, chime, coin, glitch, sparkle. Each SFX type has a job (see `graphics_plan.py`).
- **New ccut pop styles**: `slide_l/_r/_up/_down` (overshoot glide in and out, `_in`/`_out` halves for a strip that swaps contents) and `glow` (highlights settle from 106%, fade out). The old `fade` pop is now only for the black end card.
- **Landing page full frame with cards in its empty side columns** (x 0-840 and 2960-3840 at 4K), sized 0.85 to fit.
- **Transitions**: Snap Zoom (hook to screen) and Zoom to Change (site to canvas) are new; risers lead into the White Flash and the site reveal.
- **Voice true peak -2.2 dB** (not -1.5) so voice plus music stays under -1 dBTP.

## Measured (v1)

| | v1 |
|---|---|
| Runtime | 11:15 (89.7% of the take) |
| Cuts/min | 5.8, median piece 6.6 s |
| Punch-ins | 6 windows, 24.4% of runtime |
| Graphics | 92 incl. highlight boxes, 8.2/min, 14 in the first 60 s |
| Transitions | 9, all on real scene changes |
| Mix | -13.9 LUFS, -1.0 dBTP (offline) |
