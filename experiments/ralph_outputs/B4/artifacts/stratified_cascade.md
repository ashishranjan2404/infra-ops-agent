# pass@k — incident type: cascade

Numbers are pulled verbatim from each run's `by_condition[*].by_family['cascade']` block (canonical estimator; no re-computation).

| source run | model | condition | n | passes | pass@1 (CI95) | pass@2 | pass@5 | mean_r | std |
|---|---|---|---|---|---|---|---|---|---|
| full_pass_at_k_glm-5p2.json | glm-5p2 | zero_shot | 60 | 4 | 0.067 [0.026,0.159] | 0.1299 | 0.3006 | 0.2833 | 0.3276 |
| full_pass_at_k_glm-5p2.json | glm-5p2 | best_of_n | 60 | 9 | 0.150 [0.081,0.261] | 0.2797 | 0.5699 | 0.5900 | 0.2844 |
| full_pass_at_k_glm-5p2.json | glm-5p2 | retry_realistic | 60 | 12 | 0.200 [0.118,0.318] | 0.3627 | 0.6865 | 0.6225 | 0.2773 |
| full_pass_at_k_glm-5p2.json | glm-5p2 | rex | 60 | 51 | 0.850 [0.739,0.919] | 0.9797 | 1.0000 | 0.9263 | 0.1785 |
| full_pass_at_k_glm-5p2.json | glm-5p2 | rex_no_oracle | 60 | 9 | 0.150 [0.081,0.261] | 0.2797 | 0.5699 | 0.5975 | 0.2759 |
| ablation_pass_at_k_deepseek-v4-pro.json | deepseek-v4-pro | zero_shot | 50 | 1 | 0.020 [0.004,0.105] | 0.0400 | 0.1000 | 0.3430 | 0.3187 |
| ablation_pass_at_k_deepseek-v4-pro.json | deepseek-v4-pro | best_of_n | 50 | 4 | 0.080 [0.032,0.188] | 0.1551 | 0.3530 | 0.5110 | 0.3105 |
| ablation_pass_at_k_deepseek-v4-pro.json | deepseek-v4-pro | retry_realistic | 50 | 6 | 0.120 [0.056,0.238] | 0.2278 | 0.4874 | 0.5100 | 0.3358 |
| ablation_pass_at_k_deepseek-v4-pro.json | deepseek-v4-pro | rex | 50 | 34 | 0.680 [0.542,0.792] | 0.9020 | 0.9979 | 0.7840 | 0.3409 |
| ablation_pass_at_k_deepseek-v4-pro.json | deepseek-v4-pro | rex_no_oracle | 50 | 1 | 0.020 [0.004,0.105] | 0.0400 | 0.1000 | 0.4405 | 0.3036 |

**Classified `cascade` incidents not evaluated in any headline run (6):** cert_expire_cascade_ingress, fd_exhaust_cascade_gw, mem_leak_cascade_cache, multi_cert_poolleak, multi_fdexhaust_cpustarve, multi_rollout_cacheflush

_Provisional (excluded above): ablation_pass_at_k_glm-5p2.json.partial._
