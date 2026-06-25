# D10 — 08 Verification

## Success criteria (from 01) vs reality

| Criterion | Status | Evidence |
|---|---|---|
| Grounded in `rex/scoring.py` weights | MET | reads `W_ROOT/W_FIX/W_RESOLVED/TRAP_PENALTY` live from `scoring.py:22` |
| Wrapper, no core edit | MET | `reward_sweep.py` imports `rex.scoring`/`rex.harness`, edits neither; `git status` shows no core diff |
| Harness runs, selftest passes | MET | selftest OK on 292 rollouts (07 §1–2) |
| ≥8 weightings × ≥40 scenarios, real sim | MET | 8 weightings × 42 scenarios = 292 sim-executed rollouts |
| Ranking change is real & non-trivial | MET | `resolution_only` & `no_trap_penalty` flip argmax (2.4% of scenarios); `azure_ddos` flip shown (07 §5); tau drops to 0.41 for resolution_only |
| Composite reward changes shown | MET | mean composite ranges 0.211 (resolution_only) → 0.405 (diagnosis_heavy) |
| Deterministic / reproducible | MET | identical md5 across two runs (07 §3) |

## Are outputs REAL (not placeholder)?
Yes. `sweep_results.json` contains 292 rollouts each produced by executing a plan through
the actual `rex.harness.run_plan` sim and scoring it with `rex.scoring`'s own helpers. The
selftest cryptographically ties our numbers to `score_plan` at default weights — if any value
were fabricated or the formula mirrored incorrectly, the assert would fail.

## Spot-check of a claimed number
`diagnosis_heavy` mean_composite = 0.4051 > default 0.3186: expected, because most candidates
carry the gold diagnosis (`diag_ok=True`) and `diagnosis_heavy` triples W_ROOT (0.30→0.60).
Consistent.

## Honest limitation
The "RFT" here is the **reward design** half: we show how the optimization *target* (per-rollout
reward and within-group ranking) moves under each weighting. The policy-gradient *update* itself
is not run (no GPU/API). This is disclosed, not hidden.
