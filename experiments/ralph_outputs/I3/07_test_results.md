# I3 — Test results

## 1. Validation suite (gates the analysis)
```
$ python3 -m pytest experiments/ralph_outputs/I3/artifacts/test_dip_test.py -q
......                                                                   [100%]
6 passed in 0.10s
```
Key gate (Gaussian must read unimodal) passes: D<0.05 & p>0.05 for N(0,1) n=300.
Bimodal gate passes: two-spike D>0.1 & p<0.01. Range, pole-mass, determinism pass.

## 2. Engine sanity (dip_test.py __main__)
```
have diptest pkg: True
uniform   : (0.0219, 0.4235)   # unimodal, not rejected
normal    : (0.0181, 0.7601)   # unimodal, not rejected
bimodal   : (0.1906, 0.0000)   # rejected (multimodal)
```

## 3. Real-data run (run.log)
```
distribution                                n     dip        p  conclusion
A1/glm-5p2::zero_shot                     126  0.1429   0.0000  REJECT unimodality
A1/glm-5p2::best_of_n                     126  0.1508   0.0000  REJECT unimodality
A1/glm-5p2::retry_realistic               126  0.1468   0.0000  REJECT unimodality
A1/glm-5p2::rex                           126  0.0332   0.4221  fail to reject unimodality
A1/glm-5p2::rex_no_oracle                 126  0.1468   0.0000  REJECT unimodality
A1/glm-5p2::ALL_CONDITIONS_pooled         630  0.1214   0.0000  REJECT unimodality
A2/deepseek-v4-pro::zero_shot             150  0.1200   0.0000  REJECT unimodality
A2/deepseek-v4-pro::best_of_n             150  0.1643   0.0000  REJECT unimodality
A2/deepseek-v4-pro::retry_realistic       150  0.1600   0.0000  REJECT unimodality
A2/deepseek-v4-pro::rex                   150  0.0250   0.7750  fail to reject unimodality
A2/deepseek-v4-pro::rex_no_oracle         150  0.1543   0.0000  REJECT unimodality
A2/deepseek-v4-pro::ALL_CONDITIONS_pooled  750  0.1340   0.0000  REJECT unimodality
rex/runs::diagnostic_probe_scores          12  0.1875   0.0001  REJECT unimodality
```

## 4. Figure
`reward_dip_histograms.png` written (47 KB) — A1 per-condition reward histograms
with D/p/verdict annotations.

## Errors / fixes applied during the run
- **BUG (caught by Gaussian gate):** first hand-rolled dip statistic returned
  D≈0.16 for a normal (should be ~0.02), which would falsely flag every
  distribution as bimodal. Fixed by switching the engine to the vetted `diptest`
  package; the hand-rolled version is retained only as a labelled fallback.
- **`ModuleNotFoundError: diptest`** after first install — `pip` targeted a
  different interpreter. Fixed with `python3 -m pip install diptest`; re-verified
  import under the running interpreter.

All commands above were actually executed; outputs are verbatim.
