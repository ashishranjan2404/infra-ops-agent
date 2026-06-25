# D6 — 09 Critique (honest)

## What a reviewer will attack
1. **No actual DPO training run.** The strongest critique: we deliver pairs + config +
   scaffold but no trained checkpoint or before/after eval, because there's no GPU/
   torch/trl backend here and closed models aren't trainable. Mitigation: the scaffold
   is genuinely runnable (validated dry-run) and the blocker is specific/actionable.
   To close it: `hud models fork Qwen/Qwen3-8B` then run train_dpo.py on a GPU host and
   eval with rex/eval_pass_at_k.py. This is a deferred run, not a fabricated result.
2. **Approximate prompt reconstruction.** Specs are templated ({{SVC}}, {{NS}}
   unfilled). The realized prompt the model actually saw isn't stored in the trajectory
   record, so we rebuild an approximation. DPO's preference is between two answers to
   the SAME prompt, so the relative gradient is robust to this — but a purist would want
   the exact realized prompt carried in the trajectory. Future work: log prompt in the
   trajectory exporter.
3. **Off-policy preference data.** Trajectories come from many different models, not the
   policy under training. DPO tolerates this, but it's not on-policy DPO; expect smaller
   gains than iterative on-policy preference optimization.
4. **Judge = generator = evaluator.** The same deterministic judge produces the
   preference signal and would score the eval. That's internally consistent but risks
   optimizing to the judge's blind spots (e.g. keyword-matching evidence). A human spot-
   check of a sample of chosen>rejected pairs would strengthen the claim.
5. **Pair volume is modest.** 81 pairs is small for DPO; enough to validate the pipeline
   and smoke-train, not to expect a large policy shift. Scaling needs more trajectories
   per scenario (the generator already supports more models/samples).

## Honest status
The *deliverable* (constructor + config + scaffold + passing unit test on
pair-construction) is complete and real. The *downstream training run* is blocked on
GPU/backend availability and is documented, not faked.
