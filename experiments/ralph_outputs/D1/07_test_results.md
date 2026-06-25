# D1 — 07 Test Results

## 1. Launcher syntax check
```
$ bash -n run_rft_50.sh && echo OK
run_rft_50.sh OK
```
PASS — `set -euo pipefail`, correct `cd`, `exec`s the unmodified `train_rft_v2.py`.

## 2. Analyzer unit tests (spec §Test cases)
- **T1** existing v2 run (15 steps): delta=+0.0371, slope=+0.00174, verdict=`flat`. **PASS**
- **T2** existing v1 run (25 steps): slope=−0.00071, delta=−0.031, verdict=`flat`/down. **PASS**
  (analyzer distinguishes the two runs)
- **T3** <2 lines: `need >=2 steps, got 1` → SystemExit. **PASS**
- **T4** synthetic increasing run: verdict=`continuing-up`, slope=+0.02, proj@50=1.4. **PASS**

## 3. Live-backend smoke (1 step, group 2, 2 tasks)
```
[smoke] rollouts=4 rewards=[0.588, 0.704, 0.252, 0.312] spread=0.188
step   0  mean_reward=0.4640  spread=0.188  n=4  loss=None
SMOKE OK: rollouts -> reward (v2 grader) -> forward/backward -> logged.
```
PASS — full GRPO pipeline works against the live HUD/Tinker GPU backend.

## 4. REAL 50-step run — partial curve (compute-capped)
Launched: `train_rft_v2.py --model opensre-qwen3-8b-1e439a --tasks 0..9 --group 6
--steps 50 --lr 1e-5 --out artifacts/train_d1_50step.jsonl`. 60 rollouts/step.

9 real steps completed before I stopped it at the attended-time budget:
```
step 0 mean=0.5139 std=0.193 n=60
step 1 mean=0.5269 std=0.189 n=60
step 2 mean=0.5393 std=0.183 n=60
step 3 mean=0.5144 std=0.180 n=60
step 4 mean=0.5270 std=0.180 n=60
step 5 mean=0.5330 std=0.175 n=60
step 6 mean=0.5336 std=0.181 n=60
step 7 mean=0.5139 std=0.195 n=60
step 8 mean=0.5399 std=0.181 n=60
```
Analyzer on the partial curve (horizon 50):
```
n_steps=9  step0=0.5139  stepN=0.5399  delta=+0.0260
ols_slope_per_step=+0.00120  verdict=flat  projected_at_horizon{50}=0.5741
```

### Finding
The fresh run **reproduces** the original v2 trend: small positive slope
(+0.0012/step here vs +0.0017/step on the original 15-step run), same `flat`
verdict, projecting to ~0.57–0.59 at step 50. The +0.037-style trend is real in
sign and **reproducible**, but its slope is below the per-step reward std (~0.18,
SE≈0.025) — i.e. within noise, not a strong climb.

### Blocker (documented, not faked)
Finishing all 50 steps was **compute-blocked**: ~75–90 s/step on the Tinker backend
(60 rollouts/step + transient 5xx retries) → 50 steps ≈ 60–75 min, well past the
~15-min cap. I deliver the runnable 50-step launcher + this real 9-step partial
curve; the remaining 41 steps were **not** fabricated. To complete: run
`run_rft_50.sh` unattended in the background.
