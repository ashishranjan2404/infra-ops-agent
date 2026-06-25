# J6 — 08 Verification

## Success criteria vs. evidence

| criterion (from 01/03) | met? | evidence |
|------------------------|------|----------|
| Novel incident type, absent from generated set | YES | NTP clock-skew → lease split-brain; no `clock/ntp/time/lease` scenario exists; closest (`74-zk-splitbrain`) is `net_delay`, a different mechanism |
| New uniquely-named scenario YAML | YES | `scenarios/cidg/generated/90-chronos-ntp-lease-splitbrain.yaml` (unused `90-*` name) |
| YAML validates | YES | `1/1 specs valid` (T1) |
| Sim reachable & run | YES | `run_novel_sim.py` exit 0, `result: PASS` |
| Cascade emerges | YES | both victims 75% error after inject |
| Negative controls fail | YES | trap, wrong-tool, wrong-target all `is_resolved == False` |
| Canonical fix resolves | YES | `restart_service chrono-ntp` → victims 0%, resolved true |
| Agent run on it (if reachable) | YES | 3 frozen gateway models via `refine_loop` + P0 judge |
| Generalizes | YES | all 3 models reward 1.0, correct diagnosis, no trap, clean win |
| No shared-core edits | YES | `git status`: registry.json untouched; only new YAML + J6 dir added |

## Are the outputs real (not placeholder)?
- **YAML:** real, parses through `sim/spec.py`, runs through `sim/engine.py`. Not a stub.
- **Sim numbers:** computed by the actual engine `propagate()` (0.75 own-error → 75% cascaded);
  captured verbatim in `artifacts/sim_result.json`.
- **Agent numbers:** real frozen-model rollouts over the HUD gateway (`glm-5p2`, `minimax-m3`,
  `deepseek-v4-pro`) graded by the deterministic judge; captured in `artifacts/agent_results.jsonl`.
  Reproducible: `set -a; source ~/.zshrc; set +a; python3 .../run_novel_agent.py --model glm-5p2`.

## Honesty checks
- The one place the scenario could over-claim ("network policy does nothing") is explicitly
  recorded as FALSE-in-Tier-A via `engine_note_netpol_on_root_resolves: true`. The generalization
  claim does not rest on it.
- Generalization is demonstrated as a *positive* result; the limitation (N=1 scenario, same
  `dns_race` kind family, no held-out kind) is stated plainly in 09 rather than hidden.

## Verdict
All success criteria met. Deliverable is real, reproducible, and parallel-safe.
**The agent generalizes to the novel NTP-clock-skew split-brain incident.**
