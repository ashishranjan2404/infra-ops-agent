# 06 — Implementation

All artifacts live under `experiments/ralph_outputs/H1/artifacts/`. **No shared core
file was edited** — the native-provider change ships as a documented `.patch`.

## Artifacts built (real, validated)

### 1. `serve_vllm.sh` (executable)
Wraps `python3 -m vllm.entrypoints.openai.api_server` with a small pinned model
(`Qwen/Qwen2.5-1.5B-Instruct`), `--served-model-name vllm-local`, `--host/--port`,
`--max-model-len`, `--gpu-memory-utilization`, `--dtype`, `--api-key`. Sources
`vllm_config.env`. Guards on missing vllm: prints an install hint + the Apple-Silicon
caveat and `exit 3`. `exec`s the server in the foreground (PID-clean for systemd/supervisor).

### 2. `vllm_config.env`
Single source of truth, both shell-sourceable and python-parseable (`KEY=VALUE`, `#`
comments). Pins `MODEL`, `SERVED_NAME`, bind host/port/limits, and the client-side
`VLLM_BASE_URL` / `VLLM_MODEL` / `VLLM_API_KEY`.

### 3. `vllm_client.py` (the shim)
Drop-in for `agent.llm.call`. Public surface:
- `build_request(name, prompt, max_tokens, temperature, system, stop)` — **pure**,
  returns `(url, headers, payload)` in OpenAI-chat shape.
- `call(name, prompt, **kw) -> str` — HTTP round-trip + `_extract`.
- `health(timeout=5.0) -> bool` — GET `/v1/models` liveness probe.
- `_settings()` loads `vllm_config.env` via `os.environ.setdefault` (real env wins).
Eval integration is a one-line import swap in `make_proposer`:
`from H1.artifacts.vllm_client import call`.

### 4. `test_vllm_client.py`
8 tests, **no GPU required** — mocks `requests.post/get` with the exact JSON vLLM emits.
Covers request shape, system+stop, purity, env override, response parsing, empty-content,
health true/false, and **signature-equality with `agent.llm.call`**.

### 5. `integrate_vllm_provider.patch`
PROPOSED (not applied) diff adding a first-class `vllm` provider to `agent/llm.py`
(`build_request` branch + `_extract` reusing the OpenAI parser) and a `vllm-local`
roster row to `agent/models.py`. This is the clean merge path so `--model vllm-local`
works natively in `rex/eval_pass_at_k.py` with zero import changes once H1 is greenlit.

## Design reuse
The shim is intentionally the `gateway` provider's wire format pointed at localhost —
`agent/llm.py` already proved OpenAI-chat works for the eval, so vLLM (OpenAI-compatible)
needs no new parsing logic. Minimal new surface, maximal reuse of a known-good path.

## What is NOT done (honest)
- No real server started → no end-to-end live eval run (GPU blocker, see 07/09).
- `health()` exists but isn't *wired as a gate* into core eval (can't edit core).
