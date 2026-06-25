# B6 — Summary

**Task:** Add trap-action avoidance rate as a standalone metric (not embedded in reward),
grounded in `rex/scoring.py`'s deterministic judge; ship a metric module + unit test and run
it on available rollout data. No shared-core edits.

## Delivered
- **`artifacts/trap_avoidance.py`** — standalone, reward-free metric.
  `trap_avoidance_rate(episodes) -> {rate, n_safe, n_trap, n_unknown, per_scenario}`,
  where `rate = n_safe / (n_safe + n_trap)`. Trap detection (`action_is_trap`) mirrors
  `rex/scoring._traps_in` exactly; the metric prefers the judge's own `failed_checks`
  `"trap_action"` token, with a structural recompute fallback and an explicit UNKNOWN class
  excluded from the denominator. CLI + JSONL/YAML loaders included.
- **`artifacts/test_trap_avoidance.py`** — 16 unit tests, incl. an equality test vs the real
  `rex/scoring._traps_in`. Pass under pytest AND standalone.
- **`artifacts/make_rollouts.py` + `artifacts/rollouts.jsonl`** — 102 REAL episodes generated
  from 51 `scenarios/cidg/generated/*.yaml` (safe=canonical_fix, trap=trap_action).

## Results
- 16/16 tests pass (pytest: `16 passed in 0.02s`; standalone: `16/16`).
- Metric on real rollouts: **trap-avoidance rate = 0.4804** (49 safe / 53 trap / 0 unknown, 102 eps).
- Two independent signal paths (failed_checks token vs structural recompute via `--scenarios`)
  agree at **0.4804**.
- Real finding: 2 scenarios have canonical-fix tool == trap tool on the same target
  (`incidentio-anetd-cpu`, `multi-fdexhaust-cpustarve`) — surfaced by the metric.

## Caveats
- Demo rollouts use a *synthetic* policy (labels are real & judge-consistent; policy is not a
  live model). Metric measures *executed* traps; attempted-but-blocked traps are a noted
  follow-up. No shared core files modified — integration left as a documented one-line proposal.
