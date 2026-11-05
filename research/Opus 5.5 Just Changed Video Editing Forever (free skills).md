
# Opus 5.5 Just Changed Video Editing Forever (free skills)

| | |
|---|---|
| **Channel** | Nate Herk, AI Automation (AI Automation Society, "AIS") |
| **Published** | September 25, 2026 |
| **Duration** | 19:22 |
| **Source** | https://www.youtube.com/watch?v=7jHXoPGnA4c |
| **Topic** | Natural-language prompting of Claude Code (Opus 5.5) plus HyperFrames to edit talking-head, showreel, event-sizzle, whiteboard, course, Reels and product videos |

> Added to the vault 2026-11-04. Audio transcribed locally with Whisper (medium.en); the video was **watched frame by frame** (291 frames, one every 4 s) to see the prompts on screen and the edits they produced. The section map below is paraphrased, not a verbatim transcript. Name fixes: "GBD6 Astra" is GPT-6 Astra, "11labs" is ElevenLabs, "cling" is Kling, and "key.ai" is most likely Kie.ai (an image and video generation API; verify).
> Promotional: free Skool community, a free "HyperFrames student kit" and "scrollcraft" skill as lead magnets, and a plug for his AIS Live event.

---

## Summary

Nate Herk shows that Opus 5.5 inside Claude Code, given HyperFrames (HeyGen's free HTML-to-video tool) and plain-English direction, produces strong edits from one prompt: motion design, sound design, B-roll, screenshots, and generated images and video. Most of the video is a screen share of Claude Code with his camera in a strip on the left. He shows the exact prompt for each example, then plays the output.

He walks through seven examples:
1. His own **intro** (one prompt with timed directions).
2. A 15 s **YouTube showreel** made with a skill reverse-engineered from someone else's reel.
3. A one-shot **company showreel**.
4. A **30 s event sizzle reel** built from a 105 GB folder of event recordings, after three prompts.
5. Three edits of the same **avocado-toast** clip: hand-drawn whiteboard, course style, and a vertical Reel.
6. A **Lululemon** product launch built from real catalog imagery plus generated motion.

He closes with a five-step framework:
1. Transcribe.
2. Cut.
3. Plan the beats.
4. Use skills.
5. Verify, the one he calls most important.

The lesson that matters most for us is **how he prompts**. He tells Claude where things should land ("when I say X, have Y come in where I'm pointing"), how they should feel, and why ("prove to the viewer you can do this"). He leaves room for Claude to add its own touches, and Claude verifies by looking at its own frames.

## Key Takeaways

### Setup
- **HyperFrames**: give Claude Code the GitHub repo URL and say "set up HyperFrames so we can animate videos". It writes HTML and animates it, free.
- **Transcription**: ElevenLabs API (paid per use, faster) or Whisper (free, local, slower). Claude can set either up.
- **Asset generation**: images from an image API (Kie.ai), then turned into video with **Kling**. Claude decides when it needs a generated shot.
- Runs at **effort: high**.

### How he writes an edit prompt (the reusable part)
- **Anchor animations to spoken words.** "When I say *powerful models like Fable 5.1 and GPT-6 Astra*, have them come in where I'm pointing", Fable on the left with the Claude logo, GPT-6 Astra on the right with the OpenAI logo.
- **Legibility as a rule.** "Put a liquid-glass card behind each element so it's readable." Claude also added a soft scrim under the lower-third text without being asked.
- **Name the emphasis.** "When I say *best outputs ever*, put all three words at the bottom and highlight them."
- **Placement zones.** "For the rest of the video, have things come in on the left and right sides of the screen", keeping his face clear in the middle.
- **Give the purpose.** "The whole point is that I'm explaining what Opus can do, so prove it in real time": go get a real screen recording, a real screenshot, a generated image and a generated video.
- **Don't over-specify.** Claude added touches he didn't ask for and he kept them: a slow push-in at the start, a little Claude-style prompt UI on "one prompt", and a verification animation with checkmarks.
- **Emotion over specs when you're unsure.** For the reels he described the feeling (high energy, fast paced, engaging, music synced to the beats, sound effects) rather than shot lists.

### Learn a style from an example, then make it a skill
- He downloaded a reel he admired from X, gave it to Claude: "analyse this video and figure out why it's so good", then "turn that into a skill" (`motion-showreel`). Then: "use that skill to make my own 15-second showreel about YouTube; the YouTube brand should be unmistakable".
- On screen, the skill breakdown covers frame-by-frame analysis, a timing map, a **beat grid at 128 BPM**, cuts landing on beats, a chapter structure, a type and colour system, and a HUD.
- The output pulled his real thumbnails and chose the "Thank You" play-button plaque as the hero. It generated a 3D play button (image, then Kling video), used official YouTube type and colour, and ended on the YouTube logo.
- **Iterate the skill:** after each run, say what you liked and didn't, "update the skill with that", run again. "If you find yourself repeating something, put it in the skill."

### The examples (what each prompt produced)
- **Company showreel (one shot):** "make a dynamic 15-second motion graphics video that shows what an incredible motion designer you are… use real assets and logos from our products." The result had a dot-drop opener with sound, a node diagram (New lead → Claude Code → Update CRM → Reply sent), real website photos, a member counter (450,000 / 626,415) and a chrome 3D logo.
- **Event sizzle (three prompts):** from 105 GB of AIS Live recordings, Claude pulled the best spoken moments from the transcripts as kinetic captions ("IT WAS ELECTRIC.", "NEVER EVEN OPENED VS CODE", "DRIPPY"). It added a tunnel of screens with "30+ SESSIONS", a logo assembled from all the scenes, and a zoom into the red dot: "your seat is in the middle". His critique: a few awkward speech cuts.
- **Whiteboard (one prompt):** "simple, clean, hand-drawn whiteboard style, as if explaining to a kid; some scenes full-screen whiteboard, some split with the whiteboard on the left and my face on the right." The result had numbered handwritten step labels ("1 Toast it!", "2 Let it sit"), a drawing hand, and a "Done!" end. His critique: the eggs were too small and the glaze was only on one corner.
- **Course style (one prompt):** "camera starts full screen, then a rounded crop bottom right; minimal dark background; big bullet takeaways, not wordy; visual aids are AI images with light motion." The result had "STEP 01 Crisp the toast" cards with three bullets, a diagram (laid flat vs stood up, "Soggy bottom" vs "Crisp both sides"), photo cards, and the face in a round bubble.
- **Vertical Reel (one prompt):** "fast paced, switch scenes often, generate B-roll." The result: a hook frame with the finished dish and a face bubble, then **alternating face and food B-roll every 1 to 2 s**, a "7 STEPS" tracker filling with dots, a word caption at the seam, and "AND THAT'S HOW" on the closing food shot.
- **Lululemon launch:** real catalog images of real products, generated running and jumping shots of the models in them, product name supers ("Metal Vent Tech", "Define", "Swifty Tech Shirt 2.0") and a logo end. Brief: the vibe, high energy, synced to the beat.

### His five-step framework
1. **Transcribe** so beats land on time and the AI can find the story.
2. **Cut** mistakes and dead space. Even if you edit yourself, AI cleaning the clip first saves time.
3. **Plan the beats:** "at this point I want this to come in." The more precisely you set expectations, the more aligned the output.
4. **Use skills:** for anything you do repeatedly; start from examples you like.
5. **Verify (the most important):** the agent renders, screenshots and watches its own output, finds mistakes and iterates. You get its fifth or sixth version, not its first.

### How the video itself is edited (from watching it)
- **Cold open (0:00 to 0:43):** the AI-edited intro plays first, then the showreel, then "that entire intro was edited with Opus 5.5". It opens on the result; the setup comes after.
- **The body is one long screen share** of Claude Code: a fixed camera strip on the left, the prompt or output on the right, and the cursor highlighting prompt lines as he reads them. No graphics, cuts are rare, and each example plays at full screen.
- **The outro is a hand-drawn whiteboard list** ("1. Transcribe … 5. Verify") written live, then a short talking-head sign-off.
- The editing effort sits inside the examples; the wrapper is plain. A tutorial format can get away with that because the outputs are the content.

### What to take into our edits (Coley's pipeline)
- **Prompting graphics:** write each beat as "when I say *X*, show *Y* at *where*, because *why*". Add a standing legibility rule (glass card or scrim behind every element) and placement zones that keep the face clear. Our `graphics_plan.py` beats can carry the *why* line.
- **Prove, don't describe:** when the voice claims something, show the real artifact on screen at that word (screenshot, recording, generated proof). Same lesson as [[I taught Claude how to edit videos and it's INSANE]] ("show the process literally").
- **Style from an example:** take an edit Coley admires, have Claude break it down (timing map, beat grid, type and colour, structure) and save it as a skill or a profile entry. The long-form library (`LongForm/library/`) is where that belongs.
- **Leave room for the model's own touches,** then keep or cut them at review.
- **Beat-synced music for reels:** cuts on a BPM grid (his reel skill used 128 BPM).
- **Shorts pattern worth testing:** alternate face and B-roll every 1 to 2 s with a step tracker. It fits our 4-second retention rule (payoff shown in the first frame).
- **Course-style layout:** face full screen first, then shrinking to a round bubble while big bullet cards explain. That matches Duncan Rogoff's bubble layout; two independent creators now use it.

