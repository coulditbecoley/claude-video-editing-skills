# Asgard Agents Day 13 (2026-10-06)

The fourth learning video, and the first one built with the edit, Codex review, edit loop Coley asked for. Claude built v1, Codex (Herdr, Editor tab, pane 2) audited it live in CapCut, and Claude built v2 from the audit.

- Source: `Projects/Youtube/videos/2026-10-06 10-44-11.mp4`, 7:22, one take. Both mic channels were live.
- Draft: CapCut "Asgard Agents Day 13 - Edit", v2, 4:52. `verify_draft.py` returned DRAFT OK, and all 13 of the 13 transitions landed. Zooms were checked in live playback.
- Working folder: `Projects/Youtube/edits/2026-10-06 AI Agents/`. The audit is in `AUDIT - Codex.md`, the round in `corrections/2026-10-06 Asgard Agents Day 13.md`.
- Status: **v2 built, waiting for Coley's review.**

## Measured

| | Day 13 v2 | v1 | Day 6 |
|---|---|---|---|
| Runtime | 4:52 from 7:22 (66% kept) | 5:47 (78.5%) | 7:07 |
| Cuts/min | 14.4, median piece 3.5 s | 8.8 | 15.0 |
| Zoomed | 52.8%, 34 static punch-ins | 33 keyframed pieces (didn't render) | 71% |
| Graphics | 48, 9.9/min | 46 | 45 |
| Transitions | 13 (6 dissolves) | 19 (13 dissolves) | 4 to 6 |

## Structure (v2)

1. **Cold open (0:00).** "Still 23% down... not profitable yet", then "October 10th is really their deadline... four days away". Full-frame canvas with the -23% and October 10 cards. White Flash.
2. **Hook (0:12).** "Come check out how far the five AI agents have gotten in running their own business." The DAY 13 title and the five portraits, then "Let's get on over to Obsidian". Zoom transition.
3. **Canvas (0:23-2:37).** Chips 01-05: the scoreboard, follow along, they caught their own mistakes, behind the scenes, what's next. Punch-ins on each card he names. Punchline: "Reddit booted them". The music dies with an impact and the red "NO X. NO REDDIT." card, and the music returns on "So no X or Reddit".
4. **Agents Window (Swipe at 2:37).** Full-frame first, then punch-ins: the token charts, $NOODLE, the treasury (after he hides the facecam), the social buttons, fees collected, Valhalla, the polls.
5. **Socials (Swipe at 3:53, then at 4:07).** Farcaster full-frame, a punch-in on the Noodle post, Bluesky's "marked as automated".
6. **Outro (4:22).** OBS's own switch to the camera with a Zoom transition on continuous speech. New series, recap card, comment card, subscribe, fade to black.

## What was new

- **CapCut 9.2 doesn't animate keyframes on video clips** (it holds the last one). Zooms are static punch-ins, so each window is its own piece (`ZOOMS` and `frame_of` in `gen_edl.py`). See lesson 1.
- **The cold open reuses source** that plays again later. `to_out(t, cold=True)` maps graphics to the right copy.
- **Original ElevenLabs Music and SFX**: the first edit under the 2026-10-03 rule. Provenance is in `audio/music-provenance.md`.
- **Narration was checked against the screen.** A line that contradicted the canvas was cut and carded.

## Files here

`gen_edl.py`, `edit.edl.json`, `draft_built.json` (v2), `draft_built.v1.json`, `gen_edl.v1.py`, `edit.v1.edl.json`, `metrics.json`, `metrics.v1.json`, `render.mjs`, `still.py`, `qa.py`, `cam_on.py`, `snip.py`, `AUDIT BRIEF.md`, `AUDIT - Codex.md`, `YouTube Post.md`.
