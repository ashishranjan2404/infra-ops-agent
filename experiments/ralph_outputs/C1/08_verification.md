# 08 — Verification against success criteria (from 01/03)

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Driver runs end-to-end offline within the cap, emits a JSON sweep table | ✅ | runs in <1s; `lambda_sweep_offline.json` written, parse-valid |
| 2 | Sweep shows an interpretable lambda response: conditions fall as lambda grows, held-out accuracy degrades past a threshold | ✅ | 3→2→0 rules; HO acc 0.744→0.718→0.667 across lambda 0→0.03→0.08 |
| 3 | `score_with_lambda(rs, ex, 0.003) == train_score(rs, ex)` exactly | ✅ | `test_score_matches_train_score_at_default_lambda` passes (<1e-12 on `[]` and a 2-rule set) |
| 4 | All tests pass | ✅ | 6/6 driver tests, 9/9 core tests green |
| 5 | No shared core files edited | ✅ | `harness_synth.py` untracked & unchanged by me; only NEW files under `C1/artifacts/` created |

## Are the outputs REAL (not placeholder)?
- `lambda_sweep_offline.json` is produced by an actual `thompson_search` run over real
  labeled examples (101 train / 39 held-out labels) derived from the real CIDG scenarios via
  `harness_synth.labeled_examples`. Accuracies/false-allows are computed by the core
  `confusion`. Reproducible bit-for-bit (deterministic operator).
- The hand-written baseline (TRAIN 0.842 / HELD-OUT 0.949) is computed live via
  `handwritten_pred`, not copied.
- The real-API result is a REAL attempt with a REAL provider error captured (request_id
  included), not a fabricated number — the honest outcome is "blocked by billing".

## Scope honesty
The offline operator is a deterministic greedy stand-in, weaker than the haiku operator the
real `harness_synth.py` uses (3 rules vs the committed run's 10). The deliverable is therefore
the *shape of the lambda response under a fixed operator*, plus the committed real numbers as a
reference point — NOT a claim that these absolute accuracies are the production harness's.
This is stated in 06/07/09 and labelled (`mode`) on every JSON row.
