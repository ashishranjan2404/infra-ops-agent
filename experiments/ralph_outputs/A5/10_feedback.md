# 10_feedback — learnings for the next task

Outreach tasks have a hard honesty ceiling: you can produce a genuinely complete, validated
*package* (briefs, tailored drafts, a citable anonymization contract, a tracking sheet, a
validator) but you cannot truthfully claim contact or data acquisition without real channels and
authority — so define success as "review-ready package + citable permission position," not
"data in hand," and gate sending behind an explicit DO_NOT_SEND banner. The single biggest force
multiplier was the *warm hook*: every target already has public postmortems we model in
`scenarios/cidg/generated/`, so verifying those file citations exist (cheap `test -f` loop) made
the asks credible instead of cold. Reusable pattern for sibling tasks: (1) lead with the asset
we already have, (2) ask for the least-sensitive useful slice plus a tiny low-commitment CTA,
(3) make every contact role-based + `[VERIFY]` and never invent personal emails, (4) ship a
stdlib-only validator so the package is provably well-formed, and (5) write down realistic
yield + fallback so nobody later mistakes drafted-not-sent for success.
