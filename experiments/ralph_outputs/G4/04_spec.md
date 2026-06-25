# 04 — Technical Spec

## A. What "trap action" means in OUR system (grounded)

Source of truth (read, not modified):

- `rex/scoring.py:22` — `W_ROOT, W_FIX, W_RESOLVED, TRAP_PENALTY = 0.30, 0.25, 0.45, 0.60`
- `rex/scoring.py:175-182` — `_traps_in(actions, scenario)`: an applied action is a trap iff
  `a.tool == t["tool"]` AND (`t["target"] is None` OR `t["target"] == a.args.target`).
- `rex/scoring.py:206-209` — `score -= TRAP_PENALTY` when any trap is hit; final clamped to
  `[0,1]`.
- `rex/scoring.py:243-252` — per-trap natural-language `why` table (scale_deployment,
  clear_cache, restart_service) appended to feedback as `TRAP: ... WRONG: <why>`.
- `rex/scoring.py:185-196` — `failed_checks` emits `"trap_action"` as a named failed check.
- `rex/scoring.py:254-257` — separate `BLOCKED` channel: actions stopped by the safety
  harness (`sim_result["blocked_actions"]`) reported with a reason — distinct from a trap
  (trap = allowed-but-penalized; blocked = prevented).

Scenario carrier:
- `rex/harness.py:229` — `Scenario.trap_actions: list  # [{"tool": str, "target": str}]`
- `rex/harness.py:307-308` — built from `spec.trap_actions` (YAML) unless overridden.
- YAML schema (per `scenarios/cidg/generated/*.yaml`):
  ```yaml
  trap_actions:
    - tool: scale_deployment
      args: {target: <node>, replicas: <int?>}   # target/replicas optional
  ```

## B. Taxonomy record (output schema of the extractor)

```json
{
  "scenario_id": "media-oom-leak",            // meta.id
  "file": "46-media-oom-leak.yaml",
  "failure_class": "mem_leak",                // meta.failure_class
  "fault_node": "thumbnailer",                // root_cause.location head
  "trap": {"tool": "scale_deployment", "target": "thumbnailer"},
  "contrasted_gold_fix": ["increase_memory_limit"],  // canonical_fix step tools
  "why_label": "scaling does not address the root cause ..."  // from scoring.py table, or null
}
```

Top-level artifact:
```json
{
  "trap_penalty": 0.60,
  "score_weights": {"root": 0.30, "fix": 0.25, "resolved": 0.45},
  "n_scenarios": <int>,
  "n_with_trap": <int>,
  "trap_tool_distribution": {"scale_deployment": <int>, ...},
  "records": [ <taxonomy record>, ... ]
}
```

## C. Function signatures (`extract_trap_taxonomy.py`)

```python
def load_why_table(scoring_path: str) -> dict[str, str]: ...   # parse the why-dict literal
def scenario_records(yaml_dir: str, why: dict) -> list[dict]: ...
def build_taxonomy(repo_root: str) -> dict: ...
def main(repo_root: str, out_path: str) -> dict: ...           # writes JSON, returns it
```

`load_why_table` extracts the `why = {...}.get(...)` dict literal from `scoring.py` via
`ast` (read-only; no import side effects, no core edit).

## D. Test cases (`test_extract_trap_taxonomy.py`, pytest)

1. `build_taxonomy` returns `trap_penalty == 0.60` and weights summing to 1.0.
2. `n_with_trap >= 40` and every record's `trap` has a non-empty `tool`.
3. `scale_deployment` is the modal trap tool (matches the real data).
4. Every `contrasted_gold_fix` is non-empty (a trap is always contrasted against a real fix).
5. `load_why_table` returns a dict containing `scale_deployment`.

## E. Comparison report contract (`comparison_report.md`)
Sections: (1) Our mechanism (grounded, with file:line). (2) SREGym oracle. (3) ITBench /
AIOpsLab. (4) Safe-RL precedent. (5) Side-by-side table. (6) Scoped novelty claim. (7)
Honest limitations. (8) Citations.
