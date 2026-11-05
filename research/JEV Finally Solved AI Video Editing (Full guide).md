
# JEV Finally Solved AI Video Editing (Full guide)

| | |
|---|---|
| **Channel** | Albert Olgaard |
| **Published** | September 20, 2026 |
| **Duration** | 6:00 |
| **Source** | https://www.youtube.com/watch?v=ZlICPWwgmmg |
| **Topic** | A plain-Python Claude/Codex editing skill (no Remotion or HyperFrames) that one-shots a full screen-share YouTube video, using the fast "Jev" model for transcript decisions |

> Added to the vault 2026-11-04. Audio transcribed locally with Whisper (medium.en); the video was **watched frame by frame** (144 frames, one every 2.5 s). The section map below is paraphrased, not a verbatim transcript. Whisper heard the model as "JET"; the on-screen logo and title say **Jev**.
> Promotional: free Skool community (the skill), and his own paid dictation app (Cotype, $7 to $9/month). Several claims are unverified: "no human was involved", view counts, and the platform-flagging advice (see the warning below).

---

## Summary

Albert Olgaard says the video before this one, and this one too, were edited end to end by his "Albert YouTube editing skill". It handles zoom-ins, captions, face tracking, on-screen highlights and **automatic blurring of sensitive information** (API keys). He positions it against Remotion and HyperFrames, which he says give a generic AI look; his skill is plain Python and runs in Claude Code or Codex.

