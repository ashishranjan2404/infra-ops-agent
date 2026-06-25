# E9 — 04 Spec

## Data structures

### Augmented group (one record per JSONL line)
```json
{
  "scenario_id": "redis-cache-flush",
  "variant": 0,
  "source": "synthetic_augmented",
  "augmenter": "synth_sre_augmenter@E9",
  "alert_summary": "Fix the root 'session-cache' with clear_cache.",
  "gold": {"root_cause_kind","root_cause_location","fix_tool","fix_target","trap_tools":[]},
  "trajectories": [ <Trajectory>, ... ],
  "within_group_reward_spread": 0.5745
}
```

### Trajectory (FIREBALL-schema: state_before → tool → state_after → reward)
```json
{
  "label": "positive | negative_trap | negative_wrong_fix | negative_empty",
  "state_before": {"alert": str, "topology_nodes": [str], "slo_breached": true},
  "investigation": [str],            // read-only probe tools, order-shuffled
  "action": {"tool": str, "target": str} | null,
  "stated_root_cause": str | null,
  "state_after": {"slo_breached": bool, "root_cleared": bool, "trap_taken": bool},
  "reward": float                    // mirrors rex/scoring.py
}
```

## Reward rubric (mirrors rex/scoring.py — documented, not imported)
`reward = 0.30·diag_correct + 0.25·fix_present + 0.45·resolved − 0.60·trap`
- positive: (1,1,1,0) → **1.0**
- negative_trap: (0,0,0,1) → **−0.60**
- negative_wrong_fix: (0,0,0,0) → **0.0**
- negative_empty: (0,0,0,0) → **0.0**

## Function signatures (`synth_sre_augmenter.py`)
- `augment_scenario(path: str, n: int, seed: int=0) -> list[group]`
- `_gold(sc: dict) -> dict` — reads `root_cause`, `canonical_fix.steps[0]`, `trap_actions`
- `_positive / _negatives(g, sc, rng) -> ...`
- `_reward(diag, fix, resolved, trap) -> float`
- `main(argv)`; `_self_test() -> int`

## Function signatures (`compare_arms.py`)
- `score_synth_arm(groups) -> dict`  (n_traj, label_coverage, spread, domain_match=1, floor_check)
- `score_fireball_arm(path|None) -> dict`  (blocked unless export present; domain_match=0)
- `decide(arm_a, arm_b) -> dict`  (winner + reasons + caveat)

## File formats
- Input: `scenarios/cidg/generated/*.yaml` (CIDG schema; `meta/root_cause/canonical_fix/trap_actions`).
- Output: `augmented_trajectories.jsonl` (one group/line), `comparison_result.json` (pretty).

## Test cases (self-test, hermetic)
1. n=3 → 3 variants. 2. labels include positive/trap/empty. 3. positive reward==1.0.
4. trap reward < 0. 5. empty reward == 0. 6. within-group spread > 0.
7. determinism: same seed → byte-identical JSON.

## API contract for the Fireball arm
Drop a JSONL at `--fireball-jsonl`; harness scores it on the identical vector
(domain_match stays 0 — D&D classes do not map to SRE failure-classes).
