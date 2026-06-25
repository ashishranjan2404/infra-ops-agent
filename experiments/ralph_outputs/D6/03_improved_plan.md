# D6 — 03 Improved Plan

## What changed after the grill
1. **Pair quality guards (from AAAI/SMR):** added `min_margin` (default 0.10),
   skip empty answers, and skip pairs with *identical* chosen/rejected text. Pairs
   are constructed strictly within a scenario.
2. **DPO-specific hyperparams (from PSRE/RLE):** lr=5e-7 (not GRPO's), beta=0.1,
   frozen reference (reference_free: false), cosine schedule, gradient checkpointing.
   Explicitly NOT copied from train_rft.py.
3. **Off-policy + leakage framing (from SMR/AAAI):** documented that trajectories are
   off-policy (different generator models) and that eval must use the held-out
   scenarios via the existing rex/eval_pass_at_k.py — named in dpo_config.yaml.
4. **Runnability (from DOL):** train_dpo.py has a dependency-free `--dry-run` that
   validates config+data + orientation, and a real path that exits with an actionable
   BLOCKER naming the missing backend dep and the open-model fork requirement.
5. **Cap per scenario (from AAAI):** `max_pairs_per_scenario` so no single incident
   dominates the dataset.

## Critiques accepted
- dedup + margin floor + empty-skip (AAAI/SMR) — implemented and unit-tested.
- DPO-specific lr/beta (PSRE/RLE) — in dpo_config.yaml.
- name the held-out eval path (AAAI) — in config `eval:` block.

## Critiques rejected (with reason)
- "Off-policy pairs are useless" (AAAI's strong form) — rejected; DPO is designed to
  learn from static off-policy preference data. Noted as a property, not a defect.
- "Block on perfect prompt reconstruction" — rejected; specs are templated and DPO
  conditions on the prompt; exact placeholder substitution is not load-bearing for the
  preference gradient. Logged as a known limitation instead.

## Revised deliverables (unchanged set, hardened)
build_dpo_pairs.py, test_build_dpo_pairs.py, dpo_config.yaml, train_dpo.py, dpo_pairs.jsonl.
