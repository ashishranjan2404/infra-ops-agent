# 05 — Ouroboros (self-critique as 3 engineers)

## Engineer 1 — "the wire-format pedant"
**Problems found:**
- (P1) `build_request` ignores `name` for routing — silently. If someone runs the
  ablation with `--model glm-5p2` through the shim, they'd *think* they're hitting glm
  but get the local model. That's a **silent correctness trap** for cross-model runs.
- (P2) vLLM's `--api-key` makes auth mandatory; if the shim's default `local-key`
  mismatches the server's key, every call 401s with a cryptic message.
- (P3) No timeout override surfaced to `call` callers; a hung server blocks a thread for
  180s.
**Resolution:** (P1) Documented loudly in the docstring ("`name` ignored for routing;
served model fixed by server / VLLM_MODEL"). The native `.patch` removes the trap by
making `vllm-local` a real roster row that *only* the local provider serves. (P2) Both
default to `local-key`; documented that they must match. (P3) `_post` has a `timeout`
param; acceptable default. Kept simple — eval already wraps calls in a retry.

## Engineer 2 — "the reproducibility hawk"
**Problems found:**
- (P4) Model pinned by *tag* (`Qwen/Qwen2.5-1.5B-Instruct`), not by commit revision — HF
  could move the tag. Spread becomes irreproducible across months.
- (P5) vLLM version unpinned → sampling/templating differences across versions.
- (P6) `temperature=0.1` default but eval passes `temp=0.7`; small models at 0.7 may be
  noisy. Not a bug, but worth flagging the interaction.
**Resolution:** (P4/P5) Added a reproducibility note (config comment + 09) to pin vLLM
version and optionally the HF revision on the GPU host. Not enforced in the script
because the host is the source of truth; over-pinning a script we can't run here is
theater. (P6) Out of scope — eval owns temperature; noted as a limitation.

## Engineer 3 — "the over/under-engineering auditor"
**Problems found:**
- (P7) Is `health()` over-engineering? No — grill ranked it the highest-value cheap
  guard; kept. But it's **not wired into eval** here (we can't edit core), so it's a
  capability, not yet a gate. Honest gap.
- (P8) The `.patch` is hand-written, not `git diff`-generated, so `git apply` may reject
  on whitespace/line drift. Risk of bit-rot.
- (P9) `test_signature_matches_agent_llm` imports `agent.llm`, which transitively imports
  `agent.models` and may pull `.env` loading — could fail in a bare env.
**Resolution:** (P7) Documented as follow-up wiring. (P8) Labeled the patch "PROPOSED /
apply from repo root", and the *real* compliant deliverable is the standalone shim that
needs no apply — the patch is a guide. (P9) Test **skips gracefully** if `agent.llm`
won't import, so the suite stays green in any env.

## Final filtered spec (deltas folded in)
- Docstring warns `name` is non-routing (P1). API-key match documented (P2).
- Reproducibility note added; not over-pinned in an unrunnable script (P4/P5).
- `health()` kept as a capability; wiring is a documented follow-up (P7).
- Patch labeled PROPOSED with apply instructions; shim is the no-apply path (P8).
- Signature test skips when `agent.llm` is unavailable (P9).
