# 03 — Improved Plan (post-grill)

## What changed vs 01
1. **pass@1 is the headline**, not mean reward. Mean + std demoted to diagnostic columns
   (accepted REV+SMR: partial-credit 0.4s inflate mean and hide "never resolved").
2. **n printed in every row.** pass@2/pass@5 kept but explicitly secondary/extrapolated
   when n<k (accepted REV: "pass@5 from n=3 is a model, not a measurement" → keep the
   number, drop the over-claim, expose n).
3. **Wall-budget guard** (`--time-budget-s`) that skips remaining models yet still writes a
   complete `result.json` (accepted DVO: never leave a half-written file).
4. **Threshold 0.8 reused verbatim** from `compute_pass_at_k.binary_pass` /
   `eval_pass_at_k.py` = SLO restored + root cleared + no trap (accepted SRE: threshold
   must encode "no destructive trap fired", which the existing P0 reward already does).

## Critique I ACCEPTED but the substrate forces a caveat (not a code change)
- **RLE: "baseline seeds must vary or pass@k is degenerate."** Verified against the code:
  the working frontier models route through the HUD gateway and are marked
  `no_temperature` in `agent/models.py` (reasoning models accept only default temperature).
  So **zero-shot baseline output is near-deterministic across seeds** → baseline pass@1 ≈
  pass@2 ≈ pass@5, and baseline reward_std ≈ 0. This is a *property of the frozen frontier
  policies*, not a bug in the metric. I do NOT hack diversity in (raising temperature would
  require editing `agent/llm.py`/roster — shared core, forbidden, and would change the
  policy being measured). Instead I **document it**: for these models, baseline pass@k
  collapses to pass@1, while REx genuinely resamples via per-node feedback, so the
  **pass@1 lift (REx − baseline)** is the honest, well-posed headline. A model with a
  sampling-capable proposer (e.g. fireworks `glm-5p2`, temperature-enabled) would show a
  non-degenerate baseline pass@k — the script supports that unchanged.

## Critique I REJECTED
- **SMR R1: "co-headline mean and pass@1."** Rejected after REV's rebuttal — mean is
  partial-credit-dominated and misleading as a lead metric here. Mean stays as a diagnostic
  column only.
- **RLE R2: "drop baseline pass@k entirely, only baseline-pass@1 vs REx."** Rejected
  (SRE's counter): baseline pass@k is a legitimate *capability ceiling* ("if this frozen
  model retried k times"). Keep it, just label it secondary and show n.

## Final shape
Per (model, condition∈{baseline, rex}): pass@1 (+Wilson CI), pass@2, pass@5, mean, std, n.
Per model: pass@1 lift and mean lift (REx − baseline). Real subset run under the 15-min cap.
