# D5 — 03_improved_plan (revised after the grill)

## What changed vs 01_plan

### Accepted critiques
1. **Frozen, auditable split (AR).** Add `artifacts/split.json` with explicit train/eval scenario
   ids, written by the data builder with a fixed seed. Both configs reference it by path. "Same data"
   is now provable, not asserted.
2. **Parallel design, same base (DOL+RLE).** Both legs start from the *same base model slug* on the
   *same train split*; evaluate on the *same eval split* with the *same v2 grader*. SFT→RFT
   (sequential) is listed as future work, not a fourth artifact.
3. **Reward threshold + coverage on SFT targets (PSRE).** `build_sft_data.py` keeps the best
   trajectory per scenario only if its reward ≥ `min_reward` (config). It reports coverage:
   `n_scenarios_with_demo / n_train_scenarios`. Hard scenarios with no qualifying demo are dropped
   from SFT — and that asymmetry (RFT can still try them, SFT can't) is itself a finding.
4. **Hack diagnostic (RLE+SMR).** The harness reports, per leg, required-keyword density and
   red-herring density next to reward, so a reward win driven by keyword stuffing is visible.
5. **No proxy-as-result (AR).** The offline harness output is labeled `proxy_ceiling` and is NEVER
   reported as the trained SFT/RFT number. The trained numbers stay blank until the GPU legs run.
6. **SDK-surface blocker, verified (DOL).** 06/07 explicitly check whether `hud.TrainingClient`
   exposes a supervised (token-target) step. The RFT loop uses `trainer.step(batch, lr, group_size)`
   on rollout `Run` objects; SFT needs a different call. If absent, SFT leg is **SDK-blocked**, which
   is a sharper, more honest blocker than "no GPU."

### Rejected critiques (and why)
- **SMR's default "RFT adds smaller further gain" as the stated hypothesis** — rejected as the *only*
  hypothesis. The grill surfaced two competing mechanisms (SFT-clones-strong-demos dominates vs
  RFT-reward-hacks-higher). The improved plan states the hypothesis as a *directional prediction with
  named failure modes*, not a single point estimate, so the experiment can actually falsify it.
- **Adding the sequential SFT→RFT leg now** — rejected for scope (DOL). Doubles compute, confounds
  the headline question. Documented as future work.
- **Gating on the hack detector** — rejected (SMR): the v2 `mechanism_score` already penalizes
  red-herring stuffing, so the detector is a *diagnostic column*, not a pass/fail gate.

## Hypothesis (pre-registered)
**H1 (primary):** On the same split + grader, SFT-on-best-demos yields the larger *single-jump*
improvement in mean held-out v2 reward over the base trainee, because cloning Opus/Haiku/Kimi
demonstrations transfers strong behavior cheaply. **H2:** RFT yields a smaller but additional gain
concentrated in the *mechanism_match* subscore (the term with the most within-group spread). **H0
(null/failure modes):** (a) SFT wins purely by style-cloning a demonstrator whose category bias
matches the eval; (b) RFT "wins" via keyword density inflation visible in the hack diagnostic; (c)
no qualifying demos for hard scenarios cap SFT below RFT on the tail.

## Final artifact list (unchanged shape, sharper contracts)
`build_sft_data.py`, `train_sft.py`, `compare_harness.py`, `configs/{rft,sft}.yaml`, `split.json`,
`REPORT_SCAFFOLD.md` — all under `experiments/ralph_outputs/D5/artifacts/`.
