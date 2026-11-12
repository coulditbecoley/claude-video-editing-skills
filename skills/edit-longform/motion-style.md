# Motion style (Coley, 2026-11-06)

Coley on the first cloud edit: "The edit needs a lot more motion and high quality tables, charts, slides and icons." He pointed at a
reference edit (Nate Herk, "Every Claude 2.0 Concept Explained for Normal People", youtu.be/tcb5q_6jwvY, 21:39) and said to copy
**the editing style, not the content**. Never reuse its text, mascot, brand marks, layouts verbatim or footage. Use our own copy,
our own assets and the channel palette (gold and cyan on dark), and take only the grammar below.

Measured from the reference (scene pass at 768 px plus 4 fps passes over the animated moments):

## Structure and pacing

- **About half the runtime is full-screen graphics or screens**, with the face cut away entirely while the narration keeps going.
  Face and graphic alternate with a median of about 6 to 7 s each, 90th percentile about 18 s. No face-only stretch over about 20 s.
- **The cold open is pure motion design** (about 20 s, before the face appears): a kinetic headline that blurs into focus, a
  horizontal type marquee, product clips in floating frames, a new beat every 1.5 to 2 s.
- **A recurring full-screen chapter map** replaces the small chapter strip. It's a tilted 3D plane with a dotted path, numbered nodes
  and a marker that walks to the current node. Done nodes get checkmarks and the next labels pop in. The camera dollies between
  zones, one zone per part, and the map comes back for about 3 to 5 s at every chapter change. Ours: the 8 pipeline steps as the
  nodes, Coley's stepper language, our colours.
- **Title card with a count-up:** "2 ... 25 Claude concepts" counts up while blurred into focus, then the subtitle swaps.

## Motion grammar

- **Entrances are blur + fade + slight scale**, about 0.4 to 0.5 s from about 20 px blur to sharp. No bouncy overshoot pops.
  Headlines reveal word by word the same way.
- **Count-ups** for every headline number: eased over about 1 s, with the unit label fading in after and an icon above the number.
- **Progress ring** for a share: the arc fills while the number counts (0% to 20%), the label types in, and a small source line sits
  under it ("223 of 1,093 prompts").
- **Icon rows:** rounded or hex tiles, all shown dim (about 30% opacity), each lit at the word that names it. A dotted connector
  draws between lit tiles. Logo rows (official marks) slide in on a light card.
- **Lower-third chips:** small dark pills with an accent icon dot, added one at a time as he lists items, stacking left to right.
  They hold through the sentence. This is the main overlay on the talking head; the face stays otherwise clean.
- **Marker highlight** sweeps across the quoted phrase in a document.
- **Explainer animations for processes:** e.g. a waveform with "transcript says: cut here", then the clipped word turning orange
  with a CLIPPED tag. Diagrams build node by node (You -> Coordinator -> ...) with a live status line.
- **Tables are re-typeset large and clean**, not raw screenshots. Animate them in a row at a time, then highlight or zoom into the
  row being discussed. Same for charts: lines draw on and axes fade in, with the source and date in small type.

## Screens and inserts

- Real UI is always shown **inside a floating rounded frame with a soft shadow** on the dark backdrop, never raw full-bleed. It gets
  a slow push of about 3 to 5% per shot and a punch-in to the detail being discussed, with the cursor visible.
- A small **context tag pill** sits top-left on B-roll, saying what is shown ("Docs, Slides, and Design in every chat").
- "Editorial" slides: a light paper card with a serif headline beside a UI card, for definitions and quotes.

## Look

- Backdrop: near-black with a soft accent radial glow and faint drifting dust particles; nothing is ever flat black.
- Type: heavy sans for numbers (counters are italic heavy), a clean sans for UI, a serif for editorial slides, mono for code.
- One accent colour per scene, plus a light paper colour for "product" slides.

## Transitions and sound

