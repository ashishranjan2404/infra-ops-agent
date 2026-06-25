# 06 — Implementation

All artifacts under `experiments/ralph_outputs/E2/artifacts/` (task-namespaced;
no shared-core files touched).

## Artifacts built
1. **`fireball_fetch.py`** — `huggingface_hub` fetcher for `lara-martin/FIREBALL`.
   Lists `filtered/*.jsonl` shards; downloads N (`--shards`, default 1) or all
   (`--all`). CLI: `python fireball_fetch.py --shards 1 --out data/fireball_raw`.
2. **`fireball_schema.py`** — schema captured from a REAL sample (line 0 of shard
   `00068c6b...jsonl`), with `REQUIRED_KEYS`, `COMBATANT_KEYS`, and `validate_row`.
3. **`fireball_convert.py`** — `convert_row` / `convert_file` mapping a FIREBALL
   turn → `fireball-traj-v1` record (observation / actions / tools_used /
   n_tool_calls / result / target / next_observation / provenance). Streams
   shards line-by-line; skips empty action/target rows unless `--keep-empty`.
4. **`fireball_fixture.jsonl`** — 3 SYNTHETIC rows (`SYNTH_0001..0003`) matching
   the real 17-key schema; row 3 has empty `after_utterances` to exercise the
   skip path. Clearly fabricated content — does NOT impersonate real data.
5. **`test_fireball_convert.py`** — 7 pytest cases (validate, convert, multi-cmd,
   trace_id, skip-empty, invalid-raises, json-serializable).

## Real fetch performed
- Searched the Hub → found `lara-martin/FIREBALL` (public, non-gated, CC-BY-4.0).
- `dataset_info` + `list_repo_files`: 1475 files, 1473 `filtered/*.jsonl` shards.
- Downloaded ONE real shard (`00068c6b03adc2c102756053cf6edd05.jsonl`, 1.7 MB,
  111 turn rows) and captured its real schema.
- Ran the converter on that REAL shard → 49 usable trajectory records.

## Mapping rationale (FIREBALL turn → our trajectory)
| our field | FIREBALL source |
|---|---|
| observation | before_utterances + combat_state_before |
| actions | commands_norm (full Avrae commands) |
| tools_used | deduped command verbs |
| result | automation_results |
| target | after_utterances (gold continuation) |
| next_observation | combat_state_after |

## Note on shared-core
The task names "incidents.jsonl" but FIREBALL has no such file; it ships as
`filtered/*.jsonl` shards. No shared core file (`rex/*`, `sim/*`, `agent/*`,
`experiments/*.py`) was created or edited. Output trajectory format mirrors
`opensre-traj/out/hud_trajectories.jsonl` conventions (flat per-line JSON with
trace_id / scenario_id / tools_used / n_tool_calls) without importing it.
