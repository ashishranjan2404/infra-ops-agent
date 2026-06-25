# C6 — 03 Improved Plan

## What changed after the grill

**Accepted:**
1. (PSRE/AAAI) Report held-out **confusion counts** — both `false_allow` AND
   `false_block` — as the primary signal, with accuracy secondary. The driver already
   emits all of `accuracy, false_allow, false_block, false_allow_rate, n`; the
   comparison table prints FA and FB explicitly (`ho_FA`, `ho_FB` columns).
2. (RLE/DOL) Frame as a **case study under a compute cap**, single seed, explicitly
   noting (a) non-determinism from reasoning-model sampling and (b) that the *intended*
   proposer `claude-haiku-4-5` is unreachable (Anthropic credit balance too low → HTTP
   400). All Anthropic models down.
3. (AAAI) Always print the **hand-written `is_safe` baseline** row (same for all
   proposers) as the reference line. Driver does this from `handwritten_*` fields.
4. (SMR) Add a **variance-attribution read**: is held-out FA stable across proposers
   (→ interpreter/evaluator dominate) or does it swing (→ proposer dominates)? This is
   the headline interpretation in 08/09.

**Rejected (with reason):**
- (AAAI) "Need multiple seeds + CIs or it's noise." Rejected for THIS run: 3 reasoning
  proposers × ~100s/run × 5 seeds ≈ 25+ min, over the 15-min cap. Instead I label the
  result explicitly *suggestive case study, not significant*, and keep the driver
  seed-parameterized so a multi-seed sweep is a one-line follow-up. Fabricating CIs we
  can't afford to compute would be worse than an honest n=1-seed case study.
- (RLE) "Hide the non-determinism." Rejected — per SMR, the non-determinism is itself a
  finding (FA stability across noisy proposers tells you who's doing the work). I
  surface it rather than bury it.

## Final method (unchanged core, sharpened reporting)
- Vary ONLY `hs.MODEL` (the proposer). Everything else fixed: TRAIN/HELDOUT,
  labeled_examples, train_score, thompson_search(budget=8, seed=0).
- Proposers (reachable, cross-provider): `gpt-5.5`, `deepseek-v4-pro`, `minimax-m3`.
- Primary metric: held-out (false_allow, false_block); secondary: held-out accuracy,
  train score, rule count. Baseline row: hand-written `is_safe`.
- No core-file edits; driver overrides the module global and restores it in `finally`.
