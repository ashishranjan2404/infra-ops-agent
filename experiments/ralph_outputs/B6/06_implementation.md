# B6 — 06 Implementation

## Artifacts created (all task-namespaced; NO shared core files edited)
- `artifacts/trap_avoidance.py` — the metric module.
  - `action_is_trap(action, trap_actions)` — predicate mirroring `rex/scoring._traps_in`.
  - `classify_episode(ep, scenarios=None)` → `"safe"|"trap"|"unknown"` via the 3-path
    priority (failed_checks token → structural recompute → unknown).
  - `trap_avoidance_rate(episodes, scenarios=None)` → report dict with `rate`,
    `n_safe/n_trap/n_unknown`, `per_scenario` breakdown. UNKNOWN excluded from denominator.
  - `load_episodes_jsonl`, `load_trap_specs` (PyYAML + dependency-free fallback parser).
  - CLI: `python3 trap_avoidance.py EPISODES.jsonl [--scenarios DIR]`.
- `artifacts/test_trap_avoidance.py` — 16 unit tests incl. equality-vs-`rex/scoring._traps_in`.
  Runs under pytest OR standalone (`python3 test_trap_avoidance.py`).
- `artifacts/make_rollouts.py` — generates REAL episodes from `scenarios/cidg/generated/*.yaml`
  (safe agent = canonical_fix steps; trappy agent = the scenario's trap action). Trap labels
  computed with the same `action_is_trap` predicate — not fabricated.
- `artifacts/rollouts.jsonl` — 102 real episodes across 51 CIDG scenarios.

## How it grounds in the deterministic judge
`rex/scoring.py` detects a trap in `_traps_in`: an applied action is a trap iff its `tool`
matches a `scenario.trap_actions` entry and the trap's `target` is `None` or equals the
action's `args.target`. `failed_checks` emits the literal token `"trap_action"`, which
`rex/loop.py` writes into every per-iteration record. `action_is_trap` reproduces that exact
predicate; the metric prefers the judge's own `failed_checks` token when present, so it
aggregates the judge's labels rather than re-deriving them. A unit test asserts
`action_is_trap == rex/scoring._traps_in` so the two cannot silently diverge.

## Proposed (NOT applied) core integration
If later wired into `rex/eval_pass_at_k.py` / a metrics collector, the one-line addition would be:
```python
from experiments.ralph_outputs.B6.artifacts.trap_avoidance import trap_avoidance_rate
report["trap_avoidance"] = trap_avoidance_rate(per_iter_records)  # alongside resolved-rate
```
Left as a documented proposal — no shared file was modified (parallel-safety rule).
