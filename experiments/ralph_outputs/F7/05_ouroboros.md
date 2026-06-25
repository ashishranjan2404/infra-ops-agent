# F7 — 05 Ouroboros: 3 self-critiques of the spec

## Engineer 1 — "the labels are too rigid / will fail on real prose"
**Problem found:** The spec requires verbatim labeled lines (`**Steelman.**` etc.). If the doc
author writes `**Steelman:**` (colon) or `**Steelman** —`, the validator's substring check
fails on a *cosmetic* difference, flagging a healthy doc as broken. That's a brittle test that
will produce false negatives.
**Fix:** Validator matches each label by a tolerant regex `r"\*\*Steelman\*\*"` ignoring the
trailing punctuation, case-insensitive. Document the exact accepted forms.

## Engineer 2 — "the doc could pass structurally while being vacuous"
**Problem found:** check_doc only verifies *presence* of labels, not that the steelman is
actually adversarial. A doc with `**Steelman.** N/A` passes. The whole value of the task is that
attacks are *strong*; the test doesn't guard substance at all.
**Fix:** Add a minimal substance gate: each `**Steelman.**` and `**Honest response.**` body must
be ≥ 120 characters before the next label (cheap proxy for "actually written"). Not a semantic
check, but kills the empty-shell failure mode. Also require A6's block to literally contain the
string `(4` and `0.30` (forces the fixed-point arithmetic to be present, not hand-waved).

## Engineer 3 — "theme coverage check is satisfiable trivially / mismatched between files"
**Problem found:** attacks.json themes and the markdown can drift — JSON could claim theme
`flat_rft` on A4 while the A4 prose says nothing about training. Also: nothing checks that the
two top-line callouts (highest-probability, highest-depth) actually exist, which the grill
identified as the single most important structural decision.
**Fix:** (1) Add check that the Top-line section mentions both "probability" and "depth" callouts
(regex for `highest[- ]probability` and `highest[- ]depth`, case-insensitive). (2) Accept that
JSON↔prose semantic alignment can't be auto-verified cheaply; instead require each attack's
`theme` to appear as a word somewhere in its markdown block (lightweight cross-file consistency).

## Final filtered spec (deltas applied)
- Label matching: tolerant regex, case-insensitive, punctuation-agnostic. ✅
- Substance gate: steelman + honest-response bodies ≥ 120 chars; A6 must contain `(4` and `0.30`. ✅
- Top-line callouts: must contain both "highest-probability" and "highest-depth" markers. ✅
- Cross-file: each attack's `theme` token must appear in its markdown block. ✅
- Kept: 8–12 attacks, all 5 mandatory themes, four required H2 sections, one H3 per id.
- Rejected as over-engineering: full NLP "is this actually adversarial" scoring — out of scope
  for a stdlib validator; the 120-char + arithmetic gates are the pragmatic floor.
