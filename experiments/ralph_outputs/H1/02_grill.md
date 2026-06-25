# 02 — Grill (5 personas, 3 rounds)

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**, **AAAI Reviewer
(REV)**, **RL Engineer (RLE)**, **DevOps Lead (DOL)**.

## Round 1 — initial takes
- **SMR:** Local vLLM is the right lever for throughput, but swapping the *model* for a
  1.5B open model changes the policy you're evaluating. If the ablation's claim is about
  REx structure being model-agnostic, fine; if it's about a specific frontier model, a
  local small model is a *different experiment*, not a faster version of the same one.
- **PSRE:** From an ops view this is great — no rate-limit pages, deterministic latency.
  But I want a **health check** before eval fires 200 episodes at a dead port, and a
  clear failure mode when the GPU OOMs mid-run.
- **REV:** Reproducibility. Pin the model revision and vLLM version, or your "fast eval"
  is unreproducible across machines. Also: does the local model even *follow the plan
  format*? A 1.5B model may emit garbage that the deterministic judge scores as 0,
  inflating "REx helps" for the wrong reason.
- **RLE:** The win is continuous batching — but `make_proposer` calls are *serial per
  episode* and episodes are threaded. vLLM batches across concurrent HTTP requests, so
  throughput only materializes if eval keeps many requests in flight. Confirm the eval's
  ThreadPool width actually saturates the server.
- **DOL:** Don't fork `agent/llm.py`. Add a provider, gate it behind a roster row, keep
  one code path. A standalone shim that drifts from `call()` is tech debt.

## Round 2 — react to another persona (genuine disagreement)
- **RLE → SMR:** I disagree that a small model makes it "a different experiment." The
  ablation already runs a *spanning set* of weak→strong anchors (`agent/models.py`). A
  local `vllm-local` is just another **weak anchor** — it *adds* a cheap, fast point to
  the spread, it doesn't replace the frontier rows. The stall problem is real *today*;
  iterating locally on a weak anchor is exactly how you debug the harness cheaply.
- **REV → PSRE:** A health check is necessary but *not sufficient* for my reproducibility
  concern. You can have a healthy server returning fluent-but-format-violating text. The
  real guard is a tiny "does output parse into a plan" smoke test, not just HTTP 200.
- **DOL → DOL-vs-shim, answering RLE/SMR:** I'll push back on the "standalone shim is
  debt" framing *from myself*: in a **parallel Ralph-Loop** we are explicitly forbidden
  from editing core `agent/llm.py`. So the standalone shim is not debt, it's the *only
  compliant deliverable now*; the `.patch` is the clean merge path later. Both, not one.
- **SMR → RLE:** Conceding the spanning-set point — but I still insist the config **pin
  the model id** so `vllm-local` means one specific model, else the "weak anchor" moves
  under us between runs and the spread is noise.
- **PSRE → REV:** Agreed the format smoke test matters, but operationally I rank
  *liveness* first: a 200-episode run that dies at episode 3 on a cold port wastes the
  most time. Health probe is the cheapest highest-value guard; format check is second.

## Round 3 — synthesis
Consensus deliverable:
1. **Keep core untouched** → ship `vllm_client.py` (compliant now) **and** a documented
   `.patch` for the native provider (clean merge later). (DOL, resolved.)
2. **Pin the model** in `vllm_config.env` (`MODEL=Qwen/Qwen2.5-1.5B-Instruct`,
   `SERVED_NAME=vllm-local`) so the anchor is stable. (SMR/REV.)
3. **Add `health()`** to the shim as a cheap liveness probe eval can call before firing
   episodes. (PSRE.)
4. Frame `vllm-local` as an **added weak anchor**, not a replacement for frontier rows;
   the ablation's spanning-set design absorbs it. (RLE/SMR.)
5. Note the **format-fluency risk** of small models as an explicit limitation in 09; a
   full format smoke test against a live server is blocked here (no GPU) and deferred.
   (REV/PSRE.)
