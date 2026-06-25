# B3 — 01 Plan

## Objective
Compute **Wilson 95% confidence intervals** for every pass@k point estimate in the
project's pass@k result JSONs (the A1 full-42 sweep and the A2 ablation sweep), and
emit a table of `point estimate + Wilson interval` per condition. Validate the math
against a known textbook formula with a real unit test. Do not touch shared core files.

## Why Wilson (not Wald)
The normal-approximation (Wald) interval `p ± z·sqrt(p(1-p)/n)` is degenerate exactly
where these tables live: it has width 0 at p=0 and p=1 (and several cells here are at
p=0.02, p=0.0, p=1.0), and it under-covers for small n (n as low as 30 per family).
The Wilson score interval stays inside [0,1], is non-degenerate at the boundary, and
has near-nominal coverage for small n (Brown, Cai & DasGupta, 2001). It is also exactly
what the upstream `experiments/compute_pass_at_k.py` already claims to use — so a clean
re-implementation gives us a free cross-check.

## Approach
1. Write a self-contained `artifacts/wilson_ci.py`:
   - `wilson_ci(passes, n, z)` from first principles (testable closed form).
   - A parser for the A1/A2 schema (`by_condition.<cond>.overall` + `.by_family.<fam>`,
     each carrying `n`, `passes`, and an upstream `ci95`).
   - A flat table printer (point estimate, Wilson [lo,hi], half-width, match-vs-stored).
2. Write `artifacts/test_wilson_ci.py` validating against KNOWN values:
   - 50/100 → [0.4038, 0.5962]; 0/10 → [0, 0.2775]; 10/10 → [0.7225, 1]; symmetry;
     monotone width; bounds in [0,1]; contains point estimate; n=0 edge; bad-input raises.
3. Run the tool on the discovered A1/A2 JSONs; assert each recomputed CI matches the
   upstream stored `ci95` within 0.01 (independent reproduction).

## Files to create (all task-namespaced)
- `experiments/ralph_outputs/B3/artifacts/wilson_ci.py`
- `experiments/ralph_outputs/B3/artifacts/test_wilson_ci.py`
- `experiments/ralph_outputs/B3/artifacts/wilson_table.json` (machine-readable output)
- `experiments/ralph_outputs/B3/artifacts/run.log`
- 10 step files + SUMMARY.md + result.json

## Files to modify
None. The shared `experiments/compute_pass_at_k.py` already has a `wilson_ci`; I will
NOT edit it — I re-derive independently and cross-check against its stored outputs.

## Dependencies
Python 3.13 stdlib only (`math`, `json`, `argparse`). pytest if present, else a
built-in fallback runner. No network, no LLM, no cluster.

## Risks
- **Input drift**: A1/A2 schema could differ → handle missing keys defensively, skip
  unparseable files with a warning.
- **z constant**: 1.96 vs exact 1.959963984540054 → use the exact quantile; document.
- **p=0 / p=1 cells**: must not blow up → clamp to [0,1], assert in tests.

## Success criteria
- Tool runs and prints a per-condition table with point estimate + Wilson 95% CI.
- Unit test passes against known formula values.
- Every recomputed CI matches the upstream stored `ci95` within 0.01 (cross-validation).
