# G3 — SUMMARY

**Task:** Analyze SREGym's pass@1 leaderboard — where would we rank? Research SREGym's
published numbers (cited), write an honest positioning analysis using our real pass@1
(A1/A2), with explicit non-equivalence caveats. Deliver an analysis report + a small
ranking-table script. No shared core file edits.

## Answer
- **Fair single-attempt basis:** our best in-regime condition (retry_realistic /
  best_of_n, ~34.9%) lands at **rank 8 of 13** in the merged leaderboard — in the LOWER
  part of SREGym's E2E band (30.4%–60.7%), above only the two weakest Kimi-K2.5 Stratus
  rows and **below every frontier-model agent**. Bottom-of-board entry, not a leader.
- **REx (89.7%)** would nominally top the table but is **OUT-OF-REGIME** (multi-attempt +
  P0 oracle hint no SREGym agent gets). A1's ablation shows rex_no_oracle collapses to
  ~33%, so the oracle, not the tree, drives the lift. Rank-1 placement is a category error.
- Both benchmarks agree **novel failures are hardest** (SREGym E2E collapses ported->new;
  our zero-shot cascade pass@1 = 6.7%).

## Deliverables (all in experiments/ralph_outputs/G3/artifacts/)
- rank_leaderboard.py — stdlib ranking script; reads cited SREGym + live A1/A2 pass@1,
  emits one descending ranked table with regime tags. --selftest passes (6 asserts), rc=0.
- sregym_reported.json — cited frozen SREGym leaderboard (arXiv:2605.07161v1 +
  sregym.com/leaderboard, retrieved 2026-06-25).
- ranked_leaderboard.md — generated 13-row ranked table + positioning.
- positioning_report.md — primary analysis: cited numbers, merged ranking, honest
  bottom-of-board conclusion, 11 numbered non-equivalence caveats.

## Status
completed. No shared core files edited (all outputs under G3/). One blocked item
(matched-model / matched-substrate head-to-head) documented in 09 — needs SREGym infra +
API budget, not faked.

## Distinct from B15
B15 built a no-ranking comparison table; G3 produces the explicit ordinal ranked
leaderboard and the "rank 8/13" answer, reusing B15's cited inputs but reading A1/A2 live
with a fallback so it stands alone.
