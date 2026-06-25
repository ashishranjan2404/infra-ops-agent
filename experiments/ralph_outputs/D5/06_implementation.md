# D5 — 06_implementation

## What I built (all under experiments/ralph_outputs/D5/artifacts/)
1. **build_sft_data.py** — turns the shared 197-trajectory pool into SFT (prompt_ref → completion)
   pairs by selecting the argmax-reward demo per scenario (stable tie-break), keeping only those
   ≥ `--min-reward`. Writes `split.json` (frozen seeded 70/30 scenario split), `sft_pairs.jsonl`,
   and `sft_manifest.json`. Import-light (no HUD) → runs in Python 3.13. **Ran for real:** 34
   scenarios → 24 train / 10 eval → **21 SFT pairs (87.5% coverage)**; 3 hard scenarios dropped
   (`006-dns_failure`, `110-github_mysql_semaphore_rename`, `116-aws_dynamodb_dns_enactor`); teacher
   histogram Opus 8 / Haiku 7 / Kimi 6; mean demo reward 0.721.
2. **train_sft.py** — SFT (behavioral-cloning) leg scaffold via the HUD Tinker SDK, mirroring
   `train_rft_v2.py` structure (same `_aretry`, same CLI shape, SAME base slug). Loads pairs, builds
   supervised batches, renders the SAME `STATIC_PROMPT` when the HUD env is importable. At the
   training call it **introspects `TrainingClient`** for a supervised method and raises a precise
   `NotImplementedError` if absent — an honest scaffold, not a fake loss (05_ouroboros C1). `--dry`
   ran offline and built 21 examples.
3. **compare_harness.py** — `--offline` computes a labeled **proxy_ceiling** (v2-weighted reward on
   the best held-out demos + hack diagnostic, no network); post-training mode reads RFT/SFT run logs,
   computes gain-vs-base and declares a winner. **Ran for real:** mean proxy_ceiling_v2 = **0.6787**
   over 10 eval scenarios; wrote `comparison.json`.
4. **configs/rft.yaml + configs/sft.yaml** — matched configs; shared keys (`base_model`,
   `split_path`, `grader`, `eval_metric`) identical and asserted by the tests.
5. **test_d5.py** — 5 validity tests (split partition, threshold, determinism, offline harness,
   config-key equality). All pass.
6. **REPORT_SCAFFOLD.md** — the comparison report with the proxy-ceiling table filled and the
   trained-results table left blank pending the GPU/SDK legs.

## "Same data" guarantee
Both legs read `split.json`. RFT trains on `split.train` scenarios (graded rollouts, no gold needed);
SFT clones the best demo for those SAME scenarios; both eval on `split.eval` with the SAME v2 grader
and SAME base model. The split is frozen and seed-deterministic, so the equivalence is auditable.

## Shared-core files: NOT edited
No edits to `rex/*`, `sim/*`, `agent/*`, `opensre-traj/*`, or any other task's dir. I only IMPORT
`rex.scoring.mechanism_score` (read-only) and reference (do not modify) `opensre-traj/train_rft_v2.py`
and the env modules. The SFT trainer is a NEW file in my artifacts dir, not a patch to a core file.