The pipeline:
1. Transcribe (with a specific transcription API he doesn't name).
2. A fast model (Jev) makes the transcript decisions.
3. Plan every scene: when to show the screen share and when his face.
4. Build and clean the scenes, blurring secrets frame by frame.
5. A feedback loop checks every change.
6. Render section by section for his review, then the full video.

He runs it on Opus at "UltraCode" effort. A video takes 3 to 5 hours of background compute (up to 10 for long ones), and he hit his weekly Fable limit on a Max 20x plan after about three videos. Inputs are the raw camera file plus a separate screen recording (made with Screen Studio for a clean cursor), and the prompt carries his creative direction ("slow paced, animations only in the intro", "midway, show clean animations of what I'm explaining").

The edit is worth studying for its **screen-share layout**: a rounded screen card plus a tall camera card side by side on a white page, alternating with full talking head at his whiteboard and minimal white explainer scenes.

## Key Takeaways

### The workflow
- **Two inputs:** the camera recording and a separate screen recording (Screen Studio, for a smooth cursor and clean captures).
- **One prompt with direction:** "use the Albert YouTube editing skill to edit this entire video", plus pacing and moments ("show the viral exposé about the model launch in the intro", "slow paced, not too many animations, only in the intro", "around midway, when I explain things, show clean animations").
- **Model choice:** Opus at UltraCode for the main pass; Fable runs out of weekly limit too fast; a cheaper model gets "maybe 80%". The fast Jev model handles the transcript decisions.
- **Time:** 3 to 5 hours per video in the background, up to 10. It's slow on purpose, so the first pass needs no fixes.
- **Review:** renders section by section first; he checks each and asks for fixes in plain language, then the full render.

### What the skill does (claimed and shown)
- Plans scenes from the transcript: screen share vs face, and where zooms go.
- **Cleans the screen share:** highlights the thing being discussed and **blurs sensitive info** (an API key shown blurred on screen) by scanning frame by frame.
- **Catches repeated lines** ("Said twice?" step: a duplicated sentence is detected and one copy removed).
- **A feedback loop** that checks every change before moving on.

### How the video itself is edited (from watching it)
- **Hook (0:00 to 0:34):** proof first. His previous video plays in the screen layout, then his YouTube Studio dashboard with view counts, then the claim that nothing was human-edited, including this video.
- **"Coming up" card at 0:27:** a white card titled "Coming up" with two preview thumbnails of what's ahead (the free community, his Reels). It's an explicit open loop in the first 30 seconds.
- **Screen-share layout (most of the video):**
  - A rounded screen card (~75% width, soft shadow) on a white page.
  - A **tall vertical camera card** in a column on the right, the same rounded style.
  - His face is always visible, the screen is never covered, and nothing is overlaid on the screen except highlights.
- **Talking head** at his whiteboard (a to-do list behind him) for opinions and explanations, framed medium-wide.
- **Explainer scenes:** minimal white pages, one short label each, with a **dot stepper** along the bottom. The current dot is blue, and labels advance: Transcribe → Said twice? → Plan the scenes → Build + clean → Frame by frame → Feedback loop → Section by section. Simple grey-box diagrams animate each step (frame counter "78 → 591", checkmarks filling in). His face sits in a small bubble bottom right.
- **Stat cards:** big blue or green numerals on white ("400x cheaper", "200x faster than ChatGPT", "Per video 3 hours" morphing to "3–5 hours").
- **Name cards:** clean logo plus wordmark on white when a product is named (Claude, Jev, Cotype, Screen Studio). The Claude → Jev handoff is shown as two app icons with progress bars.
- **Proof inserts:** his usage-limit screen, comments under the earlier video, X posts, scaled into the same rounded card style.
- **Tone:** clean, white, Apple-like, and calm. Animation is concentrated in the intro and the explainer; the rest is the screen card and talking head.

### Warning: one claim to ignore
- He re-exports the AI render through CapCut "to rewrite the metadata" because he has *heard* platforms may flag code-edited video. He says himself he doesn't know if it's true. There's no evidence for it, and our rule is no CapCut, so skip it.

### What to take into our edits (Coley's pipeline)
- **Auto-blur secrets instead of only flagging them.** Our privacy pass (`secrets_ocr.py`) finds keys and handles by OCR; the next step is to blur them in the render automatically, frame by frame, the way his skill does.
- **A "Coming up" card in the first 30 s** with 2 or 3 preview frames of the payoff moments. It's a cheap open loop that fits our retention data.
- **A screen-share layout option:** a rounded screen card plus a tall camera card side by side. It suits sections where the whole screen matters and covering it with a camera overlay would hide content. Compare against our current cam overlay on the challenge videos.
- **A dot-stepper explainer** for process sections (setup steps, rules, build stages), one short label per step. It's the same idea as Duncan Rogoff's chapter strip in a quieter form.
- **Big single-stat cards** for prices, budgets and times. We do this; his are simpler (one number, one word, white page).
- **Section-by-section review renders** before the full render (we render per Short; for long-form, render and check by chapter).
- **Duplicate-line detection** is already in our long-form workflow (the dedup check); his skill confirms it's worth automating.
- **A separate screen recording with a clean cursor** (Screen Studio) gives sharper zooms than cropping a 4K OBS capture. Worth considering for future recordings.

---

## Section map (paraphrased, with timestamps)

- **0:00** His previous video, its views, and the claim that nothing was human-edited (zooms, captions, face tracking, highlights, blurring), including this video; plain Python, not Remotion or HyperFrames; the fast Jev model.
- **0:58** Who he is; subscribe.
- **1:17** How it works: transcribe, Jev decisions, plan the scenes, build and clean (blur keys), frame-by-frame pass, feedback loop, section-by-section output, final render.
- **2:10** Get the skill from his free community; set Opus to UltraCode; add the camera file and the screen recording.
- **2:42** The prompt: use the skill, plus direction for the intro, pacing and explainer animations; plug for his dictation app.
- **3:46** It runs 3 to 5 hours (up to 10) in the background; he reviews the section files and asks for fixes in plain language.
- **4:26** Tips: Screen Studio for a clean cursor; the unproven "re-export through an editor to rewrite metadata" advice.
- **4:57** Cost: he hit his weekly limit on Max 20x; cheaper models get about 80% of the way.
- **5:21** The same approach edits his Instagram Reels (high view counts); a Reels version is coming; sign-off.