- Mostly hard cuts and quick pushes between graphic scenes; a dissolve through blur into the map. Talking-head cuts stay plain.
- Soft whoosh on scene changes and a tick on each icon or chip lit. Count-ups get a short rising tick, not a pop on every element.

## How to build it here

- `render_mp4.py` already plays 60 fps PNG sequences (`im["seq"]`) with alpha. Build every animated scene as an HTML page driven
  by a time parameter, screenshot it per frame with Playwright, and drop it in as a sequence. Full-screen scenes are opaque
  sequences covering the canvas.
- A full-screen scene must not cover a demonstration insert that plays its own sound, and it must never hide a correction or
  qualifier card the brief requires.
- Lint readable floors still apply: about 3 s for anything read, 5 to 7 s for a card, 8+ s for a diagram or table.

## Reference 2: Nate Herk, "I Studied 10,000 AI Websites" (youtu.be/mImbbszCjCI, 11:18), added 2026-11-09

Same rule: copy the grammar, never his copy, brand, mascot or footage. Watched at 80 scene frames / 768 px. It confirms everything
above and adds these talking-head-plus-design moves. Wiki note: `FenrirVault/Wiki/Website Design/`.

- **Numbered-list video, list as a recurring 3D launcher.** The five patterns live as glowing glass tiles (number badge left, label
  right) in a tilted macOS-style window. At each chapter change the camera re-enters the grid and the current tile lights in the
  accent with a soft shine sweep; done tiles dim, future labels stay **pixel-blurred** so the list teases what's coming. ~3 s each.
  Ours: same idea in our palette whenever a script is a numbered list (lighter alternative to the full chapter map).
- **Step pills on framed demos.** Any "step 1 / 2 / 3" moment puts a glowing pill title ("Step 2 - Break the Edge", "#3 Useful
  tool") overlapping the top edge of the floating rounded frame, and the frame content **demonstrates the step live** (a page mock
  that gains a background, then a card breaking the section edge, then the CTA lifting). Show, don't list.
- **Build the analogy as its own animation.** Every analogy he says gets a purpose-built visual: an empty grey 3D room that fills
  with 60/30/10 colours, a stage, a highlighter. Script for analogies and plan one bespoke scene per analogy.
- **Recreated UI for "paste this into Claude" moments.** Instead of a screen recording, a clean animated mock of the Claude app
  (dark, glass input, typed prompt). Real screen recordings are kept for live proof (Coolors palette, his own site).
- **Citations as "paper" scenes.** Every stat cuts to the source page (CXL article, Purdue paper, Outgrow, ScienceDaily) on a soft
  light-grey gradient backdrop, page centred with a slow push, quoted figure readable. Breaks the dark look on purpose and earns
  trust. Hold long enough to read the headline (about 3 to 4 s).
- **PiP facecam during demos.** When he walks through a real site or his own tool, the face shrinks into a rounded accent-bordered
  card (bottom-right or left third) over the screen, so the talking head never fully disappears during a plug or walkthrough.
- **Blur as the transition.** Scene changes and the cold open use a heavy gaussian blur in/out (whole frame, ~0.3 to 0.5 s)
  rather than wipes. The opener is a blurred count-up ("2,712+") resolving inside a glowing frame, then a fast sizzle of example
  sites, his channel page and community page as credibility, all inside 25 s before the first face shot.
- **Stock B-roll lives inside the frame too** (AR phone shot under "#3 Useful tool"): never full-bleed, always framed with the pill.
- **Pacing:** face shots are short connective tissue (often 5 to 15 s) between graphic scenes; each pattern is roughly
  face intro, then 3 to 6 graphic scenes, then face takeaway. The sponsor-style plug is a PiP demo of his own landing page.

## Reference 3: Hidden launch promo (x.com/Hiddenpad/status/2120894077063631084, 0:22, 16:9), added 2026-11-12

