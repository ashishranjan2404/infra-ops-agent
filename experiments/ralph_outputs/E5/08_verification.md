# E5 — Verification against success criteria

| Criterion (from 01_plan) | Status | Evidence |
|---|---|---|
| Reuse A8 novel set | MET | `select_novel_set` reads A8 `heldout_manifest.json`; 10 keys, `source` field records provenance |
| Harness runs end-to-end on 10 novel incidents | MET | live run produced `transfer_results.json` with all 10 keys scored for empty/oracle/glm-5p2 |
| ≥1 real baseline with pass@1 + CI | MET | glm-5p2: pass@1=0.25, 95% CI [0.11, 0.47], mean 0.41, std 0.38 (real Fireworks calls) |
| Floor control (empty pass@1 == 0) | MET | `floor_ok=true`; empty mean 0.0 across all 10 |
| Ceiling/validity (oracle pass@1 == 1) | MET | `ceiling_ok=true`; oracle mean 1.0 across all 10 → every novel incident is solvable |
| Fireball blocker documented honestly | MET | `policies.fireball.status=blocked`, `error="KeyError: 'fireball'"`; no fabricated number |
| No shared core files edited | MET | artifact only *imports* rex/sim/agent/experiments; all writes under `E5/` |
| Outputs real, not placeholder | MET | reward arrays are real per-seed sim scores; self-test + py_compile + JSON parse all pass |

## Are the outputs real?
Yes. `transfer_results.json` holds genuine per-incident, per-seed rewards from
`sim/engine.py` via `run_plan` + the P0 deterministic judge. The glm-5p2 column came
from 20 live Fireworks completions; the spread (std 0.38, passes concentrated on the
easy back-fill leaves, misses on BGP/cert/conntrack/poison-pill cascades) is the
signature of a real model, not a constant. Controls bracket it correctly (0 floor, 1
ceiling).

## What is genuinely blocked (not hidden)
The **Fireball transfer number itself.** Fireball is not in `agent.models.ROSTER` and
no provider serves it, so there is no transfer pass@1 to report. The deliverable is the
*harness + novel set + baseline reference*; the moment a Fireball slug exists, one
re-run fills the blocked row and yields the transfer delta vs glm-5p2 with no code change.

## Honest caveat surfaced (not a failure, a disclosure)
The 10-set is 8 novel-family + 2 back-fill simple leaves. The blended pass@1 should be
read with the per-incident map (preserved in the JSON) for a family-level view; the two
simple leaves are the easiest and account for 4 of glm-5p2's 5 passes.
