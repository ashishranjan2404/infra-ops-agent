# G7 — 05 Ouroboros (3 self-critiques in sequence)

## Engineer A — "the data-integrity reviewer"
**Problems found:**
- A1. The spec lets a claim be cited to a single vendor blog. Funding/valuation should corroborate
  with ≥1 independent outlet (TechCrunch/Bloomberg/PYMNTS), or it's an echo of the press release.
- A2. "As-of date" is set but nothing forces individual claims to carry their *own* publication date;
  a 2024 fact and a 2026 fact look identical.
- A3. The Sources list could drift from inline references (dead anchors). Need a dedup + presence check.
**Fixes:** require dual-sourcing for funding/valuation; date-stamp the major launch claims inline
(Series A = Feb 2026; platform expansion = May 21 2026); keep Sources as a flat deduped list.

## Engineer B — "the over/under-engineering reviewer"
**Problems found:**
- B1. A live poller was tempting but is over-engineering for a one-shot task; good that the improved
  plan dropped it — confirm the YAML is *poll-ready* (machine-parseable `where` URLs) without us
  actually running a cron. ✔ already in schema.
- B2. The validator is under-specified on failure mode: if it just `assert`s, the error is opaque.
  Make failures print which item/key failed so re-runs are debuggable.
- B3. `why_it_matters` risks being filler. Each must tie to a *decision* (e.g., "if they ship X, our
  differentiation Y weakens"), not generic "good to know."
**Fixes:** validator emits the offending `id`/key on failure; tighten `why_it_matters` to decision-linked.

## Engineer C — "the honesty / scope reviewer"
**Problems found:**
- C1. Risk of the "relevance to REx" section overclaiming a head-to-head when we have no benchmark
  parity. Must stay explicitly qualitative and note we have NOT benchmarked against them.
- C2. The "NOT publicly knowable" list must be concrete (pricing tiers, true accuracy methodology,
  model/provider stack, retention/churn, headcount specifics) — not a hand-wave.
- C3. Customer metrics: "72% Coinbase" and "87% DoorDash" must each be attributed to the *specific*
  source and labeled vendor-reported, never blended into one number.
**Fixes:** add explicit "not benchmarked" disclaimer; enumerate concrete unknowables; keep the two
metrics separate with distinct attributions.

## Final filtered spec (delta vs. 04)
- Funding/valuation dual-sourced (vendor + independent outlet). [A1]
- Major launch claims carry inline dates. [A2]
- Validator prints offending id/key on failure. [B2]
- `why_it_matters` is decision-linked. [B3]
- REx-relevance section flagged "qualitative, not benchmarked." [C1]
- `not_publicly_knowable` enumerated concretely. [C2]
- Customer metrics kept separate, each attributed + vendor-tagged. [C3]
