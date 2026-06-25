# B3 — 03 Improved Plan

## What changed from 01 (driven by the grill)

| # | Change | From | Accepted? |
|---|--------|------|-----------|
| 1 | Use exact z = 1.959963984540054, not 1.96 | PSRE/DOL | ACCEPTED — `Z95` constant; cheap correctness, avoids scipy-diff bug reports |
| 2 | Cross-check every recomputed CI vs upstream stored `ci95` (≤ 0.01) | RLE | ACCEPTED — adds a `match?` column; turns the run into an independent reproduction of the published numbers |
| 3 | Report `n` per cell in the table | PSRE/RLE | ACCEPTED — n column present; arithmetic auditable (36+60+30=126; 50+50+50=150) |
| 4 | Accept explicit argv paths, not only hardcoded discovery | DOL | ACCEPTED — `inputs` positional args; falls back to discovery |
| 5 | Document binomial-iid limitation (seed correlation → anticonservative) | REV/SMR | ACCEPTED — stated in spec/critique; NOT silently dropped |
| 6 | Pin known textbook values in tests | SMR | ACCEPTED — 50/100, 0/10, 10/10, symmetry, monotone width |

## Critiques REJECTED and why

- **REV: "switch to a cluster-robust / correlation-aware interval."** REJECTED for the
  deliverable. The A1/A2 summary JSONs expose per-cell aggregate `(n, passes)` and
  per-incident reward arrays, but not a clean per-(incident,seed) binary matrix for
  *every* cell in a uniform shape. A cluster-robust interval would require reconstructing
  that matrix and is out of scope for "compute Wilson CIs for the pass@k numbers." I
  instead **document** the limitation honestly (per REV's fallback ask). The honest move
  is the binomial Wilson interval + a stated caveat, not a half-correct cluster estimate.

- **DOL: "fully generic plugin loader."** REJECTED as over-engineering. argv + a small
  hardcoded discovery list covers A1/A2 today and any future file passed explicitly. No
  registry/config needed.

## Final shape
`wilson_ci.py`: `wilson_ci()`, `point_estimate()`, `iter_cells()` (schema parser),
`format_table()`, `discover_inputs()`, `main()`. stdlib only.
`test_wilson_ci.py`: 11 tests, pytest-compatible + no-pytest fallback runner.
Outputs: stdout table, `wilson_table.json`, `run.log`.

## Success criteria (unchanged + tightened)
- Table prints point estimate + Wilson 95% CI + n per condition/family cell.
- All unit tests pass against known formula values.
- 100% of recomputed CIs match upstream stored `ci95` within 0.01.
