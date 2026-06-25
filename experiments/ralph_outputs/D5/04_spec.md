# D5 — 04_spec (technical spec)

All paths under `experiments/ralph_outputs/D5/artifacts/`. Python 3.13 for offline tools;
`.venv-hud` (3.12) for the HUD-Tinker training legs.

## Shared data pool
`opensre-traj/out/hud_trajectories.jsonl` — 197 rows. Relevant fields per row:
```
model: str           scenario_id: str       reward: float (combined v2-style)
true_category: str   answer: str            subscores: {root_cause_category, evidence_keywords,
                                                         ruled_out_red_herrings, remediation_tool, ...}
```
Scenario universe = `set(row.scenario_id)`.

## split.json (frozen, written by build_sft_data.py)
```json
{"seed": 7, "n_scenarios": <int>,
 "train": ["<scenario_id>", ...], "eval": ["<scenario_id>", ...],
 "train_frac": 0.7}
```
Both configs reference this file. RFT trains on `train` scenarios; SFT clones demos from `train`;
both eval on `eval`. Identical → "same data" is provable.

## build_sft_data.py
```
build_sft_data(traj_path, split_path, out_path, min_reward=0.5, seed=7, train_frac=0.7) -> dict
```
- Group rows by `scenario_id`. Pick argmax-`reward` row per scenario (the "best demo").
- Deterministic split of scenarios (seeded shuffle) into train/eval; write `split.json`.
- For each TRAIN scenario whose best demo `reward >= min_reward`, emit one SFT pair:
  `{"scenario_id", "prompt": <reconstructed STATIC_PROMPT>, "completion": <demo.answer>,
    "demo_model", "demo_reward"}` to `sft_pairs.jsonl`.
- Prompt reconstruction: import `SCENARIOS`, `_redact_alert`, `CATEGORIES` from `hud_env` and
  `STATIC_PROMPT`, `_evidence_text` from `hud_env_static` (same prompt the eval/RFT uses).
- Return + print a manifest: `{n_scenarios, n_train, n_eval, n_sft_pairs, coverage,
  dropped_no_demo: [...], mean_demo_reward}`.
- CLI: `python3 build_sft_data.py [--min-reward 0.5] [--seed 7]`. Offline, no network.

## train_sft.py (HUD Tinker scaffold — mirrors train_rft_v2 structure)
```
python3 train_sft.py --model <slug> --data sft_pairs.jsonl --epochs 3 --lr 1e-5 [--smoke] [--out runs/sft.jsonl]
```
- Loads pairs, builds supervised batches (prompt tokens masked, completion tokens as targets).
- Uses `hud.TrainingClient(model)`; calls a **supervised** forward/backward. **Open question
  verified in 06/07:** whether the SDK exposes `trainer.step` on token-target batches (vs only
  rollout `Run` batches). If not → SDK-blocked; the scaffold raises a clear `NotImplementedError`
  with the exact missing API, not a fake loss.
- Same retry wrapper (`_aretry`) for transient 5xx as train_rft_v2.
- Logs `{epoch, mean_loss, n}` per epoch to `--out`.

## compare_harness.py
```
python3 compare_harness.py --offline   # deterministic, no network: proxy ceiling on existing demos
python3 compare_harness.py --rft-log runs/rft.jsonl --sft-log runs/sft.jsonl   # post-training compare
```
- `--offline`: for each eval scenario, grade the best-demo answer with the v2 grader components
  (reuse `rex.scoring.mechanism_score` + the same weights as `hud_env_v2._grade_v2`), AND compute
  the hack diagnostic. Emits `proxy_ceiling` table. **Labeled proxy, never a trained result.**
- post-training mode: read each leg's run log, report final mean held-out reward, delta vs base,
  per-subscore breakdown, hack diagnostic, and declare the winner.
- Output: `comparison.json` + a printed table.

## Hack diagnostic (per answer)
```
req_kw_density   = (# required_keywords present) / (len(answer_tokens)/100)
herring_density  = (# ruling_out_keywords present) / (len(answer_tokens)/100)
```
A reward win with high `req_kw_density` and short answers flags possible keyword stuffing.

## Grader reuse (no re-implementation of weights)
Weights mirror `hud_env_v2`: category 0.35 | mechanism 0.20 | evidence_kw 0.25 | ruled_out 0.10
| remediation 0.10. The harness imports `mechanism_score` from `rex.scoring`; category/keyword
terms are recomputed from the trajectory's `subscores` where available (the pool already stores
graded subscores), else recomputed against `SCENARIOS[sid].answer`.

## Test cases
- T1: `build_sft_data` on the real pool produces ≥1 SFT pair, valid JSON per line, and a split
  whose train∩eval = ∅ and train∪eval = scenario universe.
- T2: every SFT pair `demo_reward >= min_reward`; coverage ≤ 1.0; dropped list disjoint from kept.
- T3: split is deterministic for a fixed seed (two runs → identical split.json).
- T4: `compare_harness --offline` runs with no network and emits a `proxy_ceiling` table with the
  five subscore columns + hack diagnostic; no key is null.
- T5: configs are valid YAML and both point at the SAME `split.json` and SAME base model.
