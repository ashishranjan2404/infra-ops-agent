# 03 — Improved Plan (post-grill)

## What changed vs 01
1. **Added `health()` to the shim** — cheap GET `/v1/models` liveness probe so eval can
   fail fast before firing a batch at a dead/cold port. (Accepted: PSRE.)
2. **Pinned the model** explicitly in `vllm_config.env` (`Qwen/Qwen2.5-1.5B-Instruct`,
   `SERVED_NAME=vllm-local`) so the "weak anchor" is a fixed point, not drifting. Added a
   reproducibility note to pin vLLM version + revision on the GPU host. (Accepted: SMR/REV.)
3. **Dual deliverable made explicit**: standalone `vllm_client.py` (compliant under the
   no-core-edit rule) **plus** `integrate_vllm_provider.patch` (the native-provider merge
   path). (Accepted: DOL — reframed as compliance, not debt.)
4. **Framing**: `vllm-local` documented as an *added weak anchor* in the spanning set,
   not a replacement for frontier rows — the ablation design absorbs it. (Accepted: RLE/SMR.)

## Critiques accepted
- Health probe, model pinning, dual deliverable, anchor framing (above).
- Small-model **format-fluency risk** logged as an explicit limitation (09).

## Critiques rejected (with reason)
- **REV: full live format smoke test as a gate.** Rejected *as a blocking deliverable
  here* — it requires a running GPU server which this host lacks. Faking its output would
  violate the no-fabrication rule. Instead: documented as the first follow-up once a GPU
  host exists, and the *mechanism* (`health()` + the existing `parse_plan`) is in place.
- **RLE: prove ThreadPool saturates the server.** Rejected as out-of-scope for H1 — that's
  a tuning/benchmark task on real hardware. The shim doesn't constrain concurrency; eval's
  existing `ThreadPoolExecutor` drives it. Noted as a perf follow-up.

## Final artifact list (unchanged paths, enriched contents)
- `serve_vllm.sh` (pinned model via config, clear no-vllm exit 3)
- `vllm_config.env` (pinned MODEL/SERVED_NAME, client base-url)
- `vllm_client.py` (build_request + call + **health** + signature match)
- `test_vllm_client.py` (mocked endpoint, env override, signature test)
- `integrate_vllm_provider.patch` (native `vllm` provider, documented, not applied)

## Success criteria (tightened)
- All shim unit tests pass incl. `health()` true/false and signature-match.
- `serve_vllm.sh` parses config and exits 3 with a clear message when vllm is missing.
- Model id is pinned in config; reproducibility note present.
