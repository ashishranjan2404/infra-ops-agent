# E9 — 08 Verification

## Success criteria vs. evidence

| Criterion (from 01) | Met? | Evidence |
|---|---|---|
| Augmenter runs over all 51 scenarios | ✅ | `{"scenarios":51,"groups":204,"trajectories":816}` |
| Every group has within-group spread > 0 | ✅ | "groups with zero spread: 0"; mean 0.5745 |
| Self-test passes (pos=1.0, trap<0, empty=0, deterministic) | ✅ | 9/9 PASS, byte-identical rerun |
| Comparison harness emits verdict scoring both arms + blocker | ✅ | `comparison_result.json` (valid JSON, both arms scored, blocker text present) |
| Floor check passes (empty/trap < pass threshold) | ✅ | `floor_check_pass: true` |
| No shared core file edited | ✅ | only `experiments/ralph_outputs/E9/**` written (see git status) |

## Are outputs real, not placeholder?
- `augmented_trajectories.jsonl` — **816 real records** derived from real CIDG YAML gold
  labels; parse-checked; each carries real `state_before/action/state_after/reward`.
- `comparison_result.json` — computed from that file, not hand-written.
- Both producer scripts run end-to-end with a hermetic self-test.

## What the verdict does and does NOT claim
- **Does** claim: as a *seeding data source*, synthetic-SRE-augmentation dominates on the
  measurable data-quality axes (in-domain, 816 trainable trajectories, non-zero spread, floor
  holds).
- **Does NOT** claim: a trained-accuracy win. The Fireball arm is **blocked**, so "816 vs 0"
  is a coverage/availability gap, not a learned-performance gap. This caveat is encoded in
  `verdict.caveat`.
- `positive_pass_rate=1.0` is a **floor-sanity** signal (positives are constructed to score
  1.0), explicitly **not** a model-accuracy number.

## Reproducibility
Deterministic (SHA1-seeded RNG, no LLM, no network, no wall-clock). Re-running yields
byte-identical artifacts — verified by `diff`.
