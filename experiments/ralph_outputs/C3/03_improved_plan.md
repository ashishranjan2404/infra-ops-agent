# C3 — 03 Improved Plan

Revisions after the grill. Format: change · source critique · accept/reject + why.

## Accepted
1. **Narrow the claim to "language-expressible safety boundary."** (SMR, REV)
   The headline is NOT "synthesis matches the human harness." It is: *given a rule
   language over 6 known features, synthesis autonomously recovers the expressible
   safety boundary from novel-incident labels and transfers it to held-out novel
   incidents.* The structural ceiling is stated before any number.

2. **Held-out false-allow rate is the headline metric; report run-to-run variance.**
   (PSRE, RLE) → ran the synthesis twice; both runs gave identical held-out numbers
   (FA% = 0.059, acc = 0.941). Recorded in `07_test_results.md`.

3. **Runtime-enforced provenance.** (DEVO, REV) The runner now:
   - loads `A8/artifacts/heldout_manifest.json` and uses its `held_out` list as the
     novel universe;
   - `assert (TRAIN ∪ HELDOUT) ⊆ A8.held_out` — fails loud if any id isn't certified novel;
   - `assert TRAIN ∩ HELDOUT = ∅`.

4. **Pin + justify the model.** (DEVO) Model and budget are read from env (default
   `claude-haiku-4-5`), recorded in stdout AND `novel_synth_result.json`. Run with
   `gpt-5.5` (HUD gateway) because Anthropic credits are exhausted (HTTP 400). The
   swap is justified: synthesis is model-agnostic (the operator only emits a JSON rule
   list; we never exec model output; the trusted interpreter is identical).

5. **Hazard-coverage table up front.** (SMR) The runner prints, per hazard, which
   incidents in each split exhibit it and tags each GENERALIZABLE / out-of-scope.

## Rejected
- **"Must learn `trap_action` too."** (implied by SMR R1) Rejected: `trap_action` is a
  per-scenario spec list with no general feature; expressing it would require either
  per-incident rules (memorization — defeats the test) or a new feature (changes the
  shared core, forbidden by the brief). I report it as a *structural ceiling*, which
  REV explicitly accepted as fair in R2.
- **"Single safe run is enough."** (PSRE R2) Rejected in favor of RLE's point: I report
  variance, because a stochastic operator's single safe run could be luck.

## Net design
Self-contained `run_novel_synth.py` importing (never editing) `rex/harness_synth.py`;
novel-only TRAIN(10)/HELDOUT(5) split drawn from A8; gpt-5.5 operator, budget 8;
emit metrics + leakage proof to JSON.
