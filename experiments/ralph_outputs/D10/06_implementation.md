# D10 — 06 Implementation

## What I built (real artifacts)
- `artifacts/reward_sweep.py` — the reward-weighting sweep harness. **Wrapper only**;
  imports `rex.scoring` and `rex.harness`, edits neither.
- `artifacts/sweep_results.json` — real output over all 42 loadable scenarios,
  **292 sim-executed rollouts**, 8 weightings.

## How it works
1. **Grounding in core.** Reads `DEFAULT_W = (W_ROOT, W_FIX, W_RESOLVED, TRAP_PENALTY)`
   live from `rex/scoring.py:22` → `(0.30, 0.25, 0.45, 0.60)`.
2. **Real rollout bank.** For each scenario, `candidate_plans()` emits a fixed family of
   plans (correct fix, fix-wrong-target, trap-only, fix+trap, good/wrong diagnosis, empty).
   Each is executed through the **real sim** `rex.harness.run_plan` (world injection + tick
   settle), so `resolved`/`trap_hit`/`fix_credit` are genuine, not asserted.
3. **Primitives via core helpers.** `primitives()` calls `scoring.judge_diagnosis`
   (deterministic keyword judge — no LLM), `scoring._fix_credit`, `scoring._traps_in`.
4. **Re-weighting.** `compose(prims, w)` recombines the four primitives under each weight
   vector, mirroring `score_plan`'s exact formula and [0,1] clamp.
5. **Ranking analysis.** Per scenario, candidates are ranked by composite; we compute
   Kendall tau and argmax-flip vs the default weighting, plus aggregate mean/spread.

## Equivalence guard (proves we mirror core, not approximate it)
`selftest()` asserts `compose(prims, DEFAULT_W) == score_plan(...)` for **all 292 rollouts**
within 1e-6. It passes (see 07). This is the contract that the wrapper faithfully reproduces
core scoring before we perturb the weights.

## Core-file change (documented, NOT applied)
This task needs **no** change to `rex/scoring.py` — the sweep is non-invasive by design.
If one wanted to make weights configurable in core (so RFT could pass them at train time),
the minimal change would be:
```python
# rex/scoring.py (PROPOSED, not applied here)
import os
W_ROOT = float(os.environ.get("REX_W_ROOT", 0.30))
W_FIX = float(os.environ.get("REX_W_FIX", 0.25))
W_RESOLVED = float(os.environ.get("REX_W_RESOLVED", 0.45))
TRAP_PENALTY = float(os.environ.get("REX_TRAP_PENALTY", 0.60))
```
Left as a note per the brief's parallel-safety rule; not written to core.

## Honest scope boundary
This runs the **reward function** (the object a weight sweep changes) over real rollouts.
It does not run a GPU policy-gradient/GRPO update — blocked by no-GPU/no-API in this env
(see 07/09). We do not fabricate training curves.
