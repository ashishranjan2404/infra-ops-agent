# E4 — 03 Improved Plan (post-grill)

## What changed vs 01
1. **Pinned + validated 8 incidents** (RLE/DVO/PSRE). `SIMPLE_8` is a hard-coded list,
   and `validate_incidents()` raises if any is not in the live `simple` family — so a
   future scenario rename fails loudly instead of silently testing the wrong 8.
2. **Both mean delta AND per-incident "hurts" flags** (PSRE vs SMR synthesis). The
   harness reports `regression.mean_delta_b_minus_a` (trend) *and*
   `per_incident[].hurts` (operator's asymmetric-cost risk view). Neither is dropped.
3. **Verdict carries its caveat in-band** (REV). The result JSON's `note` field sits
   in the same object as `verdict`, so "B_HURTS" can never be quoted without "STAND-IN
   policies … neither trained slug exists" travelling with it.
4. **Same-provider stand-in** (RLE/DVO). Stand-in run uses `glm-5p2` vs `minimax-m3`,
   both Fireworks, to isolate the harness from the cross-provider prompt-assembly bias
   documented in `agent/llm.py`. Provider/model recorded in the artifact.
5. **Wilson CIs + explicit low-power note** (REV). `summarize()` emits `ci95`; docs
   state n is illustrative, not significant.

## Critiques accepted
- REV's "label relentlessly" → the verdict caveat is in-band (accepted, strongest fix).
- PSRE's "per-incident asymmetric cost" → kept per-incident flags (accepted).
- RLE's "same provider / same judge / same scenarios" → enforced (accepted).
- DVO's pin-in-code + JSON artifact → done (accepted).

## Critiques rejected (with reason)
- REV's "n is too low, don't make the claim" → **rejected as a blocker** for the
  deliverable. The task is the harness, not a significance result; the harness exposes
  `--seeds` so the operator chooses power at real-run time. We do NOT inflate seeds now
  just to manufacture significance on stand-in models that aren't the real policies.
- SMR's "averaging is the only real signal, per-incident is noise" → **partially
  rejected**; for an on-call tool the per-incident regression flag is the operationally
  load-bearing output even if noisy, so it stays alongside the mean.

## Unchanged success criteria
No shared-core edits; offline tests pass; real run with 0 fabricated numbers; honest
BLOCKED verdict on the actual trained-vs-trained question.
