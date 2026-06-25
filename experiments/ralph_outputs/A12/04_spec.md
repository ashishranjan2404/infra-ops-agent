# A12 — 04 Spec

## Inputs
- `scenarios/cidg/generated/*.yaml` — one incident spec per file.
- `scenarios/cidg/generated/registry.json` — dict keyed by incident id, each value
  has `path`, `family` (simple|cascade|novel), `red_herrings: [str]`, ...

## Feature extraction
`_features(spec, reg_entry) -> dict` over these spec paths (all optional, defaulted):

| feature          | source                                            | type |
|------------------|---------------------------------------------------|------|
| topology_size    | `len(topology.nodes) + len(topology.edges)`       | int  |
| hidden_root      | `bool(root_cause.hidden)`                         | 0/1  |
| cascades         | `bool(assertions.cascades)`                       | 0/1  |
| loud_not_cause   | `bool(assertions.loudest_alert_not_cause)`        | 0/1  |
| buried_gun       | `bool(assertions.buried_gun_exists)`              | 0/1  |
| buried_depth     | `max(observation.smoking_guns[].buried_under, 0)` | int  |
| hysteresis       | `bool(assertions.hysteresis)`                     | 0/1  |
| mon_degrades     | `bool(assertions.monitoring_degrades)`            | 0/1  |
| n_red_herrings   | `len(registry[id].red_herrings)`                  | int  |
| n_slo            | `len(slo)`                                         | int  |
| multi_fix        | `len(canonical_fix.steps) > 1`                    | 0/1  |

## Difficulty score
`_score(feat) = sum(W[k] * feat[k] for k in W)`, rounded to 4 dp.

```
W = {topology_size:0.6, hidden_root:2.0, cascades:1.5, loud_not_cause:2.5,
     buried_gun:1.5, buried_depth:0.04, hysteresis:2.0, mon_degrades:1.5,
     n_red_herrings:0.4, n_slo:0.3, multi_fix:1.0}
```
Rationale: the four "trap" booleans dominate (sum up to 8.0) so they cleanly separate
simple-leaf clones (all 0) from real outages (all 1). Counts/size are tiebreakers.

## Ordering
`rows.sort(key=lambda r: (r.difficulty, r.id))` — easy→hard, deterministic tiebreak.
Assign integer `rank` = index after sort.

## Output: `curriculum_order.json`
```json
{
  "signal": "composite static-structural difficulty score (see weights)",
  "weights": { ... },
  "order_easy_to_hard": ["billing_disk_fill", ..., "slack_tgw_fd_exhaustion"],
  "n": 36,
  "incidents": [
    {"id","yaml","title","family","failure_class","difficulty","rank","features":{...}},
    ...
  ]
}
```

## CLI
- `python3 build_curriculum.py` → writes JSON, prints path + count.
- `--print` → also prints `rank | diff | family | id` table.

## Test cases
1. **Validity:** output parses as JSON; `len(order_easy_to_hard) == n == #yaml files`.
2. **Monotonicity:** `difficulty` is non-decreasing along `incidents`.
3. **Split sanity:** every `family=="simple"` incident ranks below every
   `family in {cascade,novel}` incident.
4. **Determinism:** two runs produce byte-identical JSON.
5. **Coverage:** no yaml dropped; unknown-family yamls handled (no crash).
