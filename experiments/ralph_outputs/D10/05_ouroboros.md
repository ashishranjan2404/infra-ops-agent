# D10 — 05 Ouroboros (self-critique as 3 engineers)

## Engineer A — Correctness auditor
**Problem found:** `compose()` re-implements `score_plan`'s formula by hand. If core ever
changes the formula (e.g. adds a 5th term), the wrapper silently diverges and reports wrong
numbers.
**Fix:** `selftest()` asserts `compose(prims, DEFAULT_W) == score_plan(...)` for every rollout
in the bank. Any formula drift in core trips the assert on the next run. We also read
`DEFAULT_W` live from the module, not a literal. → mitigated, not eliminated (a non-default-weight
core change could still slip; documented in 09).

## Engineer B — Metrics skeptic
**Problem found:** Kendall tau computed over candidate lists that contain **ties** (many
candidates score 0.0) can be misleading — tau-a numerator ignores ties but the denominator
counts all pairs, deflating tau even when the *meaningful* order is preserved.
**Fix:** Acknowledged. We pair tau with `argmax_flip_rate` (tie-robust: it only asks whether
the single best candidate changed) and `composite_spread`. The argmax flip is the decision-
relevant metric for RFT (which rollout the policy is pushed toward); tau is a secondary,
directional signal. Documented the tie caveat in 09.

**Problem found:** Candidates were hand-designed so `correct_full` is best at default weights —
risk of a tautological "ranking" that can't move.
**Fix:** This is exactly what the sweep tests: `resolution_only` and `no_trap_penalty` DO move
the argmax on a fraction of scenarios (a trap candidate that happens to resolve the SLO out-scores
the clean fix once the penalty is gone). So the design is falsifiable, and it fired. Good.

## Engineer C — Scope / over-engineering reviewer
**Problem found:** Dumping the full `rollout_bank` (292 rows) into the JSON bloats the artifact;
the `_plan`/`_sim_resolved` internal keys could leak.
**Fix:** Strip underscore-prefixed keys before serialization (done in `main()`). Keeping the bank
is justified — it's the *evidence* that rollouts are real and re-scorable, and it's small (~292
rows). Not over-engineered.

**Problem found:** Could be accused of "not real RFT." 
**Fix:** Reframe honestly (done in 06/09): we run the **reward function** — the object a weight
sweep modifies — over a real sim-executed rollout bank. The policy-gradient step is the only
missing piece and is blocked by no-GPU/no-API; we do not fabricate it.

## Final filtered spec delta
- Keep selftest equivalence guard (A).
- Headline = argmax-flip-rate + spread; tau secondary with documented tie caveat (B).
- Strip internal keys from JSON; keep bank as evidence (C).
- Honest framing of the RFT boundary (C).
