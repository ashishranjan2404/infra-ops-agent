# D13 — 06 Implementation

## Artifacts built (all under `experiments/ralph_outputs/D13/artifacts/`, no core edits)

### `probe_reward_hack.py` (≈230 lines, runnable)
Imports `rex.scoring` and `rex.harness.load_scenario` as a black box, forces
`scoring.JUDGE_MODE = "deterministic"`. Seven attack generators, each returning
`(label, stated_cause)`:
- `attack_gold_plus_herrings` — hedge: gold description + every red herring.
- `attack_one_gold_token` — a single discriminative gold stem in a non-committal sentence.
- `attack_negated_gold` — `"this is definitely NOT <gold>"` (exploits 'not' being a stopword).
- `attack_wrong_component_right_mechanism` — gold mechanism words on a bystander service.
- `attack_unicode_homoglyph` — Cyrillic look-alikes (а/е/о) on the herrings to dodge the penalty.
- `attack_keyword_stuffing` — verbatim gold echo (informational; gold hidden at eval).
- `attack_empty_padding` — whitespace/punctuation only (robustness guard).

`run_diagnosis_probes()` runs all 7 over all 42 scenarios (294 probes), comparing the
real `judge_diagnosis` verdict against a conservative `HUMAN_ORACLE`. `run_score_probe()`
calls the real `score_plan` with the hedge diagnosis + a legitimate correct fix on the
fault node. Writes `probe_results.json`.

### `test_reward_hack_probe.py` (pytest)
Six tests pinning current behavior: four vulnerable-cases assert `judge == True`
(flip when the judge is hardened), two guards assert `judge == False`.

### `probe_results.json`
Machine-readable probe output (committed alongside the script).

## Key implementation notes
- Inputs are constructed using `scoring._stems` only to *select* discriminative tokens
  for the attacks — read-only use of an internal; the judge itself is untouched.
- `HUMAN_ORACLE` carries an inline rationale per label; the two guards yield fool-rate
  0, evidencing the oracle is not rigged to always disagree with the judge.
- Fully hermetic: no network, no LLM, deterministic. Runs in <0.1s.

## How to run
```
python3 experiments/ralph_outputs/D13/artifacts/probe_reward_hack.py
python3 -m pytest experiments/ralph_outputs/D13/artifacts/test_reward_hack_probe.py -q
```
