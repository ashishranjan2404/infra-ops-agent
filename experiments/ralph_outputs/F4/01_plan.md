# F4 — Publication-quality figures · 01_plan

## Objective
Produce a self-contained matplotlib script that renders publication-quality figures
(pass@k bars with CIs, by-family breakdown, pass@k scaling curve, McNemar paired test,
model-frontier lift, learned-harness generalization) **from real result JSONs** and run
it to emit real PNGs. No fabricated numbers; no edits to shared core files.

## Approach
Ground the figures in existing real artifacts:
- `experiments/ralph_outputs/A1/artifacts/summary_table.json` — glm-5p2, 126 ep/condition
  (42 incidents × 3 seeds × 5 conditions). Per-condition pass@1/2/5, Wilson CI, by-family.
- `experiments/ralph_outputs/A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json` — 750 ep.
- `experiments/ralph_outputs/A2/artifacts/ablation_v2_mcnemar_deepseek-v4-pro.json` — McNemar.
- `rex/runs/frontier.json` — 5 models × 5 scenarios, REx vs baseline mean reward.
- `rex/runs/harness_synth_v2.json` — learned safety harness held-out accuracy / false-allow.

Mirror the column/condition ordering and threshold semantics already used in
`experiments/generate_paper_tables.py` (COND_ORDER, threshold 0.8) for consistency with the
Chrome-rendered tables.

## Files to create (all task-namespaced)
- `experiments/ralph_outputs/F4/artifacts/make_figures.py` — the generator.
- `experiments/ralph_outputs/F4/artifacts/figures/*.png` — the rendered figures.
- `experiments/ralph_outputs/F4/artifacts/run.log` — captured run output.

## Dependencies
matplotlib (3.11) + numpy (2.4), already installed. `Agg` backend (headless). No network.

## Risks
- Result JSON schema drift (A1 uses `p1/ci`, A2 uses `pass@1/ci95`). Mitigate by reading
  each file with its own accessor.
- `heldout_table` shape unknown until inspected. Mitigate by inspecting before finalizing.
- Accidentally writing into shared `experiments/figures/`. Mitigate: hard-code OUT under F4.

## Success criteria
- Script runs to completion, 0 errors, emits ≥5 PNGs, each ≥150 DPI and non-empty.
- Every number on every figure traces to a real JSON field (spot-checked).
- No shared core file modified.
