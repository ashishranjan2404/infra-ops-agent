# 09 — Critique (honest)

## What a reviewer will attack
1. **"You never ran it against a live incident."** True, and it's the headline limitation.
   The task says "run on a live incident (shadow mode)"; we ran on a *recorded-real*
   telemetry snapshot because no GKE cluster / Prometheus / LLM credits are reachable from
   this worker (interactive `gcloud` login required; Anthropic credits exhausted per
   MEMORY.md). The harness is live-ready (`--prometheus`, `--live-llm`) but unproven online.
2. **"The safety guarantee is structural, not sandboxed."** The module contains no
   execution path (no `apply_action`, no `subprocess`, no `/ctl` POST), and a test greps
   for that. But a determined author could `__import__("subprocess")` at runtime — the
   guarantee is "no execution code is written here," not OS-level sandbox isolation. A
   hardened version would run the harness under a seccomp/network-egress policy.
3. **Detection is error-mode only (B1 from ouroboros).** `observe()` derives victims from
   5xx fraction. A *slow* (not erroring) fault — which `mreal/server.py` supports via
   `OWN_FAULT=slow` — would show 0% 5xx and read as "all nominal," producing no proposal.
   The report carries `raw_metrics` (incl. latency histograms) so a richer diagnoser can
   be added, but the current observer under-uses telemetry.
4. **Root != loudest.** The stub proposer's "last victim is the root" heuristic is crude;
   in the fixture payments *is* both loudest and root, so it happens to work, but that's
   luck. Real diagnosis is delegated to the LLM proposer (untested here).
5. **Dead test assertion (C1).** `test_runner_has_no_execution_imports` has a tautological
   `... or True` clause; the two load-bearing asserts (`subprocess`, `/ctl/...`) carry the
   real weight. Cosmetic, should be cleaned.
6. **Redirect risk (A2).** `urlopen` follows redirects; scrape only trusted Prometheus.

## What's genuinely solid
- The non-execution guarantee is verified three independent ways (structural grep,
  data invariant `executed_count==0`, violation test).
- Telemetry shape is real (byte-identical to the live mesh), so the parser isn't fantasy.
- The reasoning side is the *actual* `rex/loop.py` proposer, reused unmodified.
- No shared core file was touched; the one proposed core change (`mode="shadow"` in
  `run_plan`) is documented as a sketch, not made.

## Honest status
**Completed deliverable, blocked downstream run.** The shadow harness + safety guarantee
+ tests are real and pass; the live-incident execution against a running cluster is the
documented blocker.
