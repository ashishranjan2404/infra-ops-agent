# D3 — 10 Feedback for the next task

The highest-leverage move when a fix targets a *training-loop* behavior you can't run live
(GRPO needs the forked slug + Tinker endpoint + >15 min) is to **separate the mechanism from
the outcome**: ship a stdlib-only, unit-tested module that isolates the exact quantity the fix
changes (here, the between-scenario advantage variance via the law of total variance), plus the
real runnable driver with HUD lazy-imported so `--help`/tests pass without `.venv-hud`. Ground
demo numbers in the *actually logged* stats (v2's ~0.5 mean / ~0.17 spread) and report a
falsifiable identity (mixed == same + between, to machine precision) rather than a bare ratio —
reviewers trust an exact invariant far more than a hand-tuned reduction factor. Crucially,
downgrade the claim to what you can prove ("guarantees the same-scenario invariant + removes the
between-scenario variance") and name the unprovable part ("HUD may already group per-task; no
end-to-end curve") as an explicit blocker. The next worker doing the v2-vs-v3 A/B should reuse
`gradient_variance_reduction_factor` to read the real per-scenario reward means out of the run
log, which would replace this task's assumed difficulty spread with measured difficulties.
