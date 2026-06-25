# B2 — Step 7: Test Results

## 1. Syntax / compile
```
$ python3 -m py_compile mcnemar.py test_mcnemar.py
OK compile
```

## 2. Unit tests (stdlib unittest)
```
$ python3 test_mcnemar.py
test_alignment_order ... ok
test_missing_incident_raises ... ok
test_threshold ... ok
test_analyze_synthetic_file ... ok
test_all_significant ... ok
test_holm_monotone_and_correction ... ok
test_exact_binomial_matches_hand_calc ... ok
test_known_discordant ... ok
test_length_mismatch_raises ... ok
test_no_discordant_gives_p1 ... ok
test_symmetry_swaps_cells ... ok
----------------------------------------------------------------------
Ran 11 tests in 0.000s
OK
```
**11/11 pass.**

## 3. Real run on cached pass@k JSONs (A1 glm-5p2, A2 deepseek-v4-pro)
```
$ python3 mcnemar.py A1/.../full_pass_at_k_glm-5p2.json \
                      A2/.../ablation_pass_at_k_deepseek-v4-pro.json \
                      --out mcnemar_pairwise_report.json
```
Produced full 10-pair tables per family for both models. Headline real p-values:

### glm-5p2 (overall, 42 inc x 3 seeds = 126 paired episodes/test)
| pair | b01 | b10 | n_disc | p_exact | p_holm | Holm sig |
|---|---|---|---|---|---|---|
| rex vs zero_shot | 84 | 0 | 84 | <1e-6 | <1e-6 | YES |
| rex vs best_of_n | 0 | 70 | 70 | <1e-6 | <1e-6 | YES |
| rex vs retry_realistic | 0 | 69 | 69 | <1e-6 | <1e-6 | YES |
| rex vs rex_no_oracle | 71 | 0 | 71 | <1e-6 | <1e-6 | YES |
| rex_no_oracle vs zero_shot | 13 | 0 | 13 | 0.00024 | 0.00146 | YES |
| best_of_n vs zero_shot | 16 | 2 | 18 | 0.00131 | 0.00525 | YES |
| retry_realistic vs zero_shot | 16 | 1 | 17 | 0.00028 | 0.00146 | YES |
| best_of_n vs retry_realistic | 4 | 5 | 9 | 1.000 | 1.000 | no |
| best_of_n vs rex_no_oracle | 5 | 4 | 9 | 1.000 | 1.000 | no |
| retry_realistic vs rex_no_oracle | 6 | 4 | 10 | 0.754 | 1.000 | no |

### deepseek-v4-pro (overall, 30 inc x 5 seeds = 150 paired episodes/test)
| pair | b01 | b10 | n_disc | p_exact | p_holm | Holm sig |
|---|---|---|---|---|---|---|
| rex vs zero_shot | 99 | 1 | 100 | <1e-6 | <1e-6 | YES |
| rex vs best_of_n | 0 | 88 | 88 | <1e-6 | <1e-6 | YES |
| rex vs retry_realistic | 1 | 88 | 89 | <1e-6 | <1e-6 | YES |
| rex vs rex_no_oracle | 91 | 0 | 91 | <1e-6 | <1e-6 | YES |
| retry_realistic vs zero_shot | 12 | 1 | 13 | 0.00342 | 0.02051 | YES |
| best_of_n vs zero_shot | 12 | 2 | 14 | 0.01294 | 0.06470 | no (raw only) |
| rex_no_oracle vs zero_shot | 10 | 3 | 13 | 0.09229 | 0.369 | no |
| best_of_n vs rex_no_oracle | 5 | 2 | 7 | 0.453 | 1.000 | no |
| retry_realistic vs rex_no_oracle | 7 | 3 | 10 | 0.344 | 1.000 | no |
| best_of_n vs retry_realistic | 2 | 3 | 5 | 1.000 | 1.000 | no |

(Per-family tables — simple/cascade/novel — are in the JSON; novel cells are underpowered,
see step 09.)

## 4. Cross-validation vs A2's existing mcnemar artifact
```
zero_shot        B2 disc=100 rex-wins=99   A2 disc=100 rex-wins=99   MATCH=True
best_of_n        B2 disc= 88 rex-wins=88   A2 disc= 88 rex-wins=88   MATCH=True
retry_realistic  B2 disc= 89 rex-wins=88   A2 disc= 89 rex-wins=88   MATCH=True
rex_no_oracle    B2 disc= 91 rex-wins=91   A2 disc= 91 rex-wins=91   MATCH=True
```
All four rex-vs-control comparisons reproduce A2's numbers exactly.

## Fixes applied during testing
None required — tests and real run passed on first execution after writing. Added
`pass_rate_a/b` per ouroboros P3.1 before the real run so order-of-naming can't mislead.
