# Claude Video Editing Skills

The Claude Code skills, editing rules and render scripts behind the
[@coulditbecoley](https://www.youtube.com/@coulditbecoley) YouTube channel. Raw OBS recordings go in;
finished long-form videos and vertical Shorts come out, edited by Claude with no human timeline work.

Everything here was learned on real videos: each rule comes from a correction, an audit, channel
retention data or a studied tutorial, and says where it came from.

## What's inside

| Folder | What it is |
|---|---|
| `skills/edit-longform/` | The long-form skill (`SKILL.md`): workflow, craft rules, lip sync, graphics, sound, verification, plus scripts (`render_mp4.py`, voice processing, transcription, secret sweep) and templates. |
| `skills/edit-shorts/` | The Shorts skill: split screen/facecam layout, word captions, the 4-second hook test, transitions, SFX, posting rules, and templates. |
| `longform/profile/taste.md` | The taste profile: every rule marked confirmed (by the creator) or provisional, with its evidence. |
| `longform/lessons/`, `longform/corrections/` | What went wrong on each edit and what the creator changed after reviewing it. |
| `longform/library/` | One folder per edited video: `example.md` (techniques used) and the edit's `gen_edl.py` / graphics and music plans. |
| `longform/tools/` | Draft analysis, diff and aggregation tools from the CapCut era. |
| `renderers/shorts/` | The no-CapCut Shorts pipeline: `gen_shorts.py` (plan), `render_shorts.py` (1080x1920 60 fps render, captions, SFX, loudness), `render_anim.mjs` (cards), `captions.mjs`, `callouts.py` (OCR price rings), `qa_round.py`. |
| `renderers/longform/` | A long-form edit end to end: EDL generator, graphics and music plans, ducked music stem, per-unit lip sync, secrets scan. |
| `retention/yt_analytics.py` | Pulls per-video stats and 100-point retention curves from the YouTube Analytics API (read-only OAuth) to feed lessons back into the skills. |
| `research/` | Breakdowns of AI-edited YouTube videos, watched frame by frame, with what was adopted. |

## Start here for a talking-head video

**The talking-head recipe is for talking-head videos only:** one person talking to camera, with no screen
walkthrough. It is the edit the creator approved with no notes ("absolutely perfect", 2026-11-11).

- The rules: the "Talking-head recipe" section in `longform/profile/taste.md`.
- The worked example: `longform/library/2026-11-09 Claude Edits v5 (talking head)/` (scene engine in `graphics/`,
  the pipeline scripts, the ElevenLabs sound kit list, and `example.md`).
- The house motion style it follows: `skills/edit-longform/motion-style.md`.

In short: claim-first opening with a raw-versus-finished demo, about 63% of the runtime as full-screen motion
graphics landed on the spoken word, lower-third chips over the face, direct cuts and blur-ins, a quiet per-video
sound kit, ducked music, and a second-agent audit before a 4K60 render.

Screen-recording and walkthrough videos (facecam over a screen, zooms, app transitions) are a different kind of
edit: use the general workflow in `skills/edit-longform/SKILL.md` and the earlier library folders for those.

## The pipeline in one paragraph

Word-level Whisper transcripts (GPU) drive every cut, snapped to real silences; pauses collapse; retakes
and fillers go. Lip sync is measured per kept unit. Graphics are planned as beats ("when he says X, show Y
at <zone>, because <why>"), rendered as HTML with Playwright, and landed on the spoken word with frame-exact
SFX. Original music beds come from ElevenLabs (non-copyright only) and are ducked under the voice; the mix
is mastered to -14 LUFS. Renders are 4K60 (long-form) or 1080x1920 60 fps (Shorts) with NVENC. Every edit
is verified by transcript, frame checks, loudness and an OCR privacy pass, then audited by a second agent
(Codex) before delivery. After posting, retention curves feed new rules back into the skills.

## Using it

These are written for one creator's setup (Windows, OBS, an NVIDIA GPU, Claude Code with the skills in
`~/.claude/skills/`), so paths and some tools are specific to that machine and are shown as `%USERPROFILE%`
or `~`. Read the `SKILL.md` files for the workflow; copy the templates and adapt the paths. Rules marked
provisional are defaults, not gospel.

No media, credentials or tokens are included. `yt_analytics.py` expects your own Google OAuth client and
creates its own read-only token locally.

## License

MIT, see [LICENSE](LICENSE). Use it, adapt it, build on it.
