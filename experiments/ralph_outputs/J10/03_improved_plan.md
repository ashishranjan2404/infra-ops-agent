# J10 — Improved Plan (post-grill)

## What changed vs. 01_plan.md

1. **Reframe (accepted, AR + all).** The deliverable is titled a *deployment-readiness
   analysis*, and an opening paragraph states bluntly that there is **no production
   deployment** behind this and none is being claimed. "Lessons" = what transfers from
   sim/eval + what must still be validated.

2. **Lead with the action layer, reward integrity as its driver (accepted, PSRE+SMR).**
   The lessons section now orders: (L1) action-layer safety is the binding constraint;
   (L2) the reward is a gameable proxy (D13) *and this is why it's an action-safety story*
   — a hedge diagnosis scoring 0.55 rewards non-committal behavior, the prod failure mode.

3. **Substrate fidelity gets its own lesson, framed as unknown-direction bias (accepted,
   RLE+PSRE).** Cite A16's 54/61 with the 7 specific failures, and the engine's unmodeled
   `latency_p99_ms` / `pod_restarts` and missing hysteresis. State that this both *caps* the
   eval ceiling and may bias trained behavior in an *unknown direction* (not purely bad).

4. **Every gap ships a measurable acceptance gate labeled "TARGET — NOT YET MEASURED"
   (accepted, DOL+AR).** This converts hand-waving into a specified experiment without
   fabricating a result. Numbers are clearly thresholds-to-validate, never observations.

5. **Added rollback / blast-radius to the readiness checklist (accepted, DOL).** Was missing.

6. **MTTR: state the gap, not a delta (accepted, AR+A9).** Because 12 of 30 real incidents
   have unknown MTTR (A9), we explicitly refuse to report an MTTR improvement and instead
   give the measurement protocol + the data-quality precondition.

## Rejected critiques (with reasons)
- **PSRE R2: "reward hacking is secondary, drop D13."** Rejected. SMR's rebuttal holds: the
  policy's action distribution is shaped by the reward, so D13's hedge→0.55 result is
  directly an action-safety concern. Kept, but recast under the action-safety lesson.

## Added integrity guard (new, beyond 01)
To make "no fabrication" *checkable*, the structured `readiness_gaps.json` records, per gap,
the grounding artifact path(s); `test_readiness.py` asserts every cited path exists and that
the prose contains no banned fabricated-prod phrasing. This makes the honesty constraint a
test, not a promise.

## Unchanged
Stdlib-only, task-namespaced artifacts, no core edits, the four deliverable files.
