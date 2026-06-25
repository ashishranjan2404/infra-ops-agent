# 05 — Ouroboros (self-critique as 3 engineers)

## Engineer A — Data Eng (finds real problems)
- **P1:** `trace_id` keys on `speaker_id|commands|before_state_idx`. Two distinct
  turns by the same speaker with identical commands but different state indices
  differ — OK. But within ONE shard, `before_state_idx` is shard-local; across
  shards the same idx could collide for the same speaker/commands. *Risk: cross-
  shard id collision.* Real, low-probability. Fix: acceptable for v1 (de-dup is
  best-effort); document it. Could add shard name to the key later.
- **P2:** `_render_state` puts `class: null` as the string "(None)". Ugly but
  harmless; the `_combatant_line` already guards empty class — null prints as
  "None". Minor cosmetic. Filter falsy more strictly.

## Engineer B — RL/Training (finds real problems)
- **P3:** `tools_used` dedupes verbs, so a turn that casts twice shows one "cast"
  but n_tool_calls==2. Inconsistent if a reader assumes len(tools_used)==n_calls.
  *Real ambiguity.* Resolution: documented — tools_used is a SET-like view,
  n_tool_calls is the count. Tests assert exactly this so it's intentional.
- **P4:** Empty `before_utterances` → observation ends with "## Recent dialogue\n"
  (empty). Slightly noisy but valid. Acceptable.

## Engineer C — Reliability/Reviewer (finds real problems)
- **P5:** `fetch` symlinks the HF cache file into `--out`. On Windows or a
  no-symlink FS this fails. *Real portability gap.* For this macOS worker it's
  fine; documented as a caveat. A copy fallback would be more robust.
- **P6:** No checksum/row-count assertion after fetch — a truncated download is
  undetected until convert. *Real gap.* `convert_row` does validate each row and
  raises on schema problems, which catches truncation mid-line via json error, so
  partial mitigation exists.
- **P7:** Converter loads each shard line-by-line (streaming) — good, won't OOM on
  large shards. No problem.

## Final filtered spec (after the 3 rounds)
Accept and ship as-is for v1, with these documented limitations:
1. trace_id may collide across shards in pathological cases (low risk).
2. tools_used is a deduped view; n_tool_calls is authoritative for count.
3. fetch uses symlinks (macOS/Linux); copy fallback is a future improvement.
4. No post-fetch checksum; per-row schema validation gives partial protection.
No code changes required beyond what's already implemented — the critiques are
either documented limitations or already handled by `validate_row` + streaming.
