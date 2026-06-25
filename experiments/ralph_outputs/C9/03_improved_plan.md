# C9 — 03 Improved Plan

## What changed after the grill
1. **Headline reframed to the hand-written `is_safe` baseline** (PSRE/RLE). The task says
   "report `is_safe` accuracy on the full set vs the small split" — `is_safe` is the
   hand-written harness, which is LLM-independent. So the headline = `is_safe` whole-set
   accuracy, **small-10 vs full-42**, with false-allow / false-block broken out (not just
   accuracy, per PSRE: FA is the catastrophic metric).
2. **Kept the synthesized train/held-out report** (SMR, accepted). Whole-set accuracy alone
   reads as a generalization claim; we also evaluate the synthesized harness on a 70/30
   incident-level split of the full 42 AND on the small split, so the AutoHarness framing
   survives.
3. **Universe pinned to `rex.harness._SCENARIOS` = 42** and cited (AR, accepted). The
   `scenarios/cidg/generated/` YAML dir has ~51 files; that is a superset and NOT the
   harness's incident set, so we do not use the file count.
4. **Mutation model named explicitly** (RLE/AR, accepted). Anthropic credits are exhausted
   (verified 400). We swap the mutation operator to the HUD gateway (`deepseek-v4-pro`);
   the interpreter (`is_safe_synth`) and reward (`train_score`) are byte-identical to core,
   so it is a real synthesis under the same objective — just a different proposal operator.
   The output records which model fired.
5. **Budget capped, eval decoupled** (DOL, accepted). 6 nodes per search, the deterministic
   evaluation runs with zero LLM cost so the headline always ships even if the gateway dies.

## Rejected / deferred
- **AR's "swap invalidates the run"** — rejected (RLE). It would invalidate a *like-for-like*
  comparison to the canonical haiku `harness_synth.json`, which we do not claim. We flag the
  model and treat the synthesized numbers as illustrative, not canonical.
- **SMR's push to make held-out the headline** — deferred. We report it but the task's literal
  ask (is_safe full vs small) is the headline.

## Final deliverable
`run_full42.py` (imports core, no edits) + `results_full42.json` with: 42-incident label
counts; small-10 and full-42 splits; `is_safe` whole-set accuracy small vs full (FA/FB);
seed/synthesized/hand-written train-vs-held accuracy on both splits; synthesis metadata
(model, node scores, rules) or a documented blocker.
