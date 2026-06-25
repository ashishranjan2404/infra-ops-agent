# D6 — 08 Verification

## Success criteria check
- [x] Constructor produces >0 valid pairs: **81 pairs / 23 scenarios**, real data.
- [x] chosen_reward > rejected_reward for every emitted pair (re-verified on file).
- [x] Unit test passes: 10/10 under pytest AND bare unittest.
- [x] DPO config parses (yaml.safe_load OK) with DPO-specific hyperparams.
- [x] Trainer --dry-run validates data; real path emits actionable blocker.
- [x] No shared core files edited (rex/*, sim/*, agent/*, experiments/*.py,
      opensre-traj source). All deliverables in D6/artifacts/.

## Outputs real, not placeholder?
Yes. dpo_pairs.jsonl is generated from the actual 197-row HUD trajectory file with
the real deterministic-judge rewards; prompts come from real scenario specs; chosen/
rejected are real model completions. Sample pair: scenario 001-oom_kill,
chosen_reward=0.698, rejected_reward=0.129, margin=0.569.

## Reproduce
```
cd experiments/ralph_outputs/D6/artifacts
python3 build_dpo_pairs.py            # regenerate pairs
python3 -m pytest test_build_dpo_pairs.py
python3 train_dpo.py --dry-run        # validate; drop --dry-run on a GPU host
```
