# D11 — Ouroboros: self-critique of the spec (3 sequential engineers)

## Engineer 1 — "the pedant" (correctness)
**Problems found:**
- P1.1: `plateau_std` over last-k with k > n_steps will crash or give std of <2 points.
  Spec doesn't define behavior when `n_steps < last_k` or `n_steps == 1`. FIX: clamp window
  to `min(last_k, n_steps)`; if window < 2, set plateau_std = 0.0 and add a note.
- P1.2: `pstdev` vs sample std mismatch. Within-step spread should be **population** std
  (we have the whole group, not a sample) → use `pstdev`. Across-seed CI must be **sample**
  std (seeds are a sample) → `stdev` (ddof=1). Spec mixed these; pin it: within-step=pstdev,
  across-seed=stdev. **Accepted, pinned in code.**
- P1.3: `t_multiplier(df=0)` (S=1) is undefined. Guard: `seed_ci` requires S>=2 or returns None.

## Engineer 2 — "the skeptic" (does it answer the task?)
**Problems found:**
- P2.1: The task says "variance across random seeds." With zero real seed logs, a reader
  could think we dodged it. FIX: the report MUST carry an explicit top-level
  `"seed_variance_status": "NOT MEASURED — trainer lacks --seed; see add_seed_patch.diff"`
  so the absence is a first-class, machine-readable fact, not buried prose. **Accepted.**
- P2.2: Whole-curve std is misleading and might get quoted. FIX: in the md table, label the
  column "curve_std (incl. trend — NOT stability)" and lead with plateau_std. **Accepted.**
- P2.3: Cross-config "variance" with S=3 configs is itself a 3-sample std with huge
  uncertainty AND confounded. FIX: report it as a raw spread (min/max/std of 3 numbers)
  with the confound list inline, and do NOT compute a CI on it (a CI would imply it's a
  sampling distribution of seeds, which it is not). **Accepted.**

## Engineer 3 — "the minimalist" (over/under-engineering)
**Problems found:**
- P3.1: `SeedCI.statistic` as free text is fine; no over-engineering there. But the
  `@dataclass` → JSON conversion needs `asdict`; ensure lists (collapse_steps) serialize.
  Trivial, but call it out so the artifact actually writes. **Accepted (use dataclasses.asdict).**
- P3.2: Under-engineered: no handling of an empty/garbage log line. Real jsonl can have a
  trailing newline. FIX: `load_run` skips blank/whitespace lines and lines without "step".
  **Accepted.**
- P3.3: Over-engineered risk: don't add plotting/matplotlib — DOL said zero deps. A markdown
  table is enough. **Confirmed: no plotting.**

## Final filtered spec (deltas applied)
- Clamp plateau window to `min(last_k, n_steps)`; plateau_std=0 if window<2 (+ note).
- within-step spread = `pstdev`; across-seed CI = sample `stdev` (ddof=1); seed_ci needs S>=2.
- Top-level `seed_variance_status` field, machine-readable, stating NOT MEASURED + pointer.
- md: lead with `plateau_std`; relabel `curve_std` as "incl. trend — NOT stability".
- cross_config: raw min/max/std of the 3 plateau means + inline confound list, **no CI**.
- `load_run` skips blank/malformed lines; JSON via `dataclasses.asdict`.
- No plotting / no external deps.
