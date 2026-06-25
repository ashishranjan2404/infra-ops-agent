# I5 — 06 Implementation

## What I built (real, runnable, numpy-only)

### `artifacts/sme_rlvr_model.py`
The formal model + simulation. Contents:
- `WorldParams` dataclass — all generative knobs (K, n_groups, rho_V, p_label,
  eps_override, sme_noise, lam, seed).
- `_make_groups / _verifier_reward / _sme_signal` — generative process: Beta-distributed
  true values `q`; coarse binary verifier with tunable correlation `rho_V`; dense ordinal
  SME signal with gaussian noise and an `eps_override` inversion.
- `reshaped_reward(...)` — `r = (1−λ)r_V + λ s_hat` on labeled groups, `r_V` elsewhere.
- `signal_quality(rewards, q)` — group-centered advantage `A`, alignment `Corr(A, q_c)`,
  magnitude `Std(A)`, and the proxy `G = align·magnitude`.
- `evaluate(wp)` — RLVR-only vs RLVR+SME `G`, `delta_G`, `helps`.
- `learning_curve(wp)` — illustrative online update `θ ← θ + lr·G·(1−θ)`; steps-to-target.
- `sweep(wp)` — the headline `λ × eps` grid of `delta_G` (the crossover table).
- `main()` — CLI, prints + optionally writes `sim_results.json`.

### `artifacts/test_sme_rlvr_model.py`
8 tests covering invariants (centering, perfect/flat reward), the two no-op corollaries
(λ=0, p=0), the positive case (good SME helps), the hurt case (bad SME does not), and the
sweep monotonicity in `eps`. Runs under pytest *and* as a plain script.

### `artifacts/sim_results.json`
Captured deterministic output of the run (see `07_test_results.md`).

## Key implementation decisions (traceable to the grill / ouroboros)
- **Reshape reward → recompute advantage** (RLE's option (a)), not a separate SME advantage
  term — pinned to remove ambiguity.
- **`G` is a proxy**, with the crossover sign-change as the load-bearing evidence (not the
  learning curve) — per Ouroboros Engineer B.
- **Zero-std guard** in `_safe_corr` prevents NaN on flat groups — per Engineer C.

## Shared-core safety
No shared files touched. Everything lives under
`experiments/ralph_outputs/I5/artifacts/`. No imports from `rex/`, `sim/`, `agent/`, or
`experiments/*.py`. numpy-only; no network, no GPU, no cluster.

## How to run
```bash
cd experiments/ralph_outputs/I5/artifacts
python3 sme_rlvr_model.py --out sim_results.json
python3 -m pytest test_sme_rlvr_model.py -q     # or: python3 test_sme_rlvr_model.py
```
