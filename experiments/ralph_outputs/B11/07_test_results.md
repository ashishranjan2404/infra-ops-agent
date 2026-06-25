# 07 — Test results

## Commands run (real output)

### Syntax / parse check
```
$ python3 -c "import ast; ast.parse(open('.../threshold_sweep.py').read())"
threshold_sweep.py OK
$ python3 -c "import ast; ast.parse(open('.../test_threshold_sweep.py').read())"
test_threshold_sweep.py OK
```
PASS — both artifacts parse.

### End-to-end sweep run
```
$ python3 experiments/ralph_outputs/B11/artifacts/threshold_sweep.py
arm                 thr=0.70    thr=0.80    thr=0.86    thr=0.90
zero_shot               0.20        0.00        0.00        0.00
best_of_n               0.20        0.07        0.07        0.07
retry_realistic         0.20        0.00        0.00        0.00
rex                     0.40        0.40        0.40        0.40
rex_no_oracle           0.20        0.00        0.00        0.00
REx - best ctrl        +0.20       +0.33       +0.33       +0.33
REx wins?                yes         yes         yes         yes
robust (REx wins at every threshold): True
written: .../artifacts/robustness.json
```
PASS — robustness.json written, 4 thresholds x 5 arms.

### Unit tests (offline, no network)
```
$ python3 -m pytest experiments/ralph_outputs/B11/artifacts/test_threshold_sweep.py -q
...                                                                      [100%]
3 passed in 0.02s
```
Also via the standalone runner:
```
PASS test_binary_pass_matches_canonical
PASS test_sweep_on_real_data
PASS test_wilson_matches_hand_formula
3/3 passed
```

## What each test proved
1. `test_binary_pass_matches_canonical` — the COPIED `binary_pass` reproduces the
   canonical `reward >= threshold` rule (estimator-drift guard).
2. `test_wilson_matches_hand_formula` — the COPIED `wilson_ci` matches the
   hand-computed canonical Wilson formula to <1e-3 at p in {0,0.07,0.4,1.0}, n=15.
3. `test_sweep_on_real_data` — on the REAL ablation.json: 4 thresholds x 5 arms; REx
   beats best control at the published 0.80 cutoff; REx wins at all thresholds.

## Fixes applied during dev
- Added the load-time `per_incident` shape assert (05_ouroboros) — re-ran, still PASS.
- No other fixes needed; first run was correct.

## Blockers
None. The task is a re-thresholding of existing real reward data; no live cluster /
API / GPU needed.
