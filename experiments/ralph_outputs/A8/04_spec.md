# A8 — 04 Spec

## Inputs
- `scenarios/cidg/generated/registry.json` — dict[cidg_key -> {path, family, style, ...}]
- `scenarios/cidg/generated/<n>-*.yaml` — each has `meta.failure_class`, `meta.source`
- `opensre-traj/out/trajectories.jsonl` — records with key `incident` (str), `scenario_id`
- `opensre-traj/out/hud_trajectories.jsonl` — records with key `incident`, `scenario_id`, `source`

## Data structures
```
TrainingSet   = { incidents: set[str], scenario_ids: set[str], n_lines: int }
Decision      = { held_out: bool, reasons: {
                    tier1_exact_id_match: bool,
                    tier1_significant_pair_overlap: (train_inc, [shared]) | None,
                    tier2_company_axis_hit: (company, train_inc) | None,
                    tier3_failure_class_seen_in_train: bool } }
ManifestRow   = { cidg_key, yaml, family, style, failure_class, source, held_out, reasons }
```

## Function signatures (build_heldout_split.py)
```python
norm(s: str) -> str                       # lowercase, strip non-alnum
toks(key: str) -> set[str]                # split on non-alnum
meaningful(key: str) -> set[str]          # toks minus STOP
load_training() -> (incidents, sids, n_lines)
load_yaml_meta(path: Path) -> dict        # returns meta block, robust to parse error
classify(key, fclass, train_inc) -> (held_out: bool, reasons: dict)
main() -> int                             # 0 iff assertion passes AND held set nonempty
```

## Novelty predicate (held_out == True)
`not (tier1_exact OR tier1_pair_overlap OR tier2_company_hit)`
and (if `--strict-class`) `not tier3_failure_class_seen`.

## Constants
- `STOP` = {cache, cold, stale, leak, cert, expiry, expire, disk, fill, rollout,
  limit, exhaustion, exhaust, starve, pool, flush, spike, delay, error, errors,
  node, cpu, fd, the, and, via, with}
- `COMPANIES` = {github, cloudflare, slack, aws, datadog, circleci, incidentio,
  launchdarkly, facebook, knight, azure, firefox, gke, kafka, redis, consul,
  mysql, proxysql, kinesis, dynamodb}

## Outputs / file formats
- `heldout_manifest.json`: { task_id, description, criteria, training_corpora,
  training_stats, candidate_pool, held_out[], n_held_out, contaminated[],
  n_contaminated, per_incident[], assertion_violations[], assertion_pass,
  manifest_sha256 }
- `heldout_split.csv`: cidg_key, yaml, family, failure_class, source, held_out,
  tier1_exact, tier2_company_hit, tier3_fclass_seen

## assert_no_overlap.py contract
- argv[1] (optional) = manifest path; default = sibling heldout_manifest.json.
- Re-derives training incidents independently from the raw jsonl.
- For each held_out key: fail on (exact-id) OR (>=2 meaningful-token overlap) OR
  (company-axis hit).
- Exit 0 = PASS (zero overlap); exit 1 = FAIL (prints offending pairs).

## Test cases
1. Builder runs, produces manifest + csv, `assertion_pass == True`.
2. Guard on real manifest → exit 0, "PASS".
3. Negative control: inject `github_proxysql_fd_limit` into held_out → exit 1,
   lists exact-id + pair + company-axis violations.
4. `--strict-class` produces a strict subset (held_out ⊆ default held_out).
