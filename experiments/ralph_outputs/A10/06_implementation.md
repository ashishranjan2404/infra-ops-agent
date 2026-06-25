# A10 — 06 Implementation

## What I built (all under `experiments/ralph_outputs/A10/artifacts/`)
1. **`blast_radius.py`** — read-only computer. Globs all
   `scenarios/cidg/generated/*.yaml`, parses topology, runs reverse-reachability
   BFS from `root_cause.location`, assigns a severity tier, writes the sidecar.
2. **`blast_radius.json`** — `{count, incidents[]}` with per-incident detail
   (affected count, affected service list, tier, pct, root node + severity).
3. **`blast_radius.csv`** — flat one-row-per-incident view for easy joins.
4. **`test_blast_radius.py`** — 10 unit tests over the propagation + tier logic
   and one real-scenario validation.

## Key implementation choices
- **Edge direction**: `{from: A, to: B}` = "A depends on B". Faults flow to
  callers, so I reverse edges (`to → from`) and BFS from the root cause. Validated
  on slack-consul-cache-db (4/4 affected).
- **Cycle safety**: BFS with a `seen` set, so cyclic topologies terminate.
- **Tier**: SEV1 if `n>=4` or (`sev>=0.9` & cascade); SEV2 if `n>=2` or cascade;
  else SEV3. Documented as a convenience label over the primary count signal.
- **No shared files touched**: the script only *reads* the YAMLs; all writes go to
  my task's artifacts dir. No `rex/`,`sim/`,`agent/`,`experiments/*.py` edits.

## Run command
```
python3 experiments/ralph_outputs/A10/artifacts/blast_radius.py
```

## Observed output
```
Processed 33 incidents
  wrote experiments/ralph_outputs/A10/artifacts/blast_radius.json
  wrote experiments/ralph_outputs/A10/artifacts/blast_radius.csv
  tier distribution: {'SEV1': 24, 'SEV2': 1, 'SEV3': 8}
  multi-service blast: 25/33
```
