# 09 — Honest Critique

## The headline weakness
**No real vLLM server ever ran.** This host has no GPU and no `vllm`/`torch`. Everything
is validated against the *contract* (unit tests + a stdlib mock that mimics vLLM's wire
format), not against vLLM itself. A reviewer's first attack is fair: "you didn't prove
the actual server works, only that your client speaks a compatible dialect." True. The
mitigation is that vLLM's OpenAI compatibility is well-specified and the eval already
uses that exact wire format for its `gateway` provider — so the risk is low, but not zero.

## What a reviewer attacks next
1. **Small-model format fluency.** A 1.5B model may not reliably emit the plan format the
   deterministic judge expects. If it produces malformed plans, pass@k craters for reasons
   unrelated to REx structure — or, worse, makes REx look helpful for the wrong reason
   (recovering from format noise). Unverified here (no live server). This is the single
   biggest scientific caveat: **`vllm-local` is a throughput tool, not a quality claim.**
2. **It changes the policy under test.** Speeding up eval by swapping to a local small
   model is only valid if framed as *adding a weak anchor* to the spanning set, not as
   "the same experiment, faster." Frontier rows still need the real API. So H1 does not
   actually eliminate API latency for the frontier comparison — it only does for the
   local-anchor portion. Honest scope limit.
3. **The `.patch` is hand-written**, so `git apply` won't take it verbatim; it's a guide,
   not a turnkey artifact. The compliant turnkey path is the import-swap shim.
4. **`health()` isn't wired as a gate.** It exists but eval doesn't call it (can't edit
   core). So the "fail fast before 200 episodes" benefit is latent, not active.
5. **No reproducibility pinning enforced** (vLLM version, HF revision) — deferred to the
   GPU host as a note, not enforced in code we can't run.
6. **No throughput measurement.** The whole premise is "faster," but with no GPU we never
   measured tokens/s or that eval's ThreadPool saturates vLLM's batcher. The latency win
   is argued, not benchmarked.

## What's genuinely solid
- The shim is signature-identical to `agent.llm.call` and works over real sockets.
- The launch script is correct and degrades loudly.
- Zero core files touched — parallel-safe.
- The reuse of the proven `gateway` wire format makes the compatibility claim credible.

## Net
A correct, tested, parallel-safe **scaffold + shim + config** with an honest GPU blocker
and an explicit scientific caveat (local small model ≠ frontier policy). It removes the
ablation stall *for the local-anchor path* and gives a clean merge route for the rest.
It does **not** deliver a measured speedup or a verified frontier-eval run.
