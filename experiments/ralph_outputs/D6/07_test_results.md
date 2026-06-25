# D6 — 07 Test Results

## Unit tests — PASS (10/10)
```
$ python3 -m pytest test_build_dpo_pairs.py -v
... 10 items
test_chosen_has_higher_reward PASSED
test_orientation_independent_of_input_order PASSED
test_min_margin_filters PASSED
test_empty_answers_skipped PASSED
test_identical_text_skipped PASSED
test_no_cross_scenario_pairs PASSED
test_max_per_scenario_cap PASSED
test_deterministic PASSED
test_returns_dpoexample_with_prompt PASSED
test_build_prompt_fallback_for_missing_spec PASSED
============================== 10 passed in 0.01s ==============================
```
Also passes under bare `python3 -m unittest` (no pytest needed): Ran 10 tests OK.

## Constructor run — PASS
```
$ python3 build_dpo_pairs.py
trajectories=197 pairs=81 scenarios=23 -> dpo_pairs.jsonl
avg_margin=0.422 max_margin=0.661
```
Orientation re-checked on the emitted file: all 81 pairs have
chosen_reward > rejected_reward; 23 distinct scenarios. PASS.

## Config + trainer dry-run — PASS
```
$ python3 -c "import yaml; yaml.safe_load(open('dpo_config.yaml'))"   # yaml OK
$ python3 train_dpo.py --dry-run
[dpo] pairs=81 train=69 val=12 beta=0.1 base=opensre-dpo-qwen3-8b
[dpo] DRY-RUN OK: config valid, data well-formed, orientation correct.
```

## Real training path — BLOCKED (documented, expected)
```
$ python3 train_dpo.py
BLOCKER: DPO backend unavailable — missing torch. Need torch+transformers+trl+
datasets and a GPU. Closed models (Claude/GPT) are not trainable; fork an open base
with `hud models fork Qwen/Qwen3-8B`. Re-run without --dry-run on a GPU host.
```
This is the honest training blocker: no GPU / torch+trl backend in this environment,
and (as with GRPO) only a forked OPEN model is trainable. The data+config+scaffold
are complete and validated; only the GPU run is deferred. Compute stayed well under
the ~15 min cap (all steps run in <1s).
