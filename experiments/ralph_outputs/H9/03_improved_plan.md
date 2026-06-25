# H9 — 03 Improved Plan (post-grill)

## What changed vs 01
1. **Family is now first-class** (accepted PSRE/REV). Added a `family` tag column AND a family
   filter dropdown so readers compare within a family instead of misreading a cross-family rank.
   The genuine apples-to-apples claim (REx vs baselines on the *same* model/family) is preserved
   by `highlight: true` on the REx rows so the within-model lift is visually obvious.
2. **Blocked Fireball arm is shown but unranked** (accepted REV, via RLE's compromise). It lives
   in a separate "Blocked / not evaluated" panel driven by a `blocked` array in the JSON — visible
   for honesty, but not a fake `0.0` row that would pollute the ranking.
3. **Provenance on every row** (accepted SML): each entry carries `source` (A1/A2/E3) + `episodes`
   (n) + `ci95`, rendered inline. A reader can audit any cell back to its source task.
4. **Graceful file:// failure** (accepted DVO): the fetch is wrapped; on failure the page shows an
   actionable "serve over HTTP" message instead of a blank screen.
5. **Zero external deps** (accepted DVO): no CDN, no framework. Hand-rolled ~150 lines of vanilla
   JS does sort, filter, and the CI bar — converging SML's "bars are fine" with DVO's purism.

## Critiques accepted
- PSRE category-error warning → family column + filter + highlight.
- REV selective-reporting warning → explicit blocked panel.
- RLE "prove it loads JSON" → HTTP verifier (`verify_leaderboard.py`).
- RLE/DVO file:// breakage → in-page error handler.
- SML provenance → source + n + CI per row.

## Critiques rejected (and why)
- **REV: "put the blocked arm as a table row."** REJECTED — RLE's point stands: an empty-pass@k
  row reads as 0.0 and would rank last, which is a *different* misrepresentation. A labeled,
  unranked panel is the more honest rendering.
- **DVO: "just a plain HTML `<table>`, no JS."** REJECTED as under-engineering — the task says
  "render from a JSON," which requires JS to fetch+build the table; a static `<table>` would
  inline the data and fail the core requirement. We keep JS but no framework.

## Final deliverables (unchanged from 01 in shape)
- `artifacts/leaderboard.json` — data (entries + blocked + metadata).
- `artifacts/leaderboard.html` — JSON-driven, sortable, filterable, offline, zero-dep.
- `artifacts/verify_leaderboard.py` — schema + real-number + HTTP-load verification.
