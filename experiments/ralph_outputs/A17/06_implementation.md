# A17 — Implementation

## What I built (real artifacts, all task-namespaced)
1. `artifacts/compute_stats.py` — reproducible, pure-stdlib+pyyaml stats script. Globs the
   live corpus, parses every YAML and `registry.json`, and emits a composition JSON
   (`snapshot_utc`, failure-class / cloud / chaos / fix-tool tallies, thesis-assertion
   counts, node-count histogram, provenance split, registry-gap list, `files_counted`).
   Exits non-zero on any parse error and asserts the failure-class counts sum to `n_yaml`.
2. `artifacts/stats.json` — the script's output for the current corpus snapshot.
3. `artifacts/DATA_CARD.md` — the deliverable: a Datasheets-for-Datasets data card whose
   every quantitative claim is a literal copy of `stats.json`.

## Key implementation decisions
- **No hand-typed numbers.** All composition figures in the card come from `compute_stats.py`
  output. This was the #1 grill demand (number drift) and Ouroboros staleness concern.
- **Provenance heuristic over `meta.source` + filename.** Real-org names (with synthetic
  markers excluded) → `postmortem_derived`; generic templates → `synthetic_leaf`. Documented
  in the card as a heuristic, not ground truth — auditable by re-running the script.
- **Live-corpus volatility handled, not hidden.** During authoring the corpus grew from 35 →
  51 YAMLs (parallel Ralph workers writing scenarios). Rather than freeze a wrong number, the
  card carries a `snapshot_utc` stamp and a prominent "re-run compute_stats.py to refresh"
  instruction; the script is the source of truth.
- **Scoring contract pulled from real code.** The reward weights, `deterministic_judge`
  semantics, and `REX_JUDGE_MODE` determinism caveat are read directly from `rex/scoring.py`
  (lines 22, 79–118), not invented.

## Shared-core safety
No shared-core file was edited. `rex/scoring.py`, `sim/engine.py`, `scenarios/cidg/*` were
read-only. All new files live under `experiments/ralph_outputs/A17/`.

## Snapshot reflected in the card (from stats.json)
- 51 YAML scenarios on disk; 32 indexed in registry.json (19 unindexed).
- 14–15 failure classes; top: config_bloat 7, bad_revision/cert_expire/fd_exhaust 6 each.
- Thesis: cascades / buried_gun_exists / loudest_alert_not_cause = 40/51; trap_actions 51/51.
- All 51 GKE+LKE, all chaos_kind=exec.
- Provenance: 31 postmortem_derived, 20 synthetic_leaf.
- Topology: 1 node ×11, 3 ×4, 4 ×22, 5 ×14.
