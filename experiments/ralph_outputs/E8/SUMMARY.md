# E8 — SUMMARY

**Task:** Measure how much Fireball data is needed (1k? 10k? 50k?). Design a data-size
sweep + sampling/subsetting harness over the Fireball format, with a power-analysis
estimate of required N. Document the Fireball-data blocker. Deliver runnable sweep harness
+ synthetic-fixture validation. Do NOT fabricate scaling curves.

## Outcome: COMPLETED (deliverable) with a documented BLOCKER on the downstream curve

### Delivered (real, runnable)
- `artifacts/fireball_sweep.py` — reader (Fireball-shape tolerant) + stratified/nested
  subsetter + closed-form power analysis (inline inverse-normal, no scipy) + sweep driver
  + gated learning-curve fitter + CLI.
- `artifacts/make_fixture.py` — synthetic 2k-record Fireball fixture (no score field).
- `artifacts/test_fireball_sweep.py` — 13 pytest tests, all passing, incl. two
  anti-fabrication guards (no fit => blocked/no scores; <4 points => no curve).
- `artifacts/fixture_corpus.jsonl` + `artifacts/sweep_manifests/*.json` — real outputs.

### Key numbers
- Real Fireball-format corpus = 319 trajectories, 34 families, difficulty {3:100,4:201,
  5:18}, mean 14.6 steps.
- Power analysis (eval-rollout N/arm, sd~0.22, alpha .05/power .80): delta=0.10->76,
  0.07->156, 0.05->304, 0.03->845, 0.02->1900.

### The blocker
The training data-scaling curve (the literal "1k/10k/50k?" answer) is BLOCKED: the corpus
is 319 records (~100x short of 1k), the original FIREBALL source corpus and a
fireball-trained model slug are not in repo, and a real fit callback (train->eval) would
require editing shared core. The harness degrades honestly — every requested N caps at 319,
blocked:true, no scores and no curve fabricated. The fit-callback seam
((list[Record],str)->float) is pre-defined for a future PR.

### Constraints honored
No shared core files edited (verified). No scaling curve fabricated.
