# 05 — Ouroboros (self-critique as 3 different engineers)

## Engineer A — Data integrity reviewer
**Problems found:**
1. `opensre-qwen3-8b` and `opensre-qwen3-8b-v2` share the SAME slug (`opensre-qwen3-8b-1e439a`)
   — they're two *runs* of one forked model, not two models. Is that a duplicate-id violation?
2. Frontier means are attached to eval models but `grok-4.3` was in the ROSTER yet NOT in the
   frontier run — risk of silently dropping it or faking a number.
3. `eval_pass_at_1` null everywhere may read as "registry has no eval data," und_selling it.

**Resolutions:** (1) keep both rows — `id` is the registry key and is unique; the shared `slug`
is correct and honest (same forked model, different training config v1 vs v2). Documented in
`source`. (2) grok-4.3 kept with frontier fields = null + a `source` note "not in frontier run."
(3) acceptable — the real signal lives in the frontier_* columns; a `notes` entry states pass@1
was never measured per-model. Honesty > looking full.

## Engineer B — CLI/UX reviewer
**Problems found:**
1. `--status` should accept multiple (e.g. `flat,aborted`) — single value is too rigid.
2. `show` only matching `id` would miss the common case of pasting a raw slug.
3. `list` with zero matches returning exit 0 vs `query` returning exit 2 is inconsistent —
   is that a bug?

**Resolutions:** (1) `--status` parses CSV via `_csv()`. (2) `cmd_show` matches id OR slug.
(3) intentional, not a bug: `list` is a browse command (empty = valid view, exit 0); `query`
is a lookup assertion (no match = failure, exit 2). Documented in spec API contract.

## Engineer C — Maintainability / scope reviewer
**Problems found:**
1. The registry hand-codes numbers that live in `frontier.json` / `runs/*.jsonl` — drift risk
   if those files change.
2. Is a bespoke CLI over-engineering vs `jq`?
3. `generated_at` is hand-set, not derived — could go stale.

**Resolutions:** (1) acknowledged real weakness — each numeric row carries a `source` pointer so
a future `--refresh` could re-derive it; for now the values are a verified snapshot (see 09 for
the limitation). (2) justified: the CLI adds the role/status filters, slug-or-id lookup, and the
train-delta stats view that `jq` one-liners don't give cheaply; still zero-dependency. (3) minor;
`generated_at` is a snapshot date, documented as such.

## Final filtered spec delta
- `--status` is CSV. `show` resolves id-or-slug. list/query exit-code split is intentional and
  documented. Shared-slug rows are legal (unique id). All numbers carry `source`. Snapshot
  semantics + future `--refresh` hook noted as known limitation, not silently ignored.
