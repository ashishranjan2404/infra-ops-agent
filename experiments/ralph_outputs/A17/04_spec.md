# A17 — Technical Spec

## Inputs (ground truth, read-only)
- `scenarios/cidg/generated/*.yaml` — 35 scenario files.
- `scenarios/cidg/generated/registry.json` — 32-entry index keyed by snake_case id, each:
  `{path, style, gold_root, red_herrings[], fix_tools[], traps[], forbidden[],
    recent_deploy, family, symptom}`.
- `rex/scoring.py` — the judge contract (read for documentation only).

## Scenario YAML schema (observed, every file conforms)
```
meta:        {id, title, source, urls[], failure_class, clouds[]}
topology:    {nodes[{name, kind, resources{replicas}}], edges[{from,to,type,weight,...}]}
root_cause:  {location, kind, severity, hidden, persistent, reset_by[]}
fault:       {chaos_kind, exec_cmd, sim{set{...}}, duration_s}
observation: {alerting, monitoring_degrades, smoking_guns[{tool,node,signature,buried_under}]}
slo:         [{metric, node, direction, threshold, sustain_ticks}]
trap_actions:[{tool, args{...}}]
canonical_fix: {ordering_notes, steps[{tool, args{...}}]}
assertions:  {cascades, loudest_alert_not_cause, fix_resolves, buried_gun_exists,
              hysteresis, monitoring_degrades}
chance:      {flap_prob, jitter, partial_recovery_prob}
seed:        int
```

## Artifact 1 — `compute_stats.py`
Pure-stdlib + pyyaml. Signature: `python3 compute_stats.py [--dir DIR] [--out stats.json]`.
Computes and emits JSON:
```json
{
  "n_yaml": 35, "n_registry": 32,
  "yaml_not_in_registry": ["80-...","81-...","82-..."],
  "failure_class": {<class>: count, ...},
  "clouds": {"gke": 35, "lke": 35},
  "chaos_kind": {"exec": 35},
  "canonical_fix_tools": {<tool>: count, ...},
  "families": {"simple": 8, "cascade": 14, "novel": 10},
  "thesis": {"cascades": 27, "buried_gun_exists": 27, "loudest_alert_not_cause": N,
             "hysteresis": 0, "monitoring_degrades": 0, "with_trap_actions": 35},
  "node_count_hist": {1: 8, 3: 1, 4: 16, 5: 9},
  "provenance": {"synthetic_leaf": N, "postmortem_derived": N}
}
```
Test: every YAML must `yaml.safe_load` without error; registry must `json.load`; counts
must sum to `n_yaml`. Exit non-zero on any parse failure.

## Artifact 2 — `DATA_CARD.md`
Datasheets-for-Datasets sections (Motivation, Composition, Collection, Preprocessing,
Uses, Distribution, Maintenance) + Reproducibility Appendix. Every number in the
Composition tables is a literal copy of `stats.json`. No number typed by hand.

### Scoring-contract subsection (from rex/scoring.py)
- Reward = `0.30·diagnosis + 0.25·correct_fix_present + 0.45·resolved − 0.60·trap_hit`.
- Gold label per item = `gold_root` (correct) vs `red_herrings` (distractors).
- Default judge = `deterministic_judge`: discriminative keyword-stem overlap; CORRECT iff
  `gold_hits > herr_hits and gold_hits > 0`. Pure, hermetic, **reproducible**.
- `REX_JUDGE_MODE ∈ {deterministic(default), hybrid, llm}`; hybrid/llm call an LLM on
  borderline cases ⇒ **non-deterministic** ⇒ NOT for reproducible headline numbers.

## Validation plan (for 07)
1. `python3 compute_stats.py` exits 0, writes stats.json.
2. `python3 -c "import yaml,glob; [yaml.safe_load(open(f)) for f in glob.glob(...)]"` — 35 OK.
3. `python3 -m json.tool registry.json` and `stats.json` parse.
4. Markdown: no broken headers; spot-check 3 numbers in DATA_CARD == stats.json.
