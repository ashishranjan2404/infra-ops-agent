# G5 — 09 Critique (honest)

## What a hostile reviewer attacks
1. **Self-defined dimensions.** Three of five dimensions (trap-action safety, training method, and
   the "what is graded" half of eval rigor) are ones we engineered to win. Even with two
   tie/lose rows included, a skeptic can argue the *frame* is ours. A truly neutral comparison
   would use dimensions a buyer chose (MTTR reduction, integration breadth, on-call coverage,
   cost) — on which we have nothing to show because we are not a product.
2. **No head-to-head data anywhere.** The matrix is a *posture* comparison. We never ran our
   policies on SREGym's 90 problems, nor SREGym/Komodor/Datadog agents on our cascades. Every
   "edge" is structural, not measured against the others. This is the deepest limitation and the
   matrix admits it, but admitting it doesn't make the comparison empirical.
3. **Trap-safety edge is sim-bound.** Our −0.60 trap penalty is real *in a deterministic sim and a
   controlled GKE cluster*. Komodor and Datadog take actual production risk under messy telemetry.
   Claiming a "safety" edge over systems that operate in prod is only fair because we reframed it
   as "we *grade* the trap," not "we are safer in prod." A careless reader could still misread it.
4. **Competitor info is shallow and vendor-sourced.** Komodor/Datadog cells lean on blogs and PRs;
   I could not access internal methodology. Their real diagnosis-vs-mitigation grading, their
   trap handling, and their training methods are unknown — "not disclosed" is doing a lot of work.
   Some "we're first / they don't publish" claims are arguments from absence of evidence.
5. **Validator proves form, not truth.** It enforces citation hygiene and the vendor-flag, nothing
   about whether a cited claim is correctly characterized. A wrong claim with a real citation
   passes.

## What's weak / missing
- No quantitative axis a procurement team uses (price, integrations, SLAs).
- SREGym's *specific stacks* and exact fault taxonomy weren't extracted (abstract-level only).
- Snapshot risk: vendor features move monthly; this is accurate as of 2026-06 and will rot.

## What's genuinely solid
- Every competitor number is real, dated, and cited; vendor marketing is quarantined and flagged.
- We openly lose deployment and tie open-benchmark — the matrix is not a rigged sweep.
- The one defensible, sourced, *first* claim (frozen policy → reward-shaped trajectories with a
  quantified trap penalty) stands up: none of the other three publicly emit that.

## Honest status
Completed and useful as a **positioning/strategy artifact**, explicitly NOT as an empirical
benchmark result. Its value is honesty and sourcing, not measured superiority.
