# A7 — 04 Spec

## Inputs
- Glob: `scenarios/cidg/generated/*.yaml` (33 files), parsed with `yaml.safe_load`.
- Relevant YAML fields (read-only):
  `topology.nodes[]`, `topology.edges[]`, `root_cause.{hidden,severity}`,
  `observation.smoking_guns[].buried_under`, `assertions.{cascades,
  loudest_alert_not_cause,hysteresis,monitoring_degrades}`, `trap_actions[]`,
  `canonical_fix.steps[]`, `chance.{flap_prob,partial_recovery_prob}`, `slo[]`,
  `meta.{id,title,failure_class}`.

## Function signatures
```python
def clamp(x: float, lo=0.0, hi=1.0) -> float
def trap_complexity(d: dict) -> tuple[float, dict]      # (score, breakdown)
def expected_pass_rate(d: dict, tc: float) -> tuple[float, dict]  # (score, penalties)
def bucket(epr: float) -> str                            # "easy"|"medium"|"hard"
def main() -> int
```

## trap_complexity (weights sum ≤ 1.0; clamped)
| component | formula | max |
|---|---|---|
| topology | clamp((nodes-1)/6)·0.18 | 0.18 |
| fanout | clamp(edges/6)·0.10 | 0.10 |
| cascades | 0.16 if assertions.cascades | 0.16 |
| loudest_not_cause | 0.16 if assertions.loudest_alert_not_cause | 0.16 |
| hidden_root | 0.12 if root_cause.hidden | 0.12 |
| buried_gun | clamp(max(buried_under)/50)·0.12 | 0.12 |
| hysteresis | 0.06 if assertions.hysteresis | 0.06 |
| monitoring_degrades | 0.06 if assertions.monitoring_degrades | 0.06 |
| trap_actions | clamp(len/3)·0.06 | 0.06 |
| severity | clamp(severity)·0.06 | 0.06 |

## expected_pass_rate (base − penalties; clamped to [0,1])
base = 0.92
| penalty | formula | max |
|---|---|---|
| trap_complexity | tc·0.55 | 0.55 |
| fix_steps | clamp((steps-1)/4)·0.10 | 0.10 |
| flap | clamp(flap_prob/0.2)·0.05 | 0.05 |
| partial_recovery | clamp(partial_recovery_prob)·0.06 | 0.06 |
| multi_slo | clamp((slos-1)/3)·0.06 | 0.06 |

## bucket thresholds
easy ≥ 0.70 · medium ≥ 0.45 · hard < 0.45 (on expected_pass_rate).

## Output formats
- `difficulty_scores.json`:
  `{schema:{…}, count:int, scores:[{file,id,failure_class,title,
   trap_complexity,expected_pass_rate,difficulty_bucket,trap_breakdown,
   pass_rate_penalties}]}` — sorted ascending by expected_pass_rate (hardest first).
- `difficulty_scores.csv`: columns
  `file,id,failure_class,trap_complexity,expected_pass_rate,difficulty_bucket`.

## Test cases (validation, see 07)
- T1 all scores ∈ [0,1].
- T2 count == number of YAMLs on disk.
- T3 synthetic single-node incident (e.g. redis-cache-flush, cascades=false,
  not hidden) → bucket "easy", tc < 0.15.
- T4 cascading hidden postmortem (e.g. cloudflare-waf-regex) → bucket "hard"
  or "medium", tc > 0.6.
- T5 idempotent: two runs produce byte-identical CSV.
- T6 JSON parses; breakdown keys present.
- T7 source YAML mtimes unchanged after run (non-mutation).

## Contract
Deterministic, no network, no RNG, stdlib + pyyaml. Reads source YAMLs
read-only; writes only into the A7 artifacts dir.
