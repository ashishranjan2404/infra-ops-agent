# A17 — Test Results

All commands run from repo root `/Users/mei/rl` with system `python3` (3.13) + pyyaml.

| # | Test | Result |
|---|------|--------|
| T1 | `compute_stats.py` runs, writes stats.json, exits 0 | **PASS** (exit=0) |
| T2 | Every scenario YAML `yaml.safe_load`s | **PASS** (51/51 parsed) |
| T3 | `registry.json` + `stats.json` are valid JSON | **PASS** (both OK) |
| T4 | failure_class counts sum to `n_yaml` (script asserts) | **PASS** (51 == 51) |
| T5 | DATA_CARD spot-numbers == stats.json | **PASS** (5/5 match) |
| T6 | DATA_CARD has well-formed section headers | **PASS** (8 `##` sections) |

## Real command output (abridged)
```
=== T1 === exit=0
=== T2 === parsed OK: 51
=== T3 === registry.json OK / stats.json OK
=== T4 === sum(failure_class)= 51 n_yaml= 51 -> True
=== T5 === {'cascades 40/51': True, 'config_bloat 7': True, 'postmortem 31': True,
            'synthetic 20': True, 'modify_network_policy 17': True} -> ALL PASS
=== T6 === ## sections: 8
```

## Issues found & fixed during testing
1. **Corpus is a moving target.** Between my first read (35 YAMLs) and the stats run, parallel
   Ralph workers grew the corpus to 51 (and individual files appeared/disappeared mid-run).
   Fix: never hand-type counts; the card is stamped with `snapshot_utc` and instructs readers
   to re-run `compute_stats.py`. The script is the single source of truth.
2. **Provenance heuristic mislabeled synthetic leaves.** v1 keyed only on `meta.source` and
   matched substrings like "gke", tagging `80-fd-exhaust-leaf-shipper` as postmortem. Fix:
   exclude synthetic structural markers (`leaf`, `cascade`, `multi-`, `-positive`,
   `singleton`) and also inspect the filename ⇒ sensible split (31 postmortem / 20 synthetic).
3. **Registry/disk mismatch** (32 indexed vs 51 on disk) — not a test failure but a real
   composition finding; documented in DATA_CARD §8 (E7) as the "registry gap."

No fabricated results. Every number is reproducible via the script.
