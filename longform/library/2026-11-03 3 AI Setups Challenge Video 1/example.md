# 3 AI Setups Challenge, Video 1 (2026-11-03)

Rendered MP4 (no CapCut, Coley's request): 22:20 at 4K60 from two OBS takes, 20:46 + 13:10 (33:56 raw). Edit folder: `%USERPROFILE%\Projects\Youtube\edits\2026-11-03 Recording 0939\`. Source join: `D:\edits\0939\src.mp4`.

Coley's brief: one video from both takes, the long-form skill but "more professional and precise and cleanly edited", better animations, transitions, SFX and pop-ups than the last edits, cut wasted time but keep some clips of the agents building, no secrets, check the Wiki's AI Video Editing notes, a Codex (Editor tab, pane 2) audit, then a third round.

## Structure

Cold open (the six-hours-later camera line plus the three products, Flash_Cut beats, White Flash) → hook (camera) → 01 the kit (asgardagents.com, order page) → 02 Paperclip setup → 03 the rules (Obsidian canvas, a rule list lighting each rule) → 04 three teams (Paperclip, Hermes, Grok Bot; the prompts fire) → 05 a 10 s muted time-lapse of the build with a ring timer to 6:00 (the 7-minute silent build stretch) → 06 six hours later (camera) → 07-09 the three site tours (full-frame) → 10 the prices side by side → outro.

## Techniques (Claude's choices; Codex-audited, not yet reviewed by Coley)

- **Animated graphics as 60 fps PNG sequences** from HTML/CSS (`render_anim.mjs`): masked word rises, overshoot pops, a short sheen, typed URLs, a ring timer; a held last frame and a 0.3 s exit; states that relight in place carry `noexit`.
- **Lip sync as a curve** (`sync_map.py`): shift changes only inside pauses, applied per frame by the renderer (`seg["pic"]`).
- **Measured clear zones per site** for every card on full-frame pages.
- **Accuracy cards from the vault's build log:** logged human touches, post-deadline versions (Claude + Codex polish after the freeze), AI usage excluded from the $100, test mode at recording; one absolute line cut.
- **Masks** for third-party X handles in Grok Bot's old chat history.
- **Transitions:** Flash_Cut (new) on the cold-open beats and a time skip, White_Flash, Zoom_Transition camera to screen and back, Swipe_Left on app and page changes, Light_Leaks into the build and into the first site, Dissolve (new) inside the time-lapse.
- **Sound:** the series' ElevenLabs beds (no fresh bed: Chrome couldn't load ElevenLabs), a sidechain-ducked stem about 21 dB under the voice, the padded SFX kit with each peak on its card's hit frame, a master at -14 LUFS / -1.3 dBTP.

## Codex audit

20 items (10 must-fix), all applied in v3: see `AUDIT - Codex.md` and lessons 2026-11-03 in `lessons/lessons.md`.

## Coley's review

Pending. v3 delivered 2026-11-03 17:21 to `OneDrive/Projects/YT Videos/Video` (22:20, 4K60, -14.0 LUFS / -1.3 dBTP, voice 0.0 ms at 10 checkpoints; lip sync measured on the render within 33 ms in 15 of 19 windows, three low-confidence facecam windows unverified).
