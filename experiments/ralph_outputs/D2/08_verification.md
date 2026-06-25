# D2 — 08 Verification

## Against the success criteria (from 01_plan.md)

1. **Launcher compiles, `--help` works, YAML parses** — ✅ T1/T2/T3 all PASS.
2. **`--preflight` hits the real gateway, reports 14B availability, verifies chosen base** —
   ✅ T4 returns exit 0 (substitute trainable), T5 returns exit 2 (14B absent). Output is
   from the live HUD Tinker gateway, not mocked.
3. **Launcher imports core trainer without modifying any shared core file** — ✅ It imports
   `train_rft_v2`; `git status` shows no modification to `opensre-traj/train_rft*.py` or any
   `rex/ sim/ agent/ experiments/*.py`. All new files are under `D2/artifacts/`.
4. **Blocker documented, zero fabricated metrics** — ✅ `runs/` empty; `result.json` carries
   no training numbers; the blocker is the literal gateway output.

## Are the outputs real (not placeholder)?
- `train_rft_qwen14b.py` is a runnable program that executed against the live gateway and
  returned correct, distinct exit codes for 4 scenarios. Not a stub.
- `qwen14b_train.config.yaml` parses to a real dict with the actual blocker recorded.
- The preflight table is verbatim live gateway data (matches `hud models list`).

## Honest scope boundary
The deliverable is **launcher + config + verified preflight + documented blocker** — exactly
what the brief asks for when a real 14B/long-GPU run isn't reachable. It is NOT a trained
Qwen-14B model and does NOT claim a training curve. The substitute (Qwen3.6-27B) is verified
*trainable* but was *not trained* (compute cap + it is not literally 14B).

## Reproduce
```
cd experiments/ralph_outputs/D2/artifacts
set -a; source ~/.zshrc; set +a
/Users/mei/rl/.venv-hud/bin/python train_rft_qwen14b.py --preflight   # exit 0
/Users/mei/rl/.venv-hud/bin/python train_rft_qwen14b.py --preflight --base Qwen/Qwen3-14B  # exit 2
```
