# 06 — Implementation

## What I built (all under `experiments/ralph_outputs/H4/artifacts/`)

### `exptrack.py` (226 lines, stdlib only)
The tracking shim. Key pieces:
- `select_backend()` — env-driven resolution (`EXPTRACK_BACKEND` auto|wandb|trackio|jsonl|
  none; `WANDB_DISABLED`); explicit cloud backends degrade to jsonl if the import fails.
- `init(project,name,config,directory) -> Run` — never raises; jsonl -> noop on any error.
- `JsonlRun` — **canonical** local backend. Typed lines (`_type` ∈ meta/metric/summary),
  auto-incrementing step, per-line `flush()` (tail-able), `_coerce_scalars` so any value is
  JSON-safe. Exposes `run.path`.
- `WandbRun` — one wrapper over both `wandb` and `trackio` (identical `.init/.log/.finish`).
- `NoopRun` — for `EXPTRACK_BACKEND=none`.
- `Run` is a context manager whose `__exit__` never suppresses caller exceptions.
- Every backend method is best-effort (try/except, swallow) per the PSRE never-page rule.

### `test_exptrack.py` (8 tests)
Covers backend selection, jsonl meta/metric/summary round-trip, auto-increment step,
non-scalar coercion, `none` no-op, log-after-finish safety, and the auto->jsonl fallback.
Runs under pytest AND as a standalone script.

### `INTEGRATION_GUIDE.md`
Exact call sites for the train loop (`opensre-traj/train_rft_v2.py`) and eval loop
(`rex/eval_pass_at_k.py`), plus the rationale for a shim over raw `wandb.init`.

### `train_rft_v2.exptrack.patch`
A real unified diff that adds `exptrack` to the train loop: one `init` after the log-dir
setup, one `track.log` per step mirroring the existing per-step `line` dict, and
`summary`+`finish` at the end. **Verified with `git apply --check` (see 07). NOT applied** —
the core file is left untouched per the parallel-safety rules.

## Core-file policy
No shared core file was edited. The train-loop change is delivered only as a patch; the
eval-loop change as a snippet in the guide. Verified `opensre-traj/train_rft_v2.py` remains
unmodified (`git status` shows it untracked with no diff).

## Live demo
Ran a 3-step jsonl run (`demo_runs/`) producing valid meta+3 metric+summary lines — see 07.
