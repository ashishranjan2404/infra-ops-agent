# 04 — Technical Spec

## Data structure: `model_registry.json`
Top-level object:
```
{
  schema_version: "1.0",
  generated_by, generated_at, description: str,
  fields: { <field>: <doc string> },      # self-documenting
  models: [ ModelRow, ... ],
  notes: [ str, ... ]
}
```

### ModelRow
| field                    | type           | meaning |
|--------------------------|----------------|---------|
| id                       | str (unique)   | registry key |
| slug                     | str            | actual invoke/fork slug |
| base                     | str            | base family, or "self" for foundation eval models |
| provider                 | str            | anthropic \| fireworks \| gateway \| hud-tinker |
| role                     | "eval"\|"trainable" | |
| anchor                   | str\|null      | strong\|mid\|weak (eval spanning-set) |
| training_status          | str            | frozen\|forked\|trained\|flat\|aborted |
| eval_pass_at_1           | float\|null    | measured pass@1 or null |
| frontier_baseline_mean   | float\|null    | zero-shot mean reward (rex/runs/frontier.json) |
| frontier_rex_mean        | float\|null    | REx-tree mean reward (same source) |
| train_mean_reward_start  | float\|null    | GRPO step-0 mean reward |
| train_mean_reward_end    | float\|null    | GRPO last-step mean reward |
| source                   | str            | provenance: repo file(s)/line(s) |

Invariants: `id` unique; `role` in {eval,trainable}; every row has all fields (null allowed).

## CLI: `model_registry.py`
Signatures:
- `load(path) -> dict`
- `cmd_list(reg, args) -> int` — filters: --role --status(csv) --provider --base; --json
- `cmd_show(reg, args) -> int` — lookup by id OR slug; missing -> exit 2
- `cmd_query(reg, args) -> int` — same filters as list, terse output; no match -> exit 2
- `cmd_stats(reg, args) -> int` — counts by role/status/provider + train start→end deltas
- `main(argv=None) -> int`

### API contract (exit codes)
- 0: success (incl. list with 0 matches)
- 2: show id not found / query no matches / argparse error

## Test cases (test_model_registry.py)
1. JSON parses; every row has the required field set; ids unique; role valid.
2. Known real refs present: claude-opus-4-8, glm-5p2, opensre-qwen3-8b, opensre-qwen3-30b.
3. CLI `list` shows opus; `list --role trainable` shows qwen, hides opus.
4. CLI `show <slug>` resolves by slug; `show <missing>` -> exit 2.
5. CLI `stats` reports total=11 and the real `0.5220 -> 0.4910` 8b delta.

## File formats
JSON (UTF-8, 2-space indent). CLI human table + `--json` for machine use.
