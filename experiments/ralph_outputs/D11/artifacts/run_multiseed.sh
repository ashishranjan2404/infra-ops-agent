#!/usr/bin/env bash
# D11 — Multi-seed GRPO driver for the opensre RFT run.
#
# Launches the SAME (model, tasks, group, steps, lr) config under N seeds, writing
# one log per seed, so seed_variance.py --seed-group can compute a real across-seed CI.
#
# PREREQUISITE: apply add_seed_patch.diff to train_rft_v2.py first:
#     git apply experiments/ralph_outputs/D11/artifacts/add_seed_patch.diff
#
# BLOCKER (documented): each seed is ~STEPS forward/backward steps on the HUD Tinker
# GPU backend and requires HUD_API_KEY + a forked trainable model slug. This cannot
# run inside the offline Ralph worker. Cost ~ N_SEEDS * STEPS * group rollouts of paid
# GPU time. Run this on the HUD-enabled box (../.venv-hud), in the background.
set -euo pipefail

MODEL="${MODEL:?set MODEL to a forked trainable slug, e.g. opensre-qwen3-8b-1e439a}"
TASKS="${TASKS:-0,1,2,3,4,5,6,7,8,9}"
GROUP="${GROUP:-6}"
STEPS="${STEPS:-30}"
LR="${LR:-1e-5}"
SEEDS="${SEEDS:-0 1 2 3 4}"
OUTDIR="${OUTDIR:-runs/seeds}"

cd "$(dirname "$0")/../../../../opensre-traj" 2>/dev/null || cd opensre-traj
mkdir -p "$OUTDIR"

for s in $SEEDS; do
  out="$OUTDIR/seed_${s}.jsonl"
  echo ">>> seed=$s -> $out"
  HUD_API_KEY="${HUD_API_KEY:?export HUD_API_KEY}" \
    ../.venv-hud/bin/python train_rft_v2.py \
      --model "$MODEL" --tasks "$TASKS" --group "$GROUP" \
      --steps "$STEPS" --lr "$LR" --seed "$s" --out "$out"
done

echo ">>> all seeds done. Analyze with:"
echo "python3 ../experiments/ralph_outputs/D11/artifacts/seed_variance.py \\"
echo "    --logs '$OUTDIR/seed_*.jsonl' --seed-group '${MODEL}@${LR}' \\"
echo "    --out-json seed_ci.json --out-md seed_ci.md"