---

## Section map (paraphrased, with timestamps)

- **0:00** Opus 5.5 gives his best AI edits yet; plays the one-prompt intro and a YouTube showreel.
- **0:43** The intro was edited by Opus 5.5 in Claude Code with HyperFrames; how to install HyperFrames; his free student kit.
- **1:51** The intro prompt, line by line: transcribe first; timed directions for the model names, logos and glass cards; highlight "best outputs ever"; left and right placement; prove it with real recordings, screenshots and generated media.
- **3:32** What Opus added on its own: a push-in, a prompt UI, a verification animation.
- **4:24** The YouTube showreel: one prompt; it picked the "Thank You" plaque as the hero.
- **4:59** How: a reel from X → "analyse why it's good" → a `motion-showreel` skill → "make one for YouTube"; generated images sent to Kling.
- **6:58** One-shot company showreel from a resume-style prompt, using real assets.
- **8:15** Plug: the free "scrollcraft" website-design skill.
- **8:42** Event sizzle reel from a 105 GB folder after three prompts; what worked and the awkward cuts.
- **10:40** Avocado toast, edit 1: hand-drawn whiteboard with full-screen and split scenes.
- **12:17** Edit 2: course style with a round face crop, bullets and AI images.
- **13:44** Edit 3: vertical Reel, fast paced with generated B-roll (this is where the shared link starts).
- **14:53** Lululemon product launch from catalog images plus generated motion.
- **16:11** The five things he always does: transcribe, cut, plan the beats, use skills, verify; the agent's self-review loop.
- **19:01** Sign-off.
