# 04 — Technical Spec

## Components & contracts

### A. `serve_vllm.sh` (server)
Launches vLLM's OpenAI server. Reads `vllm_config.env` (overridable by env).
- Inputs (env/config): `MODEL, SERVED_NAME, HOST, PORT, MAX_LEN, GPU_UTIL, DTYPE, VLLM_API_KEY`.
- Behavior: if `import vllm` fails → print install hint, `exit 3`. Else `exec
  python3 -m vllm.entrypoints.openai.api_server --model ... --served-model-name ...
  --host --port --max-model-len --gpu-memory-utilization --dtype --api-key`.
- Exit codes: `0` (server foreground), `3` (vllm missing), other = vllm's own.

### B. `vllm_config.env` (config — single source of truth)
Shell-sourced AND python-parsed (`KEY=VALUE`, `#` comments). Keys:
```
MODEL, SERVED_NAME, HOST, PORT, MAX_LEN, GPU_UTIL, DTYPE, VLLM_API_KEY   # server
VLLM_BASE_URL, VLLM_MODEL                                                # client
```
Pinned: `MODEL=Qwen/Qwen2.5-1.5B-Instruct`, `SERVED_NAME=vllm-local`,
`VLLM_BASE_URL=http://127.0.0.1:8000/v1`, `VLLM_MODEL=vllm-local`.

### C. `vllm_client.py` (client shim) — drop-in for `agent.llm.call`

```python
def build_request(name: str, prompt: str, max_tokens: int = 512,
                  temperature: float = 0.1, system: str | None = None,
                  stop: list | None = None) -> tuple[str, dict, dict]: ...
def call(name: str, prompt: str, **kw) -> str: ...
def health(timeout: float = 5.0) -> bool: ...
def _extract(resp: dict) -> str: ...
def _settings() -> tuple[str, str, str]:  # (base_url, model, api_key)
```
- `build_request` is **pure** (no network). Returns
  `(f"{base}/chat/completions", headers, payload)` where
  `payload = {"model", "max_tokens", "temperature", "messages"[, "stop"]}` and
  `messages = [{"role":"system",...}]? + [{"role":"user","content":prompt}]`.
- `_extract(resp)` = `resp["choices"][0]["message"]["content"]` (empty-safe).
- `call` = `_extract(POST(build_request(...)))`.
- `health` = GET `{base}/models` → `True` iff HTTP 200.
- Config: `_settings()` loads `vllm_config.env` via `os.environ.setdefault`, so real
  env vars win over the file (test isolation, deploy override).
- **Signature invariant:** `inspect.signature(call) == inspect.signature(agent.llm.call)`.

### D. Request/response wire format (OpenAI-compatible, what vLLM emits)
Request → `POST /v1/chat/completions`:
```json
{"model":"vllm-local","max_tokens":512,"temperature":0.1,
 "messages":[{"role":"user","content":"..."}]}
```
Response (parsed by `_extract`):
```json
{"choices":[{"message":{"role":"assistant","content":"<text>"}}]}
```

### E. Test cases (`test_vllm_client.py`, no GPU)
1. `build_request` basic shape (url, headers, payload keys, message list).
2. `build_request` with `system` + `stop`.
3. purity — no `requests` use during build.
4. env override (`VLLM_BASE_URL`/`VLLM_MODEL` win).
5. `call` parses OpenAI response (mocked post).
6. `call` empty-content safe.
7. `health` True on 200, False on 503 (mocked get).
8. signature equals `agent.llm.call` (skips if `agent.llm` unimportable).

### F. Integration into eval (documented, not executed here)
In `rex/eval_pass_at_k.py`, `make_proposer` does `from agent.llm import call`. Two paths:
- **Shim path (compliant now):** `from H1.artifacts.vllm_client import call`.
- **Native path (post-patch):** apply `integrate_vllm_provider.patch`, run with
  `--model vllm-local`; no import change.
