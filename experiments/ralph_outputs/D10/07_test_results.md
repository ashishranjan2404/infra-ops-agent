# D10 — 07 Test Results

## Commands run (real output)

### 1. Selftest — recomposed composite == score_plan at default weights
```
$ python3 experiments/ralph_outputs/D10/artifacts/reward_sweep.py --selftest
building rollout bank over 8 scenarios ...
  54 real rollouts (sim-executed)
selftest OK: 54 rollouts, recomposed==score_plan at default weights
```
PASS — the wrapper faithfully mirrors `rex/scoring.py` before perturbing weights.

### 2. Full sweep — all 42 scenarios, 292 sim-executed rollouts
```
$ python3 experiments/ralph_outputs/D10/artifacts/reward_sweep.py --all --out .../sweep_results.json
building rollout bank over 42 scenarios ...
  292 real rollouts (sim-executed)
selftest OK: 292 rollouts, recomposed==score_plan at default weights

=== sweep summary ===
weighting            mean  spread     tau  argmax_flip
default            0.3186     1.0  0.8317          0.0
diagnosis_heavy    0.4051     1.0   0.766          0.0
fix_heavy          0.3133     1.0  0.8306          0.0
resolution_only     0.211     1.0  0.4059       0.0238
equal_thirds       0.3351     1.0  0.8317          0.0
no_trap_penalty    0.3832     1.0  0.7229       0.0238
harsh_trap         0.2799     1.0  0.6707          0.0
diag_then_resolve  0.3432     1.0   0.766          0.0
```
PASS — 8 weightings scored over 292 real rollouts.

### 3. Determinism — two runs are byte-identical
```
$ md5 -q /tmp/d10_a.json /tmp/d10_b.json
f24b14f3df8de97fc92b519b4c01c557
f24b14f3df8de97fc92b519b4c01c557
```
PASS.

### 4. Syntax
```
$ python3 -m py_compile .../reward_sweep.py
compiles OK
```

### 5. Argmax-flip evidence (spec test #2 — trap penalty matters)
```
argmax flips per weighting: resolution_only=1, no_trap_penalty=1, all others=0
FLIP azure_ddos: default-best=fix_wrong_target -> no_trap_penalty-best=correct_full
```
PASS — dropping `TRAP_PENALTY` reorders the top-ranked rollout on `azure_ddos`
(when the penalty is removed, the clean on-target fix `correct_full` overtakes the
partial-credit `fix_wrong_target`; the trap candidate's score also rises). This is a
real ranking change, exactly the thing an RFT reward redesign would alter.

## Fixes applied during testing
- Stripped underscore-prefixed internal keys (`_plan`, `_sim_resolved`) from the JSON dump
  to keep the artifact clean (per ouroboros Engineer C). Verified present in `main()`.

## Blocker (recorded, not faked)
No GPU / no policy-gradient loop in this env: we ran the **reward function** over real
rollouts, not a live GRPO update. Training-curve numbers were deliberately NOT fabricated.
