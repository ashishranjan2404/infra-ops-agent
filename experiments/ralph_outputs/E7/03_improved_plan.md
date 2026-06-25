# E7 — 03 Improved Plan

## What changed after the grill
1. **Reframed the deliverable's claim (accepted AAAI, DVO).** The artifact proves
   *plumbing + a runnable transfer protocol*. Synthetic fixtures validate the
   adapter contract; they are NOT evidence of transfer. Every doc now says this.
2. **Defined the real control as cross-domain zero-shot (accepted RLE, SMR).**
   Transfer protocol = select/configure REx on SRE, evaluate zero-shot on a game
   domain, compare against a domain-native baseline (random-admissible policy and
   a frozen-LLM-in-domain policy).
3. **Kept `available_actions` in the schema but made the oracle-handicap an
   explicit ablation (resolved SMR vs RLE).** Plan reports metrics with and
   without the admissible-command oracle.
4. **Moved reversibility to a caveats section, not the schema (resolved DVO vs
   PSRE).** Schema is shape-only.
5. **Plural metrics (resolved PSRE vs AAAI):** episode-success rate, deterministic
   judge pass-rate, action-overlap-with-gold, normalized game score.

## Critiques accepted
- AAAI "synthetic ≠ evidence" → scope statement added to 06/08/09.
- RLE "valid_actions is an oracle handicap" → ablation + schema warning when an
  action isn't in `available_actions`.
- SMR "need cross-domain negative control" → protocol specifies native baselines.

## Critiques rejected (with reason)
- PSRE "incidents are irreversible so the analogy is invalid" → **rejected for
  the adapter scope**: irreversibility is a reward/env property, not a trajectory
  *shape* property; the adapter is shape-only and stays domain-general. Kept as a
  documented caveat in the experiment plan so the SRE story isn't overclaimed.
- "Pick one headline metric early" → rejected; plural metrics retained.

## Final shape
Schema + registry + 4 adapters + projection into the existing judge; synthetic
fixtures; pytest incl. a real `rex/scoring` call; transfer-experiment plan with
baselines, metrics, ablations, and the live-data blocker.
