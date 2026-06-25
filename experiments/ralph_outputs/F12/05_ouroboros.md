# F12 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer A — "Diligence Skeptic"
Problems found:
- A1: "0.23 → 0.90" with no model named in the body reads like cherry-picking. A diligence
  partner will ask "on what, with what grader?" The body must name "two different models" and
  "graded by code, not a model judging itself" or the stat is dismissible.
- A2: The market section risks a fabricated TAM. If I see a precise "$X B market" with no
  source, I distrust the whole memo. Every market number must be visibly an estimate.
- A3: "Code-as-policy" and "graduation" are insider terms. If they appear unexplained, the
  non-academic reader bounces. Must be defined on first use in one plain clause.

## Engineer B — "Operator / Buyer"
Problems found:
- B1: The memo doesn't say what I *buy* or *run*. Is it an API? A report? A dataset? The
  wedge sentence must be concrete: "a benchmark + a data feed," not "a platform."
- B2: "Autonomous responder" anywhere near the v1 ask will scare a buyer who's been burned by
  auto-remediation. It must be explicitly future/expansion, gated on trust.
- B3: The honest negative (rex_no_oracle ≈ baseline) — if I read it wrong it sounds like "the
  product doesn't work without a cheat." It must be framed as "we know the lift is the
  feedback content, and that feedback is the product," not as a disclaimer of failure.

## Engineer C — "Editor / Word-count Cop"
Problems found:
- C1: Risk of bloat past 1,400 words → not a 2-pager. Every section needs a hard trim;
  cut adjectives, no "revolutionary/cutting-edge."
- C2: The footnote must actually carry the rigor so the body can stay clean — if I move
  numbers to the footnote but also leave them in the body, it's redundant. Footnote = the
  ONLY place for n/seeds/p-value.
- C3: The ask is usually the weakest part of a 2-pager. It needs a concrete milestone the
  raise buys, or it's just "give us money."

## Filtered spec (after applying A/B/C)
- Body names "two models" + "graded by code" next to the headline stat. (A1)
- Market figures explicitly labeled "(estimate)". (A2)
- "Code-as-policy / graduation" defined in one plain clause on first use. (A3)
- Wedge is concrete: "a benchmark + a graded training-data feed." (B1)
- Autonomous response is explicitly the expansion, trust-gated. (B2)
- Honest negative framed as "the feedback content IS the product." (B3)
- Hard 1,400-word ceiling; no hype adjectives. (C1)
- Rigor only in the footnote, not duplicated in body. (C2)
- Ask names a concrete 12-month milestone. (C3)

These 9 filters are folded into the deliverable in step 06.
