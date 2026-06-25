# A15 — Test Results

## 1. Transform + self-validation (with-gun baseline #55)
```
$ python3 experiments/ralph_outputs/A15/artifacts/noisy_metrics_transform.py \
    scenarios/cidg/generated/55-github-network-partition.yaml --check
OK  transformed [github-network-partition-noisy] validates clean (alerting=noisy, monitoring_degrades=True)
```
PASS.

## 2. Transform on a no-smoking-gun, no-observes-edge baseline (#44)
```
$ python3 experiments/ralph_outputs/A15/artifacts/noisy_metrics_transform.py \
    scenarios/cidg/generated/44-search-cpu-starve.yaml --check
OK  transformed [search-cpu-starve-noisy] validates clean (alerting=noisy, monitoring_degrades=True)
```
PASS — observes-edge injection makes `monitoring_degrades=True` valid even with no guns.

## 3. Official validator on the written variant
```
$ python3 -m sim.spec validate experiments/ralph_outputs/A15/artifacts/55-github-network-partition-noisy.yaml
OK    ...55-github-network-partition-noisy.yaml  [github-network-partition-noisy]  6 nodes / 5 edges / rc=net_delay
1/1 specs valid
```
PASS — drop-in valid scenario (6 nodes = original 5 + monitoring-stack; 5 edges = original 4 + observes).

## 4. pytest (7 cases)
```
$ python3 -m pytest experiments/ralph_outputs/A15/artifacts/test_noisy_metrics_transform.py -q
.......                                                                  [100%]
7 passed in 0.05s
```
PASS — covers: noisy observation set, guns buried deeper (40→120), observes edge injected,
input not mutated, physics (root_cause/canonical_fix/original edges) preserved, both baselines
validate, id idempotent.

## 5. Baseline non-mutation
`git status --porcelain` on the two baselines shows `??` (untracked, pre-existing) — NOT `M`.
The transform writes only to the task artifacts dir; no source scenario was modified.

## Fixes applied during the run
- Initial `--check` failed with `No module named 'sim'` because the script ran outside the repo
  root. Fixed by inserting the computed repo root into `sys.path` inside `_validate`, so the
  transform is cwd-independent. Re-ran: clean.

## Scoped blocker (honest)
Tier-A `propagate()` does not currently read `alerting` or `buried_under` — those fields are
consumed by the observation/tool layer + live mesh, not the fast-sim error/latency math. So an
RL run of baseline-vs-noisy on the *fast sim alone* would show no behavioral delta yet. The A15
deliverable (schema-valid, reward-invariant, observation-degraded variant + reusable transform)
is complete; wiring the engine to amplify alert noise from these fields is downstream work and
would require editing shared core (out of scope per the brief).
