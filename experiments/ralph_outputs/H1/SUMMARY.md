# H1 — Local vLLM for Faster Eval — SUMMARY

## Goal
Eliminate the pass@k ablation stall caused by remote-API latency/rate-limits by serving
an eval policy from a local vLLM OpenAI-compatible endpoint.

## Delivered (all in H1/artifacts/, no core files edited)
- serve_vllm.sh — launches vllm.entrypoints.openai.api_server with a small pinned open
  model (Qwen/Qwen2.5-1.5B-Instruct), served as vllm-local. Loud exit 3 if vllm absent.
- vllm_config.env — single source of truth (model, bind, client base-url), parsed by
  both the shell script and the python client.
- vllm_client.py — OpenAI-compatible drop-in for agent.llm.call
  (build_request/call/health). Eval integration = one import swap in make_proposer.
- test_vllm_client.py — 9 tests, GPU-free; includes an exact-signature match vs
  agent.llm.call.
- integrate_vllm_provider.patch — proposed (documented, not applied) native vllm provider
  for agent/llm.py + roster row, so --model vllm-local works with no import change.

## Validation
- bash -n clean; guard exit 3 confirmed.
- 9/9 unit tests pass (mocked vLLM responses).
- Live end-to-end health() + call() proven over real sockets against a stdlib mock vLLM
  server (health=True, call -> echo:...).

## Blocker (honest)
No GPU and no vllm/torch on this arm64 mac -> a real vLLM server cannot start here, so no
live frontier eval run. Scaffold validated against vLLM's wire contract; no fabrication.

## Key caveat
vllm-local is a throughput tool, an added weak anchor — not a frontier-quality claim.
Small-model plan-format fluency is unverified (needs a live server). Frontier comparisons
still use the remote API.

Status: completed (deliverable real + tested; only the downstream GPU eval run is blocked).
