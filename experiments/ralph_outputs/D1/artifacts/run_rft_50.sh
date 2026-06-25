#!/usr/bin/env bash
# D1 — 50-step RFT launcher (Ralph Loop task D1).
# Extends the opensre RFT run from 15-25 steps to 50+ to test whether the
# observed +0.037 mean-reward trend (train_qwen3-8b_v2.jsonl: 0.504 -> 0.541
# over 15 steps; OLS slope +0.00174/step) continues.
#
# Grounds entirely in the existing, unmodified launcher:
#   opensre-traj/train_rft_v2.py  (hud_env_v2.py, P0 deterministic mechanism reward)
# This wrapper only sets steps>=50 and a fresh out-path. It edits NO core file.
#
# COMPUTE NOTE: real GRPO needs the HUD/Tinker GPU backend and is slow
# (~30-60s/step rollouts + forward/backward, plus transient 5xx retries).
# 50 steps * group 6 * 10 tasks can take 30-90 min — well past the 15-min cap.
# Run this UNATTENDED / in background. Resume-safe: out-file is append-only JSONL.
set -euo pipefail

cd "$(dirname "$0")/../../../../opensre-traj"   # -> /Users/mei/rl/opensre-traj
set -a; source ~/.zshrc 2>/dev/null || true; set +a   # HUD_API_KEY

MODEL="${MODEL:-opensre-qwen3-8b-1e439a}"   # forked trainable Qwen3-8B slug
STEPS="${STEPS:-50}"
GROUP="${GROUP:-6}"
LR="${LR:-1e-5}"                            # keep == v2 run so the curve is comparable
TASKS="${TASKS:-0,1,2,3,4,5,6,7,8,9}"       # same 10-task v2 set
OUT="${OUT:-runs/train_qwen3-8b_v2_50step.jsonl}"

echo "D1 50-step RFT: model=$MODEL steps=$STEPS group=$GROUP lr=$LR tasks=$TASKS out=$OUT"
exec ../.venv-hud/bin/python train_rft_v2.py \
  --model "$MODEL" --tasks "$TASKS" --group "$GROUP" \
  --steps "$STEPS" --lr "$LR" --out "$OUT"
