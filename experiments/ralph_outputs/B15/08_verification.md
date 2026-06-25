# B15 — 08 Verification

## Against success criteria (from 01_plan)

| Criterion | Met? | Evidence |
|---|---|---|
| Table renders from script, no hand-edits | ✅ | `gen_comparison.py` writes `comparison_table.md`; numbers pulled from A1/A2 JSON at run time |
| Our numbers come from real A1/A2 artifacts | ✅ | `load_our` reads `full_pass_at_k_glm-5p2.json` & `ablation_pass_at_k_deepseek-v4-pro.json`; selftest cross-checks rex≈0.897 |
| Every SREGym number cited | ✅ | `sregym_reported.json` carries `source` per row + `version_note`; report Sources section |
| Caveats enumerate ≥6 non-equivalence axes | ✅ | 10 numbered caveats (substrate, grader, attempts, oracle, threshold, decomposition, models, noise, overlap, mapping) |
| Script parse-checks & runs on Python 3.13 | ✅ | `py_compile` OK; `--selftest` exit 0; full run exit 0 |

## Are outputs real (not placeholder)?
- **Yes.** `our_pass_at_1.json` is generated from disk, not typed: re-running regenerates
  identical numbers traceable to A1/A2. SREGym numbers are transcribed from the paper +
  leaderboard with per-row citations (not fabricated; verifiable against the cited URLs).
- The headline framing deliberately avoids a false "we beat SREGym" claim — the `attempt_regime`
  column and the bold REx caption enforce the non-equivalence.

## Honesty checks
- We **do not** claim REx's 0.90 beats SREGym's 0.61. We explicitly state REx is multi-attempt +
  oracle with **no SREGym counterpart**, and that our fair single-attempt band (~0.31–0.34)
  sits **below** SREGym's E2E range — i.e. SREGym is harder.
- Threshold sensitivity (0.8), model mismatch, noise-off assumption, and zero task overlap are
  all disclosed.

## Verdict: meets all stated success criteria; deliverable is real and honest.
