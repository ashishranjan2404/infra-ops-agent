# B9 — 04 Spec

## Inputs
- `rex/runs/ablation.json` keys used: `model`, `incidents` (list of 5),
  `per_incident[cond][incident]` → list of 3 float rewards.
- Conditions: `zero_shot, best_of_n, retry_realistic, rex, rex_no_oracle`.
- Constants: `THRESHOLD = 0.8`.

## Data structures
- `by_incident: dict[str, list[int]]` — incident → 0/1 outcomes (len 3, the seeds).
- `flat: list[int]` — all 15 episode outcomes for a condition.

## Function signatures
```python
def percentile(sorted_vals: list[float], q: float) -> float
    # linear-interpolation percentile, q in [0,1], input pre-sorted.

def bootstrap_ci(flat_passes: list[int], resamples: int, rng: random.Random,
                 alpha: float = 0.05) -> tuple[lo, hi, point, n, se]
    # i.i.d. percentile bootstrap over episode outcomes.

def cluster_bootstrap_ci(by_incident: dict[str, list[int]], resamples: int,
                         rng: random.Random, alpha: float = 0.05)
                         -> tuple[lo, hi, point, n_blocks, se]
    # block bootstrap: resample whole incidents (n_blocks held fixed).

def main() -> dict   # CLI: --resamples --seed --threshold --data --out
```

## CLI contract
`python3 bootstrap_ci.py --resamples 10000 --seed 12345 --out <path>`
- Exit 0 on success; writes `<out>` JSON and prints a table.
- Deterministic: identical `--seed` ⇒ identical intervals.

## Output JSON schema (bootstrap_ci_results.json)
```json
{
  "source_data": "rex/runs/ablation.json",
  "model": "<str>", "threshold": 0.8, "resamples": 10000, "rng_seed": 12345,
  "reference_estimator_source": "imported|fallback",
  "n_incidents": 5, "metric": "pass@1 (P[reward>=threshold])",
  "conditions": {
    "<cond>": {
      "n": 15, "passes": <int>, "pass@1": <float>,
      "wilson95": [lo,hi], "bootstrap95": [lo,hi], "bootstrap_se": <float>,
      "cluster_bootstrap95": [lo,hi], "cluster_bootstrap_se": <float>,
      "n_blocks": 5,
      "wilson_width": <float>, "bootstrap_width": <float>,
      "cluster_bootstrap_width": <float>
    }, ...
  }
}
```

## Test cases (test_bootstrap_ci.py)
1. `percentile` median / lo-clamp / hi-clamp.
2. All-pass `[1,1,1,1]` → degenerate CI `[1,1]`, SE 0.
3. All-fail `[0,0,0]` → degenerate CI `[0,0]`.
4. 50/50 sample → point 0.5, CI brackets 0.5, SE ≈ √(pq/n).
5. Determinism: same seed ⇒ identical CI tuple.
6. On clustered all-or-nothing data, cluster width ≥ i.i.d. width.
7. Reused `wilson_ci` matches the hand formula.
