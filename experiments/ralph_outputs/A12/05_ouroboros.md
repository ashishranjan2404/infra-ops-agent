# A12 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer A — "the parser pedant"
**Problems found:**
1. `meta`/`assertions`/`observation` may be absent in some yamls → `spec.get("x", {})`
   could return `None` if the key exists with a null value. Need `(... or {})`.
2. `smoking_guns` entries might lack `buried_under` → guard with `.get("buried_under", 0)`.
3. Incident id: registry key vs `meta.id` use different separators (`_` vs `-`). If I
   key the output inconsistently the curriculum ids won't match what `rex/harness.py`
   `load_scenario` expects.

**Fixes:** added `(... or {})` on every nested get; `buried_under` defaulted;
canonical id = registry key when available (that's what `load_scenario` uses), else
`meta.id`. Yamls absent from registry fall back to `meta.id` and `family="unknown"`.

## Engineer B — "the methodology skeptic"
**Problems found:**
1. All 8 simple incidents tie at the same score, and large blocks of hard incidents
   tie too — within a tie the order is alphabetical, which is *meaningless* difficulty.
   Is that dishonest? No, but it must be visible.
2. `buried_depth` weight 0.04 is nearly inert (depth ~40 → 1.6) — does it ever break a
   tie? Marginally. Fine, but don't oversell it.
3. The score conflates *independent* axes (graph size vs trap booleans) into one
   scalar — information loss.

**Fixes / resolutions:** (1) accepted — ties are real and the `features` vector is
emitted so a user can break ties on any sub-signal; documented in 09. (2) kept as a
soft tiebreaker, not advertised as primary. (3) mitigated by emitting the full
per-feature vector alongside the scalar, so no information is actually lost — the
scalar is a *default* projection.

## Engineer C — "the integration realist"
**Problems found:**
1. Hardcoded relative paths break if run from a different cwd. Brief says agents'
   cwd resets between bash calls.
2. If parallel workers are still writing yamls, the count is a moving target.
3. Does the output id format actually round-trip into `rex/curriculum.py` /
   `load_scenario`? If not, the curriculum is unusable.

**Fixes:** (1) compute `REPO` from `__file__` via `os.path.join(..,"..","..","..","..")`,
all paths absolute. (2) re-run generator as the final implementation step. (3) ids are
taken straight from `registry.json` keys, which is the same dict the harness loads from
— verified the simple ids (`redis_cache_flush`, etc.) and HARD-tier-style ids match the
registry key convention.

## Final filtered spec
No structural change to the design; hardened: null-safe nested gets, absolute
`__file__`-relative paths, registry-key canonical ids, full feature vector emitted,
ties acknowledged as honest and tiebreakable via the emitted features. Re-run last.
