# J6 — 01 Plan

## Objective
Test whether the SRE agent / sim generalizes to a **genuinely novel incident type** it has
never seen — a failure mode absent from `scenarios/cidg/generated/`. Author the novel
scenario as a new, uniquely-named scenario YAML, validate it, run the agent/sim on it if
reachable, and report whether generalization holds.

## What counts as "novel" here
The CIDG framework has a **closed vocabulary** for `root_cause.kind` and `failure_class`
(`sim/spec.py`: `ROOT_CAUSE_KINDS`). So a "novel incident type" cannot be a brand-new kind
token — the engine would reject it. Novelty must therefore live in the **mechanism +
topology + narrative**: a failure *trigger* and *causal chain* with no analogue in the 51
generated scenarios, mapped onto the closest existing kind.

Chosen novel incident: **NTP clock-skew → distributed-lock lease expiry → split-brain.**
The trigger is a *time source*, not network/CPU/cert/disk. A skewed chrony/NTP clock makes
the leader-lease validity window read as already-expired; the lock service revokes the lease;
two replicas both think they hold it → split-brain double-writes → the dependent APIs cascade.
Closest prior scenario is `74-github-zk-splitbrain.yaml`, but that is a `net_delay` network
partition; here the partition is in **time**, and the cure is to re-sync the clock + restart
the lease root (`restart_service`), not a victim-side network-policy change.

## Approach
1. Author `scenarios/cidg/generated/90-chronos-ntp-lease-splitbrain.yaml` (unused name).
2. Map mechanism onto the closed vocab: `root_cause.kind = dns_race` (the timing/race class).
3. Validate against `sim/spec.py` (`python -m sim.spec validate`).
4. **Sim path (model-free):** drive it through `sim/engine.py` — inject → cascade present;
   trap does not resolve; wrong tool / wrong target does not resolve; canonical fix resolves.
5. **Agent path (frozen LLM):** run the real `rex.loop.refine_loop` + P0 deterministic judge
   on the scenario, registering it in the **in-memory** registry only (never writing the
   shared `registry.json`). Grade with `rex.scoring.score_plan`. Run several gateway models.

## Files to create (all task-namespaced; NO shared-core edits)
- `scenarios/cidg/generated/90-chronos-ntp-lease-splitbrain.yaml` — the new scenario (unused name).
- `experiments/ralph_outputs/J6/artifacts/run_novel_sim.py` — model-free sim driver.
- `experiments/ralph_outputs/J6/artifacts/run_novel_agent.py` — LLM agent-path driver.
- `experiments/ralph_outputs/J6/artifacts/{sim_result.json, agent_results.jsonl}` — outputs.

## Dependencies
- `sim/spec.py`, `sim/engine.py` (read-only use), `rex/harness.py`, `rex/loop.py`,
  `rex/scoring.py` (read-only use), `agent/llm.py` gateway (HUD_API_KEY).

## Risks
- A new scenario YAML is itself a generalization probe — but it should reuse existing engine
  physics correctly, else the cascade/fix may not fire (an honest finding either way).
- Anthropic credits are out → must route the agent loop to a gateway model.
- The shared `registry.json` must NOT be edited → register the scenario in-memory only.

## Success criteria
- YAML parses and `validate()` returns `[]`.
- Sim path: cascade present, trap/wrong-tool do NOT resolve, canonical fix DOES resolve.
- Agent path: at least one frozen model reaches reward ≥ 0.8 (clean win) on the unseen incident,
  OR a documented blocker if the LLM is unreachable.
