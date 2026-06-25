# D2 — 04 Spec

## Artifacts
1. `artifacts/train_rft_qwen14b.py` — RFT launcher.
2. `artifacts/qwen14b_train.config.yaml` — canonical flags + blocker record.
3. `artifacts/runs/` — JSONL output dir (only populated by a real run).

## `train_rft_qwen14b.py` — function signatures
```python
DEFAULT_BASE = "Qwen/Qwen3.6-27B"
PREFERRED_BASES = ["Qwen/Qwen3.6-27B", "Qwen/Qwen3-30B-A3B", "Qwen/Qwen3.5-4B"]

def _cli_models_raw() -> str          # shell `hud models list` (COLUMNS=400), return stdout+stderr
def preflight(requested_base: str|None) -> int
    # prints trainable Qwen bases; reports 14B presence (excluding A17B false-positive);
    # returns 0 iff requested_base is present & trainable, else 2.
async def _run_training(args) -> int  # cd opensre-traj; import train_rft_v2; return v2.run(args)
def main() -> int                     # argparse; --preflight short-circuits; else preflight-guard then run
```

## CLI contract
```
--model MODEL        forked trainable slug (required for smoke/real run)
--base BASE          base to verify/fork  (default Qwen/Qwen3.6-27B)
--preflight          list trainable Qwen bases + verify --base; exit
--tasks  "0,..,9"    0-based task indices (default 10 tasks)
--group  6           GRPO group size
--steps  30
--lr     1e-5
--reset-head         roll head back before step 0 (passed through to v2)
--out    PATH        JSONL log
--smoke              1-step fail-fast
```
`args` is shaped to match exactly what `train_rft_v2.run(args)` reads:
`.model .tasks .group .steps .lr .reset_head .out .smoke` — so delegation is a no-glue call.

## Exit codes
- `0` preflight pass / training completed.
- `2` base not trainable on gateway, or `--model` missing on a run. (Loud, not silent.)

## Test cases
| # | Command | Expected |
|---|---------|----------|
| T1 | `python -m py_compile train_rft_qwen14b.py` | compiles |
| T2 | `python train_rft_qwen14b.py --help` | argparse usage, no network |
| T3 | `yaml.safe_load(config)` | dict; `model.available == False`, `model.requested == Qwen/Qwen3-14B` |
| T4 | `.venv-hud/bin/python … --preflight` (default base) | lists bases; "14B present: False"; "Qwen3.6-27B present: True"; exit 0 |
| T5 | `… --preflight --base Qwen/Qwen3-14B` | "present: False"; exit 2 |
| T6 | `… --base Qwen/Qwen3-14B --model x` (no smoke) | preflight-guard aborts, exit 2, prints BLOCKER |

## File formats
- YAML: keys `task_id, purpose, backend, model, env, train, success_criteria, compute_note`.
- Run JSONL (when a real run executes), inherited from v2:
  `{"step","mean_reward","reward_std","n","rewards":[...],"loss"}` per line.

## API contract (delegation)
The launcher does NOT reimplement Job/Taskset/TrainingClient. It calls
`train_rft_v2.run(args)`, which: `Taskset.from_module("hud_env_v2.py")` → select task idx →
`create_agent(model)` → `TrainingClient(model)` → optional `reset-head` → `Job.start` →
loop[steps]: `ts.run` → rewards → `trainer.step(lr, group_size)` → append JSONL.
