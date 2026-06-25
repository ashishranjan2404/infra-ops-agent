# J4 — 05 Ouroboros (self-critique as 3 engineers)

## Engineer A — "the statistician"
**Problems found:**
1. Percentile bootstrap CI is biased for small n and skewed statistics; BCa would
   be better. **Verdict**: acknowledged limitation, not fixed — percentile is
   adequate at n≈30–40 and keeps the harness dependency-light; noted in `09`.
2. Paired bootstrap resamples PAIRS (correct) — verified the same index hits both
   arms. Good. But the permutation fallback for paired data uses sign-flipping of
   per-pair log-diffs, which assumes symmetric exchangeability — fine for a paired
   design, stated in code.
3. Cliff's delta is O(n_c × n_a) — fine for hundreds, would blow up at 10⁵. Capped
   by realistic n; documented.

## Engineer B — "the SRE / domain"
**Problems found:**
1. The harness analyzes whatever `mttr_minutes` it's given — it does NOT enforce
   the "diagnosis-to-resolution segment only" rule from the protocol. **Verdict**:
   intentional (over-stratification kills power, per the grill); the segment
   restriction is a *collection-time* protocol rule, documented in `04`/`09`.
2. `resolved=False` rows are loaded but `analyze` currently ignores the flag —
   unresolved attempts (timeouts) silently count at their recorded MTTR.
   **Verdict**: real gap. Documented in `09` as a known limitation; the field is
   captured so a future `--exclude-unresolved` is a one-liner. Not faked as done.
3. SLO %-within is computed but a single global `--slo` ignores per-severity SLOs.
   **Verdict**: acceptable for v1; caller runs per-severity subsets.

## Engineer C — "the reproducibility / infra"
**Problems found:**
1. `simulate_trials.py` reaches A9 via a relative `../../A9/...` path — brittle if
   moved. **Verdict**: wrapped in try/except with a lognormal-prior fallback, so it
   degrades instead of crashing. Acceptable + reported (`used_a9` flag in stderr).
2. Self-test asserts speedup in a RANGE (1.6–2.5) not a point — could a broken
   harness pass by luck? **Verdict**: combined with the null-case test (speedup
   ~1, not significant) and CI-bracketing assertions, a constant/broken estimator
   can't satisfy all of them simultaneously. Kept ranges (seed-robust) over brittle
   point asserts.
3. No CSV with malformed rows is tested. **Verdict**: `Trial.validate()` is unit-
   tested directly (T4); file-level malformed handling relies on Python's float()
   raising — acceptable, noted.

## Final filtered spec (deltas applied)
- Keep percentile bootstrap (document BCa as future work).
- Keep segment-agnostic analyze (protocol enforces segment at collection).
- **Document** the `resolved` flag gap explicitly rather than claim it's handled.
- A9 path fallback verified working (`used_a9: True` when present).
- Self-test keeps range + null + CI-bracket asserts (defeats lucky-pass).
