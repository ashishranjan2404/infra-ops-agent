# B4 — Feedback for the next task

The highest-leverage move was treating the renderer as dumb-by-design: pulling pre-computed
`by_family` blocks straight from the A1/A2 result JSONs (rather than re-estimating pass@k) made
the 3 tables provably identical to the published numbers — the parity check (105/105 exact)
became the strongest correctness evidence in the whole task. The real intellectual content was
the classifier, where the trap is the key-format mismatch: `registry.json` and the A8 sidecar use
snake_case keys while the YAML files and `meta.id` are kebab-case, so any join must normalize or
it silently drops the 32 labelled incidents into the heuristic fallback. The biggest standing gap
for downstream work is data coverage: 19 of 51 generated incidents (all 10 real-outage novels +
the 6 a11 cascades) are absent from `registry.json`, so the harness never evaluates them — a
future task that adds those to the registry with a `family` field would let B4's tables fill in
the currently-unevaluated tail for free, and would materially strengthen the "REx wins on novel"
claim by tripling the novel-stratum n.
