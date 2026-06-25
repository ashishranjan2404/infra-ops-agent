# 10 — Feedback for the next task

Benchmarking a pure helper like `is_safe` is cheap and high-confidence, but the real lesson is
**always anchor a latency number to the dominant cost it competes with** — a bare "0.27 µs" or
even "5× a no-op" is meaningless until you say "vs a millisecond-to-second sim/LLM step," which
turns it into "negligible." For microbenchmarks of sub-µs functions, a **no-op baseline with the
identical signature** is essential (it subtracts CPython's call + timer-read floor; the delta is
the only trustworthy figure), and you should **assert your workload hits the real branches** so
you're not timing a degenerate path. Scope discipline paid off: the grill surfaced a genuine
"should we fold in `build_state`?" disagreement, and resolving it by task wording (measure
`is_safe`, note `build_state` as adjacent context) kept the deliverable clean and honest. Next
time, if the verdict's *magnitude* claim depends on the surrounding cost, spend the extra 10
minutes to **co-measure the end-to-end path** so the comparison is shown, not reasoned.
