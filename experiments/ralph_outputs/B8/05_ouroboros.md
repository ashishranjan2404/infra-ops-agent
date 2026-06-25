# 05 — Ouroboros (self-critique as 3 different engineers)

## Engineer A — Numerical correctness reviewer
**Problems found:**
1. `cohens_d` div-by-zero when both groups have zero variance (e.g. a condition that
   scored identically every run). Spec must define behavior.
2. `pass@1` stored in JSON may be rounded; if I trust the stored field my h could drift
   from the true proportion. Should recompute `passes/n`.
3. `cohens_h` with `p` slightly outside [0,1] from float noise → `math.sqrt`/`asin`
   domain error. Need validation.

**Fixes:** guard sp==0 (return inf or 0.0); recompute proportion from passes/n; raise
ValueError on out-of-range p.

## Engineer B — Statistics reviewer
**Problems found:**
1. Cohen's d uses *pooled* SD which assumes near-equal variance; rex std (~0.17) vs
   zero_shot (~0.38) violates this. If I silently report pooled d a reviewer calls it.
2. Magnitude thresholds for h and d are both Cohen's 0.2/0.5/0.8 — fine, but I should
   say so, not let the reader assume a different scale.
3. No CI on the effect size itself.

**Resolution:** report BOTH group SDs (n_treat/n_base + the source std visible upstream)
and state the equal-variance caveat in SUMMARY; keep pooled d as the conventional headline.
CI on d/h is logged as a known limitation (scope), not silently dropped.

## Engineer C — API / usability reviewer
**Problems found:**
1. If `--baseline` names a condition absent from the file, a bare KeyError is ugly.
2. `--json` and pretty output share code paths; a NaN/inf d must serialize safely
   (`json.dumps(inf)` emits `Infinity`, not valid strict JSON — but acceptable for our
   internal report; flag it).
3. Over-engineering check: do I need argparse subcommands? No — flat flags suffice. Good.
   Under-engineering check: a single file with no test would be too thin — tests included.

**Fixes:** explicit `KeyError` with the available conditions listed; pretty-printer handles
non-finite d; kept the CLI flat.

## Final filtered spec (deltas applied)
- `cohens_d` returns `inf` (m1≠m2) or `0.0` (m1==m2) when pooled SD == 0.
- proportion recomputed as `passes/n`.
- `cohens_h` validates `p ∈ [0,1]`.
- baseline-missing → `KeyError` naming available conditions.
- SUMMARY carries the equal-variance + overall-only + no-effect-CI caveats.
