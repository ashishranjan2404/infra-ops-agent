# B4 — Implementation

## Artifacts built (all under experiments/ralph_outputs/B4/artifacts/)

### 1. classify_incidents.py  (+ incident_types.csv / incident_types.json)
Deterministic classifier over all 51 `scenarios/cidg/generated/*.yaml`. Reuses:
- **A8** `heldout_split.csv` family column + **registry.json** as the authoritative labels for
  the 32 labelled incidents.
- **A7** `difficulty_scores.csv` to attach an `easy|medium|hard` bucket (enrichment, orthogonal
  to the 3-way type split).
- A mechanics-grounded fallback for the 19 unregistered incidents (the 80-89 real-outage series
  + the 6 a11 transfer pairs), using the primary-type ordering `novel > cascade > simple`
  (filename `-leaf-`/`-cascade-`, dated real-outage source → novel, `assertions.cascades` + >1
  SLO node → cascade, else simple).

Result (real run output):
```
classified 51 incidents -> {'simple': 11, 'cascade': 20, 'novel': 20}
by source tier: {'registry': 32, 'real-outage': 10, 'mechanics': 3, 'name-rule': 6}
```

### 2. stratify_pass_at_k.py  (+ stratified_{simple,cascade,novel}.md / stratified_pass_at_k.json)
Discovers every pass@k result JSON under `experiments/results/` and
`experiments/ralph_outputs/*/artifacts/`, pulls the PRE-COMPUTED `by_condition[*].by_family[type]`
block from each (no re-estimation — guarantees parity with A1/A2), and renders **3 separate
Markdown tables**, one per incident type, across (source run × model × condition). It also:
- lists classified-but-unevaluated incidents per type (coverage honesty),
- excludes `.partial` files from headline tables and notes them as provisional,
- cross-checks each result's own `incidents_by_family` against the B4 classifier and reports
  mismatches.

Result (real run output):
```
headline results: ['full_pass_at_k_glm-5p2.json', 'ablation_pass_at_k_deepseek-v4-pro.json']
partial (provisional): ['ablation_pass_at_k_glm-5p2.json.partial']
  simple: 10 table rows, 3 classified-but-unevaluated
  cascade: 10 table rows, 6 classified-but-unevaluated
  novel: 10 table rows, 10 classified-but-unevaluated
classifier-vs-result mismatches: 0
```

## Headline findings visible in the 3 tables (real numbers)
- **simple**: zero-shot already strong (glm-5p2 pass@1 ≈ 0.56), REx → 1.0.
- **cascade**: zero-shot mid (glm-5p2 pass@1 ≈ 0.21), REx → 1.0.
- **novel**: zero-shot weakest (glm-5p2 0.167, deepseek 0.080), REx → 1.0 — the largest absolute
  lift is on the novel stratum, the thesis-relevant result. `rex_no_oracle` collapses back to
  ~zero-shot on novel, confirming the oracle (not just retries) drives the novel gain.
- Every `rex` cell shows reward_std = 0.0 (saturated) — a trainability caveat flagged in 09.

## Shared core files modified
NONE. The classifier and stratifier read `registry.json`, A1/A2/A7/A8 artifacts, and the
generated YAMLs read-only. All writes land in B4/artifacts/.

## Proposed (NOT applied) upstream change
`rex/eval_pass_at_k.py` already emits `by_family`, so no core change is required for B4. If the
project wanted the 19 unregistered incidents to be *runnable*, they'd need adding to
`registry.json` with a `family` field — that's an A-series data task, out of B4 scope, and is
left as a documented follow-up rather than an edit here.
