# B1 — 04 Spec

## Grid definition
```
INCIDENTS  = pick_incidents(per_family)            # full: all 42 (simple 12 / cascade 20 / novel 10)
CONDITIONS = [zero_shot, best_of_n, retry_realistic, rex, rex_no_oracle]   # 5
SEEDS      = 5
EPISODES   = |INCIDENTS| * |CONDITIONS| * SEEDS     # full grid = 42*5*5 = 1050
```
A job is the triple `(condition, incident, seed)`; `run_eval` maps each job to a reward
in `[0,1]` via the condition fn, then `binary_pass(reward, 0.8)`.

## Reused core (grounded in rex/eval_pass_at_k.py — UNMODIFIED)
- `run_eval(model, conditions, per_family, seeds, max_workers, label, ckpt) -> dict`
- `print_report(out)` — overall + per-family table.
- `floor_check(flat) -> {empty_plan_max_reward, trap_max_reward, threshold, floor_ok}`
- `summarize(rewards) -> {n, passes, pass@1, ci95, pass@2, pass@5, mean_reward, reward_std}`
- estimator: `compute_pass_at_k.pass_at_k`, `wilson_ci`, `binary_pass` (single source of truth).
- judge: `rex.scoring.score_plan` (P0 deterministic) + `failed_checks` (clean = SLO+root+no-trap).

## New artifact: run_full_grid.py
```python
main(--model=glm-5p2, --conditions=<csv>, --seeds=5, --per-family=0, --max-workers=10, --out=None)
# per_family = args.per_family or None     # 0 -> None -> all 42 (full grid)
# out = run_eval(model, conditions, per_family, seeds, max_workers, label, ckpt=out+'.partial')
# out['grid'] = {incidents, conditions, seeds, episodes, full_grid}
# assert out['floor_check']['floor_ok']
```
Path contract: REPO = 4 levels up from `artifacts/`; writes ONLY under `B1/artifacts/`.

## Result JSON schema (per condition)
```
by_condition[cond] = {
  overall: {n, passes, pass@1, ci95:[lo,hi], pass@2, pass@5, mean_reward, reward_std},
  by_family: {simple|cascade|novel: <same summarize shape>},
  per_incident_rewards: {<name>: [r,...]},   # len == seeds per incident
}
top-level: model, label, threshold=0.8, seeds, incidents_by_family, n_jobs, elapsed_s,
           errors[], n_errors, floor_check, n_incidents, grid{...}
```

## Test cases
- **T0** `py_compile run_full_grid.py` → SYNTAX OK.
- **T1** subset run: `--per-family 2 --seeds 5` → 150 jobs, `len(errors)` small, exits 0.
- **T2** floor: `floor_check.floor_ok == True` (empty_plan_max < 0.8 and trap_max < 0.8).
- **T3** family coverage: subset `incidents_by_family` has simple/cascade/novel each non-empty.
- **T4** thesis: `rex.overall.pass@1 > zero_shot.overall.pass@1`.
- **T5** monotonicity: pass@1 ≤ pass@2 ≤ pass@5 for every condition.
- **T6** schema: every `overall` carries pass@1/2/5 + ci95 + mean + std + n.
- **T7** summarizer: `summarize_grid.py` reproduces the table from the JSON.

## Summarizer (summarize_grid.py)
Reads the result JSON, prints overall table + writes `summary_table.json`
`{model, seeds, episodes, full_grid, by_condition:{cond:{pass@1,ci95,pass@2,pass@5,mean,std,n}}}`.
