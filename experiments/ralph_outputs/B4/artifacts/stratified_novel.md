# pass@k — incident type: novel

Numbers are pulled verbatim from each run's `by_condition[*].by_family['novel']` block (canonical estimator; no re-computation).

| source run | model | condition | n | passes | pass@1 (CI95) | pass@2 | pass@5 | mean_r | std |
|---|---|---|---|---|---|---|---|---|---|
| full_pass_at_k_glm-5p2.json | glm-5p2 | zero_shot | 30 | 5 | 0.167 [0.073,0.336] | 0.3103 | 0.6272 | 0.4300 | 0.3131 |
| full_pass_at_k_glm-5p2.json | glm-5p2 | best_of_n | 30 | 7 | 0.233 [0.118,0.409] | 0.4184 | 0.7639 | 0.5367 | 0.3060 |
| full_pass_at_k_glm-5p2.json | glm-5p2 | retry_realistic | 30 | 7 | 0.233 [0.118,0.409] | 0.4184 | 0.7639 | 0.5508 | 0.2945 |
| full_pass_at_k_glm-5p2.json | glm-5p2 | rex | 30 | 30 | 1.000 [0.886,1.000] | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| full_pass_at_k_glm-5p2.json | glm-5p2 | rex_no_oracle | 30 | 7 | 0.233 [0.118,0.409] | 0.4184 | 0.7639 | 0.5617 | 0.2956 |
| ablation_pass_at_k_deepseek-v4-pro.json | deepseek-v4-pro | zero_shot | 50 | 4 | 0.080 [0.032,0.188] | 0.1551 | 0.3530 | 0.3315 | 0.2835 |
| ablation_pass_at_k_deepseek-v4-pro.json | deepseek-v4-pro | best_of_n | 50 | 5 | 0.100 [0.043,0.214] | 0.1918 | 0.4234 | 0.4385 | 0.2536 |
| ablation_pass_at_k_deepseek-v4-pro.json | deepseek-v4-pro | retry_realistic | 50 | 6 | 0.120 [0.056,0.238] | 0.2278 | 0.4874 | 0.4700 | 0.2588 |
| ablation_pass_at_k_deepseek-v4-pro.json | deepseek-v4-pro | rex | 50 | 50 | 1.000 [0.929,1.000] | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| ablation_pass_at_k_deepseek-v4-pro.json | deepseek-v4-pro | rex_no_oracle | 50 | 5 | 0.100 [0.043,0.214] | 0.1918 | 0.4234 | 0.4495 | 0.2449 |

**Classified `novel` incidents not evaluated in any headline run (10):** aws_s3_typo_capacity, cloudbleed_parser_overrun, fastly_pop_config, gitlab_db_deletion, honeycomb_retry_storm, monzo_cassandra_compaction, reddit_piday_k8s_route, roblox_consul_streaming, stripe_redis_fork_latency, travis_ci_leaked_secret

_Provisional (excluded above): ablation_pass_at_k_glm-5p2.json.partial._
