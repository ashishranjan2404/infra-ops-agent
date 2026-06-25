# G1 — Test Results

## Adapter unit tests (offline, real)
```
$ python3 -m pytest experiments/ralph_outputs/G1/artifacts/test_sregym_adapter.py -q
..........                                                               [100%]
10 passed in 0.02s
```
10/10 pass: T1 import+translation load, T2 every tool translates (9 expressible argv /
4 inexpressible w/ reason), T3 diagnosis non-empty + labels victims, T4 dry-run contract,
T5 out-of-action-space, T5b partial-action-space, T6 escalation pass-through, T7 resolver
binding in argv, T8 unresolved target -> not expressible, T9 translation JSON valid.

## Syntax / parse checks
```
$ python3 -m py_compile sregym_adapter.py test_sregym_adapter.py   -> compile OK
$ json.load(action_translation.json)                               -> json OK
$ all G1/*.md readable                                             -> md readable OK
```

## Dry-run demo (real output)
`python3 sregym_adapter.py` emits a full per-problem record: a diagnosis string with
downstream services labeled as victims, and one translated command
`kubectl -n default patch deployment/checkout --type json -p '[{"op":"replace",
"path":".../limits/memory","value":"2Gi"}]'`, with `submitted=false, dry_run=true`.

## Bugs found and fixed during testing
1. **`str.format` KeyError on the memory-limit JSON patch** (`{"op":...}` braces parsed as
   format fields). Fixed with a `__MEM_PATCH__` sentinel substituted after formatting.
2. **T7 over-strict membership assert** — resolved name lives inside `deployment/<name>`
   (a token substring, not a list element). Relaxed to substring-of-joined-argv per the
   ouroboros C3 decision.

## Cluster-presence check (the blocker, verified — NOT fabricated)
```
$ which kubectl kind helm docker
/Users/mei/google-cloud-sdk/bin/kubectl
kind not found
/opt/homebrew/bin/helm
docker not found
$ kubectl get nodes
... invalid_grant: Account has been deleted ...   # no reachable cluster
```
No `kind`, no `docker`, and the only kubectl context fails auth. SREGym's live environment
cannot be installed/run here -> no benchmark scores produced, and none fabricated.
