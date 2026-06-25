# D11 — Improved Plan (post-grill)

## What changed vs 01_plan
1. **Headline reframed (PSRE/SMR/AAAI):** the primary finding is the *reproducibility gap*
   — the trainer has no `--seed` knob, so the pipeline cannot produce controlled multi-seed
   runs at all. The CI number is the deliverable that this gap currently *blocks*.
2. **Detrended stability metric (PSRE):** report **last-k plateau std** of `mean_reward`
   (k=5) as the operator-meaningful instability measure, in addition to whole-curve std
   (kept only for context, explicitly labelled as inflated by the learning trend).
3. **Reuse logged `reward_std` (RLE):** for `train_qwen3-8b_v2.jsonl` use its own logged
   `reward_std` field; for v1/30b logs (no such field) recompute population std from
   `rewards[]`. Don't silently recompute over a field that already exists.
4. **Cross-config variance quarantined (AAAI wins):** moved to its own clearly-caveated
   section, with the 3 confounds (model size, n per step, trainer version) spelled out.
   Never appears in the same table as a "seed variance" column.
5. **Spread-collapse diagnostic (RLE):** the analyzer flags any step where within-step
   `reward_std` drops below a threshold (default 0.03) — GRPO advantage collapse warning.
6. **CI method stated (AAAI):** across-seed CI uses Student-t with df=(S-1) on the per-seed
   final-reward (last-k mean) statistic. Method + n + t-multiplier printed in the report.

## Accepted critiques
- PSRE: detrend → last-k plateau std. **Accepted.**
- RLE: use logged reward_std; flag spread collapse. **Accepted.**
- AAAI: quarantine cross-config; state CI method. **Accepted.**
- DOL: zero-dep analyzer, decoupled from trainer; document GPU cost. **Accepted.**

## Rejected / deferred
- RLE's push to elevate cross-config variance into the headline — **rejected** (AAAI's
  conflation risk is real). Kept as a caveated secondary section.
- Generating synthetic seed logs to "show the CI path works on numbers" — **rejected as a
  reported result** (would look like fabricated seed data). Instead the CI path is exercised
  only by `test_seed_variance.py` on clearly-synthetic fixtures, never written into the
  real `variance_report.json`.

## Final deliverables
- `artifacts/seed_variance.py` — analyzer (stdlib): per-run curve stats, within-step spread,
  last-k plateau std, spread-collapse flags, across-seed t-CI when ≥2 seed logs given.
- `artifacts/add_seed_patch.diff` — `--seed` for `train_rft_v2.py` (documented, not applied).
- `artifacts/run_multiseed.sh` — 5-seed launch driver (blocked on GPU; real & correct).
- `artifacts/test_seed_variance.py` — pytest over synthetic fixtures (CI math + collapse flag).
- generated `artifacts/variance_report.json`, `artifacts/variance_table.md` (REAL, from 3 logs).
