# D11 — Technical Spec

## CLI
```
python3 seed_variance.py --logs <glob_or_paths...> [--last-k 5] [--collapse-thresh 0.03]
                         [--seed-group LABEL]  [--out-json report.json] [--out-md table.md]
```
- `--logs`: one or more jsonl run logs (each line a step record). Globs expanded.
- `--seed-group`: if set, ALL supplied logs are treated as seeds of ONE config →
  the across-seed CI section is computed. If unset, logs are treated as independent
  configs (per-run stats only; no seed CI; cross-config section emitted instead).
- `--last-k`: plateau window for detrended stability (default 5).
- `--collapse-thresh`: within-step reward_std below this flags GRPO advantage collapse.

## Input record schema (per line, real logs)
```json
{"step": int, "mean_reward": float, "n": int,
 "rewards": [float,...], "reward_std": float (optional), "loss": float|null}
```

## Data structures
```python
@dataclass
class RunStats:
    path: str
    n_steps: int
    group_n: int                 # rollouts per step (from "n")
    curve_mean: float            # mean of mean_reward over all steps
    curve_std: float             # std of mean_reward (whole-curve; inflated by trend)
    plateau_mean: float          # mean of last-k mean_reward (final perf estimate)
    plateau_std: float           # std of last-k mean_reward (detrended stability)
    within_step_spread_mean: float   # mean over steps of per-step reward std
    within_step_spread_min: float
    collapse_steps: list[int]    # steps where per-step std < collapse_thresh
    first_reward: float
    last_reward: float
    delta: float                 # last_reward - first_reward (did it learn?)

@dataclass
class SeedCI:               # only when --seed-group given and S>=2
    statistic: str         # "plateau_mean (last-k mean per seed)"
    n_seeds: int
    mean: float
    std: float             # sample std across seeds (ddof=1)
    sem: float
    t_mult: float          # Student-t, df=S-1, 95%
    ci_low: float
    ci_high: float
    per_seed: list[float]
```

## Functions
```python
def load_run(path) -> list[dict]                 # parse jsonl, skip blanks
def per_step_spread(rec) -> float                # rec["reward_std"] if present else pstdev(rec["rewards"])
def run_stats(path, recs, last_k, collapse_thresh) -> RunStats
def seed_ci(per_seed_finals: list[float]) -> SeedCI   # Student-t 95% CI
def t_multiplier(df: int) -> float               # 95% two-sided table, df 1..30 then z=1.96
def build_report(runs, seed_group, ...) -> dict
def render_md(report) -> str
```

## CI math
- per-seed final statistic = `plateau_mean` (mean of last-k `mean_reward`).
- `mean` = average across seeds; `std` = sample std (ddof=1); `sem = std / sqrt(S)`.
- `ci = mean ± t(0.975, df=S-1) * sem`.
- `t_multiplier`: hardcoded 95% two-sided t-table for df 1..30; for df>30 use 1.96.

## Output JSON (top-level)
```json
{
 "generated_utc": "...", "last_k": 5, "collapse_thresh": 0.03,
 "mode": "cross-config" | "seed-group",
 "runs": [ {RunStats...}, ... ],
 "seed_ci": {SeedCI...} | null,
 "cross_config": { "configs": [...], "mean_of_plateau_means": x,
                   "std_of_plateau_means": y, "caveat": "..." } | null,
 "notes": ["..."]
}
```

## Tests (`test_seed_variance.py`, pytest)
1. `test_per_step_spread_uses_logged_std`: rec with `reward_std` → returned verbatim.
2. `test_per_step_spread_recomputes`: rec without `reward_std` → pstdev(rewards).
3. `test_plateau_std_zero_for_flat`: flat curve → plateau_std == 0.
4. `test_collapse_flag`: a step with tiny spread is flagged.
5. `test_seed_ci_known`: 3 seeds [0.50,0.52,0.54] → mean 0.52, t(df=2)=4.303, CI matches hand calc.
6. `test_t_multiplier_large_df`: df=100 → 1.96.

## File formats
- `variance_report.json`: the JSON above (pretty, 2-space).
- `variance_table.md`: one row per run (steps, group_n, plateau_mean, plateau_std,
  within-step spread, delta, collapse count) + seed-CI / cross-config block.

## API contract / decoupling
- Analyzer imports stdlib only: `json, math, glob, argparse, statistics, datetime, dataclasses`.
- No import of HUD, the trainer, numpy, or any rex/sim/agent module. Runs offline.
