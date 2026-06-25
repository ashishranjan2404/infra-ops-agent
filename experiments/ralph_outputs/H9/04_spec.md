# H9 — 04 Spec

## File: `leaderboard.json`
Top-level object:
```
{
  "benchmark": str,            // board title
  "subtitle": str,             // one-line description
  "generated": "YYYY-MM-DD",
  "metric_notes": str,         // caveats (pass@5 low-seed, no fabrication)
  "columns": ["pass@1","pass@2","pass@5"],
  "entries": [ Entry, ... ],   // ranked rows
  "blocked":  [ Blocked, ... ] // unranked, not-evaluated arms
}
```
**Entry** (required keys: `rank, system, model, family, source, pass@1, episodes`):
```
{
  "rank": int,                 // 1 = best by pass@1
  "system": str,               // condition/method, e.g. "REx (tree + oracle feedback)"
  "model": str,                // backbone, e.g. "glm-5p2"
  "family": str,               // "all-42" | "all-30" | "cascade-14"
  "source": str,               // provenance task id: "A1" | "A2" | "E3"
  "episodes": int,             // n graded episodes
  "pass@1": float [0,1],
  "ci95": [lo, hi],            // floats in [0,1]
  "pass@2": float|null,
  "pass@5": float|null,        // null where not computed (E3 seeds=2)
  "mean_reward": float,
  "highlight": bool,           // true for headline REx rows
  "note": str
}
```
**Blocked**: `{ "system": str, "source": str, "reason": str }`.

## File: `leaderboard.html`
- Loads via `fetch("leaderboard.json", {cache:"no-store"})` → `await res.json()`.
- Validation: throws if `!Array.isArray(data.entries)`; on any fetch/parse error renders an
  in-page error string (no blank screen).
- Render contract `render()`:
  - filter by `STATE.fam` (family dropdown) and `STATE.q` (search over system+model);
  - sort by `STATE.sortKey`/`STATE.sortDir` (click any `th[data-sort]`); strings via
    `localeCompare`, numbers numeric, `null` sorts as `-Infinity`;
  - one `<tr>` per entry; `highlight` rows get a gold accent; pass@1 cell = `%` + CI + a bar
    whose width = `pass@1 * 100`.
  - all text passed through `escapeHtml()` (XSS-safe even though data is trusted).
- `initMeta()` populates title/subtitle/meta, builds the family `<select>` from distinct
  families, and renders the `blocked` panel if non-empty.
- Zero external requests; pure CSS in `<style>`.

## File: `verify_leaderboard.py` (test cases)
1. `leaderboard.json` parses; `entries` is a non-empty list.
2. Every entry has the required keys; `pass@1 ∈ [0,1]`.
3. Real-number cross-check (5 anchors): A1 REx=0.897, A1 zero_shot=0.230, A2 REx=0.893,
   E3 OpenSRE=0.107, E3 base=0.071 (tol 1e-3).
4. HTML contains a `fetch("leaderboard.json"` call and references `data.entries`.
5. Live HTTP: serve the dir, GET `/leaderboard.html` → 200, GET `/leaderboard.json` → 200 and
   parses to the same entry count. Exit non-zero on any failure.

## Contract
"Renders a models-vs-pass@k table from a JSON" == test 4 + test 5 both pass.
"Real A1/A2/E3 numbers" == test 3 passes.
