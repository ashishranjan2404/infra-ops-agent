# D6 — 01 Plan

## Objective
Run DPO (Direct Preference Optimization) instead of GRPO, sourcing preference
pairs from override/reward data already in the repo. Deliver a real preference-pair
constructor, a DPO training config + runnable trainer scaffold, and a unit test on
pair construction. Compute cap ~15 min; document the training blocker if backend
is unavailable.

## Key insight: where the preference signal lives
`opensre-traj/out/hud_trajectories.jsonl` (197 rows) records, per scenario, multiple
model trajectories each with a deterministic judge `reward` (rex/scoring.py) and
subscores. Same incident + different reward = a natural human-override preference:
the on-call accepts the higher-scoring diagnosis and rejects the lower one. 34
scenarios have >=2 distinct rewards. The incident `answer` text is the completion;
the prompt is reconstructable from `opensre-traj/specs/<incident>.json`.

## Approach
1. Group trajectories by `scenario_id`; for each pair within a scenario emit
   (chosen=higher reward, rejected=lower reward) when margin >= threshold.
2. Reconstruct the prompt from the scenario spec (alert title + summary).
3. Emit DPO triples {prompt, chosen, rejected, +metadata} to jsonl.
4. Write a DPO config (TRL-style) mirroring train_rft.py's GRPO config.
5. Write a runnable trainer scaffold with a dependency-free --dry-run and an
   honest backend blocker on the real path.
6. Unit test the constructor (orientation, margin filter, dedup, determinism).

## Files to create (all task-namespaced)
- artifacts/build_dpo_pairs.py — constructor
- artifacts/test_build_dpo_pairs.py — unit test
- artifacts/dpo_config.yaml — DPO config
- artifacts/train_dpo.py — trainer scaffold (dry-run + real path)
- artifacts/dpo_pairs.jsonl — generated output

## Dependencies
stdlib only for the constructor/test (json, itertools, unittest). Real training
needs torch+transformers+trl+datasets+GPU + a forked open model (Qwen). pyyaml
(already a rex dep) for config.

## Risks
- Prompt reconstruction imperfect (specs are templated with {{SVC}} placeholders) —
  acceptable: DPO conditions on prompt, exact substitution not load-bearing for the
  preference signal.
- Reward judge noise near ties -> mitigated by min_margin filter.
- No GPU/training backend here -> documented blocker, scaffold still runnable.

## Success criteria
- Constructor produces >0 valid pairs with chosen_reward > rejected_reward.
- Unit test passes (pytest/unittest).
- Config parses; trainer --dry-run validates data; real path emits clear blocker.
- No shared core files edited.
