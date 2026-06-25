# E6 — 03 Improved Plan

## What changed after the grill

1. **Strict step partition (accepted, SMR/RLE).** assistant steps → action_only,
   tool steps → state_only, with an explicit test:
   `len(state_only.trajectory) + len(action_only.trajectory) == len(full.trajectory)`.
   This makes the ablation falsifiable rather than vibes-based.

2. **Remediation key-split, overlap allowed (accepted, RLE).** The `remediation`
   dict is split by key, NOT strictly partitioned with the steps:
   - state_only keeps: `primary_metric, direction, state_before, state_after,
     recovery_check, resolved`.
   - action_only keeps: `fix_tool, canonical_fix, trust_tier`.
   Rationale: the remediation block is a separate channel from the step log; forcing
   the canonical fix out of action_only would make action_only useless.

3. **Gold action sequence treated as an action channel (accepted, SMR).**
   `answer.optimal_trajectory` and `answer.required_queries` are demonstrated actions,
   so state_only strips them.

4. **RL caveat documented (accepted, RLE).** action_only has no `state_after` →
   `recovery_check` cannot be evaluated → the variant is SFT-only, not RL-able. Stated
   in the spec and critique.

5. **No metrics table (accepted, AAAI/DOL).** The harness reports only structural,
   deterministic facts (counts, mean steps, channel composition). Train/eval is a
   documented BLOCKER.

## Rejected / deferred
- PSRE's "dashboard vs runbook" as a *finding* — **rejected**; kept only as motivation
  (AAAI was right that it over-claims as a result).
- Duplicating evidence into both variants for "fairness" — **rejected**; evidence is
  pure observed state, belongs only in state_only. Keeping the partition clean matters
  more than symmetry.

## Final deliverable set (unchanged in scope)
`fireball_ablate.py`, `fixture_fireball.jsonl`, `test_fireball_ablate.py`,
`run_ablation_e6.py`, plus the emitted `_variants/` and a JSON report. Validated on the
synthetic fixture and the 319-record in-repo opensre corpus.
