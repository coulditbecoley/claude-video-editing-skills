# Corrections: Asgard Agents Day 13 (Codex audit, round 1, 2026-10-06)

Coley asked for the loop himself: Claude edits v1, Codex (Herdr, Editor tab, pane 2) reviews it in CapCut, and Claude edits again. Coley gave no notes of his own this round. The audit is `Projects/Youtube/edits/2026-10-06 AI Agents/AUDIT - Codex.md`, written from 240 live captures over the full 5:47.

| Codex said | What was wrong in v1 | Fix in v2 |
|---|---|---|
| #1 must-fix: the live camera doesn't show what's discussed (2:01, 3:45-4:00, 4:14-4:22) | CapCut 9.2 holds a video clip at its last keyframe. Snapped zooms never showed, and ramps sat at their end value. A test draft proved it | No keyframes on video. Each zoom window is its own piece with a static frame (a punch-in). The facecam overlay is unchanged |
| #2 must-fix: "no announcement until the new story is ready" contradicts the card ("confirmed on chain") | Narration and screen disagreed | The line is cut. The canvas wording goes on a card ("No post until it's on chain"), plus a brand-check card ("Old name? Post blocked") |
| #3: the opening has no stakes | Premise, then a repeated agenda | Cold open: "still 23% down... not profitable yet", then "October 10th is their deadline... four days away", a White Flash, and the hook. The agenda intro is cut |
| #4: trim 30-45 s of repeated canvas setup | Council re-intro, Telegram detail, "follow them there", the logo-quality explanation, the $OHDEER "wait for the description", a restated October 10 | About 40 s cut. Runtime is 4:52, down from 5:47 |
| #5: dissolves double dense canvas text | 13 repair dissolves, some on a framing change | A dissolve only where the framing matches on both sides: 6 left |
| #6: hold the real logo examples | The logos card was up for 3.6 s | Held until the Codex card |
| #7: tight joins (funds, standards, the 5:20 exit) | The outro cut sat 0.30 s after "today", right before "We're" | Kept "We're going to get back into full screen". The Zoom transition sits on OBS's own switch (410.5) over continuous speech. The other joins were rechecked in the stitched literal transcript |
| #9: a 1.2 s music restart at 5:15 | `fill` restarted the dashboard bed for a sliver | Final slivers under 3 s are dropped, and the outro bed starts where the dashboard bed ends |
| #10: Farcaster post hard to read | A 1.4x hold on a moving feed | The profile plays full-frame, then a 1.6x punch-in on the Noodle post |
| #12: close today's story before the next-series CTA | No recap | A recap card: "7 coins · -23% · Oct 10 next" |
| #12: faint silhouette on the last frame | The fade PNG ends exactly at the end | A solid black hold for the last 0.2 s |

Not done:
- #8: one-frame source-duration differences between picture and voice. CapCut snaps durations to whole frames when it opens a draft. The target ranges match, so there's nothing to fix in the EDL.
- The spoken parts of #3 and #12 (new pickup lines). They need Coley to record narration.
- #11: smaller graphic copy. The agenda that carried most of it is gone.

## Rules this adds to taste.md

- Narration that contradicts the screen gets cut, and the screen's wording goes on a card (Codex audit adopted).
- A cold open with the stakes ahead of the hook (provisional, Codex audit).
- A repair dissolve only where the framing matches on both sides (refines the confirmed dissolve rule).
- Zooms are static punch-ins. This is a technical constraint since CapCut 9.2, not a taste choice.

# Final review (Coley exported v2 unchanged, 2026-10-06)

`diff_drafts.py` against both the root draft and CapCut's `Timelines/` copy: no differences. Coley exported `Asgard Agents Day 13 - Edit.mp4` (4:52) and uploaded it as "AI Agents Launched 7 Memecoins | Here's How Much $ They Made". So the v2 provisional rules (the cold open on the stakes, the recap card, cutting and carding narration that contradicts the screen, dissolves only where the framing matches, static punch-ins) shipped unchanged and are promoted to **accepted**.
