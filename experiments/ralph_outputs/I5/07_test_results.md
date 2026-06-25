# I5 — 07 Test Results

## Unit / proposition tests — PASS (8/8)
```
$ python3 -m pytest test_sme_rlvr_model.py -q
........                                                                 [100%]
8 passed in 0.12s
```
Plain-script runner (same 8):
```
$ python3 test_sme_rlvr_model.py
PASS test_bad_sme_can_hurt
PASS test_centering_zero_mean
PASS test_flat_verifier_has_low_signal
PASS test_good_sme_helps
PASS test_perfect_reward_max_alignment
PASS test_sweep_monotone_in_eps_trend
PASS test_zero_budget_is_noop
PASS test_zero_lambda_is_noop
8/8 tests passed
```

## Determinism — PASS
```
$ python3 sme_rlvr_model.py > r1 ; python3 sme_rlvr_model.py > r2 ; diff r1 r2
DETERMINISTIC: identical output across two runs
```

## Simulation run (default WorldParams, seed 0)
Headline (`rho_V=0.35`, `p=0.3`, `eps=0.10`, `λ=0.5`):
| metric            | RLVR only | RLVR + SME |
|-------------------|-----------|------------|
| alignment Corr    | 0.281     | **0.318**  |
| magnitude Std(A)  | 0.466     | 0.420      |
| proxy **G**       | 0.1307    | **0.1333** |

`delta_G = +0.00256`, `helps = True`. The *good* SME raises alignment (0.281→0.318)
enough to overcome a slight magnitude drop ⇒ net positive.

### Learning curve (illustrative)
`steps_to_target_rlvr = 7`, `steps_to_target_sme = 6`, speedup ≈ **1.17x**, both saturate
to 1.0. (Treated as illustration only — see `05`/`09`.)

### The crossover — `delta_G` over (eps rows × λ cols)  [THE KEY RESULT]
```
eps \ λ     0.0     0.25     0.5      0.75     1.0
0.00       0.0    +0.0044  +0.0087  +0.0131  +0.0174
0.10       0.0    +0.0013  +0.0026  +0.0038  +0.0051
0.25       0.0    -0.0031  -0.0063  -0.0094  -0.0126
0.40       0.0    -0.0076  -0.0152  -0.0228  -0.0304
0.50       0.0    -0.0106  -0.0213  -0.0319  -0.0426
```
Reading the table (validates the Proposition + corollaries):
- **C1/C3 left column** `λ=0` ⇒ exactly 0 everywhere (no-op).
- **Good SME** (`eps ≤ 0.10`): `delta_G > 0`, and **increases with trust λ** (help grows
  the more you trust an accurate SME).
- **Crossover** between `eps=0.10` and `eps=0.25`: sign flips. This is `eps*`.
- **Bad SME** (`eps ≥ 0.25`): `delta_G < 0`, and **more negative with higher λ** (trusting
  a wrong SME hurts more). Exactly the bang-bang corollary C3.

## Fixes applied during testing
- Removed a stray `sr = rng2 = None` dead line from `learning_curve` (caught on review
  before first run).
- Confirmed `_safe_corr` zero-std guard prevents NaN (exercised by the flat-reward test).
- No other fixes needed; first clean run reproduced the predicted crossover.
