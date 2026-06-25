# G7 — 04 Spec

## Artifact 1: `artifacts/resolve_ai_competitor_brief.md`
Markdown, human-readable. Required sections (H2):
1. As-of date + scope + one-line summary
2. Company & funding (founded, founders, HQ, rounds, valuation) — cited
3. Positioning ("AI for prod" / "AI Production Engineer" / AI SRE) — cited
4. Product capabilities (investigation, runbooks, always-on agents, collaboration) — cited
5. Architecture (stated claims, **unverified**) — cited, vendor-tagged
6. Ecosystem & integrations (vendor-neutral layer; Datadog/Grafana/GitHub/Jenkins/Slack) — cited
7. Customers & metrics (logos + MTTR claims, each `vendor-reported`, customer named) — cited
8. Leadership — cited
9. Relevance to SRE-Degrees / REx (short, honest)
10. What is NOT publicly knowable
11. Sources (deduped URL list)

**Rule:** every numeric or named-fact claim must have an inline source reference resolvable in the
Sources list. Vendor-reported metrics carry the literal tag `(vendor-reported)`.

## Artifact 2: `artifacts/resolve_ai_watchlist.yaml`
Schema (top-level keys):
```yaml
meta:
  target: "Resolve.ai (Resolve AI, Inc.)"
  as_of: "2026-06-25"
  owner: "SRE-Degrees competitive intel"
  review_cadence: "monthly"
watch_items:        # list, >= 7
  - id: str                 # stable slug
    what: str               # what to monitor
    where:                  # list of source URLs / channels
      - str
    signal: str             # the concrete change that matters
    cadence: str            # daily|weekly|monthly|on-event
    verifiability: str      # high|medium|low
    why_it_matters: str
not_publicly_knowable:      # list of str
  - str
```

### Validator: `artifacts/validate_watchlist.py`
- Loads YAML with `yaml.safe_load`.
- Asserts: `meta` has `target`,`as_of`,`review_cadence`; `watch_items` is a list of length ≥ 7;
  each item has all 6 required keys; `cadence` ∈ {daily,weekly,monthly,on-event};
  `verifiability` ∈ {high,medium,low}; `where` is a non-empty list; `not_publicly_knowable` non-empty.
- Prints `OK: N watch items, schema valid` and exits 0 on success; raises/non-zero on failure.

### Test cases (run in step 07)
- T1: `python3 artifacts/validate_watchlist.py` → exit 0, prints OK with count ≥ 7.
- T2: markdown brief parse — confirm all 11 H2 sections present (grep).
- T3: every `(vendor-reported)` metric line also names a customer or source (manual/grep check).
