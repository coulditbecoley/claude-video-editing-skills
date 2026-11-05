# AI Agents Business, Episode 1 (2026-10-06)

The premiere of the new series, and the second video through the edit, Codex audit, re-edit loop. Coley has Claude (the left terminal pane) and Codex (the right pane, via Herdr) research a business for the five Asgard agents. He rejects ideas over five Codex reviews until a bank statement converter gets a conditional go. Odin starts it in Paperclip as **PaperRows**, followed by an Obsidian canvas recap and the outro.

- Source: `Projects/Youtube/videos/2026-10-06 11-05-08.mp4`, 37:38, one take, paused in OBS between rounds (hard source jumps).
- Draft: CapCut "AI Agents Business Ep 1 - Edit", v2, 10:48. `verify_draft.py` returned DRAFT OK, and 6 of 6 transitions landed. Static punch-ins were proven live on Day 13. Codex reviewed v1 live.
- Working folder: `Projects/Youtube/edits/2026-10-06 Recording 1105/`. The audit is `AUDIT - Codex.md`, the round is in `corrections/2026-10-06 AI Agents Business Ep 1.md`.
- Status: **v2 built, waiting for Coley's review.**

## Measured

| | v2 | v1 |
|---|---|---|
| Runtime | 10:48 (32.5% of the take) | 14:38 (43.6%) |
| Cuts/min | 10.7, median piece 3.7 s | 9.8 |
| Punch-ins | 51 static, 42.7% of runtime | 59, alternating |
| Graphics | 51 | 53 |
| Transitions | 6 (1 dissolve) | 10 (5 dissolves) |

## Structure (v2)

Cold open (Codex's no-go, then review 5's green light), hook (0:16), the first prompt (0:48), Claude's first ideas (1:33), enter Codex plus a 40x wait (2:33), reviews 1-5 (2:52-6:23, one big card per review naming the idea and its blocker), the new ground rules with the VPS/outage exception (5:35), Paperclip (7:43: Odin fails, gets restarted, then PaperRows), the plan with build underway (8:43), the outro (10:07).

## What was new

- **Keeps written as phrases** (`keep(start words, end words, hint)`), snapped to silences, with `at_in` / `at_out` overrides from isolated snippets. It made a 37-minute take tractable.
- **Chunked transcription** for long takes. **`verify_voice.py` is sample-exact** now.
- **Graphics and music plans** live in their own files (`graphics_plan.py`, `music_plan.py`), timed by phrase.
- **Accuracy rules** from the audit: an unbuilt product is "the plan, build underway", "no humans" is qualified by the real boundary, and a status card lands when the status appears.
