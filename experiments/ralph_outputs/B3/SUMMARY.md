# B3 — SUMMARY

**Task:** Compute Wilson 95% CIs for all pass@k numbers. Write a real `wilson_ci.py`,
run it on available pass@k result JSONs (A1/A2), emit a table of point estimate + Wilson
interval per condition, and validate against a known formula with a unit test. No
shared-core edits.

## Delivered
- **`artifacts/wilson_ci.py`** — self-contained Wilson score interval tool (stdlib only).
  Re-derives the closed form from first principles (exact z = 1.959963984540054), parses
  the A1/A2 pass@k schema, emits a per-condition table + machine-readable `wilson_table.json`.
- **`artifacts/test_wilson_ci.py`** — 11 unit tests validating against KNOWN textbook
  values (50/100->[0.4038,0.5962]; 0/10->[0,0.2775]; 10/10->[0.7225,1]), symmetry, monotone
  width, edge cases, and the schema parser. **11 passed.**
- **`artifacts/wilson_table.json`** + **`artifacts/run.log`** — 40 pass@1 cells (2 files ×
  5 conditions × {overall + simple/cascade/novel}) with point estimate + Wilson 95% CI.

## Key result
Ran on real A1 (`glm-5p2`, full-42) and A2 (`deepseek-v4-pro`) pass@k JSONs.
**40/40 recomputed Wilson intervals match the upstream stored `ci95` within 0.01** — an
independent reproduction of the published confidence intervals. Headline cells:
- glm-5p2 REx overall: pass@1 0.897, Wilson [0.832, 0.939]
- deepseek REx overall: pass@1 0.893, Wilson [0.834, 0.933]
- baseline (zero_shot) cascade: as low as pass@1 0.020, Wilson [0.004, 0.105]

## Honest caveats (see 09)
- Intervals model binomial sampling error; anticonservative under seed correlation
  (seeds reuse incidents). True intervals are somewhat wider.
- Scoped to pass@1 (a proportion). pass@2/@5 are the combinatorial estimator and need a
  bootstrap, not Wilson.

## Compliance
No shared core file edited. `experiments/compute_pass_at_k.py` left untouched and
re-derived independently. All artifacts under `experiments/ralph_outputs/B3/`.

**Status: completed.**
