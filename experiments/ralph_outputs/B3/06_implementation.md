# B3 — 06 Implementation

## Artifacts built (all under experiments/ralph_outputs/B3/artifacts/)

| File | Lines | Purpose |
|------|------:|---------|
| `wilson_ci.py` | ~165 | Wilson CI tool: core formula + A1/A2 schema parser + table/JSON emit |
| `test_wilson_ci.py` | ~140 | 11 unit tests; pytest-compatible + no-pytest fallback runner |
| `wilson_table.json` | generated | machine-readable rows (40 cells) |
| `run.log` | generated | captured stdout of the run |

## Key implementation points

- **`wilson_ci(passes, n, z=Z95)`** — closed-form Wilson score interval, derived in the
  module docstring. Uses exact `Z95 = 1.959963984540054`. Guards `n==0` → `(0.0, 1.0)`
  and validates `0 <= passes <= n` (raises `ValueError`). Result clamped to `[0,1]`.

- **`iter_cells(doc)`** — parses the A1/A2 pass@k schema. For each condition it yields an
  `overall` row plus one row per family (`simple/cascade/novel`). Each row recomputes the
  Wilson interval from the stored `(n, passes)` and carries the upstream `ci95` for a
  cross-check (the `match?` column).

- **`format_table(rows)`** — prints `condition | scope | n | pass@1 | Wilson 95% CI |
  half-width | match?`. The `match?` column shows `ok` when our recomputed interval is
  within 0.01 of the upstream stored CI, else `DIFF <delta>`.

- **CLI** — `python3 wilson_ci.py [inputs...] [--json OUT]`. With no args it
  auto-discovers the A1 (`full_pass_at_k_glm-5p2.json`) and A2
  (`ablation_pass_at_k_deepseek-v4-pro.json`) result files. Exit 2 if none found.

## Inputs consumed (NOT modified — read-only)
- `experiments/ralph_outputs/A1/artifacts/full_pass_at_k_glm-5p2.json`
- `experiments/ralph_outputs/A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json`

## Shared-core policy
No shared core file was edited. `experiments/compute_pass_at_k.py` already contains a
`wilson_ci`; I deliberately did **not** import or modify it. The B3 tool re-derives the
formula independently so it can be validated against known values, and uses the upstream
file only as a cross-check target. Parallel-safe: everything lives in the B3 dir.

## Run
```
cd experiments/ralph_outputs/B3/artifacts
python3 wilson_ci.py --json wilson_table.json    # 40 cells, all match upstream "ok"
python3 -m pytest test_wilson_ci.py -q           # 11 passed
```
