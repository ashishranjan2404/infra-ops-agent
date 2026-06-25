# I2 — SUMMARY

**Task.** Prove the trap penalty > resolved reward creates bimodality in
`rex/scoring.py`, with math + a runnable simulation demonstrating it.

## Result
**Proven and demonstrated.** Conditioning on a competent plan (diag=fix=resolved=1)
the reward `R = clamp(W_ROOT*diag + W_FIX*fix + W_RESOLVED*resolved - TRAP_PENALTY*trap, 0, 1)`
collapses to a two-atom law:

- success atom = `MAX_CLEAN = 0.30+0.25+0.45 = 1.0`
- trap basin atom = `clamp(1.0 - 0.60) = 0.40`

separated by delta = 0.60 -> bimodal whenever `0 < p_trap < 1`. The economically
meaningful threshold — where a trapped, resolved plan scores no better than an
unresolved one (`MAX_CLEAN - W_RESOLVED = 0.55`) — is **exactly
`TRAP_PENALTY >= W_RESOLVED`**. Shipped constants `0.60 > 0.45` satisfy it
(basin 0.40 < 0.55), so the trap penalty nullifies the resolved reward.

## Evidence (real, emitted)
- Competent subpopulation: `values_seen = [0.4, 1.0]`, `is_bimodal = true`,
  gap 0.6, mass 35% basin / 65% success (N=20000).
- TRAP_PENALTY sweep: valley appears ~tp>=0.2; `resolved_reward_nullified` flips
  on **exactly at tp=0.45 = W_RESOLVED**.
- `valley_present_at_shipped_penalty = true`,
  `nullification_threshold_is_W_RESOLVED = true`,
  `shipped_penalty_nullifies_resolved = true`.
- 5/5 pytest pass; constants asserted equal to live `rex/scoring.py`.

## Honest caveat
The *full mixed* reward population is multi-modal (partial-credit plans), not a
clean 2-mode law; the bimodality theorem is on the conditioned competent slice.
Demonstration uses synthetic draws (theorem is coupling-free); real-rollout
histogram via `rex/eval_pass_at_k.py` is the noted follow-up.

## Artifacts
- `artifacts/bimodality_sim.py` — derivation + simulation + sweep (runnable).
- `artifacts/test_bimodality.py` — 5 passing pytest cases.
- `artifacts/bimodality_result.json` — emitted results.

## Shared-core safety
No edits to `rex/*.py` or any shared file. A non-applied proposed tweak (floor the
trap term instead of the total, to avoid clamp-to-0 info loss) is documented in
`06_implementation.md` only.
