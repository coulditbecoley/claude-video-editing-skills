# Corrections: C3 Research Demo (review round 1, 2026-10-01)

Coley reviewed v1 in CapCut without editing it. `diff_drafts.py` found only CapCut's frame snapping (up to 0.03 s), so he gave the changes in words.

| Coley said | What was wrong in v1 | Fix in v2 |
|---|---|---|
| "While reviewing the landing page, do not make so many cuts and also do not zoom in. I want to see the full landing page the entire time." | Two zooms (hero, Request Research button), a slow push, and 6 pause cuts while he scrolled (the page jumped at every one) | Landing plays full-frame: no zoom, no push. Pauses are cut only when over 1.2 s and while the page is still, leaving 4 cuts (2 stutters, 1 pause, the tap) |
| "After tapping the request research page, it should do the swoosh sound moving to the full screen of that page." | The Swipe and whoosh sat 1.4 s after the real tap, between two shots of the request page, and the page was then zoomed onto $19 | The piece is split on the tap frame (60.467). A Swipe and whoosh land there, and the full request page holds before the $19 zoom |
| "The base network logo needs to be fixed." | The Base tile was a solid blue block (Base's GitHub avatar), which read as a placeholder | Base's official mark (white "Square", from base/brand-kit) on Base blue, like the other tiles. The Solana label is aligned too |
| "During the wallet connection phase, there should be no zoom in so you can see the entire screen and that the wallet actually connected." | Zooms on the pay dropdown and the Phantom pop-up | 245-311 s is full-frame (no zoom, no push). "Connected" is visible |
| "Complete polish pass, mostly on transitions and timing ... versus the actual video." | Pause cuts landed mid-scroll everywhere (about 20 visual jumps in the report section). Transitions sat off the real page changes. The blank page after "Read report" showed. Chips landed before their pages | Pauses are cut only across the still part of the screen (frames.npz). Speech cuts that still jump get a 0.3 s Dissolve, 10 in all. Every page or tab change gets its transition on its own frame: tap, DexScreener, C3, Read report (blank cut), the library, X. The chips moved to after their page change. A whoosh plays into the 40x |

## Rules this adds to taste.md

- Landing or overview pages play full-frame: no zoom, no push, few cuts (confirmed, stated).
- Wallet connect and payment play full-frame, so the viewer sees it work (confirmed, stated).
- A transition and its whoosh land on the real screen change (the click or tab frame), never on a cut near it (confirmed, corrected).
- Never cut a pause while the screen is moving; cut only its still stretch (confirmed, corrected: "timing versus the actual video").
- A chain or logo tile must read as the brand at a glance. A bare brand-colour block reads as a placeholder (confirmed, corrected).

# Round 2 (Codex professional audit, 2026-10-01): `Projects/Youtube/edits/2026-10-01 Edit/AUDIT - Codex.md`

Coley: ignore "Free for admin" (it's his admin account). Then: "make your best recommended choices ... smooth and polished." Claude adopted:

- The 40x piece was unzoomed live. Fixed in ccut (keyframes in source time on sped-up segments).
- The facecam is fixed size, with punch-in zooms where the facecam is in the shot.
- The fast-forward eases to 15x for its last stage, so "Report ready" holds for about 2.9 s.
- The library and the whole exit are full-frame and static.
- Read report and the return to the library are hard cuts on the clicks: no dissolve ghosting, and the speech keeps its breath.
- Card copy matches the report: "Not enough evidence for a conclusive verdict", "What it couldn't verify", and "Findings come from the evidence" in place of the absolute "can't be talked into".
- Trims: "I'm going to get into it." (hook), the restated 7-day reasoning, and the repeated X pitch.
- The CA zoom is re-aimed at the copy row. The strips show labels only. The chapters were regenerated.

Not done, because each needs new narration or a structural re-edit: the report takeaway hold (#5), a hook payoff line (#6), a "previous request" label (#7), the bonding-curve warning before checkout (#9), and a real listening pass (#16).
