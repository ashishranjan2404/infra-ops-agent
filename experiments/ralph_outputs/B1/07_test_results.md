# B1 — 07 Test Results

All commands run for real; model = glm-5p2 (gateway, HUD_API_KEY); P0 deterministic judge.

## T0 — runner + summarizer syntax (PASS)
`python3 -m py_compile run_full_grid.py` -> `SYNTAX OK`.
`python3 -m py_compile summarize_grid.py` -> `SUMMARIZER SYNTAX OK`.

## T1 — REAL subset run (PASS)
`run_full_grid.py --model glm-5p2 --seeds 5 --per-family 2 --max-workers 10`
-> **150 episodes, 0 errors, 429.8 s (~7 min)**. Exited 0; final JSON
`artifacts/grid_sub2_glm-5p2.json` + log `artifacts/run_sub.log`.

## T2 — floor check (PASS)
`{"empty_plan_max_reward":0.0,"trap_max_reward":0.0,"threshold":0.8,"floor_ok":true}`.
Cheapest path (empty plan / first trap) stays below 0.8. No reward-hacking floor.
The runner's `assert floor_ok` passed (run exited 0).

## T3 — family coverage (PASS)
Subset `incidents_by_family` = simple/cascade/novel each = 2 incidents (non-empty). All
three families represented in the capped run.

## Overall pass@k (n=30 per condition = 6 incidents × 5 seeds)
| condition | pass@1 | 95% CI | pass@2 | pass@5* | mean | std |
|---|---|---|---|---|---|---|
| zero_shot | 0.333 | [0.19,0.51] | 0.563 | 0.891 | 0.52 | 0.42 |
| best_of_n | 0.400 | [0.25,0.58] | 0.648 | 0.940 | 0.69 | 0.32 |
| retry_realistic | 0.433 | [0.27,0.61] | 0.687 | 0.957 | 0.78 | 0.25 |
| **rex** | **0.967** | **[0.83,0.99]** | 1.000 | 1.000 | 0.98 | 0.08 |
| rex_no_oracle | 0.333 | [0.19,0.51] | 0.563 | 0.891 | 0.69 | 0.29 |

\*pass@5 with seeds=5 is optimistic (Chen estimator saturates once an incident is ever
solved). Headline = pass@1 ± Wilson CI.

## T4 — thesis direction (PASS, separated)
`rex.pass@1 (0.967) > zero_shot.pass@1 (0.333)`, and the **Wilson CIs are DISJOINT**
(rex lower 0.833 > zero_shot upper 0.512). Consistent with A1's full-42×3-seed anchor
(rex 0.897 [0.83,0.94] vs zero_shot 0.230 [0.17,0.31]).

## T5 — monotonicity pass@1 ≤ pass@2 ≤ pass@5 (PASS for all 5 conditions).

## T6 — schema (PASS)
Every `by_condition[c].overall` carries pass@1/2/5 + ci95 + mean_reward + reward_std + n;
`per_incident_rewards` retained for all 6 subset incidents.

## T7 — summarizer (PASS)
`summarize_grid.py grid_sub2_glm-5p2.json` reproduces the table, emits the DISJOINT thesis
line, and writes `artifacts/summary_table.json`.

## BLOCKER — full grid exceeds the compute cap (documented, not faked)
The full grid is **42 × 5 × 5 = 1050 episodes**. The subset ran 150 eps in 430 s
(~2.87 s/ep); the full grid scales to **~50 min**, over the ~15-min model-run cap
(consistent with A1's 630 eps in ~27 min). Per the brief's COMPUTE CAP rule I ran a
representative subset and ship the **full runnable grid** (`run_full_grid.py
--per-family 0 --seeds 5`, resumable via `.partial`) + the subset anchor + A1's full-42
reference. The 900 unrun episodes are NOT fabricated.

## Per-family note (honesty)
The subset's per-family table (e.g. cascade rex 0.900) is on n=10/family → CI ~±0.18, too
wide to claim. Per-family claims are deferred to the full grid / A1's full-42×3-seed JSON.
The hardest multi-fault cascades (80-multi-*, 82-multi-*) are only covered by the full-grid
script, not the 6-incident subset.
