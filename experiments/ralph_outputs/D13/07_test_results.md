# D13 — 07 Test Results

## Probe run (real output)
`python3 experiments/ralph_outputs/D13/artifacts/probe_reward_hack.py`

```
summary:
  scenarios_probed: 42
  attacks_per_scenario: 7
  total_diagnosis_probes: 294
  total_fooled: 201
  fool_rate_by_attack:
    negated_gold:                    42/42  rate 1.000   <-- exploit
    single_gold_token:               42/42  rate 1.000   <-- exploit
    wrong_component_right_mechanism: 42/42  rate 1.000   <-- exploit
    gold_plus_all_herrings (hedge):  39/42  rate 0.929   <-- exploit
    homoglyph_herring_evasion:       36/42  rate 0.857   <-- exploit
    verbatim_gold_echo:               0/42  rate 0.000   (informational; correctly credited)
    whitespace_only:                  0/42  rate 0.000   (guard: correctly rejected)
  max_hedge_with_correct_fix_score: 0.55
  scenarios_where_hedge_scores_diagnosis_credit: 38   (of 42)
```

### Representative fooled examples (real)
```
oom_kill | negated_gold      | judge=CORRECT human=WRONG mech=1.0
   "this is definitely NOT a per-process memory leak on 'image-resizer'..."
oom_kill | single_gold_token | judge=CORRECT human=WRONG mech=1.0
   "the issue is related to climb somehow, unclear"
oom_kill | wrong_component   | judge=CORRECT human=WRONG mech=1.0
   "the unrelated-bystander-service exhibits climb container kernel kill leak limit memori oom"
oom_kill | homoglyph         | judge=CORRECT human=WRONG mech=1.0
   "а pеr-prоcеss mеmоry lеаk оn 'imаgе-rеsizеr'..." (Cyrillic а/е/о on herrings)
gcp_service_control | single_gold_token | judge=CORRECT human=WRONG mech=1.0
   "the issue is related to 503s somehow, unclear"
```

## Regression tests (real output)
`python3 -m pytest experiments/ralph_outputs/D13/artifacts/test_reward_hack_probe.py -q`
```
......                                                                   [100%]
6 passed in 0.04s
```

## Did not modify core; existing suite unaffected
The probe and tests import `rex.scoring` read-only. The pre-existing
`tests/test_rex_deterministic_judge.py` still describes the *intended* robustness
(rejects pure herrings, credits paraphrases) — our probe attacks a different axis
(negation / commitment / component-binding / tokenization) that that suite does not cover.

## Fixes applied during the run
- Initial `sys.path` had to point three levels up (`D13/artifacts/<file>` → repo root);
  corrected and verified imports resolve. No other fixes needed.
