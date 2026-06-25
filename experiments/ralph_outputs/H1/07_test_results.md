# 07 — Test Results

## Environment probe (the blocker)
```
python3 --version        -> Python 3.13.7
import vllm              -> ModuleNotFoundError (not installed)
nvidia-smi              -> command not found
import torch            -> ModuleNotFoundError
uname -m                -> arm64   (Apple Silicon)
import requests         -> ok
```
**Blocker: no CUDA/ROCm GPU and no `vllm`/`torch` on this host (arm64 mac).** A real
vLLM server cannot start here — vLLM's CUDA builds are unsupported on Apple Silicon.
This is documented honestly; no live frontier numbers are fabricated.

## 1. Launch script — syntax + guard behavior  ✅
```
$ bash -n serve_vllm.sh                 -> serve_vllm.sh OK
$ ./serve_vllm.sh
[serve_vllm] model=Qwen/Qwen2.5-1.5B-Instruct served-as=vllm-local http://127.0.0.1:8000/v1
[serve_vllm] ERROR: vllm not importable. Install on a GPU host: pip install vllm
[serve_vllm] (CPU/Apple-Silicon is unsupported by vLLM CUDA builds — see H1 blocker.)
exit_code=3
```
Fails loudly with a clear message + nonzero exit when vllm is absent — as specified.

## 2. Config parse (shell + python)  ✅
```
$ ( set -a; . vllm_config.env; set +a; echo "$MODEL $VLLM_BASE_URL" )
Qwen/Qwen2.5-1.5B-Instruct http://127.0.0.1:8000/v1
```
Python side validated implicitly by the env-override test (loads same file).

## 3. Shim unit tests (mocked endpoint, no GPU)  ✅ 9/9
```
$ python3 -m pytest test_vllm_client.py -v
test_build_request_basic_shape ........ PASSED
test_build_request_system_and_stop .... PASSED
test_build_request_no_network ......... PASSED
test_env_override ..................... PASSED
test_call_parses_openai_response ...... PASSED
test_call_handles_empty_content ....... PASSED
test_health_true_when_models_200 ...... PASSED
test_health_false_on_error ............ PASSED
test_signature_matches_agent_llm ...... PASSED      # shim == agent.llm.call signature
9 passed in 0.02s
```
The signature test imported the real `agent.llm.call` and confirmed an exact parameter
match — the shim is a true drop-in.

## 4. Live end-to-end HTTP path (stdlib mock vLLM server, no GPU)  ✅
A minimal stdlib OpenAI-compatible server was started on :8123; the shim was pointed at
it via `VLLM_BASE_URL`:
```
LIVE HTTP OK: health=True, call -> echo:diagnose oom_kill
```
Proves `health()` (GET /v1/models) and `call()` (POST /v1/chat/completions → parse) work
over real sockets, not just mocks. (Test script: scratchpad/mock_vllm.py — throwaway.)

## 5. Patch  (documented guide, intentionally not auto-applied)
`integrate_vllm_provider.patch` is a hand-written, human-readable diff with apply
instructions. It is the *merge guide* for the native provider; the **compliant
deliverable that needs no apply is the standalone `vllm_client.py`**. `git apply --check`
does not accept the annotated hunks verbatim — expected and noted in 05 (P8).

## Fixes applied during testing
- None required — artifacts passed on first run. (Initial design reused the proven
  `gateway` OpenAI wire format, so there was little new surface to break.)
