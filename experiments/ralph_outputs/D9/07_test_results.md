# D9 — 07 Test Results

## Unit tests — `pytest test_curriculum_schedule.py -v`
```
collected 10 items
test_a12_order_loads PASSED
test_curriculum_is_easy_to_hard PASSED
test_bands_cover_all_ids_no_overlap PASSED
test_curriculum_progressive_unlock_and_rehearsal PASSED
test_random_seed_deterministic PASSED
test_random_and_curriculum_same_incident_set PASSED
test_training_config_embeds_schedule_and_blocker PASSED
test_comparison_rewards_in_unit_interval PASSED
test_curriculum_auc_beats_random_in_sim PASSED
test_anti_curriculum_is_worst_or_tied PASSED
============================== 10 passed in 0.02s ==============================
```

## Config build — `python3 curriculum_schedule.py --print`
```
wrote training_config.json  (51 incidents, 5 stages, budget=616 samples)
  stage 0: +11 new, 11 active, 88 samples
  stage 1: +10 new, 21 active, 102 samples
  stage 2: +10 new, 31 active, 122 samples
  stage 3: +10 new, 41 active, 142 samples
  stage 4: +10 new, 51 active, 162 samples
```
Active set grows monotonically (rehearsal keeps earlier bands sampled), budget
616 samples.

## Comparison — `python3 curriculum_vs_random.py --seeds 5`
```
[SIMULATED — training blocked] mean_reward per stage (eval over all 51 incidents):
  curriculum  0.12 -> 0.15 -> 0.17 -> 0.18 -> 0.19 -> 0.20
  random      0.07 -> 0.08 -> 0.09 -> 0.11 -> 0.12 -> 0.13
  anti        0.05 -> 0.05 -> 0.05 -> 0.05 -> 0.07 -> 0.12

  curriculum AUC=0.1677  random AUC=0.0929  delta=0.0748  curriculum_wins=True
```
Verdict json: `{curriculum_auc:0.1677, random_auc:0.0929, auc_delta:0.0748,
curriculum_beats_random:true, final_delta:0.0696}`.

## Validation
- Both emitted JSONs parse (`json.load` clean).
- `py_compile` clean on all 3 source files.

## Interpretation (honest)
- Ordering reproduced as designed: **curriculum > random > anti** in the proxy.
- Absolute rewards are LOW (~0.20 ceiling). This is expected, NOT a bug: mean
  incident difficulty ≈12.4 while simulated competence climbs only to ~5 over 6
  stages, so the hard real-outage cascades stay "unsolved" in the proxy. The
  **relative AUC delta** is the claim, not the absolute floor (see 05/09).

## BLOCKER
Real model training (gradient steps) was NOT run: no GPU / training backend in
this environment. The `mean_reward` figures above are a **simulated** competence
proxy (clearly labeled in stdout + `comparison.json.kind`), not measured policy
reward. Deliverables (schedule + config + harness + tests) are real and runnable;
plugging in a real eval is a one-function change (`simulate_run`).
