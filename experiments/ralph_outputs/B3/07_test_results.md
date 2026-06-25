# B3 — 07 Test Results

## 1. Unit tests (validate the formula against known values)
```
$ cd experiments/ralph_outputs/B3/artifacts
$ python3 -m pytest test_wilson_ci.py -q
...........                                                              [100%]
11 passed in 0.01s
```
Also passes via the no-pytest fallback runner (`python3 test_wilson_ci.py` → 11/11).

Tests cover:
- KNOWN textbook values: 50/100 → [0.4038, 0.5962]; 0/10 → [0, 0.2775]; 10/10 → [0.7225, 1]
- Agreement with an independently-written reference closed form (9 (c,n) pairs)
- Symmetry, monotone-narrowing-with-n, bounds in [0,1], contains point estimate
- Edge cases: n=0 → (0,1); bad inputs ((-1,10),(11,10),(5,-1)) raise ValueError
- Schema parser: synthetic doc → 2 rows, recomputed ≈ upstream stored ci95

## 2. Run on real A1/A2 pass@k JSONs
```
$ python3 wilson_ci.py --json wilson_table.json
# Wilson 95% CIs over 40 pass@1 cells from 2 file(s)
```
40 cells emitted (2 files × 5 conditions × {overall + 3 families}). Full table in `run.log`.
Representative rows:

| condition | scope | n | pass@1 | Wilson 95% CI | ± | match? |
|---|---|--:|--:|---|--:|--|
| glm-5p2 / zero_shot | cascade | 60 | 0.067 | [0.026, 0.159] | 0.067 | ok |
| glm-5p2 / rex | novel | 30 | 1.000 | [0.886, 1.000] | 0.057 | ok |
| glm-5p2 / rex | overall | 126 | 0.897 | [0.832, 0.939] | 0.054 | ok |
| deepseek / zero_shot | cascade | 50 | 0.020 | [0.004, 0.105] | 0.051 | ok |
| deepseek / rex | simple | 50 | 1.000 | [0.929, 1.000] | 0.036 | ok |
| deepseek / rex | cascade | 50 | 0.680 | [0.542, 0.792] | 0.125 | ok |

## 3. Cross-validation vs upstream stored ci95
```
$ grep -c "ok" run.log
40
```
**40/40 recomputed Wilson intervals match the upstream `ci95` within 0.01.** This is an
independent reproduction of the published A1/A2 confidence intervals (and a confirmation
that the B3 tool reads the right `(n, passes)` and the right family aggregation).

## 4. Arithmetic audit (n's are not double-counted)
```
A1: overall n=126, sum of family n=126, match=True
A2: overall n=150, sum of family n=150, match=True
```
Per-family n's sum exactly to the overall n in both files — no pooling double-count.

## Fixes applied during testing
- None required for correctness. The exact `Z95` constant (not 1.96) was chosen up front,
  which is why `test_known_value_p_half` passes to 1e-3 against the literal textbook value.
- Note: the `retry_realistic` condition label runs into the scope column in the fixed-width
  table (cosmetic only — the machine-readable `wilson_table.json` has clean fields).

## Result: PASS — all unit tests green, all 40 cells reproduce upstream CIs.
