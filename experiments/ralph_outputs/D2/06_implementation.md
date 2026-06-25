# D2 — 06 Implementation

## What I built (real, task-namespaced artifacts)

### 1. `artifacts/train_rft_qwen14b.py`  (RFT launcher, ~150 LOC)
Thin **additive** wrapper over the proven core trainer `opensre-traj/train_rft_v2.py`.
- `preflight(base)` — shells `hud models list` (COLUMNS=400 for un-wrapped rows), enumerates
  trainable Qwen Tinker bases, reports whether Qwen-14B (dense) exists (excluding the `A17B`
  false-positive), and verifies the requested `--base` is present & trainable. Returns 0/2.
- `_run_training(args)` — `cd`s into `opensre-traj`, imports `train_rft_v2`, and delegates to
  `v2.run(args)`. The `args` namespace is shaped to exactly the attributes v2 reads.
- `main()` — argparse; `--preflight` short-circuits; otherwise a preflight-guard aborts a real
  run against a missing base before any paid call.
- **Does NOT edit any shared core file.** It imports `train_rft_v2`; the trainer is untouched.

### 2. `artifacts/qwen14b_train.config.yaml`
Canonical flag set + the documented blocker (`model.requested=Qwen/Qwen3-14B`,
`model.available=false`, substitute=`Qwen/Qwen3.6-27B`, MoE alt=`Qwen/Qwen3-30B-A3B`), env
(`hud_env_v2.py`), train hyperparams (10 tasks, group 6, 30 steps, lr 1e-5, reset_head),
success criteria, and an explicit compute note.

### 3. `artifacts/runs/`
Output dir for `train_qwen14b_v2.jsonl`. Empty — no real training run was executed (see 07/09).

## Grounding
- Reused `train_rft_v2.py` verbatim (its GRPO loop, 5xx retry, within-group spread logging,
  `--reset-head`). The 8B baseline that motivated this (`runs/train_qwen3-8b_v2.jsonl`:
  0.50→0.54 over 15 steps) is the comparison target.

## Key real finding (drove the design)
`hud models list` (executed live, HUD_API_KEY present) exposes NO Qwen-14B on the Tinker
provider. Trainable Qwen bases observed:
`opensre-qwen3-8b`, `opensre-qwen3-30b`, `Qwen/Qwen3-8B`, `Qwen/Qwen3-30B-A3B`,
`Qwen/Qwen3.5-4B`, `Qwen/Qwen3.6-27B`, `Qwen/Qwen3.6-35B-A3B`, `Qwen/Qwen3.5-397B-A17B(:peft)`,
`Qwen/Qwen3-235B-A22B-Instruct-2507`. → No 14B rung exists; the design pivots to a verified
substitute + loud preflight.

## Proposed core change (NOT applied — parallel safety)
`train_rft_v2.py`'s `--reset-head` swallows exceptions and continues from an undefined head if
`trainer.checkpoints()` is empty. For a freshly forked base that is unsafe. Proposed fix
(documented only, not applied): make reset-head abort the run if no base checkpoint is found.
Left as a follow-up to avoid editing a shared core file mid-Ralph-run.
