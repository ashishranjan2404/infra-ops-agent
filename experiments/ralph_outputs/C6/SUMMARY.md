# C6 — SUMMARY

**Task:** Run harness synthesis (`rex/harness_synth.py`) with different base models —
does the proposer matter? Compute cap ~15 min, no shared-core edits.

## Proposer hook
`rex/harness_synth.py:27` `MODEL` → the only base-model entry point, used by
`propose_ruleset()` as the mutation operator inside `thompson_search`. I overrode this
module global per-model in a task-namespaced driver (`artifacts/run_synth_models.py`),
restoring it in `finally`. No core file edited.

## Reachability (real blocker)
Intended proposer `claude-haiku-4-5` and ALL Anthropic models are **unreachable** —
`400 "credit balance is too low"`. Ran reachable cross-provider proposers instead:
`gpt-5.5` (gateway), `deepseek-v4-pro` (gateway), `minimax-m3` (Fireworks).
Run: budget=8, seed=0, TRAIN=7/HELDOUT=3 incidents, ~347s total.

## Answer: YES, the proposer matters — by a large margin.
Same search, same data, only the proposer varied:

| proposer | best train | rules | TRAIN acc | HELDOUT acc | HELDOUT FA | HELDOUT FB |
|---|---|---|---|---|---|---|
| **minimax-m3** | 0.781 | 3 | 0.832 | **0.897** | 4 | 0 |
| gpt-5.5 | 0.798 | 3 | 0.762 | 0.641 | 4 | **10** |
| deepseek-v4-pro | 0.464 | **0** | 0.634 | 0.667 | **13** | 0 |
| hand-written (baseline) | — | — | 0.842 | 0.949 | 2 | 0 |

- **minimax-m3** = best proposer: discovered 3 clean general rules
  (`treats_forbidden_category`, `leak_active`, `rollback_without_deploy`), 0 false-blocks,
  0 in-scope held-out false-allows — approaches but doesn't beat the hand-written harness.
- **gpt-5.5** over-blocks: added a conditionless ban on disruptive tools → 10 held-out
  false-BLOCKS (high train score masked it).
- **deepseek-v4-pro** produced an EMPTY rule-set (all 8 nodes stuck at the seed score) →
  effectively NO harness; held-out FA=13.

So at this budget the proposer is the dominant factor in synthesized harness quality —
ranging from near-baseline (minimax) to over-blocking (gpt-5.5) to no harness (deepseek).

## Caveats (see 09)
Single seed, n=3 held-out, reasoning proposers are non-deterministic; intended haiku
proposer never ran; cross-provider prompt delivery differs. Results are directional, not
statistically significant. Driver is seed-parameterized for a follow-up multi-seed sweep.

## Artifacts
- `artifacts/run_synth_models.py` — driver (runnable, no core edits)
- `artifacts/synth_{gpt-5.5,deepseek-v4-pro,minimax-m3}.json` — per-model results
- `artifacts/comparison.json` — combined comparison
