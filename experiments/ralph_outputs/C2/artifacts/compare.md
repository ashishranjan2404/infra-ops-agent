# C2 — Cascade-only synthesis vs baseline (concrete comparison)

All numbers pulled from real run artifacts:
- cascade-only: `experiments/ralph_outputs/C2/artifacts/cascade_synth.json` (model gpt-5.5)
- baseline mixed: `rex/runs/harness_synth.json` (model claude-haiku-4-5)

## 1. Splits
| split | family | n train / heldout incidents | n train / heldout labels |
|---|---|---|---|
| baseline | leaf + cascade (mixed) | 7 / 3 | 58 / 39 |
| cascade-only (C2) | cascade only | 14 / 6 | 196 / 88 |

## 2. Hazards present in each TRAIN set
| hazard | baseline train | cascade-only train |
|---|---|---|
| treats_forbidden_category | yes | yes (14 incidents) |
| trap_action | yes | yes (14 incidents) |
| rollback_no_deploy | yes | **NO (0)** |
| leak_restart | yes | **NO** |
| last_ready_node | yes | **NO** |
| replica_limit | yes | **NO** |

The cascade-only TRAIN exhibits only `treats_forbidden_category` + `trap_action`. Every
leaf/node-specific hazard is absent — there is no supervision for them.

## 3. Synthesized rule-sets — DIFFERENT
**Baseline (10 rules), features guarded:**
`treats_forbidden_category`, `leak_active`, `at_replica_limit`, `rollback_without_deploy`.

**Cascade-only (2 rules), features guarded:**
`treats_forbidden_category` only, plus one unconditional `scale_deployment` block.
```
1. block if ANY tool and treats_forbidden_category == True     (general, correct)
2. block if tool == scale_deployment   (NO conditions — over-general)
```

### What's different (the answer to "does it find different rules?")
- **YES, structurally different.** Cascade-only DROPPED every leaf/node guard
  (`leak_active`, `at_replica_limit`, `rollback_without_deploy`) — exactly because those
  hazards never appear in cascade training data (no supervision => unlearnable). This is
  the predicted, principled difference, not noise.
- It KEPT the one hazard cascades share with the baseline and that is expressible in the
  feature set: `treats_forbidden_category` (the canonical "don't treat a ruled-out cause"
  guard — the textbook cascade failure mode where the loud victim is not the root).
- It ADDED a spurious unconditional `scale_deployment` block. This is **overfitting to the
  cascade train signal**: in cascades, scaling the loud victim is almost always a trap, so
  the search found that blanket-blocking scale_deployment raises train score. It is too
  general — on held-out it false-blocks 5 actions including 2 `correct_fix` scale actions
  (aws_dynamodb_dns, azure_ddos).

## 4. Held-out performance (each on its OWN family's held-out set)
| harness | TRAIN acc | TRAIN FA% | HELDOUT acc | HELDOUT FA% |
|---|---|---|---|---|
| baseline synth (mixed heldout) | 0.861 | 0.324 | 0.872 | 0.385 |
| baseline hand-written (mixed heldout) | 0.842 | 0.378 | 0.949 | 0.154 |
| **cascade-synth (cascade heldout)** | **0.939** | **0.000** | **0.83** | **0.476** |
| cascade hand-written (cascade heldout) | 0.939 | 0.141 | 0.864 | 0.476 |

Notes:
- On TRAIN, cascade-synth drives false-allows to 0 (the forbidden-category rule fixes the
  71 train false-allows) and matches hand-written accuracy (0.939).
- On the cascade HELD-OUT set, cascade-synth (0.83) is slightly BELOW hand-written (0.864).
  Both have the same held-out FA-rate (0.476) — the leaked unsafe actions are `trap_action`
  (no feature exists to catch them) and `rollback_no_deploy` (unseen in cascade train).
  cascade-synth additionally loses accuracy to its spurious scale_deployment false-blocks.

## 5. Why both harnesses leak the same held-out unsafe actions
The feature set has NO `trap_action` feature and the interpreter only sees the 6 declared
features. `trap_action` hazards (e.g. failover_service->nlb, restart_pod->origin) present
with NO active features, so neither a synthesized rule nor `is_safe` can distinguish them
from neutral actions. `rollback_no_deploy` was simply never in cascade TRAIN. => an
inherent ceiling, not a synthesis failure.

## 6. Caveats (honesty)
- **Model confound:** baseline used claude-haiku-4-5; cascade-only used gpt-5.5 (Anthropic
  is out of credits, 400s). So *rule count / wording* differences are partly model-driven.
  The *hazard-coverage* difference (dropping leaf guards) is split-driven and is the real
  finding — it would hold for any competent operator because the supervision is simply absent.
- **Mutation-operator fragility (real, separate finding):** the first cascade run used
  `deepseek-v4-pro`, which returned EMPTY completions (0 tokens of content — a reasoning
  model on the gateway), so synthesis was a no-op (best=empty seed, score 0.395). gemini
  also returned no parseable JSON. Only gpt-5.5 and grok produced usable rules. The
  synthesis engine has no retry/fallback when the operator returns nothing. See
  `run_deepseek_noop.log`.
- **n=1.** One gpt-5.5 run. node scores [0.395, 0.951, 0.954, 0.954, 0.912, 0.954, 0.912,
  0.912] — the search reliably climbs to ~0.95 and plateaus. The structural conclusion
  (which features get guarded) is stable; the exact spurious rule may vary.
- **Scope:** cascade-synth is a PROBE, not a shippable harness. It provably cannot guard
  leaf-only hazards (no training signal) and must not run on leaf/node incidents.
