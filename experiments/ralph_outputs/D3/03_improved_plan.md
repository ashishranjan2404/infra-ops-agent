# D3 — 03 Improved Plan (post-grill)

## What changed vs 01

### Accepted critiques
1. **(RLE) Don't claim to fix the flat baseline.** HUD's internal group semantics are not
   confirmed to mix scenarios (the v2 docstring says "(likely)"). → Reframe the deliverable as
   an **invariant enforcer**: the per-scenario loop *guarantees* same-scenario groups whether or
   not HUD already does so. If HUD already groups per-task, our loop is a zero-downside explicit
   no-op. Claim: "guarantees the same-scenario invariant + removes between-scenario advantage
   variance," not "rescues the run."
2. **(REV + DVO) Ground the demo in real reward stats.** Use mean ≈ 0.5, within-scenario
   std ≈ 0.17 (the spread the v2 baseline actually logged) and a realistic difficulty spread
   across scenarios, not invented numbers.
3. **(REV) Make "variance reduction" falsifiable.** Report the policy-gradient variance proxy
   `E[A^2]` under mixed vs same baselining, plus the law-of-total-variance decomposition
   (`between_scenario_var`, `within_scenario_var`) that must add up. Also report the **advantage
   sign-flip rate** — the share of rollouts whose gradient pointed the WRONG way under mixing.
4. **(SRE) Surface degenerate groups.** `ScenarioGroup.is_degenerate` flags zero-spread groups;
   docstrings state plainly that same-scenario grouping is necessary-not-sufficient and does not
   cure a flat scenario (that's the orthogonal graded-reward fix).

### Rejected (with reason)
- **Full ablation isolating this fix end-to-end (REV).** Rejected for THIS task: an end-to-end
  GRPO ablation needs the live Tinker trainer + ~30 min + a forked slug — over the 15-min cap and
  infra-gated. We deliver the isolated *mechanism* demo + runnable driver instead and document the
  live blocker. The ablation is a follow-up, not a D3 deliverable.
- **Larger group size to stabilize the baseline (SRE).** Rejected as out of scope: group size is a
  hyperparameter orthogonal to the grouping *invariant*. We keep G configurable (default 6, matching
  v2) and note small-G baseline noise as a known limitation in 09.

## Final shape
- `same_scenario_groups.py` — partition + GRPO advantage + variance-reduction metric (+ degenerate flag).
- `train_rft_same_scenario.py` — additive v3 driver: one single-scenario Taskset per index, looped
  per step; logs per-scenario within-spread and the cross-scenario spread it deliberately removes.
- `test_same_scenario_groups.py` — math correctness, degenerate handling, sign-corruption test.
- `demo_variance_reduction.py` — grounded numeric demo → `demo_variance_reduction.json`.

## Success criteria (unchanged + sharpened)
- pytest green; demo reduction factor > 1 with decomposition summing correctly; driver `--help`
  works without HUD venv; explanation ties the removed term to gradient variance.
