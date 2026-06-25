# 01 — Plan (H1: local vLLM for faster eval)

## Objective
Stand up a **local vLLM OpenAI-compatible serving setup** so the pass@k ablation
(`rex/eval_pass_at_k.py`) stops stalling on remote-API latency / rate limits. Deliver
three real, runnable artifacts: (1) a launch script `vllm serve` with a small open
model, (2) an OpenAI-compatible **client shim** that points our eval at the local
endpoint, (3) a **config** file shared by server + client.

## Why this is the right shape
`agent/llm.py` already has a `gateway` provider that speaks OpenAI chat
(`/v1/chat/completions`). vLLM serves *exactly that API*. So "use local vLLM" = point
the same wire format at `http://127.0.0.1:8000/v1`. Minimal surface, maximal reuse.

## Approach
1. Probe env for GPU + vllm + torch (expect a blocker on this arm64 mac).
2. `serve_vllm.sh` — wraps `python -m vllm.entrypoints.openai.api_server` with a small
   model (`Qwen/Qwen2.5-1.5B-Instruct`), served-model-name, api-key, max-len, gpu-util.
3. `vllm_config.env` — one source of truth: model, host/port, base-url for the client.
4. `vllm_client.py` — drop-in `call(name, prompt, **kw) -> str` mirroring `agent.llm.call`
   so eval swaps one import. Pure `build_request` + HTTP `call` + `health()` probe.
5. `test_vllm_client.py` — validate shim against a **mocked** OpenAI endpoint (no GPU):
   request shape, response parsing, env override, and signature-match vs `agent.llm.call`.
6. `integrate_vllm_provider.patch` — proposed (not applied) core change adding a `vllm`
   provider so `--model vllm-local` works natively, for the eventual merge.

## Files to create (all task-namespaced, NO core edits)
- `H1/artifacts/serve_vllm.sh`
- `H1/artifacts/vllm_config.env`
- `H1/artifacts/vllm_client.py`
- `H1/artifacts/test_vllm_client.py`
- `H1/artifacts/integrate_vllm_provider.patch`

## Dependencies
- Runtime: `vllm` + CUDA/ROCm GPU (for the real server). `requests` (already present).
- For validation: `pytest` only — no GPU.

## Risks
- **No GPU on dev host** → cannot start a real vLLM server. Mitigation: validate the
  client shim against a mock and document the blocker honestly (07/09).
- Shim drift from `agent.llm.call` signature → mitigated by an explicit signature test.

## Success criteria
- Launch script is syntactically valid, parameterized, fails loudly with a clear
  message + nonzero exit when vllm is absent.
- Client shim is import-clean and API-correct: all unit tests pass.
- Shim signature is identical to `agent.llm.call` (true drop-in).
- Config is parseable by both `serve_vllm.sh` (shell) and `vllm_client.py` (python).
- Blocker (no GPU) documented, not faked.
