# B4 — Ouroboros (3 self-critiques, each finds REAL problems)

## Pass 1 — Engineer A (data-correctness)
**Problem 1.1 (real):** The registry/A8 key is snake_case (`redis_cache_flush`) but the YAML
`meta.id` is kebab-case (`redis-cache-flush`). If I key the classifier off `meta.id` directly it
will MISS every registry match and fall through to the mechanics rule → wrong tiers.
→ Fix: normalize both to snake_case (`id.replace('-','_')`) before lookup.

**Problem 1.2 (real):** registry.json keys are the cidg_key (already snake), but the *file* names
are kebab (`40-redis-cache-flush.yaml`). I must map file→id→snake to join. The registry stores
`path`, so I can join file→registry by basename(path) too. Use registry `path` basename as the
join key to avoid id-format ambiguity entirely.

**Problem 1.3 (real):** `is_real_outage` regex `\b(19|20)\d\d\b` would also match a synthetic
source that happens to contain a year. Guard: require source NOT to start with "Synthetic".
Verified the 80-89 sources are real ("Monzo 2019-07-29 ...", "Knight Capital ...").

## Pass 2 — Engineer B (metric-integrity)
**Problem 2.1 (real):** Pulling `by_family` numbers assumes A1's family labels == my classifier's
labels. They might differ for an incident A1 ran. If they differ, my "cascade" table would mix in
an incident A1 filed under "novel". → Fix: the stratifier reports per result the set difference
between `result.incidents_by_family[type]` and my classifier's type set, and the tables are
rendered from the RESULT's own family block (so a table is internally consistent with its source
run) while the mismatch report flags any divergence for the reader. This is the honest design:
do not silently re-bucket another run's incidents under my labels.

**Problem 2.2 (real):** If two result files use the same model+condition (e.g. A2 partial vs A1),
naive concatenation double-counts. → Fix: key rows by (source_file, model, condition); never merge
across files. Each file contributes its own rows, labelled by source.

**Problem 2.3 (gap):** A1 reports `pass@2`/`pass@5` only if seeds≥2/≥5. A2 ran seeds=? Must handle
missing pass@k keys → render "—" not crash.

## Pass 3 — Engineer C (scope / over-engineering)
**Problem 3.1 (over-engineering):** I considered recomputing pass@k from raw per-episode passes to
"verify" A1. That re-implements the estimator and risks drift (RLE's R2 point). Cut it. Parity is
asserted by reading the same numbers, not recomputing. The dataclass `IncidentType` is fine but I
don't need `@dataclass` — plain dicts keep it stdlib-trivial and JSON-serializable. Keep dicts.

**Problem 3.2 (under-engineering / real):** I had no plan for the case where NO result file has a
`by_family` block for a type (e.g. a future model run that skipped novel). Table must render the
header + "no evaluated incidents for this type in <file>" rather than an empty confusing table.

**Problem 3.3 (real):** "classified-but-unevaluated" needs a definition. = incidents my classifier
labels type T whose id is NOT in any result's incidents_by_family[T]. Compute against the union of
all headline results' incident lists. Report counts in each table footer.

## Final filtered spec deltas
- Join classifier↔registry on **basename(registry.path)**; normalize ids to snake_case elsewhere.
- `is_real_outage` = has a 4-digit year AND source doesn't start with "Synthetic".
- Render tables from each result's OWN `by_family` block; emit a mismatch report; never re-bucket.
- Row key = (source_file, model, condition); no cross-file merge; missing pass@k → "—".
- Plain dicts, stdlib only. Footer lists classified-but-unevaluated incidents per type.
