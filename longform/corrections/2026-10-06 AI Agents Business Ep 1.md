# Corrections: AI Agents Business Ep 1 (Codex audit, round 1, 2026-10-06)

Coley's loop again: Claude built v1 (14:38), Codex (Herdr, Editor tab, pane 2) audited it live in CapCut, and Claude built v2 (10:48). Coley gave no notes of his own. The audit is `Projects/Youtube/edits/2026-10-06 Recording 1105/AUDIT - Codex.md`, from 356 live captures.

| Codex said | v1 | v2 |
|---|---|---|
| #1 must: define "no humans" | Promised zero humans. The VPS/outage exception that unlocked review 5 was cut. The 30-day card said "zero human help" | His full exception passage is restored. The 30-day card reads "Agents run every task inside the business". The canvas keep ends before "zero human help" |
| #2 must: approval isn't proof | The conditions were cut. The recap read like a live product, and the outro said "here's your guys, they got it" | Conditions restored (text PDFs and CSVs first, every value traced to its source row). "THE PLAN: BUILD UNDERWAY" chip. Privacy and price cards say "designed" and "planned". The availability line is cut |
| #3 must: Odin card announced recovery early | "ODIN RUN FAILED / Cleared and back to work" on the failure | "Workspace validation error" on the failure. "ODIN BACK TO WORK" lands on "looks like we're going again" |
| #4 must: the $3,000 | "Model usage so far" | "~$3,000 API-PRICE USAGE / Prior project, Sept 13-18, at retail API rates" |
| #5, #6: too long, repeats | 54 s intro. Every rejected idea fully explained | 25 s intro. One idea, one blocker and one decision per round. The lawsuit stats, kit explanation, repeated approvals and outro scheduling are cut |
| #7: tracker too small and inaccurate | A 5-column strip ("Too niche", "Lawsuit risk") | A large card per review naming its idea and the real blocker (customers, too complicated, no audience, reach and costs, conditional go) |
| #8: camera alternation | Full and 1.35x alternated at every cut | One static 1.5x Claude-pane frame while he reads, full frame otherwise |
| #9: dissolves across framing changes, thin handles | 5 mismatched dissolves | Dissolves only where the framing matches (1 left). The canvas-to-outro tail is 0.14 s, the most the words allow ("test." then "We need") |
| #11: stutters | — | Cut "more less complex" and "you know, it might not work, it might not work". The Codex-explanation fillers went with the trim |
| #12: QA voice didn't match the draft | `verify_voice.py` used ffmpeg's concat demuxer and rounded every piece to a packet: +5 to 30 s over 100+ pieces | The script now slices sample-exact (qa_voice = 650.936 s = the timeline) |
| #13: music | A hard stop at a bed change. A 6.7 s outro sliver | Only the no-go cue stops dead. Internal changes fade. The outro is one bed |
| #14: fast-forward speeds | 12x and 30x | The first wait is cut. The second runs at 40x |

Not changed: #8's draft one-frame source-duration differences. These are CapCut's frame snapping on open, and the target ranges match.

## Rules for taste.md

- A conditional approval or an unbuilt product is presented as "the plan, build underway". Never imply availability (Codex audit adopted).
- Narration's absolute claims ("no humans", "zero human help") get qualified by the real operating boundary in the cut itself (refines the confirmed narration-versus-screen rule).
- A status card lands when the status appears on screen, never ahead of it (Odin's recovery).
- Terminal reading sections use one static 1.5x frame per reading stretch. Never alternate framing on every cut.

# Round 2 (Coley's review of v2, 2026-10-07)

| Coley said | What was wrong in v2 | Fix in v3 |
|---|---|---|
| "The zoom at 1:40 cuts off some of the text from the Claude terminal... again at 3:00, 3:56, 4:31, 6:23. It may just be easier to remove the zoom feature" | The static 1.5x Claude-pane frame. At 1.5x (the minimum that keeps the recorded facecam off-frame) the view is narrower and shorter than the pane, so the left edge and the top and bottom lines were cut | All terminal punch-ins removed (`READ = []`). Terminals play full frame. The two Paperclip UI punch-ins (Odin's error toast, the PaperRows project) stay. With matching framing, the round-jump dissolves return (4) |

Rule (confirmed): terminals play full frame. Never crop text that's being read.

## Shorts round 1 (Codex audit, 2026-10-07)

All the must-fix items were applied: facecam above the UI line, caption tokenization and gold words, the reason for the green light in s1, s5's goal wording, s6's "got stuck" hook, and s2's closing claim. Most should-fix items were applied too: interface narration and restated rules trimmed, cards clear at scene changes, impacts on the spoken verdict, a bigger "prior project" label on the cost card, and captions kept off the right rail. The audit is in `shorts/AUDIT - Codex (Shorts).md`.
