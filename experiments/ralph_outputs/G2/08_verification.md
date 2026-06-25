# G2 — Verification against success criteria

| Success criterion (from 01_plan) | Status | Evidence |
|---|---|---|
| Adapter imports + runs a full episode against a real CIDG scenario, returning a real `sim.engine` verdict | **MET** | `sregym_adapter.py` smoke-run + stub: rollback->resolved True, restart_pod->False (07 §2-3) |
| All 5 SREGym tool families exposed over the sim | **MET** | `get_metrics/get_logs/get_traces/cluster_control/submit_*` in `sregym_adapter.py` |
| kubectl passthrough + measured fidelity gap | **MET** | `_parse_kubectl` + `fidelity()`; tests `test_kubectl_*`; untranslated_rate=0.5 in stub (07) |
| External-style agent loop proven (drop-in for Stratus) | **MET** | `stub_agent.py` -> `CONTRACT_OK: True`; same contract Stratus uses |
| `agents.yaml` matches SREGym's documented schema + parses | **MET** | yaml.safe_load OK; name/kickoff_command/kickoff_workdir/kickoff_env (07 §5) |
| Stratus design brief, sourced not invented | **MET** | `STRATUS_BRIEF.md` cites arXiv 2506.02009 / 2605.07161 + sregym.com docs |
| Blocker specific + reproducible | **MET** | `RUN_PLAN.md` names the 3 missing pieces + unblock sequence |
| No shared-core file modified | **MET** | only files under `experiments/ralph_outputs/G2/`; `git status` clean for `sim/`,`rex/`,`agent/` |
| Run REAL Stratus on our benchmark | **NOT MET (blocked)** | Stratus + MCP servers external; no transport server built — honest blocker, no fabricated numbers |

## Outputs are real, not placeholder
- `sregym_adapter.py` actually imports `sim.engine` and returns engine-computed verdicts;
  10 pytest assertions exercise real behavior (incl. a negative diagnosis + a trap).
- The 58/61 runnability figure was produced by executing every scenario, not estimated.
- The brief contains only claims traceable to the cited Stratus/SREGym sources.

## Honest gap
The single thing the task literally asks for — Stratus's *scores* on our benchmark — is
NOT produced, by design, because producing it would require fabricating numbers from an
agent we cannot run here. Per the brief's reality rule, a correct scaffold + honest
blocker is the right deliverable, and that is what was shipped.
