# A1 — 03 Improved Plan (post-grill)

## What changed vs 01
1. **Floor check is a hard gate, run first.** Already executed across all 42:
   `{"empty_plan_max_reward":0.0,"trap_max_reward":0.1,"floor_ok":true}`. Reported before any
   pass@k number. (Accepted PSRE/REV.)
2. **pass@1 + Wilson CI is the headline; pass@5 is flagged degenerate at low seeds.**
   With seeds=3, `pass_at_k(n=3,c,5)` returns 1.0 whenever the model ever solves an incident,
   so pass@5 saturates. We still emit it (pipeline does) but the report and SUMMARY lead with
   pass@1 and call pass@5 an optimistic upper bound until a seeds≥5 run lands. (Accepted RLE.)
3. **Condition priority under budget.** Keep BOTH anchor conditions (`zero_shot`, `rex`) at
   FULL 42-incident coverage no matter what; the other three are bonus. If the 5-condition
   sweep can't finish in budget, the deliverable is the 42-incident result for the conditions
   that completed + an honest blocker. (Accepted PSRE over DEV.)
4. **Per-incident reward vectors retained.** The core pipeline already serializes
   `per_incident_rewards`; we keep it for incident-by-incident spread auditing. (Accepted REV.)
5. **Family-level reward std reported** in addition to per-incident, to pool the noisy
   3-seed signal. (Accepted RLE; bounded by REV's caveat that family std can mask degeneracy,
   so per-incident vectors stay in the JSON.)
6. **Parallel safety hardened.** Checkpoint + final JSON go to `A1/artifacts/`, NOT the shared
   `experiments/results/` (which already holds another worker's
   `ablation_pass_at_k_glm-5p2.json.partial`). Core pipeline imported unmodified. (Accepted DEV.)

## Critiques rejected (and why)
- **"Drop the `rex` condition to save time"** (early DEV) — REJECTED: that deletes the thesis.
  We cut seeds before cutting `rex`.
- **"Family-level std is enough"** (RLE, sole) — PARTIALLY REJECTED: kept, but per-incident
  vectors are also retained because pooled std can hide all-0/all-1 degeneracy (REV).
- **"Report only pass@1, delete pass@2/5"** (strong RLE) — REJECTED as over-correction: the
  pipeline computes them cheaply and they're informative at higher seeds; we keep them but
  label the seed caveat rather than deleting fields.

## Final execution
- Run `artifacts/run_full_pass_at_k.py --model glm-5p2 --seeds 3` over all 5 conditions,
  all 42 incidents, checkpointed to artifacts/. If time-bound, the completed-condition subset
  (guaranteed to include `zero_shot` and, with the resume order, `rex`) is the deliverable.
