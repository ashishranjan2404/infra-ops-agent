# J4 — 04 Spec

## Experiment protocol (the human-in-the-loop design)
- **Unit**: one incident-resolution attempt. **Intervention**: frozen agent
  policy (named model + tool set + prompt, versioned).
- **Within-subjects (default)**: each staged/replayed incident is resolved in
  both arms (unassisted, agent-assisted). Counterbalance order; insert washout;
  ideally different but skill-matched operators per arm to kill learning effects.
  Link the two arms with a shared `pair_id`.
- **Between-subjects (A/B)**: randomize incident (and operator) to a single arm.
- **Segment measured**: diagnosis → resolution wall-clock (exclude fixed deploy
  overhead the agent cannot influence). Clock starts at incident-acknowledged,
  stops at SLO-restored.
- **Endpoints**: primary speedup = GM(control)/GM(agent); secondary median min,
  %-within-SLO, Cliff's delta.
- **Power**: `required_n_paired(expected_speedup, sd_log_diff)` — e.g. to detect
  1.5x with sd_log_diff=0.5 at 80% power / α=.05 ≈ 9 pairs; 1.2x ≈ 45 pairs.

## Data contract — trials file (CSV or JSON)
Row schema (one per resolution attempt):
| field | type | required | notes |
|---|---|---|---|
| incident_id | str | yes | scenario id |
| arm | "control"\|"agent" | yes | control=unassisted |
| mttr_minutes | float>0 | yes | rows with null/blank skipped |
| pair_id | str | within-design | links the two arms of one incident |
| operator_id | str | no | for random-effect / matched analysis |
| resolved | bool | no (default true) | unresolved attempts excludable |

## Function signatures (`mttr_analysis.py`)
```python
load_trials(path) -> list[Trial]
analyze(trials, *, design, slo=None, n_boot=5000, seed=0) -> Result
required_n_paired(expected_speedup, sd_log_diff, power=.8, alpha=.05) -> int
```
`Result` (JSON report) fields: design, n_control, n_agent, n_pairs,
gm_control_min, gm_agent_min, median_control_min, median_agent_min, **speedup**,
**speedup_ci95** [lo,hi], pct_reduction, p_value, test_name,
effect_size_cliffs_delta, slo_minutes, pct_within_slo_{control,agent},
significant_at_05, notes[].

## Statistics
- Primary test: paired t-test (within) / Welch t-test (between) on **log(MTTR)**.
- Nonparametric backup: Wilcoxon signed-rank (within) / Mann-Whitney U (between).
- CI: bootstrap on `exp(mean(log_c)-mean(log_a))`; paired resampling preserves
  pairing in within-design. n_boot=5000, percentile CI.
- scipy optional → permutation p-value fallback (sign-flip paired / label-shuffle).

## Simulation (`simulate_trials.py`)
`simulate(n_incidents, design, *, true_speedup, no_benefit_frac, operator_sd_log,
trial_sd_log, seed)` → rows. Baselines drawn from A9 real labels (lognormal fit
fallback). Agent arm: baseline / exp(log(true_speedup) + op_effect + noise), with
`no_benefit_frac` incidents getting ~no benefit.

## Test cases (in `_self_test`)
T1 gmean/median sanity. T2 within recovers planted ~2x, CI brackets it,
significant, n_pairs correct, Cliff's delta>0. T3 between null → speedup~1, CI
brackets 1.0, not significant. T4 validation rejects bad arm / nonpositive MTTR.
T5 power monotonic (bigger effect → fewer pairs).
