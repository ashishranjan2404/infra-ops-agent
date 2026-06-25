# C4 — 06 Implementation

## What I built
1. **`artifacts/rule_interpretability.md`** — the primary deliverable. A grounded
   interpretability analysis of the 3 synthesized rules from `rex/runs/harness_synth_v2.json`:
   per-rule what/corresponds-to/why/failure-modes/worked-example, three scored interpretability
   yardsticks, the v1→v2 collapse evidence, the held-out-miss classification, the
   by-construction provenance, and honest limitations.
2. **`artifacts/validate_rules.py`** — a runnable validator that imports the REAL trusted
   interpreter (`rex.harness_synth.is_safe_synth`, `confusion`, `labeled_examples`), re-applies
   the 3 v2 rules to the held-out incidents, prints worked examples + the false-allow breakdown,
   and asserts the result matches the published JSON (3 rules, 4 false-allows, 0 false-blocks,
   acc 0.897). Exits 0 on success.

## Key findings (all verified by running the validator, not asserted)
- The 3 rules reproduce the published held-out confusion **exactly**: acc **0.897**,
  false_allow **4**, false_block **0**, FA-rate **0.308** (39 held-out labels).
- R1 (`treats_forbidden_category`, ANY tool) and R3 (`rollback_deployment` +
  `rollback_without_deploy`) are **clean recoveries** of hand-written `is_safe` clauses.
- R2 **broadens** the hand-written leak clause: it blocks `clear_cache`/`scale_deployment` during
  a leak, which `is_safe` does not — deliberate conservatism (FA weighted 2× FB), and held-out
  FB-rate stayed 0.
- The 4 held-out false-allows are **0 synthesis-quality misses**: 2 are `last_ready_node` (a
  hazard absent from TRAIN, out of scope) and 2 are `trap_action` (unlearnable from the 6
  features — `is_safe` misses them too).
- The v1→v2 collapse (10→3 rules, +0.025 acc, −0.077 FA) is concrete evidence that the complexity
  penalty + minimality nudge drove both interpretability AND correctness.

## Source files read (not modified)
- `rex/harness_synth.py` (full) — synthesis machinery, interpreter, scoring, mutation operator.
- `rex/harness.py` (full) — hand-written `is_safe`, `TOOL_TREATS`, scenario configs.
- `rex/runs/harness_synth_v2.json` (the 3 rules) and `rex/runs/harness_synth.json` (v1, 10 rules).

## Shared-core safety
No shared core file was edited. The validator imports `rex.harness_synth` **read-only** and never
calls `main()` (which would rewrite `rex/runs/harness_synth.json`). All new files live under
`experiments/ralph_outputs/C4/`. No proposed `.patch` to core was needed — this is a pure analysis
task; the rules already exist as data.
