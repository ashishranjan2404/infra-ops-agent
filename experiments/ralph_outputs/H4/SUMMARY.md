# H4 — Experiment tracking shim — SUMMARY

**Task:** Set up W&B/Trackio experiment tracking for all runs: a lightweight logger that
wraps W&B (or Trackio) if available else falls back to local JSONL, an integration guide
showing where to call it in the eval/train loops (patch/snippet, not a core edit), and a
unit test of the fallback logger. Do not edit shared core files.

## Deliverables (all in `experiments/ralph_outputs/H4/artifacts/`)
- **`exptrack.py`** — 226-line stdlib-only shim. API: `init / log / summary / finish` +
  context manager. Backends: `wandb | trackio | jsonl | none`, env-selected
  (`EXPTRACK_BACKEND`, default `auto`; `WANDB_DISABLED`, `EXPTRACK_DIR`). JSONL is the
  canonical, typed (`_type` in meta/metric/summary), best-effort local record. All methods
  swallow backend errors so tracking can never crash a run.
- **`test_exptrack.py`** — 8 tests on the fallback + best-effort contract. Pass under
  pytest (8 passed in 0.21s) and as a standalone script (ALL PASS).
- **`INTEGRATION_GUIDE.md`** — exact call sites for the train loop
  (`opensre-traj/train_rft_v2.py`) and eval loop (`rex/eval_pass_at_k.py`), plus rationale.
- **`train_rft_v2.exptrack.patch`** — real unified diff for the train loop, verified with
  `git apply --check`. Not applied — core file left untouched.
- **`demo_runs/*.jsonl`** — a live 3-step demo run; every line parses as JSON.

## Result
All 5 success criteria met. wandb 0.27.2 is present so `auto` selects wandb; the fallback
(our real dependency in dep-free envs) is fully tested via `EXPTRACK_BACKEND=jsonl` /
`WANDB_DISABLED=true`. No shared core file edited (`opensre-traj/train_rft_v2.py` shows no
diff). Known gap: eval integration shipped as a precise snippet rather than a verified patch
because `out[cond]` keys are branch-dependent (documented in 09).

**Status: completed.**
