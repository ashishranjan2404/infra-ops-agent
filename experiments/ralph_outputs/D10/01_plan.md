# D10 — 01 Plan

## Objective
Run RFT (reinforcement fine-tuning) reward design with **different reward weightings**:
sweep `W_ROOT`, `W_FIX`, `W_RESOLVED`, `TRAP_PENALTY`. Show how the **composite reward**
and — more importantly for RFT — the **ranking** of rollouts within a scenario change as
the weights change. Ground the work in `rex/scoring.py`, where the weights live.

## Where the weights live (grounding)
`rex/scoring.py:22`:
```python
W_ROOT, W_FIX, W_RESOLVED, TRAP_PENALTY = 0.30, 0.25, 0.45, 0.60
```
`score_plan` (`rex/scoring.py:199`) composes four primitive signals:
```
score = W_ROOT*diag_ok + W_FIX*fix_credit + W_RESOLVED*resolved   (- TRAP_PENALTY if trap)
clamped to [0,1]
```
The primitives come from `judge_diagnosis` (deterministic keyword judge, no LLM),
`_fix_credit` (1.0 on-target / 0.5 right-tool-wrong-target / 0.0), `sim_result["resolved"]`,
and `_traps_in`.

## Approach (NON-INVASIVE — do not edit core)
1. Build a **wrapper** (`artifacts/reward_sweep.py`) that imports `rex.scoring` and
   `rex.harness` but never modifies them.
2. Generate a **real** rollout bank deterministically: for each scenario enumerate a
   fixed family of candidate plans (correct fix, fix-wrong-target, trap-only, fix+trap,
   good-diag-no-fix, wrong-diag, empty), run each through the **real sim**
   (`rex.harness.run_plan`), capture the four primitives via scoring.py's own helpers.
   No API key / LLM needed → reproducible.
3. Recombine primitives under each weight vector (mirroring `score_plan`'s formula).
   **Invariant:** at default weights, recomposed score == `score_plan(...)` exactly.
4. For each weighting, report mean composite, spread, and **ranking stability** vs the
   default (Kendall tau + argmax-flip rate). RFT optimizes *ranking*, so a weighting that
   reorders which rollout is best is the meaningful change.

## Files to create
- `experiments/ralph_outputs/D10/artifacts/reward_sweep.py` — the sweep harness.
- `experiments/ralph_outputs/D10/artifacts/sweep_results.json` — real output.
- 10 step docs + SUMMARY.md + result.json.

## Dependencies
`rex.scoring`, `rex.harness` (sim). Pure Python 3.13, no network.

## Risks
- Faking RFT: we cannot run a real GPU policy-gradient loop here. Mitigation: we run the
  **reward function** (the thing RFT optimizes) over a real rollout bank and show how the
  optimization *target* changes — that is the part a weight sweep actually affects.
- Over-coupling to scoring internals (`_fix_credit`, `_traps_in` are underscore-private).
  Accepted: they are the only faithful way to mirror the formula; the selftest guards drift.

## Success criteria
- Harness runs, selftest passes (recomposed==score_plan at default).
- ≥8 weightings × ≥40 scenarios of real sim rollouts.
- Ranking-change signal is real and non-trivial (some weighting reorders the argmax).
- No core file edited.
