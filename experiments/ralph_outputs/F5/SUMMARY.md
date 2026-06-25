# F5 — SUMMARY: Tighten the Abstract (<=250 words, AAAI)

## Deliverable
`experiments/ralph_outputs/F5/artifacts/abstract.md` — a tightened, AAAI-ready abstract,
**233 words** (<=250 gate), grounded in real results.

## What it does
Replaces the loose ~230-word draft in `PAPER_OUTLINE.md` Abstract with a version that
reflects the honest, measured contributions:
- Hook: MTTR/cascades; the naive fix worsens the outage; LLMs emit trap actions.
- Method: three composable components — synthesized code-as-policy harness
  (Thompson-search over rules-as-data), the REx propose->simulate->score loop, and a
  deterministic verifiable reward (no LLM judge, credit-free).
- Honest results, all repo-grounded:
  - Verifier generalizes: ~0.90 vs 0.95 hand-written on held-out, 14->3 rules, one
    miss = an unseen hazard (harness_synth.json: 7 train / 3 heldout / 3 rules).
  - REx lift 0.69 vs 0.24 zero-shot, but collapses to 0.25 with the oracle hint
    stripped — an explicit generalization boundary (ablation.json aggregate, verified).
- Released artifacts: harness, simulator, 42-incident benchmark, deterministic reward.

## Honesty choices (vs the optimistic draft)
- Dropped false-precision verifier accuracy (89.7/94.9 on n=3).
- Re-centered the contribution on the verifiable env + learned verifier.
- Omitted unrun C2 FIREBALL transfer and not-yet-locked McNemar significance (documented).

## Validation
Word gate 233 <= 250 (wc -w); checklist T1-T7 + forbidden-claims scan all PASS; ablation
arms and harness-synth structure re-derived from JSON (see 07_test_results.md).

## Scope safety
No shared-core files edited. PAPER_OUTLINE.md read-only. All outputs under F5/.

## Honest gaps (see 09)
Single-model 5-incident ablation; verifier accuracy taken on headline_insights.md
authority (structure re-verified, value not recomputed); abstract currently reads as a
two-contribution paper until C2 transfer lands.

## Files
01_plan, 02_grill, 03_improved_plan, 04_spec, 05_ouroboros, 06_implementation,
07_test_results, 08_verification, 09_critique, 10_feedback, artifacts/abstract.md
