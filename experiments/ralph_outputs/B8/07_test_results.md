# 07 — Test Results

## Self-test (known textbook values)
```
$ python3 effect_size.py --selftest
  [PASS] cohens_h(0.5,0.25): got=0.52360 want=0.52360
  [PASS] cohens_h(0.25,0.5) = -above: got=-0.52360 want=-0.52360
  [PASS] cohens_h(0.4,0.4): got=0.00000 want=0.00000
  [PASS] cohens_h(1,0)=pi: got=3.14159 want=3.14159
  [PASS] cohens_d means 7 vs 5, sd 2: got=1.00000 want=1.00000
  [PASS] cohens_d 0.5 sep, sd1: got=0.50000 want=0.50000
  [PASS] pooled_sd(2,10,2,10): got=2.00000 want=2.00000
  [PASS] pooled_sd(3,5,5,5): got=4.12311 want=4.12311
  [PASS] magnitude labels
SELFTEST: ALL PASS
```

## pytest
```
$ python3 -m pytest test_effect_size.py -q
..........                                                               [100%]
10 passed in 0.02s
```

## Run on REAL data
```
$ python3 effect_size.py A1/.../full_pass_at_k_glm-5p2.json A2/.../ablation_pass_at_k_deepseek-v4-pro.json

=== glm-5p2  (glm-5p2 (full-42))  baseline=zero_shot ===
condition          pass@1       Δp        h h-mag         reward       Δr        d d-mag
best_of_n           0.341   +0.111   +0.247 small          0.652   +0.224    0.638 medium
retry_realistic     0.349   +0.119   +0.264 small          0.662   +0.233    0.674 medium
rex                 0.897   +0.667   +1.487 large          0.943   +0.514    1.725 large
rex_no_oracle       0.333   +0.103   +0.230 small          0.660   +0.231    0.668 medium

=== deepseek-v4-pro  (deepseek-v4-pro (A2))  baseline=zero_shot ===
condition          pass@1       Δp        h h-mag         reward       Δr        d d-mag
best_of_n           0.307   +0.067   +0.150 negligible     0.605   +0.127    0.358 small
retry_realistic     0.313   +0.073   +0.164 negligible     0.616   +0.138    0.387 small
rex                 0.893   +0.653   +1.452 large          0.928   +0.450    1.462 large
rex_no_oracle       0.287   +0.047   +0.106 negligible     0.591   +0.113    0.319 small
```

`effect_size_report.json` written (2 models, 4 lifts each, 3942 bytes).

## Errors / fixes
None during the run. During build, the ouroboros-identified edges (sp==0, p out of range,
missing baseline) were covered by guards before first run; no post-hoc fixes needed.
