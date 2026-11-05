# VideoEditor

The training ground for Claude's long-form YouTube editing in CapCut. Its goal is an editor that cuts the way Coley would, learned from his videos and his corrections rather than from generic rules.

The skill that does the editing is `~/.claude/skills/edit-longform/`. It reads `profile/taste.md` before every edit and adds each finished edit to `library/`.

## Research this is built on

`%USERPROFILE%\FenrirVault\Wiki\AI Video Editing\` (start with `AI Video Editing — Index.md`) holds the transcribed tutorials and the shared recipe behind the first rule set: pacing, zoom drift, graphics components and sound. Read it alongside `profile/taste.md`. Where the two disagree, Coley's confirmed rules win. When a new Wiki note adds a technique worth trying, add it to `taste.md` as provisional with the note as its evidence.

## Folders

| Folder | What's in it |
|---|---|
| `profile/` | `taste.md`, the rules with evidence (confirmed or provisional). `metrics.json`, the measured numbers per video |
| `library/<date> <title>/` | One folder per learned video: `example.md` (techniques and tastes), `gen_edl.py`, `edit.edl.json`, `draft_built.json`, `metrics.json` |
| `corrections/` | Coley's changes to Claude's edits, one file per review round |
| `lessons/` | `lessons.md`, the mistakes and the rule that prevents each one |
| `testset/` | Held-out videos Coley edited himself, used to score the editor, never to train it |
| `inbox/` | New teaching material waiting to be filed |
| `tools/` | `analyze_draft.py` (measure any draft), `diff_drafts.py` (what changed), `aggregate.py` (update profile metrics) |

## Adding a video

1. Coley drops material in `inbox/`: the best is a raw recording plus his finished edit; next best is Claude's edit plus his changes.
2. Claude makes `library/<date> <title>/`, runs `python tools/analyze_draft.py "<draft>" --out "library/<...>/metrics.json"`, then `python tools/aggregate.py`.
3. Claude writes `example.md`: the structure, what was cut, the techniques, and the tastes, keeping what Coley confirmed separate from what Claude chose.
4. New or changed rules go into `profile/taste.md` with their evidence.

## The correction loop (how Claude improves)

1. After building, snapshot the draft: copy its `draft_content.json` to `library/<video>/draft_built.json`.
2. Coley reviews in CapCut and fixes whatever he wants.
3. `python tools/diff_drafts.py "library/<video>/draft_built.json" "<live draft folder>" --out "corrections/<date> <video>.md"`
4. Each change becomes a rule in `taste.md`. A provisional rule he left alone gets promoted to confirmed.

## Scoring

Once `testset/` has videos, Claude edits one blind and compares the result with Coley's version (see `testset/README.md`).

## Videos learned

| Date | Video | Status |
|---|---|---|
| 2026-09-25 | Asgard Agents Day 1 | Shipped unchanged (Coley exported the draft with zero edits) |
| 2026-09-29 | Asgard Agents Day 6 | Round 1 corrections applied (v2), waiting for review |
| 2026-10-01 | C3 Research Demo | Built (with a 40x loading-screen fast-forward), waiting for review |
| 2026-10-06 | Asgard Agents Day 13 | Shipped v2 unchanged (after a Codex audit round; static punch-ins since CapCut 9.2) |
| 2026-10-06 | AI Agents Business Ep 1 (PaperRows) | v2 built after a Codex audit (10:48 from 37:38), waiting for review |
| 2026-10-13 | Asgard Agents Day 20 | v3 built after Coley's review of v2 (11:06 from 14:54: content restored, no dissolves, highlight boxes), waiting for review |
| 2026-10-13 | AI Agents Business Ep 2 (PaperRows reveal) | v2 built after a Codex audit (11:13 from 12:32: only pauses, ums and stutters cut; synthesized SFX kit; slide and glow animations), waiting for review |
| 2026-10-23 | Asgard Agents Day 30 | v2 built after a Codex audit (15:04 from 19:55: frame-exact SFX on the animation keys, energy-dip cut edges, framing changes on scroll cuts, dead air between apps cut, Pump.fun feed masked), waiting for review |
| 2026-10-28 | Asgard Agents Day 35 | v3 built after two Codex audits (15:39 from 20:22: per-unit lip sync for a drifting webcam lag, GPU transcription, scroll fast-forwards instead of dead air, Light Leaks into the 3D World, overclaims cut or carded), waiting for review |
| 2026-10-28 | C3 Research tool video | v2 built after a Codex (pane 2) audit (8:00 from 9:34: a sidechain-ducked music stem, loading covers that let the swipe show, left-column step cards on full-frame pages, overclaims cut or carded), waiting for review |
| 2026-11-03 | 3 AI Setups Challenge Video 1 | Rendered 4K60 MP4 (no CapCut) after a Codex (pane 2) audit of the EDL: 22:20 from 33:56 across two takes, animated PNG-sequence graphics, a lip-sync curve, logged-human-touch and post-deadline disclosure cards; waiting for review |
