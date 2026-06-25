# F4 — 10_feedback (for the next task)

Inspect every result JSON's actual shape *before* writing accessors — schema drifts across the
result family (A1 uses `p1`/`ci`, A2 uses `pass@1`/`ci95`, and `heldout_table` is a
`{policy: metrics}` dict, not a per-incident list). A blind assumption would have silently
produced a blank figure. Read the bytes first. Two more reusable lessons: (1) the git-status
"shared file dirty" check is noisy because the repo starts with many pre-existing dirty
`rex/sim/agent` files — verify ownership with `find -newermt` against your session start, not
raw `git status`; (2) the strongest figures *draw* the honest negatives (no-oracle≈baseline,
learned-harness < hand oracle, the 0.86 plateau) rather than hiding them — downstream
writer/reviewer tasks will trust a figure set far more when the caveats are visible on the axes.
The cross-model split (glm-5p2 for bars, deepseek for McNemar) is the one real weakness to fix:
a future task should regenerate the per-episode pass matrix for a single model so significance
and headline bars share a substrate.
