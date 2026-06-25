# 04 — Technical Spec

## Module: `artifacts/effect_size.py` (stdlib only)

### Pure functions
```python
cohens_h(p1: float, p2: float) -> float
    # h = 2*asin(sqrt(p1)) - 2*asin(sqrt(p2)); signed (treat - base).
    # Raises ValueError if p not in [0,1].

pooled_sd(s1: float, n1: int, s2: float, n2: int) -> float
    # sqrt( ((n1-1)*s1^2 + (n2-1)*s2^2) / (n1+n2-2) )
    # Raises ValueError if n<1 or n1+n2<=2.

cohens_d(m1, s1, n1, m2, s2, n2) -> float
    # (m1 - m2) / pooled_sd; signed; returns 0.0 if sp==0 and m1==m2 else inf.

magnitude(es: float) -> str
    # |es|: <0.2 negligible, <0.5 small, <0.8 medium, else large. (Cohen thresholds.)
```

### Ingestion
```python
effect_sizes_for_file(data: dict, baseline="zero_shot") -> dict
```
Reads `data["by_condition"][cond]["overall"]` with keys
`n:int, passes:int, mean_reward:float, reward_std:float`.
For each non-baseline condition emits:
```json
{"condition","baseline",
 "pass1_treat","pass1_base","pass1_diff","cohens_h","h_magnitude",
 "reward_treat","reward_base","reward_diff","cohens_d","d_magnitude",
 "n_treat","n_base"}
```
`pass@1` proportion is recomputed as `passes/n` (independent of any stored rounding).

### CLI
```
effect_size.py FILE.json [FILE...] [--baseline zero_shot] [--json] [--selftest]
```
- default: pretty table per file.
- `--json`: list of per-file result dicts.
- `--selftest`: known-value assertions, exit 0/1.

## Input file contract (real, verified)
`rex/eval_pass_at_k.py` output → `by_condition` keys:
`zero_shot, best_of_n, retry_realistic, rex, rex_no_oracle`; each `.overall` has
`n, passes, pass@1, ci95, pass@2, pass@5, mean_reward, reward_std`.

## Test cases (known values)
| call | expected |
|---|---|
| `cohens_h(0.5,0.25)` | `pi/6 = 0.523599` |
| `cohens_h(1,0)` | `pi` |
| `cohens_h(0.25,0.5)` | `-pi/6` |
| `cohens_d(7,2,2,5,2,2)` | `1.0` |
| `cohens_d(0.5,1,50,0,1,50)` | `0.5` |
| `pooled_sd(3,5,5,5)` | `sqrt(17)=4.12311` |
| `magnitude(0.2)` | `"small"`; `magnitude(0.8)` `"large"` |
