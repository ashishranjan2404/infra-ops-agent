# J4 — 10 Feedback for the next task

The highest-leverage move when a task's real measurement is blocked is to ship a
*self-validating* harness: build the analysis, then build a generator that plants
a KNOWN effect and prove the analysis recovers it AND correctly reports a null —
that converts "I couldn't measure it" into "here's the validated instrument the
moment data exists," which is a completed deliverable, not a blocked one. Two
concrete reusables for downstream tasks: (1) MTTR / duration data is heavily
right-skewed (A9 spans ~160x), so always analyze in log space and report a
multiplicative geometric-mean ratio with a bootstrap CI, never a difference of
arithmetic means; (2) make scipy optional with a permutation/bootstrap fallback
so harnesses stay hermetic in CI. Watch-out: A9's MTTR labels are outage-level
customer-facing durations, NOT the diagnosis-to-resolution segment an agent
actually influences — reuse them for distribution shape, but don't treat them as
a clean baseline for an agent-assist study. The genuine open blocker for anyone
continuing this line is the staged-incident replay lab + operator pool; that, not
more statistics, is what's missing.
