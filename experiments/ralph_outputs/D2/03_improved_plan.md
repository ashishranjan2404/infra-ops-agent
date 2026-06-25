# D2 — 03 Improved Plan

## What changed after the grill

1. **Preflight is now step 0, not an afterthought (DOL).** The launcher hits
   `hud models list`, enumerates trainable Qwen bases, and exits non-zero if the requested
   base is absent. This turned the task from "train 14B" into the honest deliverable:
   "14B is not on the Tinker gateway → launcher + documented substitute + blocker."

2. **Substitute is described honestly (SMR, accepted).** No literal 14B exists. Closest
   *dense* rung above 8B is `Qwen/Qwen3.6-27B` (≈2x the asked params — stated as such, not
   sold as a clean 14B). MoE alternative `Qwen/Qwen3-30B-A3B` (~3B active, cheaper, already
   partially trained as `opensre-qwen3-30b`) is offered for the compute-sensitive path.

3. **No silent reset-head / missing-head training (AAAI, accepted) — but no core edit
   (RLE, accepted).** Rather than patch `train_rft_v2.py`'s swallow-on-exception reset-head
   (which would touch a shared core file the brief forbids), the launcher (a) preflights so
   you never train a non-existent base, and (b) documents the reset-head caveat in the config
   + critique as a follow-up. Parallel-safety beats a mid-run core edit.

4. **Reuse the v2 loop verbatim (RLE, accepted).** The launcher imports `train_rft_v2.run`;
   it adds only base-selection + preflight. Zero changes to the proven rollout/reward/step loop.

## Critiques rejected (and why)
- **SMR "confirm reward headroom before scaling":** valid research hygiene, but rejected as
  a *blocker* — DOL's existence check strictly dominates (can't train a model that isn't
  there). Noted as a recommended pre-step in the config, not gating this deliverable.
- **AAAI "patch reset-head now":** rejected as written because it requires editing core under
  parallel execution. Re-scoped to "document + preflight," which achieves the safety goal
  without the forbidden edit.

## Net plan
Thin additive launcher (`train_rft_qwen14b.py`) + canonical config YAML
(`qwen14b_train.config.yaml`) + a real preflight executed against the live gateway. Real
30-step training is out of the 15-min compute cap and against an unavailable base, so it is
explicitly NOT run; no metrics fabricated.
