# B2 — Step 5: Ouroboros (self-critique as 3 different engineers)

## Engineer 1 — Statistician (finds: test-validity gaps)
**Problems found:**
- P1.1: The exact binomial uses `0.5**n_disc`. For large n_disc (e.g. 100 in deepseek
  rex-vs-zero_shot) `2^-100 ~ 8e-31` — fine in float, but `math.comb(100,i)` is a huge int;
  the product is still exact enough. Verified no overflow (Python ints). OK, but worth noting
  p_exact rounds to 0.0 — that's "p < 1e-6," not literally zero. Must not claim "p=0."
- P1.2: chi2_cc with the continuity correction can go *negative* inside if |b01-b10|<1,
  i.e. when |b01-b10|=0 -> (−1)^2=1, fine; never negative. OK on inspection.
- P1.3: Holm uses `p < alpha/(m-rank)` for the stopping rule but then reports the
  *adjusted* p separately. These two must agree. Risk: monotonic max() on p_holm could
  make a later p_holm < alpha while `significant_holm` is already False (step-down stopped).
  This is *correct* Holm behavior (once you fail to reject, all subsequent are not rejected
  regardless of their adjusted value) but a naive reader comparing p_holm<alpha will be
  confused. **Fix: keep both, document that significant_holm is authoritative.**

## Engineer 2 — Data-pipeline engineer (finds: ingestion/robustness gaps)
**Problems found:**
- P2.1: `family_incidents` derives "overall" from the *first* condition's incident keys.
  If conditions have different incident sets, overall is silently wrong. Real files share
  the same set, but the tool should at least not crash — and `aligned_bits` *does* raise
  KeyError if another condition is missing an incident, so a mismatch surfaces loudly.
  **Acceptable: fail-loud, not silent-wrong.**
- P2.2: Per-incident reward list lengths must equal `seeds` and be equal across conditions,
  else zip truncates silently in `mcnemar_table`. `mcnemar_table` guards equal *total*
  length but not per-incident. **Mitigation:** because every condition flattens the *same*
  incident list in the same order, a per-incident length difference would change total length
  and trip the ValueError. Still, a same-total-but-shifted misalignment is theoretically
  possible. Low risk given the generator emits uniform seeds; documented as an assumption.
- P2.3: No handling of NaN/None rewards. If a reward is null, `reward >= threshold` raises
  TypeError. Real files have no nulls (n_errors=0), but this is an unguarded edge.
  **Decision: leave as-is + document; adding NaN policy is over-engineering for clean data.**

## Engineer 3 — Reviewer/consumer of the output (finds: interpretation gaps)
**Problems found:**
- P3.1: The pair key `condA__vs__condB` uses alphabetical order, so "rex" is sometimes the
  B side (`rex_no_oracle__vs__rex`... actually rex < rex_no_oracle so rex is A there). The
  sign of b01 vs b10 depends on that order. **Fix: report `pass_rate_a`/`pass_rate_b` so the
  reader sees which condition is stronger regardless of naming order.** (Implemented.)
- P3.2: Underpowered cells: novel family has n_disc as low as 1; the report shows
  p_exact=1.0 there. A skim reader could mistake "rex_no_oracle vs zero_shot not significant
  in novel" for "no effect," when really there were too few discordant pairs to detect one.
  **Fix: SUMMARY must explicitly call out n_disc and not over-claim per-family novel results.**
- P3.3: chi2_cc and p_exact can disagree at the margin; reporting both invites cherry-picking.
  **Decision: p_exact is the headline; chi2_cc is clearly secondary in the printed table
  (not even printed by default in the per-row, only in JSON). Documented.**

## Final filtered spec changes applied
- Document: `significant_holm` is authoritative; `p_holm<alpha` alone is not (P1.3).
- Document: p_exact rounding floor of 1e-6 — never write "p=0," say "p<1e-6" (P1.1).
- Add `pass_rate_a`/`pass_rate_b` to every pair (P3.1) — **implemented**.
- SUMMARY must flag low-n_disc / underpowered novel cells (P2.2, P3.2) — **done in 08/09**.
- Leave NaN unguarded but documented (P2.3) — clean data, avoid over-engineering.
