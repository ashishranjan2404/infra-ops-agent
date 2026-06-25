# 05 — Ouroboros (3 engineers critique the spec in sequence)

## Engineer A — "the metric is well-posed but the n<k story is buried"
**Problem:** Spec T1 originally asserted `pass@2/pass@5 >= pass@1` as if a clean
measurement, but with n=3 the estimator returns **1.0** for any k>n−c. A naive reader of
the output table sees `pass@5 = 1.000` next to `pass@1 = 0.0` and concludes the model is
great. That's a footgun.
**Fix accepted:** The script prints **n in every row**, and the spec/critique explicitly
label pass@5-at-n=3 as an extrapolation. Added a dedicated unit test
(`test_passk_extrapolation_edge_when_n_lt_k`) that PINS this contract so it can't silently
change. Headline stays pass@1, which is immune to the edge.

## Engineer B — "baseline pass@k is degenerate for the only models that run"
**Problem:** The working models all route through the gateway and are `no_temperature`.
So zero-shot baseline output barely varies across seeds → baseline pass@1 ≈ pass@2 ≈
pass@5 and std ≈ 0. Reporting "baseline pass@5" for these models is meaningless — it's the
same single sample five times.
**Fix accepted (as documentation, not code):** Do NOT fake diversity by editing the roster
temperature (shared core + changes the policy under test). Instead: (a) the **pass@1 lift**
is the honest headline (REx genuinely resamples via per-node feedback even with fixed
temperature); (b) 03/09 document that baseline pass@k collapses for `no_temperature`
models; (c) the script is unchanged-correct for a temperature-enabled proposer (e.g.
fireworks `glm-5p2`), where baseline pass@k is non-degenerate.

## Engineer C — "a 15-min cap that crashes loses everything"
**Problem:** If the wall budget is hit *mid-model* (not between models), or a model errors
hard, do we still get a result.json? The `--time-budget-s` guard only checks **between**
models, so a single slow model can blow the cap and the per-seed errors inside `run_model`
must not kill the process.
**Fix accepted:** (a) per-(cond,scenario,seed) calls are wrapped in try/except that record
an error row and continue — one dead API call can't abort the sweep; (b) the guard skips
*starting* new models past the budget; (c) `json.dump` of whatever rows completed happens
unconditionally at the end. Residual gap (honest): a hang *inside* the currently-running
model isn't preempted — mitigated by choosing a small subset (2×2×3) well under the cap and
the per-call HTTP timeout (180s in `agent/llm._post`).

## Final filtered spec (delta over 04)
- pass@1 = headline; n always printed; pass@k>n flagged as extrapolation (unit-tested edge).
- No temperature hack; baseline-pass@k degeneracy for `no_temperature` models documented.
- Per-call error isolation + between-model wall guard + unconditional final json write.
- Real subset sized to finish under the 15-min cap.
