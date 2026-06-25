#!/usr/bin/env bash
# serve_vllm.sh — launch a local vLLM OpenAI-compatible server for fast eval.
#
# Why: the pass@k ablation (rex/eval_pass_at_k.py) stalls on remote-API latency and
# rate limits. vLLM serves an OpenAI-compatible /v1/chat/completions endpoint locally
# with continuous batching, so N independent episodes hit a warm in-process model
# instead of paying per-request network + queueing overhead.
#
# Requires: a CUDA (or ROCm) GPU + `pip install vllm`. On a CPU-only / Apple-Silicon
# box this WILL NOT start a real server — see the dry-run note at the bottom and
# H1/07_test_results.md for the documented blocker. The client shim is validated
# independently against a mock endpoint.
#
# Usage:
#   ./serve_vllm.sh                       # defaults from config (Qwen2.5-1.5B-Instruct)
#   MODEL=Qwen/Qwen2.5-3B-Instruct ./serve_vllm.sh
#   PORT=8001 ./serve_vllm.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="${CONFIG:-$HERE/vllm_config.env}"
# shellcheck disable=SC1090
[ -f "$CONFIG" ] && set -a && . "$CONFIG" && set +a

# Defaults (overridable by env or vllm_config.env). A small model keeps VRAM low
# and is fine for an eval policy — the point is throughput, not frontier quality.
MODEL="${MODEL:-Qwen/Qwen2.5-1.5B-Instruct}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
SERVED_NAME="${SERVED_NAME:-vllm-local}"     # the `model` string clients send
MAX_LEN="${MAX_LEN:-8192}"
GPU_UTIL="${GPU_UTIL:-0.90}"
DTYPE="${DTYPE:-auto}"
API_KEY="${VLLM_API_KEY:-local-key}"          # vLLM accepts any bearer if --api-key set

echo "[serve_vllm] model=$MODEL served-as=$SERVED_NAME http://$HOST:$PORT/v1"

if ! python3 -c "import vllm" 2>/dev/null; then
  echo "[serve_vllm] ERROR: vllm not importable. Install on a GPU host: pip install vllm" >&2
  echo "[serve_vllm] (CPU/Apple-Silicon is unsupported by vLLM CUDA builds — see H1 blocker.)" >&2
  exit 3
fi

exec python3 -m vllm.entrypoints.openai.api_server \
  --model "$MODEL" \
  --served-model-name "$SERVED_NAME" \
  --host "$HOST" --port "$PORT" \
  --max-model-len "$MAX_LEN" \
  --gpu-memory-utilization "$GPU_UTIL" \
  --dtype "$DTYPE" \
  --api-key "$API_KEY"
