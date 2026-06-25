# D6 — 05 Ouroboros (self-critique as 3 engineers)

## Engineer A — Data Integrity
PROBLEM 1: `combinations` over a scenario's trajectories is O(n^2); with 6 traj/scenario
that's 15 pairs each, fine, but without a per-scenario cap the dataset over-represents
high-fanout scenarios. FIX: `max_pairs_per_scenario` (default 4 in CLI) keeps only the
highest-margin pairs.
PROBLEM 2: identical answer text from sibling models would create chosen≈rejected pairs
that give a ~0 DPO gradient and waste compute. FIX: explicit text-equality skip.
PROBLEM 3: empty `answer` (truncated/failed rollout) would produce a garbage chosen.
FIX: skip empty-answer rows up front. All three are now unit-tested.

## Engineer B — Trainer Correctness
PROBLEM 4: original draft risked reusing GRPO's learning rate; DPO at 1e-5 will collapse
the policy. FIX: dpo_config sets lr=5e-7, beta=0.1, frozen ref. Documented as NOT copied.
PROBLEM 5: the real backend path could crash with a cryptic ImportError. FIX: catch
ImportError and emit an actionable BLOCKER naming the missing dep AND the open-model
fork requirement (closed models aren't trainable — same as GRPO).
PROBLEM 6: config min_margin and constructor min_margin could silently diverge. FIX:
train_dpo re-applies cfg.min_margin as defense-in-depth and asserts orientation.

## Engineer C — Evaluation / Reviewer-Proofing
PROBLEM 7: train/eval leakage — pairs come from the same scenario pool you'd evaluate
on. FIX: config `eval:` block points at held-out scenarios via rex/eval_pass_at_k.py,
and the limitation is documented in 03/09. Not silently ignored.
PROBLEM 8: prompt reconstruction uses templated specs ({{SVC}} placeholders not filled).
This is a real fidelity gap. DECISION: accept + document — DPO conditions on the prompt
and the *relative* preference between two answers to the SAME prompt is unaffected by
placeholder substitution. Logged in 09 as a limitation, with the cleaner fix (carry the
realized prompt in the trajectory record) noted as future work.
PROBLEM 9 (under-engineering check): no KTO/IPO support. DECISION: dpo_config exposes
`loss_type` so swapping to ipo/kto is a one-line change; not over-engineering it now.

## Final filtered spec
All 9 problems resolved or explicitly deferred-with-reason. Constructor: per-scenario,
margin-floored, deduped, empty-skipped, capped, deterministic. Trainer: DPO-specific
hyperparams, dry-run + honest blocker. Eval: held-out path named. Known limitation:
approximate prompt reconstruction (documented, non-blocking).
