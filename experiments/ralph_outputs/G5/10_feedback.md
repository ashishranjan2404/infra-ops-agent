# G5 — 10 Feedback for the next task

A positioning/comparison task lives or dies on *honesty discipline*, and the cheapest way to
enforce it mechanically is to make every claim carry a citation tag and write a tiny validator
that fails if a tag is missing or unresolved — it turns "be honest" into a passing/failing test.
Two things paid off: (1) deliberately keeping the dimensions where we *tie or lose* (and saying
so) makes the whole artifact credible, whereas a clean sweep reads as propaganda; (2) quarantining
vendor marketing numbers into the vendor's own column with an explicit `vendor-stated` flag stops
us from laundering their PR into our analysis. The trap to warn the next worker about: a structural
validator proves *form, not truth* — it cannot tell you a cited claim is correctly characterized,
so don't let a green check substitute for actually reading the source. Also date-stamp every
competitor claim; commercial SRE-agent features (Komodor self-healing, Datadog Bits) shipped major
updates within the last ~6 months and an undated matrix rots fast.
