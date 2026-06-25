# E7 — 04 Spec

## Data structures
```python
@dataclass
class CanonicalStep:
    t: int                       # 0-based contiguous index
    observation: str             # alert/room text
    available_actions: list[str] # tools / admissible commands (may be oracle handicap)
    action: str
    reward: float = 0.0

@dataclass
class CanonicalTrajectory:
    episode_id: str              # required, non-empty
    domain: str                  # textworld|jericho|alfworld|sre
    goal: str
    gold_target: str             # required, non-empty -> maps to gold_root
    distractors: list[str]       # -> red_herrings / trap_actions
    steps: list[CanonicalStep]
    solved: bool                 # -> fix_resolves
    final_answer: str            # -> stated_cause
    meta: dict
```

## Function signatures
```python
register(domain: str) -> Callable[[Adapter], Adapter]   # decorator
adapt(domain: str, raw: dict) -> CanonicalTrajectory     # validates
adapt_many(domain: str, raws: Iterable[dict]) -> list[CanonicalTrajectory]
registered_domains() -> list[str]

CanonicalTrajectory.actions -> list[str]                 # property
CanonicalTrajectory.to_sre_scoring_inputs() -> dict      # {stated_cause, gold_root, red_herrings}
CanonicalTrajectory.to_dict() -> dict                    # json-serializable
```

## Field mapping per domain (source loader → canonical)
| canonical | TextWorld | Jericho | ALFWorld | SRE/REx |
|---|---|---|---|---|
| episode_id | game_id | rom | task_id | scenario_id/trace_id |
| goal | objective | goal | task_desc | (fixed) |
| gold_target | walkthrough_goal | walkthrough_summary | expert_plan_summary | gold_root |
| distractors | losing_commands | dead_end_actions | irrelevant_objects | red_herrings |
| steps[].observation | feedback | observation | obs | "" |
| steps[].available_actions | admissible_commands | valid_actions | admissible_actions | tools_used |
| steps[].action | command | action | action | tool |
| solved | won | victory | goal_condition_success | reward>=0.5 |
| final_answer | agent_summary | agent_summary | agent_summary | answer |

## Validation contract (`_validate`)
- `episode_id` non-empty → else `ValueError`.
- `gold_target` non-empty → else `ValueError` (needed by judge).
- step `t` must equal its list index → else `ValueError`.
- `action not in available_actions` (when both present) → non-fatal warning in
  `meta["warnings"]` (captures the oracle-handicap ablation signal).
- unknown domain in `adapt` → `KeyError`.

## Integration contract with existing core (read-only)
`to_sre_scoring_inputs()` returns exactly the kwargs of
`rex.scoring.deterministic_judge(stated_cause, gold_root, red_herrings)` and
`rex.scoring.mechanism_score(...)`. No core file is modified.

## Test cases (pytest)
1. all 4 domains registered
2. each domain adapts to a valid `CanonicalTrajectory` (param)
3. step indices contiguous
4. `.actions` view correct
5. missing gold_target → `ValueError`
6. unknown domain → `KeyError`
7. `to_sre_scoring_inputs` shape == 3 expected keys
8. adapted **game** traj scored by REAL `deterministic_judge`/`mechanism_score`
9. distractors flow through as `red_herrings`

## File formats
- fixtures: JSON, top-level keys = domain → list of raw episodes.
- adapter: single-file stdlib module, no third-party imports.
