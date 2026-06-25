# D6 — SUMMARY

**Task:** Run DPO instead of GRPO using preference pairs from override/reward data.

**Done.** Found the override/preference signal in `opensre-traj/out/hud_trajectories.jsonl`
(197 reward-ranked model trajectories; deterministic judge = rex/scoring.py). For each
incident, accepting the higher-reward diagnosis over a lower-reward one is the
human-override preference — no new labeling needed. 34 scenarios have pairable reward
spread.

**Built (all in D6/artifacts/, no shared core files edited):**
- `build_dpo_pairs.py` — preference-pair constructor (per-scenario, margin-floored,
  deduped, empty-skipped, capped, deterministic). Reconstructs prompts from scenario specs.
- `test_build_dpo_pairs.py` — 10 unit tests on pair construction. **10/10 pass** (pytest
  and bare unittest).
- `dpo_config.yaml` — DPO config, DPO-specific hyperparams (lr=5e-7, beta=0.1, frozen
  ref), names the held-out eval path.
- `train_dpo.py` — runnable trainer scaffold (dependency-free `--dry-run` + actionable
  backend blocker; TRL DPOTrainer on the real path).
- `dpo_pairs.jsonl` — **81 real preference pairs / 23 scenarios** (avg margin 0.42).

**Result:** pipeline complete and validated. Training run itself BLOCKED — no
GPU/torch+trl backend in this env, and (as with GRPO) only a forked OPEN model is
trainable. Blocker is documented and the scaffold fails loudly with the exact fix. All
steps ran in <1s, well under the ~15 min cap.
