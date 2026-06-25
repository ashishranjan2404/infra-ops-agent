# A1 — 07 Test Results

All commands run real; model = glm-5p2 (gateway, HUD_API_KEY); deterministic P0 judge.

## T0 — runner syntax
`python3 -m py_compile run_full_pass_at_k.py` -> `SYNTAX OK`.

## T1 — incident count == 42 (PASS)
`pick_incidents(None)` -> 42 incidents. Runner asserts `n_incidents == 42`; final JSON has
`"n_incidents": 42, "full_set": true`.

## T2 — floor check over all 42 (PASS, run offline before the sweep)
```
{"empty_plan_max_reward":0.0,"trap_max_reward":0.1,"threshold":0.8,"floor_ok":true}
```
Cheapest path (empty plan / first trap) stays below 0.8 on every incident. No reward-hacking floor.

## T3 — family sizes (PASS)
simple=12, cascade=20, novel=10  (=42).

## The full sweep (REAL RUN)
`run_full_pass_at_k.py --model glm-5p2 --seeds 3 --conditions
 zero_shot,best_of_n,retry_realistic,rex,rex_no_oracle --max-workers 10`
-> **630 episodes, 0 errors, 1608.3 s (~27 min)**. Final JSON:
`artifacts/full_pass_at_k_glm-5p2.json` (26 KB).

### Overall pass@k (n=126 per condition = 42 incidents × 3 seeds)
| condition | pass@1 | 95% CI | pass@2 | pass@5* | mean | std |
|---|---|---|---|---|---|---|
| zero_shot | 0.230 | [0.17,0.31] | 0.409 | 0.736 | 0.43 | 0.38 |
| best_of_n | 0.341 | [0.26,0.43] | 0.568 | 0.881 | 0.65 | 0.31 |
| retry_realistic | 0.349 | [0.27,0.44] | 0.578 | 0.888 | 0.66 | 0.30 |
| **rex** | **0.897** | **[0.83,0.94]** | 0.990 | 1.000 | 0.94 | 0.17 |
| rex_no_oracle | 0.333 | [0.26,0.42] | 0.557 | 0.874 | 0.66 | 0.30 |

\*pass@5 with seeds=3 is optimistic (the Chen estimator saturates once an incident is ever
solved). Headline = pass@1 ± Wilson CI.

### Per-family pass@1 (rex)
simple 0.889 [0.75,0.96] · cascade 0.850 [0.74,0.92] · novel **1.000** [0.89,1.00] (std 0).

## T4 — schema (PASS)
Every `by_condition[c].overall` carries pass@1/pass@2/pass@5/ci95/mean_reward/reward_std/n;
`per_incident_rewards` retained for all 42 incidents.

## T5 — monotonicity pass@1 <= pass@2 <= pass@5 (PASS for all 5 conditions).

## T6 — thesis direction (PASS, and separated)
`rex.pass@1 (0.897) > zero_shot.pass@1 (0.230)`, and the **Wilson CIs are disjoint**
(rex lower 0.832 > zero_shot upper 0.311). REx's advantage is statistically clean on the full set.

## T7 — summarizer (PASS)
`summarize_result.py` reproduces the table from the JSON and writes `summary_table.json`.

## Fixes applied during the run
- Runner failed first launch with `ModuleNotFoundError: rex` (deep cwd) -> added
  `sys.path.insert(REPO)`; relaunched clean.
- Killed leftover monitor shell-loops after the run (cosmetic; the runner itself exited 0).
