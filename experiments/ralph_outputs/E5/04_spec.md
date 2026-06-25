# E5 — Technical Spec

## Artifact
`experiments/ralph_outputs/E5/artifacts/transfer_eval_novel.py` — standalone CLI.
Imports frozen core, writes only under `E5/`. No core file is modified.

## Inputs
- A8 manifest: `experiments/ralph_outputs/A8/artifacts/heldout_manifest.json`
  (fields used: `per_incident[].cidg_key`, `.held_out`, `.family`,
  `.reasons.tier3_failure_class_seen_in_train`).
- Roster: `agent.models.ROSTER` (resolves model names → provider/model).
- Env: `FIREWORKS_API_KEY`, `HUD_API_KEY`, `ANTHROPIC_API_KEY` (for reachable models).

## Data structures
```python
novel_set: list[str]                  # 10 cidg_keys, asserted in rex.harness._SCENARIOS
scenarios: dict[str, Scenario]        # load_scenario(key)
policy_result = {
  "kind": "control"|"baseline"|"fireball",
  "status": "ok"|"blocked",
  "per_incident": {key: [reward, ...]},  # one reward per seed
  "error": str|None,
  "summary": {"n", "passes", "pass@1", "ci95":[lo,hi], "mean_reward", "reward_std"},
}
report = {
  "threshold": 0.8, "seeds": int, "n_incidents": int,
  "novel_set": [...], "source": "A8 heldout_manifest.json (held_out==true)",
  "policies": {name: policy_result, ...},
  "floor_ceiling": {"empty_mean","oracle_mean","floor_ok","ceiling_ok"},
}
```

## Function signatures
- `select_novel_set(n:int) -> list[str]` — A8 held-out, novel-family first, assert
  loadable; raises `FileNotFoundError` if A8 absent (no fabrication).
- `make_llm_propose(model:str) -> (scenario, seed) -> plan` — zero-shot, temp 0.7,
  `build_prompt(sc, None)` + `parse_plan`.
- `oracle_plan(sc) -> dict` — gold root + first `correct_fix_tools` on `fault_node`.
- `empty_plan(sc) -> dict` — `{"root_cause":"","actions":[]}`.
- `score_one(plan, sc) -> float` — `score_plan(plan, sc, run_plan(plan, sc))[0]`
  (P0 deterministic judge).
- `run_policy(name, scenarios, seeds, propose=None, synth=None) -> policy_result` —
  LLM via `propose`; controls via `synth` (deterministic, replicated across seeds).
  Per-policy try/except records the first error and marks `blocked` if zero episodes.
- `summarize(per_incident) -> summary` — Wilson 95% CI via `compute_pass_at_k.wilson_ci`.

## Scoring contract
- Pass iff `score_plan` reward >= `THRESHOLD = 0.8` (binary_pass).
- Reward = 0.30·diag + 0.25·fix + 0.45·resolved − 0.60·trap (P0 deterministic judge).
- Floor: `empty` pass@1 must be 0.0 (`floor_ok`).
- Ceiling/validity: `oracle` pass@1 must be 1.0 (`ceiling_ok`); a sub-1.0 oracle flags
  a mis-specified incident.

## CLI
```
--n 10  --seeds 3  --baselines glm-5p2[,gpt-5.5,...]
--fireball-model fireball  (or $FIREBALL_MODEL)
--keys k1,k2,...  (override A8 set)
--out E5/transfer_results.json
```

## Test cases
1. `select_novel_set(10)` returns 10 keys, all in `_SCENARIOS`, novel-family ranked first.
2. `empty_plan` scores 0.0 on every incident (floor).
3. `oracle_plan` scores >= 0.8 on every incident (ceiling/validity).
4. Unknown fireball model name → policy `status=blocked`, `error` mentions "not in ROSTER".
5. `transfer_results.json` parses as JSON and contains `policies.empty`,
   `policies.oracle`, and `floor_ceiling`.
