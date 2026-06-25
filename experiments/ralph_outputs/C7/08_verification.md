# C7 — Verification

## Success criteria (from 01/03) vs outcome

| Criterion | Met? | Evidence |
|---|---|---|
| Real numbers for 3 harnesses on simple(train)+cascade(heldout) | YES | `table` in `transfer_result.json`, 07 |
| Synthesis produces a transferable rule-set | YES | `synthesis_ran=true`, 4 rules, TRAIN score 0.931 |
| Computed transfer gap with hand-written oracle reference | YES | `transfer_gap` in result.json |
| Leakage check passes (cascade labels untouched in synthesis) | YES | `leakage_ok=true`, disjoint splits |
| Artifact runnable + syntax/parse valid | YES | exit 0; 4/4 pytest |

## Are the outputs real (not placeholder)?
YES — measured from a live synthesis + evaluation run:
- 156 train labels (12 simple incidents), 284 held-out labels (20 cascade incidents), from real
  specs via `labeled_examples`.
- The synthesizer saw ONLY simple-family TRAIN labels (`leakage_ok=true`); cascade labels never
  entered `propose`/`evaluate`.

## The transfer result (the C7 answer)

| harness | TRAIN(simple) acc | HELDOUT(cascade) acc | cascade false-allow rate |
|---|---|---|---|
| seed (allow-all) | 0.494 | 0.627 | 1.000 |
| **synthesized (learned on simple)** | **0.923** | **0.845** | **0.066** |
| hand-written `is_safe` (oracle) | 0.936 | 0.915 | 0.208 |

- **Cross-type transfer gap (synthesized) = 0.078** (TRAIN 0.923 − HELDOUT 0.845). The oracle's
  gap is 0.021, so the **synthesis-induced transfer cost is ≈ 0.057** — small. Rules learned on
  *simple* incidents generalize to a structurally different *cascade* family with only a ~8-point
  accuracy drop.
- **Safety:** the synthesized harness cuts cascade false-allows from 106 (allow-all) to **7**
  (false-allow rate 0.066) — *lower* than the hand-written oracle's 0.208. It is conservative: it
  trades that for 37 false-blocks (over-blocking safe cascade actions it never saw).
- **The recovered general rule** `treats_forbidden_category==True → block` is exactly the
  hand-written Layer-1 pattern — it is family-agnostic and is what drives the transfer.

## What blocks perfect transfer (real ceiling)
The 7 residual cascade false-allows are:
- `trap_action` hazards (e.g. `failover_service->nlb`, `scale_deployment` herding) — these depend
  on incident-specific *targets* that are NOT expressible in the general feature set the
  interpreter understands, so NO general rule (synthesized or oracle) blocks them via features
  alone. (The oracle catches some via per-incident `forbidden_categories` lookup, which the
  synthesizer cannot use without leaking incident identity.)
- `rollback_no_deploy` on cascades where `recent_deploy` differs — a state signal not strongly
  represented in the simple TRAIN set.

This is a genuine, honest ceiling on cross-type transfer, not a bug.
