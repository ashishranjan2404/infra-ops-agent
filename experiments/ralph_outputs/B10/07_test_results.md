# B10 — 07 Test Results

## Environment
Python 3.13.7, matplotlib 3.11.0. No network / GPU needed.

## 1. Syntax / compile
```
$ python3 -m py_compile learning_curve.py test_learning_curve.py
compile OK
```
PASS.

## 2. Unit + integration self-tests
```
$ python3 test_learning_curve.py
ok test_pass1_threshold
ok test_threshold_boundary
ok test_robust_to_garbage
ok test_wilson_ci_bounds
ok test_real_logs_parse
ALL TESTS PASS
```
PASS (5/5). The garbage-robustness test emits the expected warn-and-skip lines for the malformed /
missing / empty rows.

## 3. End-to-end on REAL logs (τ=0.8, canonical)
```
$ python3 learning_curve.py
auto-discovered 3 log(s) under .../opensre-traj/runs
  train_qwen3-30b:    14 steps, pass@1 0.000 -> 0.000 (n=24/step, threshold=0.8)
  train_qwen3-8b:     25 steps, pass@1 0.000 -> 0.000 (n=24/step, threshold=0.8)
  train_qwen3-8b_v2:  15 steps, pass@1 0.000 -> 0.000 (n=40/step, threshold=0.8)
wrote learning_curve.csv
wrote learning_curve.png
```
PASS — runs clean. pass@1 honestly flat-zero (reward ceiling ≈0.78–0.80 < 0.8 bar).

## 4. End-to-end companion (τ=0.65)
```
$ python3 learning_curve.py --threshold 0.65 --out learning_curve_t065.png --csv learning_curve_t065.csv ...
  train_qwen3-30b:    14 steps, pass@1 0.167 -> 0.167
  train_qwen3-8b:     25 steps, pass@1 0.375 -> 0.208   (degrades)
  train_qwen3-8b_v2:  15 steps, pass@1 0.375 -> 0.525   (climbs)
```
PASS — curves now carry signal; CSV tail confirms v2 climb (steps 12→14: 0.400, 0.450, 0.525).

## 5. Output artifacts present & non-trivial
```
learning_curve.png        78 KB
learning_curve.csv        2.9 KB (54 data rows)
learning_curve_t065.png  151 KB
learning_curve_t065.csv   2.9 KB
```
PNG visually verified: 3 pass@1 lines + Wilson bands + mean_reward dashed refs + threshold line.

## Fixes applied during testing
- None required after the ouroboros pass — first real run parsed all logs with zero warnings.
- Discovered (not a bug, a finding): τ=0.8 yields flat-zero → added the τ=0.65 companion as planned.

## Blocker
None for the deliverable. The only "negative result" is intrinsic to the data: the trained Qwen
checkpoints never clear the 0.8 operational bar, so the headline pass@1 is flat at 0. This is the
true RFT outcome, documented honestly — not a tooling failure.
