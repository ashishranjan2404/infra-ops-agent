# D6 — 06 Implementation

## What I built (all under experiments/ralph_outputs/D6/artifacts/, task-namespaced)
1. **build_dpo_pairs.py** — DPO preference-pair constructor. Reads
   `opensre-traj/out/hud_trajectories.jsonl`, groups by `scenario_id`, and emits
   (chosen=higher reward, rejected=lower reward) `DPOExample` triples per scenario.
   Reconstructs prompts from `opensre-traj/specs/<incident>.json`. Guards: min_margin
   floor, dedup identical text, skip empty answers, per-scenario cap, deterministic
   order. CLI writes `dpo_pairs.jsonl`. Stdlib-only.
2. **test_build_dpo_pairs.py** — 10 unittest cases on pair construction (orientation,
   order-independence, margin filter, empty-skip, text-dedup, no cross-scenario,
   cap+selection, determinism, prompt presence, missing-spec fallback).
3. **dpo_config.yaml** — DPO training config (TRL-style). DPO-specific hyperparams
   (lr=5e-7, beta=0.1, frozen ref, cosine). Names a forked open base model and the
   held-out eval path (rex/eval_pass_at_k.py + rex/scoring.py judge).
4. **train_dpo.py** — trainer scaffold. `--dry-run` validates config+data+orientation
   dependency-free; real path builds a datasets.Dataset and runs TRL DPOTrainer, or
   exits with an actionable BLOCKER if torch/trl absent.
5. **dpo_pairs.jsonl** — generated: 81 real preference pairs across 23 scenarios
   (avg margin 0.42, max 0.66).

## How the override/preference signal is sourced
The HUD trajectory reward is the deterministic SRE judge (rex/scoring.py: root-cause
category, evidence keywords, ruled-out red herrings, remediation tool). For one
incident, accepting the high-reward answer over a low-reward one IS the human-override
/ escalate-review preference. No new labeling needed.

## Shared core files
NONE edited. The constructor/config/trainer are the DPO sibling of the existing
`opensre-traj/train_rft.py` (GRPO) but live entirely in the D6 artifacts dir. The
proposed "where this would live in prod" is opensre-traj/train_dpo.py; I did not
create it there to respect the no-shared-edit rule — the artifacts copy is canonical
for this task.
