# 04 — Technical Spec

## Source dataset
- HF id: `lara-martin/FIREBALL`, repo_type `dataset`, CC-BY-4.0, non-gated.
- Layout: `FIREBALL.py` (loader), `README.md`, `files.txt`, and 1475
  `filtered/<sha>.jsonl` shards (100K–1M rows total).
- Paper: Zhu et al., ACL 2023, arXiv:2305.01528.

## FIREBALL row schema (REAL, 17 keys)
| key | type | role |
|---|---|---|
| speaker_id | str | actor (anon Discord id) |
| before_utterances | list[str] | pre-action chat |
| combat_state_before | list[dict] | OBSERVATION (combatant snapshots) |
| current_actor | dict\|None | whose turn |
| commands_norm | list[str] | ACTION (Avrae commands) |
| automation_results | list[str] | RESULT (bot resolution) |
| caster_after / targets_after | dict / list[dict] | post-action actor/targets |
| combat_state_after | list[dict] | NEXT OBSERVATION |
| after_utterances | list[str] | TARGET (gold narration) |
| utterance_history | list[str] | rolling dialogue context |
| *_idxs / *_state_idx | int / list[int] | provenance |

Combatant snapshot: `{name, hp:"<x/y HP; Status>", class, race, attacks, spells,
actions, effects, description, controller}`.

## Output trajectory record (`fireball-traj-v1`)
```json
{
  "schema": "fireball-traj-v1",
  "trace_id": "<sha1(speaker|commands|before_state_idx)>",
  "scenario_id": "fireball-<trace_id[:12]>",
  "source": "fireball",
  "speaker_id": "...",
  "observation": "## Combat state\\n<rendered>\\n\\n## Recent dialogue\\n...",
  "actions": ["!cast armor -t nim"],
  "tools_used": ["cast"],
  "n_tool_calls": 1,
  "result": "<automation_results joined>",
  "target": "<after_utterances joined>",
  "next_observation": "## Combat state\\n<rendered after>",
  "utterance_history": ["Player 1: ..."],
  "provenance": {"before_state_idx": int, "after_state_idx": int, "command_idxs": [int]}
}
```

## Function signatures
```python
# fireball_schema.py
REQUIRED_KEYS: tuple[str, ...]
COMBATANT_KEYS: tuple[str, ...]
def validate_row(row: dict) -> list[str]            # [] == valid

# fireball_convert.py
def make_trace_id(row: dict) -> str
def convert_row(row: dict, source: str = "fireball") -> dict   # raises ValueError
def convert_file(paths: Iterable[Path], skip_empty: bool = True) -> Iterator[dict]

# fireball_fetch.py
def list_shards(api) -> list[str]
def fetch(n_shards: int | None, out: Path, timeout: int = 60) -> list[Path]
```

## Test cases (pytest)
1. all fixture rows pass `validate_row` (== []).
2. `convert_row` basic fields: actions, tools_used==['attack'], result/target/obs.
3. multi-command row → deduped verb, n_tool_calls==2, full commands preserved.
4. trace_id deterministic + unique across fixture rows.
5. empty-target row skipped by default; kept with `skip_empty=False`.
6. invalid row (missing keys) → `ValueError("missing key ...")`.
7. every converted record is `json.dumps`-serializable.

## CLI contracts
- `fireball_fetch.py [--shards N | --all] --out DIR`
- `fireball_convert.py INPUTS... -o OUT [--keep-empty]`
