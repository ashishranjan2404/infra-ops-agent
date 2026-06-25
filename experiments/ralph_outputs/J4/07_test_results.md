# J4 — 07 Test Results

## T0 — syntax / compile
```
$ python3 -m py_compile mttr_analysis.py simulate_trials.py
compile OK
```

## T1 — harness self-test (scipy present)
```
$ python3 mttr_analysis.py --self-test
  [PASS] gmean(1,10,100)==10
  [PASS] median([1,2,3,4])==2.5
  [PASS] within speedup ~2 (1.6..2.5)
  [PASS] within CI brackets speedup
  [PASS] within significant
  [PASS] within n_pairs==40
  [PASS] within cliffs_delta>0 (control slower)
  [PASS] between null speedup ~1 (0.7..1.4)
  [PASS] between null CI brackets 1.0
  [PASS] rejects bad arm
  [PASS] rejects nonpositive mttr
  [PASS] power: bigger effect needs fewer pairs
ALL PASS   (exit 0)
```

## T2 — no-scipy fallback (permutation tests)  ✅
Shadowed scipy with a broken stub on PYTHONPATH:
```
HAVE_SCIPY = False
... ALL PASS   (exit 0)
```
The permutation/bootstrap fallbacks reproduce the same conclusions hermetically.

## T3 — within-subjects pipeline (50 pairs, planted 1.8x, 25% no-benefit)
A9 baseline used: **True**. Report `report_within.json`:
```
speedup        1.5049     (planted 1.8, attenuated by no-benefit frac — expected)
speedup_ci95   [1.341, 1.6783]
pct_reduction  33.55 %
p_value        0.0   (paired t-test on log MTTR; Wilcoxon p=0.0000)
gm_control 277.5 min  gm_agent 184.4 min
median 264.6 -> 187.6 min
%-within-SLO(120): control 34% -> agent 38%
cliffs_delta   0.143   significant_at_05  True
```

## T4 — between-subjects (A/B) pipeline (120 incidents)
```
speedup 1.868   CI [1.006, 3.3897]   p 0.0475 (Welch on log; Mann-Whitney p=0.0538)
cliffs_delta 0.205   significant_at_05 True
```
Wider CI / borderline p reflects the lower power of unpaired A/B — as designed.

## T5 — null case (true_speedup=1.0, 100% no-benefit)  ✅ negative control
```
speedup 0.9582   CI [0.8778, 1.0416]   p 0.343   significant_at_05 False
```
CI brackets 1.0 and the test is correctly non-significant — the harness does NOT
manufacture an effect when none exists.

## Fixes applied during dev
- Initial `--self-test` confirmed clean on first run (no fixes needed); the
  no-scipy path was validated post-hoc via a PYTHONPATH stub.

## Verdict
All hermetic tests PASS (with and without scipy). Both designs run on grounded
synthetic data; planted effect recovered (attenuated honestly), null correctly
non-significant.
