# A17 — Summary

**Task:** Create a data card / datasheet for the SRE-Degrees benchmark (AAAI reproducibility).

**Deliverable:** `artifacts/DATA_CARD.md` — a *Datasheets for Datasets* (Gebru et al. 2021)
data card grounded in the real `scenarios/cidg/generated/` corpus, plus a reproducible stats
script that re-derives every number in it.

## Artifacts
- `artifacts/DATA_CARD.md` — 8-section data card (Motivation, Composition, Collection,
  Preprocessing, Uses+scoring contract, Distribution/Licensing, Maintenance, Reproducibility
  Appendix). Every quantitative claim is machine-derived.
- `artifacts/compute_stats.py` — pure-stdlib+pyyaml corpus profiler; parses all YAML +
  registry, emits composition JSON, exits non-zero on parse error, asserts invariants.
- `artifacts/stats.json` — the script's output for the current snapshot.
- `01–10` step files + this summary + result.json.

## Corpus snapshot characterized (2026-06-25T06:46Z)
- **51** scenario YAMLs on disk; **32** indexed in `registry.json` (**19 unindexed — registry gap**).
- 14–15 failure classes (config_bloat 7, bad_revision/cert_expire/fd_exhaust 6 each, …).
- Thesis quantified: **40/51** cascade with a buried smoking gun and a non-causal loudest alert; **51/51** have trap actions.
- All 51 are GKE+LKE, all chaos_kind: exec.
- Provenance split: **31 postmortem-derived** (named real incidents — contamination risk) vs **20 synthetic-leaf** (contamination-safe).
- Topologies small (1–5 nodes); 9-tool fixed remediation vocabulary.

## Scoring contract documented (from rex/scoring.py)
reward = 0.30·diag + 0.25·fix + 0.45·resolved − 0.60·trap; default deterministic_judge
(keyword-stem, reproducible); hybrid/llm modes break determinism. Threats (keyword-hack,
paraphrase miss) flagged.

## Verification
All 6 tests pass (51/51 YAML parse, JSON valid, counts sum, card numbers == stats.json,
8 sections). No shared-core file edited. Honest limitations cover contamination,
single-platform shape, keyword-judge fragility, empty meta.urls, registry gap, unused fields.

**Status: completed.** Real, reproducible deliverable. Main caveat (documented): the corpus
is unfrozen/concurrently-growing, so the card describes a dated snapshot and instructs readers
to re-run compute_stats.py to refresh.
