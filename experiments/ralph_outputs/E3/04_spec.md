# E3 — 04 Technical Spec

## Module: `artifacts/eval_three_way_cascade.py`

### Constants
- `THRESHOLD = 0.8` — pass iff deterministic reward ≥ 0.8.
- `EXTRA_ROSTER` — local roster rows (registered at runtime, never written to `agent/models.py`):
  - `qwen3-8b-base` → `{"provider":"gateway","model":"Qwen/Qwen3-8B"}`  (zero-shot control)
  - `opensre-qwen3-8b` → `{"provider":"gateway","model":"opensre-qwen3-8b-1e439a"}` (OpenSRE forked slug)
- `ARMS` — the 3 arms:
  ```
  zero_shot        -> roster_key "qwen3-8b-base",   status "runnable"
  opensre_trained  -> roster_key "opensre-qwen3-8b", status "runnable"
  fireball_trained -> roster_key None,               status "blocked" (documented reason)
  ```

### Function signatures
- `register_extra_models() -> None` — `ROSTER.setdefault(k, v)` for each EXTRA_ROSTER row (idempotent, local).
- `select_cascade_incidents(n: int = 14) -> list[str]` — `sorted(scenarios_by_family()["cascade"])[:n]`;
  raises if fewer than `n` cascade incidents exist.
- `make_proposer(roster_key, temp=0.7, max_tokens=1400)` — returns `_propose(scenario) -> plan dict`,
  one transient-error retry; uses `agent.llm.call` + `build_prompt` + `parse_plan`.
- `score_episode(roster_key, scenario) -> float` — propose → `run_plan` → `score_plan` (deterministic).
- `summarize(rewards: list) -> dict` — `{n, passes, pass@1, ci95, pass@2, mean_reward, reward_std}`.
- `reachable(roster_key) -> (bool, str)` — one 8-token probe call; returns ok + detail.
- `run(seeds, incidents, arms_to_run, max_workers=8) -> dict` — ThreadPool over
  (arm, incident, seed) jobs; per-arm overall summary + per-incident means; errors captured.
- `main()` — CLI: `--seeds --n-incidents --max-workers --dry-run --out`.

### Episode protocol (one job)
`(arm, incident, seed)` → resolve arm's `roster_key` → `score_episode` → reward ∈ [0,1].
Zero-shot single proposal (no REx tree / no retry loop) so the comparison isolates the *policy*,
not the search budget.

### Output JSON contract (`result_three_way.json`)
```
{ "task_id":"E3", "mode":"eval"|"dry-run"|"no-runnable-arms",
  "threshold":0.8, "incident_family":"cascade", "n_incidents":14,
  "incidents":[...14 names...],
  "arm_status": { "<arm>": {"runnable":bool, "roster_key":?, "probe"|"reason":...} },
  "blocked_arms":["fireball_trained"], "runnable_arms":[...],
  "seeds":int, "elapsed_s":float, "n_errors":int, "errors":[...],
  "by_arm": { "<arm>": { "roster_key":str, "note":str,
                         "overall": <summarize>,
                         "per_incident_mean": {name: mean|null} } } }
```

### Test cases (`test_eval_three_way_cascade.py`, network-free)
1. selects exactly 14 distinct cascade incidents, all genuinely `family=cascade`.
2. selection deterministic.
3. exactly 3 arms; exactly one blocked == `fireball_trained`; its roster_key is None.
4. runnable arms have distinct real slugs (`Qwen/Qwen3-8B` vs `opensre-qwen3-8b-1e439a`).
5. `register_extra_models` is local (slugs absent before call) + idempotent.
6. `summarize` math: passes count, pass@1, mean, positive std; empty list → zeros.

### Non-goals
- No LLM judge (deterministic only). No REx search (isolates policy). No Fireball numbers.
- No edits to `agent/*`, `rex/*`, `sim/*`, `experiments/*.py`.
