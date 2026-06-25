# B1 — 03 Improved Plan

## What changed after the grill
1. **Subset must hit every family, with a fixed non-cherry-picked slice.** Use
   `pick_incidents(per_family)` → `sorted(names)[:k]` (deterministic, documented). Run
   2 incidents/family so all three families (simple/cascade/novel) are represented.
   *(accepted: AAAI cherry-pick concern, PSRE family-coverage concern.)*
2. **No per-family claims from the subset.** Per-family CIs on n=10 are ~±0.18 — too wide.
   Subset headline = OVERALL pass@1 ± Wilson CI + rex-vs-zero_shot direction. Per-family
   numbers are deferred to the full grid / A1's full-42×3-seed reference.
   *(accepted: AAAI.)*
3. **Headline is binary pass@1 ± CI, not mean reward.** Because rex is near-saturated
   (A1: mean 0.94 / std 0.17), mean reward hides nothing useful; report std explicitly as
   the trainability caveat. *(accepted: RLE, SMR.)*
4. **Don't burn the cap chasing seed depth.** rex is already separated from zero_shot;
   extra seeds confirm a known answer. Cap budget goes to a finishing subset; the full grid
   is a script + resumable checkpoint for off-cap. *(accepted: RLE, DVO.)*
5. **Flag the hardest incidents.** Multi-fault cascades (80-multi-*, 82-multi-*) are only
   covered by the full-grid script, not the 6-incident subset — stated in 07/09.

## Rejected
- **"Run more seeds for tighter CIs" (initial SMR).** Rejected — rex/zero_shot CIs are
  already disjoint at A1's 3-seed full-42 scale; SMR withdrew this in R2. Coverage > depth.
- **"Subset alone is sufficient" (initial DVO).** Rejected as the full deliverable — a
  subset proves the pipeline + overall direction only. The full grid stays as runnable
  script + documented blocker so the claim isn't overstated.

## Final shape
- `artifacts/run_full_grid.py`: `--per-family 0` = full 42×5×5 grid; `--per-family 2` =
  capped 6×5×5=150 subset. Resumable `.partial` checkpoint. Floor-invariant assert.
- REAL run: the 150-episode subset (this fits the ~15-min cap).
- Reference: A1's full-42×5-condition×3-seed JSON for the per-family / scale claims.
- Honest blocker: full grid (1050 eps ≈ 45 min) exceeds the 15-min model-run cap.
