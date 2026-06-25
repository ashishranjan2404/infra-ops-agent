# A16 — Improved Plan (post-grill)

## What changed vs 01_plan.md
1. **Scope the claim (SMR, AR)**: the validator proves *engine/label consistency*
   — "the canonical fix clears the root in the Tier-A engine" — NOT real-world
   fidelity. SUMMARY/verification language reflects this narrower, honest claim.
2. **Glob, never hardcode count (DL)**: validate every scenario present at run
   time and report the actual number (turned out to be 54 by run time, up from
   the 42 in the task title, because parallel workers kept adding YAMLs).
3. **Hysteresis is explicitly flagged as unmodeled (PS, RLE)**: the engine's
   `apply_action`/`is_resolved` never read `persistent`/`reset_by`. I do NOT treat
   that as a per-scenario pass/fail; I note it once as a known engine gap so a
   green check doesn't paper over a missing feature.
4. **Errors are first-class results (AR)**: SLOs that name metrics the engine
   doesn't model (`latency_p99_ms`, `pod_restarts`) raise KeyError. The validator
   catches per-file and records `status:"error"` with the message — it does not
   crash the whole run and does not patch the engine.

## Critiques accepted
- AR: "echoing the YAML flag proves nothing" → validator executes the engine and
  records the engine verdict independently; cross-checks the flag as a *promise*.
- RLE: "apply in order" → steps applied verbatim in list order; settle then read.
- PS: "resolved must mean root cleared" → rely on the engine's `is_resolved`,
  which already gates on `root_cleared`.

## Critiques rejected (and why)
- "Reorder/dedup steps to maximize passes" (implicit temptation) → rejected;
  that would launder the scenario's real label. Apply exactly what's authored.
- "Fix failing scenarios in place" → rejected per brief + AR; failures are
  documented in 07/09 with concrete root cause, left for the scenario owner.

## Unchanged
- Read-only over `sim/*` and the YAMLs; all new code under the A16 artifacts dir.
