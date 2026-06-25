# D5 — RFT vs SFT on the same data: 01_plan

## Objective
Answer empirically: **on identical opensre incident-diagnosis data, does RFT (GRPO/RLVR) or SFT
(supervised fine-tuning on demonstrations) give the bigger gain on the held-out eval reward?**
Deliver a comparison harness + matched configs for both regimes on the SAME data, articulate the
hypothesis, run what is runnable locally, and document the compute blocker for the GPU legs.

## Grounding (what already exists)
- `opensre-traj/train_rft.py` / `train_rft_v2.py` — real GRPO/RLVR loops via the HUD Tinker SDK.
  RFT trains an OPEN model (Qwen fork) on `hud_env_v2.py`, reward = deterministic substance grader
  (category 0.35 | mechanism 0.20 | evidence_kw 0.25 | ruled_out 0.10 | remediation 0.10).
- `opensre-traj/out/hud_trajectories.jsonl` — **197 graded trajectories** (claude-haiku 68,
  claude-opus 68, kimi-k2p5 61). Each row: `{model, scenario_id, reward, subscores, answer,
  true_category, ...}`. This is the shared data pool.
- `rex/scoring.py::mechanism_score` — the deterministic judge used as the reward.
- **No SFT script exists.** This is the gap D5 fills.

## Key insight: "same data" for two regimes that consume data differently
- **RFT** consumes data as *tasks* (scenarios) and generates its own rollouts; the reward
  shapes the policy. It needs no human/gold completions — only the grader.
- **SFT** consumes data as *(prompt, target completion)* pairs. The natural target is the
  **highest-reward existing trajectory** per scenario (behavioral cloning of the best demos),
  a.k.a. rejection-sampling / RFT-style SFT (RAFT/STaR).
- To make the comparison *fair on identical data*, both regimes must draw from the **same fixed
  scenario split** and the **same 197-trajectory pool**: SFT clones the best trajectories in the
  train split; RFT rolls out on the same train scenarios and is graded by the same grader. Both are
  evaluated on the same held-out scenarios with the same grader.

## Files to create (all task-namespaced — no shared-core edits)
- `artifacts/build_sft_data.py` — turn `hud_trajectories.jsonl` into SFT (prompt→completion) JSONL
  by selecting the best trajectory per scenario above a reward threshold. Reuses the static prompt.
- `artifacts/train_sft.py` — SFT loop scaffold via HUD Tinker SDK (mirrors train_rft_v2 structure;
  forward/backward on supervised tokens instead of advantage-weighted).
- `artifacts/compare_harness.py` — runs both legs (or loads their run logs), evals each checkpoint
  on the held-out split with the v2 grader, emits a comparison table + delta vs the base model.
- `artifacts/configs/rft.yaml`, `artifacts/configs/sft.yaml` — matched hyperparameters & the shared
  scenario split (identical train/eval ids, same base model, same eval grader).
- `artifacts/split.json` — the frozen train/eval scenario id split (so "same data" is auditable).
- `artifacts/REPORT_SCAFFOLD.md` — the comparison report with a results table to be filled in.

## Dependencies
- Local-runnable: data builder, split, configs, grader self-test, harness in `--dry/--offline` mode
  (uses the deterministic grader on existing answers — no network).
- Blocked (GPU/HUD): the actual SFT and RFT fine-tuning legs need a forked Qwen + HUD Tinker
  credits + the `.venv-hud` (3.12) env. Document as a blocker; ship the runnable scaffold.

## Risks
- "Same data" is subtle: SFT needs targets, RFT needs only scenarios. Mitigation: explicit split.json
  and a documented data-equivalence argument.
- Reward-on-train-answers (offline proxy) is NOT post-training reward; must label it a *proxy ceiling*,
  not the trained result, to avoid fabricating numbers.
- SFT-on-own-best-demos can overfit the demonstrator's style and inherit its category bias.

## Success criteria
1. A runnable SFT data builder producing valid JSONL pairs from the shared pool.
2. Matched RFT/SFT configs referencing one frozen split + same base + same grader.
3. A comparison harness that runs offline (deterministic grader) and prints a real per-split table.
4. Hypothesis stated with a fair, pre-registered metric; compute blocker honestly documented.
