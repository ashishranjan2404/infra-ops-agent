# E3 — 07 Test Results

## 1. Unit tests (network-free) — PASS
```
$ python3 -m pytest experiments/ralph_outputs/E3/artifacts/test_eval_three_way_cascade.py -q
......                                                                   [100%]
6 passed in 0.04s
```
Covers: 14 distinct cascade incidents (all family=cascade), deterministic selection, 3 arms with
exactly one blocked (fireball), distinct real slugs, local + idempotent roster registration,
summarize stats (pass count / pass@1 / mean / positive std / empty→zeros).

## 2. Dry-run (selection + reachability probe) — PASS
```
$ python3 .../eval_three_way_cascade.py --dry-run
selected 14 cascade incidents:
  aws_dynamodb_dns, aws_kinesis_cell_manager, azure_ddos, circleci_kubeproxy_iptables,
  cloudflare_bgp_reorder, cloudflare_byzantine_switch, cloudflare_waf,
  cloudflare_zonemd_stale_cache, crowdstrike_bsod, datadog_systemd_cilium,
  gcp_service_control, github_dns_zone_corruption, github_mysql_semaphore_rename,
  github_network_partition
arm zero_shot: REACHABLE (qwen3-8b-base) '<think>\nOkay, the user wants me'
arm opensre_trained: REACHABLE (opensre-qwen3-8b) '<think>\nOkay, the user wants me'
arm fireball_trained: BLOCKED — No Fireball training data or forked model exists ...
```
Both open-model arms return 200 on the HUD gateway; Fireball correctly reported blocked.

## 3. Real eval (56 episodes) — PASS, 0 errors
```
$ python3 .../eval_three_way_cascade.py --seeds 2 --n-incidents 14 --max-workers 8
running arms: ['zero_shot', 'opensre_trained']  seeds=2
  [progress] 56/56 episodes (64s, 0 errors)

3-way cascade comparison (threshold=0.8)
arm                 pass@1          95% CI    mean    std    n
zero_shot            0.071     [0.02,0.23]   0.454  0.293   28
opensre_trained      0.107     [0.04,0.27]   0.475  0.305   28
fireball_trained   BLOCKED   No Fireball training data or forked model
```

## 4. Headroom / floor-effect check — OK (null lift is interpretable)
Zero-shot per-incident mean rewards span the full range, not stuck at the floor:
`[0.0, 0.15, 0.25, 0.3, 0.3, 0.3, 0.375, 0.525, 0.55, 0.6, 0.65, 0.75, 0.75, 0.85]`.
Within-arm reward std ≈ 0.29 (real spread). So the model has room to improve on these cascades →
OpenSRE's small/null lift is a genuine finding, not a measurement artifact.

## Fixes applied during the run
None required — tests and both runs passed first time. The only environment fix was loading keys
via `set -a; source ~/.zshrc; set +a` (HUD_API_KEY not exported by default; known gotcha).
