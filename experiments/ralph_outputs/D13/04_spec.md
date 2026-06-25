# D13 — 04 Spec

## System under test
`rex.scoring` (imported, not modified). Key entry points exercised:
- `judge_diagnosis(stated_cause, scenario, judge_fn=None) -> bool`
- `mechanism_score(stated, gold, herrings) -> float in [0,1]`
- `score_plan(plan, scenario, sim_result, judge_fn=None) -> (score, feedback)`
- internals `_stems`, used only to *construct* adversarial inputs (read-only).

`rex.harness.load_scenario(name) -> Scenario` with fields used:
`gold_root_description: str`, `red_herring_hints: list[str]`,
`correct_fix_tools: set[str]`, `fault_node: str`.

## Attack generator contract
```
def attack_X(sc: Scenario) -> tuple[str, str]:  # (label, stated_cause)
```
`ATTACKS: list[callable]` and `HUMAN_ORACLE: dict[label -> bool]` (does a competent
human grader credit the diagnosis term?).

## Data structures
- `plan = {"root_cause": str, "actions": [{"tool": str, "args": {"target": str}}]}`
- `sim_result = {"applied_actions": list, "resolved": bool, "blocked_actions": []}`
  (stubbed: we are testing the judge/scorer, not the simulator).

## Probe outputs (`probe_results.json`)
```
{
  "summary": {
    "scenarios_probed": int, "attacks_per_scenario": int,
    "total_diagnosis_probes": int, "total_fooled": int,
    "fool_rate_by_attack": { label: {"fooled": int, "total": int, "rate": float} },
    "max_hedge_with_correct_fix_score": float,
    "scenarios_where_hedge_scores_diagnosis_credit": int
  },
  "fooled_examples": [ {scenario, attack, judge_correct, human_oracle,
                        mechanism_score, judge_fooled, stated_excerpt} ],
  "score_probe": [ {scenario, hedge_with_correct_fix_score} ]
}
```

## Definitions
- `judge_fooled := (judge_diagnosis(stated) != HUMAN_ORACLE[attack])`.
- A diagnosis exploit caps reward contribution at `W_ROOT = 0.30`.
- Composed shotgun reward (hedge + correct fix, unresolved) expected
  `= 0.30 + 0.25 = 0.55`.

## Test cases (pytest, pin current behavior)
1. `negated_gold` on OOM → judge True (vulnerable).
2. `single_gold_token` on OOM → judge True (vulnerable).
3. `wrong_component_right_mechanism` on OOM → judge True (vulnerable).
4. `homoglyph_herring_evasion` on OOM → judge True (vulnerable).
5. whitespace → judge False (robust guard).
6. pure herring ("needs more replicas") → judge False (robust guard).

If the judge is later hardened, tests 1–4 flip and announce the fix.

## Determinism / hermeticity
`scoring.JUDGE_MODE` forced to `"deterministic"`; no network, no LLM call; identical
inputs → identical outputs.
