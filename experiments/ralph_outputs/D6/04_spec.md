# D6 — 04 Spec

## Data sources
- `opensre-traj/out/hud_trajectories.jsonl` (197 rows). Fields used:
  `scenario_id`, `incident`, `model`, `reward` (float, deterministic judge),
  `answer` (completion text).
- `opensre-traj/specs/<incident>.json` — prompt reconstruction (alert.title +
  alert.commonAnnotations.summary).

## Data structures
```python
@dataclass(frozen=True)
class DPOExample:
    prompt: str
    chosen: str            # higher-reward answer
    rejected: str          # lower-reward answer
    chosen_reward: float
    rejected_reward: float
    margin: float          # chosen_reward - rejected_reward
    scenario_id: str
    incident: str
    chosen_model: str
    rejected_model: str
```

## Function signatures
```python
load_trajectories(path: str) -> list[dict]
build_prompt(incident: str, specs_dir: str = DEFAULT_SPECS) -> str
construct_pairs(rows, *, min_margin=0.10, max_pairs_per_scenario=None,
                specs_dir=DEFAULT_SPECS) -> list[DPOExample]
```

## construct_pairs contract
- Group rows by `scenario_id`. Skip rows with empty `answer`.
- For each unordered pair (a,b) in a scenario: chosen = max reward, rejected = min.
- Emit only if `margin >= min_margin` AND chosen.answer != rejected.answer.
- Sort a scenario's pairs by descending margin; keep top `max_pairs_per_scenario`.
- Deterministic output (scenarios sorted; stable within).
- NEVER pair across scenarios.

## Output file format — dpo_pairs.jsonl
One JSON object per line = asdict(DPOExample). Consumed by train_dpo.py via the
`prompt`/`chosen`/`rejected` keys (TRL DPOTrainer schema).

## dpo_config.yaml contract
Keys: data{pairs_file,prompt_key,chosen_key,rejected_key,min_margin,
max_pairs_per_scenario,val_split,shuffle_seed}, model{base_model,max_prompt_length,
max_length}, dpo{beta,loss_type,reference_free,label_smoothing}, train{lr,epochs,
batch,grad_accum,...}, eval{judge,scenarios}.

## train_dpo.py contract
- `--dry-run`: load config+pairs, apply min_margin, split train/val, assert
  orientation (chosen_reward > rejected_reward) and key presence, print stats, exit 0.
  Dependency-free except pyyaml.
- real path: import torch/transformers/trl/datasets; on ImportError exit with a
  BLOCKER message naming the missing dep + open-model fork requirement. Otherwise
  build a datasets.Dataset and run TRL DPOTrainer.

## Test cases (test_build_dpo_pairs.py)
1. chosen has higher reward; margin correct.
2. orientation independent of input order.
3. min_margin filters near-ties.
4. empty answers skipped.
5. identical chosen/rejected text skipped.
6. no cross-scenario pairs.
7. max_pairs_per_scenario cap + descending-margin selection.
8. determinism (same input -> same output).
9. returns DPOExample with non-empty prompt.
10. build_prompt fallback for missing spec.
