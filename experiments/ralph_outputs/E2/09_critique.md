# 09 — Critique (honest)

## What's strong
- Real fetch, not faked: dataset located, license/gating verified, a real shard
  downloaded, real schema captured, converter validated on real rows.
- Clean separation of action (`commands_norm`) vs. convenience verb view.
- Streaming converter won't OOM on large shards; loud schema validation.
- 7 passing tests, fixture clearly synthetic.

## What a reviewer attacks
1. **Only one shard downloaded.** "You validated on 1/1471 shards." True — the
   converter is shard-agnostic and `validate_row` guards drift, but I have not
   proven every shard conforms. A real run would `--all` and assert row counts.
2. **No semantic check on the trajectory's usefulness.** I mapped fields, but did
   not show that an agent trained on `(observation → target)` learns anything.
   This task was acquisition + conversion, not training — but the value claim is
   unproven downstream.
3. **trace_id cross-shard collision** (P1 in ouroboros) is possible, if rare.
4. **`tools_used` dedupe vs `n_tool_calls`** could mislead a careless reader.
   Documented + tested, but it's a footgun.
5. **Domain mismatch.** FIREBALL is D&D, not SRE. I argue it's a generic
   trajectory substrate, but a skeptic could say it's a distraction from the
   SRE-Degrees thesis. Reasonable critique; the deliverable is the converter +
   schema, which is reusable regardless.
6. **Symlink-based fetch** isn't portable to no-symlink filesystems; copy fallback
   would be more robust.

## Blocked / not done (honest)
- Full dataset NOT downloaded (size, by design). `--all` provided, untested at scale.
- No checksum/row-count post-fetch assertion.
- No integration into `rex/scoring.py` or any training loop (out of scope, and
  shared-core edits are forbidden for this worker).

## Net
Solid, real, reproducible acquisition + conversion deliverable with honest scope
limits. Not a training result, and not a full-dataset pull — and it doesn't claim
to be.
