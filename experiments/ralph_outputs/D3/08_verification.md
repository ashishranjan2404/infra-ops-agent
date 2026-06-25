# D3 — 08 Verification

## Success criteria (from 01/03) vs reality

| Criterion | Status | Evidence |
|---|---|---|
| Ground the fix in real code | ✅ | Cites `train_rft_v2.py:11-13` (named bug) + loop at `:89-100` |
| Implement same-scenario group batching as new module/config | ✅ | `same_scenario_groups.py` + `train_rft_same_scenario.py` (v3 driver) |
| Explain why it reduces gradient variance | ✅ | Total-variance decomposition in 06; numeric in 07 (2.38x, invariant exact) |
| Runnable demo or unit test | ✅ | 7/7 pytest + grounded demo → `demo_variance_reduction.json` |
| Do NOT edit shared core files | ✅ | Only wrote under `D3/artifacts/`; v3 driver is an additive copy, diff documented in 06 |
| Compute cap ~15 min / document blocker | ✅ | Live GRPO blocker stated in 07/09; no fabricated training numbers |

## Are the outputs real (not placeholder)?
- `same_scenario_groups.py` — real, importable, unit-tested (7 tests exercise every public fn).
- `demo_variance_reduction.json` — real generated file; numbers reproduce deterministically (seed=0)
  and satisfy the law-of-total-variance identity to machine precision.
- `train_rft_same_scenario.py` — real, `--help` works, HUD lazy-imported; mirrors the v2 arg surface
  so it's drop-in for a live run on `.venv-hud`.

## Independent spot-checks performed
- Re-ran the invariant `mixed_msq == same_msq + between_scenario_var` → equal to 6 dp.
- `test_advantage_sign_corruption_under_mixing` directly proves the wrong-direction gradient claim,
  not just the aggregate variance number.
- Confirmed `is_degenerate` surfaces zero-spread groups (SRE's necessary-not-sufficient caveat).

## Honest scope statement
This deliverable proves the **mechanism** (invariant + variance reduction) on grounded synthetic
rewards and ships the runnable training driver. It does NOT prove an end-to-end GRPO win — that
requires the live Tinker trainer (off-cap, infra-gated). Status: **completed** (real
plan+spec+artifacts+tests), with the live-run as a documented downstream blocker.
