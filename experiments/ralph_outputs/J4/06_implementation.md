# J4 — 06 Implementation

## Artifacts built (all under experiments/ralph_outputs/J4/artifacts/)
- **`mttr_analysis.py`** (~400 LOC) — the analysis harness.
  - `Trial` dataclass + `validate()`; `load_trials()` for CSV/JSON (skips null MTTR).
  - `analyze(trials, design, slo, n_boot, seed)` → `Result` JSON report.
    - within: join on `pair_id`, paired t-test (scipy) + Wilcoxon + paired bootstrap.
    - between: Welch t-test + Mann-Whitney + two-sample bootstrap.
    - log-space throughout; primary endpoint speedup = GM(control)/GM(agent).
    - secondary: median per arm, %-within-SLO, Cliff's delta, % reduction.
    - scipy **optional** → permutation p-value fallback (sign-flip / label-shuffle).
  - `required_n_paired()` power/sample-size planner.
  - `_self_test()` — 12 hermetic assertions; `--self-test` exits 0/1.
  - CLI: `--trials --design --slo --n-boot --seed --out --self-test`.
- **`simulate_trials.py`** (~150 LOC) — synthetic trial generator.
  - Baselines seeded from **A9 `mttr_labels.json`** real incidents (lognormal-fit
    fallback if absent). Agent arm applies `true_speedup` with operator random
    effects + per-trial noise + a `no_benefit_frac` of incidents that get ~no help.
  - Emits paired rows (`within`) or randomized single-arm rows (`between`).
- **Generated data + reports** (committed as real outputs):
  - `trials_within.csv` (100 rows / 50 pairs), `report_within.json`.
  - `trials_between.csv` (120 rows), `report_between.json`.
  - `trials_null.csv` + null-case check.

## How it's wired to existing assets
- **Reuses A9** (`mttr_labels.json`) read-only as the grounded baseline MTTR
  distribution — satisfies the brief's "reuse A9 mttr_labels as baseline."
- Touches **no shared core files** (`rex/*`, `sim/*`, `agent/*`, `experiments/*.py`).
  Pure stdlib + numpy/scipy; no network.

## Run recipe
```
cd experiments/ralph_outputs/J4/artifacts
python3 mttr_analysis.py --self-test
python3 simulate_trials.py --n 50 --design within  --true-speedup 1.8 --seed 42 --out trials_within.csv
python3 mttr_analysis.py --trials trials_within.csv  --design within  --slo 120 --out report_within.json
python3 simulate_trials.py --n 120 --design between --true-speedup 1.8 --seed 7  --out trials_between.csv
python3 mttr_analysis.py --trials trials_between.csv --design between --slo 120 --out report_between.json
```

## Known gaps (carried to 09, not hidden)
- `resolved=False` rows are captured but not yet excluded by `analyze`.
- Percentile bootstrap (not BCa). Single global `--slo` (no per-severity).
