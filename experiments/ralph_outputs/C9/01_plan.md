# C9 — 01 Plan

## Objective
Run/evaluate the synthesized safety harness (`rex/harness_synth.py`) across **all 42
incidents** the harness knows (currently it synthesizes on 7 train / 3 held-out = 10).
Report `is_safe` accuracy on the **full 42-incident set** vs the **small 10-incident
split**, under a ~15-min compute cap.

## Grounding
- `rex/harness_synth.py` is an AutoHarness-style synthesizer: a Thompson-tree search
  (`rex/tree.py:thompson_search`) over a *data* rule-set, interpreted by trusted code
  (`is_safe_synth`). The mutation operator is an LLM (`MODEL = claude-haiku-4-5`); the
  reward is classification accuracy on TRAIN labels. The hand-written `is_safe`
  (`rex/harness.py`) is the human baseline.
- `rex.harness._SCENARIOS` contains exactly **42** incidents; `harness_synth.TRAIN`
  (7) + `HELDOUT` (3) only touch 10 of them — the rest are the "full set" this task asks
  us to evaluate on.
- Label generation (`labeled_examples`, `ground_truth`) is fully **deterministic** — no
  LLM needed to evaluate any harness. Only *synthesis* needs the LLM.

## Approach
1. Build the full label universe over all 42 incidents (deterministic).
2. Keep the core `harness_synth.py` SMALL split (7/3) as the reference small split.
3. Add a deterministic 70/30 incident-level split over all 42 for the full run.
4. Synthesize a rule-set on the full-42 train split (and, for comparison, re-synthesize
   on the small split) using the **same** interpreter + reward; only the *incident set*
   and *mutation model* change.
5. Evaluate THREE harnesses — seed(empty), synthesized, hand-written `is_safe` — on both
   splits; report train vs held-out accuracy and the headline `is_safe` accuracy
   (small-10 whole-set vs full-42 whole-set).

## Files to create (task-namespaced, no core edits)
- `experiments/ralph_outputs/C9/artifacts/run_full42.py` — runner (imports core).
- `experiments/ralph_outputs/C9/artifacts/results_full42.json` — emitted results.

## Dependencies / risks
- **Anthropic credits exhausted** (verified: 400 "credit balance too low"). Mitigation:
  swap the *mutation model only* to a HUD-gateway model (`deepseek-v4-pro`) — interpreter
  and reward are byte-identical to core, so it's still a real synthesis run. If the
  gateway also fails, degrade to a deterministic-only run (seed + hand-written) and report
  the blocker honestly; the headline `is_safe` accuracy is LLM-independent and still real.
- Compute cap 15 min: keep search budget small (6 nodes per search, 2 searches ≈ 12 LLM
  calls). Evaluation is sub-10s.

## Success criteria
- Real run over all 42 incidents; `results_full42.json` with concrete numbers.
- Headline: `is_safe` accuracy on full-42 vs small-10 reported with FA/FB breakdown.
- No shared core file edited.
