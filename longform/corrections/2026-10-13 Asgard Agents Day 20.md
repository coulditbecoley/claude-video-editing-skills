# Corrections: Asgard Agents Day 20 (Codex audit, round 1, 2026-10-13)

Coley's loop: Claude built v1 (8:26), Codex (Herdr, Editor tab, pane 2) audited it, and Claude built v2 (6:32). CapCut stayed on the Spectre monitor throughout (Coley's instruction). Coley gave no notes of his own this round. The audit is `Projects/Youtube/edits/2026-10-13 Recording 0949/AUDIT - Codex.md`.

| Codex said | v1 | v2 |
|---|---|---|
| #1 must: the privacy claim exceeds the page | "None of your data reaches any server" (card and narration), "it never reaches a server", "the agents do not see any of your information". The page's own table lists what reaches the server (Stripe payment, a file fingerprint, visit counts) | Those lines are cut. Cards say "Runs in your browser / Your statement is never uploaded" and "Stays on your computer / read in your browser, never uploaded", and sit clear of the page's browser/server table |
| #2 must: absolute guarantees | "Nothing goes out... misinformation or inaccurate", "THEY RUN IT ALL", "Usage limits and sign-ins. That's it." (the board shows a Coley Stripe-webhook task), "I will no longer have any interaction with it" | Cut the guarantee and the no-interaction promise. "BUILDING, MARKETING, SUPPORT / What the agents said they could handle". "WHERE COLEY STEPS IN / Setup, access, usage limits, sign-ins" |
| #3 must: QA voice didn't match the EDL | `qa_voice.wav` was stale (508.09 s against a 505.99 s EDL) after a late outro trim | Re-stitched after every change. Final qa_voice = 392.288 s = the EDL total |
| #4: bring proof forward, shorten the canvas | 20 s of setup before the first sale, an early social tour, the Thor section repeating the cold open, the arcade animation described before it's shown | Setup cut to one line, the social tour cut (the real buttons get a punch-in later), the main Thor section keeps only the signing-service detail, the arcade preview trimmed |
| #5: PaperRows tour | The general 0.4 s pause rule on a landing page (confirmed rule: only over 1.2 s), 40 s of series and premise re-explanation, two dissolves around "They built this" | Landing-page pause rule restored (`SITE`), the premise lines cut, "They built this" cut |
| #6: a 0.5 s 1.12x flash in the outro | Alternation on every piece, including a stutter-repair piece | A talking-head piece under 1.2 s keeps the previous framing. Outro trimmed to one follow ask, one site, the two products and the sign-off |
| #7: scope and tense | "Nobody else can move their money", "Their wallet. Their keys.", "Paid... once a day" (first payday is tomorrow), "HIRED AGENTS GET $ASGARD" (zero hires) | "THOR SIGNS EVERY PAYMENT / Checked against strict rules first", "NOT EVEN COLEY / He can't make them send tokens anywhere", "100 $ASGARD PER WORK MINUTE / Accruing now. First payout Oct 14", "THE PLAN: PAY HELP IN $ASGARD" |
| #8: transition handles | Paperclip exit tail 0.27 / head 0.15 | That exit is now a split inside his real 0.6 s pause (continuous audio). Pauses containing a screen switch are never collapsed. Whoosh lead 0.12 s to 0.06 s |
| #9: camera | One 1.6x payroll crop held ~40 s, speculative Loki line over sleeping agents | Payroll punch-in for the payroll sentence, wide for the hiring plan, punch-in again for the chart and wallets. Loki line cut |
| #10: graphics on evidence, real brand | Formats card covered the sample CSV. Generic document icon for PaperRows | Formats card moved to the empty right column. PaperRows mark from paperrows.com/favicon.svg |
| #11: sound | Staggered portraits with one pop | Portraits stagger 0.1 s as one entrance, one pop. Same pop/whoosh/impact files as Day 13 |
| #12: labels | "What's new in 7 days" against a Day 6 to Day 20 canvas, "Payday Oct 14" | "What's new since Day 13", "Payday tomorrow" |

Not changed: one-frame source-duration differences in the draft (CapCut snaps to frames on open; target ranges match). The cold-open tail (0.29 s) and the socials-to-Paperclip tail (0.27 s) are as long as his speech allows.

## Rules for taste.md

- Privacy and data claims follow the product page's own scope; a claim broader than the page is cut (refines the confirmed narration-versus-screen rule).
- Absolute autonomy or accuracy claims are cut; the human boundary is shown, including setup and access, not just "sign-ins".
- Landing-page pause rule (over 1.2 s) applies to every site section, by source range.
- A pause that contains a screen switch is never collapsed; the swipe lands inside it on continuous audio.
- Talking-head alternation skips pieces under 1.2 s.
- Scheduled things are carded in the future tense ("payout Oct 14", "the plan").

# Round 2 (Coley's review of v2, 2026-10-13)

| Coley said | What was wrong in v2 | Fix in v3 |
|---|---|---|
| "There are a lot of transitions that cut off valuable information... Only cut out pauses and ums and unimportant information" | v2 followed the Codex audit's trims (8:26 to 6:32): the roadmap, follow-along socials, the Thor/custody story, the arcade description, the hiring example, the PaperRows backstory and privacy explanation, pricing advice, C3 backstory, Discord and posting details, and the outro update plans were all cut. Nine repair dissolves smeared text across speech cuts | Every informative line restored (11:06). Cuts are only pauses, ums, stutters, restarts and true repeats (the second "first payday", "let me say that again", the Heimdall line that contradicts the canvas). All repair dissolves removed; 8 transitions remain, all on real scene changes inside pauses |
| "Find any way you can improve this video... improve it drastically" | | 22 gold highlight boxes on the exact card, panel or price he's talking about; a gold facecam frame; quieter whooshes on chapter chips; a mid-video subscribe nudge; new cards (hiring example, other converters' servers, $5 / $19 pricing, "Coley's idea, their code") |

Rule (confirmed): cut only pauses, ums and unimportant information. An audit's "too long" never outranks content.
