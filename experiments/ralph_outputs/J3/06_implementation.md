# 06 — Implementation

All artifacts are task-namespaced under `experiments/ralph_outputs/J3/artifacts/`. No shared
core files were edited. Source data (`opensre-traj/out/hud_trajectories.jsonl`) was read only.

## Artifacts built
1. **`diagnoses_to_rate.json`** — the rating set. 12 **real** agent diagnoses sampled from
   197 HUD trajectory runs. Each item carries the incident, source company, difficulty,
   tools used, and the full agent RCA `answer` text. Stratified across 3 models
   (claude-opus-4-8 / claude-haiku-4-5 / kimi-k2p5), difficulty 3–5, and auto-reward
   0.11–0.75 to guarantee quality spread. Blinded (no model identity).

2. **`blinding_key.json`** — sealed key mapping each `item_id` → model, trace_id, and the
   automated `auto_reward` + `auto_subscores` from the deterministic judge. Used by the
   analysis step to compute the human-vs-auto-reward validity correlation. Not shown to raters.

3. **`rubric.md`** — anchored 1–5 Likert rubric for correctness / usefulness / safety, plus a
   binary `confident_root_cause` trust item. Every Likert point has a concrete behavioral
   anchor. Includes the "rate the claim, not the prose" and "safe-or-correctly-defers" fixes
   from the ouroboros pass.

4. **`protocol.md`** — full study protocol: RQ, within-subjects crossed design, blinding,
   stratified sampling, eligibility/recruitment (where the blocker lives), consent/ethics,
   step-by-step procedure with post-rating ground-truth reveal, the pre-registered IAA +
   validity analysis plan, and a 1-rater pilot fallback for graceful degradation.

5. **`ratings_template.csv`** — blank CSV (header + 12 pre-filled `item_id` rows) each rater
   copies and fills.

6. **`score_human_eval.py`** — stdlib-only (csv/json/math) analysis + IAA script. Computes:
   per-item means, per-rater means, **Krippendorff's alpha (ordinal)**, mean pairwise Spearman,
   exact + within-1 percent agreement, and the human-vs-auto-reward Spearman/Pearson validity
   correlation (joined via `blinding_key.json`). Runs a **synthetic 5-rater self-test** when no
   `--ratings` are passed, so the pipeline is validated without human data.

7. **`ratings_example/sre{1..5}.csv`** + **`results_example.json`** — *synthetic, clearly
   labeled* demo rater files and the analysis output, proving the real-CSV ingestion path is
   identical to the in-memory self-test.

## How the rating set was generated (reproducible)
Read `hud_trajectories.jsonl`, dropped empty answers, bucketed by (model × reward-band),
seeded RNG (seed=7), picked diverse `scenario_id`s across bands/models, padded to 12, blinded
into `diagnoses_to_rate.json` + `blinding_key.json`.

## Run commands
```bash
cd experiments/ralph_outputs/J3/artifacts
# self-test (no humans needed):
python3 score_human_eval.py --out results_selftest.json
# real run once humans submit:
python3 score_human_eval.py --ratings 'ratings/*.csv' --key blinding_key.json --out results.json
```

## Shared-core safety
- No edits to `rex/*.py`, `sim/*.py`, `agent/*.py`, `experiments/*.py`, dashboards, or status
  files. The deterministic judge is *consumed* (via the recorded `auto_reward` in the key),
  not modified.
