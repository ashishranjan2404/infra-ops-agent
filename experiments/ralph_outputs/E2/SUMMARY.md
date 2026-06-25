# E2 — FIREBALL D&D trajectory dataset: SUMMARY

**Task:** Get the FIREBALL D&D trajectory dataset; deliver a fetch script, the
expected schema, and a converter to our trajectory format. Attempt the fetch;
document any blocker; validate the converter (synthetic fixture if needed).
Do not fabricate the real dataset.

## Result: COMPLETED (real fetch succeeded)
FIREBALL = Zhu et al., ACL 2023, arXiv:2305.01528. On the Hub as
**lara-martin/FIREBALL** — public, non-gated, CC-BY-4.0, 1471 filtered/*.jsonl
shards (100K-1M rows). One real shard (1.7 MB, 111 turns) was downloaded; its
real 17-key schema captured; converter validated on it -> 49 trajectory records.

## Deliverables (experiments/ralph_outputs/E2/artifacts/)
- fireball_fetch.py    — huggingface_hub fetcher (--shards N / --all).
- fireball_schema.py   — real schema + validate_row.
- fireball_convert.py  — FIREBALL turn -> fireball-traj-v1 record.
- fireball_fixture.jsonl — 3 SYNTHETIC (SYNTH_*) schema-matching rows.
- test_fireball_convert.py — 7 pytest cases, all passing.

## Mapping
observation <- before_utterances + combat_state_before; actions <- commands_norm;
tools_used <- command verbs; result <- automation_results; target <-
after_utterances; next_observation <- combat_state_after.

## Validation
- pytest: 7/7 passed.
- Real shard: 111 raw turns -> 49 records, all targets non-empty, all JSON-serializable.
- Fixture: 3 rows -> 2 records (1 skipped: empty target).

## Honest limits
Only 1/1471 shards downloaded (full pull is --all, by design not run). No
downstream training. "incidents.jsonl" literal filename doesn't exist; FIREBALL
ships as shards — treated each line as one record. No shared-core files edited.
