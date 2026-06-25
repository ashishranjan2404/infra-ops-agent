# E9 — SUMMARY

**Task:** Compare Fireball transfer vs synthetic SRE data augmentation — which helps more?

## What got done
Designed the head-to-head and **built + ran the synthetic-augmentation arm**; **documented the
Fireball-transfer arm as blocked** (external D&D dataset, no fine-tuning stack in this frozen-LLM
project, off-domain) and wired the harness to score a real export if ever provided.

## Real artifacts (all under experiments/ralph_outputs/E9/artifacts/)
- `synth_sre_augmenter.py` — deterministic, offline synthetic SRE trajectory augmenter over the
  51 CIDG scenarios; FIREBALL-schema (state_before→tool→state_after→reward); 1 positive + 3
  graded negatives per variant; seeded perturbations; mirrors `rex/scoring.py` weights;
  hermetic `--self-test` (9/9 PASS).
- `compare_arms.py` — head-to-head harness scoring both arms on a shared metric vector
  (n_traj, label_coverage, within-group spread, domain_match, floor check) + verdict.
- `augmented_trajectories.jsonl` — 51 scenarios → 204 groups → 816 trajectories, every group
  with positive within-group spread (mean 0.5745).
- `comparison_result.json` — the scored comparison + verdict.

## Result
Synthetic-SRE-augmentation wins **on available evidence** (in-domain, 816 trainable
trajectories, non-zero spread on all 204 groups, floor check holds). **Caveat:** the Fireball
arm is blocked, not measured — this is a data-quality / seeding verdict, not a trained-accuracy
verdict ("816 vs 0" is an availability gap, not a learned-performance gap).

## Verification
Self-test 9/9 PASS; 204/204 groups parse with spread > 0; byte-identical on rerun; both result
JSONs valid. No shared core file edited.

## Honest caveats
- `label_coverage=0.10` is a vocabulary-naming artifact — the data covers 15 real failure
  mechanisms (only 2 string-match the canonical class set).
- Synthetic positives are monocultural (one canonical reasoning path) — the arm's true weakness.
- Rewards are construction artifacts (great for SFT cold-start, weak as a standalone RFT signal).
