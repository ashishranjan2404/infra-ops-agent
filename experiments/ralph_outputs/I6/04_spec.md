# I6 — 04 Spec

## Data structures

```python
@dataclass
class Rollout:
    source: str            # "probe" | "hud"
    rollout_id: str        # file:line  or  trace_id
    scenario: str          # scenario name
    score: float           # graded reward in [0,1]
    resolved: bool
    diagnosis_correct: bool
    failed_checks: list[str]   # subset of {root_cause, correct_fix_missing, trap_action, not_resolved}
    n_actions: int
    primary_bucket: str    # see precedence below
    tags: list[str]        # secondary labels
```

## Buckets & precedence
`failed_checks` (from `rex.scoring.failed_checks`) drives labeling.

Primary bucket (first match wins):
1. `trap_taken`        if "trap_action" in failed_checks
2. `wrong_root_cause`  elif "root_cause" in failed_checks
3. `no_fix`            elif "correct_fix_missing" in failed_checks
4. `not_resolved`      elif "not_resolved" in failed_checks
5. `clean_win`         else (score==1.0, empty failed_checks) — excluded from failure set

Secondary tags (non-exclusive): every raw failed_check, plus
- `empty_plan`    if n_actions == 0
- `safe_abstain`  if n_actions == 0 and "trap_action" not in failed_checks
- `zero_reward`   if score == 0.0

## Function signatures
```python
def load_probe_rollouts(path: str) -> list[Rollout]
def load_hud_rollouts(glob_pat: str) -> list[Rollout]     # re-scores via rex.scoring
def bucket(r: Rollout) -> tuple[str, list[str]]           # (primary, tags)
def summarize(rollouts: list[Rollout]) -> dict            # distribution
def main() -> None                                        # writes json + md
```

### HUD re-scoring shim
```python
class _Scenario:  # reads only the attributes score_plan / failed_checks touch
    correct_fix_tools: set
    fault_node: str
    trap_actions: list[dict]
    gold_root_description: str
    red_herring_hints: list
    category: str
# built from the captured scenario["..."] flattened fields.
```
`score, _ = rex.scoring.score_plan(plan, _Scenario(...), sim_result)` and
`fc = rex.scoring.failed_checks(plan, _Scenario(...), sim_result)`.
Judge runs in deterministic mode (no network).

## Report JSON contract
```json
{
  "corpus": {"probe": <n>, "hud": <n>, "total": <n>},
  "failure_tail": {"n_failed": <n>, "n_clean_win": <n>, "n_zero_reward": <n>},
  "primary_bucket_counts": {"trap_taken": k, "wrong_root_cause": k, ...},
  "primary_bucket_pct": {...},
  "tag_counts": {...},
  "by_scenario": {"<scn>": {"n": k, "failed": k, "buckets": {...}}},
  "caveat": "small-N error analysis; counts are over this corpus only",
  "examples": [{"rollout_id":..., "bucket":..., "root_cause_excerpt":...}, ...]
}
```

## Test cases
1. `bucket()` precedence: trap+root_cause → trap_taken.
2. `bucket()` no_fix only → no_fix, tag correct_fix_missing.
3. empty plan + no trap → tags include safe_abstain + empty_plan.
4. **Real-data fixture**: a hand-built (plan, scenario, sim_result) with a known trap →
   failed_checks contains "trap_action" (validates the rex.scoring replay path).
5. Smoke: `load_probe_rollouts` on the real oom probe file returns 6 rollouts and the
   recomputed `failed_checks` equals the stored `failed_checks` for each row.
