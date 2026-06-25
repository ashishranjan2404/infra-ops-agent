# D9 — 03 Improved Plan

## What changed after the grill

### Accepted
1. **Random + anti-curriculum controls, multi-seed random** (AAAI). The harness
   scores all three orderings on the same held-out yardstick; random is averaged
   over N seeds with reported std. → implemented in `curriculum_vs_random.py`.
2. **Training is blocked → transparent labeled simulation, not faked reward**
   (DVO + AAAI). The harness prints "[SIMULATED — training blocked]" and stores
   `kind`/`model_note` fields stating it is a competence proxy. A one-function
   seam (`simulate_run`) is the only thing to replace for a real eval run.
3. **Preserve within-group reward spread** (RLE/DVO). The schedule bands a
   *contiguous range* of difficulty per stage (not a single value) and the
   training config exposes `group_size: 8`. Rehearsal weighting keeps earlier
   bands sampled (anti-forgetting).
4. **Trap-first ordering is correct, keep it** (PSRE). A12 weights already put
   trap booleans above topology size; no reweighting.

### Rejected (with reason)
- **RLE: replace static difficulty with online/self-paced competence.** Rejected
  for this task — self-paced curricula need the live training loop that is
  blocked here. Done offline it would be unfalsifiable hand-waving. Recorded as
  an explicit **limitation / future work** instead of a redesign. The simulation
  *does* model a moving competence frontier, which previews what an online run
  would exploit.
- **AAAI: "one seed is not a result."** Honored for random (multi-seed). NOT
  applied to curriculum/anti because those orderings are *deterministic* (no
  shuffle) — extra seeds would produce identical curves. Documented.

## Final shape
- `curriculum_schedule.py` — A12 → banded GRPO schedule (curriculum/random/anti),
  progressive unlock + rehearsal, emits `training_config.json`.
- `curriculum_vs_random.py` — deterministic learning-curve simulation comparing
  the three orderings on the full set; emits `comparison.json`.
- `test_curriculum_schedule.py` — invariants + hypothesis checks.

## Success criteria (unchanged + sharpened)
Reuse A12; real runnable deterministic artifacts; tests green; curriculum ≥
random ≥ anti in sim; blocker documented; clean seam to real eval.
