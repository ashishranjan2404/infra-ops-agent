# B6 — 08 Verification

## Success criteria (from 01) vs evidence
| Criterion | Status | Evidence |
|---|---|---|
| Standalone trap-avoidance metric, not embedded in reward | MET | `trap_avoidance.py:trap_avoidance_rate` returns a reward-free rate; no `TRAP_PENALTY`/score coupling. |
| Grounded in `rex/scoring.py` deterministic judge | MET | `action_is_trap` mirrors `_traps_in`; metric consumes the judge's own `failed_checks` `"trap_action"` token; equality test passes. |
| Metric module imports clean | MET | imports under pytest and standalone; CLI runs. |
| Unit test present & passing | MET | 16/16 pass (pytest + standalone), incl. equality-vs-rex test. |
| Runs on available rollout data | MET | ran on 102 real episodes generated from 51 CIDG YAMLs → rate 0.4804. |
| failed_checks path & structural path agree | MET | both yield 0.4804 (07 step 2 & 3). |
| No shared core files edited | MET | only files under `experiments/ralph_outputs/B6/` created; integration left as documented proposal. |

## Are outputs real (not placeholder)?
- `rollouts.jsonl` is 102 JSON lines derived from the actual `scenarios/cidg/generated/*.yaml`
  trap_actions + canonical_fix — not hand-typed numbers.
- The 0.4804 rate is computed, and reproduced via two independent code paths.
- Tests execute real assertions; the consistency test imports the real `rex.scoring`.

## Honest caveats
- Rollouts are *constructed* (one safe + one trappy agent per scenario), not sampled from a
  live model, because no pre-existing rollout JSONL carries per-scenario applied actions. The
  metric itself is exercised on real, judge-consistent labels; what's synthetic is the agent
  policy, not the trap labels.
- The metric measures *executed* traps (matching the judge). Attempted-but-blocked traps are
  a separate, unmeasured notion (see 09).

Verdict: deliverable meets all success criteria; the only synthetic element (agent policy in
the demo rollouts) is disclosed and does not affect metric correctness.
