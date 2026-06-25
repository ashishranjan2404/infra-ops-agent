# A1 — 04 Spec

## Incident set (the "42")
`rex.harness.scenarios_by_family()` -> exactly:
- simple (12): auth_cert_expiry, bad_deploy_leaf, billing_disk_fill, checkout_bad_rollout,
  cpu_saturation_leaf, ingest_fd_exhaust, media_oom_leak, oom_kill, payments_dep_revoked,
  redis_cache_flush, search_cpu_starve, singleton_node_notready
- cascade (20): aws_dynamodb_dns, aws_kinesis_cell_manager, azure_ddos,
  circleci_kubeproxy_iptables, cloudflare_bgp_reorder, cloudflare_byzantine_switch,
  cloudflare_waf, cloudflare_zonemd_stale_cache, crowdstrike_bsod, datadog_systemd_cilium,
  gcp_service_control, github_dns_zone_corruption, github_mysql_semaphore_rename,
  github_network_partition, github_proxysql_fd_limit, incidentio_anetd_cpu,
  launchdarkly_cold_cache, railway_gcp_suspension, slack_consul_cache_db,
  slack_tgw_fd_exhaustion
- novel (10): azure_leapyear_cert, cloudflare_leap_second, cloudflare_waf_regex,
  conntrack_exhaustion, facebook_bgp_backbone, firefox_addon_cert, github_zk_splitbrain,
  gke_ip_exhaustion, kafka_poison_pill, knight_capital_conflict

Total = 42. Selected by `pick_incidents(per_family=None)`.

## Runner signature (artifacts/run_full_pass_at_k.py)
```
run_eval(model: str, conditions: list[str], per_family=None, seeds: int,
         max_workers: int, label: str, ckpt: str) -> dict
```
`per_family=None` is the load-bearing change: `pick_incidents(None)` returns full family lists.

## Reward / pass definition (unchanged, deterministic)
- `_score(plan, scenario)`: `run_plan` through `sim/engine.py`, then `score_plan` (P0
  deterministic judge). Reward in [0,1].
- `binary_pass(r, 0.8)`: pass iff reward >= 0.8 (SLO restored + root cleared + no trap).
- `pass_at_k(n, c, k)`: unbiased Chen estimator; `wilson_ci(p,n)`: Wilson 95%.

## Conditions
zero_shot (1 call) | best_of_n (N=4) | retry_realistic (<=N, realistic feedback) |
rex (Thompson tree, budget N=4, oracle feedback) | rex_no_oracle (rex + realistic feedback).

## Output JSON schema (full_pass_at_k_<model>.json)
```
{ model, label, threshold:0.8, seeds, n_incidents:42, full_set:true,
  incidents_by_family:{simple:[...12], cascade:[...20], novel:[...10]},
  n_jobs, elapsed_s, n_errors, errors:[...<=20],
  floor_check:{empty_plan_max_reward, trap_max_reward, threshold, floor_ok},
  by_condition:{ <cond>:{
     overall:{n,passes,"pass@1",ci95:[lo,hi],"pass@2","pass@5",mean_reward,reward_std},
     by_family:{simple:{...}, cascade:{...}, novel:{...}},
     per_incident_rewards:{<incident>:[r,...]} } } }
```

## Test cases
- T1 incident count: `n_incidents == 42` (asserted in runner).
- T2 floor: `floor_check.floor_ok is True` (asserted in runner; pre-verified offline).
- T3 family sizes: simple=12, cascade=20, novel=10.
- T4 schema: each `by_condition[c].overall` has pass@1/pass@2/pass@5/ci95/reward_std.
- T5 sanity: `0 <= pass@1 <= pass@2 <= pass@5 <= 1` per condition (monotone in k).
- T6 anchor: `rex.overall.pass@1 >= zero_shot.overall.pass@1` (thesis direction; reported,
  not asserted — a single low-seed run may not reach significance).

## Parallel-safety contract
- Writes ONLY under `experiments/ralph_outputs/A1/artifacts/`.
- Imports `rex.eval_pass_at_k` unmodified; edits no `rex/*.py`, `sim/*.py`, `agent/*.py`.
