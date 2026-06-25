# B1 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer A — Reproducibility auditor
**Problems found:**
1. `--per-family 0` mapping to "all" via `args.per_family or None` is a footgun: `0 or None`
   → `None` works, but a reader could think `0` means "zero incidents." Mitigation: the
   help string says "0 = ALL 42 = the full grid"; the `tag` ("full" vs "subN") records which
   ran, and `grid.full_grid` is a hard boolean. Acceptable, documented.
2. Two runs of the same `--out` name would clobber. Mitigation: subset writes a distinct
   `grid_sub2_*.json`; the full grid writes `grid_full_*.json`. Distinct by `tag`.
3. The summarizer must not silently pass on a missing condition. → it iterates the JSON's
   own `by_condition` keys, so it only reports what exists. OK.

## Engineer B — Statistics reviewer
**Problems found:**
1. **Headlining the subset's per-family numbers would be wrong** (n=10/family → CI ~±0.18).
   Fix already in plan: subset reports OVERALL only; per-family deferred to full grid / A1.
   Re-verified in 03/07.
2. pass@5 from 5 seeds: the Chen estimator with k==n returns "incident ever solved," which
   over-credits. Fix: headline = pass@1 ± Wilson CI; pass@5 shown but flagged optimistic.
3. Wilson CI assumes independent Bernoulli trials; seeds for one incident share the
   incident's difficulty (not iid across the whole pool). This is the standard pass@k
   caveat — the CI is on the pooled pass rate, a slight under-estimate of true variance.
   Noted in 09 as a limitation, consistent with how A1 / the core pipeline report it.

## Engineer C — Systems / cost reviewer
**Problems found:**
1. **The headline risk: the full grid does not fit the cap.** Under-claiming ("ran full
   grid") would be dishonest. Fix: the REAL run is the labeled SUBSET; the full grid is a
   runnable script + resumable checkpoint + A1 reference. Blocker documented in 07/09.
2. `max_workers=10` against a shared gateway — concurrent worker tasks (A2, etc.) also hit
   it. Risk: rate-limit errors inflate `n_errors`. Mitigation: per-job try/except already
   isolates a dead call; the subset (150 eps) is small enough to tolerate a few retries.
3. Checkpoint write every 25 episodes — if the dispatcher SIGKILLs mid-write the `.partial`
   could be truncated. Low-prob (atomic-ish small JSON); on truncation just rerun (idempotent
   resume re-derives `remaining`). Acceptable for a subset; flagged for the off-cap full run.

## Final filtered spec (deltas applied)
- Keep `--per-family 0 == full` with explicit help + `grid.full_grid` boolean.
- Subset reports OVERALL pass@1 ± CI + rex-vs-zero_shot only; NO per-family claim from subset.
- pass@1 ± Wilson CI is the single headline; pass@5 shown-but-flagged.
- REAL deliverable = subset run; full grid = script + checkpoint + A1 full-42 reference.
- Limitations (Wilson iid caveat, gateway rate-limits, checkpoint truncation) → 09.
