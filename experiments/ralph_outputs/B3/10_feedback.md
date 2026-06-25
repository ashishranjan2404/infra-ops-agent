# B3 — 10 Feedback for the next task

The A1/A2 pass@k JSONs share one clean schema (`by_condition.<cond>.{overall,by_family}`
each carrying `n`, `passes`, and a stored `ci95`), and that stored `ci95` is gold for
cross-checking any statistics you recompute — read from it before re-running anything
expensive. Two reusable lessons: (1) when a tool re-derives a formula the upstream code
already has, validate against *independent known values* (literal textbook constants), not
against the upstream output, or your test is circular — then use the upstream output as a
separate *reproduction* check. (2) The honest framing for these pooled pass@k cells is that
Wilson intervals capture binomial sampling error but are anticonservative under seed
correlation (seeds reuse incidents); the raw per-(incident,seed) booleans needed for a
cluster-robust interval are not uniformly exposed in the summary JSONs, so a downstream task
wanting tighter rigor should pull them from the per-incident reward arrays. Also: Wilson is
only well-defined on pass@1 (a proportion); pass@2/@5 are the combinatorial estimator and
need a bootstrap, not Wilson. Stdlib-only + task-namespaced artifacts kept this fully
parallel-safe with zero shared-core edits.
