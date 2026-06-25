# A11 — 03 Improved Plan

## What changed after the grill
1. **Added an explicit difficulty axis to the manifest (accepted AAAI's confound
   critique).** Each pair labels variant A as `leaf`/root-visible and variant B as
   `cascade`/root-buried. The manifest's description tells the analyst to run
   transfer in BOTH directions so difficulty can be controlled for. We do not
   claim the pairs are difficulty-matched.
2. **Locked the invariant to `failure_class` + `canonical_fix` tool (accepted
   RLE/PSRE).** That is the exact signal the deterministic judge in
   `rex/scoring.py` keys on, so "same root cause" is operationally testable, not
   just narrative.
3. **Constrained symptom deltas to schema-renderable knobs (accepted DOL/RLE,
   partially rejected SMR's "large observation-space delta").** Deltas come from
   topology shape, SLO-violating node, smoking-gun text, and cascade/leaf flags —
   no invented metrics. Rejected SMR's push for novel observation channels because
   the sim only emits `error_rate_pct` + logs; inventing channels would make the
   YAML unscoreable.
4. **Kept it a side manifest, no `registry.json` edit (accepted DOL).**

## Critiques rejected and why
- **PSRE's "difficulty is the point, don't worry about the confound":** rejected as
  the *sole* stance. Difficulty *is* a legitimate transfer target, but a benchmark
  that can't separate "failed to transfer" from "too hard" is weak. We keep the
  hard cascade AND expose the axis so both readings are possible. Compromise, not
  capitulation.
- **SMR's large multi-channel observation delta:** rejected for feasibility (sim
  can't render it).

## Final deliverable (unchanged count)
3 pairs / 6 YAMLs (numbers 80-85) + `pairs_manifest.json`, generated and validated
by `make_pairs.py`. Invariant asserted in code: within a pair, equal failure_class
and fix tool, unequal topology node count.
