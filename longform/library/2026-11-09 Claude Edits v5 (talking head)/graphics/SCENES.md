# v5 scene authoring guide (read fully before building a scene)

Video: "Claude Edits My YouTube Videos. Here's the Whole System" (talking head; every visual is built by us).
Coley's verdict on the earlier version's graphics: not polished enough. Its scenes were small, text-heavy and parked in
the top-left with empty space around them. v5 copies the grammar of his reference edit (Nate Herk, "I Studied 10,000 AI
Websites"; notes in `~/.claude/skills/edit-longform/motion-style.md`, both references). Never copy that video's text,
brand or layouts verbatim.

## The look (non-negotiable)
- **Big and centred.** One idea per scene, filling the middle 70% of the frame. The hero element (number, frame, chart,
  window) is at least 900 px wide in the 1920 layout. Nothing important lives in a corner. No dense paragraphs.
- **Type sizes (1920 layout):** headline `.h1` 104 px (or `.h0` 150 px for a 2 to 4 word punch), sub `.h3` 44 px, body 36 px,
  nothing under 26 px except `.src` source lines (23 px). If text needs to be smaller to fit, cut words instead.
- **One accent per scene:** gold by default, `<body class="cyan">` for the "second AI / review" scenes, `class="red"` for
  mistake scenes. Accent on ONE word of a headline (`<span class="acc">` or `.grad`).
- **Real things live in a `.frame`** (floating rounded frame, accent glow border), with a `.pill` title overlapping its top
  edge. Documents and quotes live on a `.paper` card with `.serif` type. Process steps are `.tile`s. Lists on the face are
  `.chip`s. Tables are `.tbl` rows, re-typeset large, one row lit at a time.
- **Motion:** entrances are blur + fade + slight rise (`data-in`), 0.4 to 0.55 s. No bounces, no spins. Headlines reveal word
  by word (`data-words="0.07"`). Numbers count up (`data-count`). Lines draw on (`data-fx="draw"`). Quoted phrases get a
  marker sweep (`<mark data-in=.. data-fx="mark">`). Cut words get a strike (`<del data-in=.. data-fx="strike">`).
  Something should change roughly every 1.5 to 2.5 s for the first two thirds of the scene; then HOLD.
- **Hold rule (hard):** the complete scene (every word and number on screen, sharp) must hold still for at least:
  a line 3 s, a card 5 s, a table / chart / diagram 8 s, before the scene ends. So finish all reveals early
  (`dur - 8` for charts). After the last reveal only the slow camera push and dust move. Qualifier and honesty labels
  ("Reconstruction", "Illustration", "Recorded estimate", data dates) appear with the FIRST element, not at the end.
- **When a narrated reveal comes too late for the hold rule:** put that element on screen early in a dim state (about 35%
  opacity, no blur) and only LIGHT it on the word. The content is then complete early and the light-up is emphasis.
- **Joins:** the orchestrator cuts scene to scene directly where they abut and blurs in from the face otherwise. Never
  animate your own exit, and make the first frame (t = 0) already show the backdrop and tag (use `data-in="0"`).
- **Mock UI, simulations and rebuilt examples** (recreated terminals, mock frames, simulated generation) carry a visible
  `.label` "Illustration" from their first frame.
- **Copy:** our own words, short, no em dashes or en dashes anywhere (use commas, periods, "to"). Spell names as on
  screen in the sources (Claude, Codex, ElevenLabs, OBS, CapCut, RunPod, GitHub, YouTube, Whisper).
- **Truth:** every number, quote and label comes from `D:\edits\claude-edits\job\inserts\<nn>\NOTES.md` and the files next
  to it, or from the scene's spec. Follow each NOTES "Boundary" section exactly. Never invent a figure, a frame or a quote.
  Rebuilt examples carry a visible `.label` ("Reconstruction" / "Illustration" / "Recorded estimate").
- **Privacy:** no personal paths (`C:\Users\<name>` becomes `~`), no emails, no handles other than Coley's public ones.

## Engine
`graphics/lib/stage.css` (components, tokens) and `graphics/lib/stage.js` (time engine). Read both; they are short.
A scene is `graphics/scenes/<id>.html`:

```html
<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="../lib/stage.css"><script src="../lib/stage.js"></script>
<style>/* scene-only layout */</style>
<body data-dur="11.5" data-seed="12">
<div id="bg"></div><canvas id="dust"></canvas>
<div id="cam">
  <div class="tag" data-in="0.05"><i></i>The qualifier card</div>
  <div class="center">
    <div class="h1" data-in="0.15" data-words="0.07">A limit, not a <span class="acc">promise</span></div>
  </div>
</div>
<div id="vig"></div>
<script>/* optional: Stage.on(t => { ... }) for charts, canvases, custom motion. Pure function of t. */</script>
</body>
```

- `data-dur` is the scene length in seconds and MUST equal the slot's duration in the spec.
- Everything is a pure function of time. No `setTimeout`, no CSS transitions, no autoplaying CSS animations, no
  `Math.random()` (use a seeded generator), no network requests. Images: copy into `graphics/assets/` and reference
  relatively. Video stills: extract a PNG with ffmpeg into `graphics/assets/`.
- Times in a scene are scene-local seconds. The spec gives the narration with scene-local word times: land each
  element 0.1 to 0.2 s BEFORE the word that names it (so it is readable as he says it).
- The renderer adds a 0.3 s fade-out at the end of every scene by itself. Do not animate your own exit unless told.
- `launch.html` is the worked example of a parametric scene with a 3D camera move.

## Sound cues (required)
List the moments that deserve a sound in the scene file, scene-local seconds, at most 7 per scene, one sound per moment,
never one per word:
```html
<script type="application/json" id="cues">[{"t":0.95,"s":"light"},{"t":2.1,"s":"count"}]</script>
```
Names (ElevenLabs kit): `tick` (an item or icon lights), `light` (a tile lights up, shimmer), `count` (a count-up starts,
about 1 s), `type` (typing starts, about 1.6 s), `draw` (a chart line or arrow draws), `strike` (a strike-through),
`wrong` (a mistake is flagged), `right` (a fix or tick lands), `impact` (the ONE biggest number of a scene), `slide`
(a card or row slides in), `scan` (a scan sweep). The orchestrator adds the scene's own entrance whoosh; do not cue it.

## Check your own work (required, every scene)
```
cd "%USERPROFILE%\Projects\Youtube\edits\2026-11-09 Claude Edits v5\graphics"
node render_scene.mjs still <id> 0.4,<mid times>,<dur-0.1>
```
It writes `probe\gfx\<id>_sheet.jpg`. LOOK at it (Read the image) and fix: clipped or overlapping text, anything outside
the frame, low contrast, empty frame areas, a hero element that is too small, text under 26 px, dashes, typos, a reveal
that finishes too late for the hold rule. Iterate until it would sit comfortably next to the reference. Do not run
`render_scene.mjs video`; the orchestrator renders the final frames.

Report back per scene: id, what it shows, the times of each reveal, the time the scene is complete, and any claim you
could not verify from the inserts.