Coley: add this "for the type of design and the quality that it brings". A 22 s product promo, no face and no voice (music only),
all code-style motion graphics. Watched at 3 fps (66 frames). Same rule: copy the grammar, never its copy, brand, logo or colours.
Ours stays gold and cyan on dark. Not confirmed that it was made in Remotion; nothing here depends on the tool.

**Why it reads as high quality**
- **One layout, held for the whole video.** Left third: a tiny mono kicker in spaced caps with a number ("02 / PRIVATE BALANCE"),
  a huge heavy grotesk headline on two lines, one small subline. Right: ONE mock UI card, always the same size and place. The eye
  never hunts; only the content changes.
- **The UI card performs the claim instead of a list stating it.** Every scene is a small state machine: a form types itself with
  a caret, the button goes action colour -> "Launching..." -> green "Live" with a tick, a checklist ticks one line at a time,
  numbers in rows count to new values, a row morphs into a redacted label. Nothing just "appears".
- **Button colour is the state.** Action = hot accent, done = second accent or green. Green is used only for success.
- **The headline is animated data too.** A second headline line arrives when the second action happens ("PRIVATE BUY", then
  "PRIVATE SELL" as the sell row lands). A number inside the headline counts up in the accent (62% -> 97% -> 100%) while the card
  shows the matching figure.
- **Subline lands last**, after the card finished its action, with the final clause in bold white ("Trackers see one pooled
  vault. **Not you.**"). Kicker -> headline -> card action -> subline, every scene.
- **Problem shown as a swarm.** The cold open ("You buy." / "They copy.", one line at a time) puts a crowd of coloured cursor
  arrows with name tags onto one table row while a counter climbs ("2 bots watching" -> 9). The fix: the row is blacked out, every
  tag flips to "404?" and the cursors scatter, the red status line turns calm. "Not anymore."
- **Two accents with meanings**, not decoration: one for danger and action, one for the safe or finished state. Near-black
  backdrop with a soft radial glow in one corner and a faint warm glow in the opposite one. Card = dark glass, thin border,
  coloured glow under it.
- **Type:** heavy grotesk for headlines (sentence case in the story open, uppercase for features), mono for all data, kickers
  and tickers. Two-tone taglines (white claim, grey second half).

**Transitions**
- **Glitch cut:** 2 to 4 frames of horizontal bars streaking across plus one washed-out flash frame, then the new scene. Used
  only at real section changes.
- **Crossed ticker tapes:** a thick accent tape with bold caps and a thin dark mono tape, tilted a few degrees in opposite
  directions, scrolling, with x separators and blacked-out bars between phrases. They wipe from story to features and come back
  framing the closing headline, so the wipe is also a recap of the feature names.

**End card**
- Centred headline with one accent word, then the wordmark builds (the logo's own gimmick animates in last), two-tone tagline,
  a mono micro line, and a pill that first appears as a solid accent bar and then resolves into "LIVE TODAY" with a pulsing dot.
  Small persistent logo bottom-right through every feature scene. Fade to black.

**Pacing (measured)**
- 8 beats in 22 s: open 4 s, twist 2 s, four features at about 3 s each, tagline 1.5 s, end card 4 s. Inside a scene something
  changes state every 0.3 to 0.5 s, and the finished state holds about 1 s before the cut.

**Where we use it**
- Cold opens, numbered feature rundowns ("what the skill does": cuts, graphics, music, render), product plugs, and the graphic
  band in Shorts. For long-form with narration, slow each scene to the readable floors above (3 s read, 5 s card).
- Build with the existing scene engine (`graphics/lib/stage.js`: `data-in/out/on/count/words/fx`). One scene template: kicker,
  headline (second line and count-up optional), one card with timed states, subline last. Cursor swarm = absolutely positioned
  tags with staggered `data-in` and a class flip at the fix.
- Checks before shipping a scene in this style: card in the same place as the previous scene; every element has a state change,
  not just an entrance; subline after the action; one accent meaning per colour; finished state held 1 s.
