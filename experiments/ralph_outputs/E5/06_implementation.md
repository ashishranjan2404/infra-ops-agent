# E5 — Implementation

## What I built (real artifacts, all under E5/, zero core edits)
1. **`artifacts/transfer_eval_novel.py`** — the transfer/generalization eval harness.
   - Reuses the A8 held-out set: `select_novel_set(10)` reads
     `experiments/ralph_outputs/A8/artifacts/heldout_manifest.json`, filters
     `held_out == true`, ranks novel-family first then back-fills simple, asserts each
     key is a loadable `rex.harness` scenario.
   - Runs any roster policy **zero-shot** (`build_prompt(sc, None)` + `parse_plan`),
     scored by the **P0 deterministic judge** (`rex.scoring.score_plan`), binary pass
     at 0.8.
   - Two no-network controls: `empty` (floor) and `oracle` (ceiling / data-validity).
   - `--fireball-model` / `$FIREBALL_MODEL` for the transfer target; unreachable →
     `status=blocked` with the concrete error, never fabricated.
   - Emits `pass@1` + Wilson 95% CI + mean + within-group std, plus a `floor_ceiling`
     gate, to `transfer_results.json`.
2. **`artifacts/test_transfer_eval.py`** — no-network self-test (selection size +
   loadability, floor==0, ceiling>=0.8, blocked-model handling). All pass.
3. **`transfer_results.json`** — REAL run output (glm-5p2 live on Fireworks +
   controls + blocked fireball).

## How the core is reused (not modified)
`transfer_eval_novel.py` only *imports*: `rex.harness.load_scenario/run_plan/_SCENARIOS`,
`rex.scoring.score_plan`, `rex.loop.build_prompt/parse_plan`, `agent.llm.call`,
`agent.models.ROSTER`, `experiments/compute_pass_at_k.wilson_ci/binary_pass`. No shared
file under `rex/`, `sim/`, `agent/`, or `experiments/` was edited.

## The Fireball blocker (documented, not faked)
"Fireball" is the named transfer-target model. It does **not** exist in this repo's
`agent.models.ROSTER` and is not reachable through any configured provider
(anthropic / fireworks / gateway). The harness records it exactly:
```
"fireball": {"kind":"fireball","status":"blocked","error":"KeyError: 'fireball'", ...}
```
When a real Fireball checkpoint/slug lands, add it to ROSTER (or pass
`--fireball-model <slug>`) and re-run — no harness change needed. Its transfer pass@1
will then be read directly against the glm-5p2 baseline already captured here.

## Real numbers captured (seeds=2, n=10 novel, threshold=0.8)
| policy   | status  | pass@1 | 95% CI         | mean  | std   |
|----------|---------|--------|----------------|-------|-------|
| empty    | ok      | 0.00   | [0.00, 0.16]   | 0.00  | 0.00  |
| oracle   | ok      | 1.00   | [0.84, 1.00]   | 1.00  | 0.00  |
| glm-5p2  | ok      | 0.25   | [0.11, 0.47]   | 0.41  | 0.38  |
| fireball | BLOCKED | —      | —              | —     | —     |

Floor/ceiling gate: `floor_ok=true`, `ceiling_ok=true` (every novel incident is
solvable; empty plan never passes). glm-5p2 std=0.38 → real within-group spread
(trainable signal), with most misses on the hard novel cascades (BGP, cert, conntrack,
poison-pill) and passes on the easy back-fill leaves (auth_cert_expiry, checkout rollout).
