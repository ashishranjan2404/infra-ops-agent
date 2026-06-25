# A1 — 05 Ouroboros (self-critique, 3 engineers)

## Engineer A — "the determinism auditor"
- **Problem (real):** The runner asserts `floor_ok` AFTER the (expensive) sweep. If a floor
  leak existed we'd burn ~50 min before finding out. **Fix:** floor_check was run OFFLINE first
  (no API) and confirmed `floor_ok=true` over all 42 before launching the sweep — documented in
  07. The in-runner assert is a redundant final guard, not the primary gate.
- **Problem (real):** Job ordering is condition-major (`for cond ... for name ... for seed`), so
  `rex` (the thesis condition) is LAST. A mid-run timeout yields zero_shot complete but rex
  empty — the opposite of the priority in 03. **Fix:** acknowledged as a real limitation of the
  unmodified core ordering. Mitigation: the checkpoint resumes, so a relaunch continues toward
  rex; and if rex is incomplete we run a second targeted invocation with
  `--conditions zero_shot,rex` so both anchors get full coverage. Reported honestly in 09.

## Engineer B — "the statistician"
- **Problem (real):** seeds=3 makes pass@5 degenerate (saturates to 1.0 once c>=1). Reporting it
  next to pass@1 invites misreading. **Fix:** SUMMARY leads with pass@1 ± Wilson CI; pass@5 is
  explicitly labeled "optimistic / low-seed" and we note a seeds>=5 rerun is the clean version.
- **Problem (real):** Wilson CI on per-family pass@1 with n=36 (12 incidents × 3 seeds) is wide.
  A reviewer could call the per-family numbers underpowered. **Fix:** report n alongside every CI
  and frame per-family pass@1 as directional; overall (n=126) is the powered number.
- **Gap:** No comparison of full-42 vs the old 15-incident slice to show the metric *moved*.
  **Fix:** SUMMARY includes a note that the headline is now over 42 incidents (vs 15 before),
  which is the entire point of A1; exact old numbers depend on a prior run not owned by A1.

## Engineer C — "the ops/parallel-safety reviewer"
- **Problem (real):** Two checkpoints named `*glm-5p2*.partial` now exist — mine in artifacts/,
  another worker's in experiments/results/. Confusable. **Fix:** mine lives ONLY under
  A1/artifacts/; I never read or write the shared one. Distinct directory = no collision.
- **Problem (real):** If the API rate-limits mid-sweep, `work()` swallows the error into the
  errors list and that (cond,incident) seed silently has fewer samples, skewing pass@k denominators
  per incident. **Fix:** report `n_errors` prominently; pass@k uses the actual per-incident sample
  count `n`, so a dropped sample lowers n rather than counting as a fail (honest). Flag if
  n_errors is non-trivial in 07/09.
- **Over-engineering check:** The runner is ~60 lines wrapping core — appropriately thin. No new
  estimator code (reuses the single-source-of-truth). Good.

## Final filtered spec deltas
1. Floor check gated OFFLINE before the sweep (done) + redundant in-runner assert.
2. Headline = pass@1 ± Wilson CI (overall = powered, per-family = directional, n shown).
   pass@5 labeled low-seed.
3. If `rex` incomplete at budget end, second targeted `zero_shot,rex` invocation to guarantee
   both anchors at full 42 coverage; report whatever completed honestly.
4. All artifacts task-namespaced; `n_errors` surfaced.
