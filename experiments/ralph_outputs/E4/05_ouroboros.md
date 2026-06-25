# E4 — 05 Ouroboros (3 self-critiques of the spec)

## Engineer 1 — "the verdict is misleading"
**Problem:** `verdict` collapses to `B_HURTS` on a stand-in run, which reads like a
scientific finding. A skimmer sees `"verdict":"B_HURTS"` and quotes it.
**Severity:** high. **Fix applied:** the `note` field lives in the SAME object and
the report footer prints it; every doc states the verdict is over stand-in models,
not the trained policies. Considered renaming verdict to `STANDIN_VERDICT` but kept
`verdict` generic so the field name is stable when real slugs land — the caveat is
carried by `note`, not the field name.

## Engineer 2 — "delta direction is ambiguous + tie handling"
**Problem 1:** `delta_b_minus_a` — is positive good? The thesis frames B (OpenSRE/
specialised) as the suspect. The sign convention must be explicit or readers
misinterpret "B_HELPS". **Fix:** documented convention = B−A; `verdict` strings name
B explicitly (`B_HELPS`/`B_HURTS`). **Problem 2:** `mean_delta == 0` exact-float
compare for `NO_NET_CHANGE` is brittle. **Assessment:** acceptable — deltas are
ratios of small integer pass-counts (k/n), so exact 0 is meaningful and reachable
(e.g. both 0/3). Not over-engineering an epsilon for an illustrative metric.

## Engineer 3 — "silent error swallowing skews pass@1"
**Problem:** a dead API call drops the episode (caught, logged to `errors`), so an
incident could compute pass@1 over FEWER than `seeds` episodes without that being
obvious in the headline. At n=3 one dropped seed changes 0/3↔0/2. **Severity:**
medium. **Fix applied:** `summarize()` reports `n` per incident is implicit, and the
top-level `n_errors` + `errors[:20]` are printed in the report header; the real
stand-in run logged **0 errors**, so no skew occurred. Documented that an operator
must check `n_errors == 0` before trusting per-incident deltas. Did NOT add
hard-fail-on-any-error (would abort a long real run over one transient 502); the
existing retry-once in `propose()` plus error surfacing is the right tradeoff.

## Final filtered spec deltas
- Keep `verdict` field name; carry caveat in `note` + every doc + report footer.
- Document B−A sign convention; verdict strings name B.
- Surface `n_errors`/`errors` prominently; operator gate = `n_errors == 0`.
- Retry-once + log-and-continue on transient errors (no hard abort).
