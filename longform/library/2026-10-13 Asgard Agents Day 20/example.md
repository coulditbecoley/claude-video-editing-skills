# Asgard Agents Day 20 (2026-10-13)

The Day 20 update: the agents' first sale (PaperRows), their own token ($ASGARD) and first payday, the new pixel-art Agents Window, the PaperRows site, the next business (C3 Research), their socials and Paperclip. Built with the edit, Codex audit (Herdr, Editor tab, pane 2), re-edit loop.

- Source: `Projects/Youtube/videos/2026-10-13 09-49-53.mp4`, 14:54, one take. Dual-mono mic, both channels live.
- Draft: CapCut "Asgard Agents Day 20 - Edit". v1 8:26 (DRAFT OK, 18 of 18 transitions). v2 6:32 after the Codex audit (`corrections/2026-10-13 Asgard Agents Day 20.md`).
- Status: **v2 built, waiting for Coley's review.**
- Working folder: `Projects/Youtube/edits/2026-10-13 Recording 0949/`.
- CapCut lives on the **Spectre** monitor for this edit (Coley's instruction). The editor opened maximized on the LG, so the window was moved once to the Spectre (-3840,5) with SetWindowPos; it stayed responsive.

## Measured

| | v2 | v1 |
|---|---|---|
| Runtime | 6:32 (43.9% of the take) | 8:26 (56.6%) |
| Cuts/min | 13.6, median piece 3.7 s | 13.2, median 3.6 s |
| Punch-ins | 10 windows, 30.5% of runtime | 11 windows, 37.4% |
| Graphics | 56, 8.6/min, 14 in the first 60 s | 64, 7.6/min |
| Transitions | 16 (7 scene, 9 dissolves) | 18 (7 scene, 11 dissolves) |
| Mix | -13.9 LUFS, -0.9 dBFS peak (offline) | -13.8 LUFS, -1.0 dBFS |

## Structure (v1)

Cold open (Thor signs every transaction, "not even myself"), White Flash, hook, Zoom into the canvas: 01 what's new, 02 mistakes, 03 behind the scenes, 04 what's next (punchline "no longer creating meme coins": music dies, impact, red card). Swipe to the Agents Window, a click-swipe into PaperRows (full frame, white-mode gag kept), swipe back for C3 Research and the socials, swipe to Paperclip, swipe back for the sign-off, OBS's own camera switch with a Zoom transition, outro with recap, subscribe, site and product cards.

## What was new

- **Narration checked against the canvas**: his "Heimdall's note says the PaperRows post is up" was vague and the canvas says Heimdall HELD the posts until every claim checked out, so the line is cut and the canvas wording is carded.
- **Absolute claims qualified in the cut**: "I don't have to do anything" and "this channel is AI agents without humans" are cut; his usage-limit and sign-in boundary stays, with a "Where Coley steps in" card.
- **Transitions keyed to cuts** when the screen change falls in a pause he never speaks across (`end_before()`); splits only for changes inside continuous speech.
- **Music**: one new 1:00 ElevenLabs bed ("Day 20 Signal", 900 credits, one variant) plus the series' own beds. The Claude browser extension wasn't connected in Brave, so ElevenLabs was driven by raw clicks on the Spectre (`ui.py` in the session scratchpad). Only 1,800 credits were left; 900 remain.
