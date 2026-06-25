# C9 — 06 Implementation

## What I built
A single task-namespaced runner that imports the core synthesizer unchanged and runs it
over the full 42-incident universe:

- `experiments/ralph_outputs/C9/artifacts/run_full42.py` — imports
  `rex.harness_synth` (labeled_examples, confusion, confusion_pred, handwritten_pred,
  is_safe_synth, train_score, propose_ruleset) and `rex.tree.thompson_search`. **No core
  file edited.**
- `experiments/ralph_outputs/C9/artifacts/results_full42.json` — emitted results.

## Key implementation points
- **Universe = `rex.harness._SCENARIOS` (42 incidents)**, asserted in code. Labels for all
  42 are generated deterministically → **580 labeled (tool,target) examples, 253 should-block**.
- **Two splits evaluated:** the core small split (7 train / 3 held-out) and a deterministic
  70/30 incident-level split of all 42 (**29 train / 13 held-out**, seed 0).
- **Three harnesses scored** on each split: seed(empty), synthesized, hand-written `is_safe`.
- **Mutation model swap:** `hs.MODEL` set to `deepseek-v4-pro` (HUD gateway) because the
  Anthropic API returned HTTP 400 "credit balance too low" (verified directly). The
  interpreter (`is_safe_synth`) and reward (`train_score`) are the **unmodified core
  functions** — only the proposal operator's model changed. Documented in the output as
  `synthesis.model`.

## Proposed core change (NOT applied — parallel safety)
To make this a first-class core capability one would add a `--full` / configurable
incident-set + split to `rex/harness_synth.py:main()` and re-run synthesis with the canonical
haiku operator once credits are restored. I did **not** edit the core; the runner replicates
the search via public imports instead. Equivalent diff sketch:
```
# rex/harness_synth.py main():  TRAIN/HELDOUT -> derive from a 70/30 split over _SCENARIOS
```

## Real outputs (from results_full42.json)
- Hand-written `is_safe` whole-set accuracy: **small-10 = 0.871** (FA 16, FB 2, n=140) vs
  **full-42 = 0.933** (FA 37, FB 2, n=580).
- Full-42 split, hand-written `is_safe`: train acc **0.927**, held-out acc **0.944**.
- Synthesized (deepseek operator): collapsed to the empty seed — `best_rules=[]`, every
  search node stuck at the seed score (full 0.408, small 0.464); see `09_critique.md`.
