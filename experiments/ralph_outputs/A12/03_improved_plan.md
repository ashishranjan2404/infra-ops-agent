# A12 — 03 Improved Plan

## What changed after the grill
1. **Explicit "prior, not measured" framing.** The output's `signal` field and all
   docs state the difficulty is a *static structural prior*, not empirical pass-rate.
   (Accepts REV + SMR.)
2. **Expose everything for re-tuning.** `curriculum_order.json` carries the full
   `weights` dict and a per-incident `features` vector, so a downstream user can
   re-weight or drop to a single component without re-parsing YAML. (Accepts RLE.)
3. **Anchor on the split everyone trusts.** The dominant weighted terms are the
   "trap" booleans (`loud_not_cause`, `hidden`, `cascades`, `hysteresis`) that
   cleanly separate the 8 simple-leaf clones from the real-outage cascades; raw
   topology size is only a gentle tiebreaker. (Accepts PSRE.)
4. **Model-free + deterministic.** No `agent.llm.call`, no HUD. Stable secondary
   sort on `id` so ordering is byte-reproducible. (Accepts DEVO.)

## Critiques accepted
- REV "magic weights": accepted *as a documentation/exposure requirement* — weights
  are emitted and explained, ablatable.
- SMR/PSRE "static ≠ learner difficulty within hard tier": accepted as a stated
  limitation + future-work item (correlate vs pass@k from `rex/eval_pass_at_k.py`).

## Critiques rejected (with reason)
- REV "must be empirically derived or it's uncitable / a null result": **rejected as
  a blocker.** Empirical difficulty requires a 36-incident × multi-model pass@k sweep
  — a separate, expensive task. A12's deliverable is the *ordering artifact*. We ship
  the defensible static prior now and leave calibration as future work; the artifact
  is explicitly versioned so re-calibration is a drop-in.
- RLE "monotone order is enough, skip rigor": **partially rejected** — we still
  document weights and provide the feature vector so the order is inspectable, not a
  black box.

## Final shape (unchanged core, hardened)
- `build_curriculum.py`: parse every `*.yaml`, join `registry.json` for
  `red_herrings`/`family`, compute feature vector → weighted score, sort easy→hard,
  emit JSON with weights + features + ranked list.
- Re-run at the end (parallel workers may still be writing scenarios).
