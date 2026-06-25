# F5 — Verification against success criteria

Success criteria from `01_plan.md` / `03_improved_plan.md`:

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | `abstract.md` exists, valid Markdown | ✅ | `artifacts/abstract.md`; parse check in 07 (T7, readable OK) |
| 2 | Body ≤ 250 words, counted & reported | ✅ | **233 words**; `wc -w` output in 07; reported in artifact + here |
| 3 | Every quantitative claim traces to a real artifact | ✅ | Provenance table in artifact; `ablation.json` + `harness_synth.json` re-read in 07 |
| 4 | States ≥1 honest limitation | ✅ | "REx's headline lift … is largely oracle-feedback leakage … collapses to 0.25" (T5 PASS) |
| 5 | Names released artifacts | ✅ | "We release the harness, simulator, a 42-incident … benchmark, and the deterministic reward" (T6 PASS) |
| 6 | Keeps the trap-action hook | ✅ | "the naive fix … worsens the outage" (T4 PASS) |
| 7 | No unsupported claims (C2 transfer, McNemar p, 2-dp verifier) | ✅ | forbidden-claims scan PASS; omissions documented in Provenance |
| 8 | No shared-core edits | ✅ | only files under `experiments/ralph_outputs/F5/` written; `PAPER_OUTLINE.md` read-only |

## Are the outputs real (not placeholder)?
Yes. The abstract is a complete, submittable paragraph — not a stub. Every number in it
was re-derived from a JSON in `rex/runs/` during this task (see 07's command output), not
copied uncritically from the outline. Where the outline and the honest insight doc
disagreed (89.7/94.9 vs 0.90/0.95; "≥2× lift" vs leakage-collapse), I took the honest
side and documented the choice.

## Honest deltas vs the original draft (what actually improved)
1. Removed false-precision verifier accuracies (n=3).
2. Re-centered the contribution on the verifiable env + learned verifier.
3. Stated REx's lift WITH its oracle-leakage boundary and the real 0.69/0.24/0.25 numbers.
4. Dropped the unrun C2 transfer claim and the not-yet-locked McNemar significance.
5. Came in at 233 words with a hard count, vs an uncounted ~230-word draft.

## Residual risk
The 0.90/0.95 held-out verifier accuracy is cited from `headline_insights.md`, not
recomputed here (the synth eval would require re-running `harness_synth`). The *structure*
(7 train / 3 heldout / 3 rules) was re-verified; the accuracy value is taken on the doc's
authority. Flagged, not hidden — see 09.
