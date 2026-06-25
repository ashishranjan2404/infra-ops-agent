# A16 — Critique (honest)

## What's solid
- The validator executes the real engine and reports an independent verdict; it
  cannot be fooled by a YAML self-declaring `fix_resolves: true`. It surfaced 7
  genuine defects that the spec-level validator (`python -m sim.spec validate`)
  does NOT catch, because that validator only checks structure/vocab, never runs
  the fix. That's the real contribution.
- Non-vacuous: passes are gated on the fault actually biting at t0.

## What a reviewer will attack
1. **"You validated internal consistency, not correctness of the benchmark."**
   True. A green result means "the labeled fix clears the root in *this* engine,"
   not "this scenario is faithful to the real incident." I scoped the claim
   accordingly (03/08) but the limitation is real.
2. **"The headline isn't 42/42."** Correct — fix_resolves does NOT hold for all
   scenarios. 7 of 61 fail/error. The task as literally phrased ("fix_resolves
   must be true" for all 42) is FALSIFIED by the run. That's the honest result.
3. **"Three of the 7 are engine limitations, not scenario bugs."** Right — the
   KeyError trio (`latency_p99_ms`, `pod_restarts`) is the engine modeling fewer
   metrics than some SLOs reference. Whether to fix the scenarios (rename metric)
   or extend the engine (add metrics) is a design call I deliberately did not make.
4. **"Hysteresis is unmodeled, so some 'passes' may be physically wrong."** The
   `persistent`/`reset_by` scenarios pass only because the engine ignores the
   latent counter. If hysteresis were implemented, the upstream-only fixes might
   no longer restore SLO. The pass for those is engine-faithful but reality-thin.

## What's missing / weak
- No automated regression wiring (the validator is standalone, not a pytest in
  the suite) — a follow-up could add it to CI so new YAMLs can't silently break.
- The validator settles a fixed `max(sustain_ticks)`; it doesn't verify the SLO
  *stays* recovered across the full sustain window tick-by-tick, only the end state.
- Moving target: parallel workers changed the count under me; the report is a
  snapshot, not a frozen contract.

## Bottom line
Deliverable is real and the finding is the opposite of the task's optimistic
premise: fix_resolves is NOT universally true. Seven scenarios need owner
attention (4 wrong-target/wrong-tool authoring bugs, 3 engine-metric gaps).
