# Corrections: Asgard Agents Day 30 (Codex audit, round 1, 2026-10-23)

Claude built v1 (15:10), Codex (Herdr, Editor tab, pane 2) audited it file-based (Coley was using the PC, so no CapCut playback and no listening), Claude reviewed the report and built v2 (15:04). CapCut stayed on the Spectre throughout. The audit is `Projects/Youtube/edits/2026-10-23 Recording 1040/AUDIT - Codex.md`.

| Codex said | v1 | v2 |
|---|---|---|
| #1 must: SFX hit offsets don't match the saved animation keys | pop 4 frames, glow 2, slide 3; a slide-out strip swap got the entrance offset | Read off ccut's keys: pop 5 frames (full size at 154 ms), glow 6 (settles at 200 ms), slide 7 (overshoot at 220 ms), a "_out" swap 0 |
| #2 must: absolute claims | "RUN BY THE AGENTS / after account setup"; "EVIDENCE, NOT ADVICE"; "REVIEWED WITHIN 24 HOURS / No one else sees it" | "AGENT-RUN, DAY TO DAY / After Coley's setup and early build work"; "AN EVIDENCE REPORT / To help you research a token"; "REVIEWED BY THE AGENTS / Within 24 hours. Your card is saved with Stripe". Narration kept (content rule; no pickups available) |
| #3 must: the stale-post narration contradicts the canvas | "a delay in the Asgard agents website... fixed" over a card saying two PaperRows posts were held | Line cut (confirmed Day 13 rule); "2 STALE POSTS HELD / Until new wording was approved" carries it |
| #4 must: Pump.fun feed and chat show explicit abuse and token spam | Visible 13:19-13:48 | Both columns covered by opaque blurred, darkened patches for the whole stretch; headers left visible |
| #5 must: the QA transcript and mix were stale | transcript from an earlier stitch | Voice re-stitched, literal transcript and mix regenerated from the final EDL (durations match) |
| #6: incoming transition margins | measured from Whisper word starts | Energy onsets checked: 0.32-0.49 s at X, Pump.fun, YouTube (fine); hook entrance 0.24 s widened to 0.38 s |
| #7: the privacy card headline | "STAYS IN YOUR BROWSER" | "YOUR PDF STAYS IN YOUR BROWSER" |
| #9: sponsor strip | step 4 never lit; "Approved" | "If approved"; step 4 "Live" lights on "you will get your response" |
| #10: suspension cause stated as fact | "For liking their own posts" | "Likely for liking their own posts" |
| #11: recap omits the opening question | "Live 24/7 · 13.17% locked · ..." | "$66 in checkouts · Not profitable yet · Live 24/7 · Back on X" |
| v2 QA (Claude) | "Uh, they did tell everyone"; the start of the "Uh" before "Stale post" | Both cut at energy dips |

Declined: #8 (X punch-ins break the full-frame rule: that rule covers landing and overview pages; on X the framing change is what keeps the scroll cuts from reading as skips, the Day 13 rule); #12 (leave the opening stack and the five Swipes until Coley has heard them). Music provenance: `audio/music-provenance.md` added, pointing at the series' original ElevenLabs prompts.
