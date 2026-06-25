# E4 — 04 Technical Spec

## Artifact: `artifacts/compare_simple8.py`

### Constants
- `THRESHOLD = 0.8` — binary pass cut on the deterministic reward (matches
  `rex.eval_pass_at_k`).
- `SIMPLE_8: list[str]` — the 8 pinned incident names (all in the `simple` family):
  `cpu_saturation_leaf, oom_kill, bad_deploy_leaf, redis_cache_flush,
  auth_cert_expiry, billing_disk_fill, singleton_node_notready, ingest_fd_exhaust`.

### Function signatures
```python
validate_incidents(names: list[str]) -> None
    # SystemExit if any name not in scenarios_by_family()["simple"].

propose(model: str, scenario, temp=0.7, max_tokens=1400) -> dict
    # zero-shot plan via build_prompt(scenario, None) -> call() -> parse_plan();
    # one retry on transient error, else re-raise.

episode_reward(model: str, scenario) -> float
    # run_plan(plan, scenario) -> score_plan(...)[0]  (P0 deterministic judge).

summarize(rewards: list[float]) -> dict
    # {n, passes, pass@1, ci95:[lo,hi], pass@2, mean_reward, reward_std}

run(model_a, model_b, label_a, label_b, seeds, incidents, max_workers=8) -> dict
print_report(out: dict) -> None
main() -> None   # argparse CLI
```

### CLI contract
```
--model-a STR (req)  --model-b STR (req)
--label-a STR  --label-b STR   (default: slug)
--seeds INT=3  --max-workers INT=8  --out PATH
```

### Output JSON schema (`run()` return)
```jsonc
{
  "task_id": "E4", "threshold": 0.8, "seeds": 3,
  "incidents": [..8..], "n_incidents": 8,
  "policy_a": {"label": str, "model": str},
  "policy_b": {"label": str, "model": str},
  "overall": { "<label_a>": <summary>, "<label_b>": <summary> },
  "per_incident": [
    { "incident": str,
      "<label_a>_pass@1": float, "<label_b>_pass@1": float,
      "delta_b_minus_a": float, "hurts": bool,
      "<label_a>_mean": float, "<label_b>_mean": float } , ...],
  "regression": {
    "n_incidents_b_hurts_vs_a": int,
    "mean_delta_b_minus_a": float,
    "verdict": "B_HELPS"|"NO_NET_CHANGE"|"B_HURTS" },
  "elapsed_s": float, "n_errors": int, "errors": [...],
  "note": "STAND-IN policies … neither trained slug exists; re-run with real slugs."
}
```

### Reward / judge contract
Reuses the FROZEN P0 deterministic judge (`rex.scoring.score_plan`): reward ≥ 0.8
≡ SLO restored + root cleared + no trap. No LLM judge → reproducible.

## Tests: `artifacts/test_compare_simple8.py` (offline, no network)
- `test_eight_pinned_incidents` — exactly 8, no dupes.
- `test_pinned_are_simple_family` — `validate_incidents(SIMPLE_8)` does not raise.
- `test_summarize_all_pass / _mixed / _empty` — pass counting + spread + empty safety.
- `test_binary_pass_threshold` — 0.79 fails, 0.80 passes.

## Non-goals
- No training. No editing `rex/*`, `sim/*`, `agent/*`, `experiments/*.py`,
  `ralph_status.json`, or another task's dir.
- No claim of statistical significance at small n.
