# D5 — SUMMARY: RFT vs SFT on the same data

Task. Compare RFT (GRPO/RLVR) vs SFT on identical opensre incident-diagnosis data — which gives
the bigger gain? Ground in opensre-traj/train_rft*.py; build a comparison harness + configs for both
on the SAME data; state the hypothesis; run what's runnable; document the compute blocker.

## Deliverables (all in experiments/ralph_outputs/D5/artifacts/)
- build_sft_data.py — builds SFT (prompt->completion) pairs from the shared 197-trajectory pool by
  cloning the best demo per scenario (reward >= 0.5); freezes a seeded 24/10 train/eval split.json.
- train_sft.py — SFT behavioral-cloning leg scaffold (mirrors train_rft_v2), with an honest SDK
  introspection guard for the missing supervised step.
- compare_harness.py — offline proxy-ceiling grader (no network) + post-training comparison mode.
- configs/rft.yaml, configs/sft.yaml — matched configs sharing base_model/split/grader/metric.
- split.json, sft_pairs.jsonl, sft_manifest.json, comparison.json — real generated data.
- test_d5.py — 5 validity tests, all PASS. REPORT_SCAFFOLD.md — report with proxy table filled.

## What ran (real)
- Data builder: 34 scenarios -> 24 train / 10 eval -> 21 SFT pairs (87.5% coverage); 3 hard
  scenarios have no qualifying demo (RFT can still attempt them; SFT cannot — a finding).
- Offline harness: mean proxy_ceiling_v2 = 0.6787 over the held-out eval split. Even the best demos
  leave headroom on remediation_tool (~0.00) and ruled_out_red_herrings (~0.27) — exactly where RFT
  can gain (motivates H2 quantitatively).
- All tests PASS; both YAMLs parse.

## Hypothesis (pre-registered)
H1: SFT gives the larger single-jump gain (cheap transfer of strong Opus/Haiku/Kimi demos).
H2: RFT gives a smaller additional gain concentrated in mechanism_match and the two weak terms.
H0/failure modes: SFT wins by teacher style-cloning; RFT "wins" via keyword-density inflation (hack
diagnostic catches it); SFT capped on the no-demo tail.

## Blocker (honest)
Trained eval rewards are LEFT BLANK — not faked. (1) Fine-tuning needs .venv-hud 3.12 + forked Qwen
+ HUD Tinker credits. (2) The SFT leg is SDK-blocked: hud.TrainingClient is rollout-batch oriented
and exposes no supervised token-target step (verified by introspection). A real SFT leg needs a
supervised endpoint or out-of-band HF/PEFT on sft_pairs.jsonl, then eval through the same v2 grader.

Status: completed — real plan+spec+runnable harness+configs+tests+report scaffold delivered;
downstream trained comparison blocked and documented.
