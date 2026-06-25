# F8 · 03 Improved Plan (post-grill)

## What changed vs 01
1. **Two explicit reproducibility tiers** added (from SMR/RLE clash):
   - *Replay tier* — committed `.jsonl` + `deterministic_judge` → fully deterministic.
   - *Generation tier* — re-running models → reproducible only in distribution
     (means ± CI over seeds), control-flow seeded, outputs NOT bitwise.
   The checklist now has a row for each, instead of one ambiguous "seeded" claim.
2. **Per-result judge pinning** (RLE): every metric row records whether it used
   `deterministic_judge` (reproducible) or `llm/hybrid_judge` (not). Cited to
   `rex/scoring.py:79,100,141`.
3. **Data status corrected by direct inspection** (AAAI demanded honesty):
   - `opensre-traj/out/hud_trajectories.jsonl` is committed AND contains **197 rollouts
     across 3 models** (claude-opus-4-8: 68, claude-haiku-4-5: 68, kimi-k2p5: 61) —
     *richer than DATA.md claims*; DATA.md is stale and says only the Claude half (60).
     Checklist flags the doc/data drift.
   - The 53 `scenarios/cidg/generated/*.yaml` are **untracked** → PARTIAL. BUT a
     deterministic in-code generator exists (`rex/curriculum.py:77 generate_simple()`),
     which mitigates per DOL's point — so for the *simple* tier the data is
     reproducible-by-construction; the 53 free-form generated YAMLs are NOT
     (no committed generator+seed found for those specific files).
4. **Weights** split into closed (version-pinned, not weight-reproducible — inherent)
   vs open (`opensre-traj/train_rft.py` recipe present, checkpoint BLOCKED: HUD key+GPU).

## Critiques accepted
- SMR/RLE two-tier distinction — **accepted**, it is the crux of honesty here.
- AAAI "don't launder missing data" — **accepted**; glm/minimax described in DATA.md as
  pending is moot because committed file actually has kimi-k2p5 instead; I report the
  *actual committed contents*, not the doc's intent.
- DOL judge/version pinning + secrets-not-committed — **accepted**.
- PSRE "committed transcripts are the primary anchor" — **accepted**; replay tier ranked first.

## Critiques rejected (with reason)
- AAAI's implicit "untracked generated scenarios ⇒ whole repo unreproducible" —
  **rejected/softened to PARTIAL**: the SIMPLE tier has a committed deterministic
  generator (`curriculum.py:77`), and the headline trajectory dataset is committed.
  The free-form 53 YAMLs are a real but bounded gap, not a total failure.
- DOL's "dated model string ⇒ reproducible weights" — **rejected** (PSRE correct:
  providers silently patch). Closed-model rows are marked "version-pinned, best-effort,
  NOT weight-reproducible," with committed transcripts as the durable fallback.

## Final deliverables (unchanged set, sharpened content)
- `artifacts/REPRODUCIBILITY_CHECKLIST.md` (two-tier, per-axis, evidence-pinned).
- `artifacts/repro_manifest.json` (machine-readable status per item).
- `artifacts/verify_repro.py` (self-audit against the live repo + git SHA stamp).
