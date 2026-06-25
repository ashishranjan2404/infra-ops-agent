# 04 — Technical Spec

## Module
`experiments/ralph_outputs/B5/artifacts/frontier_pass_at_k.py` — self-contained CLI.

## Imports (reused, not reimplemented)
- `compute_pass_at_k.pass_at_k(n, c, k)` — unbiased pass@k (Chen et al.).
- `compute_pass_at_k.wilson_ci(p, n)` — Wilson 95% score interval.
- `compute_pass_at_k.binary_pass(reward, threshold)` — reward ≥ threshold → 1.
- `agent.llm.call`, `rex.loop.build_prompt/parse_plan`, `rex.harness.load_scenario/run_plan`,
  `rex.scoring.score_plan`, `rex.tree.rex_tree`.

## Grading path (identical to rex/frontier.py)
```
_propose(model)(scenario, prior_feedback) = parse_plan(call(model, build_prompt(...), max_tokens=4000))
_grade(plan, scenario) = score_plan(plan, scenario, run_plan(plan, scenario), judge_fn=None)[0]   # deterministic
baseline reward = _grade(propose(sc, None), sc)
rex reward      = rex_tree(sc, budget=BUDGET, propose_fn=propose, seed=s)["best_score"]
```

## Function signatures
```python
summarize(rewards: list[float], threshold: float = 0.8) -> dict
  # -> {n, passes, pass@1, ci95:[lo,hi], pass@2, pass@5, mean_reward, reward_std}

run_model(model: str, scenarios: list[str], seeds: int, budget: int,
          threshold: float = 0.8, log=print) -> dict
  # -> {model, seeds, budget, threshold,
  #     baseline: <summarize>, rex: <summarize>,
  #     pass1_lift, mean_lift,
  #     baseline_per_incident: {name:[rewards]}, rex_per_incident: {...},
  #     errors:[{cond,scenario,seed,err}], n_errors}

print_report(rows, scenarios) -> None
main()  # argparse CLI
```

## CLI
```
--models <csv>        default = frontier.py roster (5 models)
--scenarios <csv>     default = frontier.py SCENARIOS (5 incidents)
--seeds <int>         default 5   (samples per model x scenario)
--budget <int>        default 3   (REx tree budget; matches frontier.py BUDGET)
--threshold <float>   default 0.8
--time-budget-s <float>  skip starting NEW models past this wall budget; still writes json
--out <path>          result json
```

## result.json schema
```json
{
  "threshold": 0.8, "seeds": 3, "budget": 3,
  "scenarios": ["oom_kill","gcp_service_control"],
  "models_requested": ["gemini-3.1-pro","deepseek-v4-pro"],
  "elapsed_s": 0.0,
  "models": [ <run_model dict>, ... ]
}
```

## Test cases
- T1 (unit, no network): `summarize([1.0,1.0,0.0], 0.8)` → passes=2, pass@1=0.667,
  pass@2 and pass@5 monotonic ≥ pass@1, ci95 ⊂ [0,1]. `summarize([],0.8)` → n=0, no crash.
- T2 (unit): `summarize([0.4,0.4,0.4],0.8)` → passes=0, pass@1=0.0 (partial-credit farming
  must NOT pass — proves the metric's value over mean=0.4).
- T3 (compile): `python3 -m py_compile` clean.
- T4 (integration, real): subset run (2 gateway models × 2 incidents × 3 seeds, budget 3)
  produces a result.json with real per-model baseline+rex pass@k under the 15-min cap.

## Non-goals / contracts
- Does NOT edit `rex/frontier.py` or any shared core. Upstreaming = call this module or
  paste `summarize`+report into frontier.py `main()`.
- Deterministic judge only (no LLM judge) → reproducible pass@k.
