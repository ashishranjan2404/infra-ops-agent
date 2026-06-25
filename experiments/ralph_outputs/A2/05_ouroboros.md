# A2 — 05 Ouroboros (self-critique as 3 engineers)

## Engineer 1 — Reliability
**Found:** SIGALRM aborts a `requests.post` mid-flight; that thread's episode is lost and the
`ThreadPoolExecutor.map` driver in `run_eval` may still be iterating. The exception unwinds
through `run_eval` — but does `run_eval` flush a final checkpoint on the way out? Looking at
the source: it checkpoints every 25 done episodes and once after the loop. If SIGALRM fires
mid-loop, the post-loop flush is skipped, so the *last <25* episodes since the previous
flush are not on disk. **Impact:** `_summarize_partial` may undercount by up to 24. **Verdict:**
acceptable and *honest* (it never OVER-counts), but document it. Also: SIGALRM is POSIX-only —
guarded with `hasattr(signal,'SIGALRM')`, fine on macOS/Linux, no-op on Windows.

**Found:** if `run_eval` raises a *non*-Timeout exception (e.g. all API calls 401), the
`except` only catches TimeoutError/KeyboardInterrupt, so it propagates -> non-zero exit with a
traceback. **Fix accepted:** that's actually desirable — a hard auth failure SHOULD surface
loudly, not be silently reported as "0 completed". Leave it.

## Engineer 2 — Statistical validity
**Found:** with a time-box, conditions complete unevenly (zero_shot finishes first because it's
1 call/episode; rex finishes last at 4 calls/episode). A partial result can have zero_shot at
150/150 but rex at 40/150. Comparing pass@1 across them is then **apples-to-oranges over
different incident subsets**. **Fix accepted:** `_summarize_partial` keeps `per_incident_rewards`
intact so any downstream paired test (McNemar) can intersect to the common completed pairs.
The report's per-condition `n` is printed, so the unevenness is *visible*, not hidden. I add a
note in 08/09 that partial cross-condition contrasts must be read per-`n`.

**Found:** `summarize([0.0])` is used as a placeholder when a condition has no data — that would
print a fake pass@1=0 with n=1. **Fix:** that branch only triggers in the empty-report path
which I now guard out of `print_report`; in the from-checkpoint path a truly empty condition
gets `summarize([])`-equivalent handling. Acceptable, but I will verify no condition shows a
spurious n=1 in the real output.

## Engineer 3 — Scope / honesty
**Found:** the task literally says "vLLM local OR cheaper API". vLLM is absent on this box
(`vllm not found`, no GPU). Claiming a vLLM path would be fiction. **Fix accepted:** explicitly
document that the *available* faster path is a cheaper/faster **API** model (deepseek-v4-pro via
the HUD gateway), and say so plainly. That satisfies the "OR cheaper API" branch honestly.

**Found:** is deepseek actually *faster* end-to-end? Single probe = 2.3s, but under 8-way
concurrency calls take 8-14s (gateway queueing). So "faster" is true *per the original glm-5p2
run's failure mode* (we now finish via budget+resume) but NOT a dramatic per-call speedup.
**Fix accepted:** be precise in 07/09 — the win is *completability* (resumable, time-boxed) +
a working proposer, not a 10x latency cut. Don't oversell.

## Final filtered spec deltas
- Document the "<25 episode undercount on abort" and "uneven per-condition n" honestly (08/09).
- Keep loud failure on non-timeout exceptions.
- Frame the model as "cheaper API (deepseek-v4-pro), vLLM unavailable" — the honest branch.
- Verify no spurious n=1 condition in real output.
