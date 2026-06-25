# 03 — Improved Plan (revised via the grill)

## What changed vs 01
1. **Added a no-op baseline with the identical `(action, state)` signature** and made the
   headline metric *overhead = is_safe − no-op* plus the ratio. (Accepted AAAI: a latency claim
   without subtracting CPython's call floor mostly measures the interpreter, not the function.)
2. **Workload now exercises every branch** — allow fast-path, two Layer-1 category blocks, two
   Layer-2 traps, one allowed generic — and **asserts each verdict** before timing, so we are
   provably timing real code paths, not a degenerate allow path. (Accepted PSRE.)
3. **Report mean + p50 + p99 + min/max/stdev**, but the writeup **explicitly caveats p99 at
   sub-µs scale as apparatus-bound** (scheduler + timer granularity), not "is_safe is sometimes
   slow." (Accepted AAAI for reporting; accepted PSRE for interpretation.)
4. **Project per-call → per-10-action plan** and frame the verdict against the dominant
   sim/LLM-step cost, so "meaningful?" is answered contextually. (Accepted SMR.)
5. **Stdlib-only, offline, pinned `--iters`/`--warmup`, JSON artifact.** (Accepted DOL.)

## Critique accepted
- AAAI (no-op baseline + distribution + regression-guard value) — **accepted**, central to the design.
- PSRE (exercise blocked paths; don't over-read p99) — **accepted**.
- SMR (per-call is the right unit; project to trajectory; compare to dominant cost) — **accepted**.
- DOL (reproducible, pinned, offline, extensible) — **accepted**.

## Critique rejected (and why)
- **RLE: fold `build_state` into the headline number.** *Rejected.* The task explicitly says
  "timing `is_safe`" and "overhead vs a no-op." Merging `build_state` would conflate two distinct
  functions and break the clean no-op comparison. `build_state` is reported as **adjacent context**
  in `09_critique.md` (and the script is structured so a `build_state` timing could be added), but
  it is deliberately **out of the headline scope**. This honors the task wording (SMR's argument).

## Final shape
- One script, `bench_is_safe.py`, CLI `--iters/--warmup/--json`.
- Headline: `is_safe` mean/p50/p99 vs `_noop` mean/p50/p99 → overhead delta + ratio.
- Context: projected per-10-action-plan cost; verdict relative to sim/LLM step.
- Success = real run, real JSON, defensible verdict.
