# J6 — SUMMARY

## Task
Test the agent on a **novel incident type it has never seen** (true generalization). Author a
genuinely novel failure mode (absent from `scenarios/cidg/generated/`) as a new, uniquely-named
scenario YAML, validate it, run the agent/sim on it, and report whether it generalizes.

## Novel incident
**NTP clock-skew -> distributed-lock leader-lease expiry -> split-brain.** The trigger is a *time
source* (a skewed chrony/NTP clock makes the lease validity window read as expired -> the lock
service revokes the leader lease -> two replicas both think they hold it -> split-brain double-writes
cascade onto dependent APIs). Distinct from all generated scenarios; the closest,
`74-github-zk-splitbrain`, is a `net_delay` *network* partition — here the partition is in **time**.

## Deliverables (all task-namespaced; no shared-core edits)
- `scenarios/cidg/generated/90-chronos-ntp-lease-splitbrain.yaml` — the novel scenario (valid).
- `experiments/ralph_outputs/J6/artifacts/run_novel_sim.py` — model-free engine driver.
- `experiments/ralph_outputs/J6/artifacts/run_novel_agent.py` — frozen-LLM agent-path driver.
- `experiments/ralph_outputs/J6/artifacts/sim_result.json`, `agent_results.jsonl` — outputs.
- `01..10` step files.

## Results
- **Validation:** `1/1 specs valid`.
- **Sim (model-free):** cascade fires (both victims 75% error); trap, wrong-tool (`clear_cache`),
  and right-tool/wrong-target all FAIL to resolve; canonical `restart_service chrono-ntp` resolves.
  All 5 checks PASS. Honest caveat recorded: `dns_race` remediation also admits
  `modify_network_policy` on the root, so the "TIME not network" story is narrative, not enforced.
- **Agent (frozen LLM, P0 deterministic judge):** 3 gateway models — `glm-5p2`, `minimax-m3`,
  `deepseek-v4-pro` — all reach **reward 1.0**, correct diagnosis, no trap, clean win in <=2 iters.

## Verdict
**The agent GENERALIZES** to the never-seen NTP-clock-skew split-brain incident: three frozen
policies independently localize the time-source root cause and apply the correct fix, while
avoiding the network red herring and the scale-the-loud-victim trap.

## Honest limits (see 09)
Mechanism-level novelty (kind `dns_race`), not a held-out fault class (closed vocab forbids that);
N=1 scenario; task is easy (reward saturates -> no within-group spread, untrainable as-is); the
clock-vs-network distinction is only half-enforced by Tier-A. Positive result, scope disclosed.

## Status: completed
