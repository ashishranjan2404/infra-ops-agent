# 09 — Honest Critique

## What a reviewer will attack
1. **Snapshot, not derived (real weakness).** The numbers are hand-copied from `frontier.json`
   and `runs/*.jsonl`. If those files change, the registry silently drifts. The right fix is a
   `--refresh` subcommand that re-parses the source files. I designed the schema for it (every
   numeric row has a `source` pointer) but did not implement it — that's an honest gap.
2. **pass@1 is null everywhere.** A "track eval pass@1" goal is only half-delivered: the repo
   does not record per-model pass@1 for these exact ids, so I left it null rather than fabricate.
   Defensible, but it means the registry's pass@1 column is currently informational-only.
3. **Two rows share one slug** (opensre-qwen3-8b vs -v2). Some would call this modeling a *run*
   as a *model*. I argue the v1/v2 distinction (different judge + GRPO grouping, different
   outcome flat-vs-up) is exactly what a registry should disambiguate, and `id` stays unique.
4. **Small surface.** It's a flat JSON + a 150-line CLI. No web UI, no write/update path
   (read-only). For the task scope ("track + list/query") that's appropriate, not impressive.
5. **frontier means != pass@1.** I deliberately kept them in separate columns to avoid
   conflation, but a careless reader might still treat `frontier_rex_mean` as an accuracy. The
   `fields` block documents the distinction; could be more prominent.

## What's genuinely solid
- Zero fabricated numbers; every value has a repo `source` and the tests pin the real figures
  (`0.5220 -> 0.4910`, `total models: 11`) so drift breaks CI.
- Captures the actual research finding (8b training went *down*; 30B aborted on a Tinker 503),
  which a naive "all green" registry would have hidden.
- Dependency-free, passes under both a bare runner and pytest, touches no shared core file.

## Blocked / negative results (honest)
- Could not measure live pass@1 — no eval was run for these ids and the task is scoped to
  building the registry, not running new evals. Reported as null, not invented.
