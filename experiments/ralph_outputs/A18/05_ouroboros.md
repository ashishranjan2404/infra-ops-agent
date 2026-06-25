# A18 — 05 Ouroboros (self-critique as 3 engineers)

## Engineer A — Data Engineer (correctness of the round-trip)
**Problems found:**
- A1. If the loader's `Features` typed `difficulty` as required but synthetic rows lack it,
  `load_dataset` raises on null. -> Must default-fill `difficulty=0`, `source_company=""`,
  `source_url=""`, `trap_actions=[]` for synthetic. (Fixed in `_generate_examples`.)
- A2. JSON re-serialization could mangle non-ASCII (the answers contain `—` etc.). -> Write shards
  with `ensure_ascii=False` and read/validate by parsing, not string compare. (Fixed.)
- A3. Validator reads the *original* JSONL, not the staged shards — it could pass while the staged
  package is broken. -> Mitigated by T2: load the *staged* dir with `datasets` (proves shards parse).

## Engineer B — Release Engineer (Hub mechanics)
**Problems found:**
- B1. The card's `configs:` for `synthetic`/`real` point at `synthetic/*.jsonl` / `real/*.jsonl`; if the
  push only uploads the root file those globs resolve to nothing -> empty config. -> `build_package`
  creates the shards; verified by hub `dataset_info` listing them.
- B2. `dataset_info:` with a feature list that disagrees with the loader's `Features` triggers a Hub card
  warning. -> Keep the card's `all` feature list byte-aligned with the loader. (Manually mirrored;
  validator checks the counts, the load test exercises the types.)
- B3. Re-running the push must not duplicate/fail. -> `create_repo(exist_ok=True)` + `upload_folder`
  (idempotent overwrite). Confirmed.

## Engineer C — Skeptical Reviewer (scope / honesty)
**Problems found:**
- C1. Over-engineering risk: both a loading script AND `dataset_info` — redundant. -> Justified
  (grill R2): redundancy is deliberate resilience to the Hub's script sandbox. Documented.
- C2. Under-tested edge: what if `datasets` isn't installed in the consumer env? The *card* path
  (bare JSONL + `configs:`) still works without the script. Good — that's the fallback.
- C3. Honesty: don't claim the push happened unless it actually did. -> The verification + result.json
  report the ACTUAL push outcome (succeeded with present credentials) vs. the dry-run fallback.

## Final filtered spec (deltas applied)
- Default-fill all real-only fields for synthetic (A1).
- `ensure_ascii=False` on all writes; parse-based validation (A2).
- T2 loads the *staged* package, not just the source, to catch shard breakage (A3).
- Shards built in `build_package`; hub `dataset_info` asserted to list them (B1).
- Card `all` features mirror the loader `Features`; load test exercises types (B2).
- `exist_ok=True` idempotent push (B3).
- Keep dual config resolution (C1) with documented rationale; report real push outcome honestly (C3).
