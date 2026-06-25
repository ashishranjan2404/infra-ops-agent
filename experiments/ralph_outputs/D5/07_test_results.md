# D5 — 07_test_results

## test_d5.py (Python 3.13, no network) — PASS
```
$ python3 test_d5.py
  T1-T3 ok: 24 train / 10 eval, 21 pairs, deterministic
  T4 ok: proxy_ceiling=0.6787, all subscores present
  T5 ok: rft.yaml and sft.yaml share base_model/split_path/grader/eval_metric
ALL D5 TESTS PASSED
```
- T1-T3: split is a disjoint partition of the scenario universe; every SFT pair has reward ≥ 0.5 and
  comes from the train split; rebuilding with the same seed gives an identical split.
- T4: offline harness runs with no network, emits all five v2 subscores, result labeled a proxy.
- T5: rft.yaml and sft.yaml share base_model / split_path / grader / eval_metric verbatim.

## build_sft_data.py — RAN
34 scenarios → 24 train / 10 eval → 21 SFT pairs (87.5% coverage). Dropped (no demo ≥ 0.5):
`006-dns_failure`, `110-github_mysql_semaphore_rename`, `116-aws_dynamodb_dns_enactor`. Teacher mix
Opus 8 / Haiku 7 / Kimi 6, mean demo reward 0.721.

## compare_harness.py --offline — RAN
mean proxy_ceiling_v2 = 0.6787 over 10 eval scenarios; subscores: cat 0.700, mechanism 1.000,
evidence_kw 0.827, ruled_out 0.268, remediation 0.000. Wrote `comparison.json`.

## YAML — parsed OK (pyyaml present)
Both `configs/rft.yaml` and `configs/sft.yaml` load via `yaml.safe_load`.

## train_sft.py
- `--dry`: built 21 supervised examples offline, PASS.
- Non-dry (the real training call): in Python 3.13 it fails at `from hud import TrainingClient`
  with `ImportError: cannot import name 'TrainingClient' from 'hud'`. This is expected — the training
  legs belong in `.venv-hud` (3.12). In that env the next boundary is the **introspection guard**: if
  `TrainingClient` has no supervised step method, the script raises a precise `NotImplementedError`.

## Blockers (documented, not faked)
1. **Compute/env:** RFT and SFT fine-tuning need `.venv-hud` (3.12) + a forked Qwen slug + HUD Tinker
   credits. Out of scope for a single offline worker.
2. **SFT SDK surface:** `hud.TrainingClient` is rollout-batch oriented
   (`step(batch_of_Runs, lr, group_size)`); no supervised token-target step is exposed. The SFT leg
   is therefore SDK-blocked unless a supervised endpoint exists or SFT is run out-of-band
   (HF/PEFT on `sft_pairs.jsonl`) and then evaluated through the same v2 grader.

Both legs' trained numbers are intentionally left blank in REPORT_SCAFFOLD §5 rather than fabricated.
