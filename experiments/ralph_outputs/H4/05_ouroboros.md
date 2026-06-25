# 05 — Ouroboros (3 self-critiques in sequence)

## Engineer 1 — correctness / edge cases
- **Problem (real):** `log()` after `finish()` writes to a closed file handle and would
  raise `ValueError: I/O operation on closed file`. The "best-effort" promise is broken.
  -> FIX: wrap `_write` in try/except (added `test_log_never_raises_after_finish`).
- **Problem:** a metric value that's a numpy float or a dict would make `json.dumps` raise,
  killing the log line. -> FIX: `_coerce_scalars` stringifies non-JSON-able values; list/
  tuple kept only if `json.dumps` succeeds. Test added.
- **Problem:** explicit `EXPTRACK_BACKEND=wandb` on a box without wandb would crash.
  -> FIX: explicit wandb/trackio degrade to jsonl when the import returns None.

## Engineer 2 — API / integration ergonomics
- **Problem (real):** the original sketch had `init` returning different shapes per backend
  (raw wandb run vs a dict), so call sites would branch. -> FIX: all backends return a
  `Run` with identical methods; eval/train code is backend-agnostic.
- **Problem:** auto-step. If the train loop passes its own `step` AND the eval loop relies
  on auto-increment, mixing could desync. -> Resolved: `step=None` auto-increments; passing
  an explicit step also *sets* the internal counter, so a later `None` continues correctly.
  Verified in test 2 (explicit 0 then auto -> 1).
- **Over-engineering check:** I considered async flushing / buffering. Rejected — these are
  ≤30-step runs; a synchronous `flush()` per line is fine and makes the file tail-able live.

## Engineer 3 — reproducibility / "does the patch actually apply"
- **Problem (real):** a patch that doesn't apply is worthless. The first generated patch had
  a mangled `b/` prefix from a sed. -> FIX: regenerate, run `git apply --check`, confirm the
  core file stays untracked/unmodified. (Done in 07.)
- **Problem:** `run.path` for non-jsonl backends. A caller printing `run.path` for a wandb
  run gets `None` — documented, and `run.backend` distinguishes. Acceptable.
- **Gap:** the eval integration is a snippet, not a verified patch, because `out[cond]`'s
  exact keys differ across branches. Documented as a known limitation in 09 rather than
  shipping a patch that won't apply.

## Final filtered spec
No structural changes beyond the three fixes above (closed-file guard, scalar coercion,
explicit-backend degrade) — all already reflected in `04_spec.md` and implemented. The eval
side stays a snippet by design; the train side ships as a `git apply --check`-verified patch.
