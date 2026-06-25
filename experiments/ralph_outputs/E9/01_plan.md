# E9 — 01 Plan

## Task
Compare **Fireball transfer** vs **synthetic SRE data augmentation**: which helps more
as a data source for seeding an SRE diagnosis policy? Design the head-to-head, build
the synthetic arm (which we *can* build), run it, and document the Fireball blocker.

## Disambiguation (what these two arms actually are)
- **Fireball-transfer arm**: the project's trajectory schema is *inspired by* the
  FIREBALL D&D dataset (Zhu et al. 2023) — structured `state_before → tool → state_after`
  (see `ARCHITECTURE.md:48`, `README.md:12`, `HANDOFF.md:10`). "Fireball transfer" =
  transfer-learn from that **external D&D dataset** into the SRE policy.
- **Synthetic-SRE-augmentation arm**: deterministically synthesize NEW in-domain SRE
  trajectories over the existing 51 CIDG scenarios (`scenarios/cidg/generated/*.yaml`),
  in the same FIREBALL-schema, with within-group reward spread.

## Objective
1. Build a synthetic SRE trajectory **augmenter** (real, runnable, offline).
2. Build a **comparison harness** that scores both arms on data-trainability metrics
   (n_trajectories, label_coverage, within-group spread, domain_match, floor check).
3. Run the synthetic arm over all 51 scenarios; produce a verdict.
4. Honestly document why the Fireball arm is **blocked** for an offline frozen-LLM worker.

## Files to create (all task-namespaced under E9/)
- `artifacts/synth_sre_augmenter.py` — the augmenter (no LLM, no external data).
- `artifacts/compare_arms.py` — the head-to-head harness + verdict.
- `artifacts/augmented_trajectories.jsonl` — real generated output.
- `artifacts/comparison_result.json` — real comparison output.

## Files to modify
- NONE. No shared core file (`rex/*`, `sim/*`, `agent/*`, `experiments/*.py`) is edited.

## Dependencies
- PyYAML (already in repo), Python 3.13 stdlib. No API key, no network, no GPU.

## Risks
- "Fairness" risk: comparing a measured arm to a blocked arm is not a trained-accuracy
  verdict — must frame as a **data-quality** verdict and state the caveat loudly.
- Coverage-metric risk: raw scenario `root_cause.kind` strings are more granular than a
  canonical class vocabulary → label_coverage may read low; must report honestly.
- Reward-consistency risk: augmenter must mirror `rex/scoring.py` weights, not invent a
  rubric.

## Success criteria
- Augmenter runs over all 51 scenarios, every group has within-group spread > 0.
- Self-test passes (positive=1.0, trap<0, empty=0, deterministic).
- Comparison harness emits a verdict JSON scoring both arms with an explicit blocker.
- Floor check passes (empty/trap < pass threshold).
