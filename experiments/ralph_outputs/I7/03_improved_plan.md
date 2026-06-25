# 03 — Improved Plan

## What changed after the grill
1. **Added `other-trap` catch-all** (REV). Unknown trap tools classify to
   `other-trap` instead of being dropped — the taxonomy degrades honestly.
2. **Dropped the "predicts reward" framing** (RLE/MLR). The `TRAP_PENALTY` is a
   FLAT `0.60` for any matched trap, so the taxonomy is *diagnostic/descriptive*,
   not a new reward axis. The doc now says this explicitly and does not oversell.
3. **Promoted zero-failover-coverage to a headline finding** (DVO). The doc's honest
   assessment leads with it: the most dangerous real-world trap is untested.
4. **Kept tool as the classification axis** (MLR, grounded in `_traps_in()`) but the
   doc table cross-references the gold-fix verb so the cause↔wrong-action contrast
   is explicit per category.

## Accepted
- catch-all bucket, flat-penalty honesty, failover-gap headline, tool-axis grounding.

## Rejected (and why)
- SRE's "don't blame the classifier for a data gap": rejected as a framing for the
  *report*. The classifier isn't blamed, but the report must own the taskset gap —
  that's the only actionable output here. The classifier code stays neutral; the
  honesty lives in the doc.
- Any attempt to weight categories by severity in the *score*: out of scope and
  would require editing `rex/scoring.py` (forbidden shared file). Documented as a
  future-work suggestion only.

## Unchanged
Reuse G4 input set; read-only; stdlib+yaml; self-test; run and report counts.
