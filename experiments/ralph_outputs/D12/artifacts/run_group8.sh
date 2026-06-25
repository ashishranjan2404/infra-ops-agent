#!/usr/bin/env bash
# D12 — launch the group=8 RFT run from group8_config.yaml.
# Does NOT edit train_rft_v2.py; just invokes it with --group 8.
# Requires HUD_API_KEY + a forked trainable slug (closed models cannot be GRPO'd).
set -euo pipefail
cd "$(dirname "$0")/../../../../opensre-traj"   # -> /Users/mei/rl/opensre-traj

set -a; source ~/.zshrc 2>/dev/null || true; set +a

MODEL="${MODEL:-opensre-qwen3-8b}"
PY=../.venv-hud/bin/python

if [[ "${1:-}" == "--smoke" ]]; then
  exec "$PY" train_rft_v2.py --model "$MODEL" --tasks 0,1 --group 8 --steps 1 --smoke
fi

# real A/B run (background-able): group 8, same 10 tasks as the v2 baseline
exec "$PY" train_rft_v2.py \
  --model "$MODEL" \
  --tasks 0,1,2,3,4,5,6,7,8,9 \
  --group 8 \
  --steps 30 \
  --lr 1e-5 \
  --reset-head \
  --out runs/train_qwen3-8b_group8.jsonl
