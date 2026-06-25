# F7 — 08 Verification

## Success criteria (from 01_plan.md) → status

| Criterion | Status | Evidence |
|---|---|---|
| 8–12 attacks, each steelman + honest response + severity + closing evidence | ✅ | 10 attacks A1–A10; validator confirms all 5 labels per block |
| Two-axis severity (probability + depth) | ✅ | every attack has Probability and Depth; enums validated |
| All 5 mandated weakness themes present | ✅ | `check_themes` returns []: synthetic_data, small_n, flat_rft, reward_hacking, single_domain |
| `attacks.json` parses | ✅ | T1 |
| `validate_attacks.py` exits 0 | ✅ | T2 final run, EXIT=0 |
| Concession ledger present | ✅ | `## Concession ledger` (4 items) |
| "What would actually sink the paper" present | ✅ | `## What would actually sink the paper` section |
| Top-line callouts (highest-probability / highest-depth) | ✅ | validator regex checks both; present |
| No shared core files edited | ✅ | only `experiments/ralph_outputs/F7/**` created |

## Are outputs real (not placeholder)?
Yes. Each attack cites a concrete, checkable repo fact rather than a generic objection:
- A4 quotes the actual flat training trace `0.522 → 0.491` (verified present in
  `opensre-traj/hud_env_v2.py` / `train_rft_v2.py`).
- A6 reproduces the `0.86 = (4×1.0 + 0.30)/5` arithmetic from ARCHITECTURE.md (validator forces
  this string to be present).
- A5/A8 reference the exact reward `0.30·diag + 0.25·fix + 0.45·resolved − 0.60·trap` and the
  deterministic-judge fallback in `rex/scoring.py`.
- A1 grounds "n=5" in the real 5-model × 5-incident headline sweep.
- A3/A7 reference the real corpus: ~51 CIDG YAML + 19 reconstructed post-mortem JSON specs.

## Honest gaps (carried to 09)
- The validator checks *structure and substance length*, not semantic quality of arguments — a
  human read confirms the arguments are non-trivial, but that judgment is not automated.
- The doc anticipates attacks; it does not *run* any of the proposed mitigations (CIs, human-SRE
  agreement study) — those are recommendations, correctly scoped as future work, not results.
