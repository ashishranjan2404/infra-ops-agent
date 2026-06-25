# D10 — 04 Spec

## Module: `experiments/ralph_outputs/D10/artifacts/reward_sweep.py`

### Constants
- `DEFAULT_W = (scoring.W_ROOT, scoring.W_FIX, scoring.W_RESOLVED, scoring.TRAP_PENALTY)`
  — read live from `rex.scoring` so we never hardcode-drift from core.
- `SWEEP: list[tuple[str, float, float, float, float]]` — 8 named weight vectors.

### Data structures
**Rollout** (one element of the bank):
```python
{
  "scenario": str, "candidate": str,
  "primitives": {"diag_ok": bool, "fix": float, "resolved": float, "trap_hit": bool},
  "score_plan_default": float,    # ground truth from rex.scoring.score_plan
}
```
**Sweep result** (one per weighting):
```python
{
  "weighting": str,
  "weights": {"W_ROOT","W_FIX","W_RESOLVED","TRAP_PENALTY"},
  "mean_composite": float, "composite_spread": float,
  "mean_kendall_tau_vs_default": float,
  "argmax_flip_rate": float, "argmax_flips": int, "n_scenarios": int,
}
```

### Function signatures
- `primitives(plan, scenario, sim_result) -> dict` — reuses `scoring.judge_diagnosis`,
  `scoring._fix_credit`, `scoring._traps_in`, `scoring._applied`. **Deterministic judge**
  (REX_JUDGE_MODE defaults to "deterministic"), no LLM/network.
- `compose(prims, w) -> float` — mirrors `score_plan`: `W_ROOT*diag + W_FIX*fix +
  W_RESOLVED*resolved - (TRAP_PENALTY if trap)`, clamped to [0,1], rounded 4dp.
- `candidate_plans(scenario) -> list[(label, plan)]` — fixed family spanning the primitive
  space: `correct_full`, `fix_wrong_target`, `wrong_diag_no_fix`, `empty`,
  `good_diag_no_fix`, and (if scenario has a trap) `trap_only`, `fix_plus_trap`.
- `build_rollout_bank(names) -> list[Rollout]` — runs each plan through real
  `rex.harness.run_plan`.
- `kendall_tau(a, b) -> float` — tau over same-ordered score lists; ties → neither.
- `per_scenario_ranking(bank, w) -> {scenario: [(candidate, score) desc]}`.
- `sweep(bank) -> (results, default_rank)`.
- `selftest(bank)` — asserts `compose(prims, DEFAULT_W) == score_plan_default` for all rollouts.

### CLI
`--selftest` · `--all` (all loadable scenarios) · `--scenarios a,b,c` · `--out path.json`.

### Invariants / test cases
1. **Equivalence:** selftest passes — recomposed default == `score_plan` default (tol 1e-6).
2. **Trap penalty:** for a `trap_only` rollout where trap_hit=True, `no_trap_penalty`
   composite > `harsh_trap` composite by exactly the penalty delta (pre-clamp).
3. **Monotone diagnosis weight:** `diagnosis_heavy` mean_composite ≥ default
   (most candidates have diag_ok=True under the gold diagnosis), observed 0.405 ≥ 0.319.
4. **Determinism:** two runs produce byte-identical `sweep_results.json`.

### File format
`sweep_results.json`: `{default_weights, n_scenarios, n_rollouts, sweep[], example_ranking_default{}, rollout_bank[]}`.
