# 08 — Verification against success criteria

| Criterion (from 01/03) | Status | Evidence |
|---|---|---|
| Launch script `vllm serve` with a small open model | ✅ | `serve_vllm.sh` execs `vllm.entrypoints.openai.api_server` with pinned `Qwen/Qwen2.5-1.5B-Instruct`; `bash -n` clean |
| Script fails loudly + nonzero exit when vllm absent | ✅ | `exit 3` with clear message (07 §1) |
| OpenAI-compatible client shim pointing eval at local endpoint | ✅ | `vllm_client.py`; live HTTP round-trip proven (07 §4) |
| Shim is a true drop-in for `agent.llm.call` | ✅ | `test_signature_matches_agent_llm` PASSED against real `agent.llm` (07 §3) |
| Config file (single source of truth, server+client) | ✅ | `vllm_config.env` parsed by both shell and python (07 §2) |
| Model pinned (grill requirement) | ✅ | `MODEL`/`SERVED_NAME` fixed in config |
| `health()` liveness probe present | ✅ | returns True on 200 / False on 503, proven live (07 §4) |
| Dry validation attempted; blocker documented if no GPU | ✅ | env probe + honest blocker (07 §0, 09) |
| No shared core file edited | ✅ | only `H1/artifacts/*`; core change is a `.patch` |
| All unit tests pass | ✅ | 9/9 |

## Are the outputs real (not placeholder)?
- `vllm_client.py` — real, importable, exercised over real sockets against a live mock
  server (not just mocked functions). 9 passing tests.
- `serve_vllm.sh` — real, runnable; produced the documented guard output.
- `vllm_config.env` — real, parsed by both consumers.
- `test_vllm_client.py` — real pytest suite, 9 passing.
- `integrate_vllm_provider.patch` — real, human-readable, accurate against current
  `agent/llm.py` + `agent/models.py` structure (verified by reading those files).

## What "completed" means here
The deliverable (serving scaffold + client shim + config, validated) is **done**. The
only thing blocked is a *live frontier eval run*, which needs a GPU host this machine
lacks — and that downstream run is explicitly allowed to be blocked per the brief, as
long as the scaffold is real. It is.
