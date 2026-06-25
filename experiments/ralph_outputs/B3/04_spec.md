# B3 — 04 Technical Spec

## Constants
- `Z95 = 1.959963984540054` — exact two-sided 95% standard-normal quantile.

## Core function
```python
def wilson_ci(passes: int, n: int, z: float = Z95) -> tuple[float, float]:
    """Wilson score interval for `passes`/`n` Bernoulli successes.
    Returns (lo, hi) clamped to [0,1]. n==0 -> (0.0, 1.0). Raises ValueError
    unless 0 <= passes <= n."""
```
Closed form (p = passes/n, z2 = z²):
```
denom  = 1 + z2/n
center = (p + z2/(2n)) / denom
half   = (z/denom) * sqrt( p(1-p)/n + z2/(4 n²) )
return (max(0, center-half), min(1, center+half))
```

## Helpers
```python
def point_estimate(passes, n) -> float            # passes/n, 0.0 if n==0
def iter_cells(doc: dict) -> Iterator[dict]        # parse A1/A2 schema
def format_table(rows: list[dict]) -> str
def discover_inputs() -> list[str]                 # A1/A2 default paths
def build_rows(paths) -> list[dict]
def main(argv) -> int
```

## Input schema (A1/A2 pass@k JSON)
```
{ "model": str, "label": str, "threshold": 0.8, "seeds": int,
  "by_condition": {
     <cond>: {
        "overall":  {"n": int, "passes": int, "pass@1": float, "ci95": [lo,hi], ...},
        "by_family": { <fam>: {"n": int, "passes": int, "pass@1": float, "ci95": [lo,hi], ...} }
     } } }
```
Conditions seen: `zero_shot, best_of_n, retry_realistic, rex, rex_no_oracle`.
Families: `simple, cascade, novel`. Scopes emitted: `overall` + each family.

## Row record (one per pass@1 cell)
```python
{ "condition": "<label> / <cond>", "scope": "overall|simple|cascade|novel",
  "n": int, "passes": int, "pass@1": float,
  "wilson_lo": float, "wilson_hi": float, "half_width": float,
  "stored_ci95": [lo,hi] | None }   # upstream value, for cross-check
```

## Output JSON (`wilson_table.json`)
```json
{ "z": 1.959963984540054, "inputs": ["...A1...", "...A2..."], "rows": [ <row>, ... ] }
```

## CLI contract
```
python3 wilson_ci.py [inputs...] [--json OUT]
  inputs   : zero or more pass@k JSON paths; default = discover A1/A2
  --json   : also write rows to OUT
  exit 0   : table printed; exit 2: no inputs found
```

## Test cases (test_wilson_ci.py)
1. `test_matches_independent_reference` — vs a separately-written closed form, 9 (c,n).
2. `test_known_value_p_half` — 50/100 → [0.4038, 0.5962] (±1e-3).
3. `test_known_value_zero_successes` — 0/10 → [0, 0.2775].
4. `test_known_value_all_successes` — 10/10 → [0.7225, 1].
5. `test_symmetry` — CI(c,n) mirrors CI(n-c,n) about 0.5.
6. `test_bounds_inside_unit_interval` — all c in 0..30 give 0 ≤ lo ≤ hi ≤ 1.
7. `test_contains_point_estimate` — lo ≤ p ≤ hi.
8. `test_width_shrinks_with_n` — 5/10 wider than 50/100.
9. `test_n_zero_is_full_interval` — (0,0) → (0,1).
10. `test_bad_inputs_raise` — (-1,10),(11,10),(5,-1) raise ValueError.
11. `test_iter_cells_parses_schema` — synthetic doc → 2 rows, recomputed ≈ stored.

## Known-value provenance
50/100 and 0/10 Wilson bounds are standard published values (e.g. Newcombe 1998;
Wikipedia "Binomial proportion confidence interval" worked example), independent of
this codebase.

## Documented limitation
Intervals model **binomial sampling error** over the pooled cell. Draws share incidents
across seeds, so they are not strictly iid; the true interval is somewhat **wider**.
Reported as anticonservative-w.r.t.-seed-correlation in 09_critique.
