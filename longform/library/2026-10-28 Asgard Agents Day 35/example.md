# Asgard Agents Day 35 (2026-10-28)

The Day 35 update of the five-agent company: the Obsidian "Day 35 - What's New" canvas (scoreboard, follow along, mistakes they caught, behind the scenes, what's next), the Agents Window ($741.12 business total, the token, the buyback), the new 3D Agents World, the Window again (PaperRows, C3 Research, the sponsor tab), X (treasury lock, $500 buyback post, first carousel, feedback post).

- Source: `D:/OBS Video/2026-10-28 11-33-56.mp4`, 20:22, 4K60, one take (track 1 = mic, dual mono; track 2 duplicate; track 3 silent).
- Draft: CapCut "Asgard Agents Day 35 - Edit", **v3 15:39** (v2 15:40, v1 15:48), 207 segments, 7 transitions, 133 images, 94 SFX, 10 music cues.
- Working folder: `Projects/Youtube/edits/2026-10-28 Recording 1133/`. CapCut stayed on the Spectre (left-most screen, the one it was on) the whole time; the watcher snapped the home window there on each launch.

## Coley's brief

"Edit it better than your previous long-form video edits... more professional, more precise, more high-quality transitions and effects and sound effects. Make it visually pleasing... Be sure everything that you add is dialed in perfectly and on time... Be sure the face lines up with the voice and the audio. Add in a slight background music, but not too loud... nice and comforting... Skip any ums and uhs and long spaces." Then a Codex (Editor pane 2) audit and a second round. Keep CapCut on the monitor it's on.

## Structure

1. Cold open: "Here we are in the agents' world. As you can see, this is them at work." (the 3D World), then "This is the amount, $741.12..." over the Window. The bed stops dead on "$741.12" under an impact; the line plays in silence; riser + White Flash + boom.
2. Talking-head hook (the restated first clause of his second line cut), Snap Zoom.
3. The canvas, chapters 01-05, gold boxes on each card he reads, a card in the screen's own words for each.
4. Zoom to Change into the Agents Window: punch-ins on the business total (1.55x) and the token panel (1.5x).
5. **Light Leaks** into the 3D World (the one big reveal).
6. Zoom to Change back to the Window (0.6 s muted picture head: his next word followed the cut with no pause), Swipe Left to X, Zoom Transition to the outro (one framing, 1.2 s fade).

## What was new

- **Per-unit lip sync, any whole-frame lag** (`lip_units.py`). The webcam lag drifted between ~85 and ~435 ms with real in-between values. Full 60 fps MediaPipe track on the GPU decoder (streamed), each unit's best lag smoothed across neighbours; own peaks win at r >= 0.28 by 0.12 (round 2); one manual pin. 93 sections, all edges in cuts; 0.0 ms error in CapCut's saved timeline.
- **GPU transcription** (faster-whisper medium.en on the RTX 3070): default, literal, filler sweep, short-island pass, first-word test, all in minutes.
- **Long spaces:** pauses collapse on still screens; a pause he scrolls through (canvas, the World camera, X) plays as a muted fast-forward (~0.35 s, <= 3x), never a jump; framing flips only on filler cuts that jump.
- **Highlight boxes measured after his scroll settles** (he scrolls one step as he starts each card), `fixed` boxes on the Window.
- **A blank page after a click covered** with a still of the settled page (the X buyback click under a 0.47 s lip shift).
- Music: the series' own calm ElevenLabs beds about 20 dB under the voice (-34 LUFS body, -31 hook/outro); bed changes on chapter boundaries.

## Codex audit (round 1 -> v2)

Adopted: rebuild so draft, EDL and QA match; strong own lip evidence beats smoothing (110.9 s now 317 ms; 419, 499, 616, 833-840, 1027 s low-lag islands); overclaims cut ("He doesn't make up anything", "Everything on the internet... gets in the audit", "They are the only ones that have access", "and get rewarded for it") or carded on the claim (Pay in ASGARD "once live", the Hall's "final test run is next", the buyback "not a promise about price", $741.12 "before costs"); calm one-framing outro; the X loading cover; World/X pauses as fast-forwards instead of cut-and-flip; feedback card off the post's artwork; the cold-open dead stop on the money line.
Not adopted: masking X's sidebar (the 1.5x punch-ins already crop most of it; nothing private there); the spoken "profits" and "carousel type videos" lines stay (his words, carded with the screen's wording; flagged to him).

## Tastes (Claude's choices, provisional)

See `profile/taste.md`, "Sync and pacing (provisional, Day 35)".

## Codex v2 audit -> v3

Verified as landed: the matching QA set, 94/94 SFX, all voice offsets, the claim removals, the calm outro, the fast-forwards. Fixed: the X cover ended a frame short (one loading frame showed; it now runs a frame past the cut, which falls between frames and CapCut snaps either way); the utility and price cards now hold through their whole claims (10.3 s and 9.0 s); three more filler "you know"s cut (188, 356, 949 s; the 949 one hid a "they, they" stutter). Still open: nobody has watched it live (Coley was never idle 3 minutes), so lip sync on the 28 weak units, the motion and the mix are unconfirmed by eye and ear.
