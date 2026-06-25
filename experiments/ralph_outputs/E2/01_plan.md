# 01 — Plan (Task E2: FIREBALL D&D trajectory dataset)

## Objective
Acquire the FIREBALL D&D trajectory dataset, document its schema, and provide a
converter into our trajectory format. Attempt a real fetch; if blocked by
auth/size, document the blocker and validate the converter on a synthetic
fixture. Do NOT fabricate the real dataset.

## What FIREBALL is
FIREBALL (Zhu et al., "FIREBALL: A Dataset of Dungeons and Dragons Actual-Play
with Structured Game State Information", ACL 2023, arXiv:2305.01528). ~25k Discord
D&D combat sessions captured via the Avrae bot, with structured game state. On
the Hub as **lara-martin/FIREBALL** (CC-BY-4.0). Each record is a combat turn:
narration + state *before*, normalized Avrae commands, bot automation output, and
narration + state *after* — i.e. a (state, action, result, next_state) tuple.

## Approach
1. `fireball_fetch.py` — HuggingFace `huggingface_hub` fetcher. Lists the
   `filtered/*.jsonl` shards; downloads N shards by default (`--all` for full).
2. `fireball_schema.py` — schema captured from a REAL sample + `validate_row`.
3. `fireball_convert.py` — maps a FIREBALL turn to our flat trajectory record
   (observation / actions / tools_used / result / target / next_observation).
4. `fireball_fixture.jsonl` — tiny SYNTHETIC, schema-matching fixture (clearly
   fake content) to validate the converter hermetically.
5. `test_fireball_convert.py` — pytest over the fixture + the real shard.

## Files to create (all task-namespaced, no shared-core edits)
- `experiments/ralph_outputs/E2/artifacts/fireball_fetch.py`
- `.../fireball_schema.py`
- `.../fireball_convert.py`
- `.../fireball_fixture.jsonl`
- `.../test_fireball_convert.py`

## Dependencies
`huggingface_hub` (present, v1.11.0). Network access for the live fetch (optional
for converter validation).

## Risks
- Dataset is large (1475 shards, 100K–1M rows) → only fetch a few shards.
- Schema drift between shards → `validate_row` fails loudly.
- "incidents.jsonl" name in the task does not exist literally; FIREBALL ships as
  `filtered/*.jsonl`. Documented, not faked.

## Success criteria
- Real fetch attempted and either succeeds (≥1 shard) or has a documented blocker.
- Schema documented from a REAL sample.
- Converter runs on the fixture AND a real shard, producing valid trajectory JSON.
- pytest green.
