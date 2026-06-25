# 08 — Verification against success criteria

| Criterion (from 01) | Status | Evidence |
|---|---|---|
| Real fetch attempted | ✅ | searched Hub, `dataset_info`, downloaded 1 real shard (1.7 MB, 111 rows) |
| Fetch succeeds or documented blocker | ✅ succeeded | `fireball_fetch.py`; 1471 shards listed; `--all` opt-in |
| Schema documented from REAL sample | ✅ | `fireball_schema.py` (17 keys, real line 0) |
| Converter to our trajectory format | ✅ | `fireball_convert.py` → `fireball-traj-v1` |
| Converter runs on real data | ✅ | 111 raw → 49 records, all targets non-empty, all serializable |
| Converter runs on synthetic fixture | ✅ | 3 rows → 2 records (1 skipped, empty target) |
| pytest green | ✅ | 7/7 passed |
| Did NOT fabricate real dataset | ✅ | fixture rows are `SYNTH_*`, clearly fake; real rows only from HF |
| No shared-core edits | ✅ | all files under `E2/artifacts/`; no `rex/ sim/ agent/ experiments/*.py` touched |

## Outputs are real, not placeholder
- `fireball_fetch.py` actually downloads from the Hub (verified, file in HF cache).
- Schema copied from a real downloaded row, not invented.
- Converter exercised on the real shard, producing 49 real records.
- Tests run and pass (7/7), including against the real shard implicitly via the
  same `convert_row` path.

## Caveat (honest)
"incidents.jsonl" as a literal filename does not exist in FIREBALL; the dataset
ships as `filtered/*.jsonl` shards. We treat each shard line as one record and say
so. Full dataset acquisition (all 1471 shards, 100K–1M rows) was NOT performed in
this worker by design (size); `--all` is provided and documented for that.

Verdict: **success criteria met.**
