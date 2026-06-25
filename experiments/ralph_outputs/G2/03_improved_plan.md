# G2 — Improved Plan (post-grill)

## What changed vs 01_plan.md
1. **Added a raw `kubectl`-style passthrough** to the cluster-control tool, with a
   translation table to our 25-verb registry and an explicit `untranslated` counter.
   (Accepted SMR's confound critique via PSRE's rebuttal: don't hide the interface gap,
   *measure* it.) This makes the adapter usable by Stratus's free-form `kubectl` action
   style, not only by agents that emit our structured `{tool,args}`.
2. **Promoted the stub agent to a required proof obligation**, not a nicety. It must
   touch every tool family and yield a real engine verdict. (Accepted AAAI.)
3. **Scoped the comparison claim** explicitly in the brief/run-plan: faithful on
   1:1-mapped leaf scenarios; report `untranslated_kubectl_rate` as the fidelity metric
   for cascade-heavy scenarios. (Accepted RLE+SMR.)
4. **Kept the stub deliberately simple** (deterministic, ~1 file). (Accepted DOL,
   rejected gold-plating it into a real LLM agent — out of scope + budget.)

## Critiques accepted
- SMR: action-distribution shift confounds subtle scenarios -> added passthrough +
  fidelity metric + scoped claim.
- AAAI: adapter must be *validated*, not just present -> stub agent + self-test.
- DOL: must match SREGym's real `agents.yaml` schema + give unblock steps.

## Critiques rejected (and why)
- SMR's strongest form ("the shim confounds everything, don't run it"): rejected for the
  **leaf** scenarios, where the 1:1 tool mapping is faithful and a Stratus pass/fail is
  interpretable. We scope the claim instead of abandoning the build. (RLE's point.)
- DOL's "stub can be trivial / loop-only": rejected the *trivially* trivial version —
  the stub still must produce a genuine `is_resolved` from `sim.engine`, not a hardcoded
  "pass". Otherwise the adapter is unfalsified.

## Final deliverable shape (unchanged targets, sharpened)
- `sregym_adapter.py`: env server exposing 5 SREGym tool families over `sim.engine`,
  with structured + `kubectl`-passthrough cluster control and a fidelity counter.
- `stub_agent.py`: deterministic SREGym-shaped client; solves an easy scenario, trips on
  a trap, both via real engine verdicts.
- `agents.yaml`: SREGym registration for Stratus (documented command) + our stub.
- `STRATUS_BRIEF.md`, `RUN_PLAN.md`, `test_adapter.py`.
- Documented blocker: no live cluster + Stratus/MCP bundle not vendored -> real Stratus
  numbers deferred; everything *up to* invoking Stratus is real and runnable.
