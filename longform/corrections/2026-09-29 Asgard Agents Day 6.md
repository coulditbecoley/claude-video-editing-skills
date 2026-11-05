# Corrections: Asgard Agents Day 6 (review round 1, 2026-09-29)

Coley reviewed v1 in CapCut without editing it (diff_drafts: no differences) and asked for changes in words.

| Coley said | What was wrong in v1 | Fix in v2 |
|---|---|---|
| "cut out any stutters" | "great, great", "you know" x2, "that that", "it's it's" (+ "um"), "there, the", "the the" survived. Whisper's default and literal passes both smoothed them over | Disfluency-primed pass (initial_prompt full of "um, uh, the the") + diff of two literal passes; every candidate cut A/B tested in isolation |
| "cut out any transition talking cutoffs" | Transition edges sat 0.05-0.12 s after the last word ("doing.", "Come with me.", "built.", "agents."); the flash and whoosh ate the word | >= 0.35 s tail and >= 0.25 s head at every transition; ordinary joins keep 0.14 s tail / 0.10 s head |
| "follow the cursor to wherever it is moving... could barely see the cursor" | Zooms were fixed on an element; the tiny 4K cursor often sat outside the zoomed view | Tracked cursor (template match, 4 shapes), camera follows it with a dead zone, smoothed; gold highlight ring on the cursor while it moves |
| "audio and video error at 6 minutes 10 seconds" | X -> Agents Window tab switch mid-sentence, then a cut 0.46 s later through the pause after it; plus a still-shot push snapping 1.035 -> 1.0 at 5:59 | Swipe on the tab switch, pause after it kept; one continuous camera instead of per-piece pushes |
| "improve the exit sequence, it was a bit choppy" | Per-piece push resets at every join, tight pause collapsing, a zoom in and out on "bookmark it", 0.45 s fade | Continuous slow push, outro collapses only pauses > 0.6 s (keeps 0.34 s), no outro zoom, 1.2 s fade into the held comment card, 3 s music fade |
