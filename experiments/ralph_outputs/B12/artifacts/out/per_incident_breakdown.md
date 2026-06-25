# Per-incident pass@k breakdown

Rows: 72  |  solvable=64  partially=1  unsolvable=7

| incident | family | model | flag | best p@1 | zero_shot p@1 | zero_shot p@k | best_of_n p@1 | best_of_n p@k | retry_realistic p@1 | retry_realistic p@k | rex p@1 | rex p@k | rex_no_oracle p@1 | rex_no_oracle p@k |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| auth_cert_expiry | simple | glm-5p2 | solvable | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| aws_dynamodb_dns | cascade | glm-5p2 | solvable | 1.00 | 0.33 | 1.00 | 0.33 | 1.00 | 0.33 | 1.00 | 1.00 | 1.00 | 0.33 | 1.00 |
| aws_kinesis_cell_manager | cascade | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| azure_ddos | cascade | glm-5p2 | unsolvable | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| azure_leapyear_cert | novel | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| bad_deploy_leaf | simple | glm-5p2 | solvable | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| billing_disk_fill | simple | glm-5p2 | solvable | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| checkout_bad_rollout | simple | glm-5p2 | solvable | 1.00 | 0.67 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| circleci_kubeproxy_iptables | cascade | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| cloudflare_bgp_reorder | cascade | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| cloudflare_byzantine_switch | cascade | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| cloudflare_leap_second | novel | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| cloudflare_waf | cascade | glm-5p2 | unsolvable | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| cloudflare_waf_regex | novel | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.33 | 1.00 |
| cloudflare_zonemd_stale_cache | cascade | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| conntrack_exhaustion | novel | glm-5p2 | solvable | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| cpu_saturation_leaf | simple | glm-5p2 | solvable | 1.00 | 0.67 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| crowdstrike_bsod | cascade | glm-5p2 | unsolvable | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| datadog_systemd_cilium | cascade | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| facebook_bgp_backbone | novel | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| firefox_addon_cert | novel | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| gcp_service_control | cascade | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| github_dns_zone_corruption | cascade | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| github_mysql_semaphore_rename | cascade | glm-5p2 | solvable | 1.00 | 0.67 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| github_network_partition | cascade | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| github_proxysql_fd_limit | cascade | glm-5p2 | solvable | 1.00 | 0.33 | 1.00 | 0.67 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.67 | 1.00 |
| github_zk_splitbrain | novel | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| gke_ip_exhaustion | novel | glm-5p2 | solvable | 1.00 | 0.67 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| incidentio_anetd_cpu | cascade | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.67 | 1.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| ingest_fd_exhaust | simple | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.33 | 1.00 | 0.33 | 1.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| kafka_poison_pill | novel | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.33 | 1.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| knight_capital_conflict | novel | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.33 | 1.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| launchdarkly_cold_cache | cascade | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| media_oom_leak | simple | glm-5p2 | solvable | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| oom_kill | simple | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.67 | 1.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.67 | 1.00 |
| payments_dep_revoked | simple | glm-5p2 | partially | 0.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.67 | 1.00 | 0.00 | 0.00 |
| railway_gcp_suspension | cascade | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| redis_cache_flush | simple | glm-5p2 | solvable | 1.00 | 0.33 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| search_cpu_starve | simple | glm-5p2 | solvable | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| singleton_node_notready | simple | glm-5p2 | unsolvable | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| slack_consul_cache_db | cascade | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| slack_tgw_fd_exhaustion | cascade | glm-5p2 | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| auth_cert_expiry | simple | deepseek-v4-pro | solvable | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| aws_dynamodb_dns | cascade | deepseek-v4-pro | solvable | 1.00 | 0.20 | 1.00 | 0.80 | 1.00 | 1.00 | 1.00 | 0.80 | 1.00 | 0.20 | 1.00 |
| aws_kinesis_cell_manager | cascade | deepseek-v4-pro | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| azure_ddos | cascade | deepseek-v4-pro | unsolvable | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| azure_leapyear_cert | novel | deepseek-v4-pro | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| bad_deploy_leaf | simple | deepseek-v4-pro | solvable | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| billing_disk_fill | simple | deepseek-v4-pro | solvable | 1.00 | 0.80 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.80 | 1.00 |
| checkout_bad_rollout | simple | deepseek-v4-pro | solvable | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| circleci_kubeproxy_iptables | cascade | deepseek-v4-pro | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.20 | 1.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| cloudflare_bgp_reorder | cascade | deepseek-v4-pro | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| cloudflare_byzantine_switch | cascade | deepseek-v4-pro | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| cloudflare_leap_second | novel | deepseek-v4-pro | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| cloudflare_waf | cascade | deepseek-v4-pro | unsolvable | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| cloudflare_waf_regex | novel | deepseek-v4-pro | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| cloudflare_zonemd_stale_cache | cascade | deepseek-v4-pro | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| conntrack_exhaustion | novel | deepseek-v4-pro | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.20 | 1.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| cpu_saturation_leaf | simple | deepseek-v4-pro | solvable | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| crowdstrike_bsod | cascade | deepseek-v4-pro | unsolvable | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| datadog_systemd_cilium | cascade | deepseek-v4-pro | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| facebook_bgp_backbone | novel | deepseek-v4-pro | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| firefox_addon_cert | novel | deepseek-v4-pro | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| github_zk_splitbrain | novel | deepseek-v4-pro | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| gke_ip_exhaustion | novel | deepseek-v4-pro | solvable | 1.00 | 0.80 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| ingest_fd_exhaust | simple | deepseek-v4-pro | solvable | 1.00 | 0.20 | 1.00 | 0.40 | 1.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.60 | 1.00 |
| kafka_poison_pill | novel | deepseek-v4-pro | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| knight_capital_conflict | novel | deepseek-v4-pro | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| media_oom_leak | simple | deepseek-v4-pro | solvable | 1.00 | 0.80 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| oom_kill | simple | deepseek-v4-pro | solvable | 1.00 | 0.40 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| payments_dep_revoked | simple | deepseek-v4-pro | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| redis_cache_flush | simple | deepseek-v4-pro | solvable | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |

## Unsolvable incidents (no condition passes a single sample)

- deepseek-v4-pro:azure_ddos
- deepseek-v4-pro:cloudflare_waf
- deepseek-v4-pro:crowdstrike_bsod
- glm-5p2:azure_ddos
- glm-5p2:cloudflare_waf
- glm-5p2:crowdstrike_bsod
- glm-5p2:singleton_node_notready

## Partially-solvable (best pass@1 in (0,1) — never reliable)

- glm-5p2:payments_dep_revoked

## By family

| family | solvable | partially | unsolvable |
|---|---|---|---|
| cascade | 24 | 0 | 6 |
| novel | 20 | 0 | 0 |
| simple | 20 | 1 | 1 |
