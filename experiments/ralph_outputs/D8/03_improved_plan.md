# D8 — 03 Improved Plan

## What changed after the grill

### Accepted critiques
1. **(SMR/RLE) Make the transition explicit, don't oversell it.** The adapter
   emits an explicit `STATE_BEFORE / CONTEXT / ACTION -> RESULT / NARRATION /
   STATE_AFTER` structure rather than dumping raw narration. We frame this as
   *necessary-not-sufficient*: it lets SFT fit the transition; the burden of
   proving transfer is on the eval, which is configured but NOT run.
2. **(REV/RLE) The `reward` field is a smell if it looks like a game score.**
   Reworked: `reward` is now explicitly a **data-quality / informativeness
   weight** in `[0,1]` for loss weighting (command present, both states present,
   observable state change). Docstring + config both say it is NOT a Fireball
   outcome. This removes any appearance of a fabricated score.
3. **(DOL/PSRE) Fail closed + loud blocker.** Config carries
   `is_real_fireball: false` and `min_examples_for_real_run: 2000`; a real
   training run must refuse fixture data and only allow `--smoke`. Blocker is
   stated at the top of the adapter, the config, 07, 09, and SUMMARY.
4. **(REV) Replication bar recorded.** Multi-seed + CI on the cascade/simple
   split is written down as the acceptance criterion for the eventual rerun
   (Claim-2 evidence), explicitly not met by D8.
5. **(SMR) Defensive schema reads.** Every FIREBALL field is optional; records
   missing load-bearing fields (no command, or no state at all) are skipped and
   counted, so real-data schema drift fails loud-but-recoverable.

### Rejected critiques (with reasons)
- **(PSRE) "D&D model is dangerous in prod."** Rejected for D8 scope: this is an
  offline research artifact evaluated in a simulator, never deployed. Noted for a
  future deployment story; not a D8 concern.
- **(REV) "single run = desk reject, so don't bother."** Rejected as a reason to
  not build: D8's job is precisely to build the replication harness so the rerun
  becomes possible. The bar applies to the paper, not to this scaffold.
- **(RLE) "use GRPO not SFT."** Partially rejected: Claim 2 is about *imitation
  transfer* from Fireball trajectories, which is SFT-shaped. GRPO-on-SRE remains
  the downstream step (train_rft_v2) and is referenced as the eval target model,
  not replaced.

## Final deliverable set (unchanged in shape, sharpened in semantics)
- `fireball_adapter.py` — explicit-transition adapter, defensive reads,
  documented data-quality reward, CLI `--in/--out`.
- `fireball_fixture.jsonl` — 7 synthetic records (incl. 1 no-command skip and
  1 no-state-change) covering the schema.
- `test_fireball_adapter.py` — skip rules, state-change/reward, fireball
  multi-target render, file roundtrip, malformed-line handling.
- `fireball_sft.config.yaml` — SFT + transfer-eval wiring, fail-closed guard,
  provenance/blocker block.

## Success criteria (refined)
- Unit test green; converter deterministic on fixture (7->6, 1 skip).
- No fabricated Fireball numbers anywhere; blocker explicit in >=4 places.
- Config self-documents the no-fabrication guard and the replication bar.
