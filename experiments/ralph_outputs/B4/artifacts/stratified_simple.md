# pass@k — incident type: simple

Numbers are pulled verbatim from each run's `by_condition[*].by_family['simple']` block (canonical estimator; no re-computation).

| source run | model | condition | n | passes | pass@1 (CI95) | pass@2 | pass@5 | mean_r | std |
|---|---|---|---|---|---|---|---|---|---|
| full_pass_at_k_glm-5p2.json | glm-5p2 | zero_shot | 36 | 20 | 0.556 [0.396,0.705] | 0.8095 | 0.9884 | 0.6694 | 0.4032 |
| full_pass_at_k_glm-5p2.json | glm-5p2 | best_of_n | 36 | 27 | 0.750 [0.589,0.863] | 0.9429 | 0.9997 | 0.8528 | 0.2710 |
| full_pass_at_k_glm-5p2.json | glm-5p2 | retry_realistic | 36 | 25 | 0.694 [0.531,0.820] | 0.9127 | 0.9988 | 0.8194 | 0.2873 |
| full_pass_at_k_glm-5p2.json | glm-5p2 | rex | 36 | 32 | 0.889 [0.747,0.956] | 0.9905 | 1.0000 | 0.9222 | 0.2200 |
| full_pass_at_k_glm-5p2.json | glm-5p2 | rex_no_oracle | 36 | 26 | 0.722 [0.560,0.842] | 0.9286 | 0.9993 | 0.8458 | 0.2704 |
| ablation_pass_at_k_deepseek-v4-pro.json | deepseek-v4-pro | zero_shot | 50 | 31 | 0.620 [0.481,0.741] | 0.8604 | 0.9945 | 0.7600 | 0.3455 |
| ablation_pass_at_k_deepseek-v4-pro.json | deepseek-v4-pro | best_of_n | 50 | 37 | 0.740 [0.605,0.841] | 0.9363 | 0.9994 | 0.8660 | 0.2614 |
| ablation_pass_at_k_deepseek-v4-pro.json | deepseek-v4-pro | retry_realistic | 50 | 35 | 0.700 [0.562,0.809] | 0.9143 | 0.9986 | 0.8670 | 0.2449 |
| ablation_pass_at_k_deepseek-v4-pro.json | deepseek-v4-pro | rex | 50 | 50 | 1.000 [0.929,1.000] | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| ablation_pass_at_k_deepseek-v4-pro.json | deepseek-v4-pro | rex_no_oracle | 50 | 37 | 0.740 [0.605,0.841] | 0.9363 | 0.9994 | 0.8830 | 0.2264 |

**Classified `simple` incidents not evaluated in any headline run (3):** cert_expire_leaf_sidecar, fd_exhaust_leaf_shipper, mem_leak_leaf_transcoder

_Provisional (excluded above): ablation_pass_at_k_glm-5p2.json.partial._
