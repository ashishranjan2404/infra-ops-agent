# B10 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer A — "the metric is subtly wrong" pass
**Found:** Initial spec said `pass@1 = mean_reward >= threshold` would be tempting to compute from
the logged `mean_reward` scalar. That is WRONG: thresholding the *group mean* is not pass@1; it
collapses to a single 0/1 per step and erases the per-rollout pass rate. **Fix:** pass@1 MUST be
computed from the per-rollout `rewards` array (`sum(r>=τ)/n`), never from `mean_reward`. Encoded
explicitly in `parse_log` and asserted by `test_pass1_threshold` (which would fail under the wrong
definition). Also pinned the `>=` (inclusive) boundary in `test_threshold_boundary`.

## Engineer B — "it breaks on real data" pass
**Found:** (1) Logs may have a truncated final line if training was killed mid-write → bare
`json.loads` would crash the whole run. (2) `train_rft.py` lines lack `reward_std`; `train_rft_v2`
has it → code must not require it. (3) A step with `"rewards": []` would divide-by-zero.
**Fix:** per-line try/except with warn-and-skip; only `step`+`rewards` required; empty-rewards
guarded. `test_robust_to_garbage` exercises all three. Verified: real logs parse with zero warnings.

## Engineer C — "it's dishonest / over-claims" pass
**Found:** (1) At τ=0.8 the curve is flat-zero because max observed reward is ~0.78–0.80 — a reader
could read "model learned nothing." (2) Plotting only pass@1 hides that `mean_reward` *does* move.
(3) Calling it "pass@1" without qualification implies per-incident resolution.
**Fix:** (1) report the reward range in `06`/`08` and overlay the threshold line so the unachievable
bar is visible; ship a labeled τ=0.65 companion. (2) overlay faint `mean_reward` dashed line on the
plot. (3) docstring + spec state it's a *batch-level* pass@1 over GRPO rollouts. Rejected
over-engineering: no per-incident split (data doesn't support it) — documented as a limitation,
not fabricated.

## Final filtered spec (deltas kept)
- pass@1 from the `rewards` array only; inclusive `>=`; from-scratch, never from `mean_reward`.
- Warn-and-skip parsing; require only `step`+`rewards`; empty-rewards guarded.
- Dual-threshold output (0.8 headline + 0.65 companion); Wilson CI bands; mean_reward overlay.
- Honest labeling (batch-level pass@1) + reward-range reporting; no per-incident claim.
